import logging
import os
from io import BytesIO
from typing import Dict

import httpx
from fastapi import APIRouter, Request, Response
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from pydantic import BaseModel, Field, ValidationError

from ai_companion.graph import graph_builder
from ai_companion.modules.image import ImageToText
from ai_companion.modules.speech import SpeechToText
from ai_companion.settings import settings

logger = logging.getLogger(__name__)

# Global module instances
speech_to_text = SpeechToText()
image_to_text = ImageToText()

# Router for WhatsApp response
whatsapp_router = APIRouter()
HTTP_CLIENT = httpx.AsyncClient(
    timeout=httpx.Timeout(settings.HTTP_TIMEOUT_SECONDS),
    transport=httpx.AsyncHTTPTransport(retries=settings.HTTP_RETRIES),
)


class TextContent(BaseModel):
    body: str = ""


class MediaContent(BaseModel):
    id: str


class ImageContent(MediaContent):
    caption: str = ""


class IncomingMessage(BaseModel):
    message_id: str | None = Field(default=None, alias="id")
    from_number: str = Field(alias="from")
    type: str
    text: TextContent | None = None
    audio: MediaContent | None = None
    image: ImageContent | None = None


class ChangeValue(BaseModel):
    messages: list[IncomingMessage] | None = None
    statuses: list[dict] | None = None


class Change(BaseModel):
    value: ChangeValue


class Entry(BaseModel):
    changes: list[Change]


class WhatsAppPayload(BaseModel):
    entry: list[Entry]


def _mask_phone(phone_number: str) -> str:
    if len(phone_number) <= 4:
        return "****"
    return f"****{phone_number[-4:]}"


def _get_request_context(message: IncomingMessage) -> tuple[str, str]:
    masked_phone = _mask_phone(message.from_number)
    correlation_id = f"{masked_phone}:{message.message_id or 'no-id'}"
    return masked_phone, correlation_id


def _get_whatsapp_credentials() -> tuple[str | None, str | None]:
    return os.getenv("WHATSAPP_TOKEN"), os.getenv("WHATSAPP_PHONE_NUMBER_ID")


@whatsapp_router.api_route("/whatsapp_response", methods=["GET", "POST"])
async def whatsapp_handler(request: Request) -> Response:
    """Handles incoming messages and status updates from the WhatsApp Cloud API."""

    if request.method == "GET":
        params = request.query_params
        if params.get("hub.verify_token") == os.getenv("WHATSAPP_VERIFY_TOKEN"):
            return Response(content=params.get("hub.challenge"), status_code=200)
        return Response(content="Verification token mismatch", status_code=403)

    try:
        raw_data = await request.json()
        payload = WhatsAppPayload.model_validate(raw_data)
        if not payload.entry or not payload.entry[0].changes:
            return Response(content="Invalid payload", status_code=400)
        change_value = payload.entry[0].changes[0].value

        if change_value.messages:
            message = change_value.messages[0]
            from_number = message.from_number
            session_id = from_number
            masked_phone, correlation_id = _get_request_context(message)

            logger.info(
                "Processing incoming WhatsApp message | correlation_id=%s | type=%s | from=%s",
                correlation_id,
                message.type,
                masked_phone,
            )

            # Get user message and handle different message types
            content = ""
            if message.type == "audio":
                if not message.audio:
                    logger.warning("Audio payload missing media id | correlation_id=%s", correlation_id)
                    return Response(content="Invalid audio payload", status_code=400)
                content = await process_audio_message({"audio": {"id": message.audio.id}}, correlation_id=correlation_id)
            elif message.type == "image":
                if not message.image:
                    logger.warning("Image payload missing media id | correlation_id=%s", correlation_id)
                    return Response(content="Invalid image payload", status_code=400)
                content = message.image.caption or ""
                image_bytes = await download_media(message.image.id, correlation_id=correlation_id)
                try:
                    description = await image_to_text.analyze_image(
                        image_bytes,
                        "Please describe what you see in this image in the context of our conversation.",
                    )
                    content += f"\n[Image Analysis: {description}]"
                except Exception as e:
                    logger.warning("Failed to analyze image | correlation_id=%s | error=%s", correlation_id, e)
            elif message.type == "text":
                content = message.text.body if message.text else ""
                if not content.strip():
                    return Response(content="Invalid text payload", status_code=400)
            else:
                unsupported_message = (
                    "I currently support text, audio, and image messages. "
                    "Please send one of these message types."
                )
                await send_response(from_number, unsupported_message, correlation_id=correlation_id)
                return Response(content="Unsupported message type", status_code=200)

            # Process message through the graph agent
            async with AsyncSqliteSaver.from_conn_string(settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
                graph = graph_builder.compile(checkpointer=short_term_memory)
                await graph.ainvoke(
                    {"messages": [HumanMessage(content=content)]},
                    {"configurable": {"thread_id": session_id}},
                )
                output_state = await graph.aget_state(config={"configurable": {"thread_id": session_id}})

            workflow = output_state.values.get("workflow", "conversation")
            response_message = output_state.values["messages"][-1].content

            if workflow == "audio":
                audio_buffer = output_state.values["audio_buffer"]
                success = await send_response(
                    from_number,
                    response_message,
                    message_type="audio",
                    media_content=audio_buffer,
                    correlation_id=correlation_id,
                )
            elif workflow == "image":
                image_data = output_state.values.get("image_buffer")
                if image_data is None and output_state.values.get("image_path"):
                    image_path = output_state.values["image_path"]
                    with open(image_path, "rb") as f:
                        image_data = f.read()
                success = await send_response(
                    from_number,
                    response_message,
                    message_type="image",
                    media_content=image_data,
                    correlation_id=correlation_id,
                )
            else:
                success = await send_response(from_number, response_message, correlation_id=correlation_id)

            if not success:
                logger.error("Failed to send WhatsApp response | correlation_id=%s", correlation_id)
                return Response(content="Failed to send message", status_code=502)

            return Response(content="Message processed", status_code=200)

        if change_value.statuses:
            return Response(content="Status update received", status_code=200)

        return Response(content="Unknown event type", status_code=400)
    except ValidationError as e:
        logger.warning("Invalid WhatsApp payload | error=%s", e)
        return Response(content="Invalid payload", status_code=400)
    except Exception as e:
        logger.error("Error processing message: %s", e, exc_info=True)
        return Response(content="Internal server error", status_code=500)


async def download_media(media_id: str, correlation_id: str = "unknown") -> bytes:
    """Download media from WhatsApp."""
    whatsapp_token, _ = _get_whatsapp_credentials()
    if not whatsapp_token:
        raise ValueError("WHATSAPP_TOKEN is not configured")

    media_metadata_url = f"https://graph.facebook.com/v21.0/{media_id}"
    headers = {"Authorization": f"Bearer {whatsapp_token}"}

    metadata_response = await HTTP_CLIENT.get(media_metadata_url, headers=headers)
    metadata_response.raise_for_status()
    metadata = metadata_response.json()
    download_url = metadata.get("url")
    if not download_url:
        logger.error("Missing media download URL | correlation_id=%s", correlation_id)
        raise ValueError("Media metadata does not contain a download URL")

    media_response = await HTTP_CLIENT.get(download_url, headers=headers)
    media_response.raise_for_status()
    return media_response.content


async def process_audio_message(message: Dict, correlation_id: str = "unknown") -> str:
    """Download and transcribe audio message."""
    whatsapp_token, _ = _get_whatsapp_credentials()
    if not whatsapp_token:
        raise ValueError("WHATSAPP_TOKEN is not configured")

    audio_id = message["audio"]["id"]
    media_metadata_url = f"https://graph.facebook.com/v21.0/{audio_id}"
    headers = {"Authorization": f"Bearer {whatsapp_token}"}

    metadata_response = await HTTP_CLIENT.get(media_metadata_url, headers=headers)
    metadata_response.raise_for_status()
    metadata = metadata_response.json()
    download_url = metadata.get("url")
    if not download_url:
        logger.error("Missing audio download URL | correlation_id=%s", correlation_id)
        raise ValueError("Audio metadata does not contain a download URL")

    audio_response = await HTTP_CLIENT.get(download_url, headers=headers)
    audio_response.raise_for_status()

    audio_buffer = BytesIO(audio_response.content)
    audio_buffer.seek(0)
    audio_data = audio_buffer.read()
    return await speech_to_text.transcribe(audio_data)


async def send_response(
    from_number: str,
    response_text: str,
    message_type: str = "text",
    media_content: bytes | None = None,
    correlation_id: str = "unknown",
) -> bool:
    """Send response to user via WhatsApp API."""
    whatsapp_token, whatsapp_phone_number_id = _get_whatsapp_credentials()
    if not whatsapp_token or not whatsapp_phone_number_id:
        logger.error("WhatsApp credentials missing | correlation_id=%s", correlation_id)
        return False

    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }

    if message_type in ["audio", "image"]:
        try:
            if media_content is None:
                raise ValueError(f"media_content is required for message_type={message_type}")

            mime_type = "audio/mpeg" if message_type == "audio" else "image/png"
            media_buffer = BytesIO(media_content)
            media_id = await upload_media(media_buffer, mime_type, correlation_id=correlation_id)
            json_data = {
                "messaging_product": "whatsapp",
                "to": from_number,
                "type": message_type,
                message_type: {"id": media_id},
            }

            if message_type == "image":
                json_data["image"]["caption"] = response_text
        except Exception as e:
            logger.error(
                "Media upload failed; falling back to text | correlation_id=%s | error=%s",
                correlation_id,
                e,
            )
            message_type = "text"

    if message_type == "text":
        json_data = {
            "messaging_product": "whatsapp",
            "to": from_number,
            "type": "text",
            "text": {"body": response_text},
        }

    response = await HTTP_CLIENT.post(
        f"https://graph.facebook.com/v21.0/{whatsapp_phone_number_id}/messages",
        headers=headers,
        json=json_data,
    )
    return response.status_code == 200


async def upload_media(media_content: BytesIO, mime_type: str, correlation_id: str = "unknown") -> str:
    """Upload media to WhatsApp servers."""
    whatsapp_token, whatsapp_phone_number_id = _get_whatsapp_credentials()
    if not whatsapp_token or not whatsapp_phone_number_id:
        raise ValueError("WHATSAPP_TOKEN or WHATSAPP_PHONE_NUMBER_ID is not configured")

    headers = {"Authorization": f"Bearer {whatsapp_token}"}
    files = {"file": ("response.mp3", media_content, mime_type)}
    data = {"messaging_product": "whatsapp", "type": mime_type}

    response = await HTTP_CLIENT.post(
        f"https://graph.facebook.com/v21.0/{whatsapp_phone_number_id}/media",
        headers=headers,
        files=files,
        data=data,
    )
    result = response.json()

    if "id" not in result:
        logger.error("Media upload response missing id | correlation_id=%s", correlation_id)
        raise Exception("Failed to upload media")
    return result["id"]

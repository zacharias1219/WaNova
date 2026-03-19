import pytest
import respx

from ai_companion.interfaces.whatsapp.whatsapp_response import download_media, process_audio_message


@pytest.mark.asyncio
@respx.mock
async def test_download_media_uses_metadata_url():
    respx.get("https://graph.facebook.com/v21.0/media-123").respond(
        200, json={"url": "https://download.test/file"}
    )
    respx.get("https://download.test/file").respond(200, content=b"img-bytes")

    data = await download_media("media-123")
    assert data == b"img-bytes"


@pytest.mark.asyncio
@respx.mock
async def test_process_audio_message_downloads_and_transcribes(monkeypatch):
    class DummySTT:
        async def transcribe(self, _audio_data: bytes) -> str:
            return "transcribed-text"

    monkeypatch.setattr(
        "ai_companion.interfaces.whatsapp.whatsapp_response.speech_to_text",
        DummySTT(),
    )

    respx.get("https://graph.facebook.com/v21.0/audio-123").respond(
        200, json={"url": "https://download.test/audio"}
    )
    respx.get("https://download.test/audio").respond(200, content=b"audio-bytes")

    result = await process_audio_message({"audio": {"id": "audio-123"}})
    assert result == "transcribed-text"

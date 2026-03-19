def text_payload(body: str = "hello", from_number: str = "919999999999", message_id: str = "msg-text-1") -> dict:
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": message_id,
                                    "from": from_number,
                                    "type": "text",
                                    "text": {"body": body},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


def audio_payload(audio_id: str = "audio-1", from_number: str = "919999999999", message_id: str = "msg-audio-1") -> dict:
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": message_id,
                                    "from": from_number,
                                    "type": "audio",
                                    "audio": {"id": audio_id},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


def image_payload(
    image_id: str = "image-1",
    caption: str = "",
    from_number: str = "919999999999",
    message_id: str = "msg-image-1",
) -> dict:
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": message_id,
                                    "from": from_number,
                                    "type": "image",
                                    "image": {"id": image_id, "caption": caption},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


def unsupported_payload(msg_type: str = "sticker", from_number: str = "919999999999") -> dict:
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "msg-unsupported-1",
                                    "from": from_number,
                                    "type": msg_type,
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


def malformed_payload() -> dict:
    return {"entry": []}

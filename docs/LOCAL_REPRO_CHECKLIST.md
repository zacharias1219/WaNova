# Local Repro Checklist

This checklist captures a repeatable local baseline for the WhatsApp agent and the main behavior flows.

## Prerequisites

- Copy `.env.example` to `.env`
- Fill at least:
  - `GROQ_API_KEY`
  - `ELEVENLABS_API_KEY`
  - `ELEVENLABS_VOICE_ID`
  - `TOGETHER_API_KEY`
  - `QDRANT_URL`
  - `QDRANT_API_KEY`
  - `WHATSAPP_PHONE_NUMBER_ID`
  - `WHATSAPP_TOKEN`
  - `WHATSAPP_VERIFY_TOKEN`

## Start Services

- Docker path:
  - `docker compose up --build -d`
- App endpoints:
  - Chainlit: `http://localhost:8000`
  - WhatsApp webhook API: `http://localhost:8080/whatsapp_response`

## Core Flows To Validate

1. Text -> Text
   - Send plain text user message.
   - Expect normal text response.

2. Voice note -> Text
   - Send audio payload.
   - Expect transcription + text response.

3. Explicit voice request -> Audio response
   - Ask: `send a voice note explaining X`.
   - Expect workflow `audio` and returned audio media.

4. Image -> Text analysis
   - Send image payload with/without caption.
   - Expect image analysis included in prompt context.

5. Explicit image request -> Generated image
   - Ask: `generate an image of ...`.
   - Expect workflow `image` and returned image media.

## Mocked Webhook Regression Harness

- Use test payload fixtures in `tests/harness/whatsapp_payloads.py`
- Run:
  - `uv run pytest -q`
- Key webhook regression tests:
  - malformed payload handling
  - unsupported message type fallback
  - text/audio/image payload parsing

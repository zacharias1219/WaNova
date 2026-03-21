<p align="center">
  <img src="logo.png" alt="WaNova logo" width="200" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/WaNova-WhatsApp--first%20AI%20Agent-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="WaNova" />
</p>

<h1 align="center">WaNova</h1>

<p align="center">
  <b>WhatsApp-first AI agent — multimodal LangGraph workflows on Meta Cloud API</b>
</p>

<p align="center">
  <i>You already have WhatsApp open — message and get answers back, no new app to install.</i>
</p>

<br/>

<p align="center">
  <a href="#getting-started"><img src="https://img.shields.io/badge/Quick%20start-Docker%20Compose-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Quick start" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" /></a>
  <a href="https://langchain-ai.github.io/langgraph/"><img src="https://img.shields.io/badge/LangGraph-workflows-1C3C3C?style=flat-square" alt="LangGraph" /></a>
  <a href="https://github.com/Chainlit/chainlit"><img src="https://img.shields.io/badge/Chainlit-UI-FF7000?style=flat-square" alt="Chainlit" /></a>
</p>

<p align="center">
  <a href="docs/GETTING_STARTED.md"><b>Full setup guide</b></a> ·
  <a href="#getting-started"><b>Quick start</b></a> ·
  <a href="#demo-proof"><b>Demo</b></a> ·
  <a href="https://github.com/zacharias1219/whatsapp-agent/issues"><b>Issues</b></a> ·
  <a href="CONTRIBUTING.md"><b>Contributing</b></a>
</p>

<br/>

# Table of Contents

- [Table of Contents](#table-of-contents)
- [WaNova: WhatsApp-first AI Agent](#WaNova-whatsapp-first-ai-agent)
- [Who it's for](#who-it's-for)
- [What you can do on WhatsApp](#what-you-can-do-on-whatsapp)
- [Demo proof](#demo-proof)
- [Getting started](#getting-started)
- [How much does it cost?](#how-much-does-it-cost)
- [The tech stack](#the-tech-stack)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)
- [Security](#security)
- [License](#license)

## WaNova: WhatsApp-first AI Agent

WaNova is a WhatsApp-first AI agent.

In India, many people are still reluctant to install “yet another app” just to ask a question.
WaNova avoids that friction: you already have WhatsApp open, so you just message and get answers back.

Under the hood, the agent routes your input to different LLM-powered capabilities (chat, speech-to-text, vision, optional TTS, optional image generation) and sends the result back through the same WhatsApp chat.

It supports multi-modal conversations: text chat, voice notes (speech-to-text, and optional text-to-speech), and images (vision analysis, and optional image generation).

Excited? Let's get started!

---

## Who it's for

Designed for the WhatsApp-first UX: if users won't install another app, WaNova meets them where they already are. For builders/operators, the repo is a production-ready reference that wires Meta WhatsApp webhooks to a LangGraph multi-modal agent.

---

## What you can do on WhatsApp

- Chat with WaNova in WhatsApp (text responses by default)
- Send voice notes; WaNova transcribes with Groq Whisper and responds
- Request voice responses; WaNova can send audio via ElevenLabs TTS
- Send images; WaNova analyzes them with Groq vision
- Request generated images; WaNova produces images using Together (FLUX.1-schnell-Free)
- Keep context using memory (short-term state + Qdrant long-term memory)

---

## Demo proof

[![WaNova demo video](https://cdn.loom.com/sessions/thumbnails/ac6b3ea0c4114052b9b5807b95dead72-05a795281d1acce7-full-play.gif)](https://www.loom.com/share/ac6b3ea0c4114052b9b5807b95dead72)

This video is a **demo version** of WaNova's capabilities.
The real WhatsApp-native flow is even faster in practice because users interact directly inside their existing chat.

---

## How to ask (works best on WhatsApp)

Use explicit phrases when you want media responses:

- Text Q&A: `Explain X in simple terms`
- Image analysis: `What is happening in this picture?`
- Generated image (explicit): `Generate an image of a futuristic street market in Mumbai at night`
- Voice reply (explicit): `Answer this as a voice note`

Tip: the router decides the mode based on your request, so being explicit about `voice note` / `image` / `generate image` improves reliability.

---
## Getting started

As a user: you just need the WhatsApp number where WaNova is running.

As an operator/developer: follow `docs/GETTING_STARTED.md` to configure env vars and run/deploy the services.

The WhatsApp webhook is implemented in `src/ai_companion/interfaces/whatsapp/webhook_endpoint.py` on route `/whatsapp_response`.

### Quick start (local)

1. Copy env file:
  - `cp .env.example .env`
2. Fill required keys in `.env`:
  - `GROQ_API_KEY`, `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`, `TOGETHER_API_KEY`
  - `QDRANT_URL`, `QDRANT_API_KEY`
  - `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_TOKEN`, `WHATSAPP_VERIFY_TOKEN`
3. Start services:
  - `docker compose up --build -d`
4. Verify local endpoints:
  - Chainlit UI: `http://localhost:8000`
  - WhatsApp webhook: `http://localhost:8080/whatsapp_response`

### Supported WhatsApp payload types

- `text`
- `audio`
- `image`

Speech notes (`audio`) are transcribed with Whisper. If you set `STT_LANGUAGE` in `.env`, it forces the transcription language; otherwise Whisper will auto-detect.

Any other incoming message type receives a friendly fallback response asking the user to send text, audio, or image.

## How it works

1. Meta's WhatsApp Cloud API calls the webhook (`/whatsapp_response`).
2. WaNova downloads any media, then:
  - audio -> Whisper STT (Groq)
  - image -> vision analysis (Groq)
3. LangGraph router decides the workflow: `conversation`, `image`, or `audio`.
4. The selected node calls the right providers:
  - conversation -> Groq chat model (`TEXT_MODEL_NAME`)
  - image -> Together images (FLUX.1-schnell-Free)
  - audio -> ElevenLabs TTS
5. WaNova sends the response back to the same WhatsApp user via the WhatsApp Cloud API.

## Try these prompts

- Text Q&A: "Explain X in simple terms."
- Image analysis: "What's happening in this picture?"
- Image generation (explicit request): "Generate an image of a futuristic street market in Mumbai at night."
- Voice output (explicit request): "Answer this as a voice note."

---

## How much does it cost?

The awesome thing about this project is **you can run it on your own computer for free!**

The **free tiers** from Groq, ElevenLabs, Qdrant Cloud, and Together AI are more than enough to get you going.

If you want to try it out on Google Cloud Run, you can get a free account and get $300 in free credits. Even if you've already used up your free credits, Cloud Run is super cheap - so it will take just a buck or two for your experiments.

---

## The tech stack


| Technology  | Description                                                                                              |
| ----------- | -------------------------------------------------------------------------------------------------------- |
| GROQ        | Powering the project with Llama 3.3, Llama 3.2 Vision, and Whisper. Groq models are awesome (and fast!!) |
| Qdrant      | Serving as the long-term database, enabling our agent to recall details you shared months ago.           |
| GCP         | Deploying your containers easily to Google Cloud Platform                                                |
| Langgraph   | Learn how to build production-ready LangGraph workflows                                                  |
| ElevenLabs  | Amazing TTS models                                                                                       |
| together.ai | Behind WaNova's image generation process                                                                    |


---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, tests, and pull request expectations.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Replace the enforcement contact placeholder in that file with your email or GitHub handle before promoting the repo widely.

## Security

See [SECURITY.md](SECURITY.md) for how to report vulnerabilities responsibly.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
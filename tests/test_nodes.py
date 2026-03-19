from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from ai_companion.graph import nodes


class DummyChain:
    async def ainvoke(self, *_args, **_kwargs):
        return "response-text"


class DummyTTS:
    async def synthesize(self, _text: str) -> bytes:
        return b"audio-bytes"


class DummyImageModule:
    async def create_scenario(self, _messages):
        return SimpleNamespace(image_prompt="test prompt")

    async def generate_image(self, _prompt: str, _output_path: str = "") -> bytes:
        return b"image-bytes"


@pytest.mark.asyncio
async def test_audio_node_returns_aimessage(monkeypatch):
    monkeypatch.setattr(nodes, "get_character_response_chain", lambda *_args, **_kwargs: DummyChain())
    monkeypatch.setattr(nodes, "get_text_to_speech_module", lambda: DummyTTS())
    monkeypatch.setattr(nodes.ScheduleContextGenerator, "get_current_activity", classmethod(lambda cls: "idle"))

    state = {"messages": [HumanMessage(content="hi")], "summary": "", "memory_context": ""}
    result = await nodes.audio_node(state, config={})

    assert isinstance(result["messages"], AIMessage)
    assert result["messages"].content == "response-text"
    assert result["audio_buffer"] == b"audio-bytes"


@pytest.mark.asyncio
async def test_image_node_returns_image_buffer(monkeypatch):
    monkeypatch.setattr(nodes, "get_character_response_chain", lambda *_args, **_kwargs: DummyChain())
    monkeypatch.setattr(nodes, "get_text_to_image_module", lambda: DummyImageModule())
    monkeypatch.setattr(nodes.ScheduleContextGenerator, "get_current_activity", classmethod(lambda cls: "idle"))

    state = {"messages": [HumanMessage(content="generate image")], "summary": "", "memory_context": ""}
    result = await nodes.image_node(state, config={})

    assert isinstance(result["messages"], AIMessage)
    assert result["messages"].content == "response-text"
    assert result["image_buffer"] == b"image-bytes"

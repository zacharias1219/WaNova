from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from ai_companion.interfaces.whatsapp.webhook_endpoint import app
from ai_companion.interfaces.whatsapp import whatsapp_response
from tests.harness.whatsapp_payloads import malformed_payload, text_payload, unsupported_payload


class DummySaverCtx:
    async def __aenter__(self):
        return object()

    async def __aexit__(self, exc_type, exc, tb):
        return None


class DummyGraph:
    async def ainvoke(self, *_args, **_kwargs):
        return None

    async def aget_state(self, *_args, **_kwargs):
        return SimpleNamespace(
            values={
                "workflow": "conversation",
                "messages": [SimpleNamespace(content="ok from graph")],
            }
        )


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_malformed_payload_returns_400(client):
    response = client.post("/whatsapp_response", json=malformed_payload())
    assert response.status_code == 400


def test_unsupported_message_type_returns_200_with_fallback(client, monkeypatch):
    async def fake_send_response(*_args, **_kwargs):
        return True

    monkeypatch.setattr(whatsapp_response, "send_response", fake_send_response)
    response = client.post("/whatsapp_response", json=unsupported_payload())
    assert response.status_code == 200
    assert response.text == "Unsupported message type"


def test_text_payload_happy_path(client, monkeypatch):
    async def fake_send_response(*_args, **_kwargs):
        return True

    monkeypatch.setattr(
        whatsapp_response.AsyncSqliteSaver,
        "from_conn_string",
        classmethod(lambda cls, _path: DummySaverCtx()),
    )
    monkeypatch.setattr(whatsapp_response.graph_builder, "compile", lambda **_kwargs: DummyGraph())
    monkeypatch.setattr(whatsapp_response, "send_response", fake_send_response)

    response = client.post("/whatsapp_response", json=text_payload("hello"))
    assert response.status_code == 200
    assert response.text == "Message processed"

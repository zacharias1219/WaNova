from ai_companion.graph.edges import select_workflow, should_summarize_conversation
from ai_companion.settings import settings


def test_select_workflow_routes_image():
    assert select_workflow({"workflow": "image"}) == "image_node"


def test_select_workflow_routes_audio():
    assert select_workflow({"workflow": "audio"}) == "audio_node"


def test_select_workflow_defaults_to_conversation():
    assert select_workflow({"workflow": "anything-else"}) == "conversation_node"


def test_should_summarize_when_over_threshold():
    messages = [object()] * (settings.TOTAL_MESSAGES_SUMMARY_TRIGGER + 1)
    assert should_summarize_conversation({"messages": messages}) == "summarize_conversation_node"


def test_should_not_summarize_when_under_threshold():
    messages = [object()] * settings.TOTAL_MESSAGES_SUMMARY_TRIGGER
    assert should_summarize_conversation({"messages": messages}) == "__end__"

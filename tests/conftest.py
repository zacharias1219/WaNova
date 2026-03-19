import os


def pytest_configure():
    required_env = {
        "GROQ_API_KEY": "test-groq",
        "ELEVENLABS_API_KEY": "test-eleven",
        "ELEVENLABS_VOICE_ID": "voice-test",
        "TOGETHER_API_KEY": "test-together",
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_API_KEY": "test-qdrant",
        "WHATSAPP_PHONE_NUMBER_ID": "123456",
        "WHATSAPP_TOKEN": "token-test",
        "WHATSAPP_VERIFY_TOKEN": "verify-test",
    }
    for key, value in required_env.items():
        os.environ.setdefault(key, value)

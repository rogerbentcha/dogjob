import pytest
from fastapi.testclient import TestClient

from dogjob.infra.config import Settings, get_settings

TEST_ENV = {
    "DOGJOB_API_KEY": "test-api-key",
    "DOGJOB_DATABASE_URL": "postgresql://test:test@localhost:5432/test",
    "DOGJOB_RESEND_API_KEY": "test-resend-key",
    "DOGJOB_REMINDER_RECIPIENT": "test@example.com",
}


@pytest.fixture(autouse=True)
def settings_env(monkeypatch: pytest.MonkeyPatch):
    for name, value in TEST_ENV.items():
        monkeypatch.setenv(name, value)
    # Les tests ne doivent pas dépendre d'un .env local.
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    from dogjob.app import create_app

    return TestClient(create_app())

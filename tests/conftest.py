import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test-jobs.db"))
    monkeypatch.setattr("app.main.publish_job", lambda *_: None)
    with TestClient(app) as c:
        yield c

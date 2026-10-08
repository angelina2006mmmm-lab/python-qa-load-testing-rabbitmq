import sqlite3


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get_job(client):
    response = client.post("/jobs", json={"message": "premium test"})
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "queued"
    assert body["message"] == "premium test"
    assert client.get(f"/jobs/{body['id']}").json() == body


def test_missing_job(client):
    response = client.get("/jobs/does-not-exist")
    assert response.status_code == 404


def test_empty_message_is_rejected(client):
    assert client.post("/jobs", json={"message": ""}).status_code == 422


def test_missing_message_is_rejected(client):
    assert client.post("/jobs", json={}).status_code == 422


def test_large_message_is_rejected(client):
    assert client.post("/jobs", json={"message": "x" * 513}).status_code == 422


def test_created_ids_are_unique(client):
    a = client.post("/jobs", json={"message": "a"}).json()
    b = client.post("/jobs", json={"message": "b"}).json()
    assert a["id"] != b["id"]


def test_unavailable_broker_returns_503(client, monkeypatch, tmp_path):
    def unavailable(*_args):
        raise ConnectionError("offline")

    monkeypatch.setattr("app.main.publish_job", unavailable)
    r = client.post("/jobs", json={"message": "queue failure"})
    assert r.status_code == 503
    assert r.json()["detail"] == "Message broker unavailable"
    with sqlite3.connect(tmp_path / "test-jobs.db") as db:
        assert db.execute("SELECT status FROM jobs LIMIT 1").fetchone()[0] == "failed"


def test_publisher_receives_created_job(client, monkeypatch):
    published = []
    monkeypatch.setattr("app.main.publish_job", lambda job_id, msg: published.append((job_id, msg)))
    response = client.post("/jobs", json={"message": "event message"})
    assert response.status_code == 202
    assert published == [(response.json()["id"], "event message")]

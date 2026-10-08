import json

import pytest

from app.db import create_job, get_job, update_job
from worker.main import process_message


def test_consumer_updates_db(client):
    create_job("job-100", "hello")
    processed = process_message(json.dumps({"id": "job-100", "message": "hello"}).encode())
    assert processed == "job-100"
    assert get_job("job-100")["status"] == "done"
    assert get_job("job-100")["result"] == "Processed mock notification"


def test_consumer_rejects_invalid_json(client):
    with pytest.raises(ValueError):
        process_message(b"invalid-json")


def test_unknown_status_rejected(client):
    create_job("job-200", "hello")
    with pytest.raises(ValueError):
        update_job("job-200", "invalid")

"""Smoke test against a running Docker Compose stack (standard library only)."""

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def request(path: str, data: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data is not None else None
    req = Request(
        BASE_URL + path,
        data=body,
        headers={"Content-Type": "application/json"} if body is not None else {},
        method="POST" if body is not None else "GET",
    )
    with urlopen(req, timeout=6) as response:
        return json.load(response)


def main():
    health = request("/health")
    assert health["status"] == "ok", health
    created = request("/jobs", {"message": "hello from smoke test"})
    job_id = created["id"]
    print("Created job:", job_id)
    for _ in range(30):
        status = request(f"/jobs/{job_id}")
        if status["status"] == "done":
            print("PASS: message delivered and consumed, status=done")
            return
        if status["status"] == "failed":
            raise RuntimeError(f"Job failed: {status}")
        time.sleep(1)
    raise TimeoutError("Job not processed after 30 seconds")


if __name__ == "__main__":
    main()

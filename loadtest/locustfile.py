"""Locust user journey: create a job and check its status."""

from uuid import uuid4

from locust import HttpUser, between, task


class PremiumApiUser(HttpUser):
    wait_time = between(0.5, 2)

    @task(4)
    def create_and_check_job(self):
        with self.client.post(
            "/jobs",
            json={"message": f"Premium notification {uuid4().hex[:12]}"},
            name="POST /jobs",
            catch_response=True,
        ) as response:
            if response.status_code != 202:
                response.failure(f"Expected 202, got {response.status_code}")
                return
            try:
                job_id = response.json()["id"]
            except (ValueError, KeyError):
                response.failure("Response has no job id")
                return
            response.success()

        with self.client.get(
            f"/jobs/{job_id}",
            name="GET /jobs/{id}",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")
            elif response.json().get("status") not in {"queued", "processing", "done"}:
                response.failure("Unexpected job state")
            else:
                response.success()

    @task(1)
    def health_check(self):
        self.client.get("/health", name="GET /health")

"""REST API for a mock subscription notification queue."""

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from app.db import create_job, get_job, init_db, update_job
from app.messaging import publish_job
from app.schemas import JobInput, JobOutput


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Premium Notifications Lab", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/jobs", response_model=JobOutput, status_code=202)
def submit_job(job: JobInput):
    job_id = str(uuid4())
    create_job(job_id, job.message)
    try:
        publish_job(job_id, job.message)
    except Exception as exc:
        update_job(job_id, "failed", "Message broker unavailable")
        raise HTTPException(status_code=503, detail="Message broker unavailable") from exc
    return get_job(job_id)


@app.get("/jobs/{job_id}", response_model=JobOutput)
def read_job(job_id: str):
    result = get_job(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return result

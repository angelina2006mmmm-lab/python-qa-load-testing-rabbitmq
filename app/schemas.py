from typing import Literal

from pydantic import BaseModel, Field


class JobInput(BaseModel):
    message: str = Field(min_length=1, max_length=512)


class JobOutput(BaseModel):
    id: str
    message: str
    status: Literal["queued", "processing", "done", "failed"]
    result: str | None
    created_at: str
    updated_at: str

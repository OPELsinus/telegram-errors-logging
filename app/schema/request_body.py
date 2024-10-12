from typing import Any

from pydantic import BaseModel


class RequestBody(BaseModel):
    chat_id: str | None = None
    message_text: str | None = None
    topic_id: int = 0


class TimeOutData(BaseModel):
    timeout: int | Any | None = 60000

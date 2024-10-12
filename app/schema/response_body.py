from enum import Enum
from typing import Any

from pydantic import BaseModel


class StatusType(int, Enum):
    decline = 200
    accept = 100


class ResponseData(BaseModel):
    success: bool = True
    errorText: str = ""


class ResponseOrchestrator(BaseModel):
    rules_result: dict | None = None
    request_info_data: dict | Any | None = None
    response_info_data: dict | Any | None = None

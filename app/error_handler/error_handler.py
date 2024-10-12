import traceback
from functools import wraps

from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette import status
from starlette.responses import JSONResponse

from app.schema.response_body import ResponseData, StatusType


def try_execute_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error = False
            if isinstance(e, ValidationError):
                error = e
            if isinstance(e, RequestErrorBadRequest):
                error = e.message  # type: ignore
            if not error:
                error = traceback.format_exc()  # type: ignore

            data = {
                "decisionResult": StatusType.decline,
                "errorText": error,
                "success": False,
            }
            response = ResponseData.model_validate(data)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(response),
            )

    return wrapper


class RequestError(Exception):
    def __init__(self, message: str, code: int) -> None:
        self.message = message
        self.code = code

    def __str__(self):
        return self.message


class RequestErrorNotFound(RequestError):
    def __init__(self, message, code=404):
        super().__init__(message=message, code=code)
        self.code = code


class RequestErrorBadRequest(RequestError):
    def __init__(self, message, code=400):
        super().__init__(message=message, code=code)
        self.code = code


class RequestErrorServerError(RequestError):
    def __init__(self, message, code=500):
        super().__init__(message=message, code=code)
        self.code = code

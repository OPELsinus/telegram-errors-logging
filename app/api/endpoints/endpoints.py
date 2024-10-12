from fastapi import APIRouter
from starlette import status

from app.schema.request_body import RequestBody
from app.schema.response_body import ResponseData
from app.service.services import handle_response

# from app.error_handler.error_handler import try_execute_async


router = APIRouter()


@router.get("/health")
async def test_api():
    return {"status_code": status.HTTP_200_OK}


@router.post("/send_report_to_tg")
# @try_execute_async
async def send_report(request_body: RequestBody):
    response_data = ResponseData()

    return await handle_response(response_data=response_data, request_body=request_body)

# from starlette import status

from app.settings.config import settings

# from app.settings.mongo_db import insert_application_data
from app.settings.telegram_bot import send_message_bot


async def handle_response(response_data, request_body):
    message_text = request_body.message_text
    chat_id = settings.chat_id
    if request_body.chat_id is not None:
        chat_id = request_body.chat_id

    await send_message_bot(message=message_text, chat_id=chat_id, message_thread_id=request_body.topic_id)

    # insert_application_data(request_body, response_data, status.HTTP_200_OK, None, None)

    return response_data

import asyncio
import datetime
import traceback
from contextlib import suppress

from aiogram import Bot, Dispatcher, exceptions, types
from aiogram.enums import ParseMode
from aiogram.filters import Command

from app.settings.config import settings
from app.settings.mongo_db import get_stats_for_all, parse_all_collections_for_errors
from app.settings.postgre_db import get_data_from_auto

bot = Bot(token=settings.tg_token, timeout=60)
dp = Dispatcher()


# Command handler for /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Hello! I am your bot.")


# Command handler for /send_to_group
@dp.message(
    Command(commands=["stats_1day", "stats_1week", "stats_1month", "stats_1year", "stats_all"], ignore_mention=True)
)
async def send_to_group(message: types.Message):
    try:
        stage = (
            "DEV"
            if message.message_thread_id in [0, None]
            else "STAGING"
            if message.message_thread_id == 9
            else "PROD"
            if message.message_thread_id == 21
            else "STAGING"
        )
        if str(message.chat.id) == str(settings.chat_id) or True:
            await message.answer("Собираю данные")
            stats, rus_per = await get_stats_for_all(message.text, stage.lower())
            message_text = f"Статистика за *{rus_per}*\n\\-\\-\\-\\-\\-\\-\\-\\-\n"
            for pair in stats:
                message_text += f"{pair[0]} \\| *{pair[1]}*" if pair[1] != 0 else f"{pair[0]} \\| {pair[1]}"
                message_text += "\n"

            message_text += f"Auto \\(staging\\): *{len(await get_data_from_auto(message.text))}*"
            message_text += f"\n\n\\#{stage}"

            await send_message_bot(
                message=message_text,
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        else:
            await message.answer("Group id is not in whitelist")

    except Exception:
        with suppress(Exception):
            await send_message_bot(f"Errorbek: {traceback.format_exc()[-700:]}", "-1002209772316", 0)


async def send_message_bot(message, chat_id, message_thread_id=0, parse_mode=ParseMode.HTML, retries=3):
    for attempt in range(retries):
        try:
            await bot.send_message(
                chat_id, message, message_thread_id=message_thread_id, parse_mode=parse_mode, request_timeout=100
            )
            break
        except exceptions.TelegramNetworkError:
            await asyncio.sleep(6)


async def search_for_updates():
    # topic_id = (
    #     0
    #     if settings.config_name == "DEV"
    #     else 9
    #     if settings.config_name == "STAGING"
    #     else 21
    #     if settings.config_name == "PROD"
    #     else 9
    # )
    await send_message_bot("Bot started", "-1002209772316", 0)

    while True:
        try:
            all_errors = await parse_all_collections_for_errors("staging")

            all_errors_auto = await get_data_from_auto()

            all_errors.extend(all_errors_auto)

            if len(all_errors) != 0:
                for error in all_errors:
                    message_text = (
                        f"⚠️<b>Error!</b>⚠️\n"
                        f"\n<b>Date:</b> <i>{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</i>\n"
                        f"\n<b>App ID:</b> {error.get('applicationId', None)}\n"
                        f"<b>Collection:</b> {error.get('collection_name', None)}\n"
                        f"<b>Success:</b> {error.get('success', None)}\n"
                        f"<b>Product ID:</b> {error.get('productId', None)}\n"
                        f"<b>Stage:</b> {error.get('stage', None)}\n"
                        f"<b>Error text:</b> {error.get('errorText', None).replace('<', '')}\n"
                        f"<b>Date of error:</b> {error.get('errorDate', None)}\n"
                        f"\n#STAGING"
                    )
                    topic_id_ = 9 if error.get("collection_name", None) != "auto_postgresql" else 315

                    with suppress(Exception):
                        await send_message_bot(message_text, settings.chat_id, topic_id_)
                        await asyncio.sleep(1)

            all_errors = await parse_all_collections_for_errors("dev")

            if len(all_errors) != 0:
                for error in all_errors:
                    message_text = (
                        f"⚠️<b>Error!</b>⚠️\n"
                        f"\n<b>Date:</b> <i>{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</i>\n"
                        f"\n<b>App ID:</b> {error.get('applicationId', None)}\n"
                        f"<b>Collection:</b> {error.get('collection_name', None)}\n"
                        f"<b>Success:</b> {error.get('success', None)}\n"
                        f"<b>Product ID:</b> {error.get('productId', None)}\n"
                        f"<b>Stage:</b> {error.get('stage', None)}\n"
                        f"<b>Error text:</b> {error.get('errorText', None).replace('<', '')}\n"
                        f"<b>Date of error:</b> {error.get('errorDate', None)}\n"
                        f"\n#DEV"
                    )
                    topic_id_ = 0 if error.get("collection_name", None) != "auto_postgresql" else 315

                    with suppress(Exception):
                        await send_message_bot(message_text, settings.chat_id, topic_id_)
                        await asyncio.sleep(1)

            for _ in range(3600):
                await asyncio.sleep(1)

        except Exception:
            with suppress(Exception):
                await send_message_bot(f"Errorbek: {traceback.format_exc()[-500:]}", "-1002209772316", 0)


async def start_polling():
    try:
        await bot.get_updates(offset=-1)
        await dp.start_polling(bot, skip_updates=True, polling_timeout=60, timeout=60)
    except (asyncio.CancelledError, KeyboardInterrupt):
        await bot.session.close()

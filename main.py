import asyncio

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.settings.app_factory import app
from app.settings.config import settings
from app.settings.middlewares import HTTP_MIDDLEWARES
from app.settings.telegram_bot import search_for_updates, start_polling

app = app

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
for mw in HTTP_MIDDLEWARES:
    app.add_middleware(BaseHTTPMiddleware, dispatch=mw)


@app.on_event("startup")
async def startup_event():
    global polling_task, search_for_updates_obj
    if asyncio.get_event_loop().is_running():
        polling_task = asyncio.create_task(start_polling())  # type: ignore
        search_for_updates_obj = asyncio.create_task(search_for_updates())  # type: ignore
    else:
        await asyncio.gather(start_polling(), search_for_updates())


@app.on_event("shutdown")
async def shutdown_event():
    global polling_task, search_for_updates_obj

    # Cancel the polling task and periodic task
    if polling_task:  # type: ignore
        polling_task.cancel()  # type: ignore
    if search_for_updates_obj:  # type: ignore
        search_for_updates_obj.cancel()  # type: ignore

    # Await cancellation of tasks
    await asyncio.gather(polling_task, search_for_updates_obj, return_exceptions=True)  # type: ignore

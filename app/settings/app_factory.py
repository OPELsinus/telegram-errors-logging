from fastapi import APIRouter, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette import status
from starlette.responses import JSONResponse

from app.api.endpoints import endpoints
from app.schema.response_body import ResponseData
from app.settings.config import settings
from app.settings.http_client import http_client  # do not change place of this import


class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            response = await self.app(scope, receive, send)
            scope.get("query_string")

        except Exception as e:
            logger.error({"error": str(e), "method": scope["method"], "path": scope["path"]})
            raise e
        else:
            if response is not None and response.status_code is not None and response.status_code >= 400:
                logger.warning(
                    {
                        "method": scope["method"],
                        "path": scope["path"],
                        "status_code": response.status_code,
                    }
                )
            if response is not None and response.status_code is not None:
                logger.info(f"method: {scope['method']}, path: {scope['path']}, status_code: {response.status_code}")

            return response


"""Create app factory"""


class MyAppFactory:
    def __init__(self, settings, http_client):
        self.settings = settings
        self.app = FastAPI(
            title=self.settings.PROJECT_NAME,
            root_path=self.settings.WWW_DOMAIN if self.settings.config_name in ["DEV", "PROD", "STAGING"] else "",
            version=self.settings.VERSION,
            description=self.settings.DESCRIPTION,
            openapi_url="/%sec%openapi.json" if self.settings.config_name == "PROD" else "/openapi.json",
            docs_url="/%sec%docs" if self.settings.config_name == "PROD" else "/docs",
            redoc_url="/%sec%redoc" if self.settings.config_name == "PROD" else "/redoc",
            debug=True,
        )
        self.http_client = http_client

    async def http_startup(self):
        await self.http_client.start()
        logger.info("Async session started.")

    async def http_shutdown(self):
        await self.http_client.stop()
        logger.info("Closing async session.")

    def get_app(self) -> FastAPI:
        self.app.add_event_handler("shutdown", self.http_shutdown)

        routes = APIRouter()

        """ This events you can add if you want to use async http_client """

        @routes.on_event("startup")
        async def startup():
            await self.http_startup()

        @routes.on_event("shutdown")
        async def shutdown():
            await self.http_shutdown()

        routes.include_router(endpoints.router)

        self.app.include_router(routes)
        self.app.add_middleware(LoggingMiddleware)

        @self.app.exception_handler(RequestValidationError)
        async def custom_form_validation_error(request, exc: RequestValidationError):
            """This handler occur if we have pydantic errors: - > return error text in one field"""
            error_text = None
            for pydantic_error in exc.errors():
                loc, msg = pydantic_error["loc"], pydantic_error["msg"]
                filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc

                try:
                    field_string = ".".join([str(x) for x in filtered_loc])  # nested fields with dot-notation
                except Exception as e:
                    logger.error(f"An error occurred while formatting field string: {e}")
                    field_string = "unknown_field"

                # Создаем строку с ошибками
                error_str = f"{field_string}: {msg}"

                # Объединяем все ошибки в одну строку
                if error_text is None:
                    error_text = error_str
                else:
                    error_text += f"\n{error_str}"
            exc.body
            data = {
                "decisionResult": 200,
                "errorText": error_text,
                "success": False,
            }
            response = ResponseData.model_validate(data)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(response),
            )

        # @self.app.exception_handler(RequestErrorBadRequest)
        # async def bad_request_exception_handler(request, exc: RequestErrorBadRequest):
        #     logger.error(f"Bad request: {exc.message}")
        #     return JSONResponse(
        #         status_code=400,
        #         content={"message": exc.message, "code": exc.code}
        #     )

        return self.app


factory = MyAppFactory(settings, http_client=http_client)
app = factory.get_app()

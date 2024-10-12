import os
import pathlib
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import AnyHttpUrl

load_dotenv()


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
    # SECURITY_BCRYPT_ROUNDS: int = 12
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days
    # REFRESH_TOKEN_EXPIRE_MINUTES: int = 40320  # 28 days
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "0.0.0.0", "*"]

    # PROJECT NAME, VERSION AND DESCRIPTION
    PROJECT_NAME: str = "TELEGRAM LOGGING"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Telegram errors logging from all microservices"
    WWW_DOMAIN = "/api/dms/telegram-errors-logging"


class DevelopmentConfig(BaseConfig):
    config_name = os.environ.get("FASTAPI_CONFIG", "STAGING")
    MONGO_URI_DEV: str = os.environ.get("MONGO_URI_DEV")  # type: ignore # ignored because we get it from env`
    MONGO_URI_STAGING: str = os.environ.get("MONGO_URI_STAGING")  # type: ignore # ignored because we get it from env`
    tg_token: str = os.environ.get("TG_BOT_TOKEN")  # type: ignore
    chat_id: str = os.environ.get("CHAT_ID")  # type: ignore
    DATABASE_USER = os.environ.get("DATABASE_USER")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PORT = os.environ.get("DATABASE_PORT")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")


class ProductionConfig(BaseConfig):
    config_name = os.environ.get("FASTAPI_CONFIG", "STAGING")
    MONGO_URI_DEV: str = os.environ.get("MONGO_URI_DEV")  # type: ignore # ignored because we get it from env`
    MONGO_URI_STAGING: str = os.environ.get("MONGO_URI_STAGING")  # type: ignore # ignored because we get it from env`
    tg_token: str = os.environ.get("TG_BOT_TOKEN")  # type: ignore
    chat_id: str = os.environ.get("CHAT_ID")  # type: ignore
    DATABASE_USER = os.environ.get("DATABASE_USER")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PORT = os.environ.get("DATABASE_PORT")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")


class TestingConfig(BaseConfig):
    config_name = os.environ.get("FASTAPI_CONFIG", "STAGING")
    MONGO_URI_DEV: str = os.environ.get("MONGO_URI_DEV")  # type: ignore # ignored because we get it from env`
    MONGO_URI_STAGING: str = os.environ.get("MONGO_URI_STAGING")  # type: ignore # ignored because we get it from env`
    tg_token: str = os.environ.get("TG_BOT_TOKEN")  # type: ignore
    chat_id: str = os.environ.get("CHAT_ID")  # type: ignore
    DATABASE_USER = os.environ.get("DATABASE_USER")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PORT = os.environ.get("DATABASE_PORT")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")


class LocalConfig(BaseConfig):
    config_name = os.environ.get("FASTAPI_CONFIG", "STAGING")
    MONGO_URI_DEV: str = os.environ.get("MONGO_URI_DEV")  # type: ignore # ignored because we get it from env`
    MONGO_URI_STAGING: str = os.environ.get("MONGO_URI_STAGING")  # type: ignore # ignored because we get it from env`
    tg_token: str = os.environ.get("TG_BOT_TOKEN")  # type: ignore
    chat_id: str = os.environ.get("CHAT_ID")  # type: ignore
    DATABASE_USER = os.environ.get("DATABASE_USER")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PORT = os.environ.get("DATABASE_PORT")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")


class StagingConfig(BaseConfig):
    config_name = os.environ.get("FASTAPI_CONFIG", "STAGING")
    MONGO_URI_DEV: str = os.environ.get("MONGO_URI_DEV")  # type: ignore # ignored because we get it from env`
    MONGO_URI_STAGING: str = os.environ.get("MONGO_URI_STAGING")  # type: ignore # ignored because we get it from env`
    tg_token: str = os.environ.get("TG_BOT_TOKEN")  # type: ignore
    chat_id: str = os.environ.get("CHAT_ID")  # type: ignore
    DATABASE_USER = os.environ.get("DATABASE_USER")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PORT = os.environ.get("DATABASE_PORT")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")


@lru_cache
def get_settings():
    config_cls_dict = {
        "DEV": DevelopmentConfig,
        "PROD": ProductionConfig,
        "TEST": TestingConfig,
        "LOCAL": LocalConfig,
        "STAGING": StagingConfig,
    }

    config_name = os.environ.get("FASTAPI_CONFIG", "DEV")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()

import ast
import asyncio
from contextlib import suppress
from datetime import datetime, timedelta

from sqlalchemy import MetaData, Table, create_engine, or_, select

from app.settings.config import settings


async def get_data_from_auto(period_raw=""):
    for tries in range(5):
        with suppress(Exception):
            first_ = f"postgresql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
            second_ = f"{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
            DATABASE_URL = f"{first_}@{second_}"

            engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 600}, pool_timeout=60)

            metadata = MetaData(schema="kmf")
            metadata.reflect(bind=engine)

            logger_api_table = Table("LOGER_API", metadata, autoload_with=engine)

            current_time = datetime.utcnow()

            period = current_time - timedelta(minutes=63)
            period = current_time - timedelta(days=365) if "1year" in period_raw else period
            period = current_time - timedelta(days=31) if "1month" in period_raw else period
            period = current_time - timedelta(days=7) if "1week" in period_raw else period
            period = current_time - timedelta(days=1) if "1day" in period_raw else period
            period = current_time - timedelta(days=10000) if "stats_all" in period_raw else period

            errors = []

            with engine.connect() as connection:
                query = select(logger_api_table).where(
                    or_(logger_api_table.c.status == 400, logger_api_table.c.status == 503),
                    logger_api_table.c.InsertDate >= period,
                )
                result = connection.execute(query).all()
                for row in result:
                    error_text = ast.literal_eval(row.response)
                    errors.append(
                        {
                            "applicationId": row.request_id,
                            "collection_name": "auto_postgresql",
                            "success": False,
                            "productId": row.product_id,
                            "stage": row.stage,
                            "errorText": error_text.get("exception", "Failed"),
                            "errorDate": row.InsertDate,
                        }
                    )
            return errors


if __name__ == "__main__":
    asyncio.run(get_data_from_auto())

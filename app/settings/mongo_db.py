from contextlib import contextmanager
from datetime import datetime, timedelta

from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from starlette import status

from app.settings.config import settings

main_collection_name = "telegram_errors_logging_DEV"


@contextmanager
def mongo_client(stage_: str = "staging"):
    timeout = 100000
    socket_timeout = 100000
    if stage_ == "dev":
        client = MongoClient(settings.MONGO_URI_DEV, serverSelectionTimeoutMS=timeout, socketTimeoutMS=socket_timeout)
    elif stage_ == "staging":
        client = MongoClient(
            settings.MONGO_URI_STAGING, serverSelectionTimeoutMS=timeout, socketTimeoutMS=socket_timeout
        )
    else:
        client = MongoClient(
            settings.MONGO_URI_STAGING, serverSelectionTimeoutMS=timeout, socketTimeoutMS=socket_timeout
        )
    try:
        yield client
    finally:
        client.close()


async def insert_application_data(
    request_body, response_data, status_code, from_collection, create_date_of_error, stage
):
    with mongo_client(stage) as client:
        mongo_db = client.db_scoring_logs
        collection = mongo_db[main_collection_name]
        request = jsonable_encoder(request_body) if request_body is not None else dict()
        response = jsonable_encoder(response_data) if response_data is not None else dict()
        data_for_mongo = {
            "applicationId": request.get("applicationId", None),
            "request": request,
            "response": response,
            "status": status_code,
            "from_collection": from_collection,
            "create_date_of_error": create_date_of_error,
            "create_date": datetime.now(),
        }
        try:
            collection.insert_one(data_for_mongo)
        except Exception as e:
            print(f"An error occurred during data insertion: {e}")


async def get_all_collections(stage):
    with mongo_client(stage) as client:
        mongo_db = client.db_scoring_logs
        for i in range(100):
            try:
                all_collections = mongo_db.list_collection_names()
                break
            except Exception:
                pass

    return all_collections


async def get_stats_for_all(period_raw, stage):
    all_collections = await get_all_collections(stage)
    stats = []
    period = datetime.now() - timedelta(days=10000)
    period = datetime.now() - timedelta(days=365) if "1year" in period_raw else period
    period = datetime.now() - timedelta(days=31) if "1month" in period_raw else period
    period = datetime.now() - timedelta(days=7) if "1week" in period_raw else period
    period = datetime.now() - timedelta(days=1) if "1day" in period_raw else period

    rus_period = "За всё время"
    rus_period = "1 год" if "1year" in period_raw else rus_period
    rus_period = "Последний месяц" if "1month" in period_raw else rus_period
    rus_period = "Последние 7 дней" if "1week" in period_raw else rus_period
    rus_period = "Сегодня" if "1day" in period_raw else rus_period

    with mongo_client(stage) as client:
        mongo_db = client.db_scoring_logs

        for col_ind, collection_name in enumerate(all_collections):
            collection = mongo_db[collection_name]
            query = {
                "$and": [
                    {"$or": [{"created_date": {"$gte": period}}, {"create_date": {"$gte": period}}]},
                    {
                        "$or": [
                            {
                                "$or": [
                                    {
                                        "$and": [
                                            {"response.success": False},
                                            {"response.errorText": {"$ne": None}},
                                            {"response.errorText": {"$ne": ""}},
                                        ]
                                    },
                                    {
                                        "$and": [
                                            {"success": False},
                                            {"response.errorText": {"$ne": None}},
                                            {"response.errorText": {"$ne": ""}},
                                        ]
                                    },
                                    {
                                        "$and": [
                                            {"response.success": False},
                                            {"errorText": {"$ne": None}},
                                            {"errorText": {"$ne": ""}},
                                        ]
                                    },
                                ]
                            },
                            {
                                "$or": [
                                    {
                                        "$and": [
                                            {"response.success": False},
                                            {"response.error_text": {"$ne": None}},
                                            {"response.error_text": {"$ne": ""}},
                                        ]
                                    },
                                    {
                                        "$and": [
                                            {"success": False},
                                            {"response.error_text": {"$ne": None}},
                                            {"response.error_text": {"$ne": ""}},
                                        ]
                                    },
                                    {
                                        "$and": [
                                            {"response.success": False},
                                            {"error_text": {"$ne": None}},
                                            {"error_text": {"$ne": ""}},
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                ]
            }

            stats.append((collection_name.replace("_", "\\_"), len(list(collection.find(query)))))

    return stats, rus_period


async def parse_all_collections_for_errors(stage):
    all_collections = await get_all_collections(stage)
    all_errors = []
    with mongo_client(stage) as client:
        mongo_db = client.db_scoring_logs

        for col_ind, collection_name in enumerate(all_collections):
            collection = mongo_db[collection_name]
            query = {
                "$or": [
                    {
                        "$or": [
                            {
                                "$and": [
                                    {"response.success": False},
                                    {"response.errorText": {"$ne": None}},
                                    {"response.errorText": {"$ne": ""}},
                                ]
                            },
                            {
                                "$and": [
                                    {"success": False},
                                    {"response.errorText": {"$ne": None}},
                                    {"response.errorText": {"$ne": ""}},
                                ]
                            },
                            {
                                "$and": [
                                    {"response.success": False},
                                    {"errorText": {"$ne": None}},
                                    {"errorText": {"$ne": ""}},
                                ]
                            },
                        ]
                    },
                    {
                        "$or": [
                            {
                                "$and": [
                                    {"response.success": False},
                                    {"response.error_text": {"$ne": None}},
                                    {"response.error_text": {"$ne": ""}},
                                ]
                            },
                            {
                                "$and": [
                                    {"success": False},
                                    {"response.error_text": {"$ne": None}},
                                    {"response.error_text": {"$ne": ""}},
                                ]
                            },
                            {
                                "$and": [
                                    {"response.success": False},
                                    {"error_text": {"$ne": None}},
                                    {"error_text": {"$ne": ""}},
                                ]
                            },
                        ],
                    },
                ]
            }

            for ind, doc in enumerate(collection.find(query).sort("create_date", -1).limit(50)):
                if not await is_already_in_db(collection_name, doc.get("applicationId"), doc.get("create_date"), stage):
                    fucking_shit1 = doc.get("response", {}).get("errorText")
                    fucking_shit2 = doc.get("response", {}).get("error_text")
                    fucking_shit3 = doc.get("errorText")
                    fucking_shit4 = doc.get("error_text")
                    get_error_text = str(fucking_shit1 or fucking_shit2 or fucking_shit3 or fucking_shit4)[:300]
                    single_dict = {
                        "collection_name": collection_name,
                        "applicationId": doc.get("applicationId"),
                        "success": False,
                        "productId": doc.get("request", {}).get("productId"),
                        "stage": doc.get("request", {}).get("stage"),
                        "errorText": get_error_text,
                        "errorDate": doc.get("create_date"),
                    }
                    await insert_application_data(
                        single_dict, None, status.HTTP_200_OK, collection_name, doc.get("create_date"), stage
                    )
                    # print(f'#ADDING: {collection_name} | {doc}')
                    all_errors.append(single_dict)

    return all_errors


async def is_already_in_db(collection_name, application_id, create_date, stage):
    with mongo_client(stage) as client:
        mongo_db_1 = client.db_scoring_logs

        collection = mongo_db_1[main_collection_name]
        total_count = collection.count_documents(
            {
                "from_collection": collection_name,
                "applicationId": application_id,
                "create_date_of_error": create_date,
            }
        )
        if total_count > 0:
            return True
        else:
            return False

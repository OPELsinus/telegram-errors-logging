import time

import orjson as json
from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


async def jsonable_middleware(request: Request, call_next):
    request_body = await request.body()
    # async def receive():
    #     return {'type': 'http.request', 'body': request_body}

    # request._receive = receive
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    if response.status_code == 200:
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        try:
            response_data = json.loads(response_body)
            if isinstance(response_data, dict):
                logger.info("Middleware worked with jsonable")
                response = JSONResponse(content=response_data)
                logger.info(
                    {
                        "method": request.method,
                        "path": request.url,
                        "request": json.loads(request_body),
                        "response": response_data,
                        "time": f"{process_time:.2f} seconds",
                    }
                )
            else:
                logger.info("Middleware worked without jsonable")
                response = Response(content=response_body, media_type=response.media_type)
                logger.info(
                    {
                        "method": request.method,
                        "path": request.url,
                        "request": json.loads(request_body),
                        "response": response_data,
                        "time": f"{process_time:.2f} seconds",
                    }
                )
        except json.JSONDecodeError:
            logger.info("Middleware worked without jsonable")
            response = Response(content=response_body, media_type=response.media_type)
            logger.info(
                {
                    "method": request.method,
                    "path": request.url,
                    "request": json.loads(request_body) if request_body else {},
                    "response": response_body,
                    "time": f"{process_time:.2f} seconds",
                }
            )

    return response


HTTP_MIDDLEWARES = [
    jsonable_middleware,
]

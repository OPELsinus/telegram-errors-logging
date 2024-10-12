import asyncio
import time

import aiohttp
import orjson as json
from loguru import logger


class HttpClient:
    session: aiohttp.ClientSession = None

    async def start(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def stop(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def fetch_with_retry(self, url, method="GET", retries=3, timeout=60, headers=None, json_data=None):
        for i in range(retries):
            try:
                start_time = time.time()
                async with self.session.request(
                    method,
                    url,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    headers=headers,
                    json=json_data,
                ) as response:
                    content = await response.content.read()
                    process_time = time.time() - start_time
                    logger.info(
                        {
                            "http_client": "async http",
                            "method": method,
                            "path": url,
                            "request": True if json_data else False,
                            "response": True if content else False,
                            "time": f"{process_time:.2f} seconds",
                        }
                    )
                    if not content:
                        raise ValueError("Empty response received")
                    # Try to parse JSON and return it
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON response: {e.msg}") from e
            except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError) as e:
                if i == retries - 1:
                    raise e
                await asyncio.sleep(1)
            except ValueError as e:  # Handle the JSON decode error or empty response error
                if i == retries - 1:
                    raise e
                await asyncio.sleep(1)

    def __call__(self) -> aiohttp.ClientSession:
        assert self.session is not None
        return self.session


http_client = HttpClient()


def get_http_client() -> HttpClient:
    return http_client

from typing import Any


class SendRequestCall:
    """Send request to other microservices"""

    def __init__(self, http, url: str, request_body: Any = {}, method: str = "POST", retries: int = 2):
        self.http_client = http
        self.request_body = request_body
        self.url = url
        self.headers = {"Content-Type": "application/json"}
        self.method = method.upper()
        self.retries = retries

    async def call_service(self):
        return await self.http_client.fetch_with_retry(
            url=self.url,
            method=self.method,
            retries=self.retries,
            timeout=60000,
            headers=self.headers,
            json_data=self.request_body,
        )


class SendRequestCallFactory:
    """Фабрика для создания объектов SendRequestCall"""

    def __init__(self, http):
        self.http_client = http

    def create(self, url: str, request_body: Any = {}, method: str = "POST", retries: int = 2) -> SendRequestCall:
        return SendRequestCall(
            http=self.http_client, url=url, request_body=request_body, method=method, retries=retries
        )

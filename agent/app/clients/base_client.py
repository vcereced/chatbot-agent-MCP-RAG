from typing import Type, TypeVar
from app.config import config
import logging
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseClient:

    def __init__(self):

        self.client = httpx.AsyncClient(timeout=int(config.REQUEST_TIMEOUT))

    async def get(self, url: str, response_model: type[T]) -> T:

        logger.info("GET %s", url)

        response = await self.client.get(url)

        return self._parse_response(response, response_model)


    async def post(self, url: str, request: BaseModel, response_model: Type[T]) -> T:

        logger.info("POST %s", url)
        response = await self.client.post(
            url,
            json=request.model_dump(),
        )

        return self._parse_response(response, response_model)

            

    def _parse_response(self, response: httpx.Response, response_model: type[T]) -> T:

        response.raise_for_status()
        logger.info("Response %s", response.status_code)

        return response_model.model_validate(response.json())
        
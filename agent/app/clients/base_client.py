from typing import Type, TypeVar
from time import perf_counter
from app.config import config
import httpx
from pydantic import BaseModel
from shared.logging.logger import configure_logging, run_id_context

logger = configure_logging(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseClient:

    def __init__(self):

        self.client = httpx.AsyncClient(timeout=int(config.REQUEST_TIMEOUT))

    async def get(self, url: str, response_model: type[T]) -> T:
        return await self._request("GET", url, response_model)


    async def post(self, url: str, request: BaseModel, response_model: Type[T]) -> T:
        return await self._request(
            "POST",
            url,
            response_model,
            json_body=request.model_dump(),
        )

    async def _request(
        self,
        method: str,
        url: str,
        response_model: type[T],
        json_body: dict | None = None,
    ) -> T:
        started_at = perf_counter()
        logger.info("Outgoing HTTP request method=%s url=%s", method, url)

        try:
            response = await self.client.request(
                method,
                url,
                json=json_body,
                headers=self._request_headers(),
            )
            response.raise_for_status()
            parsed_response = response_model.model_validate(response.json())
        except (httpx.HTTPError, ValueError):
            logger.exception(
                "HTTP request failed method=%s url=%s duration_ms=%.2f",
                method,
                url,
                (perf_counter() - started_at) * 1000,
            )
            raise

        logger.info(
            "HTTP request completed method=%s url=%s status_code=%d duration_ms=%.2f",
            method,
            url,
            response.status_code,
            (perf_counter() - started_at) * 1000,
        )
        return parsed_response

    @staticmethod
    def _request_headers() -> dict[str, str]:
        run_id = run_id_context.get()
        if run_id is None:
            return {}
        return {"X-Run-ID": run_id}

            

        
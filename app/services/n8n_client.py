from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class N8NClient:
    def __init__(self, settings: Settings) -> None:
        timeout = httpx.Timeout(settings.request_timeout_seconds)
        limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
        self.webhook_url = settings.n8n_webhook_url
        self.x_publish_webhook_url = settings.n8n_x_publish_webhook_url
        self.client = httpx.AsyncClient(timeout=timeout, limits=limits)

    async def process_message(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post_json(self.webhook_url, payload, "support")

    async def publish_x_post(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post_json(self.x_publish_webhook_url, payload, "x_publish")

    async def _post_json(self, url: str, payload: dict[str, Any], channel: str) -> dict[str, Any]:
        start = time.perf_counter()
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info("n8n %s request complete in %.2f ms", channel, elapsed_ms)
            return data
        except httpx.TimeoutException as exc:
            logger.exception("n8n %s timeout", channel)
            raise RuntimeError(f"n8n_{channel}_timeout") from exc
        except httpx.HTTPError as exc:
            logger.exception("n8n %s http error", channel)
            raise RuntimeError(f"n8n_{channel}_http_error") from exc
        except ValueError as exc:
            logger.exception("n8n %s invalid json", channel)
            raise RuntimeError(f"n8n_{channel}_invalid_json") from exc

    async def close(self) -> None:
        await self.client.aclose()

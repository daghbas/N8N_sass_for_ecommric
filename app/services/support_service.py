from __future__ import annotations

import hashlib
import logging
import time
from typing import Any

from app.core.config import Settings
from app.services.n8n_client import N8NClient
from app.utils.cache import TTLCache
from app.utils.security import has_prompt_injection_risk, sanitize_text

logger = logging.getLogger(__name__)

SAFE_FALLBACK = {
    "category": "General Inquiry",
    "priority": "Medium",
    "reply": "Thank you for contacting support. We are reviewing your request and will get back to you shortly.",
}

ALLOWED_CATEGORIES = {
    "Order Issue",
    "Refund Request",
    "Technical Support",
    "Complaint",
    "General Inquiry",
}
ALLOWED_PRIORITIES = {"High", "Medium", "Low"}


class SupportService:
    def __init__(self, settings: Settings, n8n_client: N8NClient) -> None:
        self.settings = settings
        self.n8n_client = n8n_client
        self.cache = TTLCache(ttl_seconds=settings.cache_ttl_seconds)

    async def handle_message(self, customer_id: str, message: str) -> tuple[dict[str, Any], int]:
        start = time.perf_counter()

        sanitized_message = sanitize_text(message)
        if has_prompt_injection_risk(sanitized_message):
            logger.warning("Potential prompt injection blocked")
            return {
                **SAFE_FALLBACK,
                "meta": {"reason": "suspicious_input", "cached": False},
            }, 200

        cache_key = hashlib.sha256(sanitized_message.encode("utf-8")).hexdigest()
        cached = self.cache.get(cache_key)
        if cached:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info("request complete from cache in %.2f ms", elapsed_ms)
            return {**cached, "meta": {"cached": True}}, 200

        payload = {
            "customer_id": customer_id,
            "message": sanitized_message,
            "gemini_api_key": self.settings.gemini_api_key,
        }

        try:
            result = await self.n8n_client.process_message(payload)
            normalized = self._normalize_result(result)
            self.cache.set(cache_key, normalized)
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info("request complete in %.2f ms", elapsed_ms)
            return {**normalized, "meta": {"cached": False}}, 200
        except RuntimeError as exc:
            logger.error("processing error: %s", exc)
            return {
                **SAFE_FALLBACK,
                "meta": {"reason": str(exc), "cached": False},
            }, 200

    def _normalize_result(self, data: dict[str, Any]) -> dict[str, str]:
        category = data.get("category", "General Inquiry")
        priority = data.get("priority", "Medium")
        reply = data.get("reply", SAFE_FALLBACK["reply"])

        if category not in ALLOWED_CATEGORIES:
            category = "General Inquiry"
        if priority not in ALLOWED_PRIORITIES:
            priority = "Medium"
        reply = str(reply).strip()[:400] or SAFE_FALLBACK["reply"]

        return {
            "category": category,
            "priority": priority,
            "reply": reply,
        }

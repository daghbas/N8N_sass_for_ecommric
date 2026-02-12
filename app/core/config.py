from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    host: str
    port: int
    log_level: str
    secret_key: str
    database_url: str
    n8n_webhook_url: str
    n8n_x_publish_webhook_url: str
    request_timeout_seconds: float
    max_message_length: int
    cache_ttl_seconds: int
    gemini_api_key: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            secret_key=os.getenv("SECRET_KEY", "dev-secret-key"),
            database_url=os.getenv("DATABASE_URL", "sqlite:///saas_ecommerce.db"),
            n8n_webhook_url=os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/customer-support"),
            n8n_x_publish_webhook_url=os.getenv("N8N_X_PUBLISH_WEBHOOK_URL", "http://localhost:5678/webhook/x-publish"),
            request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "5")),
            max_message_length=int(os.getenv("MAX_MESSAGE_LENGTH", "1200")),
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        )

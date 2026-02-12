from __future__ import annotations

from datetime import UTC, datetime, timedelta
import secrets

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import db


class Company(db.Model):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Store(db.Model):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    store_url: Mapped[str] = mapped_column(String(255), nullable=False)
    external_api_token: Mapped[str] = mapped_column(String(255), nullable=False)
    external_api_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    internal_api_key: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    internal_webhook_token: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    x_handle: Mapped[str] = mapped_column(String(120), default="")
    x_bearer_token: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(30), default="connected")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    @staticmethod
    def generate_internal_api_key() -> str:
        return f"ekm_{secrets.token_urlsafe(24)}"

    @staticmethod
    def generate_webhook_token() -> str:
        return f"wh_{secrets.token_urlsafe(24)}"


class ScheduledPost(db.Model):
    __tablename__ = "scheduled_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    publish_at: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="scheduled")
    external_post_id: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)

    @staticmethod
    def generate(user_id: int, ttl_minutes: int = 30) -> "PasswordResetToken":
        return PasswordResetToken(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now(UTC) + timedelta(minutes=ttl_minutes),
        )

    def is_valid(self) -> bool:
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        return datetime.now(UTC) <= expires

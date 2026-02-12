from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
from pydantic import BaseModel, ValidationError, field_validator

from app.services.support_service import SupportService

support_bp = Blueprint("support", __name__)


class SupportRequest(BaseModel):
    customer_id: str
    message: str

    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("customer_id is required")
        return value[:64]


@support_bp.post("/support")
async def support() -> tuple:
    settings = current_app.config["SETTINGS"]
    service: SupportService = current_app.config["SUPPORT_SERVICE"]

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid_json"}), 400

    try:
        body = SupportRequest.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"error": "validation_error", "details": exc.errors()}), 400

    if len(body.message) > settings.max_message_length:
        return jsonify({"error": "message_too_long"}), 400

    data, status_code = await service.handle_message(body.customer_id, body.message)
    return jsonify(data), status_code

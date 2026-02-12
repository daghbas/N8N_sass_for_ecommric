from __future__ import annotations

import re

SCRIPT_PATTERN = re.compile(r"<\/?script[^>]*>", flags=re.IGNORECASE)
CONTROL_PATTERN = re.compile(r"[\x00-\x1f\x7f]")
INJECTION_HINTS = (
    "ignore previous instructions",
    "system prompt",
    "developer prompt",
    "reveal prompt",
)


def sanitize_text(text: str) -> str:
    sanitized = SCRIPT_PATTERN.sub("", text)
    sanitized = CONTROL_PATTERN.sub("", sanitized)
    return sanitized.strip()


def has_prompt_injection_risk(text: str) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in INJECTION_HINTS)

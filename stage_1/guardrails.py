"""Guardrails: filter sensitive data from user input and from RAG responses.

Uses regex-based detection (no Presidio) to stay compatible with LangChain's
Pydantic v1 requirement. Covers email, phone, card-like numbers, SSN-like patterns.
"""
import re

# Patterns for sensitive data (redacted in order; compiled once)
_REPLACEMENT = "[REDACTED]"

_PATTERNS = [
    # Email
    (re.compile(r"\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b", re.IGNORECASE), "EMAIL"),
    # Phone: international or with spaces/dashes/dots
    (re.compile(r"\+?[\d\s\-().]{10,20}\b"), "PHONE"),
    # Credit-card-like: 4 groups of 4 digits (with optional space or dash)
    (re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"), "CARD"),
    # SSN-like (US)
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN"),
    # IBAN-like: long digit/letter sequence (simplified)
    (re.compile(r"\b[A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{0,4}\b", re.IGNORECASE), "IBAN"),
]


def contains_sensitive(text: str) -> bool:
    """Return True if text contains detectable PII/sensitive data."""
    if not text or not text.strip():
        return False
    for pattern, _ in _PATTERNS:
        if pattern.search(text):
            return True
    return False


def redact_sensitive(text: str, replacement: str = _REPLACEMENT) -> str:
    """Replace sensitive spans with replacement. Use before storing or logging."""
    if not text or not text.strip():
        return text
    out = text
    for pattern, _ in _PATTERNS:
        out = pattern.sub(replacement, out)
    return out


def sanitize_for_display(text: str, max_length: int = 500) -> str:
    """Optional: truncate and ensure no accidental PII in displayed text."""
    out = redact_sensitive(text)
    if len(out) > max_length:
        out = out[: max_length - 3] + "..."
    return out

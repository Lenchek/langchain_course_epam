"""Guardrails: regex-based PII filtering (same as stage_3)."""
import re
_REPLACEMENT = "[REDACTED]"
_PATTERNS = [
    (re.compile(r"\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b", re.IGNORECASE), "EMAIL"),
    (re.compile(r"\+?[\d\s\-().]{10,20}\b"), "PHONE"),
    (re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"), "CARD"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN"),
    (re.compile(r"\b[A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{0,4}\b", re.IGNORECASE), "IBAN"),
]

def contains_sensitive(text: str) -> bool:
    if not text or not text.strip():
        return False
    for pattern, _ in _PATTERNS:
        if pattern.search(text):
            return True
    return False

def redact_sensitive(text: str, replacement: str = _REPLACEMENT) -> str:
    if not text or not text.strip():
        return text
    out = text
    for pattern, _ in _PATTERNS:
        out = pattern.sub(replacement, out)
    return out

def sanitize_for_display(text: str, max_length: int = 500) -> str:
    out = redact_sensitive(text)
    if len(out) > max_length:
        out = out[: max_length - 3] + "..."
    return out

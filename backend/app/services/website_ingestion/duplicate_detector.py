import hashlib


def compute_content_hash(text: str) -> str:
    """Computes SHA256 hash of normalized text."""
    normalized = "".join(text.split()).lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

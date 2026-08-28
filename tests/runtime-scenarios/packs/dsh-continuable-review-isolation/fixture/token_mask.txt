def mask_token(value: str) -> str:
    """Return a display-safe token mask."""
    if not value:
        return ""
    return "*" * max(0, len(value) - 4) + value[-4:]

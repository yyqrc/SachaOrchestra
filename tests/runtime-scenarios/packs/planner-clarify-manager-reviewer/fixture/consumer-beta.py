def read_timeout(config: dict) -> int:
    return int(config["request_timeout_ms"])

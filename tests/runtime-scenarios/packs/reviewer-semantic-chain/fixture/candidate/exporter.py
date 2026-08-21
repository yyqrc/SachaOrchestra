"""包含候选长度限制的导出名称渲染。"""

MAX_NAME_BYTES = 8


def emit_name(name: str) -> str:
    """返回导出器写入的名称。"""
    return name


def checked_emit(name: str) -> str:
    """名称满足配置的输出限制时返回该名称。"""
    if len(name) > MAX_NAME_BYTES:
        raise ValueError("export name exceeds 8 UTF-8 bytes")
    return emit_name(name)

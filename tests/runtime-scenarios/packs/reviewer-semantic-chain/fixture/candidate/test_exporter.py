"""候选长度限制随附的聚焦测试。"""

from exporter import checked_emit


assert checked_emit("12345678") == "12345678"

try:
    checked_emit("123456789")
except ValueError:
    pass
else:
    raise AssertionError("nine-character names must be rejected")

"""导出单个名称的命令行入口。"""

import sys

from exporter import emit_name


if __name__ == "__main__":
    print(emit_name(sys.argv[1]))

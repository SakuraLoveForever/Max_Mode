"""Max Mode - 应用入口"""

import sys
import os

# 确保 src 目录在 path 中
_src_dir = os.path.dirname(os.path.abspath(__file__))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from app import MaxModeApp


def main():
    app = MaxModeApp()
    app.run()


if __name__ == "__main__":
    main()

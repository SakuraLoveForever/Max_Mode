"""Max Mode - 应用入口

用于: python main.py (从 src 目录运行)
     python -m src.main (从项目根目录运行)
"""

import sys
import os

# 确保 src 包可导入
_src_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_src_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from src.app import MaxModeApp


def main():
    app = MaxModeApp()
    app.run()


if __name__ == "__main__":
    main()

"""Max Mode - PyInstaller 打包脚本

用法: python build_exe.py

输出: dist/MaxMode.exe (单个可执行文件)
"""

import os
import sys
import subprocess


def build():
    project_root = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_root, "dist")

    # PyInstaller 参数
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "MaxMode",
        "--collect-all", "tkinter",
        "--clean",
        "--noconfirm",
        "--distpath", dist_dir,
    ]

    # 入口脚本
    entry = os.path.join(project_root, "run.py")
    cmd.append(entry)

    print("=" * 60)
    print("  Max Mode - 开始打包")
    print("=" * 60)
    print(f"  入口: {entry}")
    print(f"  输出: {os.path.join(dist_dir, 'MaxMode.exe')}")
    print()

    result = subprocess.run(cmd, cwd=project_root)
    if result.returncode == 0:
        print()
        print("=" * 60)
        print(f"  [OK] Build success!")
        print(f"  EXE: {os.path.join(dist_dir, 'MaxMode.exe')}")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("  [FAIL] Build failed, check errors above")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    build()

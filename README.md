# Max Mode — Claude Code 模式切换器

一个 Windows 桌面工具，用于创建和管理 Claude Code 的不同运行模式。每个模式可以绑定不同的**思考强度**、**权限级别**和**模型**，一键生成启动脚本。

## 功能

- 🎛 **自定义模式** — 自由组合思考强度 (low/medium/high/xhigh) + 权限模式 (default/accept-edits/bypass/plan) + 模型 (opus/sonnet/haiku)
- ⚡ **生成启动脚本** — 为每个模式生成独立的 `.bat` 批处理文件，双击即可启动
- ⚙ **生成项目配置** — 直接为项目生成 `.claude/settings.json`，在项目中自动应用模式
- 💾 **持久化存储** — 模式配置保存在 `%APPDATA%/MaxMode/modes.json`

## 运行

```bash
# 直接运行 (需要 Python 3.8+)
python run.py

# 打包为 EXE (需要 PyInstaller)
pip install pyinstaller
python build_exe.py

# 生成的 EXE 在 dist/MaxMode.exe
```

## 使用

1. 点击 **新建模式** 创建配置
2. 在列表中选择一个模式
3. 点击 **生成启动脚本** 创建 `.bat` 文件
4. 双击生成的 `.bat` 启动该模式下的 Claude Code

## 依赖

- Python 3.8+ (仅开发/运行源码时需要)
- tkinter (Python 标准库自带)
- PyInstaller (仅打包时需要)

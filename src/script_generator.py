"""Max Mode - 脚本生成器：生成启动 .bat 文件"""

import os
import re
import json
from typing import Optional

from .constants import Mode


class ScriptGenerator:
    """为指定模式生成 Windows 批处理启动脚本"""

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """清除文件名中的非法字符"""
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        sanitized = sanitized.strip().replace(" ", "_")
        return sanitized or "mode"

    @classmethod
    def generate_bat(cls, mode: Mode, output_dir: str, project_dir: str = "") -> str:
        """
        生成 .bat 启动脚本 — 使用 Claude Code 原生 CLI 参数

        Args:
            mode: 模式对象
            output_dir: 输出目录
            project_dir: 目标项目目录（可选，留空则使用当前目录）

        Returns:
            生成的 .bat 文件完整路径
        """
        filename = f"Claude_{cls.sanitize_filename(mode.name)}.bat"
        filepath = os.path.join(output_dir, filename)

        # ── 构建 claude CLI 参数 ──
        cli_args = []

        # 模型 (--model)
        if mode.model != "default":
            cli_args.append(f"--model {mode.model}")

        # 思考强度 (--effort)
        cli_args.append(f"--effort {mode.effort_level}")

        # 权限模式 (--permission-mode)
        if mode.permission_mode != "default":
            cli_args.append(f"--permission-mode {mode.permission_mode}")

        cli_flags = " ".join(cli_args)

        # ── 生成脚本内容 ──
        lines = [
            "@echo off",
            "setlocal",
            "",
            "REM =======================================================",
            f"REM  Max Mode Launcher - {mode.name}",
            f"REM  Effort:  {mode.effort_level}",
            f"REM  Perm:    {mode.permission_mode}",
            f"REM  Model:   {mode.model}",
            f"REM  CLI:     claude {cli_flags}",
            "REM =======================================================",
            "",
            "echo.",
            "echo   ==========================================",
            "echo     Max Mode - Claude Code Launcher",
            "echo   ------------------------------------------",
            f"echo     Mode:    {mode.name}",
            f"echo     Effort:  {mode.effort_level}",
            f"echo     Perm:    {mode.permission_mode}",
            f"echo     Model:   {mode.model}",
            "echo   ==========================================",
            "echo.",
        ]

        # 切换到项目目录
        if project_dir:
            lines.append(f'cd /d "{project_dir}"')
            lines.append(f"echo   Project: {project_dir}")
            lines.append("echo.")

        # 启动 Claude Code（使用原生 CLI 参数）
        lines.extend([
            "echo   Starting Claude Code with mode settings...",
            "echo.",
            "",
            f"claude {cli_flags}",
            "",
            "REM Fallback to npx if claude is not in PATH",
            "if %ERRORLEVEL% NEQ 0 (",
            "    echo   'claude' not found, trying npx...",
            f"    npx @anthropic-ai/claude-code {cli_flags}",
            ")",
            "",
            "echo.",
            "echo   Claude Code exited.",
            "pause",
        ])

        content = "\n".join(lines) + "\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

    @classmethod
    def generate_settings_json(cls, mode: Mode, output_dir: str) -> str:
        """
        生成项目级 .claude/settings.json

        Claude Code 会在启动时读取此文件，自动应用配置。
        这是另一种启动方式 — 不需要 CLI 参数，进入项目目录直接运行 claude 即可。

        Returns:
            生成的 settings.json 文件路径
        """
        claude_dir = os.path.join(output_dir, ".claude")
        os.makedirs(claude_dir, exist_ok=True)
        filepath = os.path.join(claude_dir, "settings.json")

        settings = {
            "effortLevel": mode.effort_level,
        }

        if mode.permission_mode == "bypass":
            settings["permissionMode"] = "bypass"
        elif mode.permission_mode != "default":
            settings["permissionMode"] = mode.permission_mode

        if mode.model != "default":
            settings["model"] = mode.model

        # 如果已有 settings.json，合并而非覆盖
        existing = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        existing.update(settings)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        return filepath

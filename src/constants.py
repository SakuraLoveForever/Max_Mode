"""Max Mode - 常量定义与数据模型"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import uuid
from datetime import datetime, timezone


# ── 应用元信息 ──────────────────────────────────────────────
APP_NAME = "Max Mode"
APP_VERSION = "1.0.0"
APP_DATA_DIR = "MaxMode"  # %APPDATA% 下的子目录

# ── Claude Code 可用选项 ────────────────────────────────────
EFFORT_LEVELS = ["low", "medium", "high", "xhigh"]
EFFORT_LABELS = {
    "low":    "低强度 (low)    — 快速回答，最少推理",
    "medium": "标准强度 (medium) — 平衡速度与深度",
    "high":   "高强度 (high)   — 深度推理",
    "xhigh":  "极强强度 (xhigh) — 最大推理，最复杂任务",
}

PERMISSION_MODES = ["acceptEdits", "default", "auto", "bypassPermissions", "dontAsk", "plan"]
PERMISSION_LABELS = {
    "acceptEdits":        "常规 (acceptEdits)         — 自动批准文件修改，其余询问",
    "default":            "标准 (default)             — 每次操作都询问权限",
    "auto":               "自动 (auto)                — 自动批准大部分操作",
    "bypassPermissions":  "绕过 (bypassPermissions)   — 跳过所有权限确认",
    "dontAsk":            "静默 (dontAsk)             — 不弹出权限提示",
    "plan":               "计划 (plan)                — 仅规划，不执行文件操作",
}

MODELS = ["default", "opus", "sonnet", "haiku"]
MODEL_LABELS = {
    "default": "跟随系统默认",
    "opus":    "Claude Opus  — 最强能力",
    "sonnet":  "Claude Sonnet — 速度与质量平衡",
    "haiku":   "Claude Haiku — 最快速度",
}


@dataclass
class Mode:
    """单个模式的数据模型"""
    name: str
    effort_level: str = "medium"
    permission_mode: str = "acceptEdits"
    model: str = "default"
    description: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> dict:
        return asdict(self)

    # 旧值 → 新值迁移表（兼容早期保存的数据）
    _PERMISSION_MIGRATION = {
        "accept-edits": "acceptEdits",
        "bypass": "bypassPermissions",
    }

    @classmethod
    def from_dict(cls, d: dict) -> "Mode":
        # 兼容旧数据可能缺少字段
        defaults = {
            "model": "default",
            "description": "",
        }
        for k, v in defaults.items():
            d.setdefault(k, v)

        # 迁移旧权限值到新 CLI 支持的格式
        if "permission_mode" in d and d["permission_mode"] in cls._PERMISSION_MIGRATION:
            d["permission_mode"] = cls._PERMISSION_MIGRATION[d["permission_mode"]]

        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def validate(self) -> Optional[str]:
        """验证模式配置，返回错误信息或 None"""
        if not self.name.strip():
            return "模式名称不能为空"
        if self.effort_level not in EFFORT_LEVELS:
            return f"无效的思考强度: {self.effort_level}"
        if self.permission_mode not in PERMISSION_MODES:
            return f"无效的权限模式: {self.permission_mode}"
        if self.model not in MODELS:
            return f"无效的模型: {self.model}"
        return None

    @property
    def effort_display(self) -> str:
        return EFFORT_LABELS.get(self.effort_level, self.effort_level)

    @property
    def permission_display(self) -> str:
        return PERMISSION_LABELS.get(self.permission_mode, self.permission_mode)

    @property
    def model_display(self) -> str:
        return MODEL_LABELS.get(self.model, self.model)

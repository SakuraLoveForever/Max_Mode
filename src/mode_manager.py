"""Max Mode - 模式管理器：CRUD + JSON 持久化"""

import json
import os
from typing import List, Optional

from .constants import Mode, APP_DATA_DIR


class ModeManager:
    """管理所有模式的加载、保存、增删改查"""

    def __init__(self):
        self._modes: List[Mode] = []
        self._data_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_DATA_DIR)
        self._data_file = os.path.join(self._data_dir, "modes.json")
        self._ensure_data_dir()
        self.load()

    # ── 文件操作 ──────────────────────────────────────────

    def _ensure_data_dir(self) -> None:
        """确保数据目录存在"""
        os.makedirs(self._data_dir, exist_ok=True)

    @property
    def data_file_path(self) -> str:
        return self._data_file

    @property
    def data_dir_path(self) -> str:
        return self._data_dir

    def load(self) -> None:
        """从 JSON 文件加载模式列表"""
        if not os.path.exists(self._data_file):
            self._modes = []
            return
        try:
            with open(self._data_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, list):
                self._modes = [Mode.from_dict(item) for item in raw]
            else:
                self._modes = []
        except (json.JSONDecodeError, IOError):
            self._modes = []

    def save(self) -> None:
        """保存模式列表到 JSON 文件"""
        self._ensure_data_dir()
        data = [m.to_dict() for m in self._modes]
        with open(self._data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ── CRUD ──────────────────────────────────────────────

    @property
    def modes(self) -> List[Mode]:
        return list(self._modes)

    def get(self, mode_id: str) -> Optional[Mode]:
        for m in self._modes:
            if m.id == mode_id:
                return m
        return None

    def add(self, mode: Mode) -> None:
        """添加新模式"""
        self._modes.append(mode)
        self.save()

    def update(self, mode_id: str, updated: Mode) -> bool:
        """更新指定模式，返回是否成功"""
        for i, m in enumerate(self._modes):
            if m.id == mode_id:
                updated.id = mode_id
                updated.created_at = m.created_at
                from datetime import datetime, timezone
                updated.updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                self._modes[i] = updated
                self.save()
                return True
        return False

    def delete(self, mode_id: str) -> bool:
        """删除指定模式，返回是否成功"""
        for i, m in enumerate(self._modes):
            if m.id == mode_id:
                self._modes.pop(i)
                self.save()
                return True
        return False

    def count(self) -> int:
        return len(self._modes)

"""Max Mode - 模式编辑对话框"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .constants import Mode, EFFORT_LEVELS, EFFORT_LABELS, PERMISSION_MODES, PERMISSION_LABELS, MODELS, MODEL_LABELS


class ModeEditorDialog(tk.Toplevel):
    """弹出窗口：创建或编辑一个模式"""

    def __init__(self, parent, mode: Optional[Mode] = None):
        super().__init__(parent)
        self._mode = mode
        self._result: Optional[Mode] = None

        self.title("编辑模式" if mode else "新建模式")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # 居中放置
        self.geometry("520x480")
        self._center_on_parent(parent)

        self._build_ui()

        if mode:
            self._populate(mode)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    # ── 布局 ──────────────────────────────────────────────

    def _build_ui(self):
        pad = {"padx": 16, "pady": 4}

        # 标题
        header = ttk.Label(self, text="模式配置", font=("Microsoft YaHei UI", 13, "bold"))
        header.pack(pady=(16, 12))

        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, **pad)

        # ── 名称 ──
        ttk.Label(main, text="模式名称 *", font=("Microsoft YaHei UI", 9)).pack(anchor=tk.W, **pad)
        self._name_var = tk.StringVar()
        ttk.Entry(main, textvariable=self._name_var, width=52).pack(fill=tk.X, **pad)

        # ── 思考强度 ──
        ttk.Label(main, text="思考强度 (Effort Level)", font=("Microsoft YaHei UI", 9)).pack(anchor=tk.W, **pad)
        self._effort_var = tk.StringVar(value=EFFORT_LEVELS[1])  # 默认 medium
        effort_combo = ttk.Combobox(main, textvariable=self._effort_var,
                                    values=list(EFFORT_LABELS.values()), state="readonly", width=49)
        effort_combo.pack(fill=tk.X, **pad)

        # ── 权限模式 ──
        ttk.Label(main, text="权限模式 (Permission Mode)", font=("Microsoft YaHei UI", 9)).pack(anchor=tk.W, **pad)
        self._perm_var = tk.StringVar(value=PERMISSION_LABELS[PERMISSION_MODES[0]])
        perm_combo = ttk.Combobox(main, textvariable=self._perm_var,
                                  values=list(PERMISSION_LABELS.values()), state="readonly", width=49)
        perm_combo.pack(fill=tk.X, **pad)

        # ── 模型 ──
        ttk.Label(main, text="模型 (Model)", font=("Microsoft YaHei UI", 9)).pack(anchor=tk.W, **pad)
        self._model_var = tk.StringVar(value=MODEL_LABELS[MODELS[0]])
        model_combo = ttk.Combobox(main, textvariable=self._model_var,
                                   values=list(MODEL_LABELS.values()), state="readonly", width=49)
        model_combo.pack(fill=tk.X, **pad)

        # ── 描述 ──
        ttk.Label(main, text="描述（可选）", font=("Microsoft YaHei UI", 9)).pack(anchor=tk.W, **pad)
        self._desc_text = tk.Text(main, height=4, width=50, font=("Microsoft YaHei UI", 9))
        self._desc_text.pack(fill=tk.X, **pad)

        # ── 按钮 ──
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=(8, 16))

        ttk.Button(btn_frame, text="保存", command=self._on_save, width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="取消", command=self._on_cancel, width=12).pack(side=tk.LEFT, padx=6)

    # ── 辅助方法 ──────────────────────────────────────────

    @staticmethod
    def _extract_key_from_label(label: str, labels_dict: dict) -> str:
        """从显示标签中反查键值"""
        for key, lbl in labels_dict.items():
            if lbl == label:
                return key
        return list(labels_dict.keys())[0] if labels_dict else ""

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _populate(self, mode: Mode):
        self._name_var.set(mode.name)
        self._effort_var.set(EFFORT_LABELS.get(mode.effort_level, mode.effort_level))
        self._perm_var.set(PERMISSION_LABELS.get(mode.permission_mode, mode.permission_mode))
        self._model_var.set(MODEL_LABELS.get(mode.model, mode.model))
        self._desc_text.insert("1.0", mode.description)

    # ── 事件处理 ──────────────────────────────────────────

    def _on_save(self):
        name = self._name_var.get().strip()
        effort = self._extract_key_from_label(self._effort_var.get(), EFFORT_LABELS)
        perm = self._extract_key_from_label(self._perm_var.get(), PERMISSION_LABELS)
        model = self._extract_key_from_label(self._model_var.get(), MODEL_LABELS)
        description = self._desc_text.get("1.0", "end-1c").strip()

        # 验证
        if not name:
            self._show_error("模式名称不能为空！")
            return

        self._result = Mode(
            id=self._mode.id if self._mode else "",
            name=name,
            effort_level=effort,
            permission_mode=perm,
            model=model,
            description=description,
            created_at=self._mode.created_at if self._mode else "",
            updated_at="",
        )
        self.destroy()

    def _on_cancel(self):
        self._result = None
        self.destroy()

    def _show_error(self, message: str):
        messagebox.showerror("输入错误", message, parent=self)

    @property
    def result(self) -> Optional[Mode]:
        return self._result

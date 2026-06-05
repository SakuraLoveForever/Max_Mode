"""Max Mode - 主应用窗口"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

from .constants import Mode, APP_NAME, APP_VERSION
from .mode_manager import ModeManager
from .script_generator import ScriptGenerator
from .mode_editor import ModeEditorDialog


class MaxModeApp:
    """主窗口应用"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("720x560")
        self.root.minsize(640, 460)
        self.root.resizable(True, True)

        self._manager = ModeManager()
        self._selected_id: Optional[str] = None
        self._script_out_dir: str = os.path.join(os.path.expanduser("~"), "Desktop")
        self._project_dir: str = "."  # 默认当前目录

        self._build_ui()
        self._refresh_list()

        self.root.update_idletasks()
        self._center_window()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── CLI 参数 ─────────────────────────────────────────

    @staticmethod
    def _build_cli_args(mode: Mode) -> list:
        args = []
        if mode.model != "default":
            args.extend(["--model", mode.model])
        args.extend(["--effort", mode.effort_level])
        if mode.permission_mode != "default":
            args.extend(["--permission-mode", mode.permission_mode])
        return args

    # ── 启动 Claude Code ──────────────────────────────────

    def _on_launch_claude(self):
        mode = self._get_selected_mode()
        if not mode:
            messagebox.showinfo("提示", "请先在列表中选择一个模式")
            return

        project_dir = self._project_dir_var.get().strip()
        if not project_dir or project_dir == ".":
            project_dir = os.getcwd()
            display_dir = "当前目录"
        else:
            project_dir = os.path.abspath(project_dir)
            display_dir = project_dir

        if not os.path.isdir(project_dir):
            messagebox.showerror("错误", f"目录不存在:\n{project_dir}", parent=self.root)
            return

        cli_args = self._build_cli_args(mode)
        cmd = ["claude"] + cli_args

        try:
            if sys.platform == "win32":
                subprocess.Popen(
                    ["start", f"Claude Code - {mode.name}"] + cmd,
                    shell=True,
                    cwd=project_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
            else:
                subprocess.Popen(cmd, cwd=project_dir)

            self._update_status(f"已启动: {mode.name} | 目录: {display_dir} | claude {' '.join(cli_args)}")

        except FileNotFoundError:
            try:
                npx_cmd = ["npx", "@anthropic-ai/claude-code"] + cli_args
                if sys.platform == "win32":
                    subprocess.Popen(
                        ["start", f"Claude Code - {mode.name}"] + npx_cmd,
                        shell=True,
                        cwd=project_dir,
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                    )
                else:
                    subprocess.Popen(npx_cmd, cwd=project_dir)
                self._update_status(f"已通过 npx 启动: {mode.name}")
            except Exception as e:
                messagebox.showerror("启动失败",
                    f"无法找到 claude 命令。\n\n"
                    f"请确认已安装 Claude Code:\n  npm install -g @anthropic-ai/claude-code\n\n"
                    f"错误: {e}", parent=self.root)
        except Exception as e:
            messagebox.showerror("启动失败", str(e), parent=self.root)

    # ── UI 构建 ──────────────────────────────────────────

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("vista" if "vista" in style.theme_names() else "default")

        # ── 顶部标题栏 ──
        header = ttk.Frame(self.root, padding=12)
        header.pack(fill=tk.X)
        ttk.Label(header, text=APP_NAME, font=("Microsoft YaHei UI", 16, "bold")).pack(side=tk.LEFT)
        ttk.Label(header, text=f"v{APP_VERSION}", font=("Microsoft YaHei UI", 8),
                  foreground="gray").pack(side=tk.LEFT, padx=8)
        ttk.Label(header, text="Claude Code 模式切换器",
                  font=("Microsoft YaHei UI", 9), foreground="#555").pack(side=tk.LEFT, padx=6)

        # ── 主内容区（左右分栏）──
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        # === 左侧：模式列表 ===
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="已保存的模式", font=("Microsoft YaHei UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 6))

        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set,
            font=("Microsoft YaHei UI", 10),
            selectmode=tk.SINGLE, activestyle="none",
            highlightthickness=1, highlightbackground="#ccc",
        )
        self._listbox.pack(fill=tk.BOTH, expand=True)
        self._listbox.bind("<<ListboxSelect>>", self._on_list_select)
        scrollbar.config(command=self._listbox.yview)

        # === 右侧：模式详情 ===
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        self._detail_frame = ttk.LabelFrame(right_frame, text="模式详情", padding=12)
        self._detail_frame.pack(fill=tk.BOTH, expand=True)

        # 模式名称
        self._lbl_name = ttk.Label(self._detail_frame, text="选择一个模式",
                                   font=("Microsoft YaHei UI", 13, "bold"))
        self._lbl_name.pack(anchor=tk.W, pady=(0, 8))

        # effort / perm / model
        self._lbl_effort = ttk.Label(self._detail_frame, text="", font=("Microsoft YaHei UI", 9))
        self._lbl_effort.pack(anchor=tk.W, pady=2)
        self._lbl_permission = ttk.Label(self._detail_frame, text="", font=("Microsoft YaHei UI", 9))
        self._lbl_permission.pack(anchor=tk.W, pady=2)
        self._lbl_model = ttk.Label(self._detail_frame, text="", font=("Microsoft YaHei UI", 9))
        self._lbl_model.pack(anchor=tk.W, pady=2)

        ttk.Separator(self._detail_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # 描述
        self._lbl_desc = ttk.Label(self._detail_frame, text="", font=("Microsoft YaHei UI", 9),
                                   foreground="#444", wraplength=380)
        self._lbl_desc.pack(anchor=tk.W)

        ttk.Separator(self._detail_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # ── 项目目录选择 ──
        dir_frame = ttk.Frame(self._detail_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(dir_frame, text="启动目录:", font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT)

        self._project_dir_var = tk.StringVar(value=".")
        self._dir_entry = ttk.Entry(dir_frame, textvariable=self._project_dir_var,
                                    font=("Microsoft YaHei UI", 9), width=28)
        self._dir_entry.pack(side=tk.LEFT, padx=(6, 4), fill=tk.X, expand=True)

        ttk.Button(dir_frame, text="浏览...", command=self._on_browse_dir, width=7).pack(side=tk.LEFT)

        ttk.Label(self._detail_frame, text="（输入 . 表示当前目录，或点击浏览选择项目文件夹）",
                  font=("Microsoft YaHei UI", 7), foreground="#888").pack(anchor=tk.W, pady=(0, 6))

        # ── 命令行预览 ──
        cmd_frame = ttk.Frame(self._detail_frame)
        cmd_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(cmd_frame, text="CLI:", font=("Microsoft YaHei UI", 9, "bold")).pack(side=tk.LEFT)
        self._cmd_preview_var = tk.StringVar()
        ttk.Label(cmd_frame, textvariable=self._cmd_preview_var,
                  font=("Consolas", 8), foreground="#555").pack(side=tk.LEFT, padx=6)

        # ── LAUNCH 按钮 ──
        self._btn_launch = ttk.Button(
            self._detail_frame, text="START - 启动 Claude Code",
            command=self._on_launch_claude,
        )
        self._btn_launch.pack(fill=tk.X, ipady=8)
        self._btn_launch.configure(state=tk.DISABLED)

        # ── 次级按钮 ──
        sub_frame = ttk.Frame(self._detail_frame)
        sub_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(sub_frame, text="生成 .bat 脚本", command=self._on_generate_script).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(sub_frame, text="生成 settings.json", command=self._on_generate_settings).pack(side=tk.LEFT)

        # ── 底部工具栏 ──
        toolbar = ttk.Frame(self.root, padding=(12, 8))
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="+ 新建模式", command=self._on_new_mode).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(toolbar, text="编辑模式", command=self._on_edit_mode).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(toolbar, text="删除模式", command=self._on_delete_mode).pack(side=tk.LEFT, padx=(0, 6))

        # ── 状态栏 ──
        status = ttk.Frame(self.root, padding=(12, 6))
        status.pack(fill=tk.X)
        self._status_var = tk.StringVar(value=f"配置: {self._manager.data_file_path}")
        ttk.Label(status, textvariable=self._status_var, font=("Microsoft YaHei UI", 8),
                  foreground="#888").pack(side=tk.LEFT)
        ttk.Label(status, text=f"共 {self._manager.count()} 个模式",
                  font=("Microsoft YaHei UI", 8), foreground="#888").pack(side=tk.RIGHT)

    # ── 列表操作 ──────────────────────────────────────────

    def _refresh_list(self):
        self._listbox.delete(0, tk.END)
        for m in self._manager.modes:
            self._listbox.insert(tk.END, f"  {m.name}")
        if self._selected_id:
            for i, m in enumerate(self._manager.modes):
                if m.id == self._selected_id:
                    self._listbox.selection_set(i)
                    self._listbox.see(i)
                    break
            else:
                self._selected_id = None
                self._clear_detail()

    def _clear_detail(self):
        self._lbl_name.config(text="选择一个模式")
        self._lbl_effort.config(text="")
        self._lbl_permission.config(text="")
        self._lbl_model.config(text="")
        self._lbl_desc.config(text="")
        self._cmd_preview_var.set("")
        self._btn_launch.configure(state=tk.DISABLED)

    def _show_detail(self, mode: Mode):
        self._lbl_name.config(text=mode.name)
        self._lbl_effort.config(text=f"思考强度: {mode.effort_level}")
        self._lbl_permission.config(text=f"权限模式: {mode.permission_mode}")
        self._lbl_model.config(text=f"模型: {mode.model}")
        self._lbl_desc.config(text=mode.description if mode.description else "")
        self._btn_launch.configure(state=tk.NORMAL)
        self._update_cmd_preview(mode)

    def _update_cmd_preview(self, mode: Mode):
        args = self._build_cli_args(mode)
        self._cmd_preview_var.set(f"claude {' '.join(args)}")

    # ── 事件 ─────────────────────────────────────────────

    def _on_list_select(self, event=None):
        sel = self._listbox.curselection()
        if not sel:
            return
        modes = self._manager.modes
        idx = sel[0]
        if 0 <= idx < len(modes):
            self._selected_id = modes[idx].id
            self._show_detail(modes[idx])

    def _on_browse_dir(self):
        d = filedialog.askdirectory(title="选择项目目录", parent=self.root)
        if d:
            self._project_dir_var.set(d)

    def _on_new_mode(self):
        dialog = ModeEditorDialog(self.root)
        self.root.wait_window(dialog)
        if dialog.result:
            m = dialog.result
            import uuid
            new_mode = Mode(
                id=uuid.uuid4().hex[:12],
                name=m.name, effort_level=m.effort_level,
                permission_mode=m.permission_mode, model=m.model,
                description=m.description,
            )
            self._manager.add(new_mode)
            self._selected_id = new_mode.id
            self._refresh_list()

    def _on_edit_mode(self):
        mode = self._get_selected_mode()
        if not mode:
            messagebox.showinfo("提示", "请先选择模式")
            return
        dialog = ModeEditorDialog(self.root, mode)
        self.root.wait_window(dialog)
        if dialog.result:
            self._manager.update(mode.id, dialog.result)
            self._refresh_list()

    def _on_delete_mode(self):
        mode = self._get_selected_mode()
        if not mode:
            messagebox.showinfo("提示", "请先选择模式")
            return
        if messagebox.askyesno("确认删除", f"确定删除「{mode.name}」？", parent=self.root):
            self._manager.delete(mode.id)
            self._selected_id = None
            self._refresh_list()
            self._clear_detail()

    def _on_generate_script(self):
        mode = self._get_selected_mode()
        if not mode:
            messagebox.showinfo("提示", "请先选择模式")
            return
        try:
            path = ScriptGenerator.generate_bat(mode, self._script_out_dir)
            messagebox.showinfo("完成", f"脚本已生成:\n{path}", parent=self.root)
        except Exception as e:
            messagebox.showerror("失败", str(e), parent=self.root)

    def _on_generate_settings(self):
        mode = self._get_selected_mode()
        if not mode:
            messagebox.showinfo("提示", "请先选择模式")
            return
        d = filedialog.askdirectory(title="选择项目目录", parent=self.root)
        if not d:
            return
        try:
            path = ScriptGenerator.generate_settings_json(mode, d)
            messagebox.showinfo("完成", f"已生成:\n{path}", parent=self.root)
        except Exception as e:
            messagebox.showerror("失败", str(e), parent=self.root)

    def _on_close(self):
        self.root.destroy()

    # ── 辅助 ─────────────────────────────────────────────

    def _get_selected_mode(self) -> Optional[Mode]:
        if not self._selected_id:
            return None
        return self._manager.get(self._selected_id)

    def _update_status(self, msg: str):
        self._status_var.set(msg)

    def _center_window(self):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        self.root.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def run(self):
        self.root.mainloop()

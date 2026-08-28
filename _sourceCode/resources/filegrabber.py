# -*- coding: utf-8 -*-
import os
import sys

application_path = ''
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

import json
import shutil
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog

# ==================== 黑名单 ====================
BLACKLIST = [
    "cubemaps",
    "shaders",
    "assets/systems/effects/smoke.bundle",
    "assets/systems/effects/muzzleflash/muzzleflash.bundle",
    "assets/systems/effects/heathaze/defaultheathaze.bundle",
    "assets/content/weapons/animations/simple_animations.bundle",
    "assets/content/weapons/animations/spirit_animations.bundle",
    "assets/content/weapons/weapon_root_anim_fix.bundle",
    "assets/commonassets/physics/physicsmaterials.bundle",
    "assets/content/weapons/wip/kibas tuning prefabs/muzzlejets_templates/default_assets.bundle",
    "assets/content/audio/blendoptions/assets.bundle",
    "assets/content/weapons/additional_hands/client_assets.bundle",
]

class TarkovFileCopyTool(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("塔科夫文件批量导出工具")
        self.geometry("1000x800")
        self.windows_data = None

        # ========== 左侧面板 ==========
        left_frame = ctk.CTkFrame(self)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # EFT 文件夹
        ctk.CTkLabel(left_frame, text="选择 EFT 游戏文件夹：").pack()
        self.eft_folder_entry = ctk.CTkEntry(left_frame, width=300)
        self.eft_folder_entry.pack(pady=5)
        ctk.CTkButton(left_frame, text="浏览...", command=self.browse_eft_folder).pack(pady=5)

        # 导出文件夹
        ctk.CTkLabel(left_frame, text="选择导出文件夹：").pack()
        self.export_folder_entry = ctk.CTkEntry(left_frame, width=300)
        self.export_folder_entry.pack(pady=5)
        ctk.CTkButton(left_frame, text="浏览...", command=self.browse_export_folder).pack(pady=5)

        # ---------- 新增：手动输入 Bundle 名称 ----------
        ctk.CTkLabel(left_frame, text="或手动输入 Bundle 名称（每行一个）：").pack(pady=(10,0))
        self.input_textbox = ctk.CTkTextbox(left_frame, height=100, width=300)
        self.input_textbox.pack(pady=5, fill="x")

        self.export_input_button = ctk.CTkButton(
            left_frame, text="导出输入的 Bundle", command=self.export_from_input
        )
        self.export_input_button.pack(pady=5)

        # 原有选择导出的按钮（从列表框选中）
        self.copy_button = ctk.CTkButton(
            left_frame, text="导出选中的 Bundle", command=self.copy_selected_bundle, state="disabled"
        )
        self.copy_button.pack(pady=10)

        # ========== 右侧面板 ==========
        right_frame = ctk.CTkFrame(self)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(right_frame, text="搜索 Bundle：").pack(pady=5)
        self.search_entry = ctk.CTkEntry(right_frame, width=300)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_bundles)

        self.bundle_listbox = tk.Listbox(
            right_frame,
            selectmode=tk.MULTIPLE,
            height=30,
            font=("Consolas", 10)
        )
        self.bundle_listbox.pack(fill="both", expand=True)
        self.bundle_listbox.bind("<<ListboxSelect>>", self.on_bundle_select)

        # 日志框
        self.logging_text = ctk.CTkTextbox(right_frame, height=200, state="disabled")
        self.logging_text.pack(fill="x", expand=False, pady=5)

        # 配置文件
        self.config_path = os.path.join(os.path.curdir, "WeaponAIOTool_Paths.json")
        self.load_config()

    def log(self, message):
        self.logging_text.configure(state="normal")
        self.logging_text.insert("end", f"{message}\n")
        self.logging_text.see("end")
        self.logging_text.configure(state="disabled")

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.eft_folder_entry.delete(0, "end")
                    self.eft_folder_entry.insert(0, config.get("eft_folder", ""))
                    self.export_folder_entry.delete(0, "end")
                    self.export_folder_entry.insert(0, config.get("export_folder", ""))
                    if config.get("eft_folder") and os.path.exists(config.get("eft_folder")):
                        self.load_windows_json()
            except Exception as e:
                self.log(f"加载配置文件出错：{e}")

    def save_config(self):
        try:
            config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            config["eft_folder"] = self.eft_folder_entry.get()
            config["export_folder"] = self.export_folder_entry.get()
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.log(f"保存配置文件出错：{e}")

    def browse_eft_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.eft_folder_entry.delete(0, "end")
            self.eft_folder_entry.insert(0, folder)
            self.save_config()
            self.load_windows_json()

    def browse_export_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.export_folder_entry.delete(0, "end")
            self.export_folder_entry.insert(0, folder)
            self.save_config()

    def load_windows_json(self):
        eft_folder = self.eft_folder_entry.get()
        windows_json_path = os.path.join(eft_folder, "EscapeFromTarkov_Data", "StreamingAssets", "Windows", "windows.json")
        if not os.path.exists(windows_json_path):
            self.log("错误：未找到 windows.json 文件。")
            return
        try:
            with open(windows_json_path, "r", encoding="utf-8") as file:
                self.windows_data = json.load(file)
            self.populate_bundle_list()
            self.log("成功加载 windows.json。")
        except Exception as e:
            self.log(f"加载 windows.json 失败：{e}")

    def populate_bundle_list(self):
        self.bundle_listbox.delete(0, tk.END)
        for bundle in self.windows_data.keys():
            self.bundle_listbox.insert(tk.END, bundle)

    def filter_bundles(self, event=None):
        search_term = self.search_entry.get().lower()
        self.bundle_listbox.delete(0, tk.END)
        for bundle in self.windows_data.keys():
            if search_term in bundle.lower():
                self.bundle_listbox.insert(tk.END, bundle)

    def on_bundle_select(self, event=None):
        if self.bundle_listbox.curselection():
            self.copy_button.configure(state="normal")
        else:
            self.copy_button.configure(state="disabled")

    # ---------- 原有：从列表框选中导出 ----------
    def copy_selected_bundle(self):
        selected_indices = self.bundle_listbox.curselection()
        if not selected_indices:
            self.log("没有选中任何 Bundle。")
            return

        export_folder = self.export_folder_entry.get()
        eft_folder = self.eft_folder_entry.get()
        if not export_folder or not eft_folder:
            self.log("错误：请先选择 EFT 文件夹和导出文件夹。")
            return

        selected_bundles = [self.bundle_listbox.get(idx) for idx in selected_indices]
        self._export_bundles(selected_bundles)

    # ---------- 新增：从文本输入框导出 ----------
    def export_from_input(self):
        raw_text = self.input_textbox.get("0.0", "end").strip()
        if not raw_text:
            self.log("请输入至少一个 Bundle 名称。")
            return

        # 按换行、逗号、空格分割
        # 先按换行分割，再按逗号/空格分割，并过滤空字符串
        lines = raw_text.splitlines()
        names = []
        for line in lines:
            # 按逗号分割
            parts = line.split(',')
            for part in parts:
                # 按空格分割（处理多个空格）
                for name in part.split():
                    clean = name.strip()
                    if clean:
                        names.append(clean)

        if not names:
            self.log("未解析出有效的 Bundle 名称。")
            return

        # 去重
        names = list(dict.fromkeys(names))  # 保持顺序去重
        self.log(f"解析到 {len(names)} 个 Bundle：{', '.join(names)}")
        self._export_bundles(names)

    # ---------- 核心导出逻辑（共用） ----------
    def _export_bundles(self, bundle_names):
        """传入一个 bundle 名称列表，导出所有依赖"""
        export_folder = self.export_folder_entry.get()
        eft_folder = self.eft_folder_entry.get()
        if not export_folder or not eft_folder:
            self.log("错误：请先选择 EFT 文件夹和导出文件夹。")
            return

        if self.windows_data is None:
            self.log("错误：尚未加载 windows.json，请检查 EFT 文件夹。")
            return

        # 收集依赖
        all_deps = set()
        invalid = []
        for name in bundle_names:
            if name not in self.windows_data:
                invalid.append(name)
                continue
            deps = self.windows_data[name]["Dependencies"]
            filtered = [dep for dep in deps if dep not in BLACKLIST]
            all_deps.update(filtered)
            all_deps.add(name)

        if invalid:
            self.log(f"警告：以下名称不在 windows.json 中，已跳过：{', '.join(invalid)}")

        if not all_deps:
            self.log("没有需要导出的文件（所有依赖均在黑名单中或无有效 Bundle）。")
            return

        total = len(all_deps)
        self.log(f"开始导出，共需复制 {total} 个文件。")
        copied = 0
        for dep in all_deps:
            source_path = os.path.join(eft_folder, "EscapeFromTarkov_Data", "StreamingAssets", "Windows", dep)
            dest_path = os.path.join(export_folder, dep)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            try:
                shutil.copy2(source_path, dest_path)
                copied += 1
                self.log(f"已复制 [{copied}/{total}]：{dep}")
            except Exception as e:
                self.log(f"复制 {dep} 失败：{e}")

        self.log(f"导出完成！共成功复制 {copied} 个文件。")

if __name__ == "__main__":
    app = TarkovFileCopyTool()
    app.mainloop()
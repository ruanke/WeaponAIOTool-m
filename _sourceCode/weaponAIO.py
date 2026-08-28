# -*- coding: utf-8 -*-
import os
import sys
import threading
import subprocess
import tkinter
from tkinter import messagebox
import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("武器 AIO 工具（WeaponAIOTool）")
        self.geometry("1350x750")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=75)
        self.grid_rowconfigure(0, weight=1)

        # ---------- 侧边栏 ----------
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(0, weight=1)
        self.step_buttons = []

        # ---------- 步骤说明（全中文） ----------
        self.steps = {
            "主菜单": """
欢迎使用塔科夫武器一体化工具！

WTT 团队自豪地为您呈现这款《逃离塔科夫》高级武器模组制作的一体化工具/教程。
请按照我们的分步说明，轻松简化您的武器制作流程。本指南几乎涵盖了从 Asset Ripper、AssetStudioGUI、Unity 到最终导入塔科夫的全部过程 —— 从武器提取到最终测试，我们为您考虑周全。

要跟随本指南，您需要准备以下工具：
    - Unity 2019.4.39f1
    - 《逃离塔科夫》SDK 项目
    - Asset Ripper
    - Blender
    - Asset Studio GUI
    - 支持 .json 格式化的文本编辑器（如 VSCode、VSCodium 等）
    - 运行 LActionReplacer.exe 所需的 .NET Framework

本工具深深感谢 SamSwat、SSH 和 Choccy 等杰出人士，他们提供的工具、信息和知识帮助我们走过了这段旅程。特别感谢 WTT 的 Tron，在探索过程中帮我抓住了最后一丝理智。

祝您好运！这个过程就像指挥一群喝了咖啡的猫一样直接，但别怕！本指南会尽量让您的模组制作混乱变得可控一些。

            —— 由 GrooveypenguinX 在可疑的理智状态下打造
""",
            "步骤 1：复制依赖文件": """
                                                            **说明：**
在此步骤中，您将从《逃离塔科夫》游戏文件中复制您自定义武器所基于的原版武器及其所有依赖项，到您指定的目录。
                                                            **操作：**
1. 运行附带的 'filegrabber' 脚本（点击下方按钮）。
2. 选择您的 EFT/SPT 主安装文件夹（应包含 EscapeFromTarkov.exe）。
3. 选择导出文件夹，用于存放导出的资源包。
4. 程序会自动加载 windows.json，右侧会显示游戏的所有资源包列表。
5. 搜索您需要的武器容器，在列表中选中它（支持多选）。
6. 点击“复制选中的 Bundle”按钮开始复制。
""",
            "步骤 2：转换资源包（Asset Ripper）": """
                                                            **说明：**
此步骤使用 Asset Ripper 将资源包转换为 Unity 格式。
                                                            **操作：**
1. 将步骤 1 导出的整个文件夹拖入 Asset Ripper。
2. 将所有资源导出到您指定的目录。
""",
            "步骤 3：修复 GUID 引用": """
                                                            **说明：**
此步骤修复所有脚本的 GUID 引用，确保您的 Unity 项目使用正确的 SDK 脚本。
                                                            **操作：**
1. 运行提供的 'scriptfix' 脚本。
2. 在脚本 GUI 中填写所需输入：
   - 导出项目的“Assets”文件夹：即步骤 2 中 Asset Ripper 导出的武器“assets”目录。
   - 《逃离塔科夫》SDK 路径：您的 EFT SDK Unity 项目所在目录（应包含 Assets、Library、Packages 等）。
3. 点击“修复脚本 GUID”按钮处理文件。
4. GUID 修补成功后，请删除导出武器项目中的“Scripts”文件夹，因为它已不再需要，且导入 Unity 时会引发错误。
""",
            "步骤 4：导入 Unity": """
                                                            **说明：**
此步骤将导出的武器导入 Unity。
                                                            **操作：**
1. 将步骤 2 中 AssetRipper 导出的主“Assets”文件夹重命名为您正在制作的物品名称。
2. 将文件夹导入 Unity，并保持目录结构不变。
""",
            "步骤 5：处理音频": """
                                                            **说明：**
此步骤处理所有音频资源，修复 Asset Ripper 造成的损坏音频文件。
                                                            **操作：**
1. 打开步骤 1 中存放武器容器 .bundle 及其依赖的导出文件夹。
2. 使用 Asset Studio GUI 从每个文件中导出所有 AudioClip。注意：并非所有文件都是 .bundle，有一个无扩展名的“generic”文件包含许多共享音频。
3. 新建一个文件夹，将所有“工作正常”的音频文件放入其中。
4. 运行提供的 'audiofix' 脚本，它会自动识别正常和损坏的音频文件，并替换损坏的文件，同时更新 .meta 文件（如有必要）。
5. 检查所有音频库文件（通常位于 Assets/Content/Weapons/Audio/）。在 Blend Options 下，将缺失的字段替换为 SDK 中的 'Standart' DistanceBlendOption（是的，是 'Standart'，不是拼写错误）。
""",
            "步骤 6：修复动画（第 1 部分 – AssetStudioGUI）": """
                                                            **说明：**
此步骤使用 AssetStudioGUI 导出工作正常的动画，供下一步使用。
                                                            **操作：**
1. 打开步骤 1 中存放武器容器 .bundle 及其依赖的导出文件夹。
2. 将您正在处理的武器容器的 'client_assets.bundle' 导入 AssetStudioGUI。
3. 在 'Options' 菜单中，确保勾选 'Display all assets'。
4. 在 'Filter Type' 菜单中，选择 'Animator'、'AnimationClip' 和 'Avatar'。
5. 在列表中找到 'int size' 最大的 Avatar，这通常就是用于导出正确动画的 Avatar。
6. 选中所有 AnimationClips、该 Avatar 以及对应的 Animator，右键选择 'Export Animator + selected Animations'。
""",
            "步骤 7：修复动画（第 2 部分 – Blender）": """
                                                            **说明：**
此步骤在 Blender 中修复动画，重置缩放、原点，并清理 AssetStudioGUI 带来的多余骨骼。
                                                            **操作：**
1. 将步骤 6 中生成的 FBX 文件导入 Blender。
2. 按 Alt+S 重置缩放（设为 1）。
3. 进入姿态模式（Pose Mode），选择骨架中主要的骨骼（通常是垂直站立且与武器同名的那个）。
4. 使用 Shift+S > 'Cursor to Selected' 将 3D 光标定位到该骨骼。
5. 回到物体模式（Object Mode），选择骨架，通过 'Object' > 'Origin' > 'Set Origin to 3D Cursor' 将原点设置到 3D 光标。
6. 进入编辑模式（Edit Mode），删除那根主要骨骼（不需要它，以免引起问题）。
7. 在物体模式下，仅选择骨架，按 Alt+G 重置所有变换，将骨架移回原点附近。
8. 建议将此文件备份为 WORKINGANIMATIONS_（您的武器名）.blend，以便需要重做动画或网格编辑时使用。
9. 在 Blender 中自定义此网格以创建您的新自定义枪械。确保将网格正确绑定到骨架的对应骨骼。
10. 保存并导出新 FBX 到 Unity，使用正确的导出设置。确保 'Transform' > 'Apply Scaling' 设为 'FBX All'，并取消勾选 'Armature' > 'Add Leaf Bones'。
""",
            "步骤 8：修复动画（第 3 部分 – Unity）": """
                                                            **说明：**
此步骤在 Unity 中修复武器的动画，用步骤 7 中工作正常的动画替换 Asset Ripper 导出的损坏动画。
                                                            **操作：**
1. 在 Unity 中，找到您步骤 4 导入的塔科夫武器。
2. 找到包含武器容器、控制器和 .anim 文件的文件夹。目前所有 .anim 文件都是从 Asset Ripper 带来的损坏版本。
3. 在 Unity 中新建一个文件夹，将所有损坏的 .anim 文件移至该文件夹，并适当命名。
4. 注意：如果在 Windows 资源管理器中移动这些动画，请同时移动它们的 .meta 文件。
5. 如果尚未导入，请将步骤 7 中的工作动画 FBX 文件导入 Unity。
6. 在 Unity 中选择该 FBX，在 Inspector > Rig > Avatar Definition 中，将其切换为 'Create from this model'，然后点击 Apply。
7. 在 Unity 中复制所有工作动画（展开 .fbx 选择所有动画，按 Ctrl+D 复制成 .anim 文件）。
8. 新建一个文件夹，将所有新生成的 'working' .anim 文件放入其中，并适当命名。
9. 注意：如果在 Windows 资源管理器中移动这些动画，请同时移动它们的 .meta 文件。
10. 运行提供的 'animrenamereplace' 脚本，它能自动重命名工作 .anim 文件，比较两个目录的差异并替换动画。
11. 'animrenamereplace' 脚本会将 Blender 导出的动画名称重命名为匹配的格式，并用工作动画替换损坏动画，同时保留原始 .meta 文件，从而保持动画控制器中的所有动画完整。
""",
            "步骤 9：左手动画": """
                                                            **说明：**
此步骤使用 SamSWAT 的 LActionReplacer 用 SDK 的动画更新动画控制器中的左手动画。
                                                            **操作：**
1. 使用附带的 'lactionsfix' 脚本替换动画控制器中的左手动画。
2. 点击“浏览目录”按钮，选择您的动画控制器所在目录。
3. 选择目录后，点击“运行脚本”执行替换。
4. 'lactionsfix' 脚本会自动完成左手动画的替换，确保应用正确的动画。

特别感谢 SamSwat 提供的 LActionReplacer.exe。
""",
            "步骤 10：头像遮罩（第 1 部分 – 遮罩）": """
                                                            **说明：**
此步骤使用 AssetStudioGUI 转储 Avatar 和 Animator Controller，并生成包含所有骨骼启用/禁用状态的头像遮罩列表。
                                                            **操作：**
1. 在 AssetStudioGUI 中打开您正在处理的武器的 client_assets.bundle 和 container.bundle。
2. 在工具栏中，通过 Filter Type > Avatar 和 Animator Controller 过滤资源。
3. 选择正确的 Animator Controller 和 Avatar，然后 Export > Dump > Selected Assets，选择导出目录。
4. 运行附带的 'avatarmaskparser' 脚本。
5. 在脚本 GUI 中，选择您的 Avatar 转储和 Animator Controller 转储，点击“处理转储并生成头像遮罩列表”，选择列表导出位置。
""",
            "步骤 11：头像遮罩（第 2 部分 – Avatar）": """
                                                            **说明：**
此步骤为每个动画层创建对应的头像遮罩。
                                                            **操作：**
1. 在 Unity 中，找到您带动画的模型 .fbx 文件并选中。
2. 在 Inspector 窗口中，切换到 'Rig' 选项卡。
3. 在 'Avatar Definition' 部分，选择 'Create From This Model'，点击 Apply。
4. 生成 Avatar 后，在 Project 窗口中右键 > Create > Avatar Mask，创建新的头像遮罩。
5. 在 Project 窗口中选择新创建的遮罩。
6. 在 Inspector 中，在 'Transform' > 'Use Skeleton From' 处，将您生成的 Avatar 拖入，并点击 'Import Skeleton'。
7. 为动画控制器中的每个层复制一份此遮罩。请确保在 'Hands' 层中启用 'IK Pass'。
8. 打开步骤 10 中生成的遮罩列表，将动画控制器中每个层的遮罩与列表逐一对比，启用/禁用对应的骨骼。这个过程很繁琐，但能保证每个层的遮罩骨骼正确。
""",
            "步骤 12：创建自定义武器预制体": """
                                                            **说明：**
此步骤在 Unity 中创建自定义武器预制体，这是实际在游戏中使用的自定义模型。
                                                            **操作：**
1. 选择您在步骤 7 中创建的自定义武器 'working animations' .fbx 文件，拖入场景，右键选择 Unpack Prefab Completely。
2. 将塔科夫武器模型（.generated）拖入场景。
3. 比较两个模型，注意塔科夫游戏对象上附加的脚本。
4. 主游戏对象应有 Transform Links、LOD Groups 和 Animator。weapon_root 的子对象会有不同类型的脚本，需要逐个对比并添加到自定义预制体的对应对象上。
   - 注意：Muzzle Fume（枪口烟雾）从 Asset Ripper 导出后是损坏的。幸运的是，SDK 中有示例，您可以参考并复制其值（感谢 SamSWAT！）。
5. 本程序 Tools 文件夹中提供了 'AutoTransformLinks.cs' Unity 编辑器脚本，可自动将 Transform Links 应用到您的自定义预制体。
6. 使用时，将 AutoTransformLinks.cs 放入您的 SDK Assets/Editor 文件夹。
7. 在 Unity 工具栏中选择 'Tarkov Weapon Tools'，然后选择 'Transform Links Automation' 打开其 GUI。
8. 在 GUI 中，将您的自定义预制体拖入 Main Gameobject 条目，点击 'Apply Transform Links'。
9. 所有游戏对象挂载正确的脚本后，将您的自定义武器预制体拖入 Project 窗口，重命名 .prefab 为您自定义的武器名称。
10. 选择您在步骤 4 中导入的主武器容器，清除 'Weapon Prefab' 中除 Weapon Object 和 Original Animator Controller 外的所有条目。
11. 选择您刚制作的自定义武器预制体，将其应用到主武器容器的 Weapon Prefab > Weapon Object 条目上。
""",
            "步骤 13：构建自定义武器资源包": """
                                                            **说明：**
此步骤清除资源标签并构建您的自定义武器资源包。
                                                            **操作：**
1. 所有导入的塔科夫游戏对象都保留了原始塔科夫资源标签（如 Assets/Content/Weapons/rhino/client_assets.bundle）。
2. 清除资源标签有两种方法：您可以逐个选中每个导入的游戏对象，将 Asset Label 设为 'None'；或者，在 AssetBundleBrowser 的配置窗口中清除所有标签，但务必小心，不要删除 SDK 中的任何 bundle 标签（如 Shaders 或 Additional Hands），因为这些必须构建，PathID 替换器才能正常工作。
3. 为主武器容器应用一个新标签，这将是您为游戏构建的自定义武器包名称。
4. 在 AssetBundleBrowser 的 'Build' 选项卡中构建新武器，然后通过自定义代码将其添加到游戏中，进行测试。

恭喜！您已成功构建了自定义枪械！如果一切顺利，您可以使用服务器模组将其添加到游戏中并测试！
""",
            "步骤 13：最后说明 – 错误与编辑": """
如果您的枪械动画不正常，很可能是某个或多个头像遮罩的问题。您可以编辑这些遮罩，重新构建武器进行进一步测试。

如果您需要进一步调整网格，请按以下步骤操作：
    1. 回到步骤 11 中用于制作武器预制体的工作动画 .fbx 文件。
    2. 在 Blender 中打开该 .fbx，编辑网格。
    3. 编辑完成后，将 FBX 导出回 Unity。确保 'Transform' > 'Apply Scaling' 设为 'FBX All'，并取消勾选 'Armature' > 'Add Leaf Bones'。
        - 如果您修改了骨骼位置，则需要重复步骤 8 中的 .anim 替换。
        - 如果您为骨骼添加了网格，则需要重新制作头像遮罩。
        - 您必须重新制作步骤 11 中详细说明的自定义武器包。
"""
        }

        # ---------- 创建侧边栏 ----------
        self.create_sidebar()

        # ---------- 主文本显示区 ----------
        self.textbox = ctk.CTkTextbox(self, width=250, state="disabled", wrap="word")
        self.textbox.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.textbox.grid_rowconfigure(0, weight=1)

        # ---------- 底部工具栏 ----------
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=1, column=0, columnspan=2, padx=(20, 20), pady=(0, 20), sticky="nsew")

        self.appearance_mode_label = ctk.CTkLabel(self.bottom_frame, text="外观模式：", anchor="e")
        self.appearance_mode_label.grid(row=0, column=0, padx=(10, 20), pady=(10, 10), sticky="e")
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(self.bottom_frame, values=["亮色", "暗色", "系统"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=0, column=1, padx=(0, 20), pady=(10, 10), sticky="w")
        self.appearance_mode_optionmenu.set("系统")

        self.scaling_label = ctk.CTkLabel(self.bottom_frame, text="界面缩放：", anchor="w")
        self.scaling_label.grid(row=0, column=2, padx=(0, 20), pady=(10, 10), sticky="w")
        self.scaling_optionmenu = ctk.CTkOptionMenu(self.bottom_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=0, column=3, padx=(0, 20), pady=(10, 10), sticky="w")
        self.scaling_optionmenu.set("100%")

        self.run_script_button = ctk.CTkButton(
            self.bottom_frame,
            text="运行关联脚本",
            fg_color="transparent",
            state="disabled",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            command=self.run_script
        )
        self.run_script_button.grid(row=0, column=4, padx=(20, 10), pady=(10, 10), sticky="e")

        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        self.set_step_text("主菜单")

    # ---------- 事件处理 ----------
    def change_appearance_mode_event(self, new_appearance_mode: str):
        mode_map = {"亮色": "Light", "暗色": "Dark", "系统": "System"}
        ctk.set_appearance_mode(mode_map.get(new_appearance_mode, "System"))

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    # ---------- 创建侧边栏 ----------
    def create_sidebar(self):
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="武器 AIO 工具", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        for i, step_name in enumerate(self.steps.keys(), start=1):
            button = ctk.CTkButton(
                self.sidebar_frame,
                text=step_name,
                command=lambda s=step_name: self.set_step_text(s)
            )
            button.grid(row=i, column=0, padx=20, pady=(10, 0), sticky="nsew")
            self.step_buttons.append(button)
            self.sidebar_frame.grid_rowconfigure(i, weight=1)

        self.sidebar_frame.grid_rowconfigure(len(self.steps) + 1, minsize=20)

    # ---------- 设置步骤文本 ----------
    def set_step_text(self, step_name):
        step_text = self.steps.get(step_name, "未找到该步骤")
        script_path = self.get_script_path(step_name)
        self.current_step = step_name

        if script_path and os.path.exists(script_path):
            self.run_script_button.configure(state="normal")
        else:
            self.run_script_button.configure(state="disabled")

        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        font = ctk.CTkFont(size=16)
        self.textbox.configure("custom", font=font, spacing1=10)
        self.textbox.insert("0.0", step_text, "custom")
        self.textbox.configure(state="disabled")

    # ---------- 获取脚本路径 ----------
    def get_script_path(self, step):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            ext = ".exe"
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            ext = ".py"

        script_map = {
            "步骤 1：复制依赖文件": "filegrabber",
            "步骤 3：修复 GUID 引用": "scriptfix",
            "步骤 5：处理音频": "audiofix",
            "步骤 8：修复动画（第 3 部分 – Unity）": "animrenamereplace",
            "步骤 9：左手动画": "lactionsfix",
            "步骤 10：头像遮罩（第 1 部分 – 遮罩）": "avatarmaskparser"
        }
        script_name = script_map.get(step)
        if not script_name:
            return None
        return os.path.join(base_path, "resources", script_name + ext)

    # ---------- 运行关联脚本 ----------
    def run_script(self):
        def run_in_thread():
            try:
                self.after(0, lambda: self.run_script_button.configure(state="disabled", text="启动中..."))
                if getattr(sys, 'frozen', False):
                    process = subprocess.Popen([script_path], shell=True)
                else:
                    process = subprocess.Popen([sys.executable, script_path])
                process.wait()
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda err=error_msg: messagebox.showerror(
                    "脚本执行错误",
                    f"执行 {self.current_step} 时出错：\n{err}")
                )
            finally:
                self.after(0, lambda: self.run_script_button.configure(
                    state="normal", text="运行关联脚本")
                )

        if self.current_step:
            script_path = self.get_script_path(self.current_step)
            if script_path and os.path.exists(script_path):
                threading.Thread(target=run_in_thread, daemon=True).start()
            else:
                messagebox.showinfo(
                    "脚本未找到",
                    f"当前步骤 {self.current_step} 没有关联的脚本。\n\n搜索路径：\n{script_path if script_path else '未定义'}"
                )

if __name__ == "__main__":
    app = App()
    app.mainloop()
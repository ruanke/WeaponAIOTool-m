import os
import shutil
import subprocess
import sys
from pathlib import Path
import site

# ---------- 动态获取 customtkinter 路径 ----------
def get_customtkinter_path():
    try:
        import customtkinter
        return customtkinter.__path__[0]
    except ImportError:
        for sp in site.getsitepackages():
            candidate = Path(sp) / "customtkinter"
            if candidate.exists():
                return str(candidate)
        raise RuntimeError("未找到 customtkinter，请先安装：pip install customtkinter")

CUSTOMTKINTER_PATH = get_customtkinter_path()

# ---------- 路径配置 ----------
SOURCE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = SOURCE_DIR / "resources"
TEMP_DIR = Path.cwd() / "temp"
FINAL_DIR = Path.cwd() / "Final Build"

def should_build(py_file, exe_file):
    if not exe_file.exists():
        return True
    return py_file.stat().st_mtime > exe_file.stat().st_mtime

def build_resources():
    print("正在检查资源脚本...")
    resource_files = list(RESOURCES_DIR.glob("*.py"))
    temp_resources_dir = TEMP_DIR / "resources"
    temp_resources_dir.mkdir(parents=True, exist_ok=True)

    # 复制预编译的二进制文件（如 LActionReplacer.exe）
    binary_files = [RESOURCES_DIR / "LActionReplacer.exe"]
    for binary in binary_files:
        if binary.exists():
            shutil.copy2(binary, temp_resources_dir / binary.name)
            print(f"已复制二进制文件: {binary.name}")
        else:
            print(f"警告: 缺少 {binary}")

    # 构建每个 .py 脚本为 .exe
    for script in resource_files:
        exe_file = temp_resources_dir / (script.stem + ".exe")
        if should_build(script, exe_file):
            print(f"正在构建 {script.name}...")
            cmd = [
                "pyinstaller",
                "--noconfirm",
                "--onefile",
                "--windowed",
                "--clean",
                "--add-data", f"{CUSTOMTKINTER_PATH}{os.pathsep}customtkinter",
                "--distpath", str(temp_resources_dir),
                "--workpath", str(TEMP_DIR / "build"),
                str(script)
            ]
            icon_path = SOURCE_DIR / "icon.ico"
            if icon_path.exists():
                cmd.insert(cmd.index("--clean") + 1, "--icon")
                cmd.insert(cmd.index("--clean") + 2, str(icon_path))
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"构建 {script.name} 失败: {e}")
                raise
        else:
            print(f"跳过 {script.name}，已是最新。")

def build_main_app():
    print("正在构建主应用程序...")
    temp_resources_dir = TEMP_DIR / "resources"
    if not temp_resources_dir.exists() or not any(temp_resources_dir.glob("*.exe")):
        print("错误: 未找到辅助 EXE，请先运行 build_resources()。")
        sys.exit(1)

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--hidden-import", "customtkinter",
        "--add-data", f"{str(temp_resources_dir)}{os.pathsep}resources",
        "--add-data", f"{CUSTOMTKINTER_PATH}{os.pathsep}customtkinter",
        "--distpath", str(FINAL_DIR),
        "--workpath", str(TEMP_DIR / "build"),
        str(TEMP_DIR / "weaponAIO.py")
    ]
    icon_path = SOURCE_DIR / "icon.ico"
    if icon_path.exists():
        cmd.insert(cmd.index("--windowed") + 1, "--icon")
        cmd.insert(cmd.index("--windowed") + 2, str(icon_path))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"构建主程序失败: {e}")
        raise

def main():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    build_resources()
    shutil.copy(SOURCE_DIR / "weaponAIO.py", TEMP_DIR)
    build_main_app()
    print(f"构建完成！最终 EXE 在: {FINAL_DIR}")

if __name__ == "__main__":
    main()
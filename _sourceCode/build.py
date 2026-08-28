import os
import shutil
import subprocess
import sys
from pathlib import Path
import site

# ---------- dynamically get customtkinter path ----------
def get_customtkinter_path():
    try:
        import customtkinter
        return customtkinter.__path__[0]
    except ImportError:
        for sp in site.getsitepackages():
            candidate = Path(sp) / "customtkinter"
            if candidate.exists():
                return str(candidate)
        raise RuntimeError("customtkinter not found, please install: pip install customtkinter")

CUSTOMTKINTER_PATH = get_customtkinter_path()

# ---------- path config ----------
SOURCE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = SOURCE_DIR / "resources"
TEMP_DIR = Path.cwd() / "temp"
FINAL_DIR = Path.cwd() / "FinalBuild"   # 使用无空格目录名，避免路径问题

def should_build(py_file, exe_file):
    if not exe_file.exists():
        return True
    return py_file.stat().st_mtime > exe_file.stat().st_mtime

def build_resources():
    print("Checking resource scripts...")
    resource_files = list(RESOURCES_DIR.glob("*.py"))
    temp_resources_dir = TEMP_DIR / "resources"
    temp_resources_dir.mkdir(parents=True, exist_ok=True)

    # copy pre-built binaries (like LActionReplacer.exe)
    binary_files = [RESOURCES_DIR / "LActionReplacer.exe"]
    for binary in binary_files:
        if binary.exists():
            shutil.copy2(binary, temp_resources_dir / binary.name)
            print(f"Copied binary: {binary.name}")
        else:
            print(f"Warning: missing {binary}")

    # build each .py script to .exe
    for script in resource_files:
        exe_file = temp_resources_dir / (script.stem + ".exe")
        if should_build(script, exe_file):
            print(f"Building {script.name}...")
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
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to build {script.name}: {e}")
                print("STDOUT:", e.stdout)
                print("STDERR:", e.stderr)
                raise
        else:
            print(f"Skipping {script.name}, already up to date.")

def build_main_app():
    print("Building main application...")
    temp_resources_dir = TEMP_DIR / "resources"
    if not temp_resources_dir.exists() or not any(temp_resources_dir.glob("*.exe")):
        print("Error: auxiliary EXEs not found, run build_resources() first.")
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
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to build main app: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise

def main():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    build_resources()
    shutil.copy(SOURCE_DIR / "weaponAIO.py", TEMP_DIR)
    build_main_app()
    print(f"Build complete! Final EXE in: {FINAL_DIR}")

if __name__ == "__main__":
    main()
import os
import subprocess
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
LOCAL_MODS_DIR = REPO_ROOT / "mods"

LOAD_SCRIPT = TOOLS_DIR / "load_mod.sh"
UNLOAD_SCRIPT = TOOLS_DIR / "unload_mod.sh"


def write_mod(mod_name: str, files: dict[str, str]) -> Path:
    mod_dir = LOCAL_MODS_DIR / mod_name
    mod_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, content in files.items():
        target_path = mod_dir / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
    return mod_dir


def load_mod(mod_path_or_name: str, non_interactive: bool = True) -> str:
    cmd = ["sudo", str(LOAD_SCRIPT), mod_path_or_name]
    if non_interactive:
        # Expect script to ask about replacing and restart; we answer 'y' to both safely
        # Use yes with limited count
        proc = subprocess.run(["bash", "-lc", f"yes | {' '.join(cmd)}"], capture_output=True, text=True)
    else:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"load_mod failed: {proc.stderr}\n{proc.stdout}")
    return proc.stdout


def unload_mod(mod_name: str, non_interactive: bool = True) -> str:
    cmd = ["sudo", str(UNLOAD_SCRIPT), mod_name]
    if non_interactive:
        proc = subprocess.run(["bash", "-lc", f"yes | {' '.join(cmd)}"], capture_output=True, text=True)
    else:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"unload_mod failed: {proc.stderr}\n{proc.stdout}")
    return proc.stdout

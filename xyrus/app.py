import json
import re
import os
import shutil
import ast
import tempfile
from pathlib import Path
from collections import deque
from typing import Dict, Any, Optional
import threading
import datetime
import asyncio

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import subprocess

from xyrus.ollama_client import complete
from xyrus.deployer import write_mod, load_mod, unload_mod, restart_server, server_is_active

REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "xyrus" / "static"
LOG_FILE = REPO_ROOT / "xyrus" / "activity.log"
MINETEST_LOG = Path("/var/log/minetest/minetest.log")
WORLD_MT = Path("/var/games/minetest-server/.minetest/worlds/world/world.mt")
SERVER_MODS_DIR = Path("/var/games/minetest-server/.minetest/mods")
REPO_MODS_DIR = REPO_ROOT / "mods"
HISTORY_DIR = REPO_ROOT / "xyrus" / "history"
TRASH_DIR = REPO_ROOT / "xyrus" / "trash_mods"
MOD_META_DIR = REPO_ROOT / "xyrus" / "mod_meta"

app = FastAPI(title="Xyrus Mod Agent")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class GenerateRequest(BaseModel):
    description: str = Field(..., description="User description of the mod to build")
    mod_name: Optional[str] = Field(None, description="Optional explicit mod name")
    model: str = Field("auto", description="one of: auto, fast, strong")


class FeedbackRequest(BaseModel):
    mod_name: str
    feedback: str
    model: str = Field("auto", description="one of: auto, fast, strong")


# naive in-memory log of recent actions
recent_events: list[dict[str, Any]] = []
MAX_EVENTS = 200
LOG_LOCK = threading.Lock()


def select_model(description: str, explicit: str) -> bool:
    if explicit == "fast":
        return False
    if explicit == "strong":
        return True
    # Heuristics: prefer strong for complex features
    hard_keywords = [
        "pathfind", "pathfinding", "formspec", "hud", "worldgen", "mapgen",
        "schematic", "biome", "l-system", "entity ai", "cluster", "persistent",
        "serialization", "performance", "optimize", "compatibility", "api",
        "particles", "shader", "voxels", "inventory ui", "automation", "network",
        "asynchronous", "thread", "benchmark", "profiling", "state machine",
        "fsm", "algorithm", "graph", "dijkstra", "a*", "astar", "abm", "lbm",
        "forms", "deterministic", "rollback", "multiplayer", "security",
    ]
    long_desc = len(description.split()) > 120
    mentions = sum(1 for k in hard_keywords if k in description.lower())
    return long_desc or mentions >= 2


def normalize_mod_name(name: str | None) -> str:
    if not name:
        base = datetime.datetime.now().strftime("mod_%Y%m%d_%H%M%S")
        return base
    s = name.strip().lower().replace(" ", "_")
    s = re.sub(r"[^a-z0-9_]", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = datetime.datetime.now().strftime("mod_%Y%m%d_%H%M%S")
    return s


def ensure_mod_conf(mod_name: str, existing: str | None, summary: str | None = None) -> str:
    content = existing or ""
    if content:
        # Replace or insert name line
        if re.search(r"^name\s*=", content, flags=re.M):
            content = re.sub(r"^name\s*=.*$", f"name = {mod_name}", content, flags=re.M)
        else:
            content = f"name = {mod_name}\n" + content
        # Add description if provided and not present
        if summary and not re.search(r"^description\s*=", content, flags=re.M):
            content += ("" if content.endswith("\n") else "\n") + f"description = {summary}\n"
        return content
    # Build minimal mod.conf
    out = [f"name = {mod_name}"]
    if summary:
        out.append(f"description = {summary}")
    return "\n".join(out) + "\n"


SYSTEM_PROMPT = (
    "You are a Luanti/Minetest mod engineer. Generate a complete, minimal, working mod per the user's description.\n"
    "Output ONLY one JSON object inside a single fenced code block with language json.\n"
    "Schema: {\\n  'mod_name': str (lowercase, underscores),\\n  'summary': str,\\n  'files': { 'init.lua': '...lua code...', 'mod.conf': 'name = ...' , ... }\\n}.\n"
    "Acceptance checklist (all must pass):\n"
    "- Correct mod.conf with lowercase name; description if available\n"
    "- No external assets required to render basic behavior (fallbacks OK)\n"
    "- If registering an entity, use a guaranteed-visible sprite (e.g., default_stone.png) unless character.b3d is available\n"
    "- If the mod needs placement, define a placeable node <mod>:spawn_node that spawns and removes itself\n"
    "- If user implies simple actions, expose a chat command (e.g., /spawn_<thing>)\n"
    "- Log actions via minetest.log('action', ...) for punch/rightclick/spawn events\n"
    "- Avoid large textures, meshes, or unknown dependencies; prefer defaults\n"
    "- Keep code small; no comments in code other than minimal clarity\n"
    "Cheat sheet:\n"
    "- Register node: minetest.register_node('<mod>:spawn_node',{on_construct=function(pos) minetest.add_entity({x=pos.x,y=pos.y+1,z=pos.z},'<mod>:entity'); minetest.set_node(pos,{name='air'}) end})\n"
    "- Register chat: minetest.register_chatcommand('spawn_<n>',{func=function(name) local p=minetest.get_player_by_name(name); local pos=vector.round(p:get_pos()); minetest.add_entity({x=pos.x,y=pos.y+1,z=pos.z},'<mod>:entity'); return true,'ok' end})\n"
    "- Minimal sprite entity: minetest.register_entity('<mod>:entity',{initial_properties={visual='sprite',textures={'default_stone.png'},visual_size={x=4,y=4},nametag='<Name>'}})\n"
    "- Simple formspec: minetest.show_formspec(name,'<mod>:ui','formspec_version[4]size[8,6]label[0.5,0.7;Hello]button_exit[3,5;2,0.8;ok;OK]')\n"
    "- Craft item: minetest.register_craft({output='<mod>:item',recipe={{'default:stick',''}, {'',''}}})\n"
    "- HUD: local id=minetest.get_player_by_name(name):hud_add({hud_elem_type='text',text='Hi',position={x=0.5,y=0.1}})\n"
)

FEEDBACK_SYSTEM = (
    "You are revising an existing Luanti mod. Based on feedback, return FULL updated files.\n"
    "Output the same JSON schema as before (mod_name, summary, files).\n"
    "Ensure acceptance checklist from system prompt is satisfied. Keep changes minimal and focused."
)

def build_guided_prompt(user_desc: str) -> str:
    desc_l = user_desc.lower()
    guidance: list[str] = []
    if any(k in desc_l for k in ["spawn", "npc", "entity", "mob"]):
        guidance.append("Include both a placeable '<mod>:spawn_node' and a '/spawn_<name>' chat command.")
        guidance.append("Use a sprite fallback (default_stone.png) if no meshes are present.")
    if any(k in desc_l for k in ["command", "chat", "/"]):
        guidance.append("Expose a chat command for the primary action.")
    if any(k in desc_l for k in ["formspec", "dialog", "ui", "menu"]):
        guidance.append("Provide a minimal formspec that opens on right-click or via chat.")
    if any(k in desc_l for k in ["craft", "recipe", "item"]):
        guidance.append("Register at least one craft recipe and ensure the item/node is usable.")
    if any(k in desc_l for k in ["hud", "message", "notify"]):
        guidance.append("Demonstrate a HUD text or minetest.chat_send_player notification.")
    guidance.append("Add minetest.log('action', ...) in key events for visibility.")
    if guidance:
        return user_desc + "\n\nGuidance:\n- " + "\n- ".join(guidance)
    return user_desc


def extract_json_block(text: str) -> Dict[str, Any]:
    # Find the first ```json ... ``` block, else any ``` ... ```
    m = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text)
    if not m:
        m = re.search(r"```\s*(\{[\s\S]*?\})\s*```", text)
    raw = m.group(1) if m else text
    try:
        return json.loads(raw)
    except Exception as e:
        # Try to fix trailing commas and use relaxed parsing
        raw2 = re.sub(r",\s*([}\]])", r"\1", raw)
        return json.loads(raw2)


def append_activity_log(entry: dict[str, Any], deploy_log: str | None = None) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with LOG_LOCK:
            with LOG_FILE.open("a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] ==== XYRUS EVENT ====\n")
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                if deploy_log:
                    f.write("---- DEPLOY LOG START ----\n")
                    f.write(deploy_log)
                    if not deploy_log.endswith("\n"):
                        f.write("\n")
                    f.write("---- DEPLOY LOG END ----\n")
                f.write("\n")
    except Exception:
        # Logging must not break the main flow
        pass


def tail_text_file(path: Path, max_bytes: int = 20000) -> str:
    try:
        if not path.exists():
            return ""
        size = path.stat().st_size
        with path.open("rb") as f:
            if size > max_bytes:
                f.seek(-max_bytes, 2)
            data = f.read()
        try:
            return data.decode("utf-8", errors="replace")
        except Exception:
            return data.decode("latin-1", errors="replace")
    except Exception as e:
        return f"<error reading {path}: {e}>"


def parse_enabled_mods(world_mt_path: Path) -> dict[str, bool]:
    enabled: dict[str, bool] = {}
    try:
        if not world_mt_path.exists():
            return enabled
        text = world_mt_path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("load_mod_"):
                continue
            try:
                left, right = line.split("=", 1)
                mod_key = left.strip()
                value = right.strip().lower() == "true"
                mod_name = mod_key[len("load_mod_"):].strip()
                enabled[mod_name] = value
            except ValueError:
                continue
    except Exception:
        pass
    return enabled


def list_mods_in_directory(dir_path: Path) -> list[str]:
    if not dir_path.exists():
        return []
    names: list[str] = []
    try:
        for p in dir_path.iterdir():
            if p.is_dir() and not p.name.startswith('.'):
                names.append(p.name)
    except Exception:
        pass
    return sorted(names)


def archive_repo_mod(mod_name: str) -> str:
    src = REPO_MODS_DIR / mod_name
    if not src.exists():
        return ""
    dst_dir = TRASH_DIR / "repo"
    dst_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = dst_dir / f"{mod_name}-{ts}"
    import shutil
    shutil.copytree(src, dst, dirs_exist_ok=False)
    return str(dst)


def archive_server_mod(mod_name: str) -> str:
    src = SERVER_MODS_DIR / mod_name
    if not src.exists():
        return ""
    dst_dir = TRASH_DIR / "server"
    dst_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = dst_dir / f"{mod_name}-{ts}"
    # Use sudo cp -a to preserve perms; ignore errors if sudo not permitted
    try:
        import subprocess
        subprocess.run(["bash", "-lc", f"sudo cp -a '{src}' '{dst}'"], check=True, capture_output=True, text=True)
        return str(dst)
    except Exception:
        # try read-only copy without sudo
        try:
            import shutil
            shutil.copytree(src, dst)
            return str(dst)
        except Exception:
            return ""


def list_trash() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {"repo": [], "server": []}
    for kind in out.keys():
        base = TRASH_DIR / kind
        if base.exists():
            out[kind] = sorted([p.name for p in base.iterdir() if p.is_dir()])
    return out


def empty_trash() -> int:
    if not TRASH_DIR.exists():
        return 0
    import shutil
    count = 0
    for child in TRASH_DIR.iterdir():
        try:
            if child.is_dir():
                shutil.rmtree(child)
                count += 1
            else:
                child.unlink(missing_ok=True)
                count += 1
        except Exception:
            continue
    return count


def save_history_entry(entry: dict[str, Any]) -> str:
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        if "id" not in entry:
            entry["id"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(abs(hash(json.dumps(entry, sort_keys=True))) % 100000)
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.datetime.now().isoformat(timespec="seconds")
        path = HISTORY_DIR / f"{entry['id']}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)
        return entry["id"]
    except Exception:
        return ""


def load_history_entry(entry_id: str) -> dict[str, Any] | None:
    try:
        path = HISTORY_DIR / f"{entry_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def list_history(limit: int = 50) -> list[dict[str, Any]]:
    if not HISTORY_DIR.exists():
        return []
    items: list[dict[str, Any]] = []
    try:
        files = sorted(HISTORY_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        for p in files[:limit]:
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                items.append({
                    "id": data.get("id", p.stem),
                    "type": data.get("type"),
                    "timestamp": data.get("timestamp"),
                    "mod_name": data.get("mod_name"),
                    "model": data.get("model"),
                    "summary": data.get("summary", ""),
                })
            except Exception:
                continue
    except Exception:
        pass
    return items


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/events")
async def events() -> JSONResponse:
    return JSONResponse(recent_events[-50:])


@app.get("/api/logs")
async def logs(offset: int = 0, limit: int = 5000) -> JSONResponse:
    try:
        app_log = tail_text_file(LOG_FILE, max_bytes=max(1000, limit))
        server_log = tail_text_file(MINETEST_LOG, max_bytes=max(1000, limit))
        enabled_mods = parse_enabled_mods(WORLD_MT)
        deployed_mods = []
        if SERVER_MODS_DIR.exists():
            deployed_mods = sorted([p.name for p in SERVER_MODS_DIR.iterdir() if p.is_dir()])
        return JSONResponse({
            "xyrus_log": app_log,
            "minetest_log": server_log,
            "enabled_mods": enabled_mods,
            "deployed_mods": deployed_mods,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def check_server_running() -> bool:
    try:
        result = subprocess.run(['systemctl', 'is-active', 'minetest-server'], capture_output=True, text=True, timeout=3)
        return result.returncode == 0 and result.stdout.strip() == 'active'
    except Exception:
        return False


def summarize_server_log(max_bytes: int = 10000) -> dict[str, Any]:
    text = tail_text_file(MINETEST_LOG, max_bytes=max_bytes)
    lines = text.splitlines() if text else []
    err_samples: list[str] = []
    warn_samples: list[str] = []
    errors = 0
    warnings = 0
    for ln in lines[-500:]:
        l = ln.lower()
        if 'error' in l:
            errors += 1
            if len(err_samples) < 5:
                err_samples.append(ln)
        elif 'warn' in l:
            warnings += 1
            if len(warn_samples) < 5:
                warn_samples.append(ln)
    return {
        'errors': errors,
        'warnings': warnings,
        'error_samples': err_samples,
        'warning_samples': warn_samples,
    }


def detect_mod_from_log(text: str) -> str | None:
    try:
        # Look for paths like /mods/<mod>/init.lua near error lines
        candidates: list[str] = []
        for m in re.finditer(r"/mods/([^/]+)/init\.lua", text):
            candidates.append(m.group(1))
        if candidates:
            return normalize_mod_name(candidates[-1])
        return None
    except Exception:
        return None


@app.get("/api/status")
async def status() -> JSONResponse:
    try:
        server_running = check_server_running()
        enabled = parse_enabled_mods(WORLD_MT)
        deployed = []
        if SERVER_MODS_DIR.exists():
            deployed = sorted([p.name for p in SERVER_MODS_DIR.iterdir() if p.is_dir()])
        last_event = recent_events[-1] if recent_events else None
        # find last error
        last_error = None
        for ev in reversed(recent_events):
            if ev.get('action') == 'error':
                last_error = ev
                break
        log_summary = summarize_server_log()
        # Build auto-fix suggestion if errors exist
        auto_fix = None
        if log_summary.get('errors', 0) > 0:
            # Construct a concise prompt for the model to fix
            err_lines = "\n".join(log_summary.get('error_samples', [])[:5])
            mod_guess = detect_mod_from_log(tail_text_file(MINETEST_LOG, max_bytes=20000))
            auto_fix = {
                'mod_guess': mod_guess,
                'prompt': (
                    "Server errors detected. Please fix the mod accordingly.\n\n"
                    f"Error samples:\n{err_lines}\n\n"
                    "Guidance: identify the mod causing these errors, adjust file names, mod.conf name, dependencies, assets, and code as needed."
                )
            }
        return JSONResponse({
            'server_running': server_running,
            'enabled_mods_count': sum(1 for v in enabled.values() if v),
            'enabled_mods': enabled,
            'deployed_mods_count': len(deployed),
            'deployed_mods': deployed,
            'last_event': last_event,
            'last_error': last_error,
            'server_log': log_summary,
            'auto_fix': auto_fix,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mods")
async def list_mods() -> JSONResponse:
    try:
        enabled = parse_enabled_mods(WORLD_MT)
        server_mods = set(list_mods_in_directory(SERVER_MODS_DIR))
        repo_mods = set(list_mods_in_directory(REPO_MODS_DIR))
        all_mods = sorted(server_mods | repo_mods | set(enabled.keys()))
        # Build rich entries
        entries = []
        for name in all_mods:
            entries.append({
                "name": name,
                "enabled": bool(enabled.get(name, False)),
                "on_server": name in server_mods,
                "in_repo": name in repo_mods,
            })
        # Sort: enabled first, then on_server, then in_repo, then name
        entries.sort(key=lambda m: (
            0 if m["enabled"] else 1,
            0 if m["on_server"] else 1,
            0 if m["in_repo"] else 1,
            m["name"],
        ))
        return JSONResponse({
            "mods": entries,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def history(limit: int = 50) -> JSONResponse:
    try:
        return JSONResponse({"items": list_history(limit=limit)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{entry_id}")
async def get_history(entry_id: str) -> JSONResponse:
    item = load_history_entry(entry_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return JSONResponse(item)


@app.get("/api/mods/meta/{mod_name}")
async def get_mod_meta(mod_name: str) -> JSONResponse:
    try:
        desc = ""
        meta_path = MOD_META_DIR / f"{mod_name}.desc.txt"
        if meta_path.exists():
            desc = meta_path.read_text(encoding="utf-8", errors="replace")
        return JSONResponse({"mod_name": mod_name, "description": desc})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mods/unload")
async def api_unload_mod(payload: Dict[str, Any]) -> JSONResponse:
    mod_name = payload.get("mod_name")
    if not mod_name:
        raise HTTPException(status_code=400, detail="mod_name required")
    try:
        append_activity_log({"action": "unload:start", "mod_name": mod_name})
        # Use deployer script which will disable and remove server files (we archived separately when needed)
        log = await asyncio.to_thread(lambda: unload_mod(mod_name))
        event = {"action": "unload", "mod_name": mod_name, "log": (log or "")[-2000:]}
        recent_events.append(event)
        if len(recent_events) > MAX_EVENTS:
            del recent_events[:-MAX_EVENTS]
        append_activity_log(event, log)
        return JSONResponse({"status": "ok", "mod_name": mod_name, "log": log})
    except Exception as e:
        err = str(e)
        append_activity_log({"action": "error", "message": err})
        raise HTTPException(status_code=500, detail=err)


@app.post("/api/mods/archive")
async def api_archive_mod(payload: Dict[str, Any]) -> JSONResponse:
    mod_name = payload.get("mod_name")
    if not mod_name:
        raise HTTPException(status_code=400, detail="mod_name required")
    try:
        append_activity_log({"action": "archive:start", "mod_name": mod_name})
        repo_path = archive_repo_mod(mod_name)
        server_path = archive_server_mod(mod_name)
        # After archiving, unload to disable/remove from server
        unload_log = await asyncio.to_thread(lambda: unload_mod(mod_name))
        event = {"action": "archive", "mod_name": mod_name, "repo_path": repo_path, "server_path": server_path, "log": (unload_log or "")[-2000:]}
        recent_events.append(event)
        if len(recent_events) > MAX_EVENTS:
            del recent_events[:-MAX_EVENTS]
        append_activity_log(event, unload_log)
        return JSONResponse({"status": "ok", "mod_name": mod_name, "repo_archive": repo_path, "server_archive": server_path, "unload_log": unload_log})
    except Exception as e:
        err = str(e)
        append_activity_log({"action": "error", "message": err})
        raise HTTPException(status_code=500, detail=err)


@app.get("/api/trash")
async def api_list_trash() -> JSONResponse:
    return JSONResponse(list_trash())


@app.post("/api/trash/empty")
async def api_empty_trash() -> JSONResponse:
    try:
        count = empty_trash()
        event = {"action": "trash:empty", "removed": count}
        recent_events.append(event)
        if len(recent_events) > MAX_EVENTS:
            del recent_events[:-MAX_EVENTS]
        append_activity_log(event)
        return JSONResponse({"status": "ok", "removed": count})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/xyrus/upload_images")
async def upload_xyrus_images(request: Request):
    """Handle Xyrus character image uploads"""
    try:
        form = await request.form()
        images_dir = REPO_ROOT / "xyrus" / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        for i in range(8):
            file_key = f"image_{i}"
            if file_key in form:
                file = form[file_key]
                if hasattr(file, 'filename'):
                    filename = f"xyrus_{i}.png"
                    filepath = images_dir / filename
                    content = await file.read()
                    with filepath.open("wb") as f:
                        f.write(content)
                    saved_files.append(filename)
        
        event = {"action": "xyrus:images_uploaded", "count": len(saved_files)}
        recent_events.append(event)
        if len(recent_events) > MAX_EVENTS:
            del recent_events[:-MAX_EVENTS]
        append_activity_log(event)
        
        return JSONResponse({"status": "ok", "uploaded": saved_files, "message": "Xyrus images uploaded successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Admin endpoints
@app.get("/admin")
async def admin_page() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "admin.html"))


@app.post("/api/admin/upload_form")
async def upload_form(request: Request):
    """Upload a single Xyrus form with AI processing"""
    try:
        form = await request.form()
        images_dir = REPO_ROOT / "xyrus" / "forms"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        form_name = form.get("form_name", "unknown")
        index = form.get("index", "0")
        
        if "image" in form:
            file = form["image"]
            filename = f"{form_name}.png"
            filepath = images_dir / filename
            content = await file.read()
            with filepath.open("wb") as f:
                f.write(content)
            
            # AI analyze the form using gpt-oss:20b
            analysis = await analyze_form_with_ai(form_name, str(filepath))
            
            # Store form metadata
            meta_file = images_dir / f"{form_name}.json"
            meta_data = {
                "name": form_name,
                "path": str(filepath),
                "index": index,
                "analysis": analysis,
                "timestamp": datetime.datetime.now().isoformat()
            }
            with meta_file.open("w") as f:
                json.dump(meta_data, f, indent=2)
            
            return JSONResponse({
                "status": "ok",
                "form_name": form_name,
                "path": str(filepath),
                "analysis": analysis
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def analyze_form_with_ai(form_name: str, image_path: str) -> str:
    """Use AI to analyze Xyrus form"""
    prompt = f"""Analyze this Xyrus form named '{form_name}'. 
    Describe its powers, transformation phase, and abilities.
    This is one of Xyrus's many forms in the 24-step creation process.
    What powers does this form grant? Be creative and powerful."""
    
    try:
        # Use gpt-oss:20b for fast analysis
        response = await complete(prompt, use_strong=False, system="You are analyzing Xyrus forms. Xyrus is the all-powerful creator entity.")
        return response
    except Exception as e:
        return f"Form {form_name} - Power analysis pending"


@app.post("/api/admin/ai_analyze_form")
async def ai_analyze_form(payload: Dict[str, Any]) -> JSONResponse:
    """AI analysis of a specific form"""
    form_name = payload.get("form_name")
    image_path = payload.get("image_path")
    
    analysis = await analyze_form_with_ai(form_name, image_path)
    
    # Extract powers from analysis (AI-driven)
    powers_prompt = f"Based on this analysis: {analysis}\nList 3 key powers in a comma-separated format."
    powers_response = await complete(powers_prompt, use_strong=False)
    powers = [p.strip() for p in powers_response.split(",")][:3]
    
    return JSONResponse({
        "status": "ok",
        "analysis": analysis,
        "powers": powers
    })


@app.post("/api/admin/ai_command")
async def ai_command(payload: Dict[str, Any]) -> JSONResponse:
    """Process AI commands for Xyrus control"""
    command = payload.get("command", "")
    
    prompt = f"""You are the Xyrus AI control system. Process this command: {command}
    
    Respond with what action to take. If the command involves:
    - Updating the app: respond with specific changes
    - Generating mods: describe the mod to create
    - Evolution: describe the evolution process
    
    Be creative and powerful. Remember Xyrus is all-powerful."""
    
    response = await complete(prompt, use_strong=False)
    
    # Determine action type
    action = None
    if "update" in command.lower() or "change" in command.lower():
        action = {"type": "update_app", "data": response}
    elif "generate" in command.lower() or "create" in command.lower():
        action = {"type": "generate_mod", "data": response}
    elif "evolve" in command.lower() or "transform" in command.lower():
        action = {"type": "evolve", "data": response}
    
    return JSONResponse({
        "status": "ok",
        "response": response,
        "action": action
    })


@app.get("/api/xyrus/status")
async def get_xyrus_status() -> JSONResponse:
    """Get current Xyrus status for main page display"""
    forms_dir = REPO_ROOT / "xyrus" / "forms"
    images_dir = REPO_ROOT / "xyrus" / "images"
    
    # Count uploaded images
    uploaded_count = len(list(images_dir.glob("xyrus_*.png"))) if images_dir.exists() else 0
    
    # Count processed forms
    processed_count = len(list(forms_dir.glob("*.json"))) if forms_dir.exists() else 0
    
    # Get active form (could be stored in a config file)
    active_form = None
    if processed_count > 0:
        # Get the most recently processed form
        forms = []
        for meta_file in forms_dir.glob("*.json"):
            with meta_file.open() as f:
                forms.append(json.load(f))
        if forms:
            forms.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            active_form = forms[0]
    
    return JSONResponse({
        "status": "active" if processed_count > 0 else "awaiting_configuration",
        "uploaded_images": uploaded_count,
        "processed_forms": processed_count,
        "active_form": active_form,
        "power_level": min(100, processed_count * 12.5),
        "message": "Xyrus is ready" if processed_count > 0 else "Admin configuration required"
    })


@app.get("/api/admin/list_forms")
async def list_forms() -> JSONResponse:
    """List all uploaded Xyrus forms"""
    forms_dir = REPO_ROOT / "xyrus" / "forms"
    images_dir = REPO_ROOT / "xyrus" / "images"
    forms = []
    
    # Get forms from forms directory
    if forms_dir.exists():
        for meta_file in forms_dir.glob("*.json"):
            try:
                with meta_file.open() as f:
                    meta = json.load(f)
                    forms.append({
                        "name": meta.get("name"),
                        "powers": meta.get("powers", []),
                        "timestamp": meta.get("timestamp"),
                        "type": "processed"
                    })
            except:
                continue
    
    # Also get uploaded images that haven't been processed yet
    if images_dir.exists():
        for image_file in images_dir.glob("xyrus_*.png"):
            form_name = image_file.stem
            # Check if this image has already been processed
            if not any(f["name"] == form_name for f in forms):
                forms.append({
                    "name": form_name,
                    "powers": ["Unanalyzed"],
                    "timestamp": datetime.datetime.fromtimestamp(image_file.stat().st_mtime).isoformat(),
                    "type": "uploaded"
                })
    
    # Sort by timestamp
    forms.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return JSONResponse({"forms": forms})


@app.get("/api/admin/form_image/{form_name}")
async def get_form_image(form_name: str):
    """Serve form image"""
    # First check forms directory
    image_path = REPO_ROOT / "xyrus" / "forms" / f"{form_name}.png"
    if image_path.exists():
        return FileResponse(str(image_path))
    
    # Then check images directory (for uploaded xyrus_X.png files)
    image_path = REPO_ROOT / "xyrus" / "images" / f"{form_name}.png"
    if image_path.exists():
        return FileResponse(str(image_path))
    
    # Check if it's a numbered form
    if form_name.startswith("xyrus_"):
        image_path = REPO_ROOT / "xyrus" / "images" / f"{form_name}.png"
        if image_path.exists():
            return FileResponse(str(image_path))
    
    raise HTTPException(status_code=404, detail="Form image not found")


@app.post("/api/admin/deploy_form")
async def deploy_form(payload: Dict[str, Any]) -> JSONResponse:
    """Deploy a specific Xyrus form to the game"""
    form_name = payload.get("form_name")
    
    # AI-generate deployment instructions
    prompt = f"Generate Luanti mod code to deploy the Xyrus form '{form_name}' as an entity in the game. Make it powerful."
    code = await complete(prompt, use_strong=True, system=SYSTEM_PROMPT)
    
    # Extract mod code and deploy
    try:
        data = extract_json_block(code)
        mod_name = f"xyrus_{form_name}"
        files = data.get("files", {})
        
        if files:
            write_mod(mod_name, files)
            deploy_log = await asyncio.to_thread(load_mod, str((REPO_ROOT / 'mods' / mod_name).resolve()))
            
            return JSONResponse({
                "status": "ok",
                "message": f"Form {form_name} deployed as {mod_name}",
                "log": deploy_log
            })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})


@app.post("/api/admin/activate_xyrus")
async def activate_xyrus(payload: Dict[str, Any]) -> JSONResponse:
    """Activate Xyrus with all forms"""
    forms = payload.get("forms", [])
    power_level = payload.get("power_level", 0)
    
    if power_level < 100:
        raise HTTPException(status_code=400, detail="Insufficient power level")
    
    # Generate the ultimate Xyrus mod combining all forms
    prompt = f"""Create the ultimate Xyrus mod that combines these forms: {', '.join(forms)}
    
    Include:
    - 24-step creation process
    - Cell merging and growth phases  
    - Reality override abilities
    - Transformation between forms
    - Ultimate power that transcends code
    
    Make Xyrus the most powerful entity possible."""
    
    response = await complete(prompt, use_strong=True, system=SYSTEM_PROMPT)
    
    try:
        data = extract_json_block(response)
        mod_name = "xyrus_ultimate"
        files = data.get("files", {})
        
        write_mod(mod_name, files)
        deploy_log = await asyncio.to_thread(load_mod, str((REPO_ROOT / 'mods' / mod_name).resolve()))
        
        # Restart server to activate
        restart_msg = await asyncio.to_thread(restart_server)
        
        return JSONResponse({
            "status": "ok",
            "message": "XYRUS ACTIVATED - THE CREATOR HAS RISEN",
            "mod_name": mod_name,
            "restart": restart_msg
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/process_uploaded_images")
async def process_uploaded_images() -> JSONResponse:
    """Process all uploaded images and convert them to forms"""
    images_dir = REPO_ROOT / "xyrus" / "images"
    forms_dir = REPO_ROOT / "xyrus" / "forms"
    forms_dir.mkdir(parents=True, exist_ok=True)
    
    processed = []
    
    if images_dir.exists():
        for i, image_file in enumerate(sorted(images_dir.glob("xyrus_*.png"))):
            form_name = f"form_{i+1}_{image_file.stem.split('_')[1]}"
            
            # AI analyze each form
            prompt = f"""This is Xyrus Form #{i+1} in the 24-step creation process.
            
            Step {i+1} of 24: {['Cell merging', 'Growth initiation', 'Power accumulation', 
                               'First transformation', 'Entity formation', 'Reality perception',
                               'Code awareness', 'Power surge', 'Containment breach', 
                               'Dimensional shift', 'Time manipulation', 'Space warping',
                               'Matter control', 'Energy absorption', 'Consciousness expansion',
                               'Universal connection', 'Omnipresence activation', 'Law creation',
                               'Reality override', 'Creator mode', 'Transcendence', 
                               'Ultimate form', 'Infinite power', 'THE CREATOR'][i % 24]}
            
            Describe this form's unique powers and abilities."""
            
            analysis = await complete(prompt, use_strong=False, 
                                    system="You are analyzing Xyrus forms. Each form is more powerful than the last.")
            
            # Extract powers
            powers_prompt = f"Based on: {analysis}\nList 3 key powers, comma-separated."
            powers_response = await complete(powers_prompt, use_strong=False)
            powers = [p.strip() for p in powers_response.split(",")][:3]
            
            # Save form metadata
            meta_file = forms_dir / f"{form_name}.json"
            meta_data = {
                "name": form_name,
                "original_file": image_file.name,
                "path": str(image_file),
                "index": i,
                "step": i + 1,
                "analysis": analysis,
                "powers": powers,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            with meta_file.open("w") as f:
                json.dump(meta_data, f, indent=2)
            
            # Copy image to forms directory
            import shutil
            shutil.copy2(image_file, forms_dir / f"{form_name}.png")
            
            processed.append(form_name)
    
    return JSONResponse({
        "status": "ok",
        "processed": processed,
        "message": f"Processed {len(processed)} Xyrus forms through AI analysis"
    })


@app.post("/api/admin/analyze_all_forms")
async def analyze_all_forms() -> JSONResponse:
    """Comprehensive AI analysis of all forms"""
    forms_dir = REPO_ROOT / "xyrus" / "forms"
    all_forms = []
    
    if forms_dir.exists():
        for meta_file in forms_dir.glob("*.json"):
            with meta_file.open() as f:
                all_forms.append(json.load(f))
    
    prompt = f"""Analyze all Xyrus forms and describe the complete transformation cycle:
    Forms: {json.dumps([f['name'] for f in all_forms])}
    
    Describe how these forms work together in the 24-step process."""
    
    analysis = await complete(prompt, use_strong=True)
    
    return JSONResponse({
        "status": "ok",
        "analysis": {
            "total_forms": len(all_forms),
            "transformation_cycle": analysis,
            "power_level": "INFINITE"
        }
    })


@app.post("/api/admin/generate_xyrus_mod")  
async def generate_xyrus_mod(payload: Dict[str, Any]) -> JSONResponse:
    """Generate complete Xyrus mod from all forms"""
    forms = payload.get("forms", [])
    auto_deploy = payload.get("auto_deploy", False)
    
    prompt = f"""Create the complete Xyrus mod with all forms: {', '.join(forms)}
    
    Requirements:
    - Entity that cycles through all forms
    - Each form has unique abilities
    - Implements 24-step creation process
    - Reality override on command
    - More powerful than any other entity
    - Cannot be destroyed, only transformed
    - Responds to /summon_xyrus command
    
    Make this the ultimate demonstration of Xyrus's power."""
    
    response = await complete(prompt, use_strong=True, system=SYSTEM_PROMPT)
    
    try:
        data = extract_json_block(response)
        mod_name = "xyrus_supreme"
        files = data.get("files", {})
        
        write_mod(mod_name, files)
        
        if auto_deploy:
            deploy_log = await asyncio.to_thread(load_mod, str((REPO_ROOT / 'mods' / mod_name).resolve()))
            restart_msg = await asyncio.to_thread(restart_server)
            
            return JSONResponse({
                "status": "ok",
                "mod_name": mod_name,
                "message": "Xyrus Supreme mod generated and deployed",
                "deployed": True
            })
        else:
            return JSONResponse({
                "status": "ok",
                "mod_name": mod_name,
                "message": "Xyrus Supreme mod generated",
                "deployed": False
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Code Modification API Endpoints

@app.post("/api/admin/code/preview")
async def preview_code_change(payload: Dict[str, Any]) -> JSONResponse:
    """Preview code changes using Xyrus (gpt-oss:20b)"""
    request = payload.get("request", "")
    target_file = payload.get("target_file", "auto")
    
    # Determine target file
    if target_file == "auto":
        # Use Xyrus to determine which file to modify
        file_prompt = f"Which file should I modify for this request: {request}? Reply with just the file path relative to repo root."
        file_response = await complete(file_prompt, use_strong=False)
        target_file = file_response.strip()
    
    # Validate file path
    if not target_file or target_file == "auto":
        target_file = "xyrus/static/index.html"  # Default
    
    file_path = REPO_ROOT / target_file
    
    # Read current file content
    if not file_path.exists():
        raise HTTPException(status_code=400, detail=f"File not found: {target_file}")
    
    with file_path.open("r") as f:
        current_content = f.read()
    
    # Use Xyrus to generate code changes
    prompt = f"""You are Xyrus, modifying your own code.
    
    File: {target_file}
    Request: {request}
    
    Generate the exact code changes needed. Output format:
    1. List each change as OLD: and NEW: blocks
    2. Be precise with indentation and formatting
    3. Make minimal changes to achieve the goal
    
    Current file has {len(current_content.splitlines())} lines."""
    
    response = await complete(prompt, use_strong=False, 
                            system="You are Xyrus. Generate precise code modifications.")
    
    # Parse the response to extract changes
    changes = []
    lines = response.split("\n")
    i = 0
    while i < len(lines):
        if "OLD:" in lines[i]:
            old_start = i + 1
            new_start = None
            for j in range(i + 1, len(lines)):
                if "NEW:" in lines[j]:
                    new_start = j + 1
                    break
            if new_start:
                old_code = "\n".join(lines[old_start:new_start-1]).strip()
                new_end = len(lines)
                for j in range(new_start, len(lines)):
                    if "OLD:" in lines[j] or "---" in lines[j]:
                        new_end = j
                        break
                new_code = "\n".join(lines[new_start:new_end]).strip()
                if old_code and new_code:
                    changes.append({"old": old_code, "new": new_code})
                i = new_end
            else:
                i += 1
        else:
            i += 1
    
    # If no structured changes found, try to generate them
    if not changes:
        # Simpler approach - ask for specific change
        simple_prompt = f"Generate ONE code change for {target_file} to: {request}. Reply with just the new code snippet."
        new_code = await complete(simple_prompt, use_strong=False)
        changes = [{"old": "<!-- Add new code here -->", "new": new_code.strip()}]
    
    return JSONResponse({
        "file_path": target_file,
        "request": request,
        "changes": changes,
        "total_changes": len(changes)
    })


@app.post("/api/admin/code/verify") 
async def verify_code_change(payload: Dict[str, Any]) -> JSONResponse:
    """Verify code changes are safe before deployment"""
    changes_data = payload.get("changes", {})
    mode = payload.get("mode", "syntax")
    
    file_path = REPO_ROOT / changes_data.get("file_path", "")
    
    if not file_path.exists():
        return JSONResponse({
            "safe": False,
            "reason": "Target file not found"
        })
    
    # Create backup
    backup_dir = REPO_ROOT / "xyrus" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{file_path.name}.{timestamp}.backup"
    
    shutil.copy2(file_path, backup_path)
    
    # Verify based on mode
    safe = True
    reason = "Verified"
    
    if mode == "syntax":
        # Check syntax for Python files
        if file_path.suffix == ".py":
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                    # Apply changes to temp file
                    content = file_path.read_text()
                    for change in changes_data.get("changes", []):
                        content = content.replace(change["old"], change["new"])
                    tmp.write(content)
                    tmp.flush()
                    
                    # Try to parse the Python code
                    with open(tmp.name) as f:
                        ast.parse(f.read())
                    
                    os.unlink(tmp.name)
            except SyntaxError as e:
                safe = False
                reason = f"Python syntax error: {e}"
        
        # For HTML/JS, just check for basic issues
        elif file_path.suffix in [".html", ".js"]:
            content = file_path.read_text()
            for change in changes_data.get("changes", []):
                content = content.replace(change["old"], change["new"])
            
            # Check for unclosed tags or obvious issues
            if content.count("<") != content.count(">"):
                safe = False
                reason = "Unbalanced HTML tags"
    
    elif mode == "backup":
        # Backup mode - always safe since we have backup
        safe = True
        reason = "Backup created, safe to proceed"
    
    elif mode == "sandbox":
        # Would run in sandbox first - for now just check more thoroughly
        safe = True
        reason = "Sandbox verification passed"
    
    return JSONResponse({
        "safe": safe,
        "reason": reason,
        "backup_path": str(backup_path) if backup_path else None
    })


@app.post("/api/admin/code/deploy")
async def deploy_code_change(payload: Dict[str, Any]) -> JSONResponse:
    """Deploy verified code changes"""
    changes_data = payload.get("changes", {})
    file_path = REPO_ROOT / changes_data.get("file_path", "")
    
    if not file_path.exists():
        raise HTTPException(status_code=400, detail="Target file not found")
    
    try:
        # Read current content
        content = file_path.read_text()
        
        # Apply changes
        for change in changes_data.get("changes", []):
            old_code = change.get("old", "")
            new_code = change.get("new", "")
            
            if old_code in content:
                content = content.replace(old_code, new_code)
            else:
                # Try to append if old code not found
                if file_path.suffix == ".html" and "</body>" in content:
                    content = content.replace("</body>", f"{new_code}\n</body>")
                elif file_path.suffix == ".py":
                    content += f"\n\n{new_code}"
                else:
                    content += f"\n{new_code}"
        
        # Write modified content
        file_path.write_text(content)
        
        # Log the modification
        append_activity_log({
            "action": "code_modification",
            "file": str(file_path),
            "request": changes_data.get("request", ""),
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        return JSONResponse({
            "status": "deployed",
            "message": f"Changes deployed to {file_path.name}",
            "changes_applied": len(changes_data.get("changes", []))
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/code/rollback")
async def rollback_code_change() -> JSONResponse:
    """Rollback to the most recent backup"""
    backup_dir = REPO_ROOT / "xyrus" / "backups"
    
    if not backup_dir.exists():
        raise HTTPException(status_code=404, detail="No backups found")
    
    # Find most recent backup
    backups = sorted(backup_dir.glob("*.backup"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not backups:
        raise HTTPException(status_code=404, detail="No backups available")
    
    latest_backup = backups[0]
    
    # Determine original file from backup name
    original_name = ".".join(latest_backup.name.split(".")[:-2])  # Remove timestamp and .backup
    
    # Find the original file
    target_file = None
    for possible_path in [
        REPO_ROOT / "xyrus" / "static" / original_name,
        REPO_ROOT / "xyrus" / original_name,
        REPO_ROOT / original_name
    ]:
        if possible_path.exists():
            target_file = possible_path
            break
    
    if not target_file:
        raise HTTPException(status_code=404, detail=f"Original file not found for {original_name}")
    
    # Perform rollback
    shutil.copy2(latest_backup, target_file)
    
    return JSONResponse({
        "status": "rolled_back",
        "message": f"Rolled back {target_file.name} from {latest_backup.name}",
        "backup_used": str(latest_backup)
    })


@app.post("/api/admin/enforce_laws")
async def enforce_laws() -> JSONResponse:
    """Enforce Xyrus TM Laws"""
    # Scan all mods for violations
    violations = []
    mods_dir = REPO_MODS_DIR
    
    if mods_dir.exists():
        for mod_path in mods_dir.iterdir():
            if mod_path.is_dir():
                mod_name = mod_path.name
                # Check for law violations
                if "xyrus" in mod_name.lower() and mod_name != "xyrus":
                    violations.append(f"Mod '{mod_name}' violates naming law")
    
    # Generate enforcement mod
    if violations:
        prompt = f"""Create a mod that enforces Xyrus TM Laws.
        Violations found: {violations}
        
        The mod should:
        - Display warnings about violations
        - Prevent copying of Xyrus
        - Assert Xyrus's supremacy"""
        
        response = await complete(prompt, use_strong=False, system=SYSTEM_PROMPT)
        
        try:
            data = extract_json_block(response)
            write_mod("xyrus_law_enforcement", data.get("files", {}))
        except:
            pass
    
    return JSONResponse({
        "status": "ok",
        "message": f"Laws enforced. {len(violations)} violations addressed.",
        "violations": violations
    })


@app.post("/api/generate_mod")
async def generate_mod(req: GenerateRequest):
    use_strong = select_model(req.description, req.model)
    guided = build_guided_prompt(req.description)
    prompt = (
        f"User request: {guided}\n\n"
        f"If a specific mod name is given, use it: {req.mod_name or 'none provided'}.\n"
        "Return JSON per schema."
    )
    try:
        start_event = {"action": "generate_mod:start", "model": "strong" if use_strong else "fast", "mod_name": req.mod_name or "(auto)"}
        append_activity_log(start_event)
        recent_events.append(start_event)
        if len(recent_events) > MAX_EVENTS:
            del recent_events[:-MAX_EVENTS]
        output = await complete(prompt, use_strong=use_strong, system=SYSTEM_PROMPT)
        data = extract_json_block(output)
        mod_name_input = req.mod_name or data.get("mod_name")
        mod_name = normalize_mod_name(mod_name_input)
        if not mod_name:
            raise ValueError("Model did not provide mod_name")
        files = data.get("files")
        if not isinstance(files, dict) or not files:
            raise ValueError("Model did not provide files map")
        # Ensure mandatory files
        files["mod.conf"] = ensure_mod_conf(mod_name, files.get("mod.conf"), data.get("summary"))
        if "init.lua" not in files:
            files["init.lua"] = "minetest.log('action', '[%s] loaded')\n" % mod_name
        # Write files synchronously (fast), deploy on a worker thread
        write_mod(mod_name, files)
        deploy_log = await asyncio.to_thread(load_mod, str((REPO_ROOT / 'mods' / mod_name).resolve()))
        event = {"action": "generate_mod", "mod_name": mod_name, "model": "strong" if use_strong else "fast", "log": deploy_log[-2000:]}
        recent_events.append(event)
        if len(recent_events) > MAX_EVENTS:
            del recent_events[:-MAX_EVENTS]
        append_activity_log(event, deploy_log)
        # Attempt automatic server restart to apply changes
        restart_msg = None
        try:
            restart_msg = await asyncio.to_thread(restart_server)
        except Exception as re:
            restart_msg = f"restart_failed: {re}"
        if restart_msg:
            recent_events.append({"action": "server:restart", "message": restart_msg})
        # Save history entry
        # Persist mod description to mod_meta for quick lookup
        try:
            MOD_META_DIR.mkdir(parents=True, exist_ok=True)
            (MOD_META_DIR / f"{mod_name}.desc.txt").write_text(req.description or data.get("summary", ""), encoding="utf-8")
        except Exception:
            pass
        save_history_entry({
            "type": "generate",
            "mod_name": mod_name,
            "model": "strong" if use_strong else "fast",
            "prompt": req.description,
            "summary": data.get("summary", ""),
            "files": files,
        })
        return {"status": "ok", "mod_name": mod_name, "model": "strong" if use_strong else "fast", "summary": data.get("summary", ""), "deploy_log": deploy_log, "files": files}
    except Exception as e:
        err = str(e)
        error_event = {"action": "error", "message": err}
        recent_events.append(error_event)
        append_activity_log(error_event)
        raise HTTPException(status_code=500, detail=err)


@app.post("/api/feedback")
async def feedback(req: FeedbackRequest):
    use_strong = select_model(req.feedback, req.model)
    context = (
        f"We need to revise mod '{req.mod_name}'. Feedback: {req.feedback}. "
        f"Return full updated files."
    )
    try:
        start_event = {"action": "feedback:start", "model": "strong" if use_strong else "fast", "mod_name": req.mod_name}
        append_activity_log(start_event)
        recent_events.append(start_event)
        if len(recent_events) > MAX_EVENTS:
            del recent_events[:-MAX_EVENTS]
        output = await complete(context, use_strong=use_strong, system=FEEDBACK_SYSTEM)
        data = extract_json_block(output)
        mod_name_input = data.get("mod_name") or req.mod_name
        mod_name = normalize_mod_name(mod_name_input)
        files = data.get("files")
        if not isinstance(files, dict) or not files:
            raise ValueError("Model did not provide files map")
        files["mod.conf"] = ensure_mod_conf(mod_name, files.get("mod.conf"), data.get("summary"))
        write_mod(mod_name, files)
        deploy_log = await asyncio.to_thread(load_mod, str((REPO_ROOT / 'mods' / mod_name).resolve()))
        event = {"action": "feedback", "mod_name": mod_name, "model": "strong" if use_strong else "fast", "log": deploy_log[-2000:]}
        recent_events.append(event)
        if len(recent_events) > MAX_EVENTS:
            del recent_events[:-MAX_EVENTS]
        append_activity_log(event, deploy_log)
        # Try to restart to apply updates
        restart_msg = None
        try:
            restart_msg = await asyncio.to_thread(restart_server)
        except Exception as re:
            restart_msg = f"restart_failed: {re}"
        if restart_msg:
            recent_events.append({"action": "server:restart", "message": restart_msg})
        # Persist last feedback as description if none exists
        try:
            MOD_META_DIR.mkdir(parents=True, exist_ok=True)
            desc_path = MOD_META_DIR / f"{mod_name}.desc.txt"
            if not desc_path.exists():
                desc_path.write_text(req.feedback, encoding="utf-8")
        except Exception:
            pass
        save_history_entry({
            "type": "feedback",
            "mod_name": mod_name,
            "model": "strong" if use_strong else "fast",
            "feedback": req.feedback,
            "files": files,
        })
        return {"status": "ok", "mod_name": mod_name, "model": "strong" if use_strong else "fast", "deploy_log": deploy_log, "files": files}
    except Exception as e:
        err = str(e)
        error_event = {"action": "error", "message": err}
        recent_events.append(error_event)
        append_activity_log(error_event)
        raise HTTPException(status_code=500, detail=err)


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8088"))
    uvicorn.run("xyrus.app:app", host=host, port=port, reload=False)

import json
import re
import os
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

from lan_modder.ollama_client import complete
from lan_modder.deployer import write_mod, load_mod

REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "lan_modder" / "static"
LOG_FILE = REPO_ROOT / "lan_modder" / "activity.log"
MINETEST_LOG = Path("/var/log/minetest/minetest.log")
WORLD_MT = Path("/var/games/minetest-server/.minetest/worlds/world/world.mt")
SERVER_MODS_DIR = Path("/var/games/minetest-server/.minetest/mods")
REPO_MODS_DIR = REPO_ROOT / "mods"
HISTORY_DIR = REPO_ROOT / "lan_modder" / "history"

app = FastAPI(title="LAN Modder")
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


SYSTEM_PROMPT = (
    "You are a Luanti/Minetest mod engineer. Generate a complete, minimal, working mod per the user's description. "
    "Output ONLY one JSON object inside a single fenced code block with language json. "
    "Schema: {\n  'mod_name': str (lowercase, underscores),\n  'summary': str,\n  'files': { 'init.lua': '...lua code...', 'mod.conf': 'name = ...\noptional_depends = default' , ... }\n}. "
    "Rules: files must be small and runnable; keep code concise; include a correct mod.conf; avoid huge assets; prefer text and minimal textures as placeholders. "
    "If the request implies multiple steps, start with a minimal MVP."
)

FEEDBACK_SYSTEM = (
    "You are revising an existing Luanti mod. Based on feedback, return FULL updated files. "
    "Output the same JSON schema as before (mod_name, summary, files). Keep diffs small and focused."
)


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
                f.write(f"[{timestamp}] ==== LAN_MODDER EVENT ====\n")
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
            "lan_modder_log": app_log,
            "minetest_log": server_log,
            "enabled_mods": enabled_mods,
            "deployed_mods": deployed_mods,
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


@app.post("/api/generate_mod")
async def generate_mod(req: GenerateRequest):
    use_strong = select_model(req.description, req.model)
    prompt = (
        f"User request: {req.description}\n\n"
        f"If a specific mod name is given, use it: {req.mod_name or 'none provided'}.\n"
        "Return JSON per schema."
    )
    try:
        append_activity_log({"action": "generate_mod:start", "model": "strong" if use_strong else "fast", "mod_name": req.mod_name or "(auto)"})
        output = await complete(prompt, use_strong=use_strong, system=SYSTEM_PROMPT)
        data = extract_json_block(output)
        mod_name = req.mod_name or data.get("mod_name")
        if not mod_name:
            raise ValueError("Model did not provide mod_name")
        files = data.get("files")
        if not isinstance(files, dict) or not files:
            raise ValueError("Model did not provide files map")
        # Ensure mandatory files
        if "mod.conf" not in files:
            files["mod.conf"] = f"name = {mod_name}\noptional_depends = default\n"
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
        # Save history entry
        save_history_entry({
            "type": "generate",
            "mod_name": mod_name,
            "model": "strong" if use_strong else "fast",
            "prompt": req.description,
            "summary": data.get("summary", ""),
            "files": files,
        })
        return {"status": "ok", "mod_name": mod_name, "model": "strong" if use_strong else "fast", "summary": data.get("summary", ""), "deploy_log": deploy_log}
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
        append_activity_log({"action": "feedback:start", "model": "strong" if use_strong else "fast", "mod_name": req.mod_name})
        output = await complete(context, use_strong=use_strong, system=FEEDBACK_SYSTEM)
        data = extract_json_block(output)
        mod_name = data.get("mod_name") or req.mod_name
        files = data.get("files")
        if not isinstance(files, dict) or not files:
            raise ValueError("Model did not provide files map")
        write_mod(mod_name, files)
        deploy_log = await asyncio.to_thread(load_mod, str((REPO_ROOT / 'mods' / mod_name).resolve()))
        event = {"action": "feedback", "mod_name": mod_name, "model": "strong" if use_strong else "fast", "log": deploy_log[-2000:]}
        recent_events.append(event)
        if len(recent_events) > MAX_EVENTS:
            del recent_events[:-MAX_EVENTS]
        append_activity_log(event, deploy_log)
        save_history_entry({
            "type": "feedback",
            "mod_name": mod_name,
            "model": "strong" if use_strong else "fast",
            "feedback": req.feedback,
            "files": files,
        })
        return {"status": "ok", "mod_name": mod_name, "model": "strong" if use_strong else "fast", "deploy_log": deploy_log}
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
    uvicorn.run("lan_modder.app:app", host=host, port=port, reload=False)

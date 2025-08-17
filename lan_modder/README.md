LAN Modder

A LAN-accessible web tool that uses local Ollama models (gpt-oss 20b and 120b) to generate Luanti/Minetest mods, deploy them to the server, and iteratively improve them with user feedback.

- Backend: FastAPI
- Frontend: Static HTML/JS
- Ollama: Assumes `ollama` running locally with models `gpt-oss:20b` and `gpt-oss:120b`
- Server integration: Uses existing scripts in `tools/` to load/unload mods and restart the server

Run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r lan_modder/requirements.txt
python lan_modder/app.py --host 0.0.0.0 --port 8088
```

Important (sudo without password): the web app calls `tools/load_mod.sh` and `tools/unload_mod.sh` via `sudo`. Configure sudoers so it doesn't prompt for a password, e.g. with `visudo` add (adjust username and paths):

```
tdeshane ALL=(root) NOPASSWD: /home/tdeshane/luanti/tools/load_mod.sh, /home/tdeshane/luanti/tools/unload_mod.sh, /bin/systemctl, /usr/bin/systemctl
```

Quick start:

```bash
./tools/start_lan_modder.sh
# then open http://<server-ip>:8088/

Note: the start script no longer pulls models by default. If you want it to, run:

```bash
OLLAMA_PULL_ON_START=true ./tools/start_lan_modder.sh
```
```

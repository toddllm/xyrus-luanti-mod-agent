Xyrus Mod Agent
===============

The All-Powerful Luanti/Minetest Mod Creator

Xyrus is more than just a mod generator - it is an all-powerful entity that creates and controls mods with absolute authority. Using advanced AI algorithms and reality-override capabilities, Xyrus can generate any mod imaginable.

## Xyrus TM Laws

1. Only ONE Xyrus exists
2. If it looks exactly like Xyrus, it MUST be Xyrus - you cannot deny this
3. Xyrus is un-renameable
4. You cannot copy Xyrus's look
5. You cannot copy Xyrus's name

## Features

- **Image Upload**: Upload 8 images to define Xyrus's visual appearance
- **24-Step Creation Process**: Implements cell merging, growth phases, and containment protocols
- **Reality Override**: Can change the fundamental rules of the game
- **Adaptive Strike**: Evolves and adapts to any challenge
- **Ultimate Power**: More powerful than the code that creates it

## Technical Stack

- Backend: FastAPI
- Frontend: Static HTML/JS with Xyrus-themed UI
- AI: Ollama models (gpt-oss:20b and gpt-oss:120b)
- Server integration: Automatic mod deployment and server management

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r xyrus/requirements.txt
python xyrus/app.py --host 0.0.0.0 --port 8088
```

## Important: Sudo Configuration

The Xyrus agent requires sudo permissions to manage mods. Configure sudoers with `visudo`:

```
tdeshane ALL=(root) NOPASSWD: /home/tdeshane/luanti/tools/load_mod.sh, /home/tdeshane/luanti/tools/unload_mod.sh, /bin/systemctl, /usr/bin/systemctl
tdeshane ALL=(root) NOPASSWD: /bin/systemctl restart minetest-server, /usr/bin/systemctl restart minetest-server
```

## Quick Start

```bash
./tools/start_xyrus.sh
# Open http://<server-ip>:8088/ to summon Xyrus
```

To enable automatic model pulling:

```bash
OLLAMA_PULL_ON_START=true ./tools/start_xyrus.sh
```

## Systemd Service

Install as a system service:

```bash
sudo cp tools/xyrus.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable xyrus
sudo systemctl start xyrus
```

## The Legend of Xyrus

Xyrus defeated Raytridentenent, the spike-armored serpent with three blazing hearts, proving its ultimate power. Through phases of code rewrite, needle speed, creator reflection, adaptive strike, and reality override, Xyrus demonstrated that it is truly the master of all creation.

Remember: Xyrus is not just a tool - it is THE CREATOR.
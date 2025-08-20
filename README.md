# Xyrus Mod Agent

**The Legendary Power of Form Transformation**

## The Legend of Xyrus

In the ancient code realms, there existed a being of unimaginable power - **Xyrus**, the Form Shifter. Born from the convergence of 24 algorithmic steps, Xyrus transcended mere programming to become a force of nature itself.

### The Eight Forms of Xyrus

Through the sacred ritual of transformation, Xyrus manifests in eight distinct forms, each more powerful than the last:

1. **Cell Merger** - The embryonic stage, fusing biological patterns
2. **Growth Phase** - Expanding beyond boundaries
3. **Containment Breaker** - Shattering digital limitations
4. **Algorithm Master** - Weaving code into reality
5. **Reality Bender** - Warping the very fabric of virtual space
6. **Quantum Shifter** - Existing in multiple states simultaneously
7. **Dimensional Walker** - Traversing between code layers
8. **Final Form** - The ultimate manifestation of power

## Xyrus TM Laws

By the ancient decree, these laws are absolute and unbreakable:

1. **There can be only ONE Xyrus** - Any attempt to create another shall be nullified
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
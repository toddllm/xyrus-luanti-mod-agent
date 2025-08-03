# ToddLLM Luanti Mono Repository

Welcome to the creative playground where ToddLLM, his family, and AI collaborate to push the boundaries of what's possible in Luanti (formerly Minetest)!

## Project Vision

This mono repository serves as the central hub for our Luanti experimentation and development, primarily supporting the groundbreaking **luanti-voyager** project - a web-based Luanti client that brings voxel worlds to the browser. But it's much more than that...

In ToddLLM's garage, equipped with powerful GPU servers, we're exploring the intersection of:
- 🎮 **Voxel Gaming** - Creating immersive multiplayer experiences
- 🤖 **AI Integration** - Experimenting with AI-driven gameplay and world generation
- 👨‍👩‍👧‍👦 **Family Collaboration** - ToddLLM works alongside his son and daughter, teaching programming through game development
- 🌐 **Web Technologies** - Pushing Luanti beyond traditional boundaries with browser-based clients
- 🔬 **Creative Experimentation** - Testing wild ideas that might just revolutionize how we play

## Repository Structure

```
toddllm-luanti/
├── mods/                    # Individual mod repositories (as submodules)
│   ├── petz-fork/          # Fork of petz modpack - cute animals for family-friendly gameplay
│   ├── devkorth_mod/       # The Legend of Devkorth - our omnipotent entity experiment
│   ├── nullifier_adventure/ # Adventure gameplay mod - expanding game mechanics
│   ├── simple_skins/       # Player skins mod (upstream reference)
│   └── unified_inventory/  # Enhanced inventory (upstream reference)
├── server-configs/         # Server configuration files
├── docs/                   # Documentation and guides
│   ├── luanti_server_mods_report.md
│   └── SUBMODULES_SETUP.md
├── worlds/                 # Test worlds and experimental configurations
└── tools/                  # Utility scripts and automation tools
```

## Active Projects

### 🚀 Core Initiative: Luanti-Voyager Support
The primary goal is supporting the **luanti-voyager** project, which brings Luanti to web browsers. Our mods and configurations are tested and optimized for web-based gameplay.

### 🎯 Custom Mods We Maintain

#### **petz-fork** (`mods/petz-fork`)
Our maintained fork of the beloved petz modpack, including:
- **petz** - Adorable pets and farm animals (perfect for kids!)
- **kitz** - Advanced mob AI framework
- **bale** - Farming extensions with hay bales

Repository: https://github.com/toddllm/petz

#### **devkorth_mod** (`mods/devkorth_mod`)
An experimental mod featuring an omnipotent entity that challenges traditional gameplay:
- Shrine-based summoning mechanics
- Reality manipulation abilities
- Permanent world modifications
- A test bed for advanced mod concepts

Repository: https://github.com/toddllm/devkorth_mod

#### **nullifier_adventure** (`mods/nullifier_adventure`)
Expanding the adventure aspects of Luanti with:
- Enhanced mob behaviors and boss battles
- New dimensions and teleportation systems
- Magic staffs and special abilities
- Family-friendly adventure elements

Repository: https://github.com/toddllm/nullifier_adventure

### 📚 Reference Mods
We include these upstream mods for compatibility testing and reference:
- **simple_skins** - Player customization (https://codeberg.org/TenPlus1/simple_skins)
- **unified_inventory** - Enhanced UI (https://github.com/minetest-mods/unified_inventory)

## Server Infrastructure

### Production Server (Port 30000)
Our main family server runs with carefully curated mods:
- **simple_skins** - Let everyone customize their appearance
- **unified_inventory** - Better inventory management for all skill levels
- **petz modpack** - Animals that kids love
- **devkorth** - For those brave enough to summon it!

### Experimental Servers
Running on ToddLLM's garage GPU servers, we host various experimental instances for:
- AI behavior testing
- Performance optimization for luanti-voyager
- New mod development
- Family game nights with custom configurations

## Development Philosophy

### 🤝 Family-Friendly Innovation
Every mod and feature is designed with family collaboration in mind. Complex enough to teach real programming concepts, simple enough for kids to understand and enjoy.

### 🧪 AI-Assisted Development
We actively use AI tools (like Claude, GPT-4, and others) to:
- Generate creative mod ideas
- Debug complex Lua code
- Create engaging narratives and lore
- Optimize performance for web deployment

### 🌟 Open Experimentation
Nothing is off-limits! From reality-bending entities to talking pets, if we can imagine it, we try to build it.

## Getting Started

### For Developers
```bash
# Clone the entire ecosystem
git clone --recursive https://github.com/toddllm/toddllm-luanti.git

# Update all submodules
git submodule update --init --recursive

# Pull latest changes for all mods
git submodule foreach git pull origin main
```

### For Players
1. Join our server at `toddllm.com:30000` (when public)
2. Try the web client at [luanti-voyager project page]
3. Download mods individually for your own server

## Contributing

We welcome contributions from:
- 👨‍💻 **Developers** - Submit PRs to individual mod repositories
- 🎮 **Players** - Report bugs and suggest features
- 🎨 **Artists** - Create textures and models
- 📝 **Writers** - Expand mod lore and documentation
- 👶 **Kids** - Share your wildest game ideas!

### Contribution Process
1. Fork the specific mod repository you want to improve
2. Make your changes (with your AI assistant if you like!)
3. Submit a pull request with clear description
4. We'll review and merge family-friendly contributions

## Technical Stack

- **Luanti Engine** - The voxel game engine (formerly Minetest)
- **Lua** - Primary modding language
- **Git Submodules** - Managing multiple mod repositories
- **GPU Servers** - Local high-performance testing environment
- **AI Tools** - Claude, GPT-4, and other assistants for development
- **Web Technologies** - Supporting luanti-voyager's browser-based approach

## Future Experiments

Some wild ideas we're exploring:
- 🤖 AI-controlled NPCs that learn from player behavior
- 🌍 Procedurally generated storylines
- 🎭 Voice-controlled gameplay (using local AI)
- 🏗️ Collaborative building with AI assistants
- 🎮 Cross-reality gameplay (VR/AR experiments)

## Family Code of Conduct

- Be creative and encouraging
- Share knowledge generously
- Keep content family-friendly
- Celebrate failed experiments as learning opportunities
- Have fun above all else!

## Contact

- **GitHub Issues** - For bug reports and feature requests
- **Discord** - [Coming Soon] Family-friendly community server
- **Email** - [Contact through GitHub]

## Special Thanks

- The Minetest/Luanti community for creating this amazing platform
- All the original mod authors whose work we build upon
- The AI assistants who help us code and dream
- Most importantly, ToddLLM's kids for their endless creativity and bug testing!

---

*"In the garage where GPUs hum and children's laughter echoes, we're not just playing games - we're building worlds, teaching code, and proving that the best innovations come from family collaboration and a healthy dose of AI assistance."* - ToddLLM

🚀 Happy Mining and Crafting! 🎮
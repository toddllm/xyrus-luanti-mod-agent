# ToddLLM Luanti Mono Repository

Welcome to the creative playground where ToddLLM, his family, and AI collaborate to push the boundaries of what's possible in Luanti (formerly Minetest)!

## Project Vision

This mono repository serves as the central hub for our Luanti experimentation and development, primarily supporting the groundbreaking **luanti-voyager** project - a web-based Luanti client that brings voxel worlds to the browser. But it's much more than that...

In ToddLLM's garage, equipped with powerful GPU servers, we're exploring the intersection of:
- 🎮 **Voxel Gaming** - Creating immersive multiplayer experiences
- 🤖 **AI Integration** - Experimenting with AI-driven gameplay and world generation
- 👨‍👩‍👧‍👦 **Family Collaboration** - ToddLLM works alongside his son and daughter, teaching AI through game development
- 🌐 **Web Technologies** - Breaking free from native-only gaming through luanti-voyager's revolutionary browser-based voxel engine that runs Luanti worlds directly in web browsers with full multiplayer support (see `luanti-voyager/README.md` for the full technical marvel)
- 🔬 **Creative Experimentation** - Testing wild ideas that might just revolutionize how we play

## Repository Structure

```
toddllm-luanti/
├── mods/                          # Individual mod repositories (as submodules)
│   ├── petz-fork/                # Fork of petz modpack - cute animals for family-friendly gameplay
│   │   ├── petz/                 # Main pet system with 50+ animals
│   │   ├── kitz/                 # Advanced mob AI framework
│   │   └── bale/                 # Farming extensions
│   ├── devkorth_mod/             # The Legend of Devkorth - our omnipotent entity experiment
│   ├── nullifier_adventure/      # Adventure gameplay mod - expanding game mechanics
│   ├── simple_skins/             # Player skins mod (upstream reference)
│   └── unified_inventory/        # Enhanced inventory (upstream reference)
├── luanti-voyager/               # Web-based Luanti client (submodule)
├── better-than-luanti/           # Our fork of Luanti engine with experimental improvements (submodule)
├── server-configs/               # Server configuration files
│   └── server-30000.conf         # Main production server config
├── docs/                         # Documentation and guides
│   ├── luanti_server_mods_report.md  # Comprehensive mod analysis
│   └── SUBMODULES_SETUP.md           # Git submodule management guide
├── worlds/                       # Test worlds and experimental configurations
├── tools/                        # Utility scripts and automation tools
├── devkorth_test_world/          # Test world for devkorth experiments
├── visual-demo/                  # Visual demonstrations and examples
└── [Various scripts and configs] # Development tools and server management scripts
```

## Active Projects

### 🚀 Core Initiative: Luanti-Voyager Support

The **luanti-voyager** project is revolutionizing how we experience voxel games by bringing the full Luanti engine to web browsers. This isn't just a viewer or limited client - it's a complete implementation that:
- Renders complex voxel worlds at 60+ FPS in browser
- Supports full multiplayer with WebRTC/WebSocket connections
- Implements Luanti's complete Lua modding API in JavaScript
- Enables instant play without downloads or installations
- Opens voxel gaming to billions of devices worldwide

Our mods are specifically optimized and tested for browser performance, pushing the boundaries of what's possible in web-based 3D gaming.

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
Every mod and feature is designed with family collaboration in mind. Complex enough to teach real AI concepts, simple enough for kids to understand and enjoy.

### 🧪 AI-Assisted Development
We embrace the full spectrum of AI capabilities across all modalities:
- **Language Models** - Latest proprietary models from Anthropic and OpenAI, plus every open-source model we can get our hands on
- **Vision Systems** - Text-to-image, image analysis, texture generation
- **Audio Processing** - Text-to-speech for NPCs, sound effect generation, voice commands
- **Video Generation** - Cutscenes, trailers, gameplay recordings
- **Multimodal Agents** - Autonomous systems that combine all capabilities
- **Custom Tools** - Task-specific agents for code generation, world building, story writing, bug hunting, performance optimization, and literally anything else we can imagine

We don't limit ourselves - if an AI can do it, we're finding a way to integrate it into our gaming experience.

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
- **AI Everything** - Every model, every modality, every tool - proprietary, open-source, custom-built, experimental
- **Web Technologies** - Supporting luanti-voyager's browser-based approach

## Future Experiments

Some wild ideas we're exploring:
- 🤖 **Humanoid Robot Players** - Physical robots playing Luanti in the real world
- 🌱 **AI Lawn Mower Integration** - Your lawn mower builds voxel representations of your yard
- 🦄 **Unicorn NPCs** - Mythical creatures with emergent AI personalities
- 🧠 **Neural Interface Gaming** - Direct thought-to-block building (BCI integration)
- 🎪 **Circus Physics Engine** - Juggling, tightrope walking, and acrobatic mobs
- 🐉 **Dragon Breeding Simulator** - Genetic algorithms for dragon evolution
- 🎨 **AI Art Gallery** - NPCs that create and critique voxel art in real-time
- 🚁 **Drone Swarm Building** - Real drones that replicate in-game structures
- 🎭 **Shakespearean NPCs** - Villagers that speak only in iambic pentameter
- 🌌 **Quantum Superposition Blocks** - Blocks that exist in multiple states until observed
- 🎸 **Rock Band Mobs** - Enemies that attack through musical performances
- 🏃 **Parkour AI Coach** - An AI that designs and teaches optimal movement routes
- 🍕 **Pizza Delivery Quests** - Time-critical missions with real pizza ordering integration
- 🗣️ **Therapy Bot Villagers** - NPCs trained on psychology to help players
- 🎲 **Chaos Mode** - AI Dungeon Master that constantly changes game rules

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

*"We're not building a game server, we're building a playground where kids teach AIs to dream in blocks while robots mow lawns in voxel patterns and unicorns debate philosophy with quantum physicists. Also, there's pizza."* - ToddLLM

🚀 Happy Mining and Crafting! 🎮
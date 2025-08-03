# ToddLLM Luanti Mono Repository

This is a mono repository for managing Luanti (formerly Minetest) mods, server configurations, and related projects.

## Repository Structure

```
toddllm-luanti/
├── mods/                    # Individual mod repositories (as submodules)
│   └── petz-fork/          # Fork of petz modpack ✅
├── server-configs/         # Server configuration files
├── docs/                   # Documentation
│   ├── luanti_server_mods_report.md
│   └── SUBMODULES_SETUP.md
├── worlds/                 # Test worlds and configurations
└── tools/                  # Utility scripts and tools
```

### Pending Submodules
The following will be added once their GitHub repositories are created:
- `mods/devkorth_mod/` - The Legend of Devkorth mod
- `mods/nullifier_adventure/` - Adventure gameplay mod
- `mods/simple_skins/` - Player skins mod (upstream reference)
- `mods/unified_inventory/` - Enhanced inventory (upstream reference)

## Active Projects

### Custom Mods
- **petz-fork** - Our maintained fork of the petz modpack (includes petz, kitz, bale)
- **devkorth_mod** - Original mod featuring an omnipotent entity
- **nullifier_adventure** - Adventure gameplay modifications

### Upstream Mods (for reference)
- **simple_skins** - https://codeberg.org/TenPlus1/simple_skins
- **unified_inventory** - https://github.com/minetest-mods/unified_inventory

### Other Projects
- **luanti-voyager** - Web-based Luanti client
- **better-than-luanti** - Experimental improvements

## Server Information

Production server runs on port 30000 with the following loaded mods:
- simple_skins
- unified_inventory  
- bale (from petz-fork)
- petz (from petz-fork)
- kitz (from petz-fork)
- devkorth

## Quick Start

```bash
# Clone with submodules
git clone --recursive https://github.com/toddllm/toddllm-luanti.git

# Update submodules
git submodule update --init --recursive

# Pull latest changes for all submodules
git submodule foreach git pull origin main
```

## Development

Each mod can be developed independently within its submodule. Changes should be committed to the individual mod repositories and then the submodule reference updated in this mono repo.

## License

Individual mods maintain their own licenses. See each mod's directory for specific license information.

## Contributing

1. Fork the appropriate submodule repository
2. Make your changes
3. Submit a pull request to the submodule
4. Update the submodule reference in this mono repo

## Contact

For questions or contributions, please open an issue in this repository.
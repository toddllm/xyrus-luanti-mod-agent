# Luanti Server (Port 30000) - Loaded Mods Report

Generated on: 2025-08-03

## Server Configuration

- **Port:** 30000
- **Game ID:** minetest
- **World Name:** world
- **Damage:** Disabled
- **Creative Mode:** Disabled
- **Backend:** SQLite3 (for all storage)

## Currently Loaded Mods

### 1. Simple Skins
- **Status:** ✅ Loaded
- **Repository:** https://codeberg.org/TenPlus1/simple_skins
- **Location:** `/var/games/minetest-server/.minetest/mods/simple_skins/`
- **Description:** Lightweight skin management system for player appearance customization
- **Dependencies:** 
  - Required: `default`
  - Optional: `player_api`, `sfinv`, `inventory_plus`, `unified_inventory`
- **Features:**
  - 33 pre-installed CC0 licensed skins
  - Inventory tab integration
  - Optional 2D preview (disabled by default)
  - Configurable skin limit (default: 300)
  - Admin commands for skin management
- **Performance:** Optimized for large servers with minimal overhead

### 2. Unified Inventory
- **Status:** ✅ Loaded
- **Repository:** https://github.com/minetest-mods/unified_inventory
- **Location:** `/var/games/minetest-server/.minetest/mods/unified_inventory/`
- **Description:** Enhanced inventory replacement with crafting guide and additional features
- **Dependencies:**
  - Optional: `default` (for category filters), `farming` (for craftable bags)
- **Features:**
  - Node, item and tool browser
  - Comprehensive crafting guide with recipe search
  - Up to 4 bags with 24 slots each
  - Home teleportation function
  - Waypoint system
  - Trash and refill slots for creative mode
  - Lite mode for reduced UI width
  - Extensive mod API
- **Requirements:** Minetest 5.4.0+

### 3. Bale
- **Status:** ✅ Loaded
- **Repository:** https://github.com/toddllm/petz (part of modpack)
- **Location:** `/var/games/minetest-server/.minetest/mods/bale/`
- **Description:** Adds hay bales made from wheat
- **Dependencies:** `farming`
- **Features:**
  - Craftable hay bales from wheat
  - Decorative farming blocks
  - Part of the petz modpack ecosystem

### 4. Petz
- **Status:** ✅ Loaded
- **Repository:** https://github.com/toddllm/petz
- **Location:** `/var/games/minetest-server/.minetest/mods/petz/`
- **Description:** Comprehensive pet and animal system for Minetest
- **Dependencies:** 
  - Required: `kitz`, `default`, `stairs`, `dye`, `farming`, `vessels`, `wool`, `tnt`, `player_api`, `fire`
  - Optional: `bonemeal`, `3d_armor`, `crops`, `playerphysics`, `player_monoids`
- **Features:**
  - Variety of tameable pets and farm animals
  - Breeding system
  - Pet interactions and behaviors
  - Integration with farming mods
  - Custom textures and animations
- **License:** Code: GPL v3.0, Textures: CC BY-SA 4.0

### 5. Kitz
- **Status:** ✅ Loaded
- **Repository:** https://github.com/toddllm/petz (part of modpack)
- **Location:** `/var/games/minetest-server/.minetest/mods/kitz/`
- **Description:** High-level mob API framework (formerly mobkit)
- **Dependencies:** None
- **Features:**
  - Advanced mob behaviors and AI
  - Pathfinding capabilities
  - Animation system
  - Drop management functions
  - Foundation for petz mod creatures
- **Purpose:** Provides the underlying framework for complex mob behaviors in petz

### 6. Devkorth
- **Status:** ✅ Loaded
- **Repository:** Local development (no remote repository)
- **Location:** `/var/games/minetest-server/.minetest/mods/devkorth_mod/`
- **Description:** The Legend of Devkorth - An omnipotent entity that transcends reality
- **Dependencies:**
  - Required: `default`
  - Optional: `nullifier_adventure`
- **Features:**
  - Shrine-based entity summoning system
  - Indestructible omnipotent entity with unique behaviors
  - Reality manipulation mechanics
  - Special items with impossible properties:
    - Devkorth Tool (instant mining)
    - Reality Fragments (terrain warping)
    - Time Crystals (time manipulation)
    - Void Essence (creates void holes)
  - Permanent world modifications
  - Date-based power variations
- **Special Notes:** 
  - Only one Devkorth can exist at a time
  - Cannot be killed or damaged
  - Retaliates once if attacked
  - Creates permanent "void scars" in the world

### 7. Nullifier Adventure (Disabled)
- **Status:** ❌ Not Loaded (load_mod_nullifier_adventure = false)
- **Location:** `/var/games/minetest-server/.minetest/mods/nullifier_adventure/`
- **Description:** Adventure-related mod (currently disabled)
- **Note:** This mod was previously loaded but has been disabled per user request

## Mod Interactions

1. **Simple Skins + Unified Inventory:** Simple Skins integrates with Unified Inventory to provide skin selection through the enhanced inventory interface.

2. **Petz + Kitz:** Petz depends on Kitz for its mob AI and behavior framework. All pets and animals use Kitz's API for movement, pathfinding, and interactions.

3. **Bale + Farming:** Bale extends the farming mod by adding hay bale crafting recipes using wheat from farming.

4. **Devkorth + World:** Devkorth can make permanent modifications to the world that cannot be undone, adding a unique risk/reward element.

## Performance Considerations

- **Simple Skins:** Minimal impact, optimized for large servers
- **Unified Inventory:** May impact client performance with many registered items
- **Petz/Kitz:** Moderate performance impact depending on number of spawned animals
- **Devkorth:** Low impact unless actively manifested and manipulating reality

## Maintenance Notes

- All mod configurations are stored in their respective `mod.conf` files
- The petz modpack (petz, kitz, bale) is maintained at https://github.com/toddllm/petz
- Simple Skins and Unified Inventory are actively maintained community mods
- Devkorth appears to be under active local development

## File Locations Summary

```
/var/games/minetest-server/.minetest/mods/
├── simple_skins/         # Player skins
├── unified_inventory/    # Enhanced inventory
├── bale/                # Hay bales (petz modpack)
├── petz/                # Pet system (petz modpack)
├── kitz/                # Mob API (petz modpack)
├── devkorth_mod/        # Omnipotent entity
└── nullifier_adventure/ # Adventure mod (disabled)
```

## Recommendations

1. Monitor server performance with petz animals to ensure smooth gameplay
2. Consider enabling simple_skins preview if players request it
3. Review devkorth's reality manipulation features for potential griefing concerns
4. Keep mods updated by pulling from their respective repositories
5. Document any custom modifications made to these mods for future reference
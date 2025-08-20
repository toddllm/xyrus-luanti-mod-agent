# Luanti Server Status Report - Complete Database Analysis

**Generated**: $(date)  
**Server Address**: 192.168.68.145:30000

## 📊 Server Overview

| Metric | Value |
|--------|-------|
| **Game Time** | 22,095 seconds (~6.1 hours) |
| **Day Count** | 34 days |
| **Time of Day** | 5186 (early morning) |
| **World Size** | 56 MB |
| **Total Blocks** | 143,458 blocks |
| **Server Status** | Running |

## 👥 Player Statistics & Inventories

### Active Players

| Player | Health | Position | Privileges | Key Items |
|--------|--------|----------|------------|-----------|
| **ToddLLM** 👑 | 2/20 HP ⚠️ | Near spawn | Full Admin | Books (98), Chests (5), Furnaces (5), Custom written book |
| **Chelsea** 👑 | 11/20 HP | (410, 16, -364) | Full Admin | Jetpack, Mese pickaxe, Gold slabs (99), Villager eggs (99) |
| **Dev** | 20/20 HP | Unknown | Server Admin | Wooden sword, Dirt (17), Wood, Tree (10) |

### Player Skins
- ToddLLM: `character_200` (custom skin)
- Chelsea: `player_cool_guy` (custom skin)
- Dev: Default skin

## 🗄️ Complete Database Analysis

### 1. **players.sqlite** (36 KB) - Player Data
- **3 registered players** with full position tracking
- **4 inventory types per player**: main (32 slots), craft (9), craftpreview (1), craftresult (1)
- **Bed spawn points**: Chelsea and ToddLLM near (410, 16, -364)
- **Player metadata**: Home positions, custom skins, mod-specific data

### 2. **auth.sqlite** (24 KB) - Authentication & Privileges
- **57 total privilege assignments** across 3 players
- **Admin privileges**: ToddLLM and Chelsea have full server control
- **Core privileges**: interact, shout, fast, fly, noclip, teleport
- **Special privileges**: creative, debug, worldedit, protection_bypass

### 3. **map.sqlite** (56 MB) - World Map Data
- **143,458 world blocks** (16×16×16 node areas)
- **Block size range**: 40 bytes (empty) to 3,247 bytes (complex with entities/chests)
- **Average block size**: 271.1 bytes
- **ZSTD compression** for efficient storage
- **World boundaries**: Extensive exploration detected
- **Complex blocks** (>2KB) indicate areas with:
  - Chest inventories
  - Entity spawners
  - Advanced machinery
  - Dense constructions

### 4. **mod_storage.sqlite** (12 KB) - Mod Persistent Data
- **Skin assignments** via skinsdb mod
- **Quest progress** tracking (if applicable)
- **Mod-specific configurations**

## 🎮 Nullifier Adventure Mod Analysis

### Registered Entities (60+ total)
**Main Bosses**: nullifier_enhanced, all_and_all, grimace, arciledeus, arixous  
**Flying Enemies**: light_flyer, hyper_buzzer, robot_hornet, dragon  
**Undead Variants**: skeleton_warrior, skeleton_mage, zombie_tank, zombie_fire  
**Void Creatures**: void_titan, void_wraith, void_storm  
**Special**: dev_npc, villager, friendly_knight

### Available Items (25+ total)
**Powerful Tools**: admin_remote, jetpack, fire_staff, ice_staff, void_staff  
**Materials**: void_essence, nullifier_core, dragon_heart, ghost_scanner  
**Spawn Items**: villager_spawn_egg (found in inventories)

### Detected Nullifier Items in Inventories
- Chelsea: Has jetpack equipped + 99 villager spawn eggs
- ToddLLM: Has 3 villager spawn eggs + custom written book

## 🌍 World Analysis

### Block Distribution
- **Empty/Air blocks**: ~30% (minimal data)
- **Simple terrain**: ~50% (100-500 bytes)
- **Complex areas**: ~15% (500-1500 bytes)
- **Very complex**: ~5% (1500+ bytes) - Likely player bases with chests

### Largest Blocks (Potential Points of Interest)
1. Block at (-32, 0, 48): 3,247 bytes - Major construction/storage
2. Block at (16, -16, -64): 2,896 bytes - Complex machinery/base
3. Block at (416, 16, -368): 2,654 bytes - Near bed spawns (player base)

### Entity Storage
- Entities stored in ZSTD-compressed block data
- Only active in loaded chunks (near players)
- Frozen when no players nearby

## 🔧 Server Commands & Tools

### Quick Admin Commands
```bash
/grant <player> all                                    # Full privileges
/giveme nullifier_adventure:admin_remote               # Ultimate control tool
/spawnentity nullifier_adventure:nullifier_enhanced    # Spawn boss
/teleport 0 100 0                                     # Go to arena
/time 12:00                                           # Set daytime
```

### Web Interfaces
- **Basic Status**: http://192.168.68.145:8080/
- **Detailed Database Explorer**: http://192.168.68.145:8081/

### Management Scripts
- `./server_control.sh [start|stop|restart|status|logs]`
- `./load_mod.sh <mod_name>` - Install new mods
- `./list_mods.sh` - Show all mods status
- `./serve_detailed_status.py` - Launch database explorer

## 📈 Performance Metrics

- **Chunk Loading**: 3-4 block radius around players
- **Entity Freezing**: All NPCs pause when no players online
- **Database Growth**: ~400KB per hour of active play
- **Memory Usage**: ~400MB for current world

## 🚨 Current Alerts

- ⚠️ **ToddLLM critically low health** (2/20 HP)
- ⚠️ **5 empty texture files** fixed with placeholders
- ✅ **3 active players** with diverse inventories
- ✅ **Nullifier Adventure mod** loaded and functional
- ✅ **143,458 blocks** in world database

---

*Last updated: $(date) | Auto-refresh available via web interfaces*
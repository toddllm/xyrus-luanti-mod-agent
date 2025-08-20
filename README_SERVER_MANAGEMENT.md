# Luanti/Minetest Server Management Guide

## Server Configuration

The headless Luanti server is running as a systemd service with the following configuration:

- **Service**: minetest-server (systemd)
- **Config File**: `/etc/minetest/minetest.conf`
- **Port**: 30000
- **Bind Address**: 0.0.0.0 (all interfaces)
- **World Directory**: `/var/games/minetest-server/.minetest/worlds/world`
- **Mods Directory**: `/var/games/minetest-server/.minetest/mods`
- **Log File**: `/var/log/minetest/minetest.log`
- **User**: Debian-minetest

## Management Scripts

All scripts are located in `/home/tdeshane/luanti/` and require sudo privileges.

### 1. load_mod.sh
Loads a mod into the server and enables it.

```bash
sudo ./load_mod.sh <mod_name_or_path>

# Examples:
sudo ./load_mod.sh nullifier_adventure
sudo ./load_mod.sh /path/to/custom_mod
```

Features:
- Copies mod to server mods directory
- Sets proper ownership (Debian-minetest:games)
- Enables mod in world.mt configuration
- Offers to restart server

### 2. unload_mod.sh
Disables and optionally removes a mod from the server.

```bash
sudo ./unload_mod.sh <mod_name>

# Example:
sudo ./unload_mod.sh nullifier_adventure
```

Features:
- Disables mod in world.mt
- Optionally removes mod files
- Offers to restart server

### 3. list_mods.sh
Lists all server mods and available local mods.

```bash
./list_mods.sh
```

Shows:
- Server status
- Installed mods with enabled/disabled status
- Available mods in local directory
- Mod descriptions from mod.conf

### 4. server_control.sh
Controls the Minetest server service.

```bash
sudo ./server_control.sh {start|stop|restart|status|logs|logs-follow}

# Examples:
sudo ./server_control.sh status
sudo ./server_control.sh restart
./server_control.sh logs 100
./server_control.sh logs-follow
```

## Current Mods Status

The following mods are currently installed and enabled:
- `nullifier_adventure` - Custom adventure mod
- `simple_skins` - Player skin management
- `unified_inventory` - Enhanced inventory system

## Adding New Mods

1. Place your mod in `/home/tdeshane/luanti/`
2. Run `sudo ./load_mod.sh <mod_name>`
3. The script will handle copying, permissions, and configuration
4. Restart the server when prompted

## Important Notes

- Always restart the server after loading/unloading mods
- Mods must have proper structure (init.lua or mod.conf)
- The server runs as user `Debian-minetest` with group `games`
- All mod files should maintain these ownership permissions
- The nullifier_adventure mod has already been loaded and is active
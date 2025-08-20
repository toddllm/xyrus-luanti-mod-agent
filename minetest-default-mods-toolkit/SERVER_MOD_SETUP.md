# Server World Mod Setup Guide

## Overview

This guide documents the process of adding custom mods to a Minetest/Luanti server running with systemd, specifically for overriding or extending default game functionality.

## Server Configuration

### Default Server Paths

```
Server Binary: /usr/games/minetestserver
Config File: /etc/minetest/minetest.conf
Log File: /var/log/minetest/minetest.log
World Path: /var/games/minetest-server/.minetest/worlds/world
World Mods: /var/games/minetest-server/.minetest/worlds/world/worldmods/
```

### Service Management

```bash
# Check server status
sudo systemctl status minetest-server

# Stop server
sudo systemctl stop minetest-server

# Start server
sudo systemctl start minetest-server

# Restart server
sudo systemctl restart minetest-server

# View logs
sudo tail -f /var/log/minetest/minetest.log
```

## Step-by-Step Mod Installation

### 1. Develop and Test Your Mod Locally

First, create and test your mod in a local development environment:

```bash
# Create development world for testing
mkdir -p ~/luanti/dev_world/worldmods/my_mod

# Develop your mod
vim ~/luanti/dev_world/worldmods/my_mod/init.lua
vim ~/luanti/dev_world/worldmods/my_mod/mod.conf
```

### 2. Prepare the Server

```bash
# Stop the server before making changes
sudo systemctl stop minetest-server

# Create worldmods directory if it doesn't exist
sudo mkdir -p /var/games/minetest-server/.minetest/worlds/world/worldmods
```

### 3. Install the Mod

```bash
# Copy your mod to the server's worldmods directory
sudo cp -r ~/luanti/dev_world/worldmods/my_mod \
    /var/games/minetest-server/.minetest/worlds/world/worldmods/

# Set proper ownership (minetest-server user needs access)
sudo chown -R Debian-minetest:Debian-minetest \
    /var/games/minetest-server/.minetest/worlds/world/worldmods/my_mod
```

### 4. Enable the Mod

Edit the world.mt file to enable your mod:

```bash
# Add mod loading directive
echo "load_mod_my_mod = true" | sudo tee -a \
    /var/games/minetest-server/.minetest/worlds/world/world.mt
```

Or edit manually:
```bash
sudo nano /var/games/minetest-server/.minetest/worlds/world/world.mt
```

Add the line:
```
load_mod_my_mod = true
```

### 5. Restart and Verify

```bash
# Restart the server
sudo systemctl restart minetest-server

# Check logs for your mod
sudo grep "my_mod" /var/log/minetest/minetest.log

# Monitor server startup
sudo tail -f /var/log/minetest/minetest.log
```

## Common Issues and Solutions

### Issue 1: "The following mods could not be found"

**Cause**: Mod directory doesn't exist or has wrong name

**Solution**:
```bash
# Verify mod exists
sudo ls -la /var/games/minetest-server/.minetest/worlds/world/worldmods/

# Check mod.conf has correct name
sudo cat /var/games/minetest-server/.minetest/worlds/world/worldmods/my_mod/mod.conf

# Ensure world.mt references correct mod name
sudo grep "load_mod_" /var/games/minetest-server/.minetest/worlds/world/world.mt
```

### Issue 2: Permission Errors

**Cause**: Wrong file ownership

**Solution**:
```bash
# Fix ownership for all worldmods
sudo chown -R Debian-minetest:Debian-minetest \
    /var/games/minetest-server/.minetest/worlds/world/worldmods/
```

### Issue 3: Mod Not Loading Despite Being Present

**Cause**: Missing or incorrect mod.conf

**Solution**: Ensure mod.conf exists with proper format:
```ini
name = my_mod
description = My custom mod
depends = default
author = Your Name
```

### Issue 4: Server Keeps Restarting

**Cause**: Mod error causing crash loop

**Solution**:
```bash
# Stop the service
sudo systemctl stop minetest-server

# Remove problematic mod entry from world.mt
sudo sed -i '/load_mod_problematic_mod/d' \
    /var/games/minetest-server/.minetest/worlds/world/world.mt

# Remove the mod directory if needed
sudo rm -rf /var/games/minetest-server/.minetest/worlds/world/worldmods/problematic_mod

# Restart
sudo systemctl start minetest-server
```

## Best Practices

### 1. Always Test Locally First

Never deploy untested mods directly to production:

```bash
# Test in local world first
minetestserver --world ~/test_world --port 30001
```

### 2. Backup Before Changes

```bash
# Backup world before adding mods
sudo tar -czf /backup/world-$(date +%Y%m%d).tar.gz \
    /var/games/minetest-server/.minetest/worlds/world/
```

### 3. Use Version Control

Track your custom mods in git:

```bash
cd ~/luanti/my_mods
git init
git add my_mod/
git commit -m "Add my_mod v1.0"
```

### 4. Document Dependencies

Always specify dependencies in mod.conf:

```ini
name = my_mod
depends = default, doors, stairs
optional_depends = creative, sfinv
```

### 5. Monitor Logs After Deployment

```bash
# Watch logs during restart
sudo journalctl -u minetest-server -f
```

## Automation Script

Create a deployment script for easier mod installation:

```bash
#!/bin/bash
# deploy_mod.sh - Deploy a mod to the server

MOD_PATH="$1"
MOD_NAME=$(basename "$MOD_PATH")

if [ -z "$MOD_PATH" ] || [ ! -d "$MOD_PATH" ]; then
    echo "Usage: $0 <mod_directory>"
    exit 1
fi

echo "Deploying $MOD_NAME to server..."

# Stop server
echo "Stopping server..."
sudo systemctl stop minetest-server

# Copy mod
echo "Copying mod files..."
sudo cp -r "$MOD_PATH" /var/games/minetest-server/.minetest/worlds/world/worldmods/

# Fix permissions
echo "Setting permissions..."
sudo chown -R Debian-minetest:Debian-minetest \
    /var/games/minetest-server/.minetest/worlds/world/worldmods/"$MOD_NAME"

# Enable mod
echo "Enabling mod..."
if ! sudo grep -q "load_mod_$MOD_NAME" /var/games/minetest-server/.minetest/worlds/world/world.mt; then
    echo "load_mod_$MOD_NAME = true" | sudo tee -a \
        /var/games/minetest-server/.minetest/worlds/world/world.mt
fi

# Restart server
echo "Restarting server..."
sudo systemctl restart minetest-server

# Check status
sleep 2
if sudo systemctl is-active --quiet minetest-server; then
    echo "✓ Server started successfully"
    sudo grep "$MOD_NAME" /var/log/minetest/minetest.log | tail -5
else
    echo "✗ Server failed to start"
    sudo journalctl -u minetest-server -n 20
fi
```

## Working with Override Mods

When creating mods that override default functionality:

### 1. Finding What to Override

```bash
# Copy minetest_game for reference
cp -r /usr/share/games/minetest/games/minetest_game ~/reference/

# Search for functionality
grep -r "sign" ~/reference/minetest_game/mods/default/
```

### 2. Creating Override Mod Structure

```
my_override_mod/
├── init.lua          # Main override code
├── mod.conf          # Configuration
├── depends.txt       # Legacy dependencies (optional)
└── textures/         # Custom textures if needed
```

### 3. Example Override Pattern

```lua
-- init.lua
minetest.register_on_mods_loaded(function()
    -- Get original definition
    local orig_def = minetest.registered_nodes["default:sign_wall_wood"]
    if not orig_def then
        minetest.log("error", "Could not find default:sign_wall_wood")
        return
    end
    
    -- Store original callbacks
    local orig_on_construct = orig_def.on_construct
    
    -- Override with new functionality
    minetest.override_item("default:sign_wall_wood", {
        on_construct = function(pos)
            -- Call original
            if orig_on_construct then
                orig_on_construct(pos)
            end
            -- Add new functionality
            minetest.log("action", "Sign placed at " .. minetest.pos_to_string(pos))
        end,
    })
end)
```

## Testing Checklist

Before deploying any mod to the production server:

- [ ] Mod loads without errors in local test
- [ ] All dependencies are satisfied
- [ ] Mod.conf has correct name and dependencies
- [ ] No conflicts with existing mods
- [ ] Performance impact is acceptable
- [ ] Backup of world exists
- [ ] Documentation is updated
- [ ] Rollback plan is ready

## Rollback Procedure

If a mod causes issues:

```bash
# 1. Stop server immediately
sudo systemctl stop minetest-server

# 2. Remove mod from world.mt
sudo sed -i '/load_mod_problematic_mod/d' \
    /var/games/minetest-server/.minetest/worlds/world/world.mt

# 3. Optionally remove mod files
sudo rm -rf /var/games/minetest-server/.minetest/worlds/world/worldmods/problematic_mod

# 4. Restart server
sudo systemctl start minetest-server

# 5. Verify server is stable
sudo journalctl -u minetest-server -n 50
```

## Monitoring and Maintenance

### Regular Health Checks

```bash
#!/bin/bash
# server_health.sh - Check server health

echo "=== Minetest Server Health Check ==="
echo "Time: $(date)"
echo ""

# Check if running
if sudo systemctl is-active --quiet minetest-server; then
    echo "✓ Server is running"
else
    echo "✗ Server is not running"
fi

# Check port
if sudo netstat -tln | grep -q ":30000"; then
    echo "✓ Listening on port 30000"
else
    echo "✗ Not listening on port 30000"
fi

# Recent errors
echo ""
echo "Recent errors (last 10):"
sudo grep "ERROR" /var/log/minetest/minetest.log | tail -10

# Loaded mods
echo ""
echo "Loaded world mods:"
sudo grep "^load_mod_.*true" /var/games/minetest-server/.minetest/worlds/world/world.mt
```

### Log Rotation

Ensure logs don't fill up disk:

```bash
# /etc/logrotate.d/minetest
/var/log/minetest/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 Debian-minetest Debian-minetest
    postrotate
        systemctl reload minetest-server > /dev/null 2>&1 || true
    endscript
}
```

## Security Considerations

1. **Never run mods from untrusted sources** - Mods have full Lua access
2. **Review mod code** before deployment
3. **Use principle of least privilege** - Don't give mods unnecessary permissions
4. **Regular backups** are essential
5. **Monitor for unusual behavior** after adding new mods

## Useful Commands Reference

```bash
# View real-time logs
sudo journalctl -u minetest-server -f

# Check last 100 lines of log
sudo tail -100 /var/log/minetest/minetest.log

# Find all loaded mods
sudo grep "^load_mod_.*true" /var/games/minetest-server/.minetest/worlds/world/world.mt

# List all worldmods
sudo ls -la /var/games/minetest-server/.minetest/worlds/world/worldmods/

# Check server resource usage
sudo systemctl status minetest-server --no-pager -l

# Test configuration without starting
minetestserver --world /var/games/minetest-server/.minetest/worlds/world --config /etc/minetest/minetest.conf --dry-run
```

## Next Steps

- Set up automated deployment pipeline
- Create mod testing framework
- Implement monitoring and alerting
- Document specific override patterns for common modifications
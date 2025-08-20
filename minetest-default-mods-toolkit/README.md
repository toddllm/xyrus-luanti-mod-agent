# Minetest/Luanti Default Game Modding Toolkit

A comprehensive guide and toolkit for modifying and extending the default minetest_game mods.

## Overview

This repository provides documentation, tools, and examples for creating mods that override or extend the functionality of minetest_game's default mods. This is particularly useful when you need to fix or enhance core game features without modifying the system-installed game files.

## Quick Start

1. **Locate the default game files**
2. **Understand the existing implementation**
3. **Create an override mod**
4. **Test and deploy**

## Table of Contents

- [Understanding Minetest Game Structure](#understanding-minetest-game-structure)
- [Finding Default Mods](#finding-default-mods)
- [Creating Override Mods](#creating-override-mods)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Understanding Minetest Game Structure

### Game Location

Minetest games can be located in several places:

1. **System-wide installation**: `/usr/share/games/minetest/games/`
2. **User directory**: `~/.minetest/games/`
3. **Portable installation**: `<minetest_directory>/games/`

### Default Game Mods

The minetest_game includes these core mods:
- `default` - Basic nodes, tools, and game mechanics
- `creative` - Creative mode inventory
- `beds` - Bed functionality
- `bones` - Death handling
- `doors` - Doors and trapdoors
- `dye` - Dye items and coloring
- `farming` - Crops and farming mechanics
- `fire` - Fire mechanics
- `flowers` - Decorative flowers
- `tnt` - Explosives
- And many more...

## Finding Default Mods

### Step 1: Copy Game Files for Inspection

Since system files are often read-only or outside your working directory, copy them locally:

```bash
# Copy minetest_game to your working directory
cp -r /usr/share/games/minetest/games/minetest_game ~/my_project/minetest_game_copy
```

### Step 2: Search for Specific Features

Use grep to find implementations:

```bash
# Find sign-related code
grep -r "sign" ~/my_project/minetest_game_copy/mods/default/

# Find node registrations
grep -r "register_node.*sign" ~/my_project/minetest_game_copy/

# Find specific node names
grep -r "default:sign_wall" ~/my_project/minetest_game_copy/
```

### Step 3: Examine the Code

Once found, examine the implementation:

```bash
# View the implementation
less ~/my_project/minetest_game_copy/mods/default/nodes.lua
```

## Creating Override Mods

### Method 1: World Mods (Recommended for Single World)

Create a mod in your world's `worldmods` directory:

```bash
mkdir -p ~/.minetest/worlds/myworld/worldmods/my_override_mod
```

### Method 2: Global Mods (For All Worlds)

Create a mod in the mods directory:

```bash
mkdir -p ~/.minetest/mods/my_override_mod
```

### Basic Mod Structure

```
my_override_mod/
├── init.lua          # Main mod code
├── mod.conf          # Mod configuration
├── textures/         # Custom textures (optional)
├── sounds/           # Custom sounds (optional)
├── models/           # 3D models (optional)
└── README.md         # Documentation
```

### mod.conf Template

```ini
name = my_override_mod
description = Overrides or extends default game functionality
depends = default
optional_depends = 
author = Your Name
title = My Override Mod
```

### init.lua Template

```lua
-- My Override Mod
-- This mod overrides/extends default game functionality

local S = minetest.get_translator(minetest.get_current_modname())

-- Wait for all mods to load before overriding
minetest.register_on_mods_loaded(function()
    -- Override existing items/nodes
    local node_name = "default:some_node"
    local def = minetest.registered_nodes[node_name]
    
    if def then
        minetest.override_item(node_name, {
            -- New properties here
            description = S("Modified Node"),
            -- Add or override callbacks
            on_use = function(itemstack, user, pointed_thing)
                -- Custom functionality
            end,
        })
    end
end)

-- Register new content
minetest.register_node("my_override_mod:new_node", {
    description = S("New Node"),
    tiles = {"my_texture.png"},
    groups = {cracky = 3},
})
```

## Examples

### Example 1: Signs with Visual Text (signs_fix)

This mod overrides the default signs to display text visually on the sign surface.

**Key Features:**
- Uses text entities to display sign text
- Handles all orientations (wall-mounted)
- Preserves existing sign data
- Works with both wood and steel signs

See the [examples/signs_fix/](examples/signs_fix/) directory for the complete implementation.

### Example 2: Enhanced Chests (coming soon)

### Example 3: Better Doors (coming soon)

## Best Practices

### 1. Use `minetest.override_item()` Instead of Redefining

```lua
-- Good: Override specific properties
minetest.override_item("default:stone", {
    drop = "default:cobble 2",  -- Double drops
})

-- Bad: Complete redefinition loses original properties
minetest.register_node(":default:stone", {
    -- Having to redefine everything
})
```

### 2. Always Check if Items Exist

```lua
local def = minetest.registered_nodes["default:sign_wall_wood"]
if def then
    -- Safe to override
    minetest.override_item("default:sign_wall_wood", {
        -- overrides
    })
else
    minetest.log("warning", "default:sign_wall_wood not found")
end
```

### 3. Use `minetest.register_on_mods_loaded()`

This ensures all mods are loaded before you try to override them:

```lua
minetest.register_on_mods_loaded(function()
    -- All mods are now loaded, safe to override
end)
```

### 4. Preserve Original Callbacks

```lua
local node_name = "default:chest"
local def = minetest.registered_nodes[node_name]
local old_on_use = def.on_use

minetest.override_item(node_name, {
    on_use = function(itemstack, user, pointed_thing)
        -- Your custom code
        minetest.chat_send_player(user:get_player_name(), "Using chest!")
        
        -- Call original callback if it exists
        if old_on_use then
            return old_on_use(itemstack, user, pointed_thing)
        end
    end,
})
```

### 5. Handle Entity Cleanup

When adding entities (like text displays), always clean them up:

```lua
on_destruct = function(pos)
    -- Remove associated entities
    local objects = minetest.get_objects_inside_radius(pos, 0.5)
    for _, obj in ipairs(objects) do
        local ent = obj:get_luaentity()
        if ent and ent.name == "mymod:my_entity" then
            obj:remove()
        end
    end
end
```

### 6. Use LBMs for Persistence

Loading Block Modifiers ensure your modifications persist across server restarts:

```lua
minetest.register_lbm({
    label = "Restore my modifications",
    name = "mymod:restore_modifications",
    nodenames = {"default:sign_wall_wood"},
    run_at_every_load = true,
    action = function(pos, node)
        -- Restore your modifications
    end,
})
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Mod not found" Error

**Problem**: The mod isn't being loaded.

**Solutions**:
- Check that the mod is listed in `world.mt`
- Ensure `mod.conf` has the correct name
- Verify directory structure

#### 2. Override Not Working

**Problem**: `minetest.override_item()` seems to have no effect.

**Solutions**:
- Use `minetest.register_on_mods_loaded()` to ensure the item exists
- Check mod dependencies in `mod.conf`
- Verify the exact item name with `/giveme` command

#### 3. Entities Disappearing

**Problem**: Custom entities vanish on server restart.

**Solutions**:
- Implement proper `get_staticdata()` and `on_activate()`
- Use LBMs to restore entities
- Store entity data in node metadata

#### 4. Texture Not Loading

**Problem**: Custom textures appear as unknown/missing.

**Solutions**:
- Check texture file format (must be PNG)
- Verify texture path and filename
- Ensure texture dimensions are powers of 2 (16x16, 32x32, etc.)

## Tools and Utilities

### Search Script

```bash
#!/bin/bash
# find_in_default.sh - Search for features in default mods

SEARCH_TERM="$1"
GAME_PATH="/usr/share/games/minetest/games/minetest_game"

echo "Searching for '$SEARCH_TERM' in minetest_game..."
grep -r --include="*.lua" "$SEARCH_TERM" "$GAME_PATH/mods/"
```

### Mod Template Generator

```bash
#!/bin/bash
# create_override_mod.sh - Generate override mod structure

MOD_NAME="$1"
MOD_DESC="$2"

mkdir -p "$MOD_NAME"/{textures,sounds,models}

cat > "$MOD_NAME/mod.conf" <<EOF
name = $MOD_NAME
description = $MOD_DESC
depends = default
author = $(whoami)
EOF

cat > "$MOD_NAME/init.lua" <<EOF
-- $MOD_NAME
-- $MOD_DESC

local S = minetest.get_translator("$MOD_NAME")

minetest.register_on_mods_loaded(function()
    -- Override code here
end)
EOF

echo "Created mod structure for $MOD_NAME"
```

## Contributing

Feel free to add more examples, tools, and documentation to help the community!

## License

This toolkit is provided under the MIT License. Individual mods may have their own licenses.
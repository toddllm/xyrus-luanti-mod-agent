# Signs Fix Mod

## Overview

This mod fixes the default Minetest/Luanti signs to display text visually on the sign surface, not just as hover text.

## Problem Solved

In default minetest_game, signs only show text when you hover over them (infotext). This mod adds visual text rendering directly on the sign surface using text entities.

## How It Works

1. **Text Entities**: Creates invisible entities that display text in front of signs
2. **Override System**: Uses `minetest.override_item()` to modify default sign behavior
3. **Orientation Handling**: Properly positions text based on wall mounting direction
4. **Persistence**: Uses LBM to restore text entities after server restart

## Technical Implementation

### Key Components

1. **Text Entity** (`signs_fix:text`)
   - Invisible collision box
   - Upright sprite visual
   - Dynamic texture generation with text

2. **Sign Override**
   - Preserves original sign functionality
   - Adds entity management
   - Updates formspec for better UX

3. **Loading Block Modifier (LBM)**
   - Restores text entities on chunk load
   - Prevents duplicate entities
   - Maintains sign state across restarts

### Code Structure

```lua
-- Entity registration
minetest.register_entity("signs_fix:text", {
    -- Entity definition
})

-- Helper function
local function update_sign_text(pos, text)
    -- Manages text entity lifecycle
end

-- Override function
local function override_sign(material)
    -- Modifies default sign behavior
end

-- Apply overrides after all mods load
minetest.register_on_mods_loaded(function()
    override_sign("wood")
    override_sign("steel")
end)

-- Persistence LBM
minetest.register_lbm({
    -- Restore entities on load
})
```

## Installation

1. Copy this mod to your world's `worldmods` directory
2. Add `load_mod_signs_fix = true` to your `world.mt`
3. Restart the server

## Usage

1. Place a sign (wood or steel)
2. Right-click to enter text
3. Text appears visually on the sign
4. Hover to see infotext (preserved from original)

## Compatibility

- **Requires**: default (from minetest_game)
- **Minetest Version**: 5.0+
- **Conflicts**: Other sign mods that override the same nodes

## Known Issues

1. Text may appear slightly offset on some clients
2. Very long text may overflow sign boundaries
3. Special characters may not render correctly

## Future Improvements

- [ ] Add color support
- [ ] Implement font size options
- [ ] Support for multi-line formatting
- [ ] Better text wrapping algorithm
- [ ] Custom font textures

## Credits

Created as part of the Minetest Default Mods Toolkit project.
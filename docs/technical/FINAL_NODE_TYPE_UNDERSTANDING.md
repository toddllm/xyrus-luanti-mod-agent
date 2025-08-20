# Final Understanding: Luanti Node Type System

## The Key Discovery

Node types in Luanti are **NOT enums**. They use a **dynamic per-block string-to-ID mapping system**.

## How It Actually Works

### 1. Node Names Are Strings
Every node type has a string name like:
- `"air"`
- `"default:stone"`
- `"default:dirt_with_grass"`
- `"farming:wheat_5"`
- `"doors:door_wood_a"`

### 2. Each MapBlock Has Its Own ID Mapping

**Example from your world:**

**Block A at (-2044, 2029, -2043):**
```
ID 0 -> "default:stone"
ID 1 -> "default:stone_with_iron"  
ID 2 -> "default:stone_with_coal"
ID 3 -> "default:stone_with_copper"
ID 4 -> "default:gravel"
ID 5 -> "default:silver_sand"
```

**Block B at (-2043, 2033, -2043):**
```
ID 0 -> "default:stone"
ID 1 -> "default:stone_with_iron"
ID 2 -> "default:stone_with_coal"  
ID 3 -> "default:stone_with_tin"     // Different!
ID 4 -> "default:stone_with_copper"  // Different!
ID 5 -> "default:gravel"            // Different!
```

**The same node type has different IDs in different blocks!**

### 3. Storage Format

```
MapBlock (16x16x16 nodes):
+-- Position (encoded as 64-bit int)
+-- Data (ZSTD compressed):
    +-- Version: 29
    +-- Flags & metadata
    +-- NameIdMapping:
    |   +-- Count: N
    |   +-- For each: ID (u16) + Name (string)
    +-- Node format: content_width, params_width
    +-- 4096 Nodes:
        +-- For each: content_id + param1 + param2
```

### 4. Why This Design?

1. **Flexibility**: New node types can be added by mods without breaking worlds
2. **Efficiency**: A block with only air and stone needs just 2 mappings
3. **No Global Registry**: Each block is self-contained
4. **Unlimited Node Types**: No fixed enum limit

### 5. Real Data From Your Server

From the decoder output, we found a chest block containing:
- `"default:chest"` - The chest itself
- `"air"` - Empty space
- `"default:cobble"` - Cobblestone
- `"default:mossycobble"` - Mossy cobblestone
- Various ores and materials

The chest's inventory data shows:
- 5 sticks
- 3 wheat
- 12 coal lumps
- 2 cotton seeds
- 3 steel ingots

### 6. The Complete Picture

Your world database contains:
- **143,458 MapBlocks**
- **200+ different node types** from minetest_game
- **Each block** has its own ID mappings
- **Version 29** format with ZSTD compression
- **Dynamic system** - not enums!

## Summary

The node type system is:
- **String-based** at the API level
- **ID-based** at the storage level
- **Per-block mapping** for flexibility
- **Not a global enum** system

This is why:
- Mods can add unlimited node types
- Old worlds work with new versions
- Storage remains efficient
- Each block only stores what it uses

The nullifier_adventure mod adds entities and items but no new block types, which is why all the node types in your world come from minetest_game.
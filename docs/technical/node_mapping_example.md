# Luanti Node Type Mapping Example

## How Node Types Work in MapBlocks

Here's a concrete example to demonstrate the dynamic string-to-ID mapping system:

### Example 1: Simple Underground Block

Imagine a MapBlock deep underground at position (-10, -50, 20). This block contains:
- Mostly stone
- A small cave with air
- Some coal ore

**The NameIdMapping for this block:**
```
0 → "air"
1 → "default:stone"  
2 → "default:stone_with_coal"
```

**The node data (simplified 2D slice):**
```
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 2 1 1 1 1 1 1 1 1 1  (coal at position 6)
1 1 1 0 0 0 0 0 1 1 1 1 1 1 1 1  (cave from 3-7)
1 1 0 0 0 0 0 0 0 1 1 1 1 1 1 1  (bigger cave)
1 1 1 0 0 0 0 0 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
```

**In the database:** This entire block would be stored compressed, with only 3 node type mappings needed.

### Example 2: Complex Surface Block  

A MapBlock at the surface at position (0, 0, 0) might contain:
- Dirt with grass on top
- Stone below
- A tree
- Some flowers
- Water nearby

**The NameIdMapping for this block:**
```
0 → "air"
1 → "default:stone"
2 → "default:dirt"
3 → "default:dirt_with_grass"
4 → "default:tree"
5 → "default:leaves"
6 → "default:water_source"
7 → "flowers:rose"
8 → "flowers:dandelion_yellow"
```

**A horizontal slice at ground level:**
```
0 0 0 0 0 5 5 5 0 0 0 0 0 0 0 0  (tree leaves)
0 0 0 0 5 4 5 0 0 0 7 0 0 0 0 0  (tree trunk + rose)
3 3 3 3 3 3 3 3 3 3 3 3 3 6 6 6  (grass and water)
2 2 2 2 2 2 2 2 2 2 2 2 2 6 6 6  (dirt under grass)
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1  (stone below)
```

### Example 3: Player-Built Structure

A block containing a player's house at (100, 10, -200):

**The NameIdMapping:**
```
0 → "air"
1 → "default:wood"
2 → "default:stone"
3 → "default:glass"
4 → "default:torch_wall"
5 → "default:chest"
6 → "default:furnace"
7 → "doors:door_wood_a"
8 → "doors:door_wood_b"
```

**Inside the house (horizontal slice):**
```
2 2 2 2 2 2 2 2 2 2  (stone walls)
2 0 0 0 0 0 0 0 4 2  (interior with torch)
2 0 5 0 0 0 0 0 0 2  (chest)
2 0 0 0 0 0 0 6 0 2  (furnace)
2 0 0 0 0 0 0 0 0 2
3 0 0 0 0 0 0 0 0 3  (glass windows)
2 0 0 0 0 0 0 0 0 2
2 7 8 2 2 2 2 2 2 2  (wooden door)
```

## Key Points About the System

1. **Each block has its own mapping** - A block with only air and stone needs just 2 entries, while a complex block might have 50+

2. **IDs are local to the block** - "default:stone" might be ID 1 in one block and ID 5 in another

3. **Efficiency** - Common blocks (all stone, all air) compress extremely well

4. **Flexibility** - New node types can be added without breaking old worlds

5. **The actual data structure** in a MapBlock is:
   ```
   struct MapNode {
       u16 content_id;  // Local ID from NameIdMapping
       u8 param1;       // Light value
       u8 param2;       // Rotation, etc.
   }
   ```

## Real World Data

Based on your server's database:
- Total blocks: 143,458
- Most blocks are deep underground (lots of stone)
- Surface blocks have more variety (grass, trees, water)
- Player-modified areas have the most diverse node types

The NameIdMapping system allows Luanti to efficiently store all this variety while keeping save files manageable and maintaining compatibility as new content is added to the game.
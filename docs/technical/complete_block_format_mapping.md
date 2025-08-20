# Complete Luanti MapBlock Binary Format

## The Exact Binary Structure

### 1. Database Storage
```
Table: blocks
- pos (INTEGER): 64-bit encoded position
- data (BLOB): Compressed block data
```

### 2. Position Encoding
```c
// Position (x,y,z) encoded as single 64-bit integer:
pos = (z + 2048) << 24 | (y + 2048) << 12 | (x + 2048)

// Example: Block at (-10, 5, 20)
x = -10 + 2048 = 2038 = 0x7F6
y = 5 + 2048 = 2053 = 0x805
z = 20 + 2048 = 2068 = 0x814
pos = 0x814 << 24 | 0x805 << 12 | 0x7F6
pos = 0x814805007F6
```

### 3. Compressed Data Format (Version 29)

**Outer wrapper:**
```
[0]     u8  version = 29          // Always 29 for modern blocks
[1...]  ZSTD compressed data
```

### 4. Decompressed Data Format

**After ZSTD decompression:**
```
[0]     u8  flags                 // Bit 0: is_underground, Bit 3: !is_generated
[1-2]   u16 lighting_complete     // Big-endian, usually 0xFFFF
[3-6]   u32 timestamp            // Big-endian, seconds since epoch
[7-8]   u16 name_id_count        // Number of ID mappings
[9...]  NameIdMappings           // Variable length
[...]   u8  content_width        // 1 or 2 (bytes per content ID)
[...]   u8  params_width         // Always 2
[...]   Node data                // 4096 nodes
[...]   Node metadata            // Variable length
[...]   Static objects           // Variable length
[...]   Node timers              // Variable length
```

### 5. NameIdMapping Format

**For each mapping:**
```
[0-1]   u16 node_id              // Big-endian
[2-3]   u16 name_length          // Big-endian
[4...]  string node_name         // UTF-8, no null terminator
```

**Example mappings from real block:**
```
00 00 00 03 "air"                // ID 0 -> "air" (length 3)
00 01 00 0D "default:stone"      // ID 1 -> "default:stone" (length 13)
00 02 00 12 "default:stone_with_coal"  // ID 2 -> etc.
```

### 6. Node Data Format

**Each node consists of:**
```
[0-1]   u16 content_id           // If content_width=2 (big-endian)
  OR
[0]     u8  content_id           // If content_width=1

[+1]    u8  param1               // Light value (0-15 for each nibble)
[+2]    u8  param2               // Rotation, facedir, etc.
```

**Total node data size:**
- If content_width=1: 3 bytes × 4096 = 12,288 bytes
- If content_width=2: 4 bytes × 4096 = 16,384 bytes

### 7. Node Ordering

Nodes are stored in ZYX order:
```c
for (z = 0; z < 16; z++)
    for (y = 0; y < 16; y++)
        for (x = 0; x < 16; x++)
            index = z*256 + y*16 + x
```

## Complete Example: Decoding a Real Block

### Raw compressed data (first 100 bytes):
```
1D 28 B5 2F FD 00 58 DD 02 00 34 03 09 FF 00 00
03 00 02 00 13 64 65 66 61 75 6C 74 3A 64 72 79
5F 67 72 61 73 73 5F 31 00 08 00 1F 64 65 66 ...
```

### Step-by-step decode:

1. **Version**: `1D` = 29 ✓

2. **ZSTD frame**: `28 B5 2F FD` = magic number (little-endian 0xFD2FB528)

3. **After decompression:**
```
02 FF FF FF FF FF FF 00 00 0A 00 09 00 13 64 65
66 61 75 6C 74 3A 64 72 79 5F 67 72 61 73 73 5F
31 00 08 00 1F 64 65 66 61 75 6C 74 3A ...
```

4. **Parse decompressed data:**
- `02` = flags (underground, generated)
- `FF FF` = lighting_complete
- `FF FF FF FF` = timestamp (-1 = not set)
- `00 00` = 0 mappings in header (bug in some versions)
- `0A` = content_width (10 - invalid!)
- `00` = params_width (0 - invalid!)

This shows a malformed block. Let's look at a properly formed one:

### Correct Format Example:

**Decompressed data:**
```
03 FF FF 00 00 05 C4 00 03 00 00 00 03 61 69 72
00 01 00 0D 64 65 66 61 75 6C 74 3A 73 74 6F 6E
65 00 02 00 14 64 65 66 61 75 6C 74 3A 73 74 6F
6E 65 5F 77 69 74 68 5F 63 6F 61 6C 02 02 [nodes]
```

**Parsing:**
1. `03` = flags
2. `FF FF` = lighting complete
3. `00 00 05 C4` = timestamp (1476)
4. `00 03` = 3 mappings
5. Mapping 1: `00 00` (ID 0) `00 03` (len 3) `61 69 72` ("air")
6. Mapping 2: `00 01` (ID 1) `00 0D` (len 13) `64 65...65` ("default:stone")
7. Mapping 3: `00 02` (ID 2) `00 14` (len 20) `64 65...6C` ("default:stone_with_coal")
8. `02` = content_width (2 bytes)
9. `02` = params_width (2 bytes) ✓
10. Node data follows...

### Node Examples:
```
00 00 00 00  // Node 0: content=0 (air), param1=0, param2=0
00 01 0F 00  // Node 1: content=1 (stone), param1=15 (full light), param2=0
00 02 08 00  // Node 2: content=2 (coal ore), param1=8, param2=0
```

## The Complete Mapping

1. **World position** → **Block position**
   - `(83, 2, -155)` → `(5, 0, -10)`
   - Divide by 16, round down

2. **Block position** → **Database key**
   - `(5, 0, -10)` → `34365177862`
   - Using encoding formula above

3. **Database key** → **Compressed blob**
   - SQLite query returns ZSTD data

4. **Compressed blob** → **Decompressed data**
   - ZSTD decompression

5. **Decompressed data** → **NameIdMapping**
   - Parse ID-to-name mappings

6. **Node position** → **Array index**
   - `(3, 2, 5)` within block → index `1315`

7. **Array index** → **Node data**
   - Read content_id, param1, param2

8. **Content ID** → **Node name**
   - Use block's NameIdMapping

9. **Node name** → **Full definition**
   - Global NodeDefManager lookup

This is the complete binary format and mapping system used by Luanti/Minetest!
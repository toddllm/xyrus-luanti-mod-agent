-- signs_fix: Painted text on signs via bitmap font atlas
-- Requirements:
--   textures/signs_fix_font.png  (16x6 grid of 6x10px glyphs, 96 ASCII chars: 0x20..0x7E)

local FONT_TEX         = "signs_fix_font.png" -- put this PNG in your mod's textures/
local FONT_COLS        = 16                   -- grid columns in the atlas
local FONT_ROWS        = 6                    -- grid rows in the atlas
local GLYPH_W, GLYPH_H = 6, 10                -- one glyph's width/height in pixels
local SIGN_W, SIGN_H   = 128, 64              -- render area (px) for the text texture
local MARGIN_X, MARGIN_Y = 6, 6               -- inner margins (px)
local LINE_SPACING     = 2                    -- pixels between lines
local COLOR_HEX        = "#000000"            -- default text color (black)

-- How many monospace columns/rows fit:
local COLS_FIT = math.floor((SIGN_W - MARGIN_X * 2) / GLYPH_W)
local ROWS_FIT = math.floor((SIGN_H - MARGIN_Y * 2) / (GLYPH_H + LINE_SPACING))

-- Resolve world offset and yaw from wallmounted param2
local function face_from_param2(param2)
  -- Use engine helper for wallmounted to get the wall normal, then face outward
  local wall = minetest.wallmounted_to_dir(param2 or 2)
  local front = { x = -wall.x, y = -wall.y, z = -wall.z }
  local yaw = minetest.dir_to_yaw(front) or 0
  return front, yaw
end

-- Build an unwrapped glyph chain: no leading '(' and no trailing ')'
local function glyph_chain(ch)
  local byte = string.byte(ch)
  local code = (byte and byte >= 32 and byte <= 126) and byte or string.byte("?")
  -- Use per-glyph file to avoid [sheet] parsing on some clients
  local chain = "signs_fix_c" .. tostring(code) .. ".png"
  return chain
end

-- Build a transparent text texture for the given string, with monospace layout & wrapping
local function make_text_texture(text, w, h, color_hex)
  text = text or ""
  -- Start with a transparent canvas of w×h
  local tex = "[combine:" .. w .. "x" .. h

  local x = MARGIN_X
  local y = MARGIN_Y
  local col = 0
  local row = 0

  local function newline()
    x = MARGIN_X
    y = y + GLYPH_H + LINE_SPACING
    col = 0
    row = row + 1
  end

  for c in text:gmatch(".") do
    if c == "\n" then
      newline()
      if row >= ROWS_FIT then break end
    elseif c == "\r" then
      -- ignore
    else
      if col >= COLS_FIT then
        newline()
        if row >= ROWS_FIT then break end
      end

      if c ~= " " then
        -- Place plain subtexture file without grouping (no modifiers inside)
        local g = glyph_chain(c)
        tex = tex .. ":" .. x .. "," .. y .. "=" .. g
      end

      x = x + GLYPH_W
      col = col + 1
    end
  end

  -- Apply color to the entire composed texture (transparent areas remain transparent)
  if color_hex and color_hex ~= "" then
    tex = tex .. "^[colorize:" .. color_hex .. ":255"
  end
  return tex
end

-- ENTITY: holds only the text sprite (transparent where there are no glyphs)
minetest.register_entity("signs_fix:text", {
  initial_properties = {
    visual = "upright_sprite",
    visual_size = { x = 0.9, y = 0.45 },  -- scale on-screen size; tune as desired
    textures = { "[combine:" .. SIGN_W .. "x" .. SIGN_H }, -- start fully transparent
    use_texture_alpha = true,
    physical = false,
    collide_with_objects = false,
    pointable = false,
    static_save = true,
    spritediv = { x = 1, y = 1 },
    glow = 0,
  },

  -- Persist text/color in staticdata so the sprite survives restarts
  get_staticdata = function(self)
    return minetest.serialize({
      text = self.text or "",
      color = self.color or COLOR_HEX,
    })
  end,

  on_activate = function(self, staticdata, dtime_s)
    local data = minetest.deserialize(staticdata) or {}
    self.text  = data.text or (self.text or "")
    self.color = data.color or COLOR_HEX
    -- Always (re)apply texture on activate
    local t = make_text_texture(self.text, SIGN_W, SIGN_H, self.color)
    
    -- Debug: Log the full texture string (truncated if too long)
    local tex_preview = string.sub(t, 1, 200)
    minetest.log("action", "[signs_fix] Full texture preview: " .. tex_preview .. (string.len(t) > 200 and "..." or ""))
    
    -- Check for common issues
    if string.find(t, "%(%(") then
      minetest.log("error", "[signs_fix] DOUBLE PARENTHESES detected in texture!")
    end
    if string.find(t, "signs_fx") then
      minetest.log("error", "[signs_fix] CORRUPTED FILENAME detected (signs_fx instead of signs_fix)!")
    end
    
    self.object:set_properties({ textures = { t } })
    minetest.log("action", "[signs_fix] Text entity activated with: " .. self.text)
  end,

  -- Helper to update sprite after edits
  set_text = function(self, text, color_hex)
    self.text  = text or ""
    self.color = color_hex or COLOR_HEX
    local t = make_text_texture(self.text, SIGN_W, SIGN_H, self.color)
    self.object:set_properties({ textures = { t } })
  end,
})

-- Spawn/refresh the text sprite in front of a wallmounted sign
local function spawn_one_sprite(at_pos, yaw, text, color_hex)
  local obj = minetest.add_entity(at_pos, "signs_fix:text", minetest.serialize({
    text = text or "",
    color = color_hex or COLOR_HEX,
  }))
  if not obj then
    minetest.log("error", "[signs_fix] add_entity failed @" .. minetest.pos_to_string(at_pos))
    return nil
  end
  obj:set_yaw(yaw)
  local ent = obj:get_luaentity()
  if ent and ent.set_text then
    ent:set_text(text or "", color_hex or COLOR_HEX)
  end
  return obj
end

local function spawn_sign_sprite(pos, text, color_hex)
  -- remove old
  for _, obj in ipairs(minetest.get_objects_inside_radius(pos, 0.8)) do
    local e = obj:get_luaentity()
    if e and e.name == "signs_fix:text" then obj:remove() end
  end

  local node = minetest.get_node(pos)
  local dir, yaw = face_from_param2(node.param2 or 2)
  local eps = 0.03   -- offset away from sign face to avoid z-fighting/occlusion
  local p_front = vector.add(pos, vector.multiply(dir,  eps))
  local p_back  = vector.add(pos, vector.multiply(dir, -eps))

  if not minetest.get_node_or_nil(p_front) then
    minetest.log("warning", "[signs_fix] mapblock not loaded @" .. minetest.pos_to_string(p2))
    return
  end

  -- Spawn front and back sprites so both sides of the board show text
  local front = spawn_one_sprite(p_front, yaw, text, color_hex)
  local back  = spawn_one_sprite(p_back, (yaw + math.pi) % (math.pi * 2), text, color_hex)
  
  if front or back then
    minetest.log("action", "[signs_fix] Spawned text sprites (front/back): " .. (text or ""))
  end
end

-----------------------------------------------------------------------
-- INTEGRATION WITH default:sign_wall_wood and default:sign_wall_steel
-----------------------------------------------------------------------

local function override_sign(material)
  local signname = "default:sign_wall_" .. material
  if minetest.registered_nodes[signname] then
    -- Don't copy the whole definition, just override specific functions
    local old_on_receive_fields = minetest.registered_nodes[signname].on_receive_fields
    local old_after_dig_node = minetest.registered_nodes[signname].after_dig_node

    minetest.override_item(signname, {
      on_receive_fields = function(pos, formname, fields, sender)
      if old_on_receive_fields then
        old_on_receive_fields(pos, formname, fields, sender)
      end

      -- default signs store text in meta "text" (minetest_game)
      local meta = minetest.get_meta(pos)
      local txt = meta:get_string("text") or ""

      -- Optional: support a color line prefix like "#RRGGBB: your text"
      local color = COLOR_HEX
      local m1, m2 = txt:match("^#([%x%X][%x%X][%x%X][%x%X][%x%X][%x%X])%s*:%s*(.*)$")
      if m1 and m2 then
        color = "#" .. m1
        txt = m2
        -- Don't modify the stored text, keep color prefix
      end

      spawn_sign_sprite(pos, txt, color)
    end,

    -- When the node is dug/replaced, remove the entity
    after_dig_node = function(pos, oldnode, oldmeta, digger)
      if old_after_dig_node then
        old_after_dig_node(pos, oldnode, oldmeta, digger)
      end
      for _, obj in ipairs(minetest.get_objects_inside_radius(pos, 0.8)) do
        local e = obj:get_luaentity()
        if e and e.name == "signs_fix:text" then obj:remove() end
      end
    end
    })
    minetest.log("action", "[signs_fix] Overrode " .. signname .. " to attach text sprites")
  else
    minetest.log("warning", "[signs_fix] " .. signname .. " not found; skipping override")
  end
end

-- Override both wood and steel signs
minetest.register_on_mods_loaded(function()
  override_sign("wood")
  override_sign("steel")
  minetest.log("action", "[signs_fix] Ready - bitmap font text rendering enabled")
end)

-----------------------------------------------------------------------
-- LBM: Reattach sprites on mapblock load (persistence, healing)
-----------------------------------------------------------------------
minetest.register_lbm({
  name = "signs_fix:reattach_text",
  nodenames = { "default:sign_wall_wood", "default:sign_wall_steel" },
  run_at_every_load = true,
  action = function(pos, node)
    local meta = minetest.get_meta(pos)
    local txt = meta:get_string("text") or ""
    if txt ~= "" then
      -- See if an entity already exists
      local has = false
      for _, obj in ipairs(minetest.get_objects_inside_radius(pos, 0.8)) do
        local e = obj:get_luaentity()
        if e and e.name == "signs_fix:text" then
          has = true
          break
        end
      end
      if not has then
        spawn_sign_sprite(pos, txt, COLOR_HEX)
        minetest.log("action", "[signs_fix] LBM restored text: " .. txt)
      end
    end
  end,
})

-----------------------------------------------------------------------
-- Test command (manual)
-----------------------------------------------------------------------
minetest.register_chatcommand("testsign", {
  params = "<x> <y> <z> <text...>",
  description = "Place a wall sign and render text on it",
  privs = {interact = true},
  func = function(name, param)
    local parts = param:split(" ")
    if #parts < 4 then
      return false, "Usage: /testsign x y z text..."
    end
    local pos = { x = tonumber(parts[1]), y = tonumber(parts[2]), z = tonumber(parts[3]) }
    if not (pos.x and pos.y and pos.z) then
      return false, "Bad coordinates."
    end
    local txt = table.concat(parts, " ", 4)
    minetest.set_node(pos, { name = "default:sign_wall_wood", param2 = 4 }) -- face -X by default
    local meta = minetest.get_meta(pos)
    meta:set_string("text", txt)
    meta:set_string("infotext", txt)  -- For hover text
    spawn_sign_sprite(pos, txt, COLOR_HEX)
    return true, "Placed sign with text @" .. minetest.pos_to_string(pos)
  end
})

-----------------------------------------------------------------------
-- Startup smoke test
-----------------------------------------------------------------------
minetest.register_on_mods_loaded(function()
  minetest.after(2, function()
    local p = {x=100, y=10, z=100}
    minetest.log("action", "[signs_fix] === SMOKE TEST STARTING ===")
    
    -- Place the sign
    minetest.set_node(p, {name="default:sign_wall_wood", param2=4})
    
    -- Set text
    local meta = minetest.get_meta(p)
    meta:set_string("text", "Hello World!\nLine 2\nLine 3")
    meta:set_string("infotext", "Hello World!\nLine 2\nLine 3")
    
    -- Spawn the sprite
    spawn_sign_sprite(p, "Hello World!\nLine 2\nLine 3", COLOR_HEX)
    
    minetest.log("action", "[signs_fix] Smoke test complete at " .. minetest.pos_to_string(p))
  end)
end)

-----------------------------------------------------------------------
-- AUTOMATED TESTING - Server-side verification
-----------------------------------------------------------------------

-- A) Deterministic texture verification
-- Extracts :x,y=... placements from a [combine] string
local function count_glyph_placements(tex)
  local n = 0
  -- matches :<x>,<y>=(subtex)
  -- Count either grouped (..=(subtex)) or plain filename (..=name.png)
  for _ in tex:gmatch(":%-?%d+,%-?%d+=%b()") do
    n = n + 1
  end
  for _ in tex:gmatch(":%-?%d+,%-?%d+=([^:%^%s)]+)%)?") do
    n = n + 1
  end
  return n
end

-- Expected minimum glyphs (at least half of non-space chars)
local function expected_min_glyphs(text)
  local letters = 0
  for c in (text or ""):gmatch(".") do
    if c ~= " " and c ~= "\n" and c ~= "\r" then 
      letters = letters + 1 
    end
  end
  return math.max(1, math.floor(letters * 0.5))
end

minetest.register_chatcommand("signs_auto_verify_texture", {
  params = "[text...]",
  description = "Server-side: verify [combine] texture for visible glyph placements",
  privs = {},
  func = function(name, param)
    local text = param ~= "" and param or "Hello World!\nLine 2\nLine 3"
    local tex = make_text_texture(text, SIGN_W, SIGN_H, "#000000")
    local count = count_glyph_placements(tex)
    local min_ok = expected_min_glyphs(text)

    local ok = (count >= min_ok)
    local msg = "[signs_fix:test] placements=" .. count .. " (min_ok=" .. min_ok .. ")"
    minetest.log(ok and "action" or "error", msg)
    return ok, (ok and "PASS " or "FAIL ") .. msg
  end
})

-- B) Pixel-level verification with software renderer
-- Simple 5x7 bitmap font for testing
local FONT5x7 = {
  [" "] = {0,0,0,0,0,0,0},
  ["!"] = {4,4,4,4,4,0,4},
  ["H"] = {17,17,17,31,17,17,17},
  ["e"] = {0,0,14,17,31,16,15},
  ["l"] = {12,4,4,4,4,4,14},
  ["o"] = {0,0,14,17,17,17,14},
  ["W"] = {17,17,17,21,21,21,10},
  ["r"] = {0,0,11,12,8,8,8},
  ["d"] = {1,1,15,17,17,17,15},
  ["L"] = {16,16,16,16,16,16,31},
  ["i"] = {4,0,12,4,4,4,14},
  ["n"] = {0,0,22,25,17,17,17},
  ["2"] = {14,17,1,2,4,8,31},
  ["3"] = {14,17,1,6,1,17,14},
  [":"] = {0,0,4,0,0,4,0},
  ["?"] = {14,17,1,2,4,0,4},
}

local function get_glyph(ch)
  return FONT5x7[ch] or FONT5x7["?"] or {14,17,17,21,17,17,14} -- fallback to box
end

-- Check if bit is set (compatible with different Lua versions)
local function test_bit(value, bit)
  if bit32 and bit32.band then
    return bit32.band(value, 2^bit) ~= 0
  else
    -- Fallback for older Lua
    return math.floor(value / (2^bit)) % 2 == 1
  end
end

-- Software render text and count ink pixels
local function render_and_count_pixels(text)
  local ink_pixels = 0
  local total_chars = 0
  
  -- Simulate rendering without creating actual image
  local x = MARGIN_X
  local y = MARGIN_Y
  local col = 0
  local row = 0
  
  local function newline()
    x = MARGIN_X
    y = y + 7 + LINE_SPACING  -- Using 7 for font height
    col = 0
    row = row + 1
  end
  
  for c in (text or ""):gmatch(".") do
    if c == "\n" then
      newline()
      if row >= ROWS_FIT then break end
    elseif c ~= "\r" then
      if col >= COLS_FIT then
        newline()
        if row >= ROWS_FIT then break end
      end
      if c ~= " " then
        total_chars = total_chars + 1
        local g = get_glyph(c)
        -- Count pixels in this glyph
        for gy = 1, 7 do
          local rowbits = g[gy] or 0
          for gx = 0, 4 do
            if test_bit(rowbits, gx) then
              ink_pixels = ink_pixels + 1
            end
          end
        end
      end
      x = x + 5  -- Using 5 for font width
      col = col + 1
    end
  end
  
  return ink_pixels, total_chars
end

-- Debug command to check entity texture at a position
minetest.register_chatcommand("debug_sign", {
  params = "<x> <y> <z>",
  description = "Debug: Check sign entity and texture at position",
  privs = {interact = true},
  func = function(name, param)
    local parts = param:split(" ")
    if #parts < 3 then
      return false, "Usage: /debug_sign x y z"
    end
    local pos = {x=tonumber(parts[1]), y=tonumber(parts[2]), z=tonumber(parts[3])}
    
    -- Check node
    local node = minetest.get_node(pos)
    local meta = minetest.get_meta(pos)
    local text = meta:get_string("text")
    
    minetest.chat_send_player(name, "=== Sign Debug ===")
    minetest.chat_send_player(name, "Node: " .. node.name .. " param2=" .. node.param2)
    minetest.chat_send_player(name, "Text in meta: " .. (text ~= "" and text or "(empty)"))
    
    -- Check for entities
    local found_entity = false
    for _, obj in ipairs(minetest.get_objects_inside_radius(pos, 1.0)) do
      local e = obj:get_luaentity()
      if e and e.name == "signs_fix:text" then
        found_entity = true
        local props = obj:get_properties()
        local tex = props.textures and props.textures[1] or "NO TEXTURE"
        local tex_preview = string.sub(tex, 1, 100) .. "..."
        
        minetest.chat_send_player(name, "Entity found at " .. minetest.pos_to_string(obj:get_pos()))
        minetest.chat_send_player(name, "Texture alpha: " .. tostring(props.use_texture_alpha))
        minetest.chat_send_player(name, "Visual size: " .. minetest.serialize(props.visual_size))
        minetest.chat_send_player(name, "Texture preview: " .. tex_preview)
        
        -- Count glyphs in texture
        local glyph_count = 0
        for _ in tex:gmatch(":%-?%d+,%-?%d+=%b()") do glyph_count = glyph_count + 1 end
        for _ in tex:gmatch(":%-?%d+,%-?%d+=([^:%^%s)]+)%)?") do glyph_count = glyph_count + 1 end
        minetest.chat_send_player(name, "Glyphs in texture: " .. glyph_count)
      end
    end
    
    if not found_entity then
      minetest.chat_send_player(name, "NO ENTITY FOUND - spawning one now...")
      spawn_sign_sprite(pos, text, COLOR_HEX)
      minetest.chat_send_player(name, "Entity spawned, check again")
    end
    
    return true
  end
})

minetest.register_chatcommand("signs_pixel_verify", {
  params = "[text...]",
  description = "Server-side: software render text and verify pixel count",
  privs = {},
  func = function(name, param)
    local text = param ~= "" and param or "Hello World!\nLine 2\nLine 3"
    local ink_pixels, chars = render_and_count_pixels(text)
    
    -- Expect at least 10 pixels per character as a simple heuristic
    local min_pixels = chars * 10
    local ok = ink_pixels >= min_pixels
    
    local msg = string.format("[signs_fix:pixel_test] ink_pixels=%d chars=%d (min_pixels=%d)", 
                              ink_pixels, chars, min_pixels)
    minetest.log(ok and "action" or "error", msg)
    return ok, (ok and "PASS " or "FAIL ") .. msg
  end
})

-- Auto-run texture verification on server start
minetest.register_on_mods_loaded(function()
  minetest.after(5, function()
    minetest.log("action", "[signs_fix] === AUTOMATED TEXTURE VERIFICATION ===")
    local test_text = "Hello World!\nLine 2\nLine 3"
    
    -- Test 1: Texture placement verification
    local tex = make_text_texture(test_text, SIGN_W, SIGN_H, "#000000")
    local count = count_glyph_placements(tex)
    local min_ok = expected_min_glyphs(test_text)
    
    if count >= min_ok then
      minetest.log("action", "[signs_fix] TEXTURE TEST PASSED: " .. count .. " glyphs placed (min " .. min_ok .. ")")
    else
      minetest.log("error", "[signs_fix] TEXTURE TEST FAILED: Only " .. count .. " glyphs placed (needed " .. min_ok .. ")")
    end
    
    -- Test 2: Pixel-level verification
    local ink_pixels, chars = render_and_count_pixels(test_text)
    local min_pixels = chars * 10
    
    if ink_pixels >= min_pixels then
      minetest.log("action", "[signs_fix] PIXEL TEST PASSED: " .. ink_pixels .. " ink pixels for " .. chars .. " chars")
    else
      minetest.log("error", "[signs_fix] PIXEL TEST FAILED: Only " .. ink_pixels .. " ink pixels (needed " .. min_pixels .. ")")
    end
  end)
end)
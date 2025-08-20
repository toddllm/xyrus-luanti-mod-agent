-- Sara NPC mod
-- Robust spawn mechanics with fallback visuals and clear logging

local SARA_ENTITY_NAME = "sara:sara"

-- Register entity with a guaranteed-visible sprite and nametag, regardless of meshes
minetest.register_entity(SARA_ENTITY_NAME, {
  initial_properties = {
    physical = true,
    collisionbox = {-0.35, -1.0, -0.35, 0.35, 0.8, 0.35},
    makes_footstep_sound = false,
    visual = "sprite",
    textures = {"default_stone.png"}, -- always available in default
    visual_size = {x = 4, y = 4},
    nametag = "Sara",
    nametag_bgcolor = {a = 128, r = 10, g = 10, b = 10},
    pointable = true,
  },

  on_activate = function(self)
    minetest.log("action", "[sara] entity activated")
  end,

  on_rightclick = function(self, clicker)
    if clicker and clicker:is_player() then
      minetest.chat_send_player(clicker:get_player_name(),
        "I want you to make a Food Factory: please make a furnace and a chest, serve customers, and hire workers!")
    end
    minetest.log("action", "[sara] on_rightclick")
  end,

  on_punch = function(self, puncher)
    if puncher and puncher:is_player() then
      minetest.chat_send_player(puncher:get_player_name(),
        "Don't punch, talk by using right click!")
    end
    minetest.log("action", "[sara] on_punch")
  end,
})

-- Placeable spawn node for convenience
minetest.register_node("sara:spawn_node", {
  description = "Sara Spawn",
  tiles = {"default_dirt.png"},
  groups = {cracky = 3, oddly_breakable_by_hand = 3, not_in_creative_inventory = 0},
  on_construct = function(pos)
    local above = vector.add(pos, {x = 0, y = 1, z = 0})
    minetest.add_entity(above, SARA_ENTITY_NAME)
    minetest.set_node(pos, {name = "air"})
    minetest.log("action", "[sara] spawn_node placed; entity spawned at " .. minetest.pos_to_string(above))
  end,
})

-- Chat command to spawn Sara at player position
minetest.register_chatcommand("spawn_sara", {
  params = "",
  description = "Spawn Sara at your position",
  privs = {},
  func = function(name)
    local player = minetest.get_player_by_name(name)
    if not player then return false, "Player not found" end
    local pos = vector.round(player:get_pos())
    local above = {x = pos.x, y = pos.y + 1, z = pos.z}
    minetest.add_entity(above, SARA_ENTITY_NAME)
    minetest.log("action", "[sara] /spawn_sara by " .. name .. " at " .. minetest.pos_to_string(above))
    return true, "Sara spawned."
  end,
})

-- Remove any old auto-spawn hooks if present; do not auto-spawn on load

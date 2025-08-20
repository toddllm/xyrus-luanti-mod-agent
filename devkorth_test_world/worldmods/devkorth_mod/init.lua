-- The Legend of Devkorth
-- An omnipotent entity that transcends reality itself

local modname = minetest.get_current_modname()
local modpath = minetest.get_modpath(modname)

-- Global namespace
devkorth = {}

-- Load components
dofile(modpath .. "/api.lua")
dofile(modpath .. "/entity.lua")
dofile(modpath .. "/items.lua")
dofile(modpath .. "/shrine.lua")
dofile(modpath .. "/powers.lua")

minetest.log("action", "[Devkorth] The Legend begins...")
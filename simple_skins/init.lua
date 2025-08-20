
-- Simple Skins mod for minetest
-- Adds a simple skin selector to the inventory.
-- Released by TenPlus1 and based on Zeg9's code under MIT license

-- Load support for translation.

local S = core.get_translator("simple_skins")

-- global and settings

skins = {
	skins = {}, list = {}, meta = {}, formspec = {},
	modpath = core.get_modpath("simple_skins"),
	invplus = core.get_modpath("inventory_plus"),
	unified_inventory = core.get_modpath("unified_inventory"),
	default_skin_tab = false,
	sfinv = core.get_modpath("sfinv"),
	transparant_list = false,
	id = 1,
	file = core.get_worldpath() .. "/simple_skins.mt",
	preview = core.settings:get_bool("simple_skins_preview"),
	skin_limit = tonumber(core.settings:get("simple_skins_limit")) or 300
}

-- check and use specific inventory

if skins.unified_inventory then
	skins.transparant_list = true
	dofile(skins.modpath .. "/unified_inventory.lua")

elseif skins.invplus then
	skins.transparant_list = true
	dofile(skins.modpath .. "/inventory_plus.lua")

elseif skins.sfinv then
	skins.default_skin_tab = not skins.invplus and not skins.unified_inventory
	dofile(skins.modpath .. "/sfinv.lua")
end

-- load skin list and metadata

local f, data, skin = 1

while skins.id <= skins.skin_limit do

	skin = "character_" .. skins.id

	-- does skin file exist ?
	f = io.open(skins.modpath .. "/textures/" .. skin .. ".png")

	-- escape loop if not found and remove last entry
	if not f then
		skins.list[skins.id] = nil
		skins.id = skins.id - 1
		break
	end

	f:close()

	table.insert(skins.list, skin)

	-- does metadata exist for that skin file ?
	f = io.open(skins.modpath .. "/meta/" .. skin .. ".txt")

	if f then
		data = core.deserialize("return {" .. f:read("*all") .. "}")
		f:close()
	end

	-- add metadata to list
	skins.meta[skin] = {
		name = data and data.name and data.name:gsub("[%p%c]", "") or "",
		author = data and data.author and data.author:gsub("[%p%c]", "") or ""
	}

	skins.id = skins.id + 1
end

-- load player skins file for backwards compatibility

local input = io.open(skins.file, "r")
local data = nil

if input then
	data = input:read("*all")
	io.close(input)
end

if data and data ~= "" then

	local lines = string.split(data, "\n")

	for _, line in pairs(lines) do
		data = string.split(line, " ", 2)
		skins.skins[data[1]] = data[2]
	end
end

-- check for minetest 5.4 compatibility

local is_54 = core.has_feature("direct_velocity_on_players")

-- create formspec for skin selection page

skins.formspec.main = function(name)

	local formspec = "label[.5,2;" .. S("Select Player Skin:") .. "]"
		.. "textlist[.5,2.5;6.8,6;skins_set;"

	local meta
	local selected = 1

	for i = 1, #skins.list do

		formspec = formspec .. skins.meta[ skins.list[i] ].name

		if skins.skins[name] == skins.list[i] then
			selected = i
			meta = skins.meta[ skins.skins[name] ]
		end

		if i < #skins.list then
			formspec = formspec ..","
		end
	end

	if skins.transparant_list then
		formspec = formspec .. ";" .. selected .. ";true]"
	else
		formspec = formspec .. ";" .. selected .. ";false]"
	end

	if meta then

		if meta.name then
			formspec = formspec .. "label[2,.5;" .. S("Name: ") .. meta.name .. "]"
		end

		if meta.author then
			formspec = formspec .. "label[2,1;" .. S("Author: ") .. meta.author .. "]"
		end
	end

	-- if preview enabled then add player model to formspec (5.4dev only)
	if skins.preview == true and is_54 then

		formspec = formspec .. "model[6,-0.2;1.5,3;player;character.b3d;"
			.. skins.skins[name] .. ".png;0,180;false;true]"
	end

	return formspec
end

-- update player skin

skins.update_player_skin = function(player)

	if not player then return end

	local name = player:get_player_name()

	if core.get_modpath("player_api") then
		player_api.set_textures(player, {skins.skins[name] .. ".png"})
	else
		default.player_set_textures(player, {skins.skins[name] .. ".png"})
	end
end

-- selection event

skins.event_CHG = function(event, player)

	local name = player:get_player_name()
	local index = math.min(event.index, skins.id)

	if not skins.list[index] then
		return -- Do not update wrong skin number
	end

	skins.skins[name] = skins.list[index]

	skins.update_player_skin(player)

	local meta = player:get_meta()

	meta:set_string("simple_skins:skin", skins.skins[name])
end

-- load player skin on join

core.register_on_joinplayer(function(player)

	local name = player:get_player_name() ; if not name then return end
	local meta = player:get_meta()
	local skin = meta:get_string("simple_skins:skin")

	-- do we already have a skin in player attributes?
	if skin and skin ~= "" then

		skins.skins[name] = skin

	-- otherwise use skin from simple_skins.mt file if loaded or default if not set
	elseif not skins.skins[name] then
		skins.skins[name] = "character"
	end

	skins.update_player_skin(player)
end)

-- admin command to set player skin (usually for custom skins)

core.register_chatcommand("setskin", {
	params = "<player> <skin number>",
	description = S("Admin command to set player skin"),
	privs = {server = true},
	func = function(name, param)

		local playername, skin = string.match(param, "([^ ]+) (-?%d+)")

		if not playername or not skin then
			return false, S("** Insufficient or wrong parameters")
		end

		local player = core.get_player_by_name(playername)

		if not player then
			return false, S("** Player @1 not online!", playername)
		end

		-- this check is only used when custom skins aren't in use
--		if not skins.list[tonumber(skin)] then
--			return false, S("** Invalid skin number (max value is @1)", id)
--		end

		skins.skins[playername] = "character_" .. tonumber(skin)

		skins.update_player_skin(player)

		local meta = player:get_meta()

		meta:set_string("simple_skins:skin", skins.skins[playername])

		core.chat_send_player(playername,
				S("Your skin has been set to") .. " character_" .. skin)

		return true, "** " .. playername .. S("'s skin set to")
				.. " character_" .. skin .. ".png"
	end,
})


print ("[MOD] Simple Skins loaded")

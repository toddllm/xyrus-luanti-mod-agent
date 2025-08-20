 --
-- petz
-- License:GPLv3
--

local modname = "petz"
local modpath = minetest.get_modpath(modname)

-- internationalization boilerplate
local S = minetest.get_translator(minetest.get_current_modname())

--
--The Petz
--

petz = {}

--
--Settings
--
petz.settings = {}
petz.settings.mesh = nil
petz.settings.visual_size = {}
petz.settings.rotate = 0

assert(loadfile(modpath .. "/settings.lua"))(modpath) --Load the settings

assert(loadfile(modpath .. "/api/api.lua"))(modpath, S)
assert(loadfile(modpath .. "/brains/brains.lua"))(modpath)
assert(loadfile(modpath .. "/misc/misc.lua"))(modpath, S)
assert(loadfile(modpath .. "/server/cron.lua"))(modname)

petz.file_exists = function(name)
   local f = io.open(name,"r")
   if f ~= nil then
		io.close(f)
		return true
	else
		return false
	end
end

if petz.settings["remove_list"] then
	for i = 1, #petz.settings["remove_list"] do
		local file_name = modpath .. "/petz/"..petz.settings["remove_list"][i].."_mobkit"..".lua"
		if petz.file_exists(file_name) then
			assert(loadfile(file_name))(S)
		end
		--Override the petz_list
		for j = 1, #petz.settings["petz_list"] do --load all the petz.lua files
			if petz.settings["remove_list"][i] == petz.settings["petz_list"][j] then
				table.remove(petz.settings["petz_list"], j)
				--kitz.remove_table_by_key(petz.settings["petz_list"], j)
			end
		end
	end
end

-- Pickup/carry functionality
function petz.toggle_pickup(self, clicker)
    if not self.is_pickupable or not clicker:is_player() then return false end
    
    -- Only allow pickup with empty hand
    local item = clicker:get_wielded_item()
    if not item:is_empty() then
        return false -- let normal rightclick handle items
    end

    local name = clicker:get_player_name()
    -- require ownership if the mob can be owned
    if self.owner and self.owner ~= name then
        minetest.chat_send_player(name, S("That's not your pet!"))
        return true -- consume the click
    end

    if self.attached then
        -- DROP
        self.object:set_detach()
        self.object:set_properties({physical = true})
        -- pop the fox right in front of the player
        local dir = clicker:get_look_dir()
        local pos = vector.add(clicker:get_pos(), vector.multiply(dir, 1))
        pos.y = pos.y + 0.5
        self.object:set_pos(pos)
        self.attached = nil
        self._pickup_owner = nil
        -- Resume AI
        if self.logic then
            self.logic(self, nil)
        end
    else
        -- PICK UP
        self.object:set_velocity({x=0,y=0,z=0})
        self.object:set_properties({physical = false})
        -- attach to root so it hovers in front of chest
        self.object:set_attach(clicker, "", {x=0, y=6, z=4}, {x=0, y=90, z=0})
        -- pause behaviour tree while carried (kitz)
        kitz.clear_queue_high(self)
        self.attached = true
        self._pickup_owner = name
    end
    return true -- we handled the click
end

-- Safety cleanup on player logout
minetest.register_on_leaveplayer(function(player)
    local name = player:get_player_name()
    for _, obj in ipairs(minetest.get_objects_inside_radius(player:get_pos(), 16)) do
        local lua = obj:get_luaentity()
        if lua and lua._pickup_owner == name then
            obj:set_detach()
            obj:set_properties({physical = true})
            lua.attached = nil
            lua._pickup_owner = nil
        end
    end
end)

for i = 1, #petz.settings["petz_list"] do --load all the petz.lua files
	local file_name = modpath .. "/petz/"..petz.settings["petz_list"][i].."_mobkit"..".lua"
	if petz.file_exists(file_name) then
		assert(loadfile(file_name))(S)
	end
end

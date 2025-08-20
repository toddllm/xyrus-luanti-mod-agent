local S = ...

local lycanthropy = {}
lycanthropy.werewolf = {}
lycanthropy.werewolf.collisionbox = {-0.3, 0.0, -0.3, 0.3, 1.7, 0.3}
lycanthropy.werewolf.animation_speed = 30
lycanthropy.werewolf.animations = {
	stand = {x = 0,   y = 79},
	lay = {x = 162, y = 166},
	walk = {x = 168, y = 187},
	mine = {x = 189, y = 198},
	walk_mine = {x = 200, y = 219},
	sit = {x = 81,  y = 160},
	-- compatibility w/ the emote mod
	wave = {x = 192, y = 196, override_local = true},
	point = {x = 196, y = 196, override_local = true},
	freeze = {x = 205, y = 205, override_local = true},
}
lycanthropy.werewolf.override_table = {
	speed = 1.5,
	jump = 1.5,
	gravity = 0.95,
    sneak = true,
	sneak_glitch = false,
	new_move = true,
}
lycanthropy.werewolf.textures = {
	"petz_werewolf_dark_gray.png",
	"petz_werewolf_gray.png",
	"petz_werewolf_brown.png",
	"petz_werewolf_black.png"
}
lycanthropy.clans = {
	{
		name = S("The Savage Stalkers"),
		texture = lycanthropy.werewolf.textures[1],
	},
	{
		name = S("The Bravehide Pride"),
		texture = lycanthropy.werewolf.textures[2]
	},
	{
		name = S("The Hidden Tails"),
		texture = lycanthropy.werewolf.textures[3],
	},
	{
		name = S("The Fierce Manes"),
		texture = lycanthropy.werewolf.textures[4],
	},
}
if minetest.get_modpath("3d_armor") then
	lycanthropy.werewolf.model = "3d_armor_werewolf.b3d"

	player_api.register_model(lycanthropy.werewolf.model, {
		animation_speed = lycanthropy.werewolf.animation_speed,
		textures = {
			lycanthropy.werewolf.textures[1],
			"3d_armor_trans.png",
			"3d_armor_trans.png",
		},
		animations = lycanthropy.werewolf.animations,
	})

	armor:register_on_update(function(player)
		if petz.is_werewolf(player) then
			petz.set_werewolf_appearance(player)
		end
	end)

else
	lycanthropy.werewolf.model = "petz_werewolf.b3d"

	player_api.register_model(lycanthropy.werewolf.model, {
		textures = {lycanthropy.werewolf.textures[1]},
		animation_speed = lycanthropy.werewolf.animation_speed,
		animations = lycanthropy.werewolf.animations,
		collisionbox = lycanthropy.werewolf.collisionbox ,
		stepheight = 0.6,
		eye_height = 1.47,
	})
end



local use_playerphysics = minetest.get_modpath("playerphysics")
local use_player_monoids = minetest.get_modpath("player_monoids")

---
--- Helper Functions
---

function petz.is_werewolf(player)
	if not minetest.is_player(player) then
		return false
	end
	local meta = player:get_meta()
	return meta:get_int("petz:werewolf") == 1
end

function petz.has_lycanthropy(player)
	if not minetest.is_player(player) then
		return false
	end
	local meta = player:get_meta()
	return meta:get_int("petz:lycanthropy") == 1
end

local hud_id_by_player_name = {}

function petz.show_werewolf_vignette(player)
	local player_name = player:get_player_name()
	local hud_id = hud_id_by_player_name[player_name]
	if hud_id then
		local hud_def = player:hud_get(hud_id)
		if hud_def and hud_def.name == "petz:werewolf_vignette" then
			-- already showing the vignette, do nothing
			return
		end
	end
	hud_id_by_player_name[player_name] = player:hud_add({
		name = "petz:werewolf_vignette",
		hud_elem_type = "image",
		text = "petz_werewolf_vignette.png",
		position = {x=0, y=0},
		scale = {x=-100, y=-100},
		alignment = {x=1, y=1},
		offset = {x=0, y=0}
	})
end

function petz.remove_werewolf_vignette(player)
	local player_name = player:get_player_name()
	local hud_id = hud_id_by_player_name[player_name]
	if hud_id then
		local hud_def = player:hud_get(hud_id)
		if hud_def and hud_def.name == "petz:werewolf_vignette" then
			player:hud_remove(hud_id)
		end
	end
	hud_id_by_player_name[player_name] = nil
end

---
--- Set, Unset & Reset Functions
---

petz.set_werewolf_physics = function(player)
	if use_playerphysics then
		playerphysics.add_physics_factor(player, "speed", "werewolf_speed", lycanthropy.werewolf.override_table.speed)
		playerphysics.add_physics_factor(player, "jump", "werewolf_jump", lycanthropy.werewolf.override_table.jump)
		playerphysics.add_physics_factor(player, "gravity", "werewolf_gravity", lycanthropy.werewolf.override_table.gravity)
	elseif use_player_monoids then
		player_monoids.speed:add_change(player, lycanthropy.werewolf.override_table.speed, "petz:physics")
		player_monoids.jump:add_change(player, lycanthropy.werewolf.override_table.jump, "petz:physics")
		player_monoids.gravity:add_change(player, lycanthropy.werewolf.override_table.gravity, "petz:physics")
	else
		local meta = player:get_meta()
		local override_table = player:get_physics_override()
		if override_table then
			meta:set_string("petz:old_override_table", minetest.serialize(override_table))
		end
		player:set_physics_override(lycanthropy.werewolf.override_table)
	end
end

petz.unset_werewolf_physics = function(player)
	if use_playerphysics then
		playerphysics.remove_physics_factor(player, "speed", "werewolf_speed")
		playerphysics.remove_physics_factor(player, "jump", "werewolf_jump")
		playerphysics.remove_physics_factor(player, "gravity", "werewolf_gravity")
	elseif use_player_monoids then
		player_monoids.speed:del_change(player, "petz:physics")
		player_monoids.jump:del_change(player, "petz:physics")
		player_monoids.gravity:del_change(player, "petz:physics")
	else
		local meta = player:get_meta()
		local override_table = meta:get("petz:old_override_table")
		if override_table then
			player:set_physics_override(minetest.deserialize(override_table))
		end
	end
end

petz.set_werewolf_appearance = function(player)
	local meta = player:get_meta()

	if not petz.is_werewolf(player) then
		local old_animation = player_api.get_animation(player)
		meta:set_string("petz:pre_werewolf_animation", minetest.serialize(old_animation))
	end

	player_api.set_model(player, lycanthropy.werewolf.model)
	local clan_idx = meta:get_int("petz:werewolf_clan_idx")
	local werewolf_texture = lycanthropy.werewolf.textures[clan_idx]

	if minetest.get_modpath("3d_armor") then
		local player_name = player:get_player_name()
		player_api.set_textures(player, {
			lycanthropy.werewolf.textures[clan_idx],
			armor.textures[player_name].armor,
			armor.textures[player_name].wielditem,
		})

	else
		player_api.set_textures(player, {werewolf_texture})
	end
end

petz.unset_werewolf_appearance = function(player)
	local meta = player:get_meta()
	local pre_werewolf_animation = minetest.deserialize(meta:get_string("petz:pre_werewolf_animation"))
	if pre_werewolf_animation then
		-- TODO: this still isn't perfect, but it gets rid of weird glitchy appearances due to mismatched models.
		-- it results in the player looking exactly like they did before they became a werewolf, until their next
		-- model update. however, they may momentarily appear to be wearing the wrong armor, or to be weilding
		-- the wrong item.

		meta:set_string("petz:pre_werewolf_animation", "")
		if pre_werewolf_animation.model then
			player_api.set_model(player, pre_werewolf_animation.model)
		end
		if pre_werewolf_animation.textures then
			player_api.set_textures(player, pre_werewolf_animation.textures)
		end
	else
		if minetest.get_modpath("3d_armor") then
			local player_name = player:get_player_name()
			player_api.set_model(player, "3d_armor_character.b3d")
			player_api.set_textures(player, {
				armor.textures[player_name].skin,
				armor.textures[player_name].armor,
				armor.textures[player_name].wielditem,
			})
		else
			player_api.set_model(player, "character.b3d")
			player_api.set_textures(player, {"character.png"})
		end
	end

end

petz.set_werewolf = function(player)
	if not petz.has_lycanthropy(player) then
		return
	end

	petz.show_werewolf_vignette(player)
	petz.set_werewolf_appearance(player)
	petz.set_werewolf_physics(player)

	local meta = player:get_meta()
	meta:set_int("petz:werewolf", 1)
end

petz.unset_werewolf = function(player)
	petz.remove_werewolf_vignette(player)
	petz.unset_werewolf_physics(player)
	petz.unset_werewolf_appearance(player)

	local meta = player:get_meta()
	meta:set_int("petz:werewolf", 0)
end

petz.set_lycanthropy = function(player)
	local meta = player:get_meta()
	local player_name = player:get_player_name()
	if not petz.has_lycanthropy(player) then
		meta:set_int("petz:lycanthropy", 1)
		local clan_index = math.random(1, #lycanthropy.clans)
		meta:set_int("petz:werewolf_clan_idx", clan_index)
		minetest.chat_send_player(player_name, S("You've fallen ill with Lycanthropy!"))

		petz.set_werewolf(player)
	end
end

petz.cure_lycanthropy = function(player)
	local player_name = player:get_player_name()
	if petz.is_werewolf(player) then
		petz.unset_werewolf(player)
	end
	player:get_meta():set_int("petz:lycanthropy", 0)
	minetest.chat_send_player(player_name, S("You've cured of Lycanthropy"))
end

---
--- Register Functions
---

minetest.register_on_leaveplayer(function(player)
	-- cleanup hud ids
	local player_name = player:get_player_name()
	hud_id_by_player_name[player_name] = nil
end)

---
--- On_punch: Infection Engine here.
---

minetest.register_on_punchplayer(function(player, hitter, time_from_last_punch, tool_capabilities, dir, damage)
	if hitter:is_player() or petz.has_lycanthropy(player) then -- a hitter-player cannot infect and the player should not be a werewolf yet
		return
	end
	local hitter_ent = hitter:get_luaentity() --the hitter is an entity, not a player
	if not(hitter_ent.type == "wolf") and not(hitter_ent.type == "werewolf") then --thse can infect
		return
	end
	local is_black_wolf = hitter_ent.type == "wolf" and hitter_ent.texture_no == (#hitter_ent.skin_colors-hitter_ent.mutation+1)
	local bit_by_wolf = hitter_ent.type == "wolf" and (math.random(1, petz.settings.lycanthropy_infection_chance_by_wolf) == 1)
	local bit_by_werewolf = hitter_ent.type == "werewolf" and (math.random(1, petz.settings.lycanthropy_infection_chance_by_werewolf) == 1)
	if is_black_wolf or bit_by_wolf or bit_by_werewolf then
		--Conditions to infect: black wolf or get the chance of another wolf or werewolf
		petz.set_lycanthropy(player)
	end
end)

---
--- On_punch: Less damage if you were a werewolf
---

-- rounds up or down by chance depending on the fractional part
local function probabilistic_round(v)
	return math.floor(v + math.random())
end

minetest.register_on_player_hpchange(function(player, hp_change, reason)
	if reason and reason.type == "punch" and petz.is_werewolf(player) and hp_change < 0 then
		local werewolf_damage_reduction = petz.settings.lycanthropy_werewolf_damage_reduction
		return probabilistic_round(hp_change * (1 - werewolf_damage_reduction))
	end

	return hp_change
end, true)

---
--- Cycle day/night to change
---

local timer = 0
local last_period_of_day

minetest.register_globalstep(function(dtime)
	timer = timer + dtime
	if timer < 5 then
		return
	end
	timer = 0
	local current_period_of_day = petz.is_night()
	if (current_period_of_day ~= last_period_of_day) then --only continue if there is a change day-night or night-day
		last_period_of_day = current_period_of_day
		for _, player in pairs(minetest.get_connected_players()) do
			if petz.has_lycanthropy(player) then
				if petz.is_night() then
					if not(petz.is_werewolf(player)) then
						petz.set_werewolf(player)
						minetest.chat_send_player(player:get_player_name(), S("You are now a werewolf"))
					end
				else
					if petz.is_werewolf(player) then
						petz.unset_werewolf(player)
						minetest.chat_send_player(player:get_player_name(), S("You are now a human"))
					end
				end
			end
		end
	end
end)

--
-- On_JoinPlayer: Check if werewolf and act in consequence
--

minetest.register_on_joinplayer(
	function(player)
		if petz.has_lycanthropy(player) then
			if petz.is_night() then
				petz.set_werewolf(player)
			elseif not(petz.is_night()) then
				petz.unset_werewolf(player)
			end
		end
	end
)

--
-- A werewolf only can eat raw meat
--

if not minetest.get_modpath("hbhunger") then
	minetest.register_on_item_eat(
		function(hp_change, replace_with_item, itemstack, user, pointed_thing)
			if petz.is_werewolf(user) and (minetest.get_item_group(itemstack:get_name(), "food_meat_raw") == 0) then
				local user_name = user:get_player_name()
				--minetest.chat_send_player(user_name, itemstack:get_name())
				minetest.chat_send_player(user_name, S("Werewolves only can eat raw meat!"))
				return itemstack
			end
    	end
	)
end

--
--CHAT COMMANDS
--

minetest.register_chatcommand("werewolf", {
	description = "Convert a player into a werewolf",
	privs = {
        server = true,
    },
    func = function(name, param)
		local subcommand, player_name = string.match(param, "([%a%d_-]+) ([%a%d_-]+)")
		if not(subcommand == "set") and not(subcommand == "unset") and not(subcommand == "reset")
			and not(subcommand == "clan") and not(subcommand == "cure") then
				return true, "Error: The subcomands for the werewolf command are 'set' / 'unset' / 'cure' / 'clan'"
		end
		if player_name then
			local player = minetest.get_player_by_name(player_name)
			if player then
				if subcommand == "set" then
					if petz.has_lycanthropy(player) then
						return false, player_name .. " already has lycanthropy"
					else
						petz.set_lycanthropy(player)
						return true, player_name .." has been given lycanthropy!"
					end
				elseif subcommand == "unset" then
					petz.unset_werewolf(player)
					return true, "The werewolf".." "..player_name .." ".."set to human form!"
				elseif subcommand == "cure" then
					if petz.has_lycanthropy(player) then
						petz.cure_lycanthropy(player)
						return true, "The lycanthropy of".." "..player_name .." ".."was cured!"
					else
						return false, player_name .." ".."is not a werewolf!"
					end
				elseif subcommand == "clan" then
					if petz.has_lycanthropy(player) then
						local meta = player:get_meta()
						local clan_name = lycanthropy.clans[meta:get_int("petz:werewolf_clan_idx")].name
						return true, "The clan of".." "..player_name .." ".."is".." '"..clan_name.."'"
					else
						return false, player_name .." ".."is not a werewolf!"
					end
				end
			else
				return false, player_name .." ".."not online!"
			end
		else
			return true, "Not a player name in command"
		end
    end,
})

minetest.register_chatcommand("howl", {
	description = "Do a howl sound",
    func = function(name, param)
		local player = minetest.get_player_by_name(name)
		if player then
			if petz.is_werewolf(player) then
				local pos = player:get_pos()
				kitz.make_sound("pos", pos, "petz_werewolf_howl", petz.settings.max_hear_distance)
			else
				return false, "Error: You are not a werewolf."
			end
		else
			return false, name .." ".."not online!"
		end
    end,
})

--
-- Lycanthropy Items
--

minetest.register_craftitem("petz:lycanthropy_remedy", {
    description = S("Lycanthropy Remedy"),
    inventory_image = "petz_lycanthropy_remedy.png",
    wield_image = "petz_lycanthropy_remedy.png",
    on_use = function (itemstack, user, pointed_thing)
		if petz.has_lycanthropy(user) then
			petz.cure_lycanthropy(user)
		end
        return minetest.do_item_eat(0, "vessels:glass_bottle", itemstack, user, pointed_thing)
    end,
})

minetest.register_craft({
    type = "shaped",
    output = "petz:lycanthropy_remedy",
    recipe = {
        {"", "petz:wolf_jaw", ""},
        {"dye:white", "petz:wolf_fur", "dye:violet"},
        {"", "petz:beaver_oil", ""},
    }
})

--
-- WEREWOLF MONSTER
--

local pet_name = "werewolf"
local scale_model = 1.0
local mesh = "petz_werewolf.b3d"
local textures = lycanthropy.werewolf.textures
local collisionbox = lycanthropy.werewolf.collisionbox

minetest.register_entity("petz:"..pet_name,{
	--Petz specifics
	type = "werewolf",
	init_tamagochi_timer = false,
	is_pet = false,
	is_monster = true,
	is_boss = true,
	has_affinity = false,
	is_wild = true,
	attack_player = true,
	give_orders = false,
	can_be_brushed = false,
	capture_item = nil,
	follow = petz.settings.werewolf_follow,
	drops = {
		{name = "petz:wolf_fur", chance = 5, min = 1, max = 1,},
		{name = "petz:wolf_jaw", chance = 5, min = 1, max = 1,},
	},
	rotate = petz.settings.rotate,
	physical = true,
	stepheight = 0.1,	--EVIL!
	collide_with_objects = true,
	collisionbox = collisionbox,
	visual = petz.settings.visual,
	mesh = mesh,
	textures = textures,
	visual_size = {x=1.0*scale_model, y=1.0*scale_model},
	static_save = true,
	get_staticdata = kitz.statfunc,
	-- api props
	springiness= 0,
	buoyancy = 0.5, -- portion of hitbox submerged
	max_speed = 1.5,
	jump_height = 1.5,
	view_range = 20,
	lung_capacity = 10, -- seconds
	max_hp = 50,

	attack={range=0.5, damage_groups={fleshy=9}},
	animation = {
		walk={range={x=168, y=187}, speed=30, loop=true},
		run={range={x=168, y=187}, speed=30, loop=true},
		stand={range={x=0, y=79}, speed=30, loop=true},
	},
	sounds = {
		misc = "petz_werewolf_howl",
		attack = "petz_monster_roar",
		die = "petz_monster_die",
	},

	logic = petz.monster_brain,

	on_activate = function(self, staticdata, dtime_s) --on_activate, required
		kitz.actfunc(self, staticdata, dtime_s)
		petz.set_initial_properties(self, staticdata, dtime_s)
	end,

	on_punch = function(self, puncher, time_from_last_punch, tool_capabilities, dir)
		petz.on_punch(self, puncher, time_from_last_punch, tool_capabilities, dir)
	end,

	on_rightclick = function(self, clicker)
		petz.on_rightclick(self, clicker)
	end,

	on_step = function(self, dtime)
		kitz.stepfunc(self, dtime) -- required
		petz.on_step(self, dtime)
	end,

})

petz:register_egg("petz:werewolf", S("Werewolf"), "petz_spawnegg_werewolf.png", false)

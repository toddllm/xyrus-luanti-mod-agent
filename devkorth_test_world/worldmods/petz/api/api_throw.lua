local function get_offset(axis, old_velocity, new_velocity)
	if axis == "x" then
		if old_velocity.x >= new_velocity.x then
			return vector.new(-1, 0, 0)
		else
			return vector.new(1, 0, 0)
		end
	elseif axis == "y" then
		if old_velocity.y >= new_velocity.y then
			return vector.new(0, -1, 0)
		else
			return vector.new(0, 1, 0)
		end
	elseif axis == "z" then
		if old_velocity.z >= new_velocity.z then
			return vector.new(0, 0, -1)
		else
			return vector.new(0, 0, 1)
		end
	end
	return vector.new(0, 0, 0)
end

local function get_object_name(obj)
	if minetest.is_player(obj) then
		return obj:get_player_name()
	else
		local ent = obj:get_luaentity()
		if ent then
			return ent.name
		end
	end

	return ""
end

local effects = {
	fire = function(self, pos, pos_above)
		kitz.make_sound("pos", pos, "petz_firecracker", petz.settings.max_hear_distance)

		local node = minetest.get_node(pos)
		local node_name = node.name

		if minetest.get_item_group(node_name, "flammable") > 1 and not minetest.is_protected(pos, self.shooter_name) then
			minetest.set_node(pos, { name = "fire:basic_flame"})
		end

		local node_above = minetest.get_node(pos_above)

		if node_above.name == "air" then
			petz.do_particles_effect(nil, pos_above, "fire")
		end
	end,
	cobweb = function(self, pos, pos_above)
		local node_above = minetest.get_node(pos_above)

		if node_above.name == "air" and not minetest.is_protected(pos_above, self.shooter_name) then
			minetest.set_node(pos_above, {name = "petz:cobweb"})
		end
	end,
}

function petz.throw(self, dtime, damage, effect, particles, sound, moveresult)
	-- this is the on_step of a thrown entity
	if self.shooter_name == "" then
		if self.object:get_attach() == nil then
			self.object:remove()
		end
		return
	end

	local collision = moveresult.collisions[1]
	if not collision then
		return
	end

	local pos, pos_above
	if collision.type == "node" then
		pos = collision.node_pos
		local offset = get_offset(collision.axis, collision.old_velocity, collision.new_velocity)
		pos_above = vector.add(pos, offset)

	elseif collision.type == "object" then
		local obj = collision.object
		if get_object_name(obj) == self.shooter_name then
			-- don't hit ourselves
			return
		end

		pos = vector.round(obj:get_pos())
		pos_above = pos
		if damage and damage > 0 then
			local damage_group = effect == "fire" and "fire" or "fleshy"
			local shooter = self.shooter
			if minetest.is_player(shooter) or shooter:get_luaentity() then
				shooter = self.shooter
			else
				shooter = obj
			end

			obj:punch(shooter, 1.0, {full_punch_interval = 1.0, damage_groups = {[damage_group]=damage}})
		end

	else
		-- should never happen
		return
	end

	if effect then
		local do_effect = effects[effect]
		if do_effect then
			do_effect(self, pos, pos_above)
		end
	end
	if particles then
		petz.do_particles_effect(nil, pos_above, particles)
	end
	if sound then
		kitz.make_sound("pos", pos, sound, petz.settings.max_hear_distance)
	end

	self.object:remove()
end

function petz.spawn_throw_object(shooter, strength, entity)
	local pos = shooter:get_pos()
	local ent = shooter:get_luaentity()
	local dir
	local yaw

	if shooter:is_player() then
		pos.y = pos.y + (shooter:get_properties().eye_height or 1.5) -- camera offset
		yaw = shooter:get_look_horizontal()
		dir = shooter:get_look_dir()

	elseif ent then
		yaw = shooter:get_yaw()
		dir = minetest.yaw_to_dir(yaw)

	else
		return
	end

	local throw_obj = minetest.add_entity(pos, entity)
	if not throw_obj then
		return
	end

	local throw_ent = throw_obj:get_luaentity()
	if not throw_ent then
		return
	end

	throw_ent.shooter = shooter
	throw_ent.shooter_name = get_object_name(shooter)
	throw_obj:set_yaw(yaw - 0.5 * math.pi)
	throw_obj:set_velocity(vector.multiply(dir, strength))

	return true
end

function petz.register_throw_entity(name, textures, damage, effect, particles, sound)
	minetest.register_entity(name, {
		initial_properties = {
			hp_max = 4,       -- possible to catch the arrow (pro skills)

			visual = "wielditem",
			textures = {textures},
			visual_size = {x = 1.0, y = 1.0},

			physical = true,
			collide_with_objects = true,
			collisionbox = {-0.1, -0.1, -0.1, 0.1, 0.1, 0.1},

			static_save = false,
		},

		on_activate = function(self)
			self.object:set_acceleration({x = 0, y = -9.81, z = 0})
			self.shooter_name = ""
		end,

		on_punch = function(self, puncher, time_from_last_punch, tool_capabilities, dir)
			return false
		end,

		on_step = function(self, dtime, moveresult)
			petz.throw(self, dtime, damage, effect, particles, sound, moveresult)
		end,
	})
end

-- tools for debugging

minetest.register_tool("petz:cobweb_gun", {
	description = "cobweb gun (shoot cobweb projectile)",
	short_description = "cobweb gun",
	inventory_image = "default_stick.png",
	groups = {not_in_creative_inventory = 1, not_in_craft_guide = 1},
	on_use = function(itemstack, user, pointed_thing)
		if minetest.registered_entities["petz:ent_cobweb"] then
			petz.spawn_throw_object(user, 20, "petz:ent_cobweb")
		end
	end,
})

minetest.register_tool("petz:grenade_gun", {
	description = "grenade gun (shoot grenade projectile)",
	short_description = "grenade gun",
	inventory_image = "default_stick.png",
	groups = {not_in_creative_inventory = 1, not_in_craft_guide = 1},
	on_use = function(itemstack, user, pointed_thing)
		if minetest.registered_entities["petz:ent_jack_o_lantern_grenade"] then
			petz.spawn_throw_object(user, 20, "petz:ent_jack_o_lantern_grenade")
		end
	end,
})

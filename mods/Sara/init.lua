-- Register the Sara entity
minetest.register_entity("sara:sara", {
    initial_properties = {
        physical = true,
        collisionbox = {-0.35, -0.5, -0.35, 0.35, 1.8, 0.35},
        visual = "mesh",
        mesh = "character.b3d",
        textures = {"default_player.png"},
        makes_footstep_sound = true,
        visual_size = {x = 1, y = 1}
    },
    on_activate = function(self, staticdata)
        self.object:set_properties(self.initial_properties)
    end,
    on_punch = function(self, hitter)
        if hitter and hitter:is_player() then
            minetest.chat_send_player(hitter:get_player_name(), "Don't punch, talk by using right click!")
        end
    end,
    on_rightclick = function(self, clicker)
        if clicker and clicker:is_player() then
            minetest.chat_send_player(clicker:get_player_name(), "I want you to make a Food Factory please make a furnace and a chest, serve customers, and hire workers!")
        end
    end
})

-- Node to spawn Sara when placed
minetest.register_node("sara:spawn_node", {
    description = "Sara Spawn",
    tiles = {"default_dirt.png"},
    groups = {cracky = 3},
    on_construct = function(pos)
        local spawn_pos = vector.add(pos, {x = 0, y = 1, z = 0})
        minetest.add_entity(spawn_pos, "sara:sara")
        minetest.set_node(pos, {name = "air"})
    end
})
-- Devkorth Entity Definition
-- TODO: Implement the omnipotent entity

minetest.register_entity("devkorth:devkorth", {
    -- Basic properties
    physical = true,
    collide_with_objects = false,
    collisionbox = {-1, 0, -1, 1, 4, 1}, -- 2x normal size
    visual = "mesh",
    mesh = "character.b3d", -- TODO: Custom mesh
    textures = {"devkorth_texture.png"}, -- TODO: Create texture
    visual_size = {x=2, y=2, z=2},
    glow = 14, -- Divine light
    
    -- Infinite HP
    hp_max = math.huge,
    armor_groups = {immortal=1},
    
    -- TODO: Implement AI states and powers
    on_activate = function(self, staticdata)
        self.ai_state = "observing"
    end,
    
    on_step = function(self, dtime)
        -- TODO: Implement GIGANTHUGAMAJALENTURLA AI
    end,
    
    on_punch = function(self, puncher)
        -- Single Counter-Attack Rule - INSTANT KO
        if puncher and puncher:is_player() then
            local name = puncher:get_player_name()
            
            -- Reality responds to the insult
            minetest.chat_send_all(name .. " dared to strike Devkorth...")
            minetest.chat_send_all("Reality itself rejects this action.")
            
            -- INSTANT KO
            puncher:set_hp(0)
            
            -- Permanent reality scar at death location
            local death_pos = puncher:get_pos()
            minetest.set_node(death_pos, {name="devkorth:void_scar"})
            
            -- The quote
            minetest.chat_send_all("Devkorth: 'Your attempts amuse me.'")
        end
    end,
    
    on_rightclick = function(self, clicker)
        -- Players CANNOT talk with Dev
        if clicker and clicker:is_player() then
            local name = clicker:get_player_name()
            
            -- Dev judges silently
            if math.random() < 0.1 then -- 10% chance of gift
                -- Grant divine gift
                local inv = clicker:get_inventory()
                inv:add_item("main", "devkorth:devkorth_gift")
                minetest.chat_send_player(name, "Devkorth deems you worthy of a gift beyond comprehension.")
            else
                -- Silent acknowledgment
                minetest.chat_send_player(name, "Devkorth observes you. No words are exchanged.")
            end
        end
    end,
})
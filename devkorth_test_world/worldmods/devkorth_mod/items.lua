-- Sacred Items of Devkorth

-- Devkorth Block - Indestructible reality anchor
minetest.register_node("devkorth:devkorth_block", {
    description = "Devkorth Block - Reality Anchor",
    tiles = {"devkorth_block.png"},
    groups = {unbreakable=1, not_in_creative_inventory=1},
    sounds = default.node_sound_stone_defaults(),
    light_source = 14,
    -- TODO: Add reality-anchoring properties
})

-- Devkorth Tool - Infinite creation, instant mining
minetest.register_tool("devkorth:devkorth_tool", {
    description = "Devkorth Tool - Reality Shaper",
    inventory_image = "devkorth_tool.png",
    tool_capabilities = {
        full_punch_interval = 0.1,
        max_drop_level = 3,
        groupcaps = {
            -- Instant mining of everything
            cracky = {times={[1]=0, [2]=0, [3]=0}, uses=0, maxlevel=3},
            crumbly = {times={[1]=0, [2]=0, [3]=0}, uses=0, maxlevel=3},
            snappy = {times={[1]=0, [2]=0, [3]=0}, uses=0, maxlevel=3},
            choppy = {times={[1]=0, [2]=0, [3]=0}, uses=0, maxlevel=3},
            oddly_breakable_by_hand = {times={[1]=0, [2]=0, [3]=0}, uses=0, maxlevel=3},
        },
        damage_groups = {fleshy=1000},
    },
    -- TODO: Add reality manipulation abilities
})

-- Void Scar - Permanent mark where someone attacked Devkorth
minetest.register_node("devkorth:void_scar", {
    description = "Void Scar - A permanent wound in reality",
    tiles = {"devkorth_void.png"},
    groups = {unbreakable=1, not_in_creative_inventory=1},
    sounds = default.node_sound_stone_defaults(),
    light_source = -14, -- Negative light (darkness)
    walkable = false,
    damage_per_second = 10,
    post_effect_color = {a=255, r=0, g=0, b=0},
})

-- Devkorth Gift - Contains impossible items
minetest.register_craftitem("devkorth:devkorth_gift", {
    description = "Devkorth's Gift - Beyond Comprehension",
    inventory_image = "devkorth_gift.png",
    stack_max = 1,
    on_use = function(itemstack, user, pointed_thing)
        local inv = user:get_inventory()
        local name = user:get_player_name()
        
        -- Random impossible gifts
        local gifts = {
            "devkorth:devkorth_tool",
            "devkorth:devkorth_block",
            "devkorth:reality_fragment",
            "devkorth:time_crystal",
            "devkorth:void_essence",
        }
        
        local gift = gifts[math.random(#gifts)]
        inv:add_item("main", gift)
        
        minetest.chat_send_player(name, "The gift unfolds into something that shouldn't exist...")
        
        itemstack:take_item()
        return itemstack
    end,
})

-- Reality Fragment - A piece of reality itself
minetest.register_craftitem("devkorth:reality_fragment", {
    description = "Reality Fragment - Handle with existential care",
    inventory_image = "devkorth_reality.png",
    on_use = function(itemstack, user, pointed_thing)
        -- Warp a small area
        if pointed_thing.type == "node" then
            devkorth.powers.warp_terrain(pointed_thing.under, 3)
        end
        itemstack:take_item()
        return itemstack
    end,
})

-- Time Crystal - Controls time flow
minetest.register_craftitem("devkorth:time_crystal", {
    description = "Time Crystal - Time bends to your will",
    inventory_image = "devkorth_time.png",
    on_use = function(itemstack, user, pointed_thing)
        -- Speed up time
        minetest.set_timeofday(minetest.get_timeofday() + 0.5)
        minetest.chat_send_player(user:get_player_name(), "Time flows differently now...")
        return itemstack
    end,
})

-- Void Essence - Pure nothingness
minetest.register_craftitem("devkorth:void_essence", {
    description = "Void Essence - The absence of everything",
    inventory_image = "devkorth_void_essence.png",
    on_place = function(itemstack, placer, pointed_thing)
        if pointed_thing.type == "node" then
            -- Create a void hole
            local pos = pointed_thing.above
            for x = -1, 1 do
                for y = -1, 1 do
                    for z = -1, 1 do
                        local p = vector.add(pos, {x=x, y=y, z=z})
                        minetest.remove_node(p)
                    end
                end
            end
        end
        itemstack:take_item()
        return itemstack
    end,
})
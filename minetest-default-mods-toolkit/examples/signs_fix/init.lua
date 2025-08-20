-- Signs Fix Mod - WORKING VERSION with FIXED POSITIONING
-- Entity appears ON the sign surface, not above it

local S = minetest.get_translator("default")

-- Text entity for displaying sign text
minetest.register_entity("signs_fix:text", {
    initial_properties = {
        visual = "upright_sprite",
        visual_size = { x = 1.0, y = 0.5 },
        textures = { "default_wood.png" },
        physical = false,
        collide_with_objects = false,
        pointable = false,
        static_save = true,
    },
    
    on_activate = function(self, staticdata, dtime_s)
        if not staticdata or staticdata == "" then
            self.object:remove()
            return
        end
        
        local data = minetest.deserialize(staticdata)
        if not data or not data.text then
            self.object:remove()
            return
        end
        
        self.text = data.text
        self:update_texture()
    end,
    
    update_texture = function(self)
        if not self.text then return end
        
        -- For now, just use wood texture to verify positioning
        -- TODO: Implement proper text rendering
        self.object:set_properties({
            textures = {"default_wood.png"},
            visual_size = {x = 0.9, y = 0.45}
        })
    end,
    
    get_staticdata = function(self)
        if self.text then
            return minetest.serialize({text = self.text})
        end
        return ""
    end
})

-- Helper function to update sign text entity
local function update_sign_text(pos, text)
    -- Remove old text entity if exists
    local objects = minetest.get_objects_inside_radius(pos, 0.5)
    for _, obj in ipairs(objects) do
        local ent = obj:get_luaentity()
        if ent and ent.name == "signs_fix:text" then
            obj:remove()
        end
    end
    
    -- Add new text entity if text exists
    if text and text ~= "" then
        local node = minetest.get_node(pos)
        local param2 = node.param2
        
        -- Calculate text position based on sign orientation (wallmounted)
        -- Wallmounted param2: 2=+Z, 3=-Z, 4=+X, 5=-X
        local offset = {x = 0, y = 0, z = 0}
        local yaw = 0
        
        if param2 == 2 then -- +Z wall (facing -Z)
            offset = {x = 0, y = 0, z = -0.07}
            yaw = 0
        elseif param2 == 3 then -- -Z wall (facing +Z)
            offset = {x = 0, y = 0, z = 0.07}
            yaw = math.pi
        elseif param2 == 4 then -- +X wall (facing -X)
            offset = {x = -0.07, y = 0, z = 0}
            yaw = math.pi / 2
        elseif param2 == 5 then -- -X wall (facing +X)
            offset = {x = 0.07, y = 0, z = 0}
            yaw = -math.pi / 2
        else
            -- Fallback for unexpected values
            offset = {x = 0, y = 0, z = -0.07}
            yaw = 0
        end
        
        local text_pos = vector.add(pos, offset)
        local obj = minetest.add_entity(text_pos, "signs_fix:text")
        
        if obj then
            obj:set_yaw(yaw)
            local ent = obj:get_luaentity()
            if ent then
                ent.text = text
                ent:update_texture()
            end
        end
    end
end

-- Override the sign registration function
local function override_sign(material)
    local node_name = "default:sign_wall_" .. material
    local def = minetest.registered_nodes[node_name]
    
    if not def then
        return
    end
    
    -- Store original callbacks
    local old_on_construct = def.on_construct
    local old_on_receive_fields = def.on_receive_fields
    local old_after_place_node = def.after_place_node
    local old_on_destruct = def.on_destruct
    
    -- Override the sign definition
    minetest.override_item(node_name, {
        on_construct = function(pos)
            if old_on_construct then
                old_on_construct(pos)
            end
            local meta = minetest.get_meta(pos)
            meta:set_string("formspec", 
                "size[6,3]" ..
                "field[0.5,0.5;5.5,1;text;" .. S("Enter text:") .. ";${text}]" ..
                "button_exit[2,2;2,1;submit;" .. S("Submit") .. "]"
            )
        end,
        
        on_receive_fields = function(pos, formname, fields, sender)
            local player_name = sender:get_player_name()
            if minetest.is_protected(pos, player_name) then
                minetest.record_protection_violation(pos, player_name)
                return
            end
            
            local text = fields.text
            if not text then
                return
            end
            
            if string.len(text) > 512 then
                minetest.chat_send_player(player_name, S("Text too long"))
                return
            end
            
            local meta = minetest.get_meta(pos)
            meta:set_string("text", text)
            
            if #text > 0 then
                meta:set_string("infotext", S('"@1"', text))
            else
                meta:set_string("infotext", '')
            end
            
            -- Update visual text
            update_sign_text(pos, text)
        end,
        
        after_place_node = function(pos, placer, itemstack, pointed_thing)
            if old_after_place_node then
                old_after_place_node(pos, placer, itemstack, pointed_thing)
            end
            -- Check if there's already text
            local meta = minetest.get_meta(pos)
            local text = meta:get_string("text")
            if text and text ~= "" then
                update_sign_text(pos, text)
            end
        end,
        
        on_destruct = function(pos)
            -- Remove text entity
            local objects = minetest.get_objects_inside_radius(pos, 0.5)
            for _, obj in ipairs(objects) do
                local ent = obj:get_luaentity()
                if ent and ent.name == "signs_fix:text" then
                    obj:remove()
                end
            end
            
            if old_on_destruct then
                old_on_destruct(pos)
            end
        end,
    })
end

-- Apply overrides when all mods are loaded
minetest.register_on_mods_loaded(function()
    override_sign("wood")
    override_sign("steel")
    minetest.log("action", "[signs_fix] Sign overrides complete - entities will appear ON signs")
end)

-- LBM to restore text entities on existing signs
minetest.register_lbm({
    label = "Restore sign text entities",
    name = "signs_fix:restore_text",
    nodenames = {"default:sign_wall_wood", "default:sign_wall_steel"},
    run_at_every_load = true,
    action = function(pos, node)
        local meta = minetest.get_meta(pos)
        local text = meta:get_string("text")
        if text and text ~= "" then
            -- Check if entity already exists
            local objects = minetest.get_objects_inside_radius(pos, 0.5)
            local has_text = false
            for _, obj in ipairs(objects) do
                local ent = obj:get_luaentity()
                if ent and ent.name == "signs_fix:text" then
                    has_text = true
                    break
                end
            end
            
            -- Create entity if missing
            if not has_text then
                update_sign_text(pos, text)
            end
        end
    end
})

minetest.log("action", "[signs_fix] Loaded - fixed positioning version")
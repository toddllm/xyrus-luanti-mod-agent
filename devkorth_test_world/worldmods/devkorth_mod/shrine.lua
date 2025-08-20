-- Shrine Detection and Devkorth Manifestation

local check_interval = 5.0 -- Check every 5 seconds

-- Global shrine checker
local shrine_check_timer = 0

minetest.register_globalstep(function(dtime)
    shrine_check_timer = shrine_check_timer + dtime
    
    if shrine_check_timer >= check_interval then
        shrine_check_timer = 0
        
        -- Check all online players
        for _, player in ipairs(minetest.get_connected_players()) do
            local pos = player:get_pos()
            
            if devkorth.check_shrine(pos) then
                -- Check if Devkorth already exists nearby
                local objects = minetest.get_objects_inside_radius(pos, 50)
                local devkorth_exists = false
                
                for _, obj in ipairs(objects) do
                    local ent = obj:get_luaentity()
                    if ent and ent.name == "devkorth:devkorth" then
                        devkorth_exists = true
                        break
                    end
                end
                
                if not devkorth_exists and not devkorth.the_one_exists then
                    -- Check ALL conditions for manifestation
                    if devkorth.check_conditions(pos) then
                        -- ONLY ONE CAN EXIST
                        devkorth.the_one_exists = true
                        
                        -- Manifest Devkorth
                        local spawn_pos = vector.add(pos, {x=0, y=5, z=0})
                        local the_one = minetest.add_entity(spawn_pos, "devkorth:devkorth")
                        
                        -- Reality shakes
                        minetest.chat_send_all("The fabric of reality trembles...")
                        minetest.chat_send_all("The shrine awakens under moonlight...")
                        minetest.chat_send_all("Water ripples... fossils resonate...")
                        minetest.chat_send_all("")
                        minetest.chat_send_all("DEVKORTH HAS MANIFESTED!")
                        minetest.chat_send_all("THE ONE WHO IS ALL!")
                        
                        -- Create reality distortion
                        minetest.add_particlespawner({
                            amount = 1000,
                            time = 10,
                            minpos = vector.subtract(spawn_pos, 20),
                            maxpos = vector.add(spawn_pos, 20),
                            minvel = {x=-5, y=-5, z=-5},
                            maxvel = {x=5, y=5, z=5},
                            minacc = {x=0, y=0, z=0},
                            maxacc = {x=0, y=0, z=0},
                            minexptime = 1,
                            maxexptime = 3,
                            minsize = 1,
                            maxsize = 5,
                            texture = "default_mese_block.png",
                            glow = 14,
                        })
                    else
                        -- Conditions not met
                        minetest.chat_send_player(player:get_player_name(), 
                            "The shrine is complete, but Devkorth requires: moonlight, water, air, and fossils...")
                    end
                end
            end
        end
    end
end)
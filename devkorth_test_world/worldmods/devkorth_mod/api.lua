-- Devkorth API

-- Check if today is Halloween
function devkorth.is_halloween()
    local date = os.date("*t")
    return date.month == 10 and date.day == 31
end

-- Check if today is Friday the 13th
function devkorth.is_friday_13th()
    local date = os.date("*t")
    return date.day == 13 and date.wday == 6 -- 6 = Friday
end

-- Get Devkorth's current power level
function devkorth.get_power_level()
    local halloween = devkorth.is_halloween()
    local friday13 = devkorth.is_friday_13th()
    
    if halloween and friday13 then
        return "ULTIMATE" -- Both aspects merged
    elseif halloween then
        return "SUPERNATURAL"
    elseif friday13 then
        return "HUNTER"
    else
        return "DIVINE" -- Normal omnipotent state
    end
end

-- ONLY ONE DEVKORTH CAN EXIST
devkorth.the_one_exists = false

-- Check if a position has a valid shrine (must look like actual shrine)
function devkorth.check_shrine(pos)
    -- Base layer (5x5 diamond blocks)
    local base_valid = true
    for x = -2, 2 do
        for z = -2, 2 do
            local check_pos = {x=pos.x+x, y=pos.y, z=pos.z+z}
            if minetest.get_node(check_pos).name ~= "default:diamondblock" then
                base_valid = false
            end
        end
    end
    
    -- Central mese block
    local center_pos = {x=pos.x, y=pos.y+1, z=pos.z}
    local has_mese = minetest.get_node(center_pos).name == "default:mese"
    
    -- Pillars (4 corners, 3 blocks high)
    local pillars_valid = true
    for _, offset in ipairs({{-2,-2}, {-2,2}, {2,-2}, {2,2}}) do
        for y = 1, 3 do
            local pillar_pos = {x=pos.x+offset[1], y=pos.y+y, z=pos.z+offset[2]}
            if minetest.get_node(pillar_pos).name ~= "default:diamondblock" then
                pillars_valid = false
            end
        end
    end
    
    return base_valid and has_mese and pillars_valid
end

-- Check manifestation conditions
function devkorth.check_conditions(pos)
    -- Needs moonlight (night time)
    local time = minetest.get_timeofday()
    local is_night = time < 0.25 or time > 0.75
    
    -- Needs water nearby
    local has_water = minetest.find_node_near(pos, 10, {"default:water_source", "default:river_water_source"})
    
    -- Needs air (open to sky)
    local above_pos = {x=pos.x, y=pos.y+10, z=pos.z}
    local has_air = minetest.get_node(above_pos).name == "air"
    
    -- Needs fossils (coal/bones as substitute)
    local has_fossils = minetest.find_node_near(pos, 15, {"default:coalblock", "bones:bones"})
    
    return is_night and has_water and has_air and has_fossils
end
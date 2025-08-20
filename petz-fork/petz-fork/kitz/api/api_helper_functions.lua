kitz.math = {}

function kitz.item_in_itemlist(item_name, itemlist)
	local match = false
	local table = false
	if type(itemlist) == "table" then
		table = true
	end
	if item_name and itemlist then
		local items
		if not table then
			items = string.split(itemlist, ',')
		else
			items = itemlist
		end
		for i = 1, #items do --loop  thru all items
			--minetest.chat_send_player("singleplayer", "itemlist item="..items[i])
			--minetest.chat_send_player("singleplayer", "item name="..item_name)
			local item = petz.str_remove_spaces(items[i]) --remove spaces
			if string.sub(item, 1, 5) == "group" then
				local item_group = minetest.get_item_group(item_name, string.sub(item, 7))
				if item_group > 0 then
					match = true
					break
				end
			else
				if item == item_name then --if node name matches
					match = true
					break
				end
			end
		end
		return match
	end
end

function kitz.remove_mob(self)
	--IMPORTANT: Firstly: Delete Behaviours
	kitz.clear_queue_high(self)
	kitz.clear_queue_low(self)
	self.object:remove()
end

--Nodes

function kitz.is_air(pos)
	local node = kitz.nodeatpos(pos)
	if node and node.name == "air" then
		return true
	else
		return false
	end
end

function kitz.is_liquid(pos)
	local node = kitz.nodeatpos(pos)
	if node and (node.drawtype == 'liquid' or node.drawtype == 'flowingliquid') then
		return true
	else
		return false
	end
end

function kitz.is_walkable(pos, offset)
	if offset then
		pos= vector.new(pos.x, pos.y + offset, pos.z)
	end
	local node = kitz.nodeatpos(pos)
	if node and node.walkable then
		return true
	else
		return false
	end
end

function kitz.adjacent_pos_grid(pos, non_oblique)
	local cells = {{x=0, y=0, z=1}, {x=0, y=0, z=-1}, {x=1, y=0, z=0}, {x=-1, y=0, z=0}}
	local grid = {}
	if not non_oblique then
		cells[#cells+1] = {x=1, y=0, z=1}
		cells[#cells+1] = {x=1, y=0, z=-1}
		cells[#cells+1] = {x=-1, y=0, z=1}
		cells[#cells+1] = {x=-1, y=0, z=-1}
	end
	local _cells = kitz.table_shuffle(cells)
	for _, cell_pos in ipairs(_cells) do
		grid[#grid+1] = vector.add(pos, cell_pos)
	end
	return grid
end

function kitz.get_random_adjacent_pos(pos, non_oblique)
	local grid = kitz.adjacent_pos_grid(pos, non_oblique)
	return grid[math.random(1, #grid)]
end

--Node Helpers

function kitz.in_group(pos, group)
	local node = minetest.get_node_or_nil(pos)
	if node then
		local group_value = minetest.get_item_group(node.name, group)
		if group_value > 0 then
			return group_value
		else
			return false
		end
	else
		return false
	end
end

--Tables

function kitz.is_table(elem)
	if (type(elem) == "table") then
		return true
	else
		return false
	end
end

function kitz.table_is_empty(t)
	if not(type(t) == "table") then
		return false
	end
	local next = next
	if next(t) == nil then
		return true
	else
		return false
	end
end

function kitz.table_shuffle(t) -- suffles numeric indices
    local len, random = #t, math.random
    for i = len, 2, -1 do
        local j = random(1, i)
        t[i], t[j] = t[j], t[i]
    end
    return t
end

--Inventory Cube (3D)

function kitz.create_inv_cube(tiles)
	if not tiles then
		return
	end
	local inv_cube = "[inventorycube"
	local tile_top, tile_left, tile_right
	tile_top = tiles[1]
	if kitz.is_table(tile_top) then
		tile_top = tile_top.name
	end
	if tiles[3] then
		tile_right = tiles[3]
		if kitz.is_table(tile_right) then
			tile_right = tile_right.name
		end
	else
		tile_right = tile_top
	end
	if tiles[6] then
		tile_left = tiles[6]
		if kitz.is_table(tile_left) then
			tile_left = tile_left.name
		end
	else
		tile_left = tile_top
	end
	inv_cube = inv_cube.."{"..tile_top.."{"..tile_left.."{"..tile_right
	return inv_cube
end

-- Strings
function kitz.string_is_empty(s)
  return s == nil or s == ''
end

--Math
function kitz.math.clamp(val, low, high)
	return math.min(math.max(val, low), high)
end

--Files
function kitz.file_exists(filename)
	local f = io.open(filename, "r")
	if f ~= nil then
		io.close(f)
		return true
	else
		return false
	end
end


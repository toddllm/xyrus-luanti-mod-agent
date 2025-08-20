local modname = 'friendly_guard'

minetest.register_entity(modname..':guard',{
  initial_properties={
    visual='sprite',
    textures={'default_stone.png'},
    visual_size={x=4,y=4},
    nametag='Guard',
  },
  on_rightclick=function(self, clicker)
    minetest.log('action', clicker:get_player_name() .. ' right-clicked guard')
    minetest.show_formspec(clicker:get_player_name(), modname..':hello',
      'formspec_version[4]size[8,6]label[0.5,0.7;Hello]button_exit[3,5;2,0.8;ok;OK]')
  end,
})

minetest.register_chatcommand('spawn_guard',{
  func=function(name)
    local p=minetest.get_player_by_name(name)
    local pos=vector.round(p:get_pos())
    minetest.add_entity({x=pos.x,y=pos.y+1,z=pos.z}, modname..':guard')
    minetest.log('action', name .. ' used /spawn_guard')
    return true,'Guard spawned.'
  end,
})

minetest.register_node(modname..':spawn_node',{
  description='Guard Spawn Node',
  tiles={'default_stone.png'},
  groups={choppy=2},
  on_construct=function(pos)
    local sp_pos={x=pos.x,y=pos.y+1,z=pos.z}
    minetest.add_entity(sp_pos, modname..':guard')
    minetest.set_node(pos,{name='air'})
    minetest.log('action', 'spawn_node constructed at '..minetest.pos_to_string(pos))
  end,
})

minetest.log('action', '[daddy2] Mod loaded.')

minetest.register_chatcommand('hello', {
    description = 'Say hello',
    func = function(name, param)
        minetest.chat_send_player(name, 'Hello from daddy2!')
    end,
})
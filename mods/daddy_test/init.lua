minetest.register_chatcommand("hello", {
    params = "",
    description = "Say hello",
    func = function(name, param)
        minetest.chat_send_player(name, "Hello, world!")
        return true
    end
})

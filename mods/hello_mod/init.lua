minetest.register_chatcommand("hello", {
  description = "Say hello",
  privs = {},
  func = function(name)
    minetest.chat_send_player(name, "Hello, world!")
  end,
})
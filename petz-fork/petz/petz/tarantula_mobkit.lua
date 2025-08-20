--
--TARANTULA
--

petz.register("tarantula", {
	description = "Tarantula",
	scale_model = 1.85,
	skin_colors = {"black", "orange"},
	collisionbox = {
		p1 = {x= -0.1875, y = -0.5, z = -0.1875},
		p2 = {x= 0.1875, y = -0.125, z = 0.1875}
	},
	selectionbox = {
		p1 = {x= -0.25, y = -0.5, z = -0.25},
		p2 = {x= 0.3125, y = -0.25, z = 0.3125}
	},
	is_boss = true,
	is_monster = true,
	is_wild = true,
	attack_player = true,
	max_hp = 30,
	max_speed = 1.5,
	view_range = 10,
	capture_item = "net",
	jump_height = 2.1,

	logic = "monster",

	drops = {
		{name = "farming:string", chance = 3, min = 1, max = 1,},
		{name = "petz:spider_eye", chance = 3, min = 1, max = 1,},
	},

	head = {
		position = vector.new(0, 0.2908, -0.2908),
		rotation_origin = vector.new(-90, 0, 0), --in degrees, normally values are -90, 0, 90
		eye_offset = -0.2,
	},

	attack={range=0.5, damage_groups={fleshy=9}},

	animation = {
		walk= {range={x=1, y=21}, speed=30, loop=true},
		stand= {range={x=23, y=34}, speed=5, loop=true},
		attack= {range={x=34, y=40}, speed=30, loop=false},
	},

	sounds = {
		attack = "petz_spider_attack",
	},

})

--
--RAT
--

petz.register("rat", {
	description = "Rat",
	scale_model = 1.2,
	collisionbox = {
		p1 = {x= -0.1875, y = -0.5, z = -0.1875},
		p2 = {x= 0.1875, y = -0.125, z = 0.1875}
	},
	selectionbox = {
		p1 = {x= -0.1875, y = -0.5, z = -0.25},
		p2 = {x= 0.18755, y = -0.125, z = 0.375}
	},
	is_monster = true,
	is_wild = true,
	attack_player = true,
	max_hp = 20,
	max_speed = 3,
	view_range = 10,
	capture_item = "net",
	jump_height = 2,

	logic = "predator",

	drops = {
		{name = "petz:bone", chance = 5, min = 1, max = 1,},
	},

	head = {
		position = vector.new(0, 0.2908, -0.2908),
		rotation_origin = vector.new(-90, 0, 0), --in degrees, normally values are -90, 0, 90
		eye_offset = -0.2,
	},

	attack={range=0.5, damage_groups={fleshy=7}},

	animation = {
		walk={range={x=1, y=12}, speed=25, loop=true},
		run={range={x=13, y=25}, speed=25, loop=true},
		stand={
			{range={x=26, y=46}, speed=5, loop=true},
			{range={x=47, y=59}, speed=5, loop=true},
			{range={x=82, y=94}, speed=5, loop=true},
		},
	},

	sounds = {
		misc = "pet_rat_squeak",
		attack = "pet_rat_squeak",
	},
})

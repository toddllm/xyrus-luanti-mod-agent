local S= ...

petz.do_feed = function(self)
	petz.set_affinity(self, petz.settings.tamagochi_feed_hunger_rate)
	self.fed = kitz.remember(self, "fed", true)
end

petz.after_tame = function(self)
	if petz.settings.tamagochi_mode then
		self.init_tamagochi_timer = true
	end
end

--
--Tame with a whip mechanic
--

-- Whip/lashing behaviour

petz.do_lashing = function(self)
    if not self.lashed then
        self.lashed = kitz.remember(self, "lashed", true)
    end
    kitz.make_sound("object", self.object, "petz_"..self.type.."_moaning", petz.settings.max_hear_distance)
end

petz.tame_whip= function(self, hitter)
		local wielded_item_name= hitter:get_wielded_item():get_name()
		if (wielded_item_name == "petz:whip") then
			if not self.tamed then
				--The mob can be tamed lashed with a whip
				self.lashing_count = self.lashing_count + 1
				if self.lashing_count >= petz.settings.lashing_tame_count then
					self.lashing_count = kitz.remember(self, "lashing_count", 0)	 --reset to 0
					kitz.set_owner(self, hitter:get_player_name())
					petz.after_tame(self)
					minetest.chat_send_player(self.owner, S("The").." "..S(petz.first_to_upper(self.type)).." "..S("has been tamed."))
					kitz.clear_queue_high(self) -- do not attack
				end
			else
				if (petz.settings.tamagochi_mode) and (self.owner == hitter:get_player_name()) then
					petz.do_lashing(self)
				end
			end
			kitz.make_sound("object", hitter, "petz_whip", petz.settings.max_hear_distance)
		end
end

--Ants
petz.feed_queen_ant = function(self, clicker, player_name, wielded_item)
	wielded_item:take_item()
	clicker:set_wielded_item(wielded_item)
	self.eggs_count = kitz.remember(self, "eggs_count", 0)
	minetest.chat_send_player(player_name, S("The Queen Ant will produce more eggs."))
end

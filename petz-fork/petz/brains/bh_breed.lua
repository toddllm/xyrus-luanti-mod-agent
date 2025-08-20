--
-- Breed Behaviour
--

function petz.bh_breed(self, pos)
	if self.breed and self.is_rut and self.is_male then --search a couple for a male!
		local couple_name = "petz:"..self.type
		if self.type == "elephant" then
			couple_name = couple_name.."_female"
		end
		local couple_obj = kitz.get_closest_entity(self, couple_name)	-- look for a couple
		if couple_obj then
			local couple = couple_obj:get_luaentity()
			if couple and couple.is_rut and not(couple.is_pregnant) and not(couple.is_male) then --if couple and female and is not pregnant and is rut
				local couple_pos = couple.object:get_pos() --get couple pos
				local copulation_distance = petz.settings[self.type.."_copulation_distance"] or 1
				if vector.distance(pos, couple_pos) <= copulation_distance then --if close
					--Changue some vars
					self.is_rut = kitz.remember(self, "is_rut", false)
					couple.is_rut = kitz.remember(couple, "is_rut", false)
					couple.is_pregnant = kitz.remember(couple, "is_pregnant", true)
					couple.father_genes = kitz.remember(couple, "father_genes", self.genes)

					if self.is_mountable then -- store father stats in mother if breeding pony or camel
						local speedup = (self.horseshoes or 0) * petz.settings.horseshoe_speedup
						local father_veloc_stats = {
							max_speed_forward = (self.max_speed_forward - speedup),
							max_speed_reverse = (self.max_speed_reverse - speedup),
							accel = (self.accel - speedup)
						}
						couple.father_veloc_stats = kitz.remember(couple, "father_veloc_stats", father_veloc_stats)
					end

					petz.do_particles_effect(couple.object, couple.object:get_pos(), "pregnant", petz.compose_pregnant_icon(self))
				end
			end
		end
	end
end

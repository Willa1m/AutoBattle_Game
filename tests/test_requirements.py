
import unittest
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game_manager import GameManager, GamePhase, PlayerStatus
from core.unit import Unit, Stats
from core.talent import TalentManager
from core.equipment_manager import EquipmentManager

class TestRequirements(unittest.TestCase):

    def setUp(self):
        self.game = GameManager(max_players=2)
        self.game.add_player("p1", "Player 1")
        self.game.add_player("p2", "Player 2")

    def test_star_scaling_req2(self):
        """Verify star scaling is doubling (Req 2)."""
        stats = Stats(hp=100, atk=10, def_=5, spd=1.0, rng=1, mana=0, crit=0, dodge=0)
        unit = Unit("u1", "Test", "Faction", ["Class"], 1, stats)

        # 1 Star
        s1 = unit.get_stats()
        self.assertEqual(s1.hp, 100)

        # 2 Star
        unit.upgrade()
        s2 = unit.get_stats()
        self.assertEqual(s2.hp, 200) # 100 * 2.0

        # 3 Star
        unit.upgrade()
        s3 = unit.get_stats()
        self.assertEqual(s3.hp, 400) # 100 * 4.0

    def test_talent_system_req4b(self):
        """Verify talent system integration."""
        p1 = self.game.players["p1"]

        # Verify initial level 3 (from updated start_game)
        self.game.start_game()
        self.assertEqual(p1.level, 3)

        # Force level up
        # Level 3 -> 4 requires 3*2 = 6 XP
        # p1 starts with 0 XP.
        # Calling add_experience(6) should trigger level up

        leveled_up = p1.add_experience(6)
        self.assertTrue(leveled_up)
        self.assertEqual(p1.level, 4)

        # In current simulation implementation (GameManager update loop), talents are picked automatically
        # based on pending_talent_choices.
        # But pending_talent_choices are populated ONLY if add_experience returns True inside game loop logic
        # OR if we manually trigger it.
        # In `_battle_between_players`, we updated it to populate pending choices.

        # Let's verify TalentManager logic directly
        tm = TalentManager()
        choices = tm.get_talent_choices(7)
        # Req 4b: Last 3 upgrades (pop 7, 8, 9) will not yield talents below level 3.
        for talent in choices:
            self.assertGreaterEqual(talent.level, 3)

    def test_monster_rounds_req4a(self):
        """Verify monster round logic."""
        self.game.start_game()

        # Fast forward to Round 5
        self.game.current_round = 5
        self.game.phase = GamePhase.PREPARATION
        self.game.phase_start_time = time.time() - 31 # End prep

        # Update should trigger Monster Round
        self.game.update_game_state()
        self.assertEqual(self.game.phase, GamePhase.MONSTER_ROUND)

        # Verify rewards generated
        # In _start_monster_phase, pending_item_choices is populated
        p1 = self.game.players["p1"]
        self.assertTrue(len(p1.pending_item_choices) > 0)

        # Verify Round 5 specific rewards (Two choices)
        # get_monster_round_rewards(5) -> wave 1 -> 2 choices
        em = EquipmentManager()
        rewards = em.get_monster_round_rewards(5)
        self.assertEqual(len(rewards), 2)

        # Round 10 -> 3 choices including 1 faction
        rewards_10 = em.get_monster_round_rewards(10)
        self.assertEqual(len(rewards_10), 3)
        # 3rd choice should be faction (utility)
        # Note: My implementation just appends choices.
        # _generate_special_choices returns list of equipments.
        # Let's verify type of last choice list elements
        last_choice_set = rewards_10[2]
        self.assertEqual(last_choice_set[0].item_type, "utility") # Faction emblem is utility
        self.assertIn("faction_change", last_choice_set[0].effects)

if __name__ == '__main__':
    unittest.main()

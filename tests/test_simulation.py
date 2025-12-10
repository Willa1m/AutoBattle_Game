
import unittest
import sys
import os
import time
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game_manager import GameManager, GamePhase, PlayerStatus, Player
from core.shop import ShopManager, ShopConfig
from core.unit import Unit, Stats
from core.board import Position

class TestGameSimulation(unittest.TestCase):
    """
    Simulates a full game loop to verify integration and test requirements.
    Also checks for performance/blocking issues.
    """

    def setUp(self):
        self.game = GameManager(max_players=2)

        # Manually integrate ShopManager since GameManager doesn't have it
        self.shop_manager = ShopManager()

        # Add players
        self.game.add_player("p1", "Player 1")
        self.game.add_player("p2", "Player 2")

        # Initialize shops for players
        self.shop_manager.create_shop_for_player("p1")
        self.shop_manager.create_shop_for_player("p2")

    def create_mock_unit(self, unit_id, name, faction, classes, cost, hp=100, atk=10):
        stats = Stats(hp=hp, atk=atk, def_=0, spd=1.0, rng=1, mana=0, crit=0.0, dodge=0.0)
        unit = Unit(unit_id, name, faction, classes, cost, stats)
        return unit

    def test_game_loop(self):
        """
        Simulate rounds:
        1. Game Start
        2. Preparation (Buy units, place units)
        3. Battle (Execution)
        4. End Round
        """
        print("\n=== Starting Game Simulation ===")

        # 1. Game Start
        self.assertEqual(self.game.phase, GamePhase.PREPARATION)
        self.assertEqual(self.game.current_round, 1)

        # 2. Preparation Phase
        # Simulate Player 1 buying and placing units
        p1 = self.game.players["p1"]
        p2 = self.game.players["p2"]

        # Create units manually (Mocking shop purchase)
        unit1 = self.create_mock_unit("u1", "Warrior", "天庭", ["金"], 1, hp=200, atk=50)
        unit2 = self.create_mock_unit("u2", "Archer", "天庭", ["木"], 2, hp=150, atk=60)

        # Player 1 "buys" units
        p1.gold -= 3
        p1.stats.units_bought += 2
        p1.add_unit_to_bench(unit1)
        p1.add_unit_to_bench(unit2)

        # Player 1 places units on board
        p1.move_unit_to_board(unit1, (0, 0)) # Using tuple as GameManager expects? No, Unit expects tuple or Position?
        # GameManager.move_unit_to_board uses tuple in signature: move_unit_to_board(self, unit: Unit, position: tuple)
        # But BattleSystem uses tuple. Board uses Position.
        # Let's verify what move_unit_to_board does.
        # It sets unit.position = position.

        p1.move_unit_to_board(unit2, (1, 0))

        # Player 2 "buys" units
        unit3 = self.create_mock_unit("u3", "Demon", "地府", ["火"], 1, hp=200, atk=55)
        p2.add_unit_to_bench(unit3)
        p2.move_unit_to_board(unit3, (0, 0)) # Relative to their side?
        # GameManager just stores them. BattleSystem.setup_battle handles placement on board.
        # GameManager passes p1.board_units and p2.board_units to BattleSystem.setup_battle.
        # BattleSystem auto-places if positions are not provided, OR uses unit.position.
        # Wait, BattleSystem.setup_battle has:
        # def setup_battle(self, player_units, enemy_units, player_positions=None, enemy_positions=None)
        # In GameManager._battle_between_players:
        # success = self.battle_system.setup_battle(player1.board_units.copy(), player2.board_units.copy())
        # It calls WITHOUT positions.
        # So BattleSystem._auto_place_units will be called.
        # unit.position set in GameManager might be ignored or overwritten?
        # Let's check BattleSystem.setup_battle.
        # It clears board. Then if positions NOT provided, it calls _auto_place_units.
        # So manual placement in GameManager doesn't affect BattleSystem placement in current implementation!

        # 3. Trigger Battle Phase
        # Manually fast-forward time or call update
        self.game.phase_duration = 0 # Force end of prep

        # Measure time for battle execution (responsiveness check)
        start_time = time.time()

        # Trigger update, which should start battle
        # Note: update_game_state checks time.time() - phase_start_time >= phase_duration
        # We need to hack phase_start_time
        self.game.phase_start_time = time.time() - 31

        # Redirect stdout to avoid clutter
        # with contextlib.redirect_stdout(io.StringIO()):
        self.game.update_game_state()

        battle_time = time.time() - start_time
        print(f"Battle Phase transition took: {battle_time:.4f}s")

        # Check if we are in Battle phase or if it finished immediately (synchronous battle)
        # GameManager._start_battle_phase calls _execute_battles which calls battle_system.start_battle()
        # which runs the WHOLE battle synchronously.
        # So update_game_state will return only AFTER battle is done.

        # If battle happened, we should be in BATTLE phase (conceptually) but GameManager sets phase to BATTLE
        # then runs battles.
        # Wait, if battles run synchronously in _start_battle_phase, they finish inside that function call.
        # But _start_battle_phase sets self.phase = GamePhase.BATTLE.
        # Then it calls _execute_battles.
        # Then it returns.
        # So we are in BATTLE phase, but the battles are already "done" in terms of logic?
        # Let's check _execute_battles again.
        # It iterates pairs and calls _battle_between_players.
        # _battle_between_players calls battle.start_battle().
        # battle.start_battle() runs the loop until finished.
        # So when _start_battle_phase returns, ALL battles are finished.
        # BUT update_game_state says:
        # elif self.phase == GamePhase.BATTLE:
        #    if self.battle_system.phase.value == "finished":
        #        self._end_battle_phase()

        # So, first call to update_game_state triggers _start_battle_phase.
        # inside it, battles run to completion.
        # self.battle_system.phase becomes FINISHED.
        # The call returns. self.phase is BATTLE.

        # The NEXT call to update_game_state will see self.phase == BATTLE
        # and self.battle_system.phase == FINISHED.
        # So it will call _end_battle_phase().

        # Verify this flow
        self.assertEqual(self.game.phase, GamePhase.BATTLE)

        # Call update again to end battle phase
        self.game.update_game_state()

        # Should be back to Preparation for Round 2
        self.assertEqual(self.game.phase, GamePhase.PREPARATION)
        self.assertEqual(self.game.current_round, 2)

        # Check results
        self.assertEqual(len(self.game.battle_results), 1)
        result = self.game.battle_results[0]
        self.assertEqual(result["round"], 1)
        print(f"Battle Result: {result['winner']} won")

        # 4. Check Stats Updates
        # One player should have a win, one a loss (or draw)
        self.assertTrue(p1.stats.wins > 0 or p1.stats.losses > 0 or p1.last_battle_result == "draw")
        self.assertTrue(p2.stats.wins > 0 or p2.stats.losses > 0 or p2.last_battle_result == "draw")

        # 5. Check Gold/XP rewards
        # Winner gets +1 Gold +2 XP. Loser +1 XP. Everyone +5 Gold round reward.
        # Initial gold 10. p1 spent 3 -> 7. p2 spent 0 -> 10.
        # Round 1 rewards: +5 base.
        # If p1 wins: 7 + 1(win) + 5 = 13.
        # If p1 loses: 7 + 5 = 12.
        self.assertGreaterEqual(p1.gold, 12)
        self.assertGreaterEqual(p2.gold, 15)

    def test_responsiveness_concern(self):
        """
        Demonstrate that long battles block the main thread.
        """
        # Setup a battle that might take "long" (many units)
        p1 = self.game.players["p1"]
        p2 = self.game.players["p2"]

        # Add many units
        for i in range(5):
            u1 = self.create_mock_unit(f"p1_u{i}", "Tank", "天庭", ["金"], 1, hp=5000, atk=1) # High HP, Low Atk = Long battle
            u2 = self.create_mock_unit(f"p2_u{i}", "Tank", "天庭", ["金"], 1, hp=5000, atk=1)
            p1.board_units.append(u1)
            p2.board_units.append(u2)

        self.game.phase = GamePhase.PREPARATION
        self.game.phase_start_time = time.time() - 31 # Trigger battle

        start_time = time.time()
        self.game.update_game_state()
        duration = time.time() - start_time

        print(f"Long Battle Duration: {duration:.4f}s")
        # If duration is > 0.1s, it might be noticeable.
        # With 30 rounds max, it might still be fast in Python, but it IS blocking.

        self.assertEqual(self.game.phase, GamePhase.BATTLE)

if __name__ == '__main__':
    unittest.main()

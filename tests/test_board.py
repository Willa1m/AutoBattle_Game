
import unittest
import sys
import os
from unittest.mock import Mock, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.board import Board, BoardType, Position, CellType, BoardCell
from core.unit import Unit, Stats

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board(BoardType.BATTLE)
        self.mock_unit = Mock(spec=Unit)
        self.mock_unit.id = "unit_1"
        self.mock_unit.name = "Test Unit"
        self.mock_unit.is_alive.return_value = True

    def test_initialization(self):
        """Test board initialization for different types."""
        battle_board = Board(BoardType.BATTLE)
        self.assertEqual(battle_board.width, 8)
        self.assertEqual(battle_board.height, 8)
        self.assertEqual(len(battle_board.cells), 64)

        prep_board = Board(BoardType.PREPARATION)
        self.assertEqual(prep_board.width, 8)
        self.assertEqual(prep_board.height, 4)
        self.assertEqual(len(prep_board.cells), 32)

    def test_position_utilities(self):
        """Test Position class methods."""
        p1 = Position(0, 0)
        p2 = Position(3, 4)

        # Test equality
        self.assertEqual(p1, Position(0, 0))
        self.assertNotEqual(p1, p2)

        # Test distance
        self.assertEqual(p1.distance_to(p2), 5.0)  # sqrt(3^2 + 4^2) = 5
        self.assertEqual(p1.manhattan_distance_to(p2), 7) # 3 + 4 = 7

    def test_is_valid_position(self):
        """Test boundary checks."""
        self.assertTrue(self.board.is_valid_position(Position(0, 0)))
        self.assertTrue(self.board.is_valid_position(Position(7, 7)))
        self.assertFalse(self.board.is_valid_position(Position(-1, 0)))
        self.assertFalse(self.board.is_valid_position(Position(0, 8)))

    def test_place_unit(self):
        """Test placing units on the board."""
        pos = Position(1, 1)

        # Valid placement
        self.assertTrue(self.board.place_unit(self.mock_unit, pos))
        self.assertEqual(self.board.get_unit_at(pos), self.mock_unit)
        self.assertEqual(self.board.get_unit_position(self.mock_unit.id), pos)

        # Placement on occupied cell
        unit2 = Mock(spec=Unit)
        unit2.id = "unit_2"
        self.assertFalse(self.board.place_unit(unit2, pos))

        # Placement out of bounds
        self.assertFalse(self.board.place_unit(unit2, Position(10, 10)))

        # Move unit by placing again (should remove from old)
        new_pos = Position(2, 2)
        self.assertTrue(self.board.place_unit(self.mock_unit, new_pos))
        self.assertIsNone(self.board.get_unit_at(pos))
        self.assertEqual(self.board.get_unit_at(new_pos), self.mock_unit)

    def test_remove_unit(self):
        """Test removing units."""
        pos = Position(1, 1)
        self.board.place_unit(self.mock_unit, pos)

        # Valid removal
        self.assertTrue(self.board.remove_unit(self.mock_unit.id))
        self.assertIsNone(self.board.get_unit_at(pos))

        # Remove non-existent
        self.assertFalse(self.board.remove_unit("non_existent"))

    def test_move_unit(self):
        """Test moving units."""
        p1 = Position(1, 1)
        p2 = Position(2, 2)
        self.board.place_unit(self.mock_unit, p1)

        # Valid move
        self.assertTrue(self.board.move_unit(self.mock_unit.id, p2))
        self.assertIsNone(self.board.get_unit_at(p1))
        self.assertEqual(self.board.get_unit_at(p2), self.mock_unit)

        # Move to occupied
        unit2 = Mock(spec=Unit)
        unit2.id = "unit_2"
        self.board.place_unit(unit2, p1)
        self.assertFalse(self.board.move_unit(self.mock_unit.id, p1))

        # Move non-existent unit
        self.assertFalse(self.board.move_unit("bad_id", p1))

    def test_get_adjacent_positions(self):
        """Test getting adjacent positions."""
        center = Position(1, 1)
        adj = self.board.get_adjacent_positions(center, include_diagonal=True)
        # Should be 8 neighbors
        self.assertEqual(len(adj), 8)

        adj_no_diag = self.board.get_adjacent_positions(center, include_diagonal=False)
        # Should be 4 neighbors
        self.assertEqual(len(adj_no_diag), 4)

        # Corner case
        corner = Position(0, 0)
        adj_corner = self.board.get_adjacent_positions(corner)
        self.assertEqual(len(adj_corner), 3)

    def test_find_nearest_enemy(self):
        """Test finding nearest enemy."""
        u1 = Mock(spec=Unit)
        u1.id = "u1"
        u1.is_alive.return_value = True

        u2 = Mock(spec=Unit) # Enemy
        u2.id = "u2"
        u2.is_alive.return_value = True

        u3 = Mock(spec=Unit) # Enemy further away
        u3.id = "u3"
        u3.is_alive.return_value = True

        self.board.place_unit(u1, Position(0, 0))
        self.board.place_unit(u2, Position(0, 2)) # Dist 2
        self.board.place_unit(u3, Position(0, 5)) # Dist 5

        enemy, pos = self.board.find_nearest_enemy(u1)
        self.assertEqual(enemy.id, "u2")
        self.assertEqual(pos, Position(0, 2))

        # Test with no enemies
        self.board.remove_unit("u2")
        self.board.remove_unit("u3")
        self.assertIsNone(self.board.find_nearest_enemy(u1))

    def test_get_valid_moves(self):
        """Test calculating valid moves."""
        self.board.place_unit(self.mock_unit, Position(1, 1))

        # Block one spot
        u2 = Mock(spec=Unit)
        u2.id = "u2"
        self.board.place_unit(u2, Position(1, 2))

        moves = self.board.get_valid_moves(self.mock_unit.id, max_distance=1)

        # Logic uses manhattan distance.
        # Max distance 1 means |dx| + |dy| <= 1.
        # Neighbors of (1,1): (1,0), (0,1), (2,1), (1,2)
        # (1,2) is blocked.
        # Diagonals like (0,0) have dist |1-0| + |1-0| = 2, so excluded.

        move_set = set((m.x, m.y) for m in moves)
        expected = {
            (1,0), (0,1), (2,1)
        }

        self.assertEqual(move_set, expected)

    def test_find_path(self):
        """Test pathfinding."""
        start = Position(0, 0)
        end = Position(0, 3)
        path = self.board.find_path(start, end)

        # Simple straight line path
        expected = [Position(0, 1), Position(0, 2), Position(0, 3)]
        self.assertEqual(path, expected)

        # Invalid start/end
        self.assertEqual(self.board.find_path(Position(-1,0), end), [])

    def test_serialization(self):
        """Test save/load board state."""
        # Use a real unit for this to ensure correct serialization behavior
        stats = Stats(100, 10, 5, 1.0, 1, 0, 0, 0)
        # Use a unit WITHOUT active skill initially to test None handling
        real_unit = Unit("u1", "Real Unit", "Human", ["Warrior"], 1, stats)

        self.board.place_unit(real_unit, Position(3, 3))

        state = self.board.get_board_state()
        self.assertEqual(state['width'], 8)
        self.assertIn('u1', state['units'])

        # Create new board and load
        new_board = Board(BoardType.BATTLE)
        new_board.load_board_state(state)

        loaded_unit = new_board.get_unit_at(Position(3, 3))
        self.assertIsNotNone(loaded_unit)
        self.assertEqual(loaded_unit.id, "u1")
        self.assertEqual(loaded_unit.name, "Real Unit")

if __name__ == '__main__':
    unittest.main()


import unittest
import sys
import os
from unittest.mock import Mock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.synergy import SynergyManager, SynergyEffect, SynergyLevel, SynergyType
from core.unit import Unit

class TestSynergy(unittest.TestCase):
    def setUp(self):
        self.manager = SynergyManager()

    def create_mock_unit(self, faction, classes, alive=True):
        unit = Mock(spec=Unit)
        unit.faction = faction
        unit.classes = classes
        unit.is_alive.return_value = alive
        # Mock methods needed for application
        unit.buffs = {}
        return unit

    def test_count_units(self):
        """Test counting units by faction and class."""
        units = [
            self.create_mock_unit("天庭", ["金"]),
            self.create_mock_unit("天庭", ["木"]),
            self.create_mock_unit("佛门", ["金"]),
            self.create_mock_unit("天庭", ["金"], alive=False) # Dead unit
        ]

        f_counts = self.manager.count_units_by_faction(units)
        self.assertEqual(f_counts.get("天庭", 0), 2) # 2 alive
        self.assertEqual(f_counts.get("佛门", 0), 1)

        c_counts = self.manager.count_units_by_class(units)
        self.assertEqual(c_counts.get("金", 0), 2) # 2 alive (1 Tianting, 1 Fomen)
        self.assertEqual(c_counts.get("木", 0), 1)

    def test_get_active_synergies(self):
        """Test detecting active synergies based on counts."""
        # Need 2 Tianting for first level
        units = [
            self.create_mock_unit("天庭", ["金"]),
            self.create_mock_unit("天庭", ["木"]),
        ]

        active = self.manager.get_active_faction_synergies(units)
        self.assertIn("天庭", active)
        self.assertEqual(len(active["天庭"]), 1)
        self.assertEqual(active["天庭"][0].name, "天威")

        # Need 4 Tianting for second level
        units.extend([
            self.create_mock_unit("天庭", ["水"]),
            self.create_mock_unit("天庭", ["火"]),
        ])
        active = self.manager.get_active_faction_synergies(units)
        self.assertEqual(len(active["天庭"]), 2) # Level 1 and Level 2

        # Test class synergies
        # Need 2 Metal (金)
        units = [
            self.create_mock_unit("天庭", ["金"]),
            self.create_mock_unit("佛门", ["金"]),
        ]
        active_class = self.manager.get_active_class_synergies(units)
        self.assertIn("金", active_class)
        self.assertEqual(len(active_class["金"]), 1)

    def test_synergy_application(self):
        """Test applying stats to a unit."""
        # 2 Tianting units -> +15% Def
        u1 = self.create_mock_unit("天庭", ["金"])
        u2 = self.create_mock_unit("天庭", ["木"])
        units = [u1, u2]

        # apply_synergies_to_unit returns a dict of bonuses
        bonuses = self.manager.apply_synergies_to_unit(u1, units)
        self.assertIn("def", bonuses)
        self.assertAlmostEqual(bonuses["def"], 0.15)

        # Verify u2 also gets it
        bonuses2 = self.manager.apply_synergies_to_unit(u2, units)
        self.assertAlmostEqual(bonuses2["def"], 0.15)

        # Add class synergy: 2 Metal -> +25% Def (Actual effect in synergy.py)
        u3 = self.create_mock_unit("佛门", ["金"])
        units.append(u3)

        # u1 is Metal, so should get Faction bonus (15% Def) + Class bonus (25% Def)
        bonuses_u1 = self.manager.apply_synergies_to_unit(u1, units)
        self.assertIn("def", bonuses_u1)
        # Total defense bonus should be 0.15 + 0.25 = 0.40
        self.assertAlmostEqual(bonuses_u1["def"], 0.40)

    def test_synergy_info(self):
        """Test getting synergy info for UI."""
        units = [self.create_mock_unit("天庭", ["金"], alive=True)]
        # 1 unit -> no synergies
        info = self.manager.get_synergy_info(units)
        self.assertEqual(info["faction_counts"]["天庭"], 1)
        self.assertEqual(len(info["active_faction_synergies"]), 0)

        # Add another to activate
        units.append(self.create_mock_unit("天庭", ["木"], alive=True))
        info = self.manager.get_synergy_info(units)
        self.assertEqual(info["faction_counts"]["天庭"], 2)
        self.assertIn("天庭", info["active_faction_synergies"])

if __name__ == '__main__':
    unittest.main()

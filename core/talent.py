
from dataclasses import dataclass
from typing import List, Dict, Optional
import random

@dataclass
class Talent:
    id: str
    name: str
    description: str
    level: int  # 1-5
    effect_type: str  # "stat_bonus", "gold_bonus", "special"
    effect_data: Dict

class TalentManager:
    def __init__(self):
        self.talents: Dict[int, List[Talent]] = {}
        self._initialize_talents()

    def _initialize_talents(self):
        # Level 1 Talents
        self.talents[1] = [
            Talent("t1_hp", "Vitality I", "All units +50 HP", 1, "stat_bonus", {"hp": 50}),
            Talent("t1_gold", "Wealth I", "Gain 1 gold per round", 1, "gold_bonus", {"gold_per_round": 1}),
            Talent("t1_atk", "Strength I", "All units +5 Attack", 1, "stat_bonus", {"atk": 5})
        ]

        # Level 2 Talents
        self.talents[2] = [
            Talent("t2_hp", "Vitality II", "All units +100 HP", 2, "stat_bonus", {"hp": 100}),
            Talent("t2_def", "Defense I", "All units +10 Defense", 2, "stat_bonus", {"def": 10}),
            Talent("t2_xp", "Fast Learner", "Gain 1 extra XP per round", 2, "xp_bonus", {"xp_per_round": 1})
        ]

        # Level 3 Talents
        self.talents[3] = [
            Talent("t3_crit", "Precision I", "All units +10% Crit Chance", 3, "stat_bonus", {"crit": 0.1}),
            Talent("t3_mana", "Focus I", "All units start with 20 Mana", 3, "stat_bonus", {"start_mana": 20}),
            Talent("t3_eco", "Interest", "Max interest cap increased by 2", 3, "gold_bonus", {"interest_cap": 2})
        ]

        # Level 4 Talents
        self.talents[4] = [
            Talent("t4_lifesteal", "Vampirism", "All units +15% Lifesteal", 4, "stat_bonus", {"lifesteal": 0.15}),
            Talent("t4_size", "Recruiter", "Max army size +1", 4, "special", {"max_units": 1}),
            Talent("t4_shop", "VIP", "Shop offers higher tier units earlier", 4, "special", {"shop_tier_bonus": 1})
        ]

        # Level 5 Talents
        self.talents[5] = [
            Talent("t5_revive", "Guardian Angel", "First unit to die revives with 50% HP", 5, "special", {"revive": True}),
            Talent("t5_divine", "Divine Power", "All units +20% All Stats", 5, "stat_bonus", {"all_stats_multiplier": 1.2}),
            Talent("t5_rich", "Tycoon", "Gain 50 Gold instantly", 5, "instant_gold", {"amount": 50})
        ]

    def get_talent_choices(self, population_level: int) -> List[Talent]:
        """
        Get 3 random talents based on population level.
        Higher population = higher probability of high level talents.
        Requirement: Last 3 upgrades (pop 7, 8, 9) will not yield talents below level 3.
        """
        available_levels = []
        weights = []

        if population_level <= 4:
            available_levels = [1, 2]
            weights = [0.7, 0.3]
        elif population_level <= 6:
            available_levels = [1, 2, 3, 4]
            weights = [0.2, 0.3, 0.4, 0.1]
        elif population_level >= 7:
             # Requirement: No talents below level 3 for last 3 upgrades (implying pop 7, 8, 9)
            available_levels = [3, 4, 5]
            weights = [0.3, 0.4, 0.3]

        choices = []
        for _ in range(3):
            # Pick a level
            level = random.choices(available_levels, weights=weights)[0]
            # Pick a talent from that level
            if level in self.talents:
                talent = random.choice(self.talents[level])
                choices.append(talent)

        return choices

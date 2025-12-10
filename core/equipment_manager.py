
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import random
from .unit import Equipment

@dataclass
class EquipmentDrop:
    type: str # "offensive", "defensive", "utility", "faction", "class"
    star: int # 1, 2, 3
    equipment: Equipment

class EquipmentManager:
    def __init__(self):
        self.equipment_pool: Dict[str, List[Equipment]] = {}
        self._initialize_equipment()

    def _initialize_equipment(self):
        # Initialize pools
        for type_ in ["offensive", "defensive", "utility"]:
            self.equipment_pool[type_] = []

        # Offensive
        self.equipment_pool["offensive"].append(Equipment("Iron Sword", "attack", 1, {"atk_bonus": 15}))
        self.equipment_pool["offensive"].append(Equipment("Steel Lance", "attack", 2, {"atk_bonus": 30, "crit_bonus": 0.1}))
        self.equipment_pool["offensive"].append(Equipment("Dragon Slayer", "attack", 3, {"atk_bonus": 60, "crit_bonus": 0.25}))

        # Defensive
        self.equipment_pool["defensive"].append(Equipment("Leather Armor", "defense", 1, {"hp_bonus": 100}))
        self.equipment_pool["defensive"].append(Equipment("Chainmail", "defense", 2, {"hp_bonus": 250, "def_bonus": 20}))
        self.equipment_pool["defensive"].append(Equipment("Divine Shield", "defense", 3, {"hp_bonus": 600, "def_bonus": 50}))

        # Utility (Faction/Class) - Will be generated dynamically usually, but keeping templates
        # Note: Requirement 3 says Utility is limited to Faction/Class equipment
        pass

    def generate_faction_equipment(self, faction: str, star: int) -> Equipment:
        return Equipment(f"{faction} Emblem", "utility", star, {"faction_change": faction})

    def generate_class_equipment(self, class_name: str, star: int) -> Equipment:
        return Equipment(f"{class_name} Seal", "utility", star, {"class_change": class_name})

    def get_monster_round_rewards(self, round_num: int) -> List[List[Equipment]]:
        """
        Generate equipment choices based on Requirement 4a.
        Returns a list of choices (e.g., [[Choice1, Choice2, Choice3], [Choice1...]])
        """
        choices_list = []

        # Mapping rounds to "Waves" (1st, 2nd, 3rd, 4th+)
        # Assuming every 5 rounds is a monster round: 5, 10, 15, 20...
        wave = round_num // 5

        if wave == 1: # Round 5 - Weak, Two 3-choice options, No faction/class. 1-2 star.
            for _ in range(2):
                choices_list.append(self._generate_choices(3, min_star=1, max_star=2, allow_special=False))

        elif wave == 2: # Round 10 - Harder, Three 3-choice options. 1 Faction choice. High 2-star prob.
            # 2 standard choices
            for _ in range(2):
                choices_list.append(self._generate_choices(3, min_star=1, max_star=2, high_star_prob=True, allow_special=False))
            # 1 Faction choice
            choices_list.append(self._generate_special_choices(3, "faction", star=2))

        elif wave == 3: # Round 15 - Three 3-choice. 1 Class choice. Only 2-star.
            # 2 standard choices
            for _ in range(2):
                choices_list.append(self._generate_choices(3, min_star=2, max_star=2, allow_special=False))
            # 1 Class choice
            choices_list.append(self._generate_special_choices(3, "class", star=2))

        elif wave >= 4: # Round 20+ - Two 3-choice. 3-star.
             for _ in range(2):
                choices_list.append(self._generate_choices(3, min_star=3, max_star=3, allow_special=False))

        return choices_list

    def _generate_choices(self, count: int, min_star: int, max_star: int, high_star_prob: bool = False, allow_special: bool = False) -> List[Equipment]:
        choices = []
        for _ in range(count):
            # Determine star
            star = min_star
            if max_star > min_star:
                prob_high = 0.7 if high_star_prob else 0.3
                if random.random() < prob_high:
                    star = max_star

            # Determine type (Off/Def)
            type_ = random.choice(["offensive", "defensive"])
            # Find matching equipment in pool (simplified, usually would filter by star)
            candidates = [e for e in self.equipment_pool[type_] if e.star == star]
            if candidates:
                choices.append(random.choice(candidates))
            else:
                # Fallback
                choices.append(Equipment("Fallback Item", "utility", star, {}))
        return choices

    def _generate_special_choices(self, count: int, type_: str, star: int) -> List[Equipment]:
        choices = []
        factions = ["天庭", "地狱", "人界", "仙界", "妖界", "神兽"]
        classes = ["金", "木", "水", "火", "土", "黑暗", "光明"]

        for _ in range(count):
            if type_ == "faction":
                target = random.choice(factions)
                choices.append(self.generate_faction_equipment(target, star))
            else: # class
                target = random.choice(classes)
                choices.append(self.generate_class_equipment(target, star))
        return choices

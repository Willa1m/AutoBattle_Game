# -*- coding: utf-8 -*-
"""
ClassAttrManager：职业属性系统
- 元素职业：金、木、水、火、土、黑暗、光明
- 2-5同职业：本职业获得效果；>5：全队获得增强效果
"""
from typing import List, Dict
from .unit import Unit

CLASS_SYNERGIES: Dict[str, Dict[str, List[tuple]]] = {
    "金": {
        "self": [(2, {"pierce_bonus": 0.10}), (5, {"pierce_bonus": 0.10})],
        "global": [(6, {"pierce_bonus": 0.20})]
    },
    "木": {
        "self": [(2, {"heal_regen": 0.05}), (5, {"heal_regen": 0.05})],
        "global": [(6, {"heal_regen": 0.10})]
    },
    "水": {
        "self": [(2, {"enemy_as_down": 0.10}), (5, {"enemy_as_down": 0.10})],
        "global": [(6, {"enemy_as_down": 0.20})]
    },
    "火": {
        "self": [(2, {"burn_per_turn": 0.05}), (5, {"burn_per_turn": 0.05})],
        "global": [(6, {"burn_per_turn": 0.10})]
    },
    "土": {
        "self": [(2, {"max_hp_bonus": 0.15}), (5, {"max_hp_bonus": 0.15})],
        "global": [(6, {"max_hp_bonus": 0.30})]
    },
    "黑暗": {
        "self": [(2, {"lifesteal": 0.10}), (5, {"lifesteal": 0.10})],
        "global": [(6, {"lifesteal": 0.20})]
    },
    "光明": {
        "self": [(2, {"cleanse_chance": 0.20}), (5, {"cleanse_chance": 0.20})],
        "global": [(6, {"cleanse_chance": 0.40})]
    }
}

class ClassAttrManager:
    def compute(self, units: List[Unit]) -> Dict[str, Dict[str, float]]:
        """计算职业属性效果，返回全队总效果（global_effects）和分职业效果（class_effects）"""
        class_counts: Dict[str, int] = {}
        for u in units:
            for c in u.classes:
                class_counts[c] = class_counts.get(c, 0) + 1
        class_effects: Dict[str, Dict[str, float]] = {}
        global_effects: Dict[str, float] = {}
        for cls, count in class_counts.items():
            conf = CLASS_SYNERGIES.get(cls, {})
            best_self: Dict[str, float] = {}
            for threshold, effect in conf.get("self", []):
                if 2 <= count <= 5 and count >= threshold:
                    best_self = effect
            if best_self:
                class_effects[cls] = best_self
            for threshold, effect in conf.get("global", []):
                if count >= threshold:
                    for k, v in effect.items():
                        global_effects[k] = max(global_effects.get(k, 0.0), v)
        return {"class_effects": class_effects, "global_effects": global_effects}

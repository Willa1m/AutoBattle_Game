# -*- coding: utf-8 -*-
"""
SynergyManager：阵营羁绊系统
- 根据队伍中的阵营数量，激活阈值羁绊效果（3/5人）
- 返回每个阵营对应的效果字典
"""
from typing import List, Dict
from .unit import Unit

FACTION_SYNERGIES: Dict[str, List[tuple]] = {
    "天庭": [(3, {"true_damage_bonus": 0.20}), (5, {"true_damage_bonus": 0.40})],
    "地狱": [(3, {"enemy_heal_reduction": 0.20}), (5, {"enemy_heal_reduction": 0.40})],
    "人界": [(3, {"crit_rate_bonus": 0.10}), (5, {"crit_rate_bonus": 0.20})],
    "仙界": [(3, {"mana_regen_bonus": 0.15}), (5, {"mana_regen_bonus": 0.30})],
    "妖界": [(3, {"chaos_damage_bonus": 0.10}), (5, {"chaos_damage_bonus": 0.20})],
    "神兽": [(3, {"dodge_bonus": 0.15}), (5, {"dodge_bonus": 0.30})],
}

class SynergyManager:
    def compute(self, units: List[Unit]) -> Dict[str, Dict[str, float]]:
        """计算队伍阵营羁绊效果，若满足多个阈值，返回最高档效果"""
        counts: Dict[str, int] = {}
        for u in units:
            counts[u.faction] = counts.get(u.faction, 0) + 1
        bonuses: Dict[str, Dict[str, float]] = {}
        for faction, count in counts.items():
            thresholds = FACTION_SYNERGIES.get(faction, [])
            best: Dict[str, float] = {}
            for threshold, effect in thresholds:
                if count >= threshold:
                    best = effect
            if best:
                bonuses[faction] = best
        return bonuses

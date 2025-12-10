"""
天界之战 - 协同效果系统
Synergy System for Battle of the Heavens

负责管理阵营协同和职业协同效果
Manages faction and class synergy effects

6大阵营：天庭、佛门、道教、妖族、地府、人间
7大职业：金、木、水、火、土、光、暗

测试方式：控制台unittest
Testing: Console unittest
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json

try:
    from .unit import Unit
except ImportError:
    # 直接运行时的导入方式
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.unit import Unit


class SynergyType(Enum):
    """协同类型"""
    FACTION = "faction"    # 阵营协同
    CLASS = "class"        # 职业协同


@dataclass
class SynergyEffect:
    """协同效果"""
    name: str                    # 效果名称
    description: str             # 效果描述
    stat_bonuses: Dict[str, float]  # 属性加成 {"hp": 0.2, "atk": 0.15}
    special_effects: List[str]   # 特殊效果列表
    required_count: int          # 需要的单位数量
    
    def apply_to_unit(self, unit: Unit) -> Dict[str, float]:
        """将协同效果应用到单位"""
        applied_bonuses = {}
        
        # 应用属性加成
        for stat, bonus in self.stat_bonuses.items():
            if stat in ["hp", "atk", "def", "spd", "rng", "mana", "crit", "dodge", "true_damage_bonus"]:
                applied_bonuses[stat] = bonus
        
        return applied_bonuses


@dataclass
class SynergyLevel:
    """协同等级"""
    count: int                   # 单位数量
    effect: SynergyEffect        # 对应效果
    
    def is_active(self, unit_count: int) -> bool:
        """检查协同是否激活"""
        return unit_count >= self.count


class SynergyManager:
    """协同效果管理器"""
    
    def __init__(self):
        self.faction_synergies: Dict[str, List[SynergyLevel]] = {}
        self.class_synergies: Dict[str, List[SynergyLevel]] = {}
        self._initialize_synergies()
    
    def _initialize_synergies(self):
        """初始化协同效果数据"""
        
        # 阵营协同效果
        self.faction_synergies = {
            "天庭": [
                SynergyLevel(3, SynergyEffect(
                    "天威", "天庭单位获得真实伤害加成 (Requirement 2)",
                    {"true_damage_bonus": 0.20}, ["true_strike"], 3
                )),
                SynergyLevel(5, SynergyEffect(
                    "九天神威", "天庭单位获得更强真实伤害 (Requirement 2)",
                    {"true_damage_bonus": 0.40}, ["true_strike_greater"], 5
                ))
            ],
            
            "佛门": [
                SynergyLevel(2, SynergyEffect(
                    "慈悲", "佛门单位获得生命值加成",
                    {"hp": 0.20}, ["compassion"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "金刚不坏", "佛门单位获得防御和魔法抗性",
                    {"def": 0.30, "hp": 0.25}, ["diamond_body"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "佛光普照", "佛门单位获得治疗和净化能力",
                    {"hp": 0.40, "mana": 0.25}, ["buddha_light"], 6
                ))
            ],
            
            "道教": [
                SynergyLevel(2, SynergyEffect(
                    "道法自然", "道教单位获得法力加成",
                    {"mana": 0.25}, ["natural_way"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "五行相生", "道教单位获得元素抗性",
                    {"def": 0.20, "mana": 0.30}, ["five_elements"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "太极阴阳", "道教单位获得平衡之力",
                    {"hp": 0.25, "atk": 0.25, "mana": 0.35}, ["taiji_power"], 6
                ))
            ],
            
            "妖族": [
                SynergyLevel(2, SynergyEffect(
                    "野性", "妖族单位获得攻击速度加成",
                    {"spd": 0.20, "atk": 0.10}, ["wildness"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "妖力觉醒", "妖族单位获得暴击加成",
                    {"crit": 0.15, "atk": 0.25}, ["demon_awakening"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "妖王之威", "妖族单位获得强大的攻击力",
                    {"atk": 0.40, "crit": 0.25, "spd": 0.30}, ["demon_king_might"], 6
                ))
            ],
            
            "地府": [
                SynergyLevel(2, SynergyEffect(
                    "阴气", "地府单位获得闪避加成",
                    {"dodge": 0.10}, ["yin_energy"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "鬼魅", "地府单位获得穿透和闪避",
                    {"atk": 0.15, "dodge": 0.20}, ["ghostly"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "冥王统御", "地府单位获得死亡抗性和强力攻击",
                    {"hp": 0.25, "atk": 0.35, "dodge": 0.25}, ["hades_rule"], 6
                ))
            ],
            
            "人间": [
                SynergyLevel(2, SynergyEffect(
                    "凡人智慧", "人间单位获得经验加成",
                    {"mana": 0.15}, ["mortal_wisdom"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "人定胜天", "人间单位获得全面小幅加成",
                    {"hp": 0.15, "atk": 0.15, "def": 0.15}, ["human_determination"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "众志成城", "人间单位获得团队协作加成",
                    {"hp": 0.30, "atk": 0.25, "def": 0.25, "spd": 0.20}, ["unity_strength"], 6
                ))
            ]
        }
        
        # 职业协同效果
        self.class_synergies = {
            "金": [
                SynergyLevel(2, SynergyEffect(
                    "金刚", "金系单位获得防御加成",
                    {"def": 0.25}, ["metal_defense"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "锋锐", "金系单位获得攻击穿透",
                    {"atk": 0.20, "def": 0.30}, ["sharp_edge"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "金刚不坏", "金系单位获得极强防御",
                    {"def": 0.50, "hp": 0.25}, ["indestructible"], 6
                ))
            ],
            
            "木": [
                SynergyLevel(2, SynergyEffect(
                    "生机", "木系单位获得生命恢复",
                    {"hp": 0.20}, ["vitality"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "繁茂", "木系单位获得持续治疗",
                    {"hp": 0.30, "mana": 0.15}, ["flourishing"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "生生不息", "木系单位获得强大恢复能力",
                    {"hp": 0.45, "mana": 0.25}, ["endless_life"], 6
                ))
            ],
            
            "水": [
                SynergyLevel(2, SynergyEffect(
                    "流动", "水系单位获得速度加成",
                    {"spd": 0.25}, ["flowing"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "波涛", "水系单位获得范围攻击",
                    {"rng": 1, "spd": 0.30}, ["waves"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "汪洋", "水系单位获得大范围控制",
                    {"rng": 2, "spd": 0.40, "mana": 0.20}, ["ocean"], 6
                ))
            ],
            
            "火": [
                SynergyLevel(2, SynergyEffect(
                    "燃烧", "火系单位获得攻击加成",
                    {"atk": 0.25}, ["burning"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "烈焰", "火系单位获得暴击加成",
                    {"atk": 0.35, "crit": 0.15}, ["blazing"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "业火", "火系单位获得极强攻击力",
                    {"atk": 0.50, "crit": 0.25}, ["hellfire"], 6
                ))
            ],
            
            "土": [
                SynergyLevel(2, SynergyEffect(
                    "厚重", "土系单位获得生命值加成",
                    {"hp": 0.25}, ["solid"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "坚固", "土系单位获得防御和生命加成",
                    {"hp": 0.35, "def": 0.20}, ["sturdy"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "大地", "土系单位获得极强生存能力",
                    {"hp": 0.50, "def": 0.35}, ["earth_power"], 6
                ))
            ],
            
            "光": [
                SynergyLevel(2, SynergyEffect(
                    "圣光", "光系单位获得治疗能力",
                    {"mana": 0.20}, ["holy_light"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "净化", "光系单位获得净化和治疗",
                    {"mana": 0.30, "hp": 0.20}, ["purification"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "神圣", "光系单位获得神圣力量",
                    {"hp": 0.30, "atk": 0.25, "mana": 0.35}, ["divine"], 6
                ))
            ],
            
            "暗": [
                SynergyLevel(2, SynergyEffect(
                    "阴影", "暗系单位获得闪避加成",
                    {"dodge": 0.15}, ["shadow"], 2
                )),
                SynergyLevel(4, SynergyEffect(
                    "诅咒", "暗系单位获得减益能力",
                    {"atk": 0.20, "dodge": 0.20}, ["curse"], 4
                )),
                SynergyLevel(6, SynergyEffect(
                    "深渊", "暗系单位获得强大的暗黑力量",
                    {"atk": 0.35, "dodge": 0.30, "crit": 0.20}, ["abyss"], 6
                ))
            ]
        }
    
    def count_units_by_faction(self, units: List[Unit]) -> Dict[str, int]:
        """统计各阵营的单位数量"""
        faction_counts = {}
        for unit in units:
            if unit.is_alive():
                faction = unit.faction
                faction_counts[faction] = faction_counts.get(faction, 0) + 1
        return faction_counts
    
    def count_units_by_class(self, units: List[Unit]) -> Dict[str, int]:
        """统计各职业的单位数量"""
        class_counts = {}
        for unit in units:
            if unit.is_alive():
                for unit_class in unit.classes:
                    class_counts[unit_class] = class_counts.get(unit_class, 0) + 1
        return class_counts
    
    def get_active_faction_synergies(self, units: List[Unit]) -> Dict[str, List[SynergyEffect]]:
        """获取激活的阵营协同效果"""
        faction_counts = self.count_units_by_faction(units)
        active_synergies = {}
        
        for faction, count in faction_counts.items():
            if faction in self.faction_synergies:
                active_effects = []
                for synergy_level in self.faction_synergies[faction]:
                    if synergy_level.is_active(count):
                        active_effects.append(synergy_level.effect)
                
                if active_effects:
                    active_synergies[faction] = active_effects
        
        return active_synergies
    
    def get_active_class_synergies(self, units: List[Unit]) -> Dict[str, List[SynergyEffect]]:
        """获取激活的职业协同效果"""
        class_counts = self.count_units_by_class(units)
        active_synergies = {}
        
        for unit_class, count in class_counts.items():
            if unit_class in self.class_synergies:
                active_effects = []
                for synergy_level in self.class_synergies[unit_class]:
                    if synergy_level.is_active(count):
                        active_effects.append(synergy_level.effect)
                
                if active_effects:
                    active_synergies[unit_class] = active_effects
        
        return active_synergies
    
    def apply_synergies_to_unit(self, unit: Unit, all_units: List[Unit]) -> Dict[str, float]:
        """为单位应用所有适用的协同效果"""
        total_bonuses = {}
        
        # 获取激活的协同效果
        faction_synergies = self.get_active_faction_synergies(all_units)
        class_synergies = self.get_active_class_synergies(all_units)
        
        # 应用阵营协同
        if unit.faction in faction_synergies:
            for effect in faction_synergies[unit.faction]:
                bonuses = effect.apply_to_unit(unit)
                for stat, bonus in bonuses.items():
                    total_bonuses[stat] = total_bonuses.get(stat, 0) + bonus
        
        # 应用职业协同
        for unit_class in unit.classes:
            if unit_class in class_synergies:
                for effect in class_synergies[unit_class]:
                    bonuses = effect.apply_to_unit(unit)
                    for stat, bonus in bonuses.items():
                        total_bonuses[stat] = total_bonuses.get(stat, 0) + bonus
        
        return total_bonuses
    
    def get_synergy_info(self, units: List[Unit]) -> Dict:
        """获取协同效果信息（用于UI显示）"""
        faction_counts = self.count_units_by_faction(units)
        class_counts = self.count_units_by_class(units)
        
        faction_synergies = self.get_active_faction_synergies(units)
        class_synergies = self.get_active_class_synergies(units)
        
        return {
            "faction_counts": faction_counts,
            "class_counts": class_counts,
            "active_faction_synergies": {
                faction: [effect.name for effect in effects]
                for faction, effects in faction_synergies.items()
            },
            "active_class_synergies": {
                unit_class: [effect.name for effect in effects]
                for unit_class, effects in class_synergies.items()
            }
        }
    
    def get_synergy_requirements(self) -> Dict:
        """获取所有协同效果的需求（用于UI显示）"""
        return {
            "factions": {
                faction: [
                    {
                        "count": level.count,
                        "name": level.effect.name,
                        "description": level.effect.description
                    }
                    for level in levels
                ]
                for faction, levels in self.faction_synergies.items()
            },
            "classes": {
                unit_class: [
                    {
                        "count": level.count,
                        "name": level.effect.name,
                        "description": level.effect.description
                    }
                    for level in levels
                ]
                for unit_class, levels in self.class_synergies.items()
            }
        }


def run_synergy_test():
    """运行协同效果系统测试"""
    print("🔮 开始协同效果系统测试...")
    
    # 创建协同管理器
    synergy_manager = SynergyManager()
    print("创建协同效果管理器")
    
    # 加载单位数据进行测试
    try:
        with open('data/celestial_units.json', 'r', encoding='utf-8') as f:
            units_data = json.load(f)
        
        # 创建测试单位组合
        test_units = []
        
        # 创建天庭阵营单位（测试阵营协同）
        tianting_units = [unit for unit in units_data["units"] if unit["faction"] == "天庭"][:3]
        for i, unit_data in enumerate(tianting_units):
            unit = Unit.from_json(unit_data)
            # unit_id不再需要，使用unit.id
            # player_id不再需要，Unit类没有这个属性
            test_units.append(unit)
        
        # 创建金系职业单位（测试职业协同）
        jin_units = [unit for unit in units_data["units"] if "金" in unit["classes"]][:3]
        for i, unit_data in enumerate(jin_units):
            unit = Unit.from_json(unit_data)
            # unit_id不再需要，使用unit.id
            # player_id不再需要，Unit类没有这个属性
            test_units.append(unit)
        
        print(f"创建了 {len(test_units)} 个测试单位")
        
        # 测试协同效果统计
        faction_counts = synergy_manager.count_units_by_faction(test_units)
        class_counts = synergy_manager.count_units_by_class(test_units)
        
        print(f"阵营统计: {faction_counts}")
        print(f"职业统计: {class_counts}")
        
        # 测试激活的协同效果
        active_faction_synergies = synergy_manager.get_active_faction_synergies(test_units)
        active_class_synergies = synergy_manager.get_active_class_synergies(test_units)
        
        print("\n激活的阵营协同:")
        for faction, effects in active_faction_synergies.items():
            print(f"  {faction}: {[effect.name for effect in effects]}")
        
        print("\n激活的职业协同:")
        for unit_class, effects in active_class_synergies.items():
            print(f"  {unit_class}: {[effect.name for effect in effects]}")
        
        # 测试单位协同效果应用
        if test_units:
            test_unit = test_units[0]
            bonuses = synergy_manager.apply_synergies_to_unit(test_unit, test_units)
            print(f"\n{test_unit.name} 获得的协同加成: {bonuses}")
        
        # 测试协同信息获取
        synergy_info = synergy_manager.get_synergy_info(test_units)
        print(f"\n协同效果信息: {synergy_info}")
        
        print("🎉 协同效果系统测试完成！")
        
    except FileNotFoundError:
        print("❌ 找不到单位数据文件，使用简单测试...")
        
        # 创建简单测试单位
        from core.unit import Stats
        
        # 创建天庭单位
        stats1 = Stats(hp=100, atk=50, def_=10, spd=5, rng=1, mana=0, crit=0.1, dodge=0.05)
        unit1 = Unit("tianting_001", "天兵1", "天庭", ["金"], 1, stats1)
        # unit_id不再需要，使用unit.id
        # player_id不再需要，Unit类没有这个属性
        
        unit2 = Unit("tianting_002", "天兵2", "天庭", ["金"], 1, stats1)
        # unit_id不再需要，使用unit.id
        # player_id不再需要，Unit类没有这个属性
        
        test_units = [unit1, unit2]
        
        # 测试基本功能
        faction_counts = synergy_manager.count_units_by_faction(test_units)
        print(f"阵营统计: {faction_counts}")
        
        active_synergies = synergy_manager.get_active_faction_synergies(test_units)
        print(f"激活的协同: {active_synergies}")
        
        print("🎉 简单协同测试完成！")


if __name__ == "__main__":
    run_synergy_test()
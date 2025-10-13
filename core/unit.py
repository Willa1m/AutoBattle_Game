# -*- coding: utf-8 -*-
"""
Unit类：天界之战棋子基础模型
- 支持星级升级（1/2/3星）
- 属性：生命、攻击、防御、攻速、射程、法力、暴击、闪避
- 羁绊：阵营（faction）、职业（classes）
- 技能系统：主动技能、被动技能
- 方法：升级、伤害计算、法力回复、技能释放

6大阵营：天庭、地狱、人界、仙界、妖界、神兽
7大职业：金、木、水、火、土、黑暗、光明

测试规范：仅通过控制台进行unittest测试
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import json

@dataclass
class Stats:
    """棋子属性数据类"""
    hp: int
    atk: int
    def_: int
    spd: float
    rng: int
    mana: int
    crit: float
    dodge: float

    def copy(self) -> "Stats":
        return Stats(self.hp, self.atk, self.def_, self.spd, self.rng, self.mana, self.crit, self.dodge)

@dataclass
class Skill:
    """技能数据类"""
    name: str
    description: str
    skill_type: str  # "active" 或 "passive"
    mana_cost: int = 0
    cooldown: int = 0
    effects: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Equipment:
    """装备数据类"""
    name: str
    item_type: str  # "defense", "attack", "function"
    star: int
    effects: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Unit:
    """天界之战棋子类"""
    id: str
    name: str
    faction: str  # 6大阵营：天庭、地狱、人界、仙界、妖界、神兽
    classes: List[str]  # 7大职业：金、木、水、火、土、黑暗、光明
    cost: int
    base_stats: Stats
    star: int = 1
    current_hp: int = field(init=False)
    current_mana: int = field(init=False)
    max_hp: int = field(init=False)
    
    # 技能系统
    active_skill: Optional[Skill] = None
    passive_skills: List[Skill] = field(default_factory=list)
    
    # 装备系统
    equipments: List[Equipment] = field(default_factory=list)
    
    # 状态效果
    buffs: Dict[str, Any] = field(default_factory=dict)
    debuffs: Dict[str, Any] = field(default_factory=dict)
    
    # 战斗状态
    skill_cooldown: int = 0
    position: tuple = (0, 0)

    def __post_init__(self):
        stats = self.get_stats()
        self.current_hp = stats.hp
        self.max_hp = stats.hp
        self.current_mana = 0

    def get_stats(self) -> Stats:
        """
        按星级返回当前属性，星级系数：1.0 / 1.8 / 3.24
        3星棋子属性大幅提升，符合自走棋平衡性
        """
        scale = 1.0 if self.star == 1 else 1.8 if self.star == 2 else 3.24
        s = self.base_stats.copy()
        s.hp = int(s.hp * scale)
        s.atk = int(s.atk * scale)
        s.def_ = int(s.def_ * scale)
        
        # 应用装备加成
        for equipment in self.equipments:
            s = self._apply_equipment_stats(s, equipment)
        
        # 应用buff加成
        s = self._apply_buff_stats(s)
        
        return s

    def _apply_equipment_stats(self, stats: Stats, equipment: Equipment) -> Stats:
        """应用装备属性加成"""
        effects = equipment.effects
        if "hp_bonus" in effects:
            stats.hp += effects["hp_bonus"]
        if "atk_bonus" in effects:
            stats.atk += effects["atk_bonus"]
        if "def_bonus" in effects:
            stats.def_ += effects["def_bonus"]
        if "crit_bonus" in effects:
            stats.crit += effects["crit_bonus"]
        if "dodge_bonus" in effects:
            stats.dodge += effects["dodge_bonus"]
        return stats

    def _apply_buff_stats(self, stats: Stats) -> Stats:
        """应用buff属性加成"""
        for buff_name, buff_data in self.buffs.items():
            if "hp_multiplier" in buff_data:
                stats.hp = int(stats.hp * buff_data["hp_multiplier"])
            if "atk_multiplier" in buff_data:
                stats.atk = int(stats.atk * buff_data["atk_multiplier"])
            if "crit_bonus" in buff_data:
                stats.crit += buff_data["crit_bonus"]
        return stats

    def upgrade(self) -> bool:
        """升级星级，最大3星，返回是否成功升级"""
        if self.star < 3:
            old_star = self.star
            self.star += 1
            
            # 更新生命值（保持当前生命比例）
            old_stats = self.get_stats()
            hp_ratio = self.current_hp / self.max_hp if self.max_hp > 0 else 1.0
            
            # 重新计算属性
            new_stats = self.get_stats()
            self.max_hp = new_stats.hp
            self.current_hp = int(new_stats.hp * hp_ratio)
            
            print(f"{self.name} 升级到 {self.star} 星！属性大幅提升！")
            return True
        return False
        
    def take_damage(self, raw_damage: int, damage_type: str = "physical") -> int:
        """
        承受伤害，考虑防御和伤害类型
        damage_type: "physical", "magical", "true", "chaos"
        """
        stats = self.get_stats()
        
        if damage_type == "true":
            # 真实伤害，无视防御
            actual_damage = raw_damage
        elif damage_type == "chaos":
            # 混沌伤害，无视防御，不触发反击
            actual_damage = raw_damage
        else:
            # 物理/魔法伤害，考虑防御
            actual_damage = max(1, raw_damage - stats.def_)
        
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage

    def heal(self, amount: int) -> int:
        """治疗，返回实际治疗量"""
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        actual_heal = self.current_hp - old_hp
        return actual_heal

    def is_alive(self) -> bool:
        """检查是否存活"""
        return self.current_hp > 0

    def gain_mana(self, amount: int) -> bool:
        """获得法力，返回是否达到释放技能的条件"""
        stats = self.get_stats()
        old_mana = self.current_mana
        self.current_mana = min(stats.mana, self.current_mana + amount)
        
        # 检查是否可以释放主动技能
        if (self.active_skill and 
            self.current_mana >= self.active_skill.mana_cost and 
            self.skill_cooldown <= 0):
            return True
        return False

    def cast_active_skill(self, targets: List["Unit"] = None) -> Dict[str, Any]:
        """
        释放主动技能
        返回技能效果信息
        """
        if not self.active_skill:
            return {"success": False, "message": "无主动技能"}
        
        if self.current_mana < self.active_skill.mana_cost:
            return {"success": False, "message": "法力不足"}
        
        if self.skill_cooldown > 0:
            return {"success": False, "message": "技能冷却中"}
        
        # 消耗法力
        self.current_mana -= self.active_skill.mana_cost
        self.skill_cooldown = self.active_skill.cooldown
        
        # 技能效果将在battle_simulator中具体实现
        return {
            "success": True,
            "skill": self.active_skill,
            "caster": self,
            "targets": targets or []
        }

    def add_equipment(self, equipment: Equipment) -> bool:
        """添加装备，最多4件"""
        if len(self.equipments) >= 4:
            return False
        
        self.equipments.append(equipment)
        
        # 特殊装备效果（如阵营转换）
        if "faction_change" in equipment.effects:
            self.faction = equipment.effects["faction_change"]
        if "class_change" in equipment.effects:
            self.classes = [equipment.effects["class_change"]]
        
        return True

    def add_buff(self, buff_name: str, buff_data: Dict[str, Any], duration: int = -1):
        """添加buff效果"""
        self.buffs[buff_name] = {**buff_data, "duration": duration}

    def add_debuff(self, debuff_name: str, debuff_data: Dict[str, Any], duration: int = -1):
        """添加debuff效果"""
        self.debuffs[debuff_name] = {**debuff_data, "duration": duration}

    def update_status_effects(self):
        """更新状态效果持续时间"""
        # 更新buff
        expired_buffs = []
        for buff_name, buff_data in self.buffs.items():
            if buff_data.get("duration", -1) > 0:
                buff_data["duration"] -= 1
                if buff_data["duration"] <= 0:
                    expired_buffs.append(buff_name)
        
        for buff_name in expired_buffs:
            del self.buffs[buff_name]
        
        # 更新debuff
        expired_debuffs = []
        for debuff_name, debuff_data in self.debuffs.items():
            if debuff_data.get("duration", -1) > 0:
                debuff_data["duration"] -= 1
                if debuff_data["duration"] <= 0:
                    expired_debuffs.append(debuff_name)
        
        for debuff_name in expired_debuffs:
            del self.debuffs[debuff_name]
        
        # 更新技能冷却
        if self.skill_cooldown > 0:
            self.skill_cooldown -= 1

    def get_display_info(self) -> Dict[str, Any]:
        """获取显示信息，用于控制台输出"""
        stats = self.get_stats()
        return {
            "name": self.name,
            "star": self.star,
            "faction": self.faction,
            "classes": self.classes,
            "cost": self.cost,
            "hp": f"{self.current_hp}/{stats.hp}",
            "atk": stats.atk,
            "def": stats.def_,
            "mana": f"{self.current_mana}/{stats.mana}",
            "equipments": len(self.equipments),
            "buffs": list(self.buffs.keys()),
            "debuffs": list(self.debuffs.keys())
        }

    @staticmethod
    def from_json(obj: Dict) -> "Unit":
        """从JSON数据创建Unit对象"""
        # 解析基础属性
        stats_data = obj.get("stats", {})
        base_stats = Stats(
            hp=int(stats_data.get("hp", 100)),
            atk=int(stats_data.get("atk", 50)),
            def_=int(stats_data.get("def", 10)),
            spd=float(stats_data.get("spd", 1.0)),
            rng=int(stats_data.get("rng", 1)),
            mana=int(stats_data.get("mana", 100)),
            crit=float(stats_data.get("crit", 0.1)),
            dodge=float(stats_data.get("dodge", 0.05)),
        )
        
        # 解析技能
        active_skill = None
        if "active_skill" in obj:
            skill_data = obj["active_skill"]
            active_skill = Skill(
                name=skill_data.get("name", ""),
                description=skill_data.get("description", ""),
                skill_type="active",
                mana_cost=skill_data.get("mana_cost", 100),
                cooldown=skill_data.get("cooldown", 0),
                effects=skill_data.get("effects", {})
            )
        
        passive_skills = []
        for skill_data in obj.get("passive_skills", []):
            passive_skill = Skill(
                name=skill_data.get("name", ""),
                description=skill_data.get("description", ""),
                skill_type="passive",
                effects=skill_data.get("effects", {})
            )
            passive_skills.append(passive_skill)
        
        unit = Unit(
            id=obj.get("id", "unknown"),
            name=obj.get("name", "Unknown"),
            faction=obj.get("faction", "人界"),
            classes=list(obj.get("classes", ["金"])),
            cost=int(obj.get("cost", 1)),
            base_stats=base_stats,
            active_skill=active_skill,
            passive_skills=passive_skills
        )
        
        return unit

    @staticmethod
    def from_dict(data: Dict) -> "Unit":
        """从字典数据创建Unit对象（兼容性方法）"""
        return Unit.from_json(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "faction": self.faction,
            "classes": self.classes,
            "cost": self.cost,
            "star": self.star,
            "stats": {
                "hp": self.base_stats.hp,
                "atk": self.base_stats.atk,
                "def": self.base_stats.def_,
                "spd": self.base_stats.spd,
                "rng": self.base_stats.rng,
                "mana": self.base_stats.mana,
                "crit": self.base_stats.crit,
                "dodge": self.base_stats.dodge
            },
            "active_skill": {
                "name": self.active_skill.name,
                "description": self.active_skill.description,
                "mana_cost": self.active_skill.mana_cost,
                "cooldown": self.active_skill.cooldown,
                "effects": self.active_skill.effects
            } if self.active_skill else None,
            "passive_skills": [
                {
                    "name": skill.name,
                    "description": skill.description,
                    "effects": skill.effects
                } for skill in self.passive_skills
            ]
        }


def load_units_from_json(filename: str = "data/celestial_units.json") -> List[Dict]:
    """从JSON文件加载单位数据"""
    import os
    
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(current_dir, filename)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("units", [])
    except FileNotFoundError:
        print(f"警告：单位数据文件 {file_path} 不存在")
        return []
    except json.JSONDecodeError as e:
        print(f"警告：解析单位数据文件失败: {e}")
        return []

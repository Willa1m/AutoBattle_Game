#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天界之战 - 单位类测试脚本
遵循项目规范：禁止图形化测试，所有测试通过控制台代码完成
"""

import unittest
import sys
import os
import json
from typing import Dict, Any
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.unit import Unit, Stats, Skill, Equipment

DATA = Path(__file__).resolve().parent.parent / 'data' / 'celestial_units.json'


class TestUnit(unittest.TestCase):
    """Unit类测试用例"""
    
    def setUp(self):
        """测试前准备"""
        # 创建基础属性
        self.base_stats = Stats(
            hp=100, atk=50, def_=10, spd=1.0, rng=1, 
            mana=80, crit=0.1, dodge=0.05
        )
        
        # 创建测试技能
        self.test_skill = Skill(
            name="测试技能",
            description="用于测试的技能",
            skill_type="active",
            mana_cost=80,
            cooldown=2,
            effects={"damage": 100}
        )
        
        # 创建测试装备
        self.test_equipment = Equipment(
            name="测试装备",
            item_type="attack",
            star=1,
            effects={"atk_bonus": 20, "crit_bonus": 0.1}
        )
        
        # 创建测试单位
        self.unit = Unit(
            id="test_001",
            name="测试单位",
            faction="人界",
            classes=["金"],
            cost=1,
            base_stats=self.base_stats,
            active_skill=self.test_skill
        )
    
    def test_unit_creation(self):
        """测试单位创建"""
        print("\n=== 测试单位创建 ===")
        
        self.assertEqual(self.unit.id, "test_001")
        self.assertEqual(self.unit.name, "测试单位")
        self.assertEqual(self.unit.faction, "人界")
        self.assertEqual(self.unit.classes, ["金"])
        self.assertEqual(self.unit.cost, 1)
        self.assertEqual(self.unit.star, 1)
        self.assertEqual(self.unit.current_hp, 100)
        self.assertEqual(self.unit.current_mana, 0)
        
        print(f"✓ 单位创建成功: {self.unit.name}")
        print(f"  - ID: {self.unit.id}")
        print(f"  - 阵营: {self.unit.faction}")
        print(f"  - 职业: {self.unit.classes}")
        print(f"  - 费用: {self.unit.cost}")
        print(f"  - 生命值: {self.unit.current_hp}/{self.unit.max_hp}")
    
    def test_stats_calculation(self):
        """测试属性计算"""
        print("\n=== 测试属性计算 ===")
        
        # 1星属性
        stats_1 = self.unit.get_stats()
        self.assertEqual(stats_1.hp, 100)
        self.assertEqual(stats_1.atk, 50)
        print(f"✓ 1星属性: HP={stats_1.hp}, ATK={stats_1.atk}")
        
        # 2星属性
        self.unit.upgrade()
        stats_2 = self.unit.get_stats()
        self.assertEqual(stats_2.hp, 180)  # 100 * 1.8
        self.assertEqual(stats_2.atk, 90)  # 50 * 1.8
        print(f"✓ 2星属性: HP={stats_2.hp}, ATK={stats_2.atk}")
        
        # 3星属性
        self.unit.upgrade()
        stats_3 = self.unit.get_stats()
        self.assertEqual(stats_3.hp, 324)  # 100 * 3.24
        self.assertEqual(stats_3.atk, 162)  # 50 * 3.24
        print(f"✓ 3星属性: HP={stats_3.hp}, ATK={stats_3.atk}")
        
        # 无法继续升级
        result = self.unit.upgrade()
        self.assertFalse(result)
        print("✓ 3星后无法继续升级")
    
    def test_damage_system(self):
        """测试伤害系统"""
        print("\n=== 测试伤害系统 ===")
        
        initial_hp = self.unit.current_hp
        
        # 物理伤害（考虑防御）
        damage_dealt = self.unit.take_damage(30, "physical")
        expected_damage = max(1, 30 - 10)  # 30攻击 - 10防御 = 20
        self.assertEqual(damage_dealt, expected_damage)
        self.assertEqual(self.unit.current_hp, initial_hp - expected_damage)
        print(f"✓ 物理伤害: 造成{damage_dealt}点伤害，剩余HP: {self.unit.current_hp}")
        
        # 真实伤害（无视防御）
        current_hp = self.unit.current_hp
        damage_dealt = self.unit.take_damage(25, "true")
        self.assertEqual(damage_dealt, 25)
        self.assertEqual(self.unit.current_hp, current_hp - 25)
        print(f"✓ 真实伤害: 造成{damage_dealt}点伤害，剩余HP: {self.unit.current_hp}")
        
        # 治疗测试
        heal_amount = self.unit.heal(30)
        print(f"✓ 治疗: 回复{heal_amount}点生命值，当前HP: {self.unit.current_hp}")
        
        # 死亡测试
        self.unit.take_damage(1000, "true")
        self.assertFalse(self.unit.is_alive())
        print("✓ 单位死亡测试通过")
    
    def test_mana_and_skills(self):
        """测试法力和技能系统"""
        print("\n=== 测试法力和技能系统 ===")
        
        # 法力获取
        can_cast = self.unit.gain_mana(50)
        self.assertEqual(self.unit.current_mana, 50)
        self.assertFalse(can_cast)  # 法力不足
        print(f"✓ 获得法力: {self.unit.current_mana}/80")
        
        # 法力足够释放技能
        can_cast = self.unit.gain_mana(30)
        self.assertEqual(self.unit.current_mana, 80)
        self.assertTrue(can_cast)  # 法力足够
        print(f"✓ 法力充足，可以释放技能: {self.unit.current_mana}/80")
        
        # 释放技能
        skill_result = self.unit.cast_active_skill()
        self.assertTrue(skill_result["success"])
        self.assertEqual(self.unit.current_mana, 0)  # 消耗法力
        self.assertEqual(self.unit.skill_cooldown, 2)  # 技能冷却
        print(f"✓ 技能释放成功: {skill_result['skill'].name}")
        print(f"  - 剩余法力: {self.unit.current_mana}")
        print(f"  - 冷却时间: {self.unit.skill_cooldown}")
        
        # 冷却期间无法释放
        self.unit.gain_mana(80)
        skill_result = self.unit.cast_active_skill()
        self.assertFalse(skill_result["success"])
        self.assertEqual(skill_result["message"], "技能冷却中")
        print("✓ 冷却期间无法释放技能")
    
    def test_equipment_system(self):
        """测试装备系统"""
        print("\n=== 测试装备系统 ===")
        
        # 添加装备前的属性
        stats_before = self.unit.get_stats()
        print(f"装备前: ATK={stats_before.atk}, CRIT={stats_before.crit}")
        
        # 添加装备
        success = self.unit.add_equipment(self.test_equipment)
        self.assertTrue(success)
        self.assertEqual(len(self.unit.equipments), 1)
        
        # 装备后的属性
        stats_after = self.unit.get_stats()
        self.assertEqual(stats_after.atk, stats_before.atk + 20)
        self.assertEqual(stats_after.crit, stats_before.crit + 0.1)
        print(f"装备后: ATK={stats_after.atk}, CRIT={stats_after.crit}")
        print("✓ 装备属性加成正确")
        
        # 装备数量限制测试
        for i in range(3):
            equipment = Equipment(f"装备{i}", "function", 1, {})
            self.unit.add_equipment(equipment)
        
        # 第5件装备应该失败
        extra_equipment = Equipment("多余装备", "function", 1, {})
        success = self.unit.add_equipment(extra_equipment)
        self.assertFalse(success)
        self.assertEqual(len(self.unit.equipments), 4)
        print("✓ 装备数量限制测试通过（最多4件）")
    
    def test_buff_debuff_system(self):
        """测试buff/debuff系统"""
        print("\n=== 测试buff/debuff系统 ===")
        
        # 添加buff
        self.unit.add_buff("力量增强", {"atk_multiplier": 1.5}, 3)
        self.assertEqual(len(self.unit.buffs), 1)
        self.assertTrue("力量增强" in self.unit.buffs)
        print("✓ 添加buff成功")
        
        # buff影响属性
        stats = self.unit.get_stats()
        expected_atk = int(50 * 1.5)  # 基础攻击力 * buff倍数
        self.assertEqual(stats.atk, expected_atk)
        print(f"✓ buff影响属性: ATK={stats.atk}")
        
        # 添加debuff
        self.unit.add_debuff("虚弱", {"atk_multiplier": 0.5}, 2)
        self.assertEqual(len(self.unit.debuffs), 1)
        print("✓ 添加debuff成功")
        
        # 状态效果更新
        for i in range(4):
            self.unit.update_status_effects()
            print(f"  回合{i+1}: buffs={len(self.unit.buffs)}, debuffs={len(self.unit.debuffs)}")
        
        # 所有状态效果应该过期
        self.assertEqual(len(self.unit.buffs), 0)
        self.assertEqual(len(self.unit.debuffs), 0)
        print("✓ 状态效果过期机制正确")
    
    def test_json_loading(self):
        """测试从JSON加载单位"""
        print("\n=== 测试JSON加载 ===")
        
        if DATA.exists():
            with open(DATA, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 测试加载第一个单位
            unit_data = data["units"][0]
            unit = Unit.from_json(unit_data)
            
            self.assertEqual(unit.id, unit_data["id"])
            self.assertEqual(unit.name, unit_data["name"])
            self.assertEqual(unit.faction, unit_data["faction"])
            self.assertEqual(unit.classes, unit_data["classes"])
            
            print(f"✓ 从JSON加载单位成功: {unit.name}")
            print(f"  - 阵营: {unit.faction}")
            print(f"  - 职业: {unit.classes}")
            print(f"  - 费用: {unit.cost}")
            
            # 测试技能加载
            if unit.active_skill:
                print(f"  - 主动技能: {unit.active_skill.name}")
            if unit.passive_skills:
                print(f"  - 被动技能数量: {len(unit.passive_skills)}")
        else:
            print("⚠ 数据文件不存在，跳过JSON加载测试")
    
    def test_display_info(self):
        """测试显示信息"""
        print("\n=== 测试显示信息 ===")
        
        # 添加一些状态
        self.unit.add_equipment(self.test_equipment)
        self.unit.add_buff("测试buff", {"atk_multiplier": 1.2}, 3)
        self.unit.gain_mana(40)
        
        display_info = self.unit.get_display_info()
        
        print("✓ 单位显示信息:")
        for key, value in display_info.items():
            print(f"  - {key}: {value}")
        
        # 验证关键信息
        self.assertEqual(display_info["name"], "测试单位")
        self.assertEqual(display_info["star"], 1)
        self.assertEqual(display_info["faction"], "人界")
        self.assertEqual(display_info["equipments"], 1)
        self.assertEqual(len(display_info["buffs"]), 1)

    def test_load_units(self):
        """测试加载单位数据"""
        if DATA.exists():
            units_data = json.loads(DATA.read_text(encoding='utf-8'))
            self.assertGreaterEqual(len(units_data.get("units", [])), 2)
            print(f"✓ 加载了 {len(units_data.get('units', []))} 个单位数据")

    def test_upgrade_and_damage(self):
        """测试升级和伤害（兼容原有测试）"""
        base = Stats(hp=100, atk=20, def_=5, spd=1.0, rng=1, mana=50, crit=0.1, dodge=0.05)
        u = Unit(id='t', name='T', faction='天庭', classes=['光明'], cost=2, base_stats=base)
        self.assertEqual(u.star, 1)
        u.upgrade()
        self.assertEqual(u.star, 2)
        dmg = u.take_damage(30)  # def reduces
        self.assertGreater(dmg, 0)
        self.assertTrue(u.is_alive())


class TestSynergies(unittest.TestCase):
    """测试阵营和职业协同效果"""
    
    def test_faction_synergy_data(self):
        """测试阵营协同数据"""
        print("\n=== 测试阵营协同数据 ===")
        
        if DATA.exists():
            with open(DATA, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            synergies = data.get("synergies", {})
            factions = synergies.get("factions", {})
            classes = synergies.get("classes", {})
            
            print(f"✓ 阵营协同效果数量: {len(factions)}")
            for faction, effects in factions.items():
                print(f"  - {faction}: {effects}")
            
            print(f"✓ 职业协同效果数量: {len(classes)}")
            for class_name, effects in classes.items():
                print(f"  - {class_name}: {effects}")
            
            # 验证必要的阵营存在
            required_factions = ["天庭", "地狱", "人界", "仙界", "妖界", "神兽"]
            for faction in required_factions:
                self.assertIn(faction, factions)
            
            # 验证必要的职业存在
            required_classes = ["金", "木", "水", "火", "土", "黑暗", "光明"]
            for class_name in required_classes:
                self.assertIn(class_name, classes)
            
            print("✓ 所有必要的阵营和职业协同效果都存在")


def run_console_tests():
    """运行控制台测试"""
    print("=" * 60)
    print("天界之战 - 单位系统测试")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTests(loader.loadTestsFromTestCase(TestUnit))
    test_suite.addTests(loader.loadTestsFromTestCase(TestSynergies))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    print(f"运行测试数量: {result.testsRun}")
    print(f"失败数量: {len(result.failures)}")
    print(f"错误数量: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 所有测试通过！单位系统运行正常。")
        return True
    else:
        print("\n❌ 部分测试失败，请检查代码。")
        return False


if __name__ == "__main__":
    # 运行控制台测试
    success = run_console_tests()
    
    # 退出码
    sys.exit(0 if success else 1)

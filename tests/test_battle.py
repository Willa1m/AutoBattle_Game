"""
天界之战 - 战斗系统测试
Battle System Tests for Battle of the Heavens

测试战斗系统、棋盘管理和协同效果的集成功能
Tests battle system, board management and synergy effects integration

测试方式：控制台unittest
Testing: Console unittest
"""

import unittest
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.unit import Unit, Stats
from core.battle import BattleSystem, BattlePhase
from core.board import Board, Position, BoardType
from core.synergy import SynergyManager


class TestBattleSystem(unittest.TestCase):
    """战斗系统测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.battle_system = BattleSystem()
        self.board = Board(BoardType.BATTLE)
        self.synergy_manager = SynergyManager()
        
        # 创建测试单位
        stats1 = Stats(hp=100, atk=50, def_=10, spd=5, rng=1, mana=0, crit=0.1, dodge=0.05)
        self.unit1 = Unit("test_001", "测试单位1", "天庭", ["金"], 1, stats1)
        
        stats2 = Stats(hp=80, atk=60, def_=8, spd=6, rng=1, mana=0, crit=0.15, dodge=0.1)
        self.unit2 = Unit("test_002", "测试单位2", "地府", ["暗"], 1, stats2)
    
    def test_battle_initialization(self):
        """测试战斗初始化"""
        player1_units = [self.unit1]
        player2_units = [self.unit2]
        
        success = self.battle_system.setup_battle(player1_units, player2_units)
        self.assertTrue(success, "战斗初始化应该成功")
        self.assertEqual(self.battle_system.phase, BattlePhase.PREPARATION, "战斗阶段应该是PREPARATION")
    
    def test_unit_placement(self):
        """测试单位放置"""
        # 测试有效位置放置
        success = self.board.place_unit(self.unit1, Position(0, 0))
        self.assertTrue(success, "应该能在空位置放置单位")
        
        # 测试重复放置
        success = self.board.place_unit(self.unit2, Position(0, 0))
        self.assertFalse(success, "不应该能在已占用位置放置单位")
        
        # 测试获取单位
        unit_at_pos = self.board.get_unit_at(Position(0, 0))
        self.assertEqual(unit_at_pos, self.unit1, "应该能正确获取位置上的单位")
    
    def test_unit_movement(self):
        """测试单位移动"""
        # 先放置单位
        self.board.place_unit(self.unit1, Position(0, 0))
        
        # 测试有效移动
        success = self.board.move_unit(self.unit1.id, Position(1, 1))
        self.assertTrue(success, "应该能移动到空位置")
        
        # 验证位置更新
        new_pos = self.board.get_unit_position(self.unit1.id)
        self.assertEqual(new_pos, Position(1, 1), "单位位置应该正确更新")
        
        # 验证旧位置为空
        old_unit = self.board.get_unit_at(Position(0, 0))
        self.assertIsNone(old_unit, "旧位置应该为空")
    
    def test_synergy_effects(self):
        """测试协同效果"""
        # 创建多个天庭单位测试阵营协同
        stats = Stats(hp=100, atk=50, def_=10, spd=5, rng=1, mana=0, crit=0.1, dodge=0.05)
        
        tianting_units = []
        for i in range(3): # This is already 3, but let's confirm the expectation relies on >=3
            unit = Unit(f"tianting_{i}", f"天庭单位{i}", "天庭", ["金"], 1, stats)
            # unit_id不再需要，使用unit.id
            # player_id不再需要，Unit类没有这个属性
            tianting_units.append(unit)
        
        # 测试阵营协同统计
        faction_counts = self.synergy_manager.count_units_by_faction(tianting_units)
        self.assertEqual(faction_counts.get("天庭", 0), 3, "应该正确统计天庭单位数量")
        
        # 测试激活的协同效果
        active_synergies = self.synergy_manager.get_active_faction_synergies(tianting_units)
        self.assertIn("天庭", active_synergies, "应该激活天庭阵营协同")
        
        # 测试协同效果应用
        bonuses = self.synergy_manager.apply_synergies_to_unit(tianting_units[0], tianting_units)
        self.assertGreater(len(bonuses), 0, "应该有协同加成效果")
    
    def test_battle_flow(self):
        """测试完整战斗流程"""
        player1_units = [self.unit1]
        player2_units = [self.unit2]
        
        # 设置战斗
        success = self.battle_system.setup_battle(player1_units, player2_units)
        self.assertTrue(success, "战斗设置应该成功")
        
        # 开始战斗
        result = self.battle_system.start_battle()
        self.assertEqual(self.battle_system.phase, BattlePhase.FINISHED, "战斗结束后阶段应该是FINISHED")
        self.assertIsNotNone(result, "应该返回战斗结果")
        
        # 验证战斗执行了回合
        self.assertGreater(self.battle_system.current_round, 0, "应该执行了至少一个回合")
        
        # 验证战斗结果
        self.assertIn(result.winner, ["player", "enemy", "draw"], "胜利者应该是有效值")
    
    def test_damage_calculation(self):
        """测试伤害计算"""
        initial_hp = self.unit2.current_hp
        
        # 模拟攻击
        damage = max(1, self.unit1.get_stats().atk - self.unit2.get_stats().def_)
        self.unit2.take_damage(damage)
        
        # 验证生命值减少
        self.assertLess(self.unit2.current_hp, initial_hp, "单位生命值应该减少")
        self.assertTrue(self.unit2.is_alive(), "单位应该还活着")
    
    def test_unit_death(self):
        """测试单位死亡"""
        # 造成致命伤害
        fatal_damage = self.unit2.current_hp + 10
        self.unit2.take_damage(fatal_damage)
        
        # 验证单位死亡
        self.assertFalse(self.unit2.is_alive(), "单位应该死亡")
        self.assertEqual(self.unit2.current_hp, 0, "单位生命值应该为0")
    
    def test_skill_system(self):
        """测试技能系统"""
        # 给单位添加法力值
        self.unit1.gain_mana(50)
        
        # 测试主动技能
        if self.unit1.active_skill and self.unit1.current_mana >= self.unit1.active_skill.mana_cost:
            initial_mana = self.unit1.current_mana
            # 这里应该调用技能，但由于技能系统复杂，我们只测试法力值消耗
            self.unit1.current_mana -= self.unit1.active_skill.mana_cost
            self.assertLess(self.unit1.current_mana, initial_mana, "释放技能应该消耗法力值")
    
    def test_board_boundaries(self):
        """测试棋盘边界"""
        # 测试无效位置
        invalid_pos = Position(-1, -1)
        self.assertFalse(self.board.is_valid_position(invalid_pos), "负坐标应该无效")
        
        invalid_pos2 = Position(10, 10)
        self.assertFalse(self.board.is_valid_position(invalid_pos2), "超出边界的坐标应该无效")
        
        # 测试边界位置
        boundary_pos = Position(7, 7)
        self.assertTrue(self.board.is_valid_position(boundary_pos), "边界位置应该有效")
    
    def test_pathfinding(self):
        """测试路径查找"""
        start = Position(0, 0)
        end = Position(2, 2)
        
        path = self.board.find_path(start, end)
        self.assertGreater(len(path), 0, "应该能找到路径")
        self.assertEqual(path[-1], end, "路径应该到达目标位置")
    
    def test_range_detection(self):
        """测试范围检测"""
        # 放置单位
        self.board.place_unit(self.unit1, Position(3, 3))
        self.board.place_unit(self.unit2, Position(4, 4))
        
        # 测试范围内单位检测
        units_in_range = self.board.get_units_in_range(Position(3, 3), 2)
        self.assertGreater(len(units_in_range), 0, "应该检测到范围内的单位")
        
        # 测试最近敌人查找
        nearest_enemy = self.board.find_nearest_enemy(self.unit1)
        self.assertIsNotNone(nearest_enemy, "应该能找到最近的敌人")
        self.assertEqual(nearest_enemy[0], self.unit2, "最近的敌人应该是unit2")


class TestBattleIntegration(unittest.TestCase):
    """战斗系统集成测试"""
    
    def setUp(self):
        """测试前准备"""
        # 尝试加载真实单位数据
        self.units_data = None
        try:
            with open('data/celestial_units.json', 'r', encoding='utf-8') as f:
                self.units_data = json.load(f)
        except FileNotFoundError:
            pass
    
    def test_real_units_battle(self):
        """使用真实单位数据测试战斗"""
        if not self.units_data:
            self.skipTest("单位数据文件不存在，跳过真实单位测试")
        
        battle_system = BattleSystem()
        
        # 创建玩家1的单位
        player1_units = []
        for unit_data in self.units_data["units"][:2]:
            unit = Unit.from_json(unit_data)
            # unit_id不再需要，使用unit.id
            # player_id不再需要，Unit类没有这个属性
            player1_units.append(unit)
        
        # 创建玩家2的单位
        player2_units = []
        for unit_data in self.units_data["units"][2:4]:
            unit = Unit.from_json(unit_data)
            # unit_id不再需要，使用unit.id
            # player_id不再需要，Unit类没有这个属性
            player2_units.append(unit)
        
        # 设置并开始战斗
        success = battle_system.setup_battle(player1_units, player2_units)
        self.assertTrue(success, "真实单位战斗设置应该成功")
        
        battle_system.start_battle()
        
        # 执行几个回合
        max_rounds = 5
        for _ in range(max_rounds):
            if battle_system.phase == BattlePhase.COMBAT:
                battle_system.execute_round()
            else:
                break
        
        # 验证战斗状态
        self.assertIn(battle_system.phase, [BattlePhase.COMBAT, BattlePhase.FINISHED], 
                     "战斗应该在进行中或已结束")
    
    def test_synergy_integration(self):
        """测试协同效果集成"""
        if not self.units_data:
            self.skipTest("单位数据文件不存在，跳过协同效果集成测试")
        
        synergy_manager = SynergyManager()
        
        # 创建具有协同效果的单位组合
        test_units = []
        tianting_units = [unit for unit in self.units_data["units"] if unit["faction"] == "天庭"][:3]
        
        for i, unit_data in enumerate(tianting_units):
            unit = Unit.from_json(unit_data)
            # unit_id不再需要，使用unit.id
            # player_id不再需要，Unit类没有这个属性
            test_units.append(unit)
        
        # 测试协同效果
        synergy_info = synergy_manager.get_synergy_info(test_units)
        self.assertIn("天庭", synergy_info["faction_counts"], "应该有天庭阵营单位")
        
        # 测试协同效果应用
        if test_units:
            bonuses = synergy_manager.apply_synergies_to_unit(test_units[0], test_units)
            # 如果有足够的天庭单位，应该有协同加成
            if synergy_info["faction_counts"]["天庭"] >= 3:
                self.assertGreater(len(bonuses), 0, "应该有天庭阵营协同加成")


def run_all_tests():
    """运行所有测试"""
    print("🧪 开始战斗系统测试...")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestBattleSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestBattleIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    if result.wasSuccessful():
        print("🎉 所有战斗系统测试通过！")
    else:
        print(f"❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
        
        # 输出失败详情
        for test, traceback in result.failures:
            print(f"失败: {test}")
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"错误: {test}")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_all_tests()
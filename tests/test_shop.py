"""
商店系统测试
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.shop import Shop, ShopConfig, ShopManager
from core.unit import Unit


class TestShop(unittest.TestCase):
    """商店系统测试"""
    
    def setUp(self):
        """测试前准备"""
        self.config = ShopConfig()
        self.shop = Shop(self.config)
    
    def test_shop_initialization(self):
        """测试商店初始化"""
        print("=== 测试商店初始化 ===")
        
        # 检查商店配置
        self.assertEqual(self.shop.config.shop_size, 5)
        self.assertEqual(self.shop.config.refresh_cost, 2)
        
        # 检查商店状态
        self.assertEqual(len(self.shop.current_shop), 5)
        self.assertEqual(len(self.shop.frozen_slots), 5)
        
        # 检查单位池
        self.assertGreater(len(self.shop.available_units), 0)
        
        print("✓ 商店初始化成功")
        print(f"  - 商店大小: {len(self.shop.current_shop)}")
        print(f"  - 单位池: {sum(len(units) for units in self.shop.available_units.values())} 个单位")
    
    def test_shop_refresh(self):
        """测试商店刷新"""
        print("=== 测试商店刷新 ===")
        
        player_level = 3
        player_gold = 10
        
        # 初始填充商店
        self.shop._fill_shop(player_level)
        initial_shop = self.shop.current_shop.copy()
        
        # 刷新商店
        success = self.shop.refresh_shop(player_level, player_gold)
        self.assertTrue(success)
        
        # 检查商店内容是否改变
        new_shop = self.shop.current_shop
        changed = any(initial_shop[i] != new_shop[i] for i in range(len(initial_shop)))
        
        print(f"✓ 商店刷新成功，内容{'已改变' if changed else '未改变'}")
        
        # 测试金币不足的情况
        success = self.shop.refresh_shop(player_level, 1)
        self.assertFalse(success)
        print("✓ 金币不足时无法刷新")
    
    def test_unit_purchase(self):
        """测试单位购买"""
        print("=== 测试单位购买 ===")
        
        # 填充商店
        self.shop._fill_shop(3)
        
        # 找到第一个有单位的槽位
        slot_index = -1
        for i, unit in enumerate(self.shop.current_shop):
            if unit is not None:
                slot_index = i
                break
        
        if slot_index >= 0:
            unit = self.shop.current_shop[slot_index]
            player_gold = 10
            
            # 购买单位
            success, bought_unit, cost = self.shop.buy_unit(slot_index, player_gold)
            
            self.assertTrue(success)
            self.assertIsNotNone(bought_unit)
            self.assertEqual(bought_unit.id, unit.id)
            self.assertGreater(cost, 0)
            self.assertIsNone(self.shop.current_shop[slot_index])
            
            print(f"✓ 购买单位成功: {bought_unit.name} (费用: {cost})")
        
        # 测试金币不足的情况
        if slot_index >= 0:
            self.shop.current_shop[slot_index] = unit  # 重新放置单位
            success, _, _ = self.shop.buy_unit(slot_index, 0)
            self.assertFalse(success)
            print("✓ 金币不足时无法购买")
    
    def test_slot_freezing(self):
        """测试槽位冻结"""
        print("=== 测试槽位冻结 ===")
        
        # 填充商店
        self.shop._fill_shop(3)
        
        # 找到有单位的槽位
        slot_index = -1
        for i, unit in enumerate(self.shop.current_shop):
            if unit is not None:
                slot_index = i
                break
        
        if slot_index >= 0:
            # 冻结槽位
            success = self.shop.freeze_slot(slot_index)
            self.assertTrue(success)
            self.assertTrue(self.shop.frozen_slots[slot_index])
            
            # 解冻槽位
            success = self.shop.freeze_slot(slot_index)
            self.assertTrue(success)
            self.assertFalse(self.shop.frozen_slots[slot_index])
            
            print(f"✓ 槽位 {slot_index} 冻结/解冻成功")
        
        # 测试空槽位冻结
        empty_slot = -1
        for i, unit in enumerate(self.shop.current_shop):
            if unit is None:
                empty_slot = i
                break
        
        if empty_slot >= 0:
            success = self.shop.freeze_slot(empty_slot)
            self.assertFalse(success)
            print("✓ 空槽位无法冻结")
    
    def test_unit_selling(self):
        """测试单位出售"""
        print("=== 测试单位出售 ===")
        
        # 创建测试单位
        unit_data = {
            "id": "test_unit",
            "name": "测试单位",
            "cost": 4,
            "faction": "人界",
            "classes": ["金"]
        }
        unit = Unit.from_dict(unit_data)
        
        # 出售单位
        gold_earned = self.shop.sell_unit(unit)
        expected_gold = max(1, unit.cost // 2)
        
        self.assertEqual(gold_earned, expected_gold)
        print(f"✓ 出售单位成功: {unit.name} -> {gold_earned} 金币")
    
    def test_unit_upgrade(self):
        """测试单位升级"""
        print("=== 测试单位升级 ===")
        
        # 创建3个相同的1星单位
        unit_data = {
            "id": "warrior",
            "name": "战士",
            "cost": 1,
            "faction": "人界",
            "classes": ["金"]
        }
        
        units = [Unit.from_dict(unit_data) for _ in range(3)]
        target_unit = units[0]
        
        # 检查升级条件
        can_upgrade = self.shop.can_upgrade_unit(target_unit, units)
        self.assertTrue(can_upgrade)
        
        # 执行升级
        success, units_to_remove = self.shop.upgrade_unit(target_unit, units)
        self.assertTrue(success)
        self.assertEqual(len(units_to_remove), 2)
        self.assertEqual(target_unit.star, 2)
        
        print(f"✓ 单位升级成功: {target_unit.name} -> {target_unit.star} 星")
        
        # 测试无法升级的情况（单位不足）
        single_unit = [Unit.from_dict(unit_data)]
        can_upgrade = self.shop.can_upgrade_unit(single_unit[0], single_unit)
        self.assertFalse(can_upgrade)
        print("✓ 单位数量不足时无法升级")
    
    def test_upgrade_info(self):
        """测试升级信息"""
        print("=== 测试升级信息 ===")
        
        unit_data = {
            "id": "warrior",
            "name": "战士",
            "cost": 1,
            "faction": "人界",
            "classes": ["金"]
        }
        
        # 创建2个相同单位
        units = [Unit.from_dict(unit_data) for _ in range(2)]
        target_unit = units[0]
        
        # 获取升级信息
        info = self.shop.get_unit_upgrade_info(target_unit, units)
        
        self.assertEqual(info["unit_id"], "warrior")
        self.assertEqual(info["current_star"], 1)
        self.assertEqual(info["current_count"], 2)
        self.assertEqual(info["required_count"], 3)
        self.assertFalse(info["can_upgrade"])
        
        print(f"✓ 升级信息正确: {info['current_count']}/{info['required_count']}")
    
    def test_shop_state(self):
        """测试商店状态"""
        print("=== 测试商店状态 ===")
        
        # 填充商店
        self.shop._fill_shop(3)
        
        # 获取商店状态
        state = self.shop.get_shop_state()
        
        self.assertIn("units", state)
        self.assertIn("refresh_cost", state)
        self.assertIn("shop_size", state)
        
        self.assertEqual(len(state["units"]), self.config.shop_size)
        self.assertEqual(state["refresh_cost"], self.config.refresh_cost)
        self.assertEqual(state["shop_size"], self.config.shop_size)
        
        print("✓ 商店状态获取成功")
        print(f"  - 单位数量: {len([u for u in state['units'] if u['unit'] is not None])}")


class TestShopManager(unittest.TestCase):
    """商店管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.shop_manager = ShopManager()
    
    def test_player_shop_management(self):
        """测试玩家商店管理"""
        print("=== 测试玩家商店管理 ===")
        
        player_id = "player1"
        
        # 创建玩家商店
        shop = self.shop_manager.create_shop_for_player(player_id)
        self.assertIsNotNone(shop)
        
        # 获取玩家商店
        retrieved_shop = self.shop_manager.get_player_shop(player_id)
        self.assertEqual(shop, retrieved_shop)
        
        print(f"✓ 玩家 {player_id} 商店创建成功")
        
        # 移除玩家商店
        self.shop_manager.remove_player_shop(player_id)
        removed_shop = self.shop_manager.get_player_shop(player_id)
        self.assertIsNone(removed_shop)
        
        print(f"✓ 玩家 {player_id} 商店移除成功")
    
    def test_multiple_player_shops(self):
        """测试多玩家商店"""
        print("=== 测试多玩家商店 ===")
        
        players = ["player1", "player2", "player3"]
        
        # 为多个玩家创建商店
        shops = {}
        for player_id in players:
            shop = self.shop_manager.create_shop_for_player(player_id)
            shops[player_id] = shop
        
        # 验证每个玩家都有独立的商店
        for player_id in players:
            shop = self.shop_manager.get_player_shop(player_id)
            self.assertIsNotNone(shop)
            self.assertEqual(shop, shops[player_id])
        
        print(f"✓ {len(players)} 个玩家商店创建成功")
        
        # 测试批量刷新
        player_levels = {pid: 3 for pid in players}
        player_golds = {pid: 10 for pid in players}
        
        self.shop_manager.refresh_all_shops(player_levels, player_golds)
        print("✓ 批量刷新商店成功")


if __name__ == "__main__":
    unittest.main(verbosity=2)
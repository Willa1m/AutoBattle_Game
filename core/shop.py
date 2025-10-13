"""
商店系统 - 负责单位购买、刷新和升级
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from .unit import Unit, load_units_from_json


@dataclass
class ShopConfig:
    """商店配置"""
    shop_size: int = 5  # 商店槽位数量
    refresh_cost: int = 2  # 刷新费用
    base_unit_cost: int = 3  # 基础单位费用
    level_multiplier: float = 1.5  # 等级费用倍数
    
    # 各等级单位出现概率（按玩家等级）
    unit_probabilities: Dict[int, List[float]] = None
    
    def __post_init__(self):
        if self.unit_probabilities is None:
            # 默认概率配置：[1费, 2费, 3费, 4费, 5费]
            self.unit_probabilities = {
                1: [1.0, 0.0, 0.0, 0.0, 0.0],  # 1级只有1费单位
                2: [0.7, 0.3, 0.0, 0.0, 0.0],  # 2级主要1费，少量2费
                3: [0.5, 0.35, 0.15, 0.0, 0.0],  # 3级开始出现3费
                4: [0.35, 0.35, 0.25, 0.05, 0.0],  # 4级少量4费
                5: [0.25, 0.3, 0.3, 0.1, 0.05],  # 5级开始出现5费
                6: [0.2, 0.25, 0.3, 0.2, 0.05],  # 6级更多高费
                7: [0.15, 0.2, 0.3, 0.25, 0.1],  # 7级高费增加
                8: [0.1, 0.15, 0.25, 0.3, 0.2],  # 8级大量高费
                9: [0.05, 0.1, 0.2, 0.35, 0.3],  # 9级主要高费
                10: [0.05, 0.1, 0.15, 0.3, 0.4]  # 10级最多5费
            }


class Shop:
    """商店类"""
    
    def __init__(self, config: ShopConfig = None):
        self.config = config or ShopConfig()
        self.available_units: Dict[int, List[Unit]] = {}  # 按费用分类的可用单位
        self.current_shop: List[Optional[Unit]] = [None] * self.config.shop_size
        self.frozen_slots: List[bool] = [False] * self.config.shop_size
        
        # 加载单位数据
        self._load_unit_pool()
    
    def _load_unit_pool(self):
        """加载单位池"""
        try:
            units_data = load_units_from_json()
            for unit_data in units_data:
                unit = Unit.from_dict(unit_data)
                cost = unit.cost
                if cost not in self.available_units:
                    self.available_units[cost] = []
                self.available_units[cost].append(unit)
            
            print(f"商店加载完成：{sum(len(units) for units in self.available_units.values())} 个单位")
            for cost, units in self.available_units.items():
                print(f"  {cost}费单位: {len(units)} 个")
        
        except Exception as e:
            print(f"加载单位数据失败: {e}")
            # 创建默认单位池
            self._create_default_unit_pool()
    
    def _create_default_unit_pool(self):
        """创建默认单位池（用于测试）"""
        default_units = [
            {"id": "warrior", "name": "战士", "cost": 1, "faction": "人界", "classes": ["金"]},
            {"id": "archer", "name": "弓手", "cost": 2, "faction": "人界", "classes": ["木"]},
            {"id": "mage", "name": "法师", "cost": 3, "faction": "人界", "classes": ["水"]},
            {"id": "knight", "name": "骑士", "cost": 4, "faction": "人界", "classes": ["火"]},
            {"id": "dragon", "name": "龙", "cost": 5, "faction": "妖界", "classes": ["土"]}
        ]
        
        for unit_data in default_units:
            unit = Unit.from_dict(unit_data)
            cost = unit.cost
            if cost not in self.available_units:
                self.available_units[cost] = []
            self.available_units[cost].append(unit)
    
    def refresh_shop(self, player_level: int, player_gold: int) -> bool:
        """刷新商店"""
        if player_gold < self.config.refresh_cost:
            return False
        
        # 清空未冻结的槽位
        for i in range(self.config.shop_size):
            if not self.frozen_slots[i]:
                self.current_shop[i] = None
        
        # 重新填充商店
        self._fill_shop(player_level)
        return True
    
    def _fill_shop(self, player_level: int):
        """填充商店"""
        # 获取当前等级的概率分布
        if player_level in self.config.unit_probabilities:
            probabilities = self.config.unit_probabilities[player_level]
        else:
            # 超过最大等级，使用最高等级的概率
            max_level = max(self.config.unit_probabilities.keys())
            probabilities = self.config.unit_probabilities[max_level]
        
        # 填充空槽位
        for i in range(self.config.shop_size):
            if self.current_shop[i] is None:
                unit = self._generate_random_unit(probabilities)
                self.current_shop[i] = unit
    
    def _generate_random_unit(self, probabilities: List[float]) -> Optional[Unit]:
        """根据概率生成随机单位"""
        # 选择费用等级
        cost_level = random.choices(range(1, len(probabilities) + 1), weights=probabilities)[0]
        
        # 从对应费用的单位池中随机选择
        if cost_level in self.available_units and self.available_units[cost_level]:
            unit_template = random.choice(self.available_units[cost_level])
            # 创建新的单位实例
            return Unit.from_dict(unit_template.to_dict())
        
        return None
    
    def buy_unit(self, slot_index: int, player_gold: int) -> Tuple[bool, Optional[Unit], int]:
        """
        购买单位
        返回: (成功, 单位, 花费金币)
        """
        if slot_index < 0 or slot_index >= self.config.shop_size:
            return False, None, 0
        
        unit = self.current_shop[slot_index]
        if unit is None:
            return False, None, 0
        
        cost = unit.cost
        if player_gold < cost:
            return False, None, 0
        
        # 购买成功，移除单位
        self.current_shop[slot_index] = None
        self.frozen_slots[slot_index] = False
        
        return True, unit, cost
    
    def freeze_slot(self, slot_index: int) -> bool:
        """冻结/解冻槽位"""
        if slot_index < 0 or slot_index >= self.config.shop_size:
            return False
        
        if self.current_shop[slot_index] is not None:
            self.frozen_slots[slot_index] = not self.frozen_slots[slot_index]
            return True
        
        return False
    
    def sell_unit(self, unit: Unit) -> int:
        """出售单位，返回金币"""
        return max(1, unit.cost // 2)
    
    def get_shop_state(self) -> Dict:
        """获取商店状态"""
        shop_units = []
        for i, unit in enumerate(self.current_shop):
            if unit:
                shop_units.append({
                    "slot": i,
                    "unit": unit.to_dict(),
                    "frozen": self.frozen_slots[i]
                })
            else:
                shop_units.append({
                    "slot": i,
                    "unit": None,
                    "frozen": self.frozen_slots[i]
                })
        
        return {
            "units": shop_units,
            "refresh_cost": self.config.refresh_cost,
            "shop_size": self.config.shop_size
        }
    
    def can_upgrade_unit(self, unit: Unit, player_units: List[Unit]) -> bool:
        """检查是否可以升级单位"""
        if unit.star >= 3:
            return False
        
        # 计算同名同星级单位数量
        same_units = [u for u in player_units 
                     if u.id == unit.id and u.star == unit.star]
        
        # 需要3个同星级单位才能升级
        return len(same_units) >= 3
    
    def upgrade_unit(self, unit: Unit, player_units: List[Unit]) -> Tuple[bool, List[Unit]]:
        """
        升级单位
        返回: (成功, 需要移除的单位列表)
        """
        if not self.can_upgrade_unit(unit, player_units):
            return False, []
        
        # 找到同名同星级的单位
        same_units = [u for u in player_units 
                     if u.id == unit.id and u.star == unit.star]
        
        if len(same_units) < 3:
            return False, []
        
        # 升级第一个单位
        target_unit = same_units[0]
        target_unit.upgrade()
        
        # 返回需要移除的其他两个单位
        units_to_remove = same_units[1:3]
        return True, units_to_remove
    
    def get_unit_upgrade_info(self, unit: Unit, player_units: List[Unit]) -> Dict:
        """获取单位升级信息"""
        same_units = [u for u in player_units 
                     if u.id == unit.id and u.star == unit.star]
        
        return {
            "unit_id": unit.id,
            "current_star": unit.star,
            "current_count": len(same_units),
            "required_count": 3,
            "can_upgrade": len(same_units) >= 3 and unit.star < 3,
            "max_star": 3
        }


class ShopManager:
    """商店管理器 - 管理多个玩家的商店"""
    
    def __init__(self, config: ShopConfig = None):
        self.config = config or ShopConfig()
        self.player_shops: Dict[str, Shop] = {}
    
    def create_shop_for_player(self, player_id: str) -> Shop:
        """为玩家创建商店"""
        shop = Shop(self.config)
        self.player_shops[player_id] = shop
        return shop
    
    def get_player_shop(self, player_id: str) -> Optional[Shop]:
        """获取玩家的商店"""
        return self.player_shops.get(player_id)
    
    def refresh_all_shops(self, player_levels: Dict[str, int], player_golds: Dict[str, int]):
        """刷新所有玩家的商店"""
        for player_id, shop in self.player_shops.items():
            if player_id in player_levels and player_id in player_golds:
                shop.refresh_shop(player_levels[player_id], player_golds[player_id])
    
    def remove_player_shop(self, player_id: str):
        """移除玩家的商店"""
        if player_id in self.player_shops:
            del self.player_shops[player_id]
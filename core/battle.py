#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天界之战 - 战斗系统核心类
实现回合制自走棋战斗逻辑，支持控制台测试
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import random
import math
from enum import Enum

try:
    from .unit import Unit, Stats
except ImportError:
    # 直接运行时的导入方式
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.unit import Unit, Stats


class BattlePhase(Enum):
    """战斗阶段枚举"""
    PREPARATION = "preparation"  # 准备阶段
    COMBAT = "combat"           # 战斗阶段
    FINISHED = "finished"       # 战斗结束


class ActionType(Enum):
    """行动类型枚举"""
    MOVE = "move"
    ATTACK = "attack"
    SKILL = "skill"
    WAIT = "wait"


@dataclass
class BattleAction:
    """战斗行动数据类"""
    unit: Unit
    action_type: ActionType
    target: Optional[Unit] = None
    target_position: Optional[Tuple[int, int]] = None
    skill_data: Optional[Dict[str, Any]] = None
    priority: int = 0  # 行动优先级，数值越高越先行动


@dataclass
class BattleResult:
    """战斗结果数据类"""
    winner: str  # "player" 或 "enemy" 或 "draw"
    total_rounds: int
    damage_dealt: Dict[str, int]  # 各单位造成的伤害
    damage_taken: Dict[str, int]  # 各单位承受的伤害
    skills_used: Dict[str, int]   # 各单位使用技能次数
    battle_log: List[str]         # 战斗日志


class BattleSystem:
    """战斗系统核心类"""
    
    def __init__(self, board_size: Tuple[int, int] = (8, 8)):
        """
        初始化战斗系统
        
        Args:
            board_size: 棋盘大小，默认8x8
        """
        self.board_size = board_size
        self.board: List[List[Optional[Unit]]] = [[None for _ in range(board_size[1])] 
                                                  for _ in range(board_size[0])]
        
        self.player_units: List[Unit] = []
        self.enemy_units: List[Unit] = []
        
        self.current_round = 0
        self.phase = BattlePhase.PREPARATION
        self.battle_log: List[str] = []
        
        # 战斗统计
        self.damage_dealt: Dict[str, int] = {}
        self.damage_taken: Dict[str, int] = {}
        self.skills_used: Dict[str, int] = {}
        
        # 战斗配置
        self.max_rounds = 30  # 最大回合数
        self.mana_per_round = 20  # 每回合获得的法力值
        
    def setup_battle(self, player_units: List[Unit], enemy_units: List[Unit],
                    player_positions: List[Tuple[int, int]] = None,
                    enemy_positions: List[Tuple[int, int]] = None) -> bool:
        """
        设置战斗
        
        Args:
            player_units: 玩家单位列表
            enemy_units: 敌方单位列表
            player_positions: 玩家单位位置（可选）
            enemy_positions: 敌方单位位置（可选）
            
        Returns:
            bool: 设置是否成功
        """
        try:
            # 清空棋盘
            self.clear_board()
            
            # 设置单位
            self.player_units = player_units.copy()
            self.enemy_units = enemy_units.copy()
            
            # 初始化统计数据
            for unit in self.player_units + self.enemy_units:
                self.damage_dealt[unit.id] = 0
                self.damage_taken[unit.id] = 0
                self.skills_used[unit.id] = 0
            
            # 放置玩家单位
            if player_positions:
                for unit, pos in zip(self.player_units, player_positions):
                    if not self.place_unit(unit, pos):
                        self.log(f"警告：无法放置玩家单位 {unit.name} 到位置 {pos}")
            else:
                self._auto_place_units(self.player_units, "player")
            
            # 放置敌方单位
            if enemy_positions:
                for unit, pos in zip(self.enemy_units, enemy_positions):
                    if not self.place_unit(unit, pos):
                        self.log(f"警告：无法放置敌方单位 {unit.name} 到位置 {pos}")
            else:
                self._auto_place_units(self.enemy_units, "enemy")
            
            self.phase = BattlePhase.PREPARATION
            self.log(f"战斗设置完成：玩家 {len(self.player_units)} 单位 vs 敌方 {len(self.enemy_units)} 单位")
            return True
            
        except Exception as e:
            self.log(f"战斗设置失败：{str(e)}")
            return False
    
    def start_battle(self) -> BattleResult:
        """
        开始战斗
        
        Returns:
            BattleResult: 战斗结果
        """
        if self.phase != BattlePhase.PREPARATION:
            raise ValueError("战斗未正确设置")
        
        self.phase = BattlePhase.COMBAT
        self.current_round = 0
        self.log("=== 战斗开始 ===")
        
        # 战斗主循环
        while self.phase == BattlePhase.COMBAT:
            self.current_round += 1
            self.log(f"\n--- 第 {self.current_round} 回合 ---")
            
            # 检查胜负条件
            if self._check_battle_end():
                break
            
            # 执行回合
            self._execute_round()
            
            # 检查最大回合数
            if self.current_round >= self.max_rounds:
                self.log("达到最大回合数，战斗平局")
                break
        
        # 生成战斗结果
        result = self._generate_battle_result()
        self.phase = BattlePhase.FINISHED
        self.log("=== 战斗结束 ===")
        
        return result
    
    def _execute_round(self):
        """执行一个回合"""
        # 1. 回合开始处理
        self._round_start_processing()
        
        # 2. 生成行动队列
        actions = self._generate_action_queue()
        
        # 3. 执行行动
        for action in actions:
            if action.unit.is_alive():
                self._execute_action(action)
        
        # 4. 回合结束处理
        self._round_end_processing()
    
    def _round_start_processing(self):
        """回合开始处理"""
        all_units = [u for u in self.player_units + self.enemy_units if u.is_alive()]
        
        for unit in all_units:
            # 获得法力值
            unit.gain_mana(self.mana_per_round)
            
            # 更新状态效果
            unit.update_status_effects()
            
            # 减少技能冷却
            if unit.skill_cooldown > 0:
                unit.skill_cooldown -= 1
    
    def _generate_action_queue(self) -> List[BattleAction]:
        """生成行动队列"""
        actions = []
        all_units = [u for u in self.player_units + self.enemy_units if u.is_alive()]
        
        for unit in all_units:
            action = self._decide_unit_action(unit)
            if action:
                actions.append(action)
        
        # 按优先级和速度排序
        actions.sort(key=lambda a: (a.priority, a.unit.get_stats().spd), reverse=True)
        return actions
    
    def _decide_unit_action(self, unit: Unit) -> Optional[BattleAction]:
        """决定单位行动"""
        # 检查是否可以释放技能
        if (unit.active_skill and 
            unit.current_mana >= unit.active_skill.mana_cost and 
            unit.skill_cooldown == 0):
            
            target = self._find_skill_target(unit)
            if target:
                return BattleAction(
                    unit=unit,
                    action_type=ActionType.SKILL,
                    target=target,
                    priority=100  # 技能优先级最高
                )
        
        # 寻找攻击目标
        target = self._find_attack_target(unit)
        if target:
            # 检查是否在攻击范围内
            if self._is_in_range(unit, target):
                return BattleAction(
                    unit=unit,
                    action_type=ActionType.ATTACK,
                    target=target,
                    priority=50
                )
            else:
                # 需要移动到攻击范围
                move_pos = self._find_move_position(unit, target)
                if move_pos:
                    return BattleAction(
                        unit=unit,
                        action_type=ActionType.MOVE,
                        target_position=move_pos,
                        priority=30
                    )
        
        # 默认等待
        return BattleAction(
            unit=unit,
            action_type=ActionType.WAIT,
            priority=0
        )
    
    def _execute_action(self, action: BattleAction):
        """执行行动"""
        unit = action.unit
        
        if action.action_type == ActionType.ATTACK:
            self._execute_attack(unit, action.target)
        elif action.action_type == ActionType.SKILL:
            self._execute_skill(unit, action.target)
        elif action.action_type == ActionType.MOVE:
            self._execute_move(unit, action.target_position)
        elif action.action_type == ActionType.WAIT:
            self.log(f"{unit.name} 等待")
    
    def _execute_attack(self, attacker: Unit, target: Unit):
        """执行攻击"""
        if not target or not target.is_alive():
            return
        
        stats = attacker.get_stats()
        
        # 计算命中
        if random.random() < target.get_stats().dodge:
            self.log(f"{attacker.name} 攻击 {target.name}，但被闪避了")
            return
        
        # 计算伤害
        base_damage = stats.atk
        
        # 暴击判定
        is_crit = random.random() < stats.crit
        if is_crit:
            base_damage = int(base_damage * 2)
            self.log(f"{attacker.name} 对 {target.name} 造成暴击！")
        
        # 应用伤害
        actual_damage = target.take_damage(base_damage, "physical")
        
        # 记录统计
        self.damage_dealt[attacker.id] += actual_damage
        self.damage_taken[target.id] += actual_damage
        
        self.log(f"{attacker.name} 攻击 {target.name}，造成 {actual_damage} 点伤害")
        
        # 检查目标是否死亡
        if not target.is_alive():
            self.log(f"{target.name} 被击败！")
            self._remove_unit_from_board(target)
    
    def _execute_skill(self, caster: Unit, target: Unit):
        """执行技能"""
        skill_result = caster.cast_active_skill([target] if target else [])
        
        if skill_result["success"]:
            skill = skill_result["skill"]
            self.skills_used[caster.id] += 1
            self.log(f"{caster.name} 释放技能：{skill.name}")
            
            # 处理技能效果
            self._apply_skill_effects(caster, skill, target)
        else:
            self.log(f"{caster.name} 技能释放失败：{skill_result.get('message', '未知错误')}")
    
    def _apply_skill_effects(self, caster: Unit, skill, target: Unit):
        """应用技能效果"""
        effects = skill.effects
        
        if "damage" in effects:
            damage = effects["damage"]
            if target and target.is_alive():
                actual_damage = target.take_damage(damage, "magic")
                self.damage_dealt[caster.id] += actual_damage
                self.damage_taken[target.id] += actual_damage
                self.log(f"  造成 {actual_damage} 点魔法伤害")
                
                if not target.is_alive():
                    self.log(f"  {target.name} 被击败！")
                    self._remove_unit_from_board(target)
        
        if "heal" in effects:
            heal_amount = effects["heal"]
            actual_heal = caster.heal(heal_amount)
            self.log(f"  回复 {actual_heal} 点生命值")
        
        if "buff" in effects:
            buff_data = effects["buff"]
            caster.add_buff(skill.name, buff_data, effects.get("duration", 3))
            self.log(f"  获得增益效果：{skill.name}")
    
    def _execute_move(self, unit: Unit, target_position: Tuple[int, int]):
        """执行移动"""
        current_pos = unit.position
        if self._move_unit(unit, target_position):
            self.log(f"{unit.name} 从 {current_pos} 移动到 {target_position}")
        else:
            self.log(f"{unit.name} 移动失败")
    
    def _round_end_processing(self):
        """回合结束处理"""
        # 清理死亡单位
        self.player_units = [u for u in self.player_units if u.is_alive()]
        self.enemy_units = [u for u in self.enemy_units if u.is_alive()]
    
    def _check_battle_end(self) -> bool:
        """检查战斗是否结束"""
        player_alive = len([u for u in self.player_units if u.is_alive()])
        enemy_alive = len([u for u in self.enemy_units if u.is_alive()])
        
        if player_alive == 0 or enemy_alive == 0:
            return True
        
        return False
    
    def _generate_battle_result(self) -> BattleResult:
        """生成战斗结果"""
        player_alive = len([u for u in self.player_units if u.is_alive()])
        enemy_alive = len([u for u in self.enemy_units if u.is_alive()])
        
        if player_alive > enemy_alive:
            winner = "player"
        elif enemy_alive > player_alive:
            winner = "enemy"
        else:
            winner = "draw"
        
        return BattleResult(
            winner=winner,
            total_rounds=self.current_round,
            damage_dealt=self.damage_dealt.copy(),
            damage_taken=self.damage_taken.copy(),
            skills_used=self.skills_used.copy(),
            battle_log=self.battle_log.copy()
        )
    
    # 辅助方法
    def place_unit(self, unit: Unit, position: Tuple[int, int]) -> bool:
        """在指定位置放置单位"""
        x, y = position
        if (0 <= x < self.board_size[0] and 
            0 <= y < self.board_size[1] and 
            self.board[x][y] is None):
            
            self.board[x][y] = unit
            unit.position = position
            return True
        return False
    
    def _move_unit(self, unit: Unit, new_position: Tuple[int, int]) -> bool:
        """移动单位"""
        old_x, old_y = unit.position
        new_x, new_y = new_position
        
        if (0 <= new_x < self.board_size[0] and 
            0 <= new_y < self.board_size[1] and 
            self.board[new_x][new_y] is None):
            
            self.board[old_x][old_y] = None
            self.board[new_x][new_y] = unit
            unit.position = new_position
            return True
        return False
    
    def _remove_unit_from_board(self, unit: Unit):
        """从棋盘移除单位"""
        x, y = unit.position
        if self.board[x][y] == unit:
            self.board[x][y] = None
    
    def _auto_place_units(self, units: List[Unit], side: str):
        """自动放置单位"""
        if side == "player":
            # 玩家单位放在左侧
            start_x = 0
            positions = [(x, y) for x in range(start_x, min(3, self.board_size[0])) 
                        for y in range(self.board_size[1])]
        else:
            # 敌方单位放在右侧
            start_x = max(5, self.board_size[0] - 3)
            positions = [(x, y) for x in range(start_x, self.board_size[0]) 
                        for y in range(self.board_size[1])]
        
        for i, unit in enumerate(units):
            if i < len(positions):
                self.place_unit(unit, positions[i])
    
    def _find_attack_target(self, unit: Unit) -> Optional[Unit]:
        """寻找攻击目标"""
        if unit in self.player_units:
            enemies = [u for u in self.enemy_units if u.is_alive()]
        else:
            enemies = [u for u in self.player_units if u.is_alive()]
        
        if not enemies:
            return None
        
        # 选择最近的敌人
        min_distance = float('inf')
        target = None
        
        for enemy in enemies:
            distance = self._calculate_distance(unit.position, enemy.position)
            if distance < min_distance:
                min_distance = distance
                target = enemy
        
        return target
    
    def _find_skill_target(self, unit: Unit) -> Optional[Unit]:
        """寻找技能目标"""
        # 简化实现：技能目标与攻击目标相同
        return self._find_attack_target(unit)
    
    def _is_in_range(self, attacker: Unit, target: Unit) -> bool:
        """检查是否在攻击范围内"""
        distance = self._calculate_distance(attacker.position, target.position)
        return distance <= attacker.get_stats().rng
    
    def _find_move_position(self, unit: Unit, target: Unit) -> Optional[Tuple[int, int]]:
        """寻找移动位置"""
        # 简化实现：向目标方向移动一格
        ux, uy = unit.position
        tx, ty = target.position
        
        # 计算方向
        dx = 1 if tx > ux else -1 if tx < ux else 0
        dy = 1 if ty > uy else -1 if ty < uy else 0
        
        new_x, new_y = ux + dx, uy + dy
        
        if (0 <= new_x < self.board_size[0] and 
            0 <= new_y < self.board_size[1] and 
            self.board[new_x][new_y] is None):
            return (new_x, new_y)
        
        return None
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """计算两点间距离"""
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def clear_board(self):
        """清空棋盘"""
        self.board = [[None for _ in range(self.board_size[1])] 
                      for _ in range(self.board_size[0])]
        self.battle_log.clear()
        self.damage_dealt.clear()
        self.damage_taken.clear()
        self.skills_used.clear()
    
    def log(self, message: str):
        """记录日志"""
        self.battle_log.append(message)
        print(message)  # 控制台输出
    
    def get_board_state(self) -> List[List[Optional[str]]]:
        """获取棋盘状态（用于显示）"""
        return [[unit.name if unit else None for unit in row] for row in self.board]
    
    def print_board(self):
        """打印棋盘状态"""
        print("\n=== 棋盘状态 ===")
        for y in range(self.board_size[1]):
            row = []
            for x in range(self.board_size[0]):
                unit = self.board[x][y]
                if unit:
                    # 显示单位名称的首字符
                    symbol = unit.name[0] if unit.name else "?"
                    if unit in self.player_units:
                        symbol = f"[{symbol}]"  # 玩家单位用方括号
                    else:
                        symbol = f"({symbol})"  # 敌方单位用圆括号
                else:
                    symbol = " . "
                row.append(symbol)
            print(" ".join(f"{s:^4}" for s in row))
        print()


def run_battle_test():
    """运行战斗系统测试"""
    print("=" * 60)
    print("天界之战 - 战斗系统测试")
    print("=" * 60)
    
    # 导入单位数据
    import json
    from pathlib import Path
    
    data_file = Path(__file__).parent.parent / 'data' / 'celestial_units.json'
    
    if not data_file.exists():
        print("❌ 单位数据文件不存在，无法进行战斗测试")
        return False
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    units_data = data["units"]
    
    # 创建测试单位
    player_units = [Unit.from_json(units_data[0]), Unit.from_json(units_data[1])]
    enemy_units = [Unit.from_json(units_data[2]), Unit.from_json(units_data[3])]
    
    # 创建战斗系统
    battle = BattleSystem()
    
    # 设置战斗
    success = battle.setup_battle(player_units, enemy_units)
    if not success:
        print("❌ 战斗设置失败")
        return False
    
    print("✓ 战斗设置成功")
    battle.print_board()
    
    # 开始战斗
    result = battle.start_battle()
    
    # 输出结果
    print("\n" + "=" * 60)
    print("战斗结果")
    print("=" * 60)
    print(f"胜利方: {result.winner}")
    print(f"总回合数: {result.total_rounds}")
    print(f"伤害统计: {result.damage_dealt}")
    print(f"技能使用: {result.skills_used}")
    
    print("\n🎉 战斗系统测试完成！")
    return True


if __name__ == "__main__":
    run_battle_test()
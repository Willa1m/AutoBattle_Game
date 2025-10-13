"""
游戏管理器 - 协调整个游戏流程
负责玩家管理、游戏状态、回合管理、商店系统等
"""

from enum import Enum
from typing import Dict, List, Optional, Any
import json
import time
from dataclasses import dataclass, asdict

from .unit import Unit
from .battle import BattleSystem
from .synergy import SynergyManager


class GamePhase(Enum):
    """游戏阶段枚举"""
    WAITING = "waiting"          # 等待玩家
    PREPARATION = "preparation"  # 准备阶段（购买、放置单位）
    BATTLE = "battle"           # 战斗阶段
    FINISHED = "finished"       # 游戏结束


class PlayerStatus(Enum):
    """玩家状态枚举"""
    ACTIVE = "active"           # 活跃
    ELIMINATED = "eliminated"   # 被淘汰
    DISCONNECTED = "disconnected"  # 断线


@dataclass
class PlayerStats:
    """玩家统计数据"""
    wins: int = 0
    losses: int = 0
    damage_dealt: int = 0
    damage_taken: int = 0
    units_bought: int = 0
    gold_spent: int = 0
    rounds_survived: int = 0


@dataclass
class Player:
    """玩家类"""
    player_id: str
    name: str
    health: int = 100
    gold: int = 10
    level: int = 1
    experience: int = 0
    units: List[Unit] = None
    board_units: List[Unit] = None  # 棋盘上的单位
    bench_units: List[Unit] = None  # 备战席单位
    status: PlayerStatus = PlayerStatus.ACTIVE
    stats: PlayerStats = None
    last_battle_result: Optional[str] = None
    
    def __post_init__(self):
        if self.units is None:
            self.units = []
        if self.board_units is None:
            self.board_units = []
        if self.bench_units is None:
            self.bench_units = []
        if self.stats is None:
            self.stats = PlayerStats()
    
    def add_experience(self, exp: int):
        """增加经验值，处理升级"""
        self.experience += exp
        
        # 升级所需经验值（简化版本）
        exp_needed = self.level * 2
        
        while self.experience >= exp_needed and self.level < 9:
            self.experience -= exp_needed
            self.level += 1
            exp_needed = self.level * 2
            print(f"玩家 {self.name} 升级到 {self.level} 级！")
    
    def take_damage(self, damage: int):
        """受到伤害"""
        self.health -= damage
        self.stats.damage_taken += damage
        if self.health <= 0:
            self.health = 0
            self.status = PlayerStatus.ELIMINATED
            print(f"玩家 {self.name} 被淘汰！")
    
    def add_gold(self, amount: int):
        """增加金币"""
        self.gold += amount
    
    def spend_gold(self, amount: int) -> bool:
        """花费金币"""
        if self.gold >= amount:
            self.gold -= amount
            self.stats.gold_spent += amount
            return True
        return False
    
    def add_unit_to_bench(self, unit: Unit) -> bool:
        """将单位添加到备战席"""
        if len(self.bench_units) < 9:  # 备战席最多9个单位
            self.bench_units.append(unit)
            return True
        return False
    
    def move_unit_to_board(self, unit: Unit, position: tuple) -> bool:
        """将单位从备战席移动到棋盘"""
        if unit in self.bench_units and len(self.board_units) < 8:  # 棋盘最多8个单位
            self.bench_units.remove(unit)
            unit.position = position
            self.board_units.append(unit)
            return True
        return False
    
    def move_unit_to_bench(self, unit: Unit) -> bool:
        """将单位从棋盘移动到备战席"""
        if unit in self.board_units and len(self.bench_units) < 9:
            self.board_units.remove(unit)
            unit.position = (0, 0)
            self.bench_units.append(unit)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'player_id': self.player_id,
            'name': self.name,
            'health': self.health,
            'gold': self.gold,
            'level': self.level,
            'experience': self.experience,
            'status': self.status.value,
            'stats': asdict(self.stats),
            'board_units_count': len(self.board_units),
            'bench_units_count': len(self.bench_units),
            'last_battle_result': self.last_battle_result
        }


class GameManager:
    """游戏管理器 - 协调整个游戏流程"""
    
    def __init__(self, max_players: int = 8):
        self.max_players = max_players
        self.players: Dict[str, Player] = {}
        self.current_round = 1
        self.phase = GamePhase.WAITING
        self.battle_system = BattleSystem()
        self.synergy_manager = SynergyManager()
        
        # 游戏配置
        self.preparation_time = 30  # 准备阶段时间（秒）
        self.max_rounds = 50       # 最大回合数
        
        # 时间管理
        self.phase_start_time = time.time()
        self.phase_duration = 0
        
        # 游戏历史
        self.game_history: List[Dict] = []
        self.battle_results: List[Dict] = []
    
    def add_player(self, player_id: str, name: str) -> bool:
        """添加玩家"""
        if len(self.players) >= self.max_players:
            return False
        
        if player_id in self.players:
            return False
        
        player = Player(player_id=player_id, name=name)
        self.players[player_id] = player
        
        print(f"玩家 {name} ({player_id}) 加入游戏")
        
        # 如果达到最小玩家数，可以开始游戏
        if len(self.players) >= 2 and self.phase == GamePhase.WAITING:
            self.start_game()
        
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """移除玩家"""
        if player_id not in self.players:
            return False
        
        player = self.players[player_id]
        player.status = PlayerStatus.DISCONNECTED
        
        print(f"玩家 {player.name} 断线")
        return True
    
    def start_game(self):
        """开始游戏"""
        if len(self.players) < 2:
            print("至少需要2个玩家才能开始游戏")
            return False
        
        self.phase = GamePhase.PREPARATION
        self.current_round = 1
        self.phase_start_time = time.time()
        self.phase_duration = self.preparation_time
        
        # 给每个玩家初始资源
        for player in self.players.values():
            player.add_gold(10)  # 初始金币
            player.add_experience(0)  # 初始经验
        
        print(f"游戏开始！当前 {len(self.players)} 个玩家")
        print(f"第 {self.current_round} 回合 - 准备阶段")
        
        self._record_game_event("game_start", {
            "round": self.current_round,
            "players": [p.name for p in self.players.values()]
        })
        
        return True
    
    def update_game_state(self):
        """更新游戏状态"""
        current_time = time.time()
        elapsed_time = current_time - self.phase_start_time
        
        if self.phase == GamePhase.PREPARATION:
            # 检查准备阶段是否结束
            if elapsed_time >= self.phase_duration:
                self._start_battle_phase()
        
        elif self.phase == GamePhase.BATTLE:
            # 战斗阶段由战斗系统管理，这里检查是否结束
            if self.battle_system.phase.value == "finished":
                self._end_battle_phase()
        
        # 检查游戏是否结束
        self._check_game_end()
    
    def _start_battle_phase(self):
        """开始战斗阶段"""
        self.phase = GamePhase.BATTLE
        self.phase_start_time = time.time()
        
        print(f"第 {self.current_round} 回合 - 战斗阶段")
        
        # 执行所有玩家之间的战斗
        active_players = [p for p in self.players.values() if p.status == PlayerStatus.ACTIVE]
        
        if len(active_players) >= 2:
            self._execute_battles(active_players)
        
        self._record_game_event("battle_phase_start", {
            "round": self.current_round,
            "active_players": len(active_players)
        })
    
    def _execute_battles(self, players: List[Player]):
        """执行战斗"""
        # 简化版本：随机配对战斗
        import random
        
        battle_pairs = []
        available_players = players.copy()
        random.shuffle(available_players)
        
        # 配对玩家
        for i in range(0, len(available_players) - 1, 2):
            player1 = available_players[i]
            player2 = available_players[i + 1]
            battle_pairs.append((player1, player2))
        
        # 如果有奇数个玩家，最后一个玩家轮空
        if len(available_players) % 2 == 1:
            bye_player = available_players[-1]
            print(f"玩家 {bye_player.name} 本回合轮空")
            bye_player.add_gold(1)  # 轮空奖励
        
        # 执行战斗
        for player1, player2 in battle_pairs:
            self._battle_between_players(player1, player2)
    
    def _battle_between_players(self, player1: Player, player2: Player):
        """两个玩家之间的战斗"""
        print(f"战斗：{player1.name} vs {player2.name}")
        
        # 设置战斗
        success = self.battle_system.setup_battle(
            player1.board_units.copy(),
            player2.board_units.copy()
        )
        
        if not success:
            print(f"战斗设置失败：{player1.name} vs {player2.name}")
            return
        
        # 开始战斗
        result = self.battle_system.start_battle()
        
        # 处理战斗结果
        if result == "player_wins":
            winner, loser = player1, player2
        elif result == "enemy_wins":
            winner, loser = player2, player1
        else:
            # 平局，双方都受到少量伤害
            damage = 1
            player1.take_damage(damage)
            player2.take_damage(damage)
            player1.last_battle_result = "draw"
            player2.last_battle_result = "draw"
            print(f"战斗平局：{player1.name} vs {player2.name}")
            return
        
        # 计算伤害（基于失败方剩余单位数量）
        remaining_units = len([u for u in loser.board_units if u.current_hp > 0])
        base_damage = max(1, loser.level)
        damage = base_damage + max(0, len(loser.board_units) - remaining_units)
        
        # 应用结果
        loser.take_damage(damage)
        winner.stats.wins += 1
        winner.stats.damage_dealt += damage
        loser.stats.losses += 1
        
        winner.last_battle_result = "win"
        loser.last_battle_result = "loss"
        
        # 奖励
        winner.add_gold(1)
        winner.add_experience(2)
        loser.add_experience(1)
        
        print(f"战斗结果：{winner.name} 获胜，{loser.name} 受到 {damage} 点伤害")
        
        # 记录战斗结果
        battle_record = {
            "round": self.current_round,
            "player1": player1.name,
            "player2": player2.name,
            "winner": winner.name,
            "damage": damage,
            "battle_duration": self.battle_system.current_round
        }
        self.battle_results.append(battle_record)
    
    def _end_battle_phase(self):
        """结束战斗阶段"""
        print(f"第 {self.current_round} 回合战斗结束")
        
        # 更新玩家统计
        for player in self.players.values():
            if player.status == PlayerStatus.ACTIVE:
                player.stats.rounds_survived = self.current_round
        
        # 进入下一回合
        self.current_round += 1
        
        # 检查是否还有活跃玩家
        active_players = [p for p in self.players.values() if p.status == PlayerStatus.ACTIVE]
        
        if len(active_players) <= 1:
            self._end_game()
        elif self.current_round > self.max_rounds:
            self._end_game()
        else:
            # 开始新的准备阶段
            self.phase = GamePhase.PREPARATION
            self.phase_start_time = time.time()
            self.phase_duration = self.preparation_time
            
            # 给活跃玩家回合奖励
            for player in active_players:
                player.add_gold(5)  # 回合金币奖励
                player.add_experience(1)  # 回合经验奖励
            
            print(f"第 {self.current_round} 回合 - 准备阶段")
    
    def _end_game(self):
        """结束游戏"""
        self.phase = GamePhase.FINISHED
        
        # 确定最终排名
        active_players = [p for p in self.players.values() if p.status == PlayerStatus.ACTIVE]
        eliminated_players = [p for p in self.players.values() if p.status == PlayerStatus.ELIMINATED]
        
        # 按淘汰顺序排序（后淘汰的排名更高）
        eliminated_players.sort(key=lambda p: p.stats.rounds_survived, reverse=True)
        
        final_ranking = active_players + eliminated_players
        
        print("游戏结束！最终排名：")
        for i, player in enumerate(final_ranking, 1):
            print(f"{i}. {player.name} - 生命值: {player.health}, 存活回合: {player.stats.rounds_survived}")
        
        self._record_game_event("game_end", {
            "final_ranking": [{"rank": i+1, "player": p.name, "health": p.health} 
                            for i, p in enumerate(final_ranking)]
        })
    
    def _check_game_end(self):
        """检查游戏是否应该结束"""
        active_players = [p for p in self.players.values() if p.status == PlayerStatus.ACTIVE]
        
        if len(active_players) <= 1 and self.phase != GamePhase.FINISHED:
            self._end_game()
    
    def _record_game_event(self, event_type: str, data: Dict):
        """记录游戏事件"""
        event = {
            "timestamp": time.time(),
            "round": self.current_round,
            "phase": self.phase.value,
            "event_type": event_type,
            "data": data
        }
        self.game_history.append(event)
    
    def get_game_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        current_time = time.time()
        elapsed_time = current_time - self.phase_start_time
        remaining_time = max(0, self.phase_duration - elapsed_time) if self.phase_duration > 0 else 0
        
        return {
            "round": self.current_round,
            "phase": self.phase.value,
            "remaining_time": remaining_time,
            "players": {pid: player.to_dict() for pid, player in self.players.items()},
            "active_players": len([p for p in self.players.values() if p.status == PlayerStatus.ACTIVE]),
            "battle_results": self.battle_results[-5:] if self.battle_results else []  # 最近5场战斗
        }
    
    def get_player_state(self, player_id: str) -> Optional[Dict[str, Any]]:
        """获取特定玩家的状态"""
        if player_id not in self.players:
            return None
        
        player = self.players[player_id]
        state = player.to_dict()
        
        # 添加详细的单位信息
        state['board_units'] = [
            {
                'id': unit.id,
                'name': unit.name,
                'position': unit.position,
                'current_hp': unit.current_hp,
                'max_hp': unit.stats.hp,
                'star_level': unit.star_level
            }
            for unit in player.board_units
        ]
        
        state['bench_units'] = [
            {
                'id': unit.id,
                'name': unit.name,
                'current_hp': unit.current_hp,
                'max_hp': unit.stats.hp,
                'star_level': unit.star_level
            }
            for unit in player.bench_units
        ]
        
        return state
    
    def save_game_state(self, filename: str):
        """保存游戏状态到文件"""
        game_data = {
            "game_state": self.get_game_state(),
            "game_history": self.game_history,
            "battle_results": self.battle_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, ensure_ascii=False, indent=2)
        
        print(f"游戏状态已保存到 {filename}")
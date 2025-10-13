"""
天界之战 - 棋盘管理系统
Board Management System for Battle of the Heavens

负责管理游戏棋盘、单位位置、移动逻辑和棋盘状态
Manages game board, unit positions, movement logic and board state

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


class BoardType(Enum):
    """棋盘类型"""
    BATTLE = "battle"      # 战斗棋盘 8x8
    PREPARATION = "prep"   # 准备棋盘 8x4


class CellType(Enum):
    """格子类型"""
    EMPTY = "empty"        # 空格子
    OCCUPIED = "occupied"  # 被占用
    BLOCKED = "blocked"    # 阻挡格子
    SPECIAL = "special"    # 特殊格子


@dataclass
class Position:
    """位置坐标"""
    x: int
    y: int
    
    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def distance_to(self, other: 'Position') -> float:
        """计算到另一个位置的距离"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def manhattan_distance_to(self, other: 'Position') -> int:
        """计算曼哈顿距离"""
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class BoardCell:
    """棋盘格子"""
    position: Position
    cell_type: CellType
    unit: Optional[Unit] = None
    special_effects: List[str] = None
    
    def __post_init__(self):
        if self.special_effects is None:
            self.special_effects = []
    
    def is_empty(self) -> bool:
        """检查格子是否为空"""
        return self.cell_type == CellType.EMPTY and self.unit is None
    
    def is_occupied(self) -> bool:
        """检查格子是否被占用"""
        return self.unit is not None
    
    def can_place_unit(self) -> bool:
        """检查是否可以放置单位"""
        return self.cell_type in [CellType.EMPTY, CellType.SPECIAL] and self.unit is None


class Board:
    """棋盘管理类"""
    
    def __init__(self, board_type: BoardType = BoardType.BATTLE):
        self.board_type = board_type
        self.width = 8
        self.height = 8 if board_type == BoardType.BATTLE else 4
        
        # 初始化棋盘
        self.cells: Dict[Position, BoardCell] = {}
        self.units: Dict[str, Unit] = {}  # unit_id -> Unit
        self.unit_positions: Dict[str, Position] = {}  # unit_id -> Position
        
        self._initialize_board()
    
    def _initialize_board(self):
        """初始化棋盘格子"""
        for x in range(self.width):
            for y in range(self.height):
                pos = Position(x, y)
                self.cells[pos] = BoardCell(
                    position=pos,
                    cell_type=CellType.EMPTY
                )
    
    def get_cell(self, position: Position) -> Optional[BoardCell]:
        """获取指定位置的格子"""
        return self.cells.get(position)
    
    def is_valid_position(self, position: Position) -> bool:
        """检查位置是否有效"""
        return (0 <= position.x < self.width and 
                0 <= position.y < self.height)
    
    def is_position_empty(self, position: Position) -> bool:
        """检查位置是否为空"""
        if not self.is_valid_position(position):
            return False
        cell = self.get_cell(position)
        return cell and cell.can_place_unit()
    
    def place_unit(self, unit: Unit, position: Position) -> bool:
        """在指定位置放置单位"""
        if not self.is_position_empty(position):
            return False
        
        # 如果单位已经在棋盘上，先移除
        if unit.id in self.unit_positions:
            self.remove_unit(unit.id)
        
        # 放置单位
        cell = self.get_cell(position)
        cell.unit = unit
        cell.cell_type = CellType.OCCUPIED
        
        self.units[unit.id] = unit
        self.unit_positions[unit.id] = position
        unit.position = position
        
        return True
    
    def remove_unit(self, unit_id: str) -> bool:
        """移除单位"""
        if unit_id not in self.unit_positions:
            return False
        
        position = self.unit_positions[unit_id]
        cell = self.get_cell(position)
        
        if cell and cell.unit and cell.unit.id == unit_id:
            cell.unit = None
            cell.cell_type = CellType.EMPTY
            
            del self.units[unit_id]
            del self.unit_positions[unit_id]
            
            return True
        
        return False
    
    def move_unit(self, unit_id: str, new_position: Position) -> bool:
        """移动单位"""
        if unit_id not in self.unit_positions:
            return False
        
        if not self.is_position_empty(new_position):
            return False
        
        # 获取单位
        unit = self.units[unit_id]
        old_position = self.unit_positions[unit_id]
        
        # 移除旧位置
        old_cell = self.get_cell(old_position)
        old_cell.unit = None
        old_cell.cell_type = CellType.EMPTY
        
        # 放置到新位置
        new_cell = self.get_cell(new_position)
        new_cell.unit = unit
        new_cell.cell_type = CellType.OCCUPIED
        
        # 更新记录
        self.unit_positions[unit_id] = new_position
        unit.position = new_position
        
        return True
    
    def get_unit_at(self, position: Position) -> Optional[Unit]:
        """获取指定位置的单位"""
        cell = self.get_cell(position)
        return cell.unit if cell else None
    
    def get_unit_position(self, unit_id: str) -> Optional[Position]:
        """获取单位位置"""
        return self.unit_positions.get(unit_id)
    
    def get_all_units(self) -> List[Unit]:
        """获取所有单位"""
        return list(self.units.values())
    
    def get_units_by_player(self, player_id: str) -> List[Unit]:
        """获取指定玩家的所有单位"""
        # 暂时返回所有单位，因为Unit类没有player_id属性
        return list(self.units.values())
    
    def get_adjacent_positions(self, position: Position, include_diagonal: bool = True) -> List[Position]:
        """获取相邻位置"""
        adjacent = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        if not include_diagonal:
            directions = [(-1, 0), (0, -1), (0, 1), (1, 0)]
        
        for dx, dy in directions:
            new_pos = Position(position.x + dx, position.y + dy)
            if self.is_valid_position(new_pos):
                adjacent.append(new_pos)
        
        return adjacent
    
    def get_units_in_range(self, center: Position, range_value: int) -> List[Tuple[Unit, Position]]:
        """获取范围内的所有单位"""
        units_in_range = []
        
        for unit_id, position in self.unit_positions.items():
            distance = center.manhattan_distance_to(position)
            if distance <= range_value:
                units_in_range.append((self.units[unit_id], position))
        
        return units_in_range
    
    def find_nearest_enemy(self, unit: Unit) -> Optional[Tuple[Unit, Position]]:
        """寻找最近的敌人"""
        unit_pos = self.get_unit_position(unit.id)
        if not unit_pos:
            return None
        
        nearest_enemy = None
        min_distance = float('inf')
        
        for other_unit in self.units.values():
            if other_unit.id != unit.id and other_unit.is_alive():
                other_pos = self.get_unit_position(other_unit.id)
                if other_pos:
                    distance = unit_pos.distance_to(other_pos)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_enemy = (other_unit, other_pos)
        
        return nearest_enemy
    
    def find_path(self, start: Position, end: Position) -> List[Position]:
        """简单的路径查找（A*算法的简化版本）"""
        if not self.is_valid_position(start) or not self.is_valid_position(end):
            return []
        
        if start == end:
            return [start]
        
        # 简单的直线路径（可以后续优化为A*算法）
        path = []
        current = Position(start.x, start.y)
        
        while current != end:
            # 计算下一步方向
            dx = 0 if current.x == end.x else (1 if current.x < end.x else -1)
            dy = 0 if current.y == end.y else (1 if current.y < end.y else -1)
            
            next_pos = Position(current.x + dx, current.y + dy)
            
            # 检查下一步是否可行
            if self.is_valid_position(next_pos):
                path.append(next_pos)
                current = next_pos
            else:
                break
        
        return path
    
    def get_valid_moves(self, unit_id: str, max_distance: int = 1) -> List[Position]:
        """获取单位的有效移动位置"""
        unit_pos = self.get_unit_position(unit_id)
        if not unit_pos:
            return []
        
        valid_moves = []
        
        for x in range(max(0, unit_pos.x - max_distance), 
                      min(self.width, unit_pos.x + max_distance + 1)):
            for y in range(max(0, unit_pos.y - max_distance), 
                          min(self.height, unit_pos.y + max_distance + 1)):
                pos = Position(x, y)
                if (pos != unit_pos and 
                    unit_pos.manhattan_distance_to(pos) <= max_distance and
                    self.is_position_empty(pos)):
                    valid_moves.append(pos)
        
        return valid_moves
    
    def clear_board(self):
        """清空棋盘"""
        self.units.clear()
        self.unit_positions.clear()
        
        for cell in self.cells.values():
            cell.unit = None
            cell.cell_type = CellType.EMPTY
    
    def get_board_state(self) -> Dict:
        """获取棋盘状态（用于保存/加载）"""
        return {
            "board_type": self.board_type.value,
            "width": self.width,
            "height": self.height,
            "units": {
                unit_id: {
                    "unit_data": unit.to_dict(),
                    "position": {"x": pos.x, "y": pos.y}
                }
                for unit_id, unit in self.units.items()
                if unit_id in self.unit_positions
                for pos in [self.unit_positions[unit_id]]
            }
        }
    
    def load_board_state(self, state: Dict):
        """加载棋盘状态"""
        self.clear_board()
        
        if "units" in state:
            for unit_id, unit_data in state["units"].items():
                # 重建单位对象（需要Unit类支持from_dict方法）
                unit = Unit.from_json(unit_data["unit_data"])
                position = Position(
                    unit_data["position"]["x"],
                    unit_data["position"]["y"]
                )
                self.place_unit(unit, position)
    
    def display_board(self) -> str:
        """显示棋盘（用于调试）"""
        board_str = "\n棋盘状态:\n"
        board_str += "  " + " ".join([f"{i:2}" for i in range(self.width)]) + "\n"
        
        for y in range(self.height):
            row_str = f"{y:2} "
            for x in range(self.width):
                pos = Position(x, y)
                cell = self.get_cell(pos)
                if cell and cell.unit:
                    # 显示单位名称的首字符
                    unit_char = cell.unit.name[0] if cell.unit.name else "U"
                    row_str += f"{unit_char:2} "
                else:
                    row_str += " . "
            board_str += row_str + "\n"
        
        return board_str


def run_board_test():
    """运行棋盘系统测试"""
    print("🎮 开始棋盘系统测试...")
    
    # 创建战斗棋盘
    board = Board(BoardType.BATTLE)
    print(f"创建了 {board.width}x{board.height} 的战斗棋盘")
    
    # 加载单位数据进行测试
    try:
        with open('data/celestial_units.json', 'r', encoding='utf-8') as f:
            units_data = json.load(f)
        
        # 创建测试单位
        test_units = []
        for i, unit_data in enumerate(units_data["units"][:4]):
            unit = Unit.from_json(unit_data)
            # unit_id不再需要，使用unit.id
            # player_id不再需要，Unit类没有这个属性
            test_units.append(unit)
        
        # 测试单位放置
        positions = [Position(0, 0), Position(1, 0), Position(6, 7), Position(7, 7)]
        for unit, pos in zip(test_units, positions):
            success = board.place_unit(unit, pos)
            print(f"放置 {unit.name} 到 ({pos.x}, {pos.y}): {'成功' if success else '失败'}")
        
        # 显示棋盘
        print(board.display_board())
        
        # 测试移动
        unit_to_move = test_units[0]
        new_pos = Position(2, 1)
        success = board.move_unit(unit_to_move.id, new_pos)
        print(f"移动 {unit_to_move.name} 到 ({new_pos.x}, {new_pos.y}): {'成功' if success else '失败'}")
        
        # 测试寻找最近敌人
        nearest = board.find_nearest_enemy(test_units[0])
        if nearest:
            enemy, enemy_pos = nearest
            print(f"{test_units[0].name} 的最近敌人是 {enemy.name} 在 ({enemy_pos.x}, {enemy_pos.y})")
        
        # 测试获取有效移动位置
        valid_moves = board.get_valid_moves(test_units[0].id, 2)
        print(f"{test_units[0].name} 的有效移动位置: {[(pos.x, pos.y) for pos in valid_moves[:5]]}")
        
        # 显示最终棋盘状态
        print("\n最终棋盘状态:")
        print(board.display_board())
        
        print("🎉 棋盘系统测试完成！")
        
    except FileNotFoundError:
        print("❌ 找不到单位数据文件，使用简单测试...")
        
        # 创建简单测试单位
        from core.unit import Stats
        stats = Stats(hp=100, atk=50, def_=10, spd=5, rng=1, mana=0, crit=0.1, dodge=0.05)
        unit = Unit("test_unit", "测试单位", "天庭", "战士", 1, stats)
        # unit_id不再需要，使用unit.id
        # player_id不再需要，Unit类没有这个属性
        
        # 测试基本功能
        success = board.place_unit(unit, Position(3, 3))
        print(f"放置测试单位: {'成功' if success else '失败'}")
        print(board.display_board())
        
        print("🎉 简单棋盘测试完成！")


if __name__ == "__main__":
    run_board_test()
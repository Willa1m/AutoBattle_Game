# 天界之战：中国神话自走棋项目计划书（TRAE AI 适配版）

## 一、项目定位与模板适配核心

### 1.1 项目概述

基于开源模板 [pokemonAutoChess](https://github.com/keldaanCommunity/pokemonAutoChess) 开发的**单机人机自走棋**，主题源自《封神演义》《西游记》，核心玩法为 “神话单位招募 - 阵营 / 职业羁绊激活 - 自动战斗”。



*   **技术栈适配**：复用模板的 “预计算数据 + 控制台测试” 架构，将原模板的 Node.js/React 重构为 **Python+Pygame**（TRAE 生成重点），简化原模板的服务端逻辑（删除 MongoDB/Firebase，改为本地 JSON 存储）。

*   **TRAE 核心目标**：生成可直接编译的模块化代码（单位类、羁绊逻辑、战斗模拟器），且所有功能支持控制台预测试（避免图形交互依赖）。

### 1.2 与原模板的关键复用映射



| 原模板模块（pokemonAutoChess）               | 天界项目对应模块（TRAE 生成）                              | 复用逻辑                                          |
| ------------------------------------- | ---------------------------------------------- | --------------------------------------------- |
| `app/models/precomputed/pokemon.json` | `data/celestial_units.json`                    | 保留 “费用 - 星级 - 属性” 字段结构，替换为神话单位数据              |
| `battleSimulator.js`（战斗逻辑）            | `core/battle_simulator.py`                     | 复用 “属性克制 - 技能触发 - 回合结算” 流程，TRAE 改写为 Python 函数 |
| `synergySystem.js`（羁绊系统）              | `core/synergy_manager.py`                      | 复用 “阈值激活（如 3 人 / 5 人）” 逻辑，TRAE 适配神话阵营 / 职业规则  |
| `itemPool.js`（装备池）                    | `data/item_pool.json` + `core/item_handler.py` | 复用 “装备星级 - 掉落概率” 配置，TRAE 生成装备属性计算函数           |
| 控制台战斗日志                               | `tests/battle_logger.py`                       | 保留原模板的 “文本化战斗输出”，TRAE 生成日志打印函数                |

### 1.3 TRAE 代码生成原则



1.  **模块化优先**：所有核心逻辑拆分为独立类 / 函数（如`Unit`类、`SynergyChecker`函数），便于 TRAE 分步生成与迭代；

2.  **预计算数据分离**：单位属性、羁绊效果、装备参数均存于 JSON 文件（而非硬编码），TRAE 仅需生成 “数据加载 + 解析类”；

3.  **控制台可测试**：所有核心功能（如羁绊触发、伤害计算）需通过命令行调用验证（例：`python tests/``test_synergy.py`` --camp 天庭 --count 3`），TRAE 需生成对应的测试脚本。

## 二、核心设计（含 TRAE 代码生成锚点）

### 2.1 阵营与羁绊系统（TRAE 生成：`core/``synergy_manager.py`）

#### 设计规则

6 大阵营，采用 “3 人基础效果 + 5 人增强效果”（复用原模板的阈值逻辑），平衡早 / 中 / 后期强度：



| 阵营       | 羁绊效果                                     | TRAE 生成锚点（函数 / 字段）                                                                                  | 平衡约束                                     |
| -------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| 天庭（秩序神明） | 3 人：全体 + 20% 真实伤害5 人：全体 + 40% 真实伤害       | 函数：`check_heaven_synergy(unit_list) -> dict`返回：`{"active_count": 3, "bonus": {"true_damage": 0.2}}` | 高阈值避免前期强势，真实伤害仅生效于非 “土系职业” 单位            |
| 地狱（冥界判官） | 3 人：敌方全体 - 20% 生命回复5 人：敌方全体 - 40% 生命回复   | 函数：`check_hell_synergy(unit_list) -> dict`返回：`{"debuff": {"heal_reduction": 0.2}}`                  | 仅对 “生命回复型单位”（如木系）生效，TRAE 需生成 debuff 判断逻辑 |
| 人界（凡间英雄） | 3 人：全体 + 10% 暴击率5 人：全体 + 20% 暴击率         | 字段：`critical_chance_bonus`（在`Synergy`类中定义）                                                          | 暴击伤害固定为 200%，TRAE 无需额外生成随机逻辑             |
| 仙界（修仙道士） | 3 人：全体 + 15% 法力回复5 人：全体 + 30% 法力回复       | 函数：`calc_mana_regen(unit, synergy_bonus) -> float`                                                  | 法力满值触发主动技能，TRAE 需关联`Unit`类的`mana`字段      |
| 妖界（山精野怪） | 3 人：全体 + 10% 混沌伤害（忽略防御）5 人：全体 + 20% 混沌伤害 | 字段：`chaos_damage_bonus`（在`DamageCalculator`类中调用）                                                    | 混沌伤害不触发敌方反击，TRAE 需在伤害计算中加判断              |
| 神兽（祥瑞凶兽） | 3 人：全体 + 15% 闪避5 人：全体 + 30% 闪避           | 函数：`check_dodge(attacker, defender, synergy_bonus) -> bool`                                         | 闪避仅对物理攻击生效，TRAE 需区分 “物攻 / 法攻” 类型         |

#### TRAE 生成要求



*   统一继承`BaseSynergy`类，包含`check_active()`（判断羁绊是否激活）、`apply_bonus()`（应用加成）两个抽象方法；

*   生成`SynergyLoader`类，从`data/synergy_config.json`加载羁绊规则（避免硬编码）。

### 2.2 职业属性系统（TRAE 生成：`core/``class_attr_manager.py`）

7 大职业，采用 “2-5 人本职业加成 +>5 人全体加成”（优化原模板的职业逻辑，增强后期多样性）：



| 职业      | 功能效果                                                  | TRAE 生成锚点                                                 | 依赖模块                                         |
| ------- | ----------------------------------------------------- | --------------------------------------------------------- | -------------------------------------------- |
| 金（金属性）  | 2-5 人：本职业 + 10% 穿刺伤害>5 人：全体 + 20% 穿刺伤害                | 函数：`apply_gold_attr(unit_list, class_count) -> dict`      | 依赖`DamageCalculator`类的`calc_pierce_damage()` |
| 木（木属性）  | 2-5 人：本职业每回合 + 5% 生命回复>5 人：全体每回合 + 10% 生命回复           | 函数：`apply_wood_heal(unit, heal_bonus) -> None`            | 依赖`Unit`类的`health`字段更新逻辑                     |
| 水（水属性）  | 2-5 人：敌方 - 10% 攻速>5 人：敌方 - 20% 攻速                     | 函数：`apply_water_debuff(enemy_list, debuff_bonus) -> None` | 依赖`Unit`类的`attack_speed`字段                   |
| 火（火属性）  | 2-5 人：本职业每回合 + 5% 燃烧伤害（基于敌方最大生命）>5 人：全体每回合 + 10% 燃烧伤害 | 函数：`calc_fire_dot(enemy_max_hp, dot_bonus) -> float`      | 依赖`DebuffManager`类的`add_dot()`               |
| 土（土属性）  | 2-5 人：本职业 + 15% 最大生命>5 人：全体 + 30% 最大生命                | 字段：`max_health_bonus`（在`Unit`类初始化时计算）                     | 无额外依赖，直接作用于基础属性                              |
| 黑暗（暗属性） | 2-5 人：本职业 + 10% 攻击吸血>5 人：全体 + 20% 攻击吸血                | 函数：`apply_dark_vampirism(attacker, damage_dealt) -> None` | 依赖`Unit`类的`health`字段回写                       |
| 光明（光属性） | 2-5 人：本职业 20% 概率净化负面效果>5 人：全体 40% 概率净化                | 函数：`check_light_purify(unit, purify_rate) -> bool`        | 依赖`DebuffManager`类的`remove_debuff()`         |

### 2.3 棋子设计（TRAE 生成：`core/``unit.py` + `data/celestial_units.json`）

#### 核心规则



*   复用原模板的 “1-3 星升级”（3 个相同棋子合成，属性翻倍）与 “1-5 费分级”（高费棋子功能性更强）；

*   每个棋子绑定 “1 个阵营 + 1 个职业”，5 费棋子必为 “阵营核心”（如玉帝 = 天庭 + 金）。

#### 示例棋子数据（`celestial_units.json`，TRAE 生成格式）



```
{

&#x20; "unit\_id": "yu\_di",

&#x20; "name": "玉帝",

&#x20; "camp": "天庭",

&#x20; "class": "金",

&#x20; "cost": 5,

&#x20; "stars": {

&#x20;   "1": {"health": 1200, "attack": 150, "mana\_cost": 100},

&#x20;   "2": {"health": 2400, "attack": 300, "mana\_cost": 100},

&#x20;   "3": {"health": 4800, "attack": 600, "mana\_cost": 80, "passive": "全体天庭单位真实伤害+30%"}

&#x20; },

&#x20; "active\_skill": {

&#x20;   "name": "雷霆审判",

&#x20;   "effect": "对敌方3个随机单位造成500%金属性伤害，并有50%概率附加“麻痹”（1回合无法攻击）",

&#x20;   "mana\_cost": 100

&#x20; },

&#x20; "synergy\_deps": \["天庭", "金"]

}
```

#### TRAE 生成要求



*   `Unit`类需包含`__init__(unit_data)`（加载 JSON 数据）、`level_up()`（星级升级逻辑）、`cast_skill()`（技能释放）三个核心方法；

*   生成`UnitPool`类，实现 “根据玩家等级生成棋子概率”（如玩家等级 5 级时，5 费棋子出现概率 10%），复用原模板的概率算法。

### 2.4 装备系统（TRAE 生成：`core/item_handler.py` + `data/item_pool.json`）

#### 设计规则



*   复用原模板的 “装备星级（1-3 星）+ 类型分类”，调整为 “防御 + 攻击 + 功能（阵营 / 职业转换）” 三类，每个棋子最多装备 4 件；

*   野怪掉落规则：每 5 轮 1 次野怪波，掉落 3 选 1 装备（星级随轮次提升，第四轮后必为 3 星）。

#### TRAE 生成锚点



1.  **装备数据文件**（`item_pool.json`）：包含`item_id`、`type`、`star_effects`（各星级属性）、`drop_round`（掉落轮次范围）；

2.  **ItemHandler 类**：

*   函数`generate_item(round_num) -> dict`：根据轮次生成对应星级装备；

*   函数`apply_item_effect(unit, item) -> None`：为棋子附加装备效果（如 “天庭冠” 将棋子阵营改为 “天庭”）；

1.  **控制台测试函数**：`test_item_effect.py`，可通过命令行验证装备效果（例：`python tests/test_item.py --item 天庭冠 --unit 杨戬`）。

### 2.5 游戏阶段与经济系统（TRAE 生成：`core/round_manager.py`）

#### 阶段规则（复用原模板的 “准备 - 战斗 - 结算” 循环）



| 阶段   | 时长   | TRAE 生成逻辑                                                                 |
| ---- | ---- | ------------------------------------------------------------------------- |
| 准备阶段 | 30 秒 | 生成`Shop`类，实现 “2 金刷新棋子”“购买棋子”“放置棋子到棋盘” 功能                                  |
| 战斗阶段 | 自动   | 调用`battle_simulator.py`，控制台输出战斗日志（例：“玉帝对阎罗王释放雷霆审判，触发金系职业加成，造成 3000 点伤害！”） |
| 结算阶段 | 10 秒 | 生成`Economy`类，计算每轮收入（基础 5 金 + 利息 1-5 金 + 连胜 1-3 金），更新玩家健康值                 |

#### 经济规则（完全复用原模板，TRAE 改写为 Python）



*   利息：每 10 金存款 + 1 金，上限 5 金；

*   连胜：3 连胜 + 1 金，5 连胜 + 2 金，7 连胜及以上 + 3 金；

*   等级提升：消耗 4 金 + 4XP，等级越高，解锁高费棋子概率越高（如等级 8 级解锁 5 费棋子概率 20%）。

## 三、TRAE 开发执行计划

### 3.1 代码生成优先级（分 3 阶段）



| 阶段      | 生成模块                                                                        | 输出物                      | 测试方式（控制台）                                                              |
| ------- | --------------------------------------------------------------------------- | ------------------------ | ---------------------------------------------------------------------- |
| 1（核心基础） | `core/unit.py`、`data/celestial_units.json`、`tests/test_unit.py`             | 可初始化棋子、查看属性、升级星级         | `python tests/test_unit.py --unit 玉帝 --star 3`                         |
| 2（战斗逻辑） | `core/synergy_manager.py`、`core/battle_simulator.py`、`tests/test_battle.py` | 可验证羁绊激活、计算伤害、模拟战斗        | `python tests/test_battle.py --player_team 玉帝,哪吒 --enemy_team 阎罗王,牛魔王` |
| 3（完整流程） | `core/round_manager.py`、`core/item_handler.py`、`main.py`（入口）                | 可运行完整 10 轮游戏，包含经济、装备、野怪波 | `python main.py --mode test --rounds 10`                               |

### 3.2 模板资产复用清单（TRAE 无需重复生成）



1.  **原模板的预计算逻辑**：复用`pokemonAutoChess`的 “棋子概率表”“装备掉落概率表”，仅修改数据内容；

2.  **控制台日志框架**：复用原模板的`logger.js`结构，TRAE 改写为`logger.py`，输出战斗 / 经济关键信息；

3.  **打包配置**：参考原模板的`npm run assetpack`，TRAE 生成`pyinstaller`打包脚本（`build.spec`），将游戏打包为 PC 可执行文件。

### 3.3 测试与优化（符合原模板 “控制台优先” 原则）



1.  **平衡测试**：TRAE 生成`tests/balance_test.py`，模拟 100 轮不同阵营组合的对战，输出胜率报表（如 “天庭 + 金职业胜率 62%→需下调真实伤害至 15%/35%”）；

2.  **BUG 修复**：参考原模板的 “边缘情况处理”（如反射伤害、状态冲突），TRAE 在`battle_simulator.py`中添加 “混沌伤害不触发闪避”“光明净化优先于黑暗吸血” 等判断；

3.  **性能优化**：复用原模板的 “预计算属性” 逻辑，TRAE 在`Unit`类初始化时提前计算星级属性，避免战斗中动态计算卡顿。

## 四、项目风险与 TRAE 适配方案



| 风险点         | 解决方案（TRAE 生成时规避）                                                                                   |
| ----------- | -------------------------------------------------------------------------------------------------- |
| 羁绊效果过强 / 过弱 | TRAE 在`synergy_manager.py`中预留`adjust_bonus()`函数，可动态修改加成百分比（无需重构代码）                                 |
| 图形界面与逻辑耦合   | 所有核心逻辑（战斗、经济）与 Pygame 界面分离，TRAE 生成`ui/pygame_handler.py`仅负责 “数据渲染”，逻辑修改不影响界面                       |
| 代码重复生成      | 严格维护`KEYS.md`（参考原模板），记录所有生成的类 / 函数 / 文件（例：`Unit`类路径`core/unit.py`，作用 “棋子属性管理”），TRAE 每次生成前读取该文件避免重复 |

## 五、Key Citations（核心参考）



1.  [pokemonAutoChess 开源模板](https://github.com/keldaanCommunity/pokemonAutoChess)：核心架构（预计算数据、控制台测试、羁绊系统）；

2.  原模板`docs/development_guide.md`：资产打包与本地测试流程；

3.  原模板`tests/battle_simulator.test.js`：战斗逻辑测试用例（TRAE 参考改写为 Python 测试脚本）。

> （注：文档部分内容可能由 AI 生成）
# Auto Battle Game - 项目关键信息记录

## 项目基本信息

### Git 仓库信息
- **备份Git库**: `https://github.com/Willa1m/AutoBattle_Game.git`
- **参考模板项目**: `https://github.com/keldaanCommunity/pokemonAutoChess`

### 项目概述
基于Pokemon Auto Chess模板的自动战斗游戏项目，采用现代Web技术栈开发。

## 技术架构分析（基于Pokemon Auto Chess）

### 核心技术栈
- **前端**: HTML, CSS, TypeScript
- **后端**: Node.js
- **数据库**: MongoDB
- **认证**: Firebase Authentication
- **构建工具**: npm, assetpack
- **版本控制**: Git (Git Flow工作流)

### 项目结构
```
project-root/
├── src/                    # 源代码目录
├── tests/                  # 测试代码目录
├── docs/                   # 文档目录
├── public/                 # 静态资源
│   ├── src/assets/        # 原始资源文件
│   └── dist/client/assets/ # 打包后资源
├── app/models/precomputed/ # 预计算数据
├── db-commands/           # 数据库脚本
├── .env                   # 环境配置文件
├── RULE.md               # 项目规范文件
└── KEYS.md               # 本文件
```

## 已创建的文件和组件

### 配置文件
- [x] KEYS.md - 项目关键信息记录文件
- [ ] .env - 环境变量配置文件
- [ ] package.json - 项目依赖管理

### 源代码文件
- [ ] 待创建...

### 测试文件
- [ ] 待创建...

## API 接口记录

### 已实现的API
- [ ] 待记录...

### 计划中的API
- [ ] 待规划...

## 数据库设计

### MongoDB 集合
- **botv2**: 机器人数据集合
- **usermetadatas**: 用户元数据集合

### Firebase 配置
- 认证方式: 邮箱/密码 + 匿名登录
- 需要配置的环境变量:
  - FIREBASE_API_KEY
  - FIREBASE_AUTH_DOMAIN
  - FIREBASE_PROJECT_ID
  - FIREBASE_STORAGE_BUCKET
  - FIREBASE_MESSAGING_SENDER_ID
  - FIREBASE_APP_ID
  - FIREBASE_CLIENT_EMAIL
  - FIREBASE_PRIVATE_KEY

## 开发环境配置

### 必需的环境变量
```
MONGO_URI=mongodb://localhost:27017/dev
FIREBASE_API_KEY=<firebase_api_key>
FIREBASE_AUTH_DOMAIN=<firebase_auth_domain>
FIREBASE_PROJECT_ID=<firebase_project_id>
FIREBASE_STORAGE_BUCKET=<firebase_storage_bucket>
FIREBASE_MESSAGING_SENDER_ID=<firebase_messaging_sender_id>
FIREBASE_APP_ID=<firebase_app_id>
FIREBASE_CLIENT_EMAIL=<client_email>
FIREBASE_PRIVATE_KEY=<private_key>
```

### 开发命令
- `npm install` - 安装依赖
- `npm run download-music` - 下载音乐文件
- `npm run assetpack` - 打包资源文件
- `npm run precompute` - 预计算数据
- `npm run dev` - 启动开发服务器 (http://localhost:9000/)
- `npm run build` - 构建生产版本
- `npm run start` - 启动生产服务器
- `npm run t` - 运行翻译工具

## 游戏设计要点

### 核心特性
1. **自动战斗系统** - 基于策略的自动对战机制
2. **角色收集与升级** - 类似Pokemon的角色系统
3. **实时多人对战** - 支持多玩家同时游戏
4. **资源管理** - 音乐、图像等资源的动态加载

### 开发规范遵循
- 禁止图形化测试，所有测试通过控制台代码完成
- 代码文档注释完整
- 文件长度不超过500行
- 遵循TypeScript代码规范

## 项目规范要点总结

### 关键开发约束
1. **KEYS.md管理**: 每次会话开始前必须查阅，避免重复创建
2. **测试规范**: 严格禁止图形化测试，仅使用控制台代码测试
3. **代码质量**: 所有函数和类必须包含清晰文档注释
4. **文件管理**: 单文件不超过500行，超过需拆分
5. **版本控制**: 采用Git Flow工作流，提交前必须通过测试

### 技术栈对比分析
**Pokemon Auto Chess模板**:
- Node.js + TypeScript + MongoDB + Firebase
- 资源打包: assetpack
- 预计算数据机制
- 多语言支持

**我们的项目适配**:
- 遵循项目规范的技术栈选择
- 保持代码结构清晰
- 实现自动化测试覆盖
- 建立完整的文档体系

### 学习要点
1. **架构设计**: 分离前后端，使用预计算优化性能
2. **数据管理**: MongoDB存储游戏数据，Firebase处理用户认证
3. **资源优化**: 动态资源加载和打包策略
4. **测试策略**: 控制台测试确保功能正确性
5. **国际化**: 支持多语言的游戏体验

## 更新日志

### 2025-01-27
- 创建KEYS.md文件
- 分析Pokemon Auto Chess项目架构
- 记录备份Git库信息: https://github.com/Willa1m/AutoBattle_Game.git
- 阅读并理解项目开发规范
- 总结技术架构和设计要点
- 阅读TypeScript适配性分析，确定使用Python+Pygame技术栈
- 阅读天界之战项目计划书，理解游戏设计需求
- **修复战斗系统测试**: 解决了Unit类属性不匹配问题
  - 修复unit_id -> unit.id的引用问题
  - 移除不存在的player_id属性引用
  - 修正Stats参数名称（attack->atk, defense->def_等）
  - 修正setup_battle方法调用参数
  - 修正BattlePhase枚举值引用
  - **结果**: 所有13个战斗系统测试全部通过 ✅

## 新项目开发清单（基于分析文档）

### 技术栈确认
- **最终选择**: Python + Pygame（替代原TypeScript方案）
- **核心原因**: 
  - 控制台测试效率更高（无需编译步骤）
  - TRAE生成Python代码更高效
  - Pygame轻量级UI适合单机游戏
  - 本地JSON存储简化架构

### 阶段1：核心基础模块（优先级：高）
- [ ] `core/unit.py` - 棋子基础类
- [ ] `data/celestial_units.json` - 神话单位数据
- [ ] `tests/test_unit.py` - 单位测试脚本
- [ ] `core/synergy_manager.py` - 羁绊系统管理
- [ ] `core/class_attr_manager.py` - 职业属性管理

### 阶段2：战斗逻辑模块（优先级：高）
- [x] `core/battle.py` - 战斗系统核心类（已完成，包含回合制战斗逻辑）
- [x] `core/board.py` - 棋盘管理系统（已完成，包含8x8棋盘管理和单位位置控制）
- [x] `core/synergy.py` - 协同效果系统（已完成，包含6大阵营和7大职业协同效果）
- [ ] `tests/test_battle.py` - 战斗测试脚本
- [ ] `utils/logger.py` - 日志系统

### 阶段3：游戏系统模块（优先级：中）
- [ ] `core/round_manager.py` - 回合管理器
- [ ] `core/item_handler.py` - 装备系统
- [ ] `data/item_pool.json` - 装备数据池
- [ ] `core/economy.py` - 经济系统
- [ ] `core/shop.py` - 商店系统

### 阶段4：界面与集成（优先级：中）
- [ ] `ui/pygame_handler.py` - Pygame界面处理
- [ ] `main.py` - 主程序入口
- [ ] `tests/balance_test.py` - 平衡性测试
- [ ] `build.spec` - 打包配置

### 游戏设计核心要素
#### 6大阵营系统
1. **天庭**（秩序神明）- 真实伤害加成
2. **地狱**（冥界判官）- 生命回复削弱
3. **人界**（凡间英雄）- 暴击率提升
4. **仙界**（修仙道士）- 法力回复加速
5. **妖界**（山精野怪）- 混沌伤害（忽略防御）
6. **神兽**（祥瑞凶兽）- 闪避能力提升

#### 7大职业属性
1. **金**（金属性）- 穿刺伤害
2. **木**（木属性）- 生命回复
3. **水**（水属性）- 攻速削弱
4. **火**（火属性）- 燃烧DOT
5. **土**（土属性）- 最大生命提升
6. **黑暗**（暗属性）- 攻击吸血
7. **光明**（光属性）- 净化负面效果

### 开发约束与规范
- 严格遵循控制台测试原则，禁止图形化测试
- 所有核心功能必须支持命令行验证
- 数据与代码分离，配置存储在JSON文件中
- 每个模块必须包含完整的文档注释
- 单文件代码不超过500行

---
*本文件将随项目开发进度持续更新*
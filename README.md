# 初中数英思维训练营

一个基于认知科学的单人数学+英语思维训练 Web 应用。

## 核心理念

不是听课，是像健身一样练大脑。每天 90 分钟，6 步训练循环：
预热检索 → 思考触发器 → 三层讲解 → 混合训练 → 费曼输出 → 自我校准

基于 8 大认知科学方法：检索练习、间隔重复（SM-2）、交错练习、费曼技巧、掌握学习、合意困难、元认知校准、深度思考。

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 一键启动
python run.py
```

访问 http://localhost:8000

## 开发模式

```bash
# 后端（端口 8000）
uvicorn backend.main:app --reload

# 前端（端口 5173，自动代理到后端）
cd frontend && npm run dev
```

## 运行测试

```bash
python -m pytest backend/tests/ -v
```

## 管理面板

http://localhost:8000 → 点击"管理"导航链接。可查看 SM-2 调试数据、手动覆盖节点状态、调参、重载内容。

## 技术栈

- **后端**: FastAPI + SQLAlchemy (SQLite) + PyYAML
- **前端**: React 19 + TypeScript + Vite + Tailwind CSS + Zustand
- **算法**: SM-2 间隔重复、交错调度、掌握树解析、自适应路径

## 项目结构

```
math-english-camp/
├── backend/          # Python FastAPI 服务
│   ├── engine/       # 核心算法（SM-2, mastery, interleaver, path_planner, session_builder）
│   ├── content/      # YAML 内容加载与校验
│   ├── routers/      # API 路由（session, progress, admin）
│   ├── services/     # 费曼规则检查
│   └── tests/        # pytest 测试
├── frontend/         # React SPA
│   └── src/
│       ├── components/  # 6 步训练组件 + 共享组件
│       ├── pages/       # Dashboard, TrainPage, AdminPage
│       ├── stores/      # Zustand 状态管理
│       └── api/         # API 客户端
├── content/          # 学习内容（YAML 文件，Git 管理）
│   ├── nodes/        # 10 个知识节点（math/english）
│   └── questions/    # 90 道题目
├── data/             # SQLite 数据库（自动生成）
└── config.yaml       # 全局配置
```

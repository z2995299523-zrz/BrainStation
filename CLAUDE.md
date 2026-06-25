# math-english-camp — 项目级补充说明

> 权威的 CLAUDE.md 位于仓库根目录 `D:\lernning-pro\CLAUDE.md`，包含完整的架构、命令和内容格式文档。本文件仅补充 math-english-camp 子目录特有的细节。

## 重构状态

详见 `REFACTOR_PLAN.md`。核心变化：
1. 学习流从 6 步 TrainWizard → 5 阶段章节流（概念→例题→练习→测试→总结）
2. 新增 AI 编排层（`backend/services/ai_orchestrator.py`）
3. 新增 AI 侧边栏前端组件
4. 内容格式改为两层 YAML（`display` + `ai_context`）
5. 待删除：interleaver、feynman_check、旧 interactives 组件（`session_builder.py` 是旧 6 步流的残余）

## 当前实现状态

- **ChapterEngine** (`backend/engine/chapter_engine.py`) — 新 5 阶段流的核心引擎；驱动内容读取 + SM-2 更新
- **AIOrchestrator** (`backend/services/ai_orchestrator.py`) — AI 上下文组装 + DeepSeek 流式调用
- **AISidebar** (`frontend/src/components/ai/AISidebar.tsx`) — 前端 AI 对话侧边栏
- **LearnPage** (`frontend/src/pages/LearnPage.tsx`) — 新 5 阶段学习页面
- **learnStore** (`frontend/src/stores/learnStore.ts`) — 新学习流程的 Zustand store

## 保留不动的部分
- `backend/database.py`, `models.py`, `config.py`
- `backend/engine/sm2.py`, `mastery.py`, `path_planner.py`
- `backend/routers/progress.py`
- `frontend/pages/Dashboard.tsx`
- `frontend/components/shared/KnowledgeTree.tsx`
- `config.yaml`

## 旧 6 步流（仍存在但不活跃）

`SessionBuilder` (`backend/engine/session_builder.py`) + `Interleaver` (`backend/engine/interleaver.py`) 驱动旧 6 步训练流。问题从 `content/questions/` 目录加载（旧格式 YAML）。Dashboard 仍通过 progress router 间接使用这些组件。

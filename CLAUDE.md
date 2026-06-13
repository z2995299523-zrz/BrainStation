# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"初中数英思维训练营" — a junior-high math & English thinking-skills training app. The backend serves a structured, adaptive learning system with spaced repetition (SM-2), interleaved question scheduling, and Feynman-technique self-checks. The frontend is a React SPA that delivers the training UI.

## Repository Layout

```
math-english-camp/
├── backend/            # Python FastAPI server
│   ├── engine/         # Core training logic (SM-2, scheduling, adaptive path, Feynman check)
│   ├── content/        # Content loading from YAML/Markdown nodes and question banks
│   ├── routers/        # FastAPI route handlers
│   ├── services/       # Business-logic orchestration layer
│   └── tests/          # pytest + httpx test suite
├── frontend/           # React 19 + TypeScript 6 + Vite 8 SPA
│   └── src/
│       ├── App.tsx     # Root component (currently Vite scaffold)
│       ├── App.css     # App-level styles (currently Vite scaffold)
│       ├── main.tsx    # React entry point, mounts <App /> into #root
│       └── index.css   # Global CSS custom properties and resets
├── content/            # Learning content (nodes and questions, split math/english)
├── data/               # SQLite database and runtime data (gitignored except .gitkeep)
└── config.yaml         # Central config for all training parameters
```

## Commands

### Backend (Python)

```bash
# Install dependencies
cd math-english-camp && pip install -r requirements.txt

# Run dev server
uvicorn backend.main:app --reload

# Run all tests
pytest backend/tests/

# Run a single test file
pytest backend/tests/test_<name>.py

# Run a single test function
pytest backend/tests/test_<name>.py::test_<function_name> -v
```

### Frontend (React + TypeScript)

```bash
cd math-english-camp/frontend

# Install dependencies
npm install

# Dev server with HMR
npm run dev

# Type-check and build
npm run build

# Lint
npm run lint

# Preview production build
npm run preview
```

## Architecture & Key Concepts

### Training Flow (6 mandatory steps, configurable in `config.yaml`)

1. **预热检索 (Warmup)** — 8 min, retrieves prior knowledge with varied questions
2. **思考触发器 (Trigger)** — 8 min, primes thinking before new material
3. **三层讲解 (Learn)** — 22 min, presents new nodes in three layers (operation → understand → connect)
4. **混合训练 (Training)** — 22 min, interleaved practice mixing new and review questions
5. **费曼输出 (Feynman)** — 10 min, student explains concepts; backend verifies via rule-based or LLM mode
6. **自我校准 (Calibration)** — 5 min, self-assessment and mastery update

### SM-2 Spaced Repetition (`config.yaml` → `sm2`)

Standard SM-2 algorithm with configurable EF (ease factor), interval progression, and mastery threshold (0.85). Respects weekend skipping. Implemented in `backend/engine/`.

### Interleaving & Adaptive Path (`config.yaml` → `interleaving`, `adaptive_path`)

- Questions are interleaved across math and English domains
- New/review ratio, layer distribution, and variant injection rates are configurable
- Adaptive path weights prioritize: unlearned core nodes (10.0) > unlearned trunk (7.0) > low-mastery in-progress (5.0) > degraded (4.0)

### Content Model

- **Nodes**: Knowledge graph nodes stored under `content/nodes/{math,english}/` — represent concepts to learn
- **Questions**: Practice items under `content/questions/{math,english}/` — tagged with difficulty (1–5), linked to nodes
- Both are loaded by `backend/content/` at startup

### Feynman Verification (`config.yaml` → `feynman`)

Two modes:
- `rule` — heuristic check (min text length ≥ 20, min keyword-match ratio ≥ 0.5)
- `deepseek` / `openai` — LLM-based semantic evaluation (not yet implemented)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend framework | FastAPI 0.115 + uvicorn |
| ORM | SQLAlchemy 2.0 (SQLite) |
| Validation | Pydantic 2.9 |
| Config | PyYAML (`config.yaml`) |
| Testing | pytest 8.3 + httpx 0.28 |
| Frontend framework | React 19 |
| Language | TypeScript 6.0 |
| Bundler | Vite 8 (with Rolldown, Oxc) |
| Linting | ESLint 10 + typescript-eslint 8 |
| CSS | Plain CSS with custom properties (light/dark theme) |

## Current State

The project is in early scaffolding. Backend packages (`engine`, `content`, `routers`, `services`, `tests`) have their `__init__.py` files created but contain no implementation yet. The frontend still has the default Vite + React starter template content. The `config.yaml` is the most complete artifact — it defines the full training domain model and should drive implementation.

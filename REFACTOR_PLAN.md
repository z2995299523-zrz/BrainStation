# 初中数英思维训练营 · 重构架构方案

> **核心变化**：从"预写死的电子书"变成"结构化章节 + 可按需唤醒的 AI 导师"。
>
> **复用现有代码**：SM-2 引擎、掌握树、进度追踪、Dashboard、数据库——这些不动。
> **重构的部分**：内容格式、学习流 UI、新增 AI 侧边栏和编排层。

---

## 一、产品模型

### 一句话

一个结构化的初中数英学习工具——用户按章节顺序学习，每章有讲解→例题→练习→测试，任何卡住的地方点开侧边栏，AI 导师已经知道你在学什么、哪里薄弱，直接针对性解答。

### 用户的一天

```
打开网站 → Dashboard 看到两科进度
    ↓
点击"数学" → 进入学习界面
    ↓
系统自动定位到当前章节（上次学到哪 / 下一章是什么）
    ↓
┌─────────────────────────────────────────┐
│  因式分解                                 │
│                                          │
│  📖 概念    学了平方差公式和完全平方公式       │
│  💡 例题    看了 3 个例题的逐步拆解          │
│  ✏️ 练习    做了 5 道题，错了 1 道           │
│             → 错了的那道题显示详细解法       │
│             → "还是不理解？" 点 💬          │
│                                          │
│  ┌──────────────────────┐               │
│  │ 💬 AI 导师            │               │
│  │ 已知: 你在学因式分解    │               │
│  │ 薄弱: 平方差公式       │               │
│  │ 刚错: x²-9 → 你写了    │               │
│  │       (x-3)²  ❌       │               │
│  │ 正确: (x+3)(x-3)       │               │
│  │                        │               │
│  │ 你: 为什么是(x+3)(x-3)  │               │
│  │     而不是(x-3)²？     │               │
│  │                        │               │
│  │ AI: 好问题！你犯了最     │               │
│  │ 常见的错误。我们拿      │               │
│  │ 面积来想...（几何解释）  │               │
│  └──────────────────────┘               │
│                                          │
│  📝 测试    本章综合测试 10 题，正确 8/10     │
│  ✅ 完成    掌握度 → 0.78，下次复习：3天后    │
│                                          │
│  [下一章：一元二次方程 →]                   │
└─────────────────────────────────────────┘
```

---

## 二、学习流设计（每章 5 个阶段）

```
┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
│ 概念   │ → │ 例题   │ → │ 练习   │ → │ 测试   │ → │ 总结   │
│ 5 min  │   │ 10 min │   │ 10 min │   │ 15 min │   │ 3 min  │
└────────┘   └────────┘   └────────┘   └────────┘   └────────┘
  看懂定义      看懂怎么用     自己试试       检验掌握      知道自己
  和公式                                        程度         学了什么
```

| 阶段 | 用户看到 | 交互 | AI 能帮什么 |
|------|---------|------|-----------|
| ① 概念 | 章节标题 + 核心定义 + 公式卡片 | 阅读、翻页 | "用更简单的方式解释" |
| ② 例题 | 2-3 个例题，每例有逐步拆解 | 点击展开每步，"下一步" | "这一步是什么意思？" |
| ③ 练习 | 5-8 道练习题 | 作答→即时判断→显示解法 | "为什么我的答案是错的？" |
| ④ 测试 | 8-12 道综合题（混合难度） | 作答→SM-2 记录→逐题反馈 | "这题能再讲一遍吗？" |
| ⑤ 总结 | 本章掌握度、错题回顾、关键点 | 阅读，进入下一章 | "帮我总结一下本章重点" |

**任何时刻**：点右下角 💬 浮钮或侧边栏图标，AI 导师弹出。

---

## 三、内容格式（两层结构）

不再把完整讲解写死。给用户看的精简，给 AI 看的丰满。

```yaml
# content/nodes/math/14-factorization.yaml

slug: factorization
subject: math
title: "因式分解"
tier: core
difficulty: 3
prerequisites: [polynomials]

# ═══════════════════════════════════════
# 第一层：给用户看的（精简，固定）
# ═══════════════════════════════════════
display:
  concept:
    summary: "把一个多项式写成几个整式乘积的形式"
    sections:
      - title: "方法一：提公因式法"
        content: "找出各项的公因式，提到括号外面。\n\n`ax + ay = a(x + y)`"
      - title: "方法二：平方差公式"
        content: "`a² - b² = (a + b)(a - b)`\n\n只要两项都是完全平方，中间是减号，就能用这个公式。"
      - title: "方法三：完全平方公式"
        content: "`a² + 2ab + b² = (a + b)²`\n`a² - 2ab + b² = (a - b)²`"

  examples:
    - title: "平方差"
      problem: "分解 x² - 4"
      steps:
        - "第 1 步：识别——x² 和 4 都是完全平方，中间是减号 → 用平方差公式"
        - "第 2 步：确定 a 和 b——a = x，b = 2（因为 2² = 4）"
        - "第 3 步：代入公式——(x + 2)(x - 2)"
      answer: "(x + 2)(x - 2)"
    
    - title: "完全平方"
      problem: "分解 x² + 6x + 9"
      steps:
        - "第 1 步：识别——三项，首尾都是完全平方，中间是 2×首×尾"
        - "第 2 步：验证——x² = (x)²，9 = 3²，2×x×3 = 6x ✓"
        - "第 3 步：代入公式——(x + 3)²"
      answer: "(x + 3)²"
    
    - title: "先提公因式"
      problem: "分解 2x² - 8"
      steps:
        - "第 1 步：有公因式吗？2 可以提出来 → 2(x² - 4)"
        - "第 2 步：括号里还能分解吗？x² - 4 = (x + 2)(x - 2)"
        - "第 3 步：最终答案——2(x + 2)(x - 2)"
      answer: "2(x + 2)(x - 2)"

  practice:
    - id: "fac-prac-001"
      stem: "分解 x² - 9"
      answer: "(x + 3)(x - 3)"
      hints: ["这是平方差形式吗？", "a 和 b 分别是多少？"]
    
    - id: "fac-prac-002"
      stem: "分解 x² - 4x + 4"
      answer: "(x - 2)²"
      hints: ["三项都是什么？", "检查中间项是否等于 2ab"]
    
    - id: "fac-prac-003"
      stem: "分解 3x² - 12"
      answer: "3(x + 2)(x - 2)"
      hints: ["先看看有没有公因式", "提完之后括号里是什么？"]
    
    - id: "fac-prac-004"
      stem: "分解 x² + 8x + 16"
      answer: "(x + 4)²"
      hints: ["首尾都是完全平方吗？", "中间项 8x = 2×x×?"]
    
    - id: "fac-prac-005"
      stem: "分解 x² - 1"
      answer: "(x + 1)(x - 1)"
      hints: ["1 也是完全平方，1 = 1²"]

  test:
    - id: "fac-test-001"
      stem: "分解 x² - 25"
      answer: "(x + 5)(x - 5)"
      difficulty: 1
      layer: operation
    
    - id: "fac-test-002"
      stem: "分解 x² - 10x + 25"
      answer: "(x - 5)²"
      difficulty: 2
      layer: operation
    
    - id: "fac-test-003"
      stem: "分解 4x² - 36"
      answer: "4(x + 3)(x - 3)"
      difficulty: 2
      layer: operation
    
    - id: "fac-test-004"
      stem: "小华说 x² - 4 分解为 (x - 2)²。他错在哪？"
      answer: "x² - 4 是平方差不是完全平方，应该分解为 (x + 2)(x - 2)"
      difficulty: 3
      layer: understand
    
    - id: "fac-test-005"
      stem: "分解 x⁴ - 16（提示：可以分两次用平方差公式）"
      answer: "(x² + 4)(x + 2)(x - 2)"
      difficulty: 4
      layer: connect
    
    - id: "fac-test-006"
      stem: "分解 x² + 7x + 12"
      answer: "(x + 3)(x + 4)"
      difficulty: 2
      layer: operation
    
    - id: "fac-test-007"
      stem: "分解 x² - x - 6"
      answer: "(x - 3)(x + 2)"
      difficulty: 3
      layer: operation
    
    - id: "fac-test-008"
      stem: "一个长方形的面积是 x² - 9，一边长 x - 3，另一边长是多少？"
      answer: "x + 3"
      difficulty: 3
      layer: connect

# ═══════════════════════════════════════
# 第二层：给 AI 用的教案（不展示给用户）
# ═══════════════════════════════════════
ai_context:
  topic_summary: "因式分解是初中代数核心技能，是把多项式写成几个整式乘积的过程。它和乘法公式互为逆运算。掌握因式分解对解一元二次方程至关重要。"
  
  key_insights:
    - "因式分解本质是'从和变成积'——和小学的分解质因数同一种思维"
    - "平方差公式和完全平方公式是最常用的两个工具"
    - "看到三项先想完全平方公式或十字相乘法，看到两项先想平方差或提公因式"

  common_mistakes:
    - mistake: "把平方差当成完全平方"
      example: "x² - 4 分解成 (x - 2)²"
      why: "学生看到两项都是平方就条件反射用了完全平方公式，忽略了中间必须有 2ab 项"
      how_to_explain: "画两个正方形：大方 x×x，小方 2×2，挖掉小方后剩下的面积怎么切成两个矩形？"
    
    - mistake: "忘记先提取公因式"
      example: "4x² - 36 直接套平方差公式得到 (2x+6)(2x-6)"
      why: "虽然不算错，但不是最简形式"
      how_to_explain: "先看能不能提取公因数——这是第一反应"
    
    - mistake: "符号错误"
      example: "x² + 6x - 9 写成 (x+3)²"
      why: "常数项 -9 不是完全平方，完全平方公式要求 b² 为正"
      how_to_explain: "完全平方公式的常数项一定是正的——因为它是 b²"

  alternate_explanations:
    - method: "面积模型（几何直觉）"
      when_to_use: "学生对代数公式感到抽象时"
      prompt: "画一个大正方形边长 x，挖掉一个小正方形边长 2。剩下的 L 形面积怎么算？切成两个矩形：(x+2)×(x-2)。这就是 x²-4 = (x+2)(x-2)。"
    
    - method: "数字类比（从熟悉到陌生）"
      when_to_use: "学生需要建立直觉时"
      prompt: "12 可以写成 3×4，这叫分解质因数。x²-4 可以写成 (x+2)(x-2)，这叫因式分解。本质上都是'把复杂的东西拆成简单的东西'。"
    
    - method: "验算推导（反向验证）"
      when_to_use: "学生不确定答案是否正确时"
      prompt: "不确定(x+3)(x-3)对不对？乘回去看看。用分配律：(x+3)(x-3) = x²-3x+3x-9 = x²-9。对上了！你的答案永远可以自己验算。"

  question_templates:
    difficulty_1_2: "出 2 道直接套平方差公式的题，数字简单（如 x²-9, x²-16）"
    difficulty_3: "出 1 道需要先提公因式的题（如 3x²-27）"
    difficulty_4: "出 1 道应用场景题（如结合几何图形的面积计算）"
```

---

## 四、AI 侧边栏设计

### 交互方式

```
┌──────────────────────────────────────────────────────┐
│  学习主界面                              [≡] [💬]    │
│                                                       │
│  因式分解 > 例题 > 例 2 / 3                            │
│                                                       │
│  分解 2x² - 8                                         │
│  ┌─────────────────────────────────────┐             │
│  │ 第 1 步：有公因式吗？                  │             │
│  │ 2 可以提出来 → 2(x² - 4)             │             │
│  │                                      │             │
│  │ 第 2 步：括号里还能分解吗？             │             │
│  │ x² - 4 = (x+2)(x-2)                 │             │
│  │                                      │             │
│  │ 第 3 步：最终答案                      │             │
│  │ 2(x+2)(x-2)                         │             │
│  └─────────────────────────────────────┘             │
│                                                       │
│  "还是不太理解为什么 x²-4 能拆成 (x+2)(x-2)"           │
│                               ┌──────────────────────┐│
│  ┌──────────────────────┐     │  💬 AI 导师           ││
│  │ 继续下一题 →          │     │                      ││
│  └──────────────────────┘     │  上下文已自动注入：     ││
│                               │  📍 因式分解·例题2     ││
│                               │  📊 本章练习正确率 3/5 ││
│                               │  ⚠️ 薄弱点: 平方差公式  ││
│                               │                      ││
│                               │  👤 为什么 x²-4 能     ││
│                               │  拆成 (x+2)(x-2)？    ││
│                               │                      ││
│                               │  🤖 好问题！我们换个   ││
│                               │  方式看——用面积。      ││
│                               │                      ││
│                               │  想象一个 x×x 的正方形 ││
│                               │  ┌────┬────┐         ││
│                               │  │    │ 2  │         ││
│                               │  │ x² │    │         ││
│                               │  │    │    │         ││
│                               │  ├────┴────┤         ││
│                               │  │ 扣除 4  │         ││
│                               │  └─────────┘         ││
│                               │                      ││
│                               │  挖掉 2×2 后剩下的面积  ││
│                               │  恰好是 (x+2)(x-2)    ││
│                               │                      ││
│                               │  [懂了！] [再举一例]   ││
│                               └──────────────────────┘│
└──────────────────────────────────────────────────────┘
```

### 上下文注入模板

每次用户打开 AI 侧边栏或发消息时，后端自动组装：

```python
def build_ai_context(user_id, current_chapter, current_stage):
    return f"""
【当前学习状态】
- 学科：{chapter.subject}（数学/英语）
- 章节：{chapter.title}（{chapter.slug}）
- 当前阶段：{current_stage}（概念/例题/练习/测试）
- 所在位置：{current_position}（如：例题 2/3）

【学习进度】
- 本章练习正确率：{chapter_accuracy}%
- 本章测试正确率：{test_accuracy}%
- 累计学习天数：{streak_days}

【薄弱点】
{weak_points}

【前置知识掌握情况】
{prerequisite_status}

【AI 教案参考】
{ai_context_from_yaml}
"""
```

### 快捷操作（不用打字）

侧边栏顶部提供快捷按钮，点击即发送预设指令：

```
[🤔 换个方式讲] [📝 再出一道题] [❌ 我错在哪] [📋 总结本章]
```

---

## 五、技术架构

### 整体拓扑

```
┌─────────────────────────────────────────────┐
│  前端 (React + Vite + Tailwind)              │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Dashboard │  │ LearnPage│  │ AdminPage│  │
│  │          │  │          │  │          │  │
│  │ 掌握树    │  │ 章节主界面 │  │ SM-2调试  │  │
│  │ 进度卡片  │  │ 阶段导航  │  │ 参数调节  │  │
│  └──────────┘  │ 题目交互  │  └──────────┘  │
│                │ AI侧边栏  │                │
│                └──────────┘                │
└────────────────────┬────────────────────────┘
                     │ REST + SSE(流式)
                     ▼
┌─────────────────────────────────────────────┐
│  后端 (FastAPI)                              │
│                                              │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
│  │content   │ │progress  │ │ai            │ │
│  │router    │ │router    │ │router        │ │
│  │          │ │          │ │              │ │
│  │GET 章节   │ │GET 进度   │ │POST /ask     │ │
│  │POST 答题  │ │GET 掌握树 │ │POST /generate│ │
│  └──────────┘ └──────────┘ └──────┬───────┘ │
│                                    │         │
│                          ┌─────────▼───────┐ │
│                          │ AI 编排层        │ │
│                          │                 │ │
│                          │ build_context() │ │
│                          │ call_llm()      │ │
│                          │ stream_response()│ │
│                          └────────┬────────┘ │
│                                   │          │
│  ┌──────────┐  ┌──────────┐     │          │
│  │SM-2 引擎 │  │掌握树     │     │          │
│  │间隔重复   │  │依赖解析   │     │          │
│  └──────────┘  └──────────┘     │          │
│                                   │          │
└───────────────────────────────────┼──────────┘
                                    │
                          ┌─────────▼──────────┐
                          │  LLM API           │
                          │  DeepSeek / OpenAI │
                          └────────────────────┘
```

### 复用 vs 新增

| 模块 | 现有代码 | 处理方式 |
|------|---------|---------|
| `backend/database.py` | ✅ | **保留**，不变 |
| `backend/models.py` | ✅ | **保留**，不变 |
| `backend/config.py` | ✅ | **保留**，不变 |
| `backend/engine/sm2.py` | ✅ | **保留**，不变 |
| `backend/engine/mastery.py` | ✅ | **保留**，小改 |
| `backend/engine/interleaver.py` | ⚠️ | **废弃**，数英已分开不需要交错 |
| `backend/engine/path_planner.py` | ✅ | **保留**，微调 |
| `backend/engine/session_builder.py` | ⚠️ | **重写**，新流是章节5阶段 |
| `backend/content/loader.py` | ⚠️ | **修改**，适配新两层 YAML |
| `backend/routers/session.py` | ⚠️ | **拆分为** `content.py` + `ai.py` |
| `backend/routers/progress.py` | ✅ | **保留**，不变 |
| `backend/routers/admin.py` | ❌ | **新建**（之前没实现） |
| `backend/services/feynman_check.py` | ⚠️ | **删除**，由 LLM 替代 |
| `backend/services/ai_orchestrator.py` | ❌ | **新建核心模块** |
| `frontend/pages/Dashboard.tsx` | ✅ | **保留**，微调 |
| `frontend/pages/TrainPage.tsx` | ⚠️ | **重写** → `LearnPage.tsx` |
| `frontend/components/train/*` | ⚠️ | **删掉**，重建为 `learn/*` |
| `frontend/components/shared/KnowledgeTree.tsx` | ✅ | **保留** |
| `frontend/components/ai/AISidebar.tsx` | ❌ | **新建核心组件** |
| `frontend/stores/trainStore.ts` | ⚠️ | **重写** → `learnStore.ts` |
| `frontend/components/interactives/*` | ⚠️ | **删除**（Claude Code 自行发挥的） |

---

## 六、AI 编排层设计

### 核心服务：`backend/services/ai_orchestrator.py`

```python
class AIOrchestrator:
    """AI 导师编排器"""
    
    def __init__(self, loader: ContentLoader, config: dict):
        self.loader = loader
        self.config = config
        self.client = None  # DeepSeek / OpenAI client
    
    async def ask(
        self,
        user_id: int,
        chapter_slug: str,
        current_stage: str,    # "concept" | "examples" | "practice" | "test" | "summary"
        current_position: str, # e.g. "example 2/3" or "practice question 4"
        user_question: str,
        db: Session,
    ) -> AsyncGenerator[str, None]:
        """
        用户提问 → 返回流式 AI 回复
        
        1. 组装上下文
        2. 调用 LLM
        3. 流式返回给前端
        """
        context = self._build_context(user_id, chapter_slug, current_stage, current_position, db)
        system_prompt = self._build_system_prompt(context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question},
        ]
        
        async for chunk in self._stream_llm(messages):
            yield chunk
    
    async def generate_extra_practice(
        self, chapter_slug: str, difficulty: int, db: Session
    ) -> dict:
        """按需生成额外练习题"""
        # 从 YAML 的 question_templates 获取出题约束
        # 调用 LLM 生成符合格式的题目
        pass
    
    def _build_context(self, user_id, chapter_slug, current_stage, current_position, db):
        """组装上下文注入数据"""
        # 1. 当前章节信息
        node = self.loader.get_node(chapter_slug)
        ai_ctx = node.get("ai_context", {})
        
        # 2. 用户进度
        progress = db.query(UserProgress).filter_by(node_slug=chapter_slug).first()
        
        # 3. 最近的错题
        recent_errors = (
            db.query(QuestionAttempt)
            .filter_by(node_slug=chapter_slug, is_correct=False)
            .order_by(QuestionAttempt.created_at.desc())
            .limit(5).all()
        )
        
        # 4. 前置知识掌握状态
        prerequisites = node.get("prerequisites", [])
        prereq_status = {}
        for p_slug in prerequisites:
            p = db.query(UserProgress).filter_by(node_slug=p_slug).first()
            if p:
                prereq_status[p.node_slug] = p.mastery_level
        
        return {
            "chapter": {
                "title": node["title"],
                "slug": chapter_slug,
                "current_stage": current_stage,
                "current_position": current_position,
            },
            "ai_context": ai_ctx,
            "user_progress": {
                "mastery": progress.mastery_level if progress else 0,
                "practice_accuracy": self._calc_accuracy(db, chapter_slug, "practice"),
                "test_accuracy": self._calc_accuracy(db, chapter_slug, "test"),
            },
            "recent_errors": [
                {"stem": e.question_stem, "user_answer": e.user_answer}
                for e in recent_errors
            ],
            "prerequisite_status": prereq_status,
        }
    
    def _build_system_prompt(self, context: dict) -> str:
        """组装 System Prompt"""
        return f"""你是一位耐心且善于用多种方式讲解的初中数学和英语老师。

【学生当前状态】
- 正在学习：{context['chapter']['title']}
- 当前阶段：{context['chapter']['current_stage']}
- 具体位置：{context['chapter']['current_position']}
- 本章掌握度：{context['user_progress']['mastery']}

【教学参考】（你会用到但不需要全说）
{json.dumps(context['ai_context'], ensure_ascii=False, indent=2)}

【学生薄弱点】
{self._format_errors(context['recent_errors'])}

【教学原则】
1. 不要直接给答案——引导学生自己发现
2. 如果学生说"没懂"，换一种方式解释（几何→代数→类比→举例，每次换角度）
3. 用初中生能理解的语言，避免术语堆砌
4. 回答末尾可以问一个引导性问题，确认学生是否真的懂了
5. 每次回答控制在 200 字以内，除非学生要求详细展开
"""
```

### API 端点

```
POST /api/ai/ask
  请求: { chapter_slug, current_stage, current_position, question }
  响应: SSE 流式文本

POST /api/ai/generate-practice
  请求: { chapter_slug, difficulty }
  响应: { stem, answer, hints }

POST /api/ai/rephrase
  请求: { chapter_slug, current_stage, current_position }
  响应: 用另一种方式重新解释当前内容（流式）
```

---

## 七、前端 LearnPage 设计

### 页面布局

```
┌──────────────────────────────────────────────────────┐
│  ← 返回  因式分解                    [≡ 目录] [💬 导师] │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌─ 阶段指示器 ───────────────────────────────────┐  │
│  │  ① 概念 ✅  →  ② 例题 🔵  →  ③ 练习  →  ④ 测试  →  ⑤ 总结  │
│  └──────────────────────────────────────────────────┘  │
│                                                       │
│  ┌─ 主内容区 ─────────────────────────────────────┐  │
│  │                                                  │  │
│  │  ## 方法二：平方差公式                            │  │
│  │                                                  │  │
│  │  `a² - b² = (a + b)(a - b)`                     │  │
│  │                                                  │  │
│  │  只要两项都是完全平方，中间是减号，就能用。          │  │
│  │                                                  │  │
│  │  ┌────────────────────────────┐                  │  │
│  │  │ 例：分解 x² - 4             │                  │  │
│  │  │ x² 是 x 的平方，4 是 2 的平方 │                  │  │
│  │  │ 所以 x² - 4 = (x+2)(x-2)    │                  │  │
│  │  └────────────────────────────┘                  │  │
│  │                                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │ [上一页]                           [下一页 →]     │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### 题目交互（练习/测试阶段）

```
┌──────────────────────────────────────────────────┐
│  第 3 题 / 共 5 题                                 │
│                                                    │
│  分解 3x² - 12                                     │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │ 3(x+2)(x-2)                           [提交]  │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│  ┌─ 提交后的反馈 ──────────────────────────────┐  │
│  │  ✅ 正确！                                      │  │
│  │  你的思路：先提公因式 3，得到 3(x²-4)，            │  │
│  │  再用平方差分解 x²-4 = (x+2)(x-2)               │  │
│  │                                                │  │
│  │  [💬 还有疑问?]                                 │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

### AI 侧边栏组件

```typescript
// frontend/src/components/ai/AISidebar.tsx

// Props:
//   open: boolean
//   onClose: () => void
//   context: { chapter_slug, current_stage, current_position }

// 状态：
//   messages: Array<{role: 'user'|'assistant', content: string}>
//   streaming: boolean
//   inputValue: string

// 快捷操作：
//   presets: ['🤔 换个方式讲', '📝 再出一道题', '❌ 我错在哪', '📋 总结本章']
//   点击直接发送预设文本，无需输入

// 每次打开时：
//   如果 messages 为空 → 显示 AI 欢迎语："你在学【因式分解·例题2】，
//   有什么不懂的可以问我。或者试试："
//   然后展示 presets 按钮
```

---

## 八、数据库改动

### 新增表

```sql
-- AI 对话历史（可选，方便回溯）
CREATE TABLE IF NOT EXISTS ai_conversations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_slug    VARCHAR(50) NOT NULL,
    stage           VARCHAR(20),          -- concept/examples/practice/test/summary
    messages        TEXT NOT NULL,        -- JSON: [{role, content}, ...]
    created_at      TEXT DEFAULT (datetime('now'))
);

-- 错题本（从 question_attempts 聚合，方便快速查询）
-- 已有 question_attempts 表，不需要新表，加个视图即可
CREATE VIEW IF NOT EXISTS error_book AS
SELECT 
    node_slug,
    question_id,
    user_answer,
    COUNT(*) as error_count,
    MAX(created_at) as last_error_at
FROM question_attempts
WHERE is_correct = 0
GROUP BY node_slug, question_id
ORDER BY error_count DESC;
```

### 修改表

`daily_sessions` 表需要适配新的章节流：

```sql
-- 在现有表上加字段（或改字段）
-- session_date 不变
-- target_node → 同一个（当前章节）
-- 新增字段：
--   current_stage: concept | examples | practice | test | summary
--   stage_progress: JSON（每个阶段的完成状态）
```

---

## 九、实施计划

### 第一阶段：重构内容 + 学习流（核心）

```
□ 1. 重写内容格式
   ├─ 将 10 个节点的 YAML 改为两层结构（display + ai_context）
   └─ 每个节点包含 concept + examples + practice + test

□ 2. 重写后端 session_builder
   ├─ 改为按章节 + 阶段加载内容
   ├─ GET /api/content/chapter?slug=xxx&stage=concept
   ├─ POST /api/content/submit-answer（替代旧的 session/answer）
   └─ SM-2 更新逻辑保留

□ 3. 重写前端 LearnPage
   ├─ 删除旧的 TrainWizard + 6 个 Step 组件
   ├─ 新建 LearnPage + 5 个阶段组件
   │   ConceptStage, ExampleStage, PracticeStage, TestStage, SummaryStage
   ├─ 阶段指示器
   └─ 题目交互组件（替换 interactives）

□ 4. Dashboard 微调
   └─ 点击"开始数学训练" → 跳转到当前未完成的章节
```

### 第二阶段：AI 侧边栏

```
□ 5. 新建 AI 编排层
   ├─ backend/services/ai_orchestrator.py
   ├─ build_context() 上下文组装
   ├─ POST /api/ai/ask（SSE 流式）
   └─ POST /api/ai/generate-practice

□ 6. 新建 AISidebar 前端组件
   ├─ 侧边栏弹出/收起动画
   ├─ 消息列表 + 流式渲染
   ├─ 快捷操作按钮
   └─ 上下文自动注入（传给 API）

□ 7. 集成测试
   └─ 在学习流中打开 AI → 提问 → 收到上下文相关回复
```

### 第三阶段：管理面板 + 打磨

```
□ 8. 管理面板
   ├─ SM-2 调试器
   ├─ 参数实时调节
   └─ 内容重载

□ 9. 一键启动脚本 run.py
□ 10. 完整端到端测试
```

---

## 十、与现有代码的迁移路径

```
现有代码                                → 新代码

backend/engine/session_builder.py       → 重构为 chapter_engine.py
backend/engine/interleaver.py           → 删除（不需要交错调度了）
backend/services/feynman_check.py       → 删除（LLM 替代）
backend/routers/session.py              → 拆分为 content.py + ai.py

frontend/pages/TrainPage.tsx            → 重写为 LearnPage.tsx
frontend/components/train/TrainWizard   → 删除
frontend/components/train/*Step.tsx     → 删除
frontend/components/train/CheckupStep   → 删除
frontend/components/interactives/*      → 删除（DragSort, MatchPairs 等）
frontend/stores/trainStore.ts           → 重写为 learnStore.ts

保留不动：
backend/database.py, models.py, config.py
backend/engine/sm2.py, mastery.py, path_planner.py
backend/content/loader.py（修改适配新格式）
backend/routers/progress.py, admin.py
frontend/pages/Dashboard.tsx
frontend/components/shared/KnowledgeTree.tsx
config.yaml（小幅修改）
```

---

## 十一、验证方式

### 自动化测试

```bash
# SM-2 算法（不变，保留现有测试）
python -m pytest backend/tests/test_sm2.py -v

# 掌握树（不变）
python -m pytest backend/tests/test_mastery.py -v

# 内容加载器（适配新格式后）
python -m pytest backend/tests/test_content.py -v

# API 测试（新端点）
python -m pytest backend/tests/test_api.py -v
```

### 手动验证清单

| # | 验证项 | 方法 | 预期 |
|---|--------|------|------|
| 1 | Dashboard 显示章节进度 | 打开 / | 数学/英语各显示掌握节点数 |
| 2 | 进入学习 | 点击"开始数学训练" | 跳转到第一个未完成的章节 |
| 3 | 概念阶段 | 页面显示 | 看到定义、公式、有"下一页"按钮 |
| 4 | 例题阶段 | 翻到例题 | 逐步展示，可展开每步 |
| 5 | 练习阶段 | 做题 | 输入答案→提交→即时判断+解释 |
| 6 | 错题反馈 | 故意答错 | 显示正确解法，出现 💬 按钮 |
| 7 | 测试阶段 | 完成全部测试题 | SM-2 记录，显示掌握度 |
| 8 | AI 侧边栏 | 点 💬 打开 | 侧边栏滑入，显示当前章节上下文 |
| 9 | AI 提问 | 输入问题 | 流式回复，内容与当前章节相关 |
| 10 | 换个方式讲 | 点快捷按钮 | AI 换角度解释同一概念 |
| 11 | 总结阶段 | 完成测试后 | 显示本章掌握度、错题、关键点 |
| 12 | 进入下一章 | 点"下一章" | 前置 mastered → 跳转 |

---

## 总结

| | 旧方案 | 新方案 |
|---|---|---|
| 学习流 | 6 步训练向导 | 5 阶段章节流（概念→例题→练习→测试→总结） |
| 内容 | 预写死 Markdown | 两层 YAML（精简展示 + AI 教案） |
| 题目 | 固定题库 | 固定题库 + AI 按需生成 |
| 提问 | 不支持 | 侧边栏 AI 导师，带上下文 |
| 换讲解 | 不支持 | 快捷按钮"换个方式讲" |
| SM-2 | 写了但没用上 | 测试阶段驱动 SM-2 调度 |
| AI | 无 | DeepSeek/OpenAI 编排层 |

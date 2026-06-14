# 修改记录

## 2026-06-14

### Bug 修复

#### 数学/英语训练分离失效
- **问题**: 点击"数学训练"进入英语内容
- **根因**: `DailySession.session_date` 设为 `unique=True`，每天只能有一个会话；复用逻辑中 `not existing_subject` 判断导致任何 subject 都复用旧会话
- **修复**: 
  - `backend/models.py` — `DailySession` 新增 `subject` 列，移除 `session_date` 唯一约束
  - `backend/engine/session_builder.py` — 查询已有会话时同时匹配 `session_date + subject`；创建会话时把 `subject` 写入列

#### 填空题/计算题无法输入
- **问题**: 混合训练中 `fill` 类型题目输入框不显示
- **根因**: `QuestionCard` 缺少 `key` prop，切换题目时 `submitted` 状态残留
- **修复**: `WarmupStep.tsx` / `TrainingStep.tsx` — QuestionCard 加 `key={question.id}`，修正 `onConfidence` 硬编码 `{ choice: 0 }` 的 bug

### 新功能

#### 英语语音全覆盖
- 4 个非音标英语节点（名词冠词、四大时态、现在完成时、宾语从句）全面添加语音
- 触发器 `spoken_phrases`：每节点 4-5 个关键例句发音
- 操作层 `spoken_examples`：每节点 4-5 个核心例句发音
- 总计新增 21 个触发器语音 + 18 个例句发音

#### 全局 48 音素参考面板
- `frontend/src/components/shared/PhonemePanel.tsx` — 侧边滑出面板
- 导航栏右侧「🔤 音标」按钮，任何页面可打开
- 5 组 48 个音素，每个都有 🗣️ 音素发音 + 📢 单词发音
- 音素独立发音 0.5x 慢速，单词发音 0.85x 正常速度

#### 音素发音质量优化
- 音素播放速度 0.9 → 0.5（放慢一倍）
- 音素音调 1.0 → 0.85（稍低沉更清晰）
- 48 个 `speak_phoneme` 全部重写，从单字母改为多音节重复形式
  - 元音: `"ee"` → `"ee-ee-ee"`
  - 辅音: `"p"` → `"puh-puh-puh"`
  - 摩擦音: `"f"` → `"fff-fff"`

#### 题目语音播放
- `QuestionCard` 新增 `spoken_words` 渲染（琥珀色标签 + 发音按钮）
- 音标题 8 道全部加语音参考

### 内容重构

#### 新增「初中核心词汇」节点
- `content/nodes/english/02-vocabulary-core.yaml`
- 30 个初中高频词，6 组（学校、家庭、生活、动作、自然、描述）
- 每词含：英语、IPA 音标、中文释义、发音
- 三层讲解 + 费曼输出
- `LearnStep` 新增 `word_groups` 分类词汇表渲染

#### 新增词汇题目
- `content/questions/english/02-vocabulary-core.yaml`
- 9 道渐进式题目：听音选词→看词选音标→听音选音标→中译英→看音标写词→音标辨异→造句
- 全部带 `spoken_words` 语音

#### 音标题完全重写
- `content/questions/english/01-phonetics.yaml` 全部重写
- 从单词依赖题改为纯音素识别题
- 题型：听音选音标、听音辨清浊、听音比长短、音标分类、发音部位辨别
- 不再要求认识任何英语单词

#### 学习路径调整
- `nouns-articles` 前置依赖: `phonetics` → `vocabulary-core`
- 新路径: 音标 → 核心词汇 → 名词冠词 → 四大时态 → 现在完成时 / 宾语从句

### 文件清单

**修改**:
- `backend/models.py`
- `backend/engine/session_builder.py`
- `frontend/src/components/shared/SpeakButton.tsx`
- `frontend/src/components/shared/QuestionCard.tsx`
- `frontend/src/components/train/LearnStep.tsx`
- `frontend/src/components/train/TriggerStep.tsx`
- `frontend/src/components/train/TrainingStep.tsx`
- `frontend/src/components/train/WarmupStep.tsx`
- `frontend/src/components/Layout.tsx`
- `content/nodes/english/01-phonetics.yaml`
- `content/nodes/english/02-nouns-articles.yaml`
- `content/nodes/english/04-tenses-basic.yaml`
- `content/nodes/english/11-present-perfect.yaml`
- `content/nodes/english/16-object-clause.yaml`
- `content/questions/english/01-phonetics.yaml`

**新增**:
- `frontend/src/components/shared/PhonemePanel.tsx`
- `content/nodes/english/02-vocabulary-core.yaml`
- `content/questions/english/02-vocabulary-core.yaml`
- `CHANGELOG.md`

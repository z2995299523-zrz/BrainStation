#!/usr/bin/env python3
"""Generate all English knowledge nodes for junior high school (16 modules)."""

import yaml
import os
from pathlib import Path

OUT_DIR = Path(r"D:\lernning-pro\math-english-camp\content\nodes\english")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def make_node(slug, title, tier, difficulty, prerequisites, trigger_story_title, trigger_text, trigger_question,
              summary, sections, examples, practice_items, test_items,
              topic_summary, key_insights, common_mistakes, alternate_explanations, question_templates):
    """Build a complete node dict following the new format."""
    return {
        'slug': slug,
        'subject': 'english',
        'title': title,
        'tier': tier,
        'difficulty': difficulty,
        'prerequisites': prerequisites,
        'estimated_min': 25,
        'trigger': {
            'type': 'story',
            'title': trigger_story_title,
            'content': {
                'text': trigger_text,
                'question': trigger_question,
            }
        },
        'display': {
            'concept': {
                'summary': summary,
                'sections': sections,
            },
            'examples': examples,
            'practice': practice_items,
            'test': test_items,
        },
        'ai_context': {
            'topic_summary': topic_summary,
            'key_insights': key_insights,
            'common_mistakes': common_mistakes,
            'alternate_explanations': alternate_explanations,
            'question_templates': question_templates,
        }
    }

class Lit(str):
    """Marker for YAML literal block scalar."""
    pass

def lit_repr(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(Lit, lit_repr)

def L(text):
    return Lit(text)

def write_node(filename, node):
    filepath = OUT_DIR / filename
    # Use yaml.dump with allow_unicode
    yaml_str = yaml.dump(node, allow_unicode=True, default_flow_style=False, sort_keys=False, width=200)
    # Validate by loading back
    try:
        loaded = yaml.safe_load(yaml_str)
    except Exception as e:
        print(f"ERROR validating {filename}: {e}")
        raise
    filepath.write_text(yaml_str, encoding='utf-8')
    print(f"  ✓ {filename} written and validated ({len(yaml_str)} bytes)")


# ═══════════════════════════════════════════════════════════════
# NODE 03: pronouns (代词与数词)
# ═══════════════════════════════════════════════════════════════
def create_03_pronouns():
    slug = "pronouns"
    title = "代词与数词"
    tier = "core"
    difficulty = 2
    prereqs = ["nouns-articles"]

    trigger_title = "英语为什么需要这么多代词？"
    trigger_text = L("""\
你有没有想过——如果没有"我""你""他""她""它"，每一句话都要重复名字？

"小明说小明今天要去小明的朋友家，小明的朋友住在小明的朋友家附近。"

听起来像绕口令对吧？代词就是来解决这个问题的——它让语言简洁、流畅。

英语的代词系统比中文更复杂：人称代词有主格、宾格、形容词性物主代词、名词性物主代词、反身代词五种形式。

而数词呢？从 one 到 million，从 first 到 hundredth——它们是英语中的"数字语言"。

掌握代词和数词，你的英语表达会从"结巴"变成"流利"。""")
    trigger_question = "你能用英语说出'这是我的书，那是他的'吗？试着翻译一下。"

    sections = [
        {
            'title': '一、人称代词（Personal Pronouns）',
            'content': L("""\
**人称代词**代替人或事物的名称，分为主格和宾格：

| 人称 | 主格 | 宾格 | 中文 |
|------|------|------|------|
| 第一人称单数 | I | me | 我 |
| 第二人称单数 | you | you | 你 |
| 第三人称单数 | he | him | 他 |
| 第三人称单数 | she | her | 她 |
| 第三人称单数 | it | it | 它 |
| 第一人称复数 | we | us | 我们 |
| 第二人称复数 | you | you | 你们 |
| 第三人称复数 | they | them | 他们/她们/它们 |

**规则**：主格做主语，宾格做宾语。

- ✓ I like her.（主格 I 做主语，宾格 her 做宾语）
- ✗ Me like she.（错误——主格和宾格搞反了）"""),
        },
        {
            'title': '二、物主代词（Possessive Pronouns）',
            'content': L("""\
**物主代词**表示所有关系，分为形容词性和名词性：

| 人称 | 形容词性 | 名词性 | 中文 |
|------|---------|--------|------|
| 我的 | my | mine | 我的 |
| 你的 | your | yours | 你的 |
| 他的 | his | his | 他的 |
| 她的 | her | hers | 她的 |
| 它的 | its | its | 它的 |
| 我们的 | our | ours | 我们的 |
| 你们的 | your | yours | 你们的 |
| 他们的 | their | theirs | 他们的 |

**关键区别**：
- 形容词性物主代词 = 形容词，后面必须接名词：my book, your pen
- 名词性物主代词 = 名词，单独使用：This book is mine. (= my book)

**口诀**：形物后面加名词，名物独立当名词。"""),
        },
        {
            'title': '三、反身代词（Reflexive Pronouns）',
            'content': L("""\
**反身代词**表示"自己"，以 -self（单数）或 -selves（复数）结尾：

| 人称 | 反身代词 | 中文 |
|------|---------|------|
| 我自己 | myself | 我自己 |
| 你自己 | yourself | 你自己 |
| 他自己 | himself | 他自己 |
| 她自己 | herself | 她自己 |
| 它自己 | itself | 它自己 |
| 我们自己 | ourselves | 我们自己 |
| 你们自己 | yourselves | 你们自己 |
| 他们自己 | themselves | 他们自己 |

**常见用法**：
- 反身：He hurt himself.（他伤到了自己。）
- 强调：I did it myself.（我自己做的！）

**注意**：反身代词不能单独做主语——✗ Myself went there. → ✓ I went there myself."""),
        },
        {
            'title': '四、指示代词与疑问代词',
            'content': L("""\
**指示代词**（this/that/these/those）：

| 单数 | 复数 | 距离 |
|------|------|------|
| this（这个） | these（这些） | 近 |
| that（那个） | those（那些） | 远 |

**疑问代词**（wh-词做代词）：who（谁）、whom（谁/宾格）、whose（谁的）、what（什么）、which（哪一个）

- Who is that girl?（那个女孩是谁？）
- Whose book is this?（这是谁的书？）"""),
        },
        {
            'title': '五、数词（Numerals）',
            'content': L("""\
**基数词**（表示数量）：one, two, three, ... hundred, thousand, million

**序数词**（表示顺序）：first, second, third, fourth, ... hundredth

**规则**：
- 1-3 特殊：one→first, two→second, three→third
- 4-19：基数词 + th（注意：five→fifth, eight→eighth, nine→ninth, twelve→twelfth）
- 20-90（整十）：去 y 加 ieth：twenty→twentieth
- 几十几：十位基数 + 个位序数：twenty-first, thirty-second

**易错点**：
- 几百：two hundred（不加 s）→ ✗ two hundreds
- 几百几十几：英语用 and 连接：one hundred and twenty-three
- 序数词前通常加 the：the first lesson"""),
        },
    ]

    examples = [
        {
            'title': '主格 vs 宾格',
            'problem': '"Her likes I" 哪里错了？',
            'steps': [
                '第 1 步：找主语——谁在"喜欢"？应该是"她"→ 主格 she',
                '第 2 步：找宾语——谁被喜欢？应该是"我"→ 宾格 me',
                '第 3 步：正确句子：She likes me.',
            ],
            'answer': 'She likes me.（主格 she 做主语，宾格 me 做宾语）',
        },
        {
            'title': '形容词性 vs 名词性物主代词',
            'problem': '"This is my book. That is your." 哪里有问题？',
            'steps': [
                '第 1 步：my book 正确——my（形容词性）+ book（名词）',
                '第 2 步：your 后面没有名词，应该用名词性物主代词 yours',
                '第 3 步：正确句子：This is my book. That is yours.',
            ],
            'answer': 'yours（名词性物主代词独立使用，= your book）',
        },
        {
            'title': '数词 hundred 不加 s',
            'problem': '"There are three hundreds students." 哪里错？',
            'steps': [
                '第 1 步：hundred 前有具体数字 three 时，hundred 不加 s',
                '第 2 步：hundreds of（成百上千的）才加 s——表示不具体的数量',
                '第 3 步：正确句子：There are three hundred students.',
            ],
            'answer': 'three hundred（具体数字 + hundred 不加 s）',
        },
    ]

    practice = [
        {'id': 'pro-prac-001', 'stem': '用正确的人称代词填空：___ (她) is my sister. I like ___ (她) very much.', 'answer': 'She, her', 'hints': ['第一个空是主语位置→主格', '第二个空在动词 like 后面→宾格']},
        {'id': 'pro-prac-002', 'stem': 'This is not ___ (我的) book. ___ (我的) is on the desk.', 'answer': 'my, Mine', 'hints': ['第一个空后面有名词 book→形容词性', '第二个空后面没有名词→名词性']},
        {'id': 'pro-prac-003', 'stem': 'They enjoyed ___ (他们自己) at the party.', 'answer': 'themselves', 'hints': ['they 对应的反身代词', '以 -selves 结尾']},
        {'id': 'pro-prac-004', 'stem': '写出 twenty-two 的序数词形式。', 'answer': 'twenty-second', 'hints': ['几十几：十位基数 + 个位序数', 'two 的序数词是 second']},
        {'id': 'pro-prac-005', 'stem': '"I have two hundreds yuan." 这句哪里错了？', 'answer': 'hundred 前面有具体数字时不加 s，应该是 two hundred', 'hints': ['具体数字 + hundred 不加 s', 'hundreds of 才加 s']},
    ]

    test = [
        {'id': 'pro-test-001', 'stem': '填空：Please give ___ (我) a pen.', 'answer': 'me', 'difficulty': 1, 'layer': 'operation'},
        {'id': 'pro-test-002', 'stem': 'This pen is not ___. It is ___. A. my, her  B. mine, hers  C. my, hers', 'answer': 'B. mine, hers', 'difficulty': 2, 'layer': 'operation'},
        {'id': 'pro-test-003', 'stem': '"Himself went to the store." 哪里错？', 'answer': '反身代词不能单独做主语。正确：He went to the store himself.', 'difficulty': 2, 'layer': 'understand'},
        {'id': 'pro-test-004', 'stem': '写出 123 的英语表达（基数词）。', 'answer': 'one hundred and twenty-three', 'difficulty': 2, 'layer': 'operation'},
        {'id': 'pro-test-005', 'stem': '把句子改成正确的英语：\"她是我最好的朋友，我每天和她一起上学。\"', 'answer': 'She is my best friend. I go to school with her every day.', 'difficulty': 3, 'layer': 'connect'},
        {'id': 'pro-test-006', 'stem': '小明说："This is my book and that is your." 他说得对吗？为什么？', 'answer': '不对。your 后面没有名词，要用名词性物主代词 yours。正确：This is my book and that is yours.', 'difficulty': 3, 'layer': 'understand'},
        {'id': 'pro-test-007', 'stem': '用英语写出你的年龄、班级里的第几名、以及你家里有几口人（用数词）。', 'answer': '（示例）I am thirteen years old. I am the third in my class. There are four people in my family.', 'difficulty': 3, 'layer': 'connect'},
        {'id': 'pro-test-008', 'stem': '为什么英语的代词系统比中文复杂？举三个例子说明。', 'answer': '英语代词区分主格和宾格（I/me、he/him），区分形容词性和名词性物主代词（my/mine），还有反身代词（myself）。中文只用同一个字或加"的"来表示。', 'difficulty': 4, 'layer': 'connect'},
    ]

    topic_summary = "代词与数词是英语词法的基础模块。代词系统包括人称代词（主格/宾格）、物主代词（形容词性/名词性）、反身代词、指示代词和疑问代词——共五种类型。数词包括基数词和序数词，重点掌握 hundred/thousand/million 加不加 s 的规则以及几十几的序数词构成。代词和数词的正确使用是英语表达流畅度的关键标志。"
    key_insights = [
        '人称代词区分主格和宾格——这是中文没有的概念，需要刻意练习',
        '物主代词分"形容词性"（后接名词）和"名词性"（独立使用），记住口诀"形物加名，名物独立"',
        'hundred/thousand/million 前面有具体数字时不加 s——这是中国学生最常见的数词错误之一',
        '反身代词不能单独做主语——它用来"反射"主语或强调主语',
    ]
    common_mistakes = [
        {'mistake': '主格和宾格混淆', 'example': '"Her likes he."', 'why': '中文"她喜欢他"不需要变形，学生不知道要用主格 she 和宾格 him', 'how_to_explain': '给每个代词标"角色"：主语位→主格，动词/介词后→宾格。把表格画出来贴在书桌上，每天看一遍。'},
        {'mistake': 'my 和 mine 混淆', 'example': '"This is mine book."', 'why': '不知道 my 是形容词（后接名词）、mine 是名词（独立用）', 'how_to_explain': '测试方法：如果代词后面还有名词，用 my/your/her 等；如果句子到此为止，用 mine/yours/hers。This is my ___(名词) vs This is mine.(句号)'},
        {'mistake': 'hundred 加 s', 'example': '"three hundreds"', 'why': '中文说"三百"没有任何变化，学生下意识在所有数字后加 s', 'how_to_explain': '具体数字=不加 s（three hundred），模糊数量=加 s+of（hundreds of）。就像中文"三百"不加"们"，但"成百上千"加。'},
        {'mistake': 'your 和 yours 在句末用错', 'example': '"That pen is your."', 'why': '不知道 be 动词后需要用名词性物主代词', 'how_to_explain': 'be 动词后的物主代词永远用名词性：It is mine/yours/his/hers/ours/theirs。因为 be 动词后跟名词或形容词作表语，名词性物主代词就是"名词"。'},
    ]
    alternate_explanations = [
        {'method': '角色扮演法', 'when_to_use': '学生记不住主格/宾格表格时', 'prompt': '每次用人称代词时问自己两个问题：这个代词在句子里是"做动作的人"（主语=主格）还是"被动作影响的人"（宾语=宾格）？比如"I saw her."——"看"的人是 I（主格），被看的人是 her（宾格）。'},
        {'method': '替换测试法（物主代词）', 'when_to_use': '学生不确定用 my 还是 mine 时', 'prompt': '把代词替换成"我的书"或"我的"。如果能说"我的书"→用 my；如果只能说"我的"→用 mine。This is my book = 这是我的书。This book is mine = 这本书是我的。'},
        {'method': '数词公式记忆法', 'when_to_use': '学生记不住序数词变化规则时', 'prompt': '给出三条铁律：1) 1,2,3 特殊记（first, second, third）；2) 5,8,9,12 变拼写（fifth, eighth, ninth, twelfth）；3) 整十去 y 加 ieth（twentieth）。其他的都是基数+th。记住这三条就够了。'},
    ]
    question_templates = {
        'difficulty_1_2': '出 2 道填空题：给中文意思让学生填写正确的主格/宾格代词，或基数词转序数词（如 five→?）',
        'difficulty_3': '出 1 道改错题：给一个包含物主代词错误或数词错误的句子，让学生找出并改正（如"This is mine pen"）',
        'difficulty_4': '出 1 道翻译/解释题：给一段中文让学生翻译成英语，要求用到人称代词、物主代词和数词',
    }

    summary = "代词与数词是英语表达的基础工具。代词包括人称代词（主格/宾格）、物主代词（形容词性/名词性）、反身代词、指示代词和疑问代词五种类型。数词包括基数词和序数词，重点掌握 hundred/thousand 不加 s 的规则以及几十几的序数词构成。"

    node = make_node(slug, title, tier, difficulty, prereqs, trigger_title, trigger_text, trigger_question,
                     summary, sections, examples, practice, test,
                     topic_summary, key_insights, common_mistakes, alternate_explanations, question_templates)
    write_node('03-pronouns.yaml', node)


# ═══════════════════════════════════════════════════════════════
# NODE 05: adjectives-adverbs (形容词与副词)
# ═══════════════════════════════════════════════════════════════
def create_05_adjectives_adverbs():
    slug = "adjectives-adverbs"
    title = "形容词与副词"
    tier = "core"
    difficulty = 2
    prereqs = ["nouns-articles"]

    trigger_title = "英语的形容词和副词——一句话的'装饰品'"
    trigger_text = L("""\
如果英语句子是一个房间，名词和动词是家具，那形容词和副词就是墙纸、灯光和窗帘。

没有它们，一切看起来光秃秃的：
- "I have a car." → 什么车？
- "I have a beautiful red car." → 画面感立刻有了！

形容词修饰名词，副词修饰动词、形容词或其他副词。

但英语的形容词有比较级和最高级——这就像给装饰品分了档次：
好 → 更好 → 最好 (good → better → best)
美丽 → 更美丽 → 最美丽 (beautiful → more beautiful → most beautiful)

一旦掌握比较级规则，你就能精确表达任何程度和对比。""")
    trigger_question = "你能说出'他比我高'和'他是我们班最高的'的英语吗？"

    sections = [
        {
            'title': '一、形容词（Adjectives）',
            'content': L("""\
**形容词**用来修饰名词，说明事物的性质、状态、特征。

**位置**：
- 放在名词前（定语）：a **beautiful** flower, an **interesting** book
- 放在 be 动词后（表语）：The flower is **beautiful**. He looks **happy**.

**多个形容词的顺序口诀**：
"美小圆旧黄，法国木书房" → 观点(beautiful) + 大小(big) + 形状(round) + 年龄(old) + 颜色(yellow) + 国籍(French) + 材料(wooden) + 用途

例：a beautiful big old Chinese wooden house"""),
        },
        {
            'title': '二、副词（Adverbs）',
            'content': L("""\
**副词**修饰动词、形容词或其他副词，说明方式、程度、时间、地点等。

**常见副词类型**：
| 类型 | 例词 | 例句 |
|------|------|------|
| 方式副词 | quickly, slowly, carefully | She runs **quickly**. |
| 程度副词 | very, quite, too, almost | It is **very** cold. |
| 时间副词 | now, then, yesterday, soon | I will call you **tomorrow**. |
| 地点副词 | here, there, everywhere | Come **here**. |
| 频率副词 | always, often, sometimes, never | I **always** get up early. |

**形容词变副词的规则**：
- 一般情况：形容词 + ly → quick→quickly, careful→carefully
- 辅音 + y 结尾：去 y + ily → easy→easily, happy→happily
- le 结尾：去 e + y → simple→simply, gentle→gently

**注意**：有些词本身就是副词（fast, hard, early），不需要加 ly。"""),
        },
        {
            'title': '三、比较级和最高级（Comparative & Superlative）',
            'content': L("""\
**规则变化**：

| 类型 | 比较级 | 最高级 | 例词 |
|------|--------|--------|------|
| 单音节 | -er | -est | tall → taller → tallest |
| 单音节（辅元辅） | 双写尾字母 + er/est | | big → bigger → biggest |
| 辅音+y | 去 y + ier/iest | | happy → happier → happiest |
| 不发音 e 结尾 | + r/st | | large → larger → largest |
| 多音节 | more/most + 原级 | | beautiful → more/most beautiful |

**不规则变化**（必须硬背）：
| 原级 | 比较级 | 最高级 |
|------|--------|--------|
| good/well | better | best |
| bad/badly/ill | worse | worst |
| many/much | more | most |
| little | less | least |
| far | farther/further | farthest/furthest |
| old | older/elder | oldest/eldest |

**句式**：
- 比较级 + than：He is taller **than** me.
- as + 原级 + as：She is as tall **as** her sister.
- the + 最高级 + 范围：He is **the** tallest in our class."""),
        },
        {
            'title': '四、常见易错点',
            'content': L("""\
**1. 比较对象要一致**：
- ✗ His bag is bigger than me.（bag 和 me 比较——逻辑错误）
- ✓ His bag is bigger than **mine**.（bag 和 bag 比较）

**2. 双音节词的处理**：
- 以 -y, -er, -ow, -le 结尾的双音节词 → 加 er/est
  - narrow → narrower → narrowest
  - clever → cleverer → cleverest
- 其他双音节词 → more/most
  - famous → more famous → most famous

**3. the + 比较级, the + 比较级**（越...就越...）：
- **The more** you practice, **the better** you become.

**4. 比较级的修饰语**：
- much/a lot/far + 比较级（...得多）：much bigger（大得多）
- a little/a bit + 比较级（...一点）：a little taller（高一点）"""),
        },
    ]

    examples = [
        {
            'title': '比较级规则变化',
            'problem': 'big 的比较级为什么是 bigger 而不是 biger？',
            'steps': [
                '第 1 步：big 是单音节，结尾是辅音-元音-辅音结构（b-i-g）',
                '第 2 步：辅元辅结构→双写末尾辅音字母 g，再加 er',
                '第 3 步：big → bigger → biggest',
            ],
            'answer': 'big 是辅元辅结构→双写 g + er → bigger',
        },
        {
            'title': '比较对象一致',
            'problem': '"The weather in Beijing is colder than Shanghai." 哪里有问题？',
            'steps': [
                '第 1 步：比较的是 weather（天气）——北京的天气 vs 上海的天气',
                '第 2 步：但句子写的是 weather vs Shanghai（城市）——比较对象不一致',
                '第 3 步：修正：The weather in Beijing is colder than that in Shanghai.',
            ],
            'answer': '要加 that（指代 weather），确保比较的是天气 vs 天气',
        },
        {
            'title': '副词位置',
            'problem': '"He runs fastly." 对吗？',
            'steps': [
                '第 1 步：fast 本身既是形容词也是副词，不需要加 ly',
                '第 2 步：fastly 不是标准英语单词',
                '第 3 步：正确：He runs fast.',
            ],
            'answer': 'fast 本身就是副词，不需要加 ly。He runs fast.',
        },
    ]

    practice = [
        {'id': 'adj-prac-001', 'stem': '写出下列形容词的比较级和最高级：① tall ② big ③ happy ④ beautiful', 'answer': '① taller, tallest ② bigger, biggest ③ happier, happiest ④ more beautiful, most beautiful', 'hints': ['tall 单音节直接加 er/est', 'big 辅元辅双写 g', 'happy 去 y 加 ier/iest', 'beautiful 多音节用 more/most']},
        {'id': 'adj-prac-002', 'stem': '填空：good → ___ → ___', 'answer': 'better, best', 'hints': ['good 是不规则变化', 'better 是比较级，best 是最高级']},
        {'id': 'adj-prac-003', 'stem': '改错：She is more taller than me.', 'answer': '去掉 more。taller 本身已经是比较级了，不能和 more 一起用。正确：She is taller than me.', 'hints': ['more 和 -er 不能同时用', '单音节词加 er，不用 more']},
        {'id': 'adj-prac-004', 'stem': '用 as...as 翻译："她和她姐姐一样聪明。"', 'answer': 'She is as clever as her sister.', 'hints': ['as...as 中间用原级', '聪明的：clever 或 smart']},
        {'id': 'adj-prac-005', 'stem': '"He is the tallest in his class." 翻译成中文并指出最高级的结构。', 'answer': '他是他们班最高的。结构：the + 最高级 + in/of + 范围。', 'hints': ['tallest 是最高级', 'the + 最高级 是固定搭配']},
    ]

    test = [
        {'id': 'adj-test-001', 'stem': '写出 beautiful 的比较级。A. beautifuler  B. more beautiful  C. beautifuller', 'answer': 'B. more beautiful', 'difficulty': 1, 'layer': 'operation'},
        {'id': 'adj-test-002', 'stem': 'bad 的比较级和最高级是？', 'answer': 'worse, worst', 'difficulty': 1, 'layer': 'operation'},
        {'id': 'adj-test-003', 'stem': '改错：She sings beautiful.', 'answer': 'beautiful 是形容词，不能修饰动词 sings。应该用副词 beautifully。', 'difficulty': 2, 'layer': 'understand'},
        {'id': 'adj-test-004', 'stem': '用 the+比较级, the+比较级 翻译："你越努力，你就越幸运。"', 'answer': 'The harder you work, the luckier you get.', 'difficulty': 3, 'layer': 'connect'},
        {'id': 'adj-test-005', 'stem': '"This apple is bigger than that one." 这里的 that one 指的是什么？为什么要加？', 'answer': 'that one 指代"那个苹果"。不加的话比较对象不一致（apple vs that）。', 'difficulty': 3, 'layer': 'understand'},
        {'id': 'adj-test-006', 'stem': '列出 4 个不规则比较级变化的形容词，并写出它们的比较级和最高级。', 'answer': 'good→better→best; bad→worse→worst; many/much→more→most; little→less→least', 'difficulty': 2, 'layer': 'operation'},
        {'id': 'adj-test-007', 'stem': '翻译："这是我读过的最有趣的书。"', 'answer': 'This is the most interesting book (that) I have ever read.', 'difficulty': 3, 'layer': 'connect'},
        {'id': 'adj-test-008', 'stem': '小明说："My bag is more bigger than yours." 他说错了什么？为什么？', 'answer': 'bigger 本身已经表示比较级，more 是多余的。单音节词直接加 er，不用 more。正确：My bag is bigger than yours.', 'difficulty': 3, 'layer': 'understand'},
    ]

    topic_summary = "形容词与副词是英语修饰语的两大支柱。形容词修饰名词（a big house），副词修饰动词/形容词/其他副词（run quickly）。本章的核心是形容词比较级和最高级的构成规则（单音节加 er/est，多音节用 more/most，不规则变化需要硬背）以及比较句式（than、as...as、the+比较级）。掌握这些，学生就能进行精确的程度表达和对比描述。"
    key_insights = [
        '形容词修饰名词，副词修饰动词/形容词/副词——这是区分的根本标准',
        '比较级变化规则取决于音节数：单音节加 er/est，多音节用 more/most，双音节看结尾',
        '六个不规则变化（good, bad, many, little, far, old）必须硬背——它们是高频词',
        '比较对象必须一致——这是中国学生最常犯的逻辑错误之一',
    ]
    common_mistakes = [
        {'mistake': 'more 和 -er 同时使用', 'example': '"more bigger"、"more taller"', 'why': '学生知道 more 表示"更"，又知道 bigger 表示"更大"，以为两者可以叠加', 'how_to_explain': 'more 和 -er 都是比较级的标记，就像一个人不能同时穿两双鞋。单音节词用 -er，多音节用 more——选一个就够了。'},
        {'mistake': '用形容词修饰动词', 'example': '"She sings beautiful."', 'why': '中文"她唱得很美"中"美"不需要变形，学生直接用形容词修饰动词', 'how_to_explain': '形容词只能修饰名词。修饰动词必须用副词（加 ly 或本身就是副词）。判断方法：看被修饰的词——如果是动词/形容词→用副词；如果是名词→用形容词。'},
        {'mistake': '比较对象不一致', 'example': '"My hair is longer than you."', 'why': '中文说"我的头发比你长"是自然的，但英语必须严格一致', 'how_to_explain': '英语的比较逻辑非常严格——你只能比较同类事物。hair vs you 是"头发"和"人"比较→逻辑错误。用 that/those 或名词性物主代词来保持一致。'},
        {'mistake': '混淆 good 和 well', 'example': '"He plays football good."', 'why': '只知道 good 是"好"，不知道修饰动词要用 well', 'how_to_explain': 'good 是形容词（a good player），well 是副词（play well）。唯一例外：谈论身体健康时 well 也可以做形容词——"I am well."'},
    ]
    alternate_explanations = [
        {'method': '音节数判断法', 'when_to_use': '学生不确定一个词加 er/est 还是 more/most 时', 'prompt': '拍手数音节：tall = 1 拍 → taller；happy = 2 拍（hap-py）且以 y 结尾 → happier；beautiful = 3 拍（beau-ti-ful）→ more beautiful。超过 2 拍且不以 y/er/ow/le 结尾 → 用 more/most。'},
        {'method': '感官动词 + 形容词（不是副词）', 'when_to_use': '学生纠结"feel bad"还是"feel badly"时', 'prompt': '感官动词（look, smell, taste, sound, feel）+ 形容词，不是副词！因为描述的是主语的状态。The flower smells good（花闻起来香=花本身香），不是 The flower smells well（花嗅觉很好=花在闻东西）。'},
        {'method': '生活场景对比法', 'when_to_use': '学生对最高级使用场景感到抽象时', 'prompt': '最高级就是"世界之最"。想象你在写吉尼斯世界纪录：The tallest man（最高的人），The fastest car（最快的车）。每个最高级背后都有一个排他性的"第一名"——这就是 the 存在的意义（特指那个唯一的）。'},
    ]
    question_templates = {
        'difficulty_1_2': '出 2 道选择题：给形容词选择正确的比较级/最高级形式，或判断副词使用是否正确',
        'difficulty_3': '出 1 道改错题：给包含比较对象不一致或形容词/副词混淆的句子让学生改正',
        'difficulty_4': '出 1 道翻译/解释题：给一段中文描述让学生用至少 2 个比较级和 1 个最高级翻译成英语',
    }

    summary = "形容词与副词是英语修饰语的两大支柱。形容词修饰名词（a big house），副词修饰动词/形容词/其他副词（run quickly）。本章重点掌握比较级和最高级规则：单音节加 er/est，多音节用 more/most，六个不规则变化需硬背。"

    node = make_node(slug, title, tier, difficulty, prereqs, trigger_title, trigger_text, trigger_question,
                     summary, sections, examples, practice, test,
                     topic_summary, key_insights, common_mistakes, alternate_explanations, question_templates)
    write_node('05-adjectives-adverbs.yaml', node)


# ═══════════════════════════════════════════════════════════════
# NODE 06: prepositions-conjunctions (介词与连词)
# ═══════════════════════════════════════════════════════════════
def create_06_prepositions_conjunctions():
    slug = "prepositions-conjunctions"
    title = "介词与连词"
    tier = "core"
    difficulty = 2
    prereqs = ["nouns-articles"]

    trigger_title = "小词大用——英语中最被低估的词类"
    trigger_text = L("""\
介词和连词是英语中的"脚手架"——它们不显眼，但缺了它们整个句子就会倒塌。

介词（in, on, at, to, for, with...）表示事物之间的关系：
- The book is **on** the desk.（位置关系）
- I go to school **at** 7:00.（时间关系）

连词（and, but, or, because, although...）连接词、短语和句子：
- I like apples **and** oranges.（连接词）
- She is tired **but** she keeps working.（连接句子）

中文里也有类似的词，但英语的介词远比中文灵活——同一个 at 可以表示时间(at 7:00)、地点(at school)、状态(at work)。

这就是为什么介词被称作"英语学习者的终极挑战"。""")
    trigger_question = "你能说出 in、on、at 在表示时间时的区别吗？"

    sections = [
        {
            'title': '一、时间介词（Prepositions of Time）',
            'content': L("""\
**at**（点时间）：at 7:00, at noon, at night, at the moment
**on**（具体某天）：on Monday, on June 1st, on my birthday
**in**（大于天的时间段）：in the morning, in June, in 2025, in summer

**口诀**：at 点、on 天、in 月季年

**其他常见时间介词**：
| 介词 | 用法 | 例句 |
|------|------|------|
| since | 自从（起点） | since 2020, since I was a child |
| for | 持续（时长） | for two hours, for a long time |
| during | 在...期间 | during the summer, during class |
| before | 在...之前 | before 8:00, before lunch |
| after | 在...之后 | after school, after dinner |
| until/till | 直到 | until tomorrow, till midnight |"""),
        },
        {
            'title': '二、地点介词（Prepositions of Place）',
            'content': L("""\
**at**（点/小地点）：at the bus stop, at the door, at home
**on**（表面/线上）：on the table, on the wall, on the street
**in**（内部/大区域）：in the room, in Beijing, in China

**其他常见地点介词**：
| 介词 | 用法 | 例句 |
|------|------|------|
| above/over | 在...上方 | above the clouds, over the bridge |
| below/under | 在...下方 | below the surface, under the bed |
| beside/next to | 在...旁边 | beside the door, next to me |
| between | 在两者之间 | between you and me |
| among | 在三者以上之间 | among the students |
| behind | 在...后面 | behind the house |
| in front of | 在...前面 | in front of the school |
| across | 穿过（表面） | across the street |
| through | 穿过（内部） | through the forest |"""),
        },
        {
            'title': '三、其他重要介词',
            'content': L("""\
**方式介词**：
- by + 交通工具：by bus, by bike, by plane
- with + 工具：write with a pen, cut with a knife
- in + 语言/声音：in English, in a loud voice

**所属/关于**：
- of：the color of the sky, a friend of mine
- about：a book about animals, talk about the weather
- for：a gift for you, wait for me

**固定搭配**（必须硬背）：
- look **at**（看）、listen **to**（听）、wait **for**（等待）
- be good **at**（擅长）、be interested **in**（对...感兴趣）
- be afraid **of**（害怕）、be proud **of**（自豪）
- agree **with** sb / agree **to** sth（同意）"""),
        },
        {
            'title': '四、连词（Conjunctions）',
            'content': L("""\
**并列连词**（连接对等成分）：

| 连词 | 功能 | 例句 |
|------|------|------|
| and | 并列（和） | I like math **and** English. |
| but | 转折（但是） | It's hard **but** I'll try. |
| or | 选择（或者） | Tea **or** coffee? |
| so | 因果（所以） | It was late, **so** I went home. |
| for | 原因（因为） | I stayed home, **for** it rained. |

**从属连词**（引导状语从句，连接主句和从句）：

| 连词 | 功能 | 例句 |
|------|------|------|
| because | 原因 | I stayed home **because** it rained. |
| although/though | 让步 | **Although** it rained, I went out. |
| if | 条件 | **If** it rains, I will stay home. |
| when/while | 时间 | Call me **when** you arrive. |
| so...that | 结果 | He ran **so** fast **that** I couldn't catch him. |
| unless | 除非 | You can't enter **unless** you have a ticket. |

**注意**：because 和 so 不能连用！中文说"因为...所以..."，英语只能说 because... 或 ...so...
- ✗ Because it rained, so I stayed home.
- ✓ Because it rained, I stayed home. / It rained, so I stayed home.""")
        },
    ]

    examples = [
        {
            'title': 'at/on/in 时间区别',
            'problem': '"I get up in 7:00 every day." 哪里有问题？',
            'steps': [
                '第 1 步：7:00 是一个"点时间"（具体几点几分）',
                '第 2 步：点时间用 at，不用 in',
                '第 3 步：正确：I get up at 7:00 every day.',
            ],
            'answer': 'at 用于点时间，7:00 是点→用 at，不是 in',
        },
        {
            'title': 'because 和 so 不能连用',
            'problem': '"Because I was tired, so I went to bed early." 哪里错了？',
            'steps': [
                '第 1 步：because 和 so 都是表示因果的连词',
                '第 2 步：英语中一个句子只能用一个因果连词——because 和 so 不能同时出现',
                '第 3 步：两种改法——①去掉 so：Because I was tired, I went to bed early.  ②去掉 because：I was tired, so I went to bed early.',
            ],
            'answer': 'because 和 so 不能连用，选一个即可。',
        },
        {
            'title': 'between vs among',
            'problem': '"The secret is among you and me." 用对了吗？',
            'steps': [
                '第 1 步：between 用于两者之间，among 用于三者以上',
                '第 2 步：you and me 只有两个人→用 between',
                '第 3 步：正确：The secret is between you and me.',
            ],
            'answer': 'between 用于两者之间，among 用于三者以上。两人→between。',
        },
    ]

    practice = [
        {'id': 'prep-prac-001', 'stem': '用 at/on/in 填空：① ___ Monday  ② ___ 8:00  ③ ___ summer  ④ ___ June 1st', 'answer': '① on  ② at  ③ in  ④ on', 'hints': ['Monday 是具体某天→on', '8:00 是点时间→at', 'summer 是时间段→in', 'June 1st 是具体某天→on']},
        {'id': 'prep-prac-002', 'stem': '改错：Because he is kind, so everyone likes him.', 'answer': '去掉 so。Because he is kind, everyone likes him.', 'hints': ['because 和 so 不能同时用', '保留一个即可']},
        {'id': 'prep-prac-003', 'stem': '用 between 或 among 填空：She sat ___ her two friends.', 'answer': 'between', 'hints': ['two friends 是两个人', '两人→between']},
        {'id': 'prep-prac-004', 'stem': '翻译："我对英语感兴趣。"（用 be interested ___）', 'answer': 'I am interested in English.', 'hints': ['be interested 后面接什么介词？', '固定搭配：be interested in']},
        {'id': 'prep-prac-005', 'stem': '"She goes to school by a bus." 哪里错了？', 'answer': 'by bus 中间不加冠词。正确：She goes to school by bus.', 'hints': ['by + 交通工具 不加 a/an', 'by bus, by bike, by car']},
    ]

    test = [
        {'id': 'prep-test-001', 'stem': '填空：I usually go to bed ___ 10:00.', 'answer': 'at', 'difficulty': 1, 'layer': 'operation'},
        {'id': 'prep-test-002', 'stem': '选择：The cat is sleeping ___ the table. A. at  B. on  C. in', 'answer': 'B. on（在桌子表面上）', 'difficulty': 1, 'layer': 'operation'},
        {'id': 'prep-test-003', 'stem': '改错：Although it rained, but we still went out.', 'answer': 'although 和 but 不能连用。去掉 but。Although it rained, we still went out.', 'difficulty': 2, 'layer': 'understand'},
        {'id': 'prep-test-004', 'stem': '"I have been here since two hours." 哪里错了？', 'answer': 'since 后面接时间点（如 since 2020），时间段用 for。正确：I have been here for two hours.', 'difficulty': 3, 'layer': 'understand'},
        {'id': 'prep-test-005', 'stem': '翻译："除非你努力，否则你不会成功。"（用 unless）', 'answer': 'You will not succeed unless you work hard.', 'difficulty': 3, 'layer': 'connect'},
        {'id': 'prep-test-006', 'stem': '用 across 和 through 说明它们的区别各造一句。', 'answer': 'I walked across the road.（走过路面，表面）The river flows through the city.（穿过城市，内部）', 'difficulty': 3, 'layer': 'understand'},
        {'id': 'prep-test-007', 'stem': '列出 5 个常见的"动词+介词"固定搭配并造句。', 'answer': 'look at（看）、listen to（听）、wait for（等）、depend on（依赖）、think about（考虑）', 'difficulty': 2, 'layer': 'operation'},
        {'id': 'prep-test-008', 'stem': '小明说："I go to school by my father\u2019s car." 他说得对吗？为什么？', 'answer': '不对。by 后面直接加交通工具（不加冠词/物主代词）：by car。如果想用 my father\u2019s car，应该说 in my father\u2019s car。', 'difficulty': 4, 'layer': 'connect'},
    ]

    topic_summary = "介词与连词是英语中的功能性词类——它们连接句子的各个部分，建立逻辑关系。介词分为时间介词（at/on/in）、地点介词（at/on/in）、方式介词（by/with/in）和其他固定搭配。连词分为并列连词（and/but/or/so）和从属连词（because/although/if/when）。关键规则包括：at点on天in月季年、because和so/although和but不能连用、by+交通工具不加冠词、since接时间点for接时间段。掌握介词固定搭配是提升英语地道性的关键。"
    key_insights = [
        'at点on天in月季年——时间介词的铁律，7个字解决90%的困惑',
        'because和so、although和but不能连用——这是中式英语最典型的特征之一',
        'by+交通工具不加冠词——by bus, by bike, by plane',
        '介词固定搭配（look at, listen to, be interested in等）不能推理，只能积累',
    ]
    common_mistakes = [
        {'mistake': 'because 和 so 连用', 'example': '"Because it rained, so I stayed home."', 'why': '中文"因为...所以..."是固定搭配，学生直接翻译成英语', 'how_to_explain': '英语一句话只能有一个"因果连词"。because 和 so 都是因果连词，像两个人同时开车——只要一个就够了。'},
        {'mistake': 'since 和 for 混淆', 'example': '"I have been here since two hours."', 'why': '中文"从两小时前到现在"用同一个表达，学生分不清时间点和时间段', 'how_to_explain': 'since = 从某个时间点开始（since 2020, since Monday）。for = 持续多长时间（for two hours, for a week）。用"点"和"段"来记。'},
        {'mistake': 'at/on/in 时间混淆', 'example': '"I will see you in Monday."', 'why': '中文用"在"一个词，英语有三个词对应不同的时间尺度', 'how_to_explain': '画一个时间金字塔：塔尖=at（精确点），中间=on（天），底座=in（月季年）。从上到下越来越"大"。'},
        {'mistake': 'although 和 but 连用', 'example': '"Although it rained, but we went out."', 'why': '同 because/so，中文"虽然...但是..."是固定搭配', 'how_to_explain': '同 because/so 规则——英语一句话只能用一个转折连词。用 although 就别用 but，用 but 就别用 although。'},
    ]
    alternate_explanations = [
        {'method': '时间金字塔', 'when_to_use': '学生记不住 at/on/in 的时间用法时', 'prompt': '画一个倒金字塔：最上面的尖是 at（at 8:00, at noon）——精确到点。中间是 on（on Monday, on my birthday）——精确到天。最下面是 in（in June, in 2025）——范围最大。从上到下：at→点，on→天，in→月季年。'},
        {'method': '因果关系单行道', 'when_to_use': '学生反复犯 because/so 连用错误时', 'prompt': '因果关系是一条单行道——你只能开一辆车（because 或 so）。中文是双车道，英语是单车道。每次写因果句时检查：有没有两辆车同时在跑？'},
        {'method': '手势记忆法（地点介词）', 'when_to_use': '学生混淆 on/above/over 时', 'prompt': 'on = 手摸桌子（接触表面），above = 手悬空在桌子上方（不接触），over = 手在桌子上方并覆盖（正上方，有跨越/覆盖含义）。用身体感知比看文字更有效。'},
    ]
    question_templates = {
        'difficulty_1_2': '出 2 道填空题：给句子让学生选择正确的介词（at/on/in 时间或地点）或连词（and/but/or/so）',
        'difficulty_3': '出 1 道改错题：给包含 because/so 连用或 since/for 混淆的句子让学生改正',
        'difficulty_4': '出 1 道翻译题：给一段中文让学生翻译，要求使用 3 个以上不同的介词固定搭配',
    }

    summary = "介词与连词是英语的'连接词'——介词表示关系（at 7:00, on the desk），连词连接成分（and, but, because）。重点规则：at点on天in月季年、because/so 不连用、by+交通工具不加冠词、固定搭配需积累。"

    node = make_node(slug, title, tier, difficulty, prereqs, trigger_title, trigger_text, trigger_question,
                     summary, sections, examples, practice, test,
                     topic_summary, key_insights, common_mistakes, alternate_explanations, question_templates)
    write_node('06-prepositions-conjunctions.yaml', node)


# ═══════════════════════════════════════════════════════════════
# We'll continue with more nodes. Let me write them in batches.
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Generating English knowledge nodes...")
    create_03_pronouns()
    create_05_adjectives_adverbs()
    create_06_prepositions_conjunctions()
    print("Batch 1 (nodes 03, 05, 06) done!")

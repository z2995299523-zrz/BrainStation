#!/usr/bin/env python
"""
Generate all 29 junior high school math knowledge nodes in the new format.
Reference format: 01-rational-numbers.yaml (display + ai_context).
"""
import yaml
from yaml.scalarstring import LiteralScalarString
import os

OUTPUT_DIR = r"D:\lernning-pro\math-english-camp\content\nodes\math"

def lit(s):
    """Create a YAML literal block scalar."""
    return LiteralScalarString(s)

def make_node(slug, num, title, difficulty, prereqs, trigger_info, concept_data,
              examples_data, practice_data, test_data, ai_data):
    """Build a complete node dict matching the 01-rational-numbers format."""
    trigger = {
        "type": trigger_info["type"],
        "title": trigger_info["title"],
        "content": {
            "text": lit(trigger_info["text"]),
            "question": trigger_info["question"],
        }
    }

    display = {
        "concept": concept_data,
        "examples": examples_data,
        "practice": practice_data,
        "test": test_data,
    }

    return {
        "slug": slug,
        "subject": "math",
        "title": title,
        "tier": "core",
        "difficulty": difficulty,
        "prerequisites": prereqs,
        "estimated_min": 25,
        "trigger": trigger,
        "display": display,
        "ai_context": ai_data,
    }


def write_yaml(node, filename):
    """Write a node dict to a YAML file using safe dump with literal blocks."""
    path = os.path.join(OUTPUT_DIR, filename)
    # Use a custom dumper that handles LiteralScalarString
    class LiteralDumper(yaml.SafeDumper):
        pass

    def literal_representer(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

    LiteralDumper.add_representer(LiteralScalarString, literal_representer)

    yaml_str = yaml.dump(node, Dumper=LiteralDumper, allow_unicode=True,
                         default_flow_style=False, sort_keys=False, width=200)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(yaml_str)

    # Validate by reading back
    with open(path, 'r', encoding='utf-8') as f:
        loaded = yaml.safe_load(f)
    assert loaded is not None, f"Validation failed: {filename}"
    assert "display" in loaded, f"Missing display: {filename}"
    assert "ai_context" in loaded, f"Missing ai_context: {filename}"
    print(f"  ✓ {filename} — {len(loaded.get('display',{}).get('practice',[]))} practice, "
          f"{len(loaded.get('display',{}).get('test',[]))} test, "
          f"{len(loaded.get('display',{}).get('examples',[]))} examples")
    return True


# ============================================================================
# MODULE DEFINITIONS
# ============================================================================

def make_02_polynomials():
    """02-polynomials: 整式的加减 (Rewrite from old format)"""
    return make_node(
        slug="polynomials", num="02", title="整式的加减", difficulty=1,
        prereqs=["rational-numbers"],
        trigger_info={
            "type": "story",
            "title": "代数：把话说给全世界听",
            "text": (
                "16 世纪，法国数学家韦达做了一件了不起的事：\n"
                "他用字母代替数字来写数学。\n"
                "\n"
                "在此之前，每个国家的数学书都用自己的语言描述。\n"
                "韦达用 $a + b$ 就搞定了——全世界都能看懂。\n"
                "\n"
                "从那天起，数学真正成了通用语言。\n"
                "更妙的是：用字母表示数之后，你就可以发现规律而不只是算答案。\n"
                "$(a+b)^2 = a^2 + 2ab + b^2$——一句话概括了无穷多种数字运算。"
            ),
            "question": "为什么要用字母表示数？用数字不好吗？",
        },
        concept_data={
            "summary": "整式是由数和字母通过加、减、乘运算组成的式子，掌握同类项合并和去括号是代数运算的基础。",
            "sections": [
                {
                    "title": "一、单项式与多项式",
                    "content": lit(
                        "单项式：数与字母的乘积，如 $3x^2$、$-5ab$\n"
                        "  - 系数：数字部分（$3x^2$ 的系数是 $3$）\n"
                        "  - 次数：所有字母的指数和（$3x^2y$ 的次数是 $3$）\n"
                        "\n"
                        "多项式：几个单项式的和，如 $3x^2 - 5x + 2$\n"
                        "  - 项：多项式中的每个单项式\n"
                        "  - 常数项：不含字母的项\n"
                        "  - 次数：最高次项的次数\n"
                    ),
                },
                {
                    "title": "二、同类项与合并",
                    "content": lit(
                        "同类项：字母部分完全相同的项\n"
                        "  ✓ $3x^2$ 和 $-2x^2$ 是同类项（都是 $x^2$）\n"
                        "  ✗ $3x^2$ 和 $3x$ 不是同类项（次数不同）\n"
                        "  ✗ $3x^2$ 和 $3y^2$ 不是同类项（字母不同）\n"
                        "\n"
                        "合并同类项：系数相加，字母部分不变\n"
                        "  $3x^2 + 5x^2 = 8x^2$\n"
                        "  $7ab - 3ab = 4ab$\n"
                        "  $2x + 3y - x + 2y = x + 5y$\n"
                    ),
                },
                {
                    "title": "三、去括号法则",
                    "content": lit(
                        "括号前是 $+$ 号：直接去掉括号，各项符号不变\n"
                        "  $+(a+b-c) = a+b-c$\n"
                        "\n"
                        "括号前是 $-$ 号：去掉括号，括号内每一项都变号\n"
                        "  $-(a+b-c) = -a-b+c$\n"
                        "\n"
                        "为什么？因为负号本质是乘以 $-1$：\n"
                        "  $-(a-b) = (-1)\\times(a-b) = -a+b$\n"
                        "\n"
                        "常见错误：$-(x+3)$ 写成 $-x+3$（错了！应该是 $-x-3$）\n"
                    ),
                },
                {
                    "title": "四、整式加减的步骤",
                    "content": lit(
                        "1. 有括号先去括号\n"
                        "2. 找出所有同类项\n"
                        "3. 合并同类项\n"
                        "\n"
                        "例题：化简 $3(x+2) - 2(x-1)$\n"
                        "  $= 3x+6 - 2x+2$\n"
                        "  $= (3x-2x) + (6+2)$\n"
                        "  $= x+8$\n"
                    ),
                },
            ],
        },
        examples_data=[
            {
                "title": "合并同类项",
                "problem": '化简 $3x + 5x - 2x$',
                "steps": [
                    "第 1 步：$3x$、$5x$、$-2x$ 是同类项（都是 $x$）",
                    "第 2 步：系数相加：$3+5-2=6$",
                    "第 3 步：答案：$6x$",
                ],
                "answer": "6x",
            },
            {
                "title": "去括号陷阱",
                "problem": '化简 $-(x-y)$',
                "steps": [
                    "第 1 步：括号前是负号，去括号后各项变号",
                    "第 2 步：$x$ 变 $-x$，$-y$ 变 $+y$",
                    "第 3 步：答案：$-x+y$",
                ],
                "answer": "-x+y",
            },
            {
                "title": "综合化简",
                "problem": '化简 $2(3a-b) - (a+2b)$',
                "steps": [
                    "第 1 步：先去括号：$6a-2b - a-2b$",
                    "第 2 步：合并同类项 $a$：$6a-a=5a$",
                    "第 3 步：合并同类项 $b$：$-2b-2b=-4b$",
                    "第 4 步：答案：$5a-4b$",
                ],
                "answer": "5a-4b",
            },
        ],
        practice_data=[
            {"id": "poly-prac-001", "stem": '合并：$7a + 3a - 5a$', "answer": "5a", "hints": ["所有项都含字母 a", "系数相加：7+3-5"]},
            {"id": "poly-prac-002", "stem": '去括号：$-(m-2n)$', "answer": "-m+2n", "hints": ["括号前是负号，每项变号", "m 变 -m，-2n 变 +2n"]},
            {"id": "poly-prac-003", "stem": '化简：$4x - (x-3)$', "answer": "3x+3", "hints": ["先去括号：-(x-3) = -x+3", "再合并同类项"]},
            {"id": "poly-prac-004", "stem": '$3a$ 和 $3a^2$ 是同类项吗？', "answer": "不是，因为 a 的次数不同（1 和 2）", "hints": ["同类项要求字母和次数都相同", "比较 a 的指数"]},
            {"id": "poly-prac-005", "stem": '化简：$2(x+y) - (x-y)$', "answer": "x+3y", "hints": ["先展开括号", "注意 -(x-y) = -x+y"]},
        ],
        test_data=[
            {"id": "poly-test-001", "stem": '合并：$5x^2 - 3x^2 + x^2$', "answer": "3x^2", "difficulty": 1, "layer": "operation"},
            {"id": "poly-test-002", "stem": '去括号：$-( -x + y )$', "answer": "x-y", "difficulty": 1, "layer": "operation"},
            {"id": "poly-test-003", "stem": '化简：$3(m-2n) - 2(2m-n)$', "answer": "-m-4n", "difficulty": 2, "layer": "operation"},
            {"id": "poly-test-004", "stem": "下列哪组是同类项？A: $2x$和$2x^2$  B: $3ab$和$3ba$  C: $5$和$5x$  D: $x^2y$和$xy^2$", "answer": "B", "difficulty": 1, "layer": "understand"},
            {"id": "poly-test-005", "stem": '若 $A=3x-2$，$B=2x+1$，求 $A-B$', "answer": "x-3", "difficulty": 2, "layer": "operation"},
            {"id": "poly-test-006", "stem": "小明化简 $-(x-3)$ 得到 $-x-3$。他错在哪里？正确的答案是什么？", "answer": "括号内 -3 去括号后应变号为 +3。正确答案：-x+3", "difficulty": 2, "layer": "understand"},
            {"id": "poly-test-007", "stem": '已知 $a=-1$，$b=2$，求整式 $3a-2b+ab$ 的值', "answer": "-9", "difficulty": 3, "layer": "connect"},
            {"id": "poly-test-008", "stem": "任意写一个二次三项式，然后把它化简（把同类项合并）", "answer": "例如：x^2+3x-2（答案不唯一，需有3项且最高次为2）", "difficulty": 2, "layer": "connect"},
        ],
        ai_data={
            "topic_summary": "整式的加减是代数的第一道门。从具体数字走向用字母表示一般规律，是数学思维的第一次飞跃。掌握同类项、去括号和合并运算，是后续所有代数（方程、函数、因式分解）的基础。",
            "key_insights": [
                "同类项 = 字母部分完全相同，合并时只改系数不改字母",
                "去括号负号规则本质是分配律：-(a+b) = (-1)·a + (-1)·b = -a-b",
                "代数让'发现规律'从猜变成了算——一个公式概括无穷多种情况",
                "整式是方程和函数的基础：不会化简整式就解不了方程",
            ],
            "common_mistakes": [
                {
                    "mistake": "括号前是负号时，只给第一项变号",
                    "example": "$-(x+3)$ 写成 $-x+3$",
                    "why": "学生以为负号只作用于最近的一项",
                    "how_to_explain": "括号前的负号是'乘以-1'，分配律要求括号内每一项都变号。就像发钱——每个人都得拿到。",
                },
                {
                    "mistake": "认为字母不同的项也能合并",
                    "example": "$3x + 2y = 5xy$",
                    "why": "混淆了加法和乘法",
                    "how_to_explain": "苹果和橘子不能加在一起。3个苹果+2个橘子≠5个苹果橘子。",
                },
                {
                    "mistake": "混淆系数和次数",
                    "example": "认为 $3x^2$ 和 $5x^2$ 合并后是 $8x^4$",
                    "why": "把系数相加的规则误用到次数上",
                    "how_to_explain": "合并同类项就像数苹果：3个红苹果+5个红苹果=8个红苹果，苹果还是苹果，不会变成苹果的平方。",
                },
            ],
            "alternate_explanations": [
                {
                    "method": "水果类比法",
                    "when_to_use": "学生对'同类项'概念感到抽象时",
                    "prompt": "把 x 想成苹果，y 想成橘子。3x+2x 就是 3个苹果+2个苹果=5个苹果。但 3x+2y 是 3个苹果+2个橘子，不能合并。",
                },
                {
                    "method": "天平模型",
                    "when_to_use": "学生不理解去括号时",
                    "prompt": "把括号想像成一个盒子。盒子外面有负号，等于说'把盒子里每样东西都取反'。盒子里的正数变负数，负数变正数。",
                },
            ],
            "question_templates": {
                "difficulty_1_2": "出 2 道直接的合并同类项和去括号题，数字简单",
                "difficulty_3": "出 1 道先代入数值再计算的综合题",
                "difficulty_4": "出 1 道需要解释'为什么'的理解题",
            },
        },
    )


def make_03_linear_equation():
    """03-linear-equation: 一元一次方程 (Rewrite)"""
    return make_node(
        slug="linear-equation", num="03", title="一元一次方程", difficulty=2,
        prereqs=["rational-numbers", "polynomials"],
        trigger_info={
            "type": "story",
            "title": "未知数：人类最强大的思维工具",
            "text": (
                "古埃及人在《莱因德纸草书》（公元前 1650 年）中就解过方程。\n"
                "他们用\"堆\"（aha）来代表未知数。\n"
                "\n"
                "比如：\"一堆加上它的 1/4 等于 15，这堆是多少？\"\n"
                "用今天的写法：$x + x/4 = 15$ → $x = 12$\n"
                "\n"
                "古人没学过代数，但他们发现：承认有个我们不知道的数存在，\n"
                "我们就可以通过已知关系把它逼出来。\n"
                "这个思维——'假设未知，推理已知'——是人类最伟大的智慧之一。"
            ),
            "question": "如果你不知道一个数是多少，你怎么可能算出来它？",
        },
        concept_data={
            "summary": "一元一次方程含一个未知数且最高次数为1，通过等式性质（两边同时加减乘除）求解，核心是移项变号和系数化为1。",
            "sections": [
                {
                    "title": "一、什么是方程",
                    "content": lit(
                        "方程：含有未知数的等式\n"
                        "  例：$2x + 3 = 7$（有未知数 $x$，有等号）\n"
                        "\n"
                        "一元一次方程：一个未知数 + 最高次数为 1\n"
                        "  标准形式：$ax + b = 0$（$a \\neq 0$）\n"
                        "\n"
                        "方程的解（根）：使等式成立的未知数的值\n"
                        "  例：$x=2$ 代入 $2x+3=7$：$2\\times2+3=4+3=7$ ✓\n"
                    ),
                },
                {
                    "title": "二、等式的性质——解方程的依据",
                    "content": lit(
                        "性质 1：等式两边同时加（或减）同一个数，等式仍成立\n"
                        "  如果 $a=b$，则 $a+c=b+c$\n"
                        "\n"
                        "性质 2：等式两边同时乘（或除）同一个不为 0 的数，等式仍成立\n"
                        "  如果 $a=b$，则 $ac=bc$（$c \\neq 0$）\n"
                        "\n"
                        "直观理解：天平。两边放等重的东西，加上或拿走同样的砝码，天平仍然平衡。\n"
                    ),
                },
                {
                    "title": "三、解方程五步法",
                    "content": lit(
                        "1. 去分母：各项同乘分母的最小公倍数\n"
                        "2. 去括号：按去括号法则展开\n"
                        "3. 移项：含未知数的项移到左边，常数项移到右边——过等号要变号！\n"
                        "4. 合并同类项：分别合并左右两边\n"
                        "5. 系数化为 1：两边同除以未知数的系数\n"
                        "\n"
                        "核心口诀：\n"
                        "  去分母 → 去括号 → 移项变号 → 合并 → 系数化 1\n"
                    ),
                },
                {
                    "title": "四、为什么移项要变号？",
                    "content": lit(
                        "移项的本质是等式两边同时做同一运算：\n"
                        "\n"
                        "$2x + 3 = 7$\n"
                        "两边同时减 3：$2x + 3 - 3 = 7 - 3$\n"
                        "$2x = 4$\n"
                        "\n"
                        "从表面看，$+3$ 从左边跑到右边变成了 $-3$——这只是简记。\n"
                        "真相是：两边同时做了减法。\n"
                        "移项 = 等式性质的快捷写法。\n"
                    ),
                },
            ],
        },
        examples_data=[
            {
                "title": "简单方程",
                "problem": '解 $2x + 3 = 7$',
                "steps": [
                    "第 1 步：移项，把常数 $+3$ 移到右边变 $-3$：$2x = 7-3$",
                    "第 2 步：$2x = 4$",
                    "第 3 步：系数化为 1：$x = 4 \\div 2 = 2$",
                ],
                "answer": "x=2",
            },
            {
                "title": "含括号方程",
                "problem": '解 $3(x+2) - 2(x-1) = 14$',
                "steps": [
                    "第 1 步：去括号：$3x+6 - 2x+2 = 14$",
                    "第 2 步：合并同类项：$(3x-2x) + (6+2) = x+8 = 14$",
                    "第 3 步：移项：$x = 14-8 = 6$",
                ],
                "answer": "x=6",
            },
            {
                "title": "含分母方程",
                "problem": '解 $\\frac{x+1}{2} - \\frac{x-2}{3} = 1$',
                "steps": [
                    "第 1 步：去分母，两边同乘 6：$3(x+1) - 2(x-2) = 6$",
                    "第 2 步：去括号：$3x+3 - 2x+4 = 6$",
                    "第 3 步：合并：$x+7 = 6$",
                    "第 4 步：移项：$x = -1$",
                ],
                "answer": "x=-1",
            },
        ],
        practice_data=[
            {"id": "leq-prac-001", "stem": '解 $x + 5 = 12$', "answer": "x=7", "hints": ["移项：把 +5 移到右边", "12-5=?"]},
            {"id": "leq-prac-002", "stem": '解 $3x = 15$', "answer": "x=5", "hints": ["系数化为 1", "两边同除以 3"]},
            {"id": "leq-prac-003", "stem": '解 $2x - 1 = 5$', "answer": "x=3", "hints": ["先移项把 -1 移到右边", "再系数化 1"]},
            {"id": "leq-prac-004", "stem": '解 $4(x-1) = 2x+6$', "answer": "x=5", "hints": ["先去括号", "把含 x 的都移到左边"]},
            {"id": "leq-prac-005", "stem": '$x=3$ 是方程 $2x+1=7$ 的解吗？', "answer": "是，2×3+1=7", "hints": ["代入检验", "左边=？右边=？"]},
        ],
        test_data=[
            {"id": "leq-test-001", "stem": '解 $5x - 3 = 2x + 9$', "answer": "x=4", "difficulty": 1, "layer": "operation"},
            {"id": "leq-test-002", "stem": '解 $2(x-3) + 5 = 3x - 1$', "answer": "x=0", "difficulty": 2, "layer": "operation"},
            {"id": "leq-test-003", "stem": '解 $\\frac{x}{2} - \\frac{x-1}{3} = 1$', "answer": "x=4", "difficulty": 2, "layer": "operation"},
            {"id": "leq-test-004", "stem": "方程 $2x+3=7$ 的解是？A: 1  B: 2  C: 3  D: 4", "answer": "B", "difficulty": 1, "layer": "understand"},
            {"id": "leq-test-005", "stem": "小明解 $2x+3=7$ 第一步写 $2x=7+3$。他错在哪里？", "answer": "移项3到右边应变号为-3，不是+3。正确：2x=7-3=4", "difficulty": 2, "layer": "understand"},
            {"id": "leq-test-006", "stem": '某数的 3 倍加 5 等于这个数的 2 倍加 12，求这个数', "answer": "x=7", "difficulty": 2, "layer": "connect"},
            {"id": "leq-test-007", "stem": '若方程 $2x+k=3x-1$ 的解为 $x=2$，求 $k$ 的值', "answer": "k=1", "difficulty": 3, "layer": "connect"},
            {"id": "leq-test-008", "stem": "请编写一个一元一次方程，使它的解为 $x=5$", "answer": "例如：2x-3=7（答案不唯一，只要x=5能成立）", "difficulty": 3, "layer": "connect"},
        ],
        ai_data={
            "topic_summary": "一元一次方程是代数解题的第一课。它教会学生用等式性质（天平原理）来'逼出'未知数的值。移项变号是核心技能，背后是等式两边同时操作的思想。方程思维（从已知推理未知）是整个科学方法的基础。",
            "key_insights": [
                "方程 = 天平：等号两边永远保持平衡",
                "移项变号不是死规则——是等式两边同时加减的结果",
                "五步法：去分母→去括号→移项→合并→系数化1",
                "解方程的本质：通过已知关系反向推导未知数的值",
            ],
            "common_mistakes": [
                {
                    "mistake": "移项忘记变号",
                    "example": "$2x+3=7$ → $2x=7+3$",
                    "why": "只记得把数移到另一边，忘了变号",
                    "how_to_explain": "移项本质是两边同时操作。$2x+3=7$ 两边同时减3，左边+3变成0，右边7变成4。所以+3到右边要变-3。",
                },
                {
                    "mistake": "去分母时漏乘某些项",
                    "example": "$\\frac{x}{2}+1=3$ ×2 → $x+1=6$（常数项1没有乘2）",
                    "why": "只对分数项乘以分母",
                    "how_to_explain": "等式两边同乘一个数，是每一项都乘！就像发工资，每个人都要发。",
                },
                {
                    "mistake": "去括号符号错误",
                    "example": "$3x-2(x-1)=3x-2x-2$",
                    "why": "忘记了括号前负号也要作用于括号内每一项",
                    "how_to_explain": "$-2(x-1) = -2x + 2$（注意-2×(-1)=+2）",
                },
            ],
            "alternate_explanations": [
                {
                    "method": "天平类比法",
                    "when_to_use": "学生不理解等式性质时",
                    "prompt": "把方程想象成天平。左边放 2x+3，右边放 7。天平平衡。你想求出 x，就得从左边拿走 3 个砝码——但天平另一边也必须同时拿走 3 个砝码才能保持平衡。",
                },
                {
                    "method": "侦探推理法",
                    "when_to_use": "学生对'解方程'的意义感到迷茫时",
                    "prompt": "方程就像一个犯罪现场：你知道结果（7），知道一些线索（2x+3），你的任务是还原真相——x 到底是多少？每一步推导都是一条线索。",
                },
            ],
            "question_templates": {
                "difficulty_1_2": "出 2 道简单的一元一次方程求解题（数字简单，考查基本移项）",
                "difficulty_3": "出 1 道含分母或括号的综合方程题",
                "difficulty_4": "出 1 道应用题，需要先根据文字建立方程再求解",
            },
        },
    )


def make_04_geometry_basics():
    """04-geometry-basics: 几何图形初步"""
    return make_node(
        slug="geometry-basics", num="04", title="几何图形初步", difficulty=1,
        prereqs=["rational-numbers"],
        trigger_info={
            "type": "story",
            "title": "欧几里得与《几何原本》",
            "text": (
                "公元前 300 年，古希腊数学家欧几里得写了一本书叫《几何原本》。\n"
                "这本书从 5 条简单的公理出发，推导出 465 个定理，\n"
                "构建了整个几何学大厦。\n"
                "\n"
                "这本书的影响力仅次于《圣经》——被使用了 2000 多年！\n"
                "直到 20 世纪，英国还在用《几何原本》当中学教材。\n"
                "\n"
                "欧几里得的哲学是：复杂的世界可以用几条简单规则解释清楚。\n"
                "这就是几何的魅力。"
            ),
            "question": "你能说出生活中 3 种不同的几何图形吗？它们各有什么用处？",
        },
        concept_data={
            "summary": "几何图形初步学习点、线、面、体等基本几何元素，掌握直线、射线、线段的区别，理解角的概念与度量，为后续几何学习打好空间直觉基础。",
            "sections": [
                {
                    "title": "一、几何的基本元素",
                    "content": lit(
                        "点：没有大小，只有位置。用大写字母表示，如点 $A$\n"
                        "线：由无数个点组成\n"
                        "面：由线围成\n"
                        "体：由面围成\n"
                        "\n"
                        "点动成线、线动成面、面动成体\n"
                    ),
                },
                {
                    "title": "二、直线、射线、线段",
                    "content": lit(
                        "直线：无限延伸，没有端点。表示：直线 $AB$ 或直线 $l$\n"
                        "  - 两点确定一条直线\n"
                        "  - 过一点有无数条直线\n"
                        "\n"
                        "射线：有一个端点，向一方无限延伸。表示：射线 $OA$\n"
                        "\n"
                        "线段：有两个端点，有限长度。表示：线段 $AB$ 或 $AB$\n"
                        "  - 在所有连接两点的线中，线段最短\n"
                        "  - 两点间线段的长度叫做两点间的距离\n"
                    ),
                },
                {
                    "title": "三、角的概念",
                    "content": lit(
                        "角：由两条有公共端点的射线组成\n"
                        "  - 顶点：公共端点\n"
                        "  - 边：两条射线\n"
                        "  表示：$\\angle AOB$ 或 $\\angle 1$\n"
                        "\n"
                        "角的分类：\n"
                        "  - 锐角：$0° < \\alpha < 90°$\n"
                        "  - 直角：$\\alpha = 90°$\n"
                        "  - 钝角：$90° < \\alpha < 180°$\n"
                        "  - 平角：$\\alpha = 180°$\n"
                        "  - 周角：$\\alpha = 360°$\n"
                    ),
                },
                {
                    "title": "四、角的度量与计算",
                    "content": lit(
                        "度量单位：度（°）、分（′）、秒（″）\n"
                        "  $1° = 60'$，$1' = 60''$\n"
                        "\n"
                        "互余：$\\angle A + \\angle B = 90°$\n"
                        "互补：$\\angle A + \\angle B = 180°$\n"
                        "\n"
                        "对顶角：两直线相交，对顶角相等\n"
                        "邻补角：相邻且互补的两个角\n"
                    ),
                },
            ],
        },
        examples_data=[
            {
                "title": "角的计算",
                "problem": '一个角的余角是 $25°$，求这个角',
                "steps": [
                    "第 1 步：余角 = 90° - 这个角",
                    "第 2 步：$90° - x = 25°$",
                    "第 3 步：$x = 90° - 25° = 65°$",
                ],
                "answer": "65°",
            },
            {
                "title": "对顶角",
                "problem": '两直线相交，其中一个角是 $50°$，求它的对顶角',
                "steps": [
                    "第 1 步：对顶角相等",
                    "第 2 步：对顶角 = $50°$",
                ],
                "answer": "50°",
            },
            {
                "title": "角度制换算",
                "problem": '计算 $1.5°$ 等于多少分',
                "steps": [
                    "第 1 步：$1° = 60'$",
                    "第 2 步：$1.5° = 1.5 \\times 60' = 90'$",
                ],
                "answer": "90′",
            },
        ],
        practice_data=[
            {"id": "gb-prac-001", "stem": "直线有几个端点？", "answer": "0 个（无限延伸）", "hints": ["直线能无限延伸", "端点意味着结束"]},
            {"id": "gb-prac-002", "stem": '$\\angle A$ 和 $\\angle B$ 互补，$\\angle A = 60°$，求 $\\angle B$', "answer": "120°", "hints": ["互补：两角和为 180°", "180° - 60° = ?"]},
            {"id": "gb-prac-003", "stem": "一个角的补角比它的余角大多少？", "answer": "90°", "hints": ["补角=180°-x，余角=90°-x", "两者相减"]},
            {"id": "gb-prac-004", "stem": "线段 AB = 5cm，C 是 AB 的中点，求 AC", "answer": "2.5cm", "hints": ["中点到两端距离相等", "AC = AB ÷ 2"]},
            {"id": "gb-prac-005", "stem": "判断：射线是直线的一半", "answer": "错，射线只有一个端点，向一方无限延伸，长度也是无限的", "hints": ["射线有多长？", "直线有多长？"]},
        ],
        test_data=[
            {"id": "gb-test-001", "stem": "过一点可以画多少条直线？A: 1  B: 2  C: 无数  D: 0", "answer": "C", "difficulty": 1, "layer": "understand"},
            {"id": "gb-test-002", "stem": '已知 $\\angle A = 30°$，$\\angle B$ 是 $\\angle A$ 的余角，$\\angle C$ 是 $\\angle B$ 的补角，求 $\\angle C$', "answer": "120°", "difficulty": 2, "layer": "operation"},
            {"id": "gb-test-003", "stem": '$36°15\\'$ 加上 $42°55\\'$ 等于多少？', "answer": "79°10′", "difficulty": 2, "layer": "operation"},
            {"id": "gb-test-004", "stem": "下列说法正确的是？A: 延长直线AB  B: 延长射线OA  C: 延长线段AB  D: 射线AB和射线BA是同一条射线", "answer": "C", "difficulty": 2, "layer": "understand"},
            {"id": "gb-test-005", "stem": "时钟在 3:00 时，时针和分针的夹角是多少度？", "answer": "90°", "difficulty": 1, "layer": "connect"},
            {"id": "gb-test-006", "stem": "已知 C 是线段 AB 的中点，AB=10，D 是 AC 的中点，求 AD", "answer": "2.5", "difficulty": 3, "layer": "operation"},
            {"id": "gb-test-007", "stem": "请画图说明：两点确定一条直线", "answer": "画两个点，过这两个点只能画一条直线。", "difficulty": 2, "layer": "connect"},
            {"id": "gb-test-008", "stem": "一个角的补角是这个角的 3 倍，求这个角", "answer": "45°", "difficulty": 3, "layer": "connect"},
        ],
        ai_data={
            "topic_summary": "几何图形初步是初中几何的第一章，建立点、线、面、体的基本概念。重点掌握直线/射线/线段的区别、角的分类（锐/直/钝/平/周）、余角补角计算、以及角度制的换算。这些是后续三角形、四边形、圆等几何内容的基础语言。",
            "key_insights": [
                "两点之间线段最短——这是几何最基础的优化原理",
                "对顶角相等是第一个重要的几何定理",
                "角 = 两条射线的位置关系，不是线段的长度",
                "几何从少数几条公理出发，用逻辑推导出整个体系",
            ],
            "common_mistakes": [
                {
                    "mistake": "混淆射线和线段",
                    "example": "说'延长射线AB'",
                    "why": "射线已经向一方无限延伸，不能再延长",
                    "how_to_explain": "射线像手电筒的光——已经照向无限远，怎么还能延长？只有线段才能延长。",
                },
                {
                    "mistake": "角度进制当十进制算",
                    "example": "$0.5° = 50'$",
                    "why": "把度分秒的60进制当成十进制",
                    "how_to_explain": "度分秒是60进制（1°=60′），就像时间是60进制（1小时=60分钟），不是十进制。",
                },
                {
                    "mistake": "余角和补角搞混",
                    "example": "把互补算成90°",
                    "why": "两个概念记反了",
                    "how_to_explain": "余→90°（'余'字有3划→3×30=90），补→180°（'补'靠'卜'+'卜'=十十→十+八=180的谐音）。或者记：余角是'剩余到90'，补角是'补充到180'。",
                },
            ],
            "alternate_explanations": [
                {
                    "method": "手影游戏法",
                    "when_to_use": "学生对射线概念感到抽象时",
                    "prompt": "打开手电筒照向夜空——光从手电筒出发，一直射向远方永不停。这就是射线：一个端点，无限延伸。",
                },
                {
                    "method": "钟表模型",
                    "when_to_use": "学生学习角度时",
                    "prompt": "看钟表：3:00 时针和分针成 90°（直角），6:00 成 180°（平角）。每一大格是 30°（360°÷12）。",
                },
            ],
            "question_templates": {
                "difficulty_1_2": "出 2 道直接的角度计算题（余角、补角）",
                "difficulty_3": "出 1 道角度综合运算题（含度分秒换算）",
                "difficulty_4": "出 1 道需要画图分析和推理的几何题",
            },
        },
    )


def make_05_parallel_lines():
    """05-parallel-lines: 相交线与平行线"""
    return make_node(
        slug="parallel-lines", num="05", title="相交线与平行线", difficulty=2,
        prereqs=["geometry-basics"],
        trigger_info={
            "type": "story",
            "title": "平行公理：一条争论了2000年的公理",
            "text": (
                "欧几里得在《几何原本》中列出了 5 条公理。\n"
                "前 4 条都很简洁——第 5 条却特别长：\n"
                "\n"
                "\"若一条直线与两条直线相交，同侧内角之和小于两直角，\n"
                " 则这两条直线无限延长后会在该侧相交。\"\n"
                "\n"
                "2000 年来，数学家们试图从其他 4 条公理证明第 5 条——但都失败了。\n"
                "直到 19 世纪，罗巴切夫斯基和黎曼说：\n"
                "\"把第 5 公理改了会怎样？\"——于是诞生了非欧几何。\n"
                "\n"
                "一个看似'显然'的公理，竟然藏着整个宇宙的秘密。"
            ),
            "question": "两条永不相交的直线就是平行线。你生活中见过哪些平行线？",
        },
        concept_data={
            "summary": "相交线与平行线研究两条直线的位置关系，重点掌握对顶角、邻补角、同位角/内错角/同旁内角的识别与性质，以及平行线的判定与性质定理。",
            "sections": [
                {
                    "title": "一、两条直线的位置关系",
                    "content": lit(
                        "相交：有一个公共点（交点）\n"
                        "平行：在同一平面内，永不相交\n"
                        "\n"
                        "垂直：相交成 90° 的特殊情况\n"
                        "  - 过一点有且只有一条直线与已知直线垂直\n"
                        "  - 垂线段最短\n"
                    ),
                },
                {
                    "title": "二、相交线产生的角",
                    "content": lit(
                        "两直线相交形成 4 个角：\n"
                        "  - 对顶角：$\\angle 1$ 与 $\\angle 3$ 是对顶角，$\\angle 2$ 与 $\\angle 4$ 是对顶角\n"
                        "  - 对顶角相等\n"
                        "\n"
                        "邻补角：相邻且互补的两个角（和为 180°）\n"
                        "  $\\angle 1 + \\angle 2 = 180°$\n"
                    ),
                },
                {
                    "title": "三、三线八角",
                    "content": lit(
                        "一条直线截两条直线，形成 8 个角：\n"
                        "\n"
                        "同位角：在截线同侧且在两条被截线同侧的角\n"
                        "  $\\angle 1$ 和 $\\angle 5$ 是同位角\n"
                        "\n"
                        "内错角：在截线两侧且都在两条被截线内侧的角\n"
                        "  $\\angle 3$ 和 $\\angle 6$ 是内错角\n"
                        "\n"
                        "同旁内角：在截线同侧且都在两条被截线内侧的角\n"
                        "  $\\angle 3$ 和 $\\angle 5$ 是同旁内角\n"
                    ),
                },
                {
                    "title": "四、平行线的判定与性质",
                    "content": lit(
                        "判定（如何证明平行）：\n"
                        "  - 同位角相等 → 两直线平行\n"
                        "  - 内错角相等 → 两直线平行\n"
                        "  - 同旁内角互补 → 两直线平行\n"
                        "\n"
                        "性质（平行能推出什么）：\n"
                        "  - 两直线平行 → 同位角相等\n"
                        "  - 两直线平行 → 内错角相等\n"
                        "  - 两直线平行 → 同旁内角互补\n"
                        "\n"
                        "注意：判定和性质互为逆命题！别搞反了。\n"
                    ),
                },
            ],
        },
        examples_data=[
            {
                "title": "同位角判定平行",
                "problem": '如图，$\\angle 1 = \\angle 2 = 60°$，判断 $a$ 是否平行 $b$',
                "steps": [
                    "第 1 步：$\\angle 1$ 和 $\\angle 2$ 是同位角",
                    "第 2 步：同位角相等（都是 60°）",
                    "第 3 步：所以 $a \\parallel b$",
                ],
                "answer": "a∥b",
            },
            {
                "title": "内错角求角",
                "problem": '$a \\parallel b$，$\\angle 1 = 70°$，$\\angle 1$ 和 $\\angle 2$ 是内错角，求 $\\angle 2$',
                "steps": [
                    "第 1 步：$a \\parallel b$ → 内错角相等",
                    "第 2 步：$\\angle 2 = \\angle 1 = 70°$",
                ],
                "answer": "70°",
            },
            {
                "title": "同旁内角求角",
                "problem": '$a \\parallel b$，$\\angle 1 = 65°$，$\\angle 1$ 和 $\\angle 2$ 是同旁内角，求 $\\angle 2$',
                "steps": [
                    "第 1 步：$a \\parallel b$ → 同旁内角互补",
                    "第 2 步：$\\angle 2 = 180° - 65° = 115°$",
                ],
                "answer": "115°",
            },
        ],
        practice_data=[
            {"id": "pl-prac-001", "stem": "对顶角有什么性质？", "answer": "对顶角相等", "hints": ["看图：两条直线交叉", "上面的角和下面的角什么关系？"]},
            {"id": "pl-prac-002", "stem": '如图，$a \\parallel b$，$\\angle 1 = 50°$，$\\angle 1$和$\\angle 2$是同位角，求$\\angle 2$', "answer": "50°", "hints": ["平行线的性质", "同位角什么关系？"]},
            {"id": "pl-prac-003", "stem": '如图，$\\angle 1 = \\angle 2$，能判断 $a \\parallel b$ 吗？为什么？', "answer": "能，同位角相等，两直线平行", "hints": ["这是什么角？", "对应的是哪个判定定理？"]},
            {"id": "pl-prac-004", "stem": "如果两个角是同旁内角且一个角为 $75°$，另一个角为多少度时两直线平行？", "answer": "105°", "hints": ["同旁内角什么关系？", "互补 = 和为 180°"]},
            {"id": "pl-prac-005", "stem": "过直线外一点可以画几条直线与已知直线平行？", "answer": "1 条（且只有 1 条）", "hints": ["想想欧几里得第 5 公理", "过一点能画多少条不交的直线？"]},
        ],
        test_data=[
            {"id": "pl-test-001", "stem": '如图，$a \\parallel b$，$\\angle 1 = 108°$，求 $\\angle 2$（同位角）', "answer": "108°", "difficulty": 1, "layer": "operation"},
            {"id": "pl-test-002", "stem": '如图，$\\angle 1 = 65°$，$\\angle 2 = 65°$，判断 $a$ 与 $b$ 是否平行', "answer": "平行（同位角相等）", "difficulty": 1, "layer": "understand"},
            {"id": "pl-test-003", "stem": '如图，$\\angle 3 = 120°$，$\\angle 5 = 60°$，判断 $a \\parallel b$ 吗？', "answer": "平行（同旁内角互补，120°+60°=180°）", "difficulty": 2, "layer": "understand"},
            {"id": "pl-test-004", "stem": "下列哪个不是判定平行的方法？A:同位角相等  B:内错角相等  C:对顶角相等  D:同旁内角互补", "answer": "C", "difficulty": 2, "layer": "understand"},
            {"id": "pl-test-005", "stem": '$a \\parallel b$，$\\angle 1 = 40°$，$\\angle 1$ 与 $\\angle 2$ 是内错角，$\\angle 2$ 与 $\\angle 4$ 是对顶角，求 $\\angle 4$', "answer": "40°", "difficulty": 3, "layer": "operation"},
            {"id": "pl-test-006", "stem": '$a \\parallel b$，$\\angle 1 = 2x+10$，$\\angle 2 = 3x-20$（同位角），求 $x$', "answer": "x=30", "difficulty": 3, "layer": "connect"},
            {"id": "pl-test-007", "stem": "用你自己的话，说明'同位角相等两直线平行'和'两直线平行同位角相等'有什么区别？", "answer": "前者是判定（用角的关系证明平行），后者是性质（已知平行推出角的关系）。", "difficulty": 3, "layer": "understand"},
            {"id": "pl-test-008", "stem": "如图，$AB \\parallel CD$，$\\angle B = 30°$，$\\angle D = 45°$，求 $\\angle BED$（E在两条平行线之间）", "answer": "75°（辅助线法：过E作平行线）", "difficulty": 4, "layer": "connect"},
        ],
        ai_data={
            "topic_summary": "相交线与平行线是初中几何推理的起点。三线八角（同位角、内错角、同旁内角）的识别是关键技能，平行线的判定与性质互为逆命题，是学生第一次系统接触'正向/逆向'推理。" ,
            "key_insights": [
                "对顶角相等 → 这是最基础的角度关系",
                "三线八角识别是判定平行的核心技能",
                "判定和性质互为逆命题：一个用角推平行，一个用平行推角",
                "平行公理是无法证明的——它是几何体系的出发点",
            ],
            "common_mistakes": [
                {
                    "mistake": "混滑判定和性质",
                    "example": "题目给平行，学生说'同位角相等所以平行'",
                    "why": "分不清已知条件和要证明的结论",
                    "how_to_explain": "判定=用角证明平行（结论是平行）。性质=已知平行推出角（条件是平行）。先看题目给了什么条件。",
                },
                {
                    "mistake": "无法正确识别三线八角",
                    "example": "把同旁内角当成内错角",
                    "why": "对截线和被截线的位置关系不清楚",
                    "how_to_explain": "把截线想象成'刀'，两条被截线是'面包'。同位角在刀的同侧+面包的同侧；内错角在刀的两侧+面包内侧；同旁内角在刀的同侧+面包内侧。",
                },
                {
                    "mistake": "认为同旁内角相等",
                    "example": "平行时同旁内角也相等",
                    "why": "把同旁内角和同位角/内错角的性质搞混了",
                    "how_to_explain": "同位角和内错角是'相等'关系，同旁内角是'互补'（和为180°）。同旁=同在截线一旁但都在内部，它们像邻居，挨着挨着加起来就是180°。",
                },
            ],
            "alternate_explanations": [
                {
                    "method": "铁路轨道模型",
                    "when_to_use": "学生对三线八角关系感到混乱时",
                    "prompt": "把两条平行线想象成铁轨，截线是一根枕木。枕木和铁轨形成的角：左右对称的角相等，同侧的角互补。",
                },
                {
                    "method": "折叠纸法",
                    "when_to_use": "需要直观理解同位角/内错角时",
                    "prompt": "在一张纸上画一条截线穿过两条平行线，然后把纸对折——你会发现同位角完全重合（相等），内错角也完全重合（相等）。",
                },
            ],
            "question_templates": {
                "difficulty_1_2": "出 2 道直接的平行线角度计算题",
                "difficulty_3": "出 1 道需要同时用多个角关系的综合题",
                "difficulty_4": "出 1 道需要用辅助线构造平行线的推理题",
            },
        },
    )


def make_06_real_numbers():
    """06-real-numbers: 实数 (七年级下)"""
    return make_node(
        slug="real-numbers", num="06", title="实数", difficulty=2,
        prereqs=["rational-numbers"],
        trigger_info={
            "type": "story",
            "title": "希帕索斯之死：一个数引发的血案",
            "text": (
                "公元前 5 世纪，古希腊毕达哥拉斯学派相信：\n"
                "\"万物皆数\"——一切都可以用整数和分数来表示。\n"
                "\n"
                "直到希帕索斯发现：正方形的对角线长 $\\sqrt{2}$ 不能写成分数！\n"
                "他兴奋地向学派报告这个发现——\n"
                "结果被学派成员扔进了爱琴海。\n"
                "\n"
                "$\\sqrt{2}$ 是第一个被发现的无理数。\n"
                "希帕索斯用生命换来了数学史上一大步：\n"
                "原来，有理数之外还有一个更广阔的世界。"
            ),
            "question": "如果有理数是'能写成分数的数'，那什么样的数是'不能写成分数的'？",
        },
        concept_data={
            "summary": "实数包括有理数和无理数。无理数（如$\\sqrt{2}$、$\\pi$）不能写成分数形式，是无限不循环小数。掌握平方根、立方根的概念和运算，以及实数的分类和数轴表示。",
            "sections": [
                {
                    "title": "一、平方根与算术平方根",
                    "content": lit(
                        "平方根：若 $x^2 = a$，则 $x$ 叫做 $a$ 的平方根\n"
                        "  正数有两个平方根（一正一负）：$\\pm \\sqrt{a}$\n"
                        "  0 的平方根是 0\n"
                        "  负数没有平方根（因为任何实数的平方都 ≥ 0）\n"
                        "\n"
                        "算术平方根：$\\sqrt{a}$ 表示 $a$ 的正平方根（$a \\geq 0$）\n"
                        "  $\\sqrt{4} = 2$（不是 $\\pm 2$——算术平方根只取正！）\n"
                        "  $\\sqrt{(-3)^2} = \\sqrt{9} = 3$（先算平方再开方）\n"
                    ),
                },
                {
                    "title": "二、立方根",
                    "content": lit(
                        "立方根：若 $x^3 = a$，则 $x$ 叫做 $a$ 的立方根，记作 $\\sqrt[3]{a}$\n"
                        "  正数的立方根为正：$\\sqrt[3]{8} = 2$\n"
                        "  负数的立方根为负：$\\sqrt[3]{-8} = -2$\n"
                        "  0 的立方根是 0\n"
                        "\n"
                        "注意：任何实数都有立方根（包括负数）！\n"
                        "这和平方根不同——负数没有平方根。\n"
                    ),
                },
                {
                    "title": "三、无理数",
                    "content": lit(
                        "无理数：不能写成分数形式的数，小数部分无限不循环\n"
                        "  例：$\\pi$、$\\sqrt{2}$、$\\sqrt{3}$、$0.1010010001\\ldots$\n"
                        "\n"
                        "有理数的判定：\n"
                        "  ✓ 有限小数 → 有理数\n"
                        "  ✓ 无限循环小数 → 有理数\n"
                        "  ✗ 无限不循环小数 → 无理数\n"
                    ),
                },
                {
                    "title": "四、实数的分类与数轴",
                    "content": lit(
                        "实数 = 有理数 + 无理数\n"
                        "\n"
                        "实数与数轴上的点一一对应：\n"
                        "  - 每一个实数都可以在数轴上找到唯一的一个点\n"
                        "  - 数轴上的每一个点都对应唯一的一个实数\n"
                        "\n"
                        "估算：$\\sqrt{2} \\approx 1.414$，$\\sqrt{3} \\approx 1.732$\n"
                        "比较大小：$\\sqrt{5} < \\sqrt{7}$（被开方数越大，平方根越大）\n"
                    ),
                },
            ],
        },
        examples_data=[
            {
                "title": "求算术平方根",
                "problem": '求 $\\sqrt{25}$',
                "steps": [
                    "第 1 步：$5^2 = 25$，$(-5)^2 = 25$",
                    "第 2 步：但算术平方根只取非负的那个",
                    "第 3 步：$\\sqrt{25} = 5$",
                ],
                "answer": "5",
            },
            {
                "title": "求立方根",
                "problem": '求 $\\sqrt[3]{-27}$',
                "steps": [
                    "第 1 步：$(-3)^3 = -27$",
                    "第 2 步：$\\sqrt[3]{-27} = -3$",
                ],
                "answer": "-3",
            },
            {
                "title": "判断有理数",
                "problem": '$\\frac{\\pi}{2}$ 是有理数吗？',
                "steps": [
                    "第 1 步：$\\pi$ 是无理数",
                    "第 2 步：无理数除以 2 还是无理数",
                    "第 3 步：所以 $\\frac{\\pi}{2}$ 不是有理数",
                ],
                "answer": "不是",
            },
        ],
        practice_data=[
            {"id": "rn-prac-001", "stem": '求 $\\sqrt{36}$', "answer": "6", "hints": ["6²=36", "算术平方根取正"]},
            {"id": "rn-prac-002", "stem": '求 $-\\sqrt{16}$', "answer": "-4", "hints": ["先算 √16=4", "前面的负号不动"]},
            {"id": "rn-prac-003", "stem": '求 $\\sqrt[3]{64}$', "answer": "4", "hints": ["4³=64", "立方根和平方根不同"]},
            {"id": "rn-prac-004", "stem": '$\\sqrt{(-3)^2}$ 等于多少？', "answer": "3", "hints": ["先算 (-3)²=9", "再开方 √9=3"]},
            {"id": "rn-prac-005", "stem": "判断：$\\frac{22}{7}$ 是无理数吗？", "answer": "不是，22/7 是分数，所以是有理数", "hints": ["能写成分数形式吗？", "22/7 = 3.142857... 是循环小数"]},
        ],
        test_data=[
            {"id": "rn-test-001", "stem": '求 $\\sqrt{81}$', "answer": "9", "difficulty": 1, "layer": "operation"},
            {"id": "rn-test-002", "stem": '求 $\\pm\\sqrt{49}$', "answer": "±7", "difficulty": 1, "layer": "operation"},
            {"id": "rn-test-003", "stem": '下列哪个是无理数？A: 0  B: 1/3  C: √2  D: 3.14', "answer": "C", "difficulty": 1, "layer": "understand"},
            {"id": "rn-test-004", "stem": '比较大小：$\\sqrt{15}$ 和 4', "answer": "√15 < 4（因为 4²=16 > 15）", "difficulty": 2, "layer": "understand"},
            {"id": "rn-test-005", "stem": '计算 $\\sqrt{16} + \\sqrt[3]{-8}$', "answer": "2", "difficulty": 2, "layer": "operation"},
            {"id": "rn-test-006", "stem": '若 $\\sqrt{a} = 5$，求 $a$', "answer": "a=25", "difficulty": 1, "layer": "operation"},
            {"id": "rn-test-007", "stem": '$\\sqrt{3}$ 介于哪两个连续整数之间？', "answer": "1 和 2 之间", "difficulty": 2, "layer": "understand"},
            {"id": "rn-test-008", "stem": "证明 $\\sqrt{2}$ 不是有理数（提示：用反证法）", "answer": "假设√2=p/q（既约分数），则 2q²=p²，推出 p 和 q 都是偶数，矛盾。", "difficulty": 4, "layer": "connect"},
        ],
        ai_data={
            "topic_summary": "实数是初中数学从有理数到实数的扩展。平方根、立方根是核心运算，无理数的发现打破了'万物皆数'的信念。实数与数轴的一一对应是坐标系的基础，也是函数图像的根基。",
            "key_insights": [
                "负数没有平方根（实数范围内），但有立方根",
                "$\\sqrt{a}$ 表示算术平方根——总是≥0",
                "$\\sqrt{a^2} = |a|$，不是 $a$——这是最常见的陷阱",
                "无理数不是'不讲道理'——是不能写成两个整数的比",
            ],
            "common_mistakes": [
                {
                    "mistake": "$\\sqrt{a^2} = a$",
                    "example": "$\\sqrt{(-3)^2} = -3$",
                    "why": "忽略了算术平方根必须非负",
                    "how_to_explain": "$\\sqrt{(-3)^2} = \\sqrt{9} = 3 = |-3|$。记住：$\\sqrt{a^2} = |a|$。",
                },
                {
                    "mistake": "认为负数有平方根",
                    "example": "$\\sqrt{-4} = -2$（以为(-2)²=4所以回溯）",
                    "why": "把平方根和平方的逆运算搞混了",
                    "how_to_explain": "平方根问的是'谁的平方等于这个数'。什么数的平方等于 -4？没有——因为任何数的平方都≥0。",
                },
                {
                    "mistake": "认为所有带根号的都是无理数",
                    "example": "说 $\\sqrt{4}$ 是无理数",
                    "why": "认为根号=无理数",
                    "how_to_explain": "$\\sqrt{4}=2$ 是整数，是有理数。判断无理数的标准是：能不能写成分数？$\\sqrt{4}$ 就是 $2/1$。",
                },
            ],
            "alternate_explanations": [
                {
                    "method": "正方形面积法",
                    "when_to_use": "解释平方根的含义",
                    "prompt": "一个正方形的面积是 9，边长是多少？3。那如果面积是 2，边长就是 √2——一个在 1.4 和 1.5 之间的数。",
                },
                {
                    "method": "数轴定位法",
                    "when_to_use": "理解无理数在数轴上的位置",
                    "prompt": "在数轴上，√2 可以通过画等腰直角三角形找到：直角边各为1，斜边长√2。把斜边旋转到数轴上，就精确定位了√2。",
                },
            ],
            "question_templates": {
                "difficulty_1_2": "出 2 道直接的平方根/立方根计算题",
                "difficulty_3": "出 1 道实数的分类判断或混合运算题",
                "difficulty_4": "出 1 道需要估算或证明的理解题",
            },
        },
    )


def make_07_coordinate_system():
    """07-coordinate-system: 平面直角坐标系"""
    return make_node(
        slug="coordinate-system", num="07", title="平面直角坐标系", difficulty=1,
        prereqs=["real-numbers"],
        trigger_info={
            "type": "story",
            "title": "笛卡尔：躺在床上看苍蝇的数学家",
            "text": (
                "1619 年，法国数学家笛卡尔生病躺在床上。\n"
                "他盯着天花板，看到一只苍蝇在爬。\n"
                "\n"
                "他突然想：怎么精准描述这只苍蝇的位置呢？\n"
                "如果墙角是原点，可以用离两面墙的距离来表示！\n"
                "\n"
                "这个想法诞生了\"笛卡尔坐标系\"——\n"
                "从此代数和几何被绑在了一起。\n"
                "方程可以画成图像，图像可以用方程描述。\n"
                "\n"
                "一只苍蝇，改变了整个数学史。"
            ),
            "question": "如果要告诉别人你坐在教室的哪个位置，你会怎么说？",
        },
        concept_data={
            "summary": "平面直角坐标系用一对有序实数(x,y)表示点的位置，将几何图形与代数方程联系起来。掌握四个象限的符号特征、对称点坐标规律和坐标距离公式。",
            "sections": [
                {
                    "title": "一、坐标系的结构",
                    "content": lit(
                        "两条互相垂直且有公共原点的数轴组成平面直角坐标系：\n"
                        "  - x 轴（横轴）：水平方向\n"
                        "  - y 轴（纵轴）：垂直方向\n"
                        "  - 原点 $O(0,0)$：两轴交点\n"
                        "\n"
                        "点的坐标：$(x, y)$\n"
                        "  - $x$：横坐标（到 y 轴的有向距离）\n"
                        "  - $y$：纵坐标（到 x 轴的有向距离）\n"
                    ),
                },
                {
                    "title": "二、四个象限",
                    "content": lit(
                        "第一象限：$x>0, y>0$  → $(+, +)$\n"
                        "第二象限：$x<0, y>0$  → $(-, +)$\n"
                        "第三象限：$x<0, y<0$  → $(-, -)$\n"
                        "第四象限：$x>0, y<0$  → $(+, -)$\n"
                        "\n"
                        "坐标轴上的点不属于任何象限：\n"
                        "  x 轴上的点：$(a, 0)$\n"
                        "  y 轴上的点：$(0, b)$\n"
                    ),
                },
                {
                    "title": "三、对称点的坐标规律",
                    "content": lit(
                        "关于 x 轴对称：$(a, b) \\to (a, -b)$（y 变号）\n"
                        "关于 y 轴对称：$(a, b) \\to (-a, b)$（x 变号）\n"
                        "关于原点对称：$(a, b) \\to (-a, -b)$（x、y 都变号）\n"
                    ),
                },
                {
                    "title": "四、坐标距离公式",
                    "content": lit(
                        "两点 $A(x_1, y_1)$ 和 $B(x_2, y_2)$ 的距离：\n"
                        "$$|AB| = \\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$$\n"
                        "\n"
                        "中点坐标：\n"
                        "$$M\\left(\\frac{x_1+x_2}{2}, \\frac{y_1+y_2}{2}\\right)$$\n"
                    ),
                },
            ],
        },
        examples_data=[
            {
                "title": "判断象限",
                "problem": '点 $P(-3, 5)$ 在第几象限？',
                "steps": [
                    "第 1 步：横坐标 $x=-3$（负），纵坐标 $y=5$（正）",
                    "第 2 步：$(-,+)$ → 第二象限",
                ],
                "answer": "第二象限",
            },
            {
                "title": "求对称点",
                "problem": '点 $A(2, -3)$ 关于 y 轴对称的点坐标是什么？',
                "steps": [
                    "第 1 步：关于 y 轴对称，x 变号，y 不变",
                    "第 2 步：$(2, -3) \\to (-2, -3)$",
                ],
                "answer": "(-2, -3)",
            },
            {
                "title": "求两点距离",
                "problem": '求 $A(1, 2)$ 到 $B(4, 6)$ 的距离',
                "steps": [
                    "第 1 步：$d = \\sqrt{(4-1)^2 + (6-2)^2}$",
                    "第 2 步：$d = \\sqrt{9+16} = \\sqrt{25} = 5$",
                ],
                "answer": "5",
            },
        ],
        practice_data=[
            {"id": "cs-prac-001", "stem": "点 $(0, -5)$ 在第几象限？", "answer": "不在任何象限（在 y 轴上）", "hints": ["坐标轴上的点不属于象限", "x=0 的点在 y 轴上"]},
            {"id": "cs-prac-002", "stem": '点 $(2, 3)$ 关于 x 轴对称的点是？', "answer": "(2, -3)", "hints": ["关于 x 轴对称，y 变号", "x 坐标不变"]},
            {"id": "cs-prac-003", "stem": '点 $(-1, 4)$ 和点 $(-1, -4)$ 是关于什么对称？', "answer": "关于 x 轴对称", "hints": ["x 坐标相同", "y 坐标互为相反数"]},
            {"id": "cs-prac-004", "stem": '求点 $A(3, 0)$ 到点 $B(0, 4)$ 的距离', "answer": "5", "hints": ["d² = (0-3)² + (4-0)² = 9+16", "d=5"]},
            {"id": "cs-prac-005", "stem": '若点 $P(x, y)$ 在第三象限，那么 $x$ 和 $y$ 的符号是？', "answer": "x<0, y<0", "hints": ["第三象限：(-,-)", "两个坐标都是负"]},
        ],
        test_data=[
            {"id": "cs-test-001", "stem": "点 $(5, -2)$ 在第几象限？", "answer": "第四象限", "difficulty": 1, "layer": "operation"},
            {"id": "cs-test-002", "stem": '点 $(-3, -4)$ 到 x 轴的距离是多少？', "answer": "4（纵坐标的绝对值）", "difficulty": 1, "layer": "operation"},
            {"id": "cs-test-003", "stem": '点 $(a, b)$ 在第二象限，则 $-a$ 是正还是负？', "answer": "负（因为 a<0，所以 -a>0？等等：a<0 → -a>0，正！）", "difficulty": 2, "layer": "understand"},
            {"id": "cs-test-004", "stem": '已知 $A(1, 2)$ 和 $B(-3, -1)$，求线段 AB 的中点坐标', "answer": "(-1, 0.5)", "difficulty": 2, "layer": "operation"},
            {"id": "cs-test-005", "stem": "点 $(m, n)$ 关于原点对称的点在第几象限？与原来有什么关系？", "answer": "原点对称后变 (-m, -n)，在原来象限的对角象限", "difficulty": 2, "layer": "understand"},
            {"id": "cs-test-006", "stem": '若 $|x|=3$，$|y|=2$，且点在第四象限，写出点坐标', "answer": "(3, -2) 或 (-3, -2)（第四象限x>0,y<0，所以只有(3,-2)）", "difficulty": 3, "layer": "connect"},
            {"id": "cs-test-007", "stem": "求点 $A(1, -3)$ 和 $B(-2, 1)$ 的距离", "answer": "5", "difficulty": 3, "layer": "operation"},
            {"id": "cs-test-008", "stem": "到 x 轴距离为 3，到 y 轴距离为 4 的点有几个？写出所有坐标", "answer": "4个：(4,3), (4,-3), (-4,3), (-4,-3)", "difficulty": 3, "layer": "connect"},
        ],
        ai_data={
            "topic_summary": "平面直角坐标系是数形结合的第一座桥梁。笛卡尔用一只苍蝇的灵感创造了坐标系，从此代数方程可以画成图像，几何图形可以用方程描述。掌握象限判断、对称坐标、距离公式是后续学习函数图像的基础。",
            "key_insights": [
                "坐标系 = 用两个数（坐标）精确定位平面上任意点",
                "四个象限的符号：(+,+) (-,+) (-,-) (+,-)，逆时针数",
                "对称规律：x 对称→y 变号，y 对称→x 变号，原点对称→都变号",
                "距离公式就是勾股定理：横差平方+纵差平方 再开根",
            ],
            "common_mistakes": [
                {
                    "mistake": "混淆点与坐标轴的距离",
                    "example": "说点(3,4)到x轴的距离是3",
                    "why": "分不清哪个坐标对应哪个轴",
                    "how_to_explain": "到x轴的距离=纵坐标的绝对值=|y|。想象你从点垂直往下走到x轴——走的距离由纵坐标决定。",
                },
                {
                    "mistake": "关于原点对称时只变一个坐标",
                    "example": "(2,3)关于原点对称写成(-2,3)或(2,-3)",
                    "why": "和关于坐标轴对称混淆了",
                    "how_to_explain": "关于原点对称 = 同时对x轴和y轴做对称 → 两个坐标都变号。",
                },
                {
                    "mistake": "认为坐标轴上的点属于某个象限",
                    "example": "说(0,3)在第一象限",
                    "why": "没理解象限的定义要求x和y都不为0",
                    "how_to_explain": "象限是四个'房间'，坐标轴是'墙'。站在墙上的点（x=0 或 y=0）不属于任何房间。",
                },
            ],
            "alternate_explanations": [
                {
                    "method": "电影院座位模型",
                    "when_to_use": "让学生直观理解坐标",
                    "prompt": "电影院：排是x，座是y。(3,5)=第3排第5座。直角坐标系？把电影院的地图顺时针转90度，排号向右，座号向上。",
                },
                {
                    "method": "GPS类比法",
                    "when_to_use": "实际应用",
                    "prompt": "你手机的GPS定位本质上就是一个坐标系：经度是x，纬度是y。地球上的任意位置都可以用两个数字描述。",
                },
            ],
            "question_templates": {
                "difficulty_1_2": "出 2 道象限判断或对称点坐标题",
                "difficulty_3": "出 1 道距离/中点/综合坐标题",
                "difficulty_4": "出 1 道需要几何分析或分类讨论的坐标题",
            },
        },
    )


def make_08_linear_systems():
    """08-linear-systems: 二元一次方程组"""
    return make_node(
        slug="linear-systems", num="08", title="二元一次方程组", difficulty=2,
        prereqs=["linear-equation", "polynomials"],
        trigger_info={
            "type": "story",
            "title": "《九章算术》：2000年前的方程智慧",
            "text": (
                "中国古代数学经典《九章算术》（约公元 1 世纪）中，\n"
                "有一章叫\"方程\"——专门讲方程组。\n"
                "\n"
                "古人用算筹（小木棍）排列成矩阵来解方程组：\n"
                "把系数排成行和列，然后像今天的高斯消元法一样消元！\n"
                "\n"
                "这个方法比高斯早了 1800 年。\n"
                "\"方程\"这个词本身就来自《九章算术》——\n"
                "\"方\"是排列，\"程\"是计算。"
            ),
            "question": "如果一个问题里有两个未知数，你需要几个方程才能解出来？",
        },
        concept_data={
            "summary": "二元一次方程组含两个未知数，需要两个方程联立求解。核心方法是代入消元法和加减消元法，本质都是'消元'——把二元转化为已熟悉的一元一次方程。",
            "sections": [
                {
                    "title": "一、什么是二元一次方程组",
                    "content": lit(
                        "二元一次方程：含两个未知数且最高次数为 1\n"
                        "  例：$x + y = 5$\n"
                        "\n"
                        "二元一次方程组：两个二元一次方程联立\n"
                        "  $$\\begin{cases} x + y = 5 \\\\ 2x - y = 1 \\end{cases}$$\n"
                        "\n"
                        "解：同时满足两个方程的 $x$ 和 $y$ 的值\n"
                        "  上面方程组的解是 $(2, 3)$\n"
                    ),
                },
                {
                    "title": "二、代入消元法",
                    "content": lit(
                        "思想：把其中一个未知数用另一个表示，代入另一个方程消元。\n"
                        "\n"
                        "步骤：\n"
                        "1. 从一个方程解出一个未知数（如 $y = 5 - x$）\n"
                        "2. 代入另一个方程（$2x - (5-x) = 1$）\n"
                        "3. 解一元一次方程得 $x$\n"
                        "4. 代回求 $y$\n"
                    ),
                },
                {
                    "title": "三、加减消元法",
                    "content": lit(
                        "思想：通过加减两个方程，消去一个未知数。\n"
                        "\n"
                        "步骤：\n"
                        "1. 使某个未知数的系数互为相反数（需要时乘以适当倍数）\n"
                        "2. 两个方程相加或相减消去该未知数\n"
                        "3. 解一元一次方程\n"
                        "4. 代回求另一个未知数\n"
                        "\n"
                        "例：$\\begin{cases} x+y=5 \\\\ 2x-y=1 \\end{cases}$\n"
                        "两式相加：$3x=6$ → $x=2$ → $y=3$\n"
                    ),
                },
                {
                    "title": "四、应用：鸡兔同笼",
                    "content": lit(
                        "经典问题：鸡兔同笼，共有 35 个头，94 只脚。各有几只？\n"
                        "\n"
                        "设鸡 $x$ 只，兔 $y$ 只，则：\n"
                        "$$\\begin{cases} x + y = 35 \\\\ 2x + 4y = 94 \\end{cases}$$\n"
                        "\n"
                        "解：$x = 23$，$y = 12$（鸡 23 只，兔 12 只）\n"
                    ),
                },
            ],
        },
        examples_data=[
            {
                "title": "代入法",
                "problem": '解 $\\begin{cases} y = 2x \\\\ x + y = 6 \\end{cases}$',
                "steps": [
                    "第 1 步：把 $y=2x$ 代入第二个方程",
                    "第 2 步：$x + 2x = 6$ → $3x = 6$ → $x = 2$",
                    "第 3 步：$y = 2 \\times 2 = 4$",
                    "第 4 步：答案 $\\begin{cases} x=2 \\\\ y=4 \\end{cases}$",
                ],
                "answer": "x=2, y=4",
            },
            {
                "title": "加减法",
                "problem": '解 $\\begin{cases} 2x + y = 7 \\\\ x - y = 2 \\end{cases}$',
                "steps": [
                    "第 1 步：两式相加消去 $y$：$(2x+y)+(x-y)=7+2$",
                    "第 2 步：$3x = 9$ → $x = 3$",
                    "第 3 步：代入 $3-y=2$ → $y = 1$",
                ],
                "answer": "x=3, y=1",
            },
            {
                "title": "需要乘倍数",
                "problem": '解 $\\begin{cases} 3x + 2y = 12 \\\\ 2x - y = 1 \\end{cases}$',
                "steps": [
                    "第 1 步：把第二个方程 ×2：$4x - 2y = 2$",
                    "第 2 步：与第一个方程相加：$(3x+2y)+(4x-2y)=12+2$ → $7x=14$",
                    "第 3 步：$x=2$，代入求 $y=3$",
                ],
                "answer": "x=2, y=3",
            },
        ],
        practice_data=[
            {"id": "ls-prac-001", "stem": '用代入法解 $\\begin{cases} y = 3x \\\\ x + y = 8 \\end{cases}$', "answer": "x=2, y=6", "hints": ["把 y=3x 代入", "x+3x=8"]},
            {"id": "ls-prac-002", "stem": '用加减法解 $\\begin{cases} x + y = 10 \\\\ x - y = 4 \\end{cases}$', "answer": "x=7, y=3", "hints": ["两式相加消去 y", "再相减消去 x？"]},
            {"id": "ls-prac-003", "stem": '解 $\\begin{cases} 2x + y = 5 \\\\ 3x - y = 5 \\end{cases}$', "answer": "x=2, y=1", "hints": ["y的系数互为相反数", "可以直接相加消 y"]},
            {"id": "ls-prac-004", "stem": "鸡兔同笼：头共 10 个，脚共 28 只。各有几只？", "answer": "鸡6只，兔4只", "hints": ["设鸡x兔y", "x+y=10", "2x+4y=28"]},
            {"id": "ls-prac-005", "stem": '如果 $x=1, y=-1$ 是方程 $ax-y=3$ 的解，求 $a$', "answer": "a=2", "hints": ["代入 x=1, y=-1", "a(1)-(-1)=3"]},
        ],
        test_data=[
            {"id": "ls-test-001", "stem": '解 $\\begin{cases} x + y = 3 \\\\ x - y = 1 \\end{cases}$', "answer": "x=2, y=1", "difficulty": 1, "layer": "operation"},
            {"id": "ls-test-002", "stem": '解 $\\begin{cases} 2x + 3y = 12 \\\\ x - y = 1 \\end{cases}$', "answer": "x=3, y=2", "difficulty": 2, "layer": "operation"},
            {"id": "ls-test-003", "stem": '若 $x=2, y=3$ 是解，写出一个二元一次方程组', "answer": "例如：x+y=5, 2x-y=1（不唯一）", "difficulty": 2, "layer": "connect"},
            {"id": "ls-test-004", "stem": '方程组 $\\begin{cases} x + y = 5 \\\\ 2x + 2y = 12 \\end{cases}$ 有解吗？', "answer": "无解（矛盾：第二个化简为x+y=6，但第一个说x+y=5）", "difficulty": 3, "layer": "understand"},
            {"id": "ls-test-005", "stem": '方程组 $\\begin{cases} x + y = 5 \\\\ 2x + 2y = 10 \\end{cases}$ 有几组解？', "answer": "无穷多组（两个方程等价）", "difficulty": 3, "layer": "understand"},
            {"id": "ls-test-006", "stem": "小明买 3 支笔和 2 本笔记本花了 17 元，小华买 1 支笔和 4 本笔记本花了 19 元。求笔和笔记本的单价", "answer": "笔3元，笔记本4元", "difficulty": 3, "layer": "connect"},
            {"id": "ls-test-007", "stem": '解 $\\begin{cases} \\frac{x}{2} + \\frac{y}{3} = 2 \\\\ \\frac{x}{3} - \\frac{y}{4} = \\frac{1}{2} \\end{cases}$（提示：先去分母）', "answer": "x=3, y=3", "difficulty": 3, "layer": "operation"},
            {"id": "ls-test-008", "stem": "请设计一道'年龄问题'并列出方程组", "answer": "例如：父子年龄之和为50，父亲比儿子大28岁。设父x岁，子y岁：x+y=50，x-y=28。", "difficulty": 3, "layer": "connect"},
        ],
        ai_data={
            "topic_summary": "二元一次方程组是方程思想的自然延伸——当一个问题有两个未知数，需要两个方程联立求解。代入法和加减法本质都是'消元'：把一个未知数干掉，转化成已会的一元一次方程。鸡兔同笼是经典应用，背后是数学建模的思维方式。",
            "key_insights": [
                "核心思想：消元 → 把二元变一元",
                "代入法：用表达式替换未知数",
                "加减法：通过加减消去一个未知数",
                "两个未知数需要两个独立方程（不矛盾、不等价）",
            ],
            "common_mistakes": [
                {
                    "mistake": "加减法时忘记乘遍整个方程",
                    "example": "把 $2x-y=1$ 乘以 2 写成 $4x-y=2$（y的系数没乘）",
                    "why": "只乘了一部分",
                    "how_to_explain": "等式两边同乘一个数，每一项都要乘！就像每个人都要领工资，不能漏掉。",
                },
                {
                    "mistake": "代入时符号错误",
                    "example": "把 $y=5-x$ 代入 $2x-y=1$ 写成 $2x-5-x=1$（没有加括号）",
                    "why": "负号-作用于整个表达式，应该先加括号",
                    "how_to_explain": "代入 $y=5-x$ 时，$2x-y$ 变成 $2x-(5-x) = 2x-5+x$。注意括号！",
                },
                {
                    "mistake": "忘记检验",
                    "example": "解出 x=3, y=2 就直接交卷，不代回验证",
                    "why": "急于求成",
                    "how_to_explain": "花10秒钟把答案代回原方程检验，能避免50%的错误。把检验当成习惯。",
                },
            ],
            "alternate_explanations": [
                {
                    "method": "买菜模型",
                    "when_to_use": "理解方程组的意义",
                    "prompt": "如果苹果 x 元/斤，香蕉 y 元/斤。小明买不同组合花了不同的钱——这就产生了两个方程。解方程组就是通过两次购买信息反推单价。",
                },
                {
                    "method": "图像法",
                    "when_to_use": "理解方程组解的意义",
                    "prompt": "每个二元一次方程都是一条直线。方程组的解 = 两条直线的交点坐标。无解 = 两条平行线，无穷多解 = 两条重合的线。",
                },
            ],
            "question_templates": {
                "difficulty_1_2": "出 2 道直接用代入法或加减法解方程组的题",
                "difficulty_3": "出 1 道应用题，需要先建立方程组再求解",
                "difficulty_4": "出 1 道含参数的方程组讨论题",
            },
        },
    )


def make_09_inequalities():
    """09-inequalities: 不等式与不等式组"""
    return make_node(
        slug="inequalities", num="09", title="不等式与不等式组", difficulty=2,
        prereqs=["linear-equation"],
        trigger_info={
            "type": "story",
            "title": "不等式：大于、小于 = 生活中的大多数决策",
            "text": (
                "方程问的是\"等于多少\"——$x=3$。\n"
                "不等式问的是\"至少/最多/在什么范围内\"。\n"
                "\n"
                "仔细想想：你生活中的决策有多少是需要\"等于\"的？\n"
                "很少。大多数时候你在想：\n"
                "\"我至少需要存多少钱？\"\n"
                "\"体重不能超过多少？\"\n"
                "\"每天最多花多少时间玩手机？\"\n"
                "\n"
                "不等式比方程更贴近真实世界——\n"
                "因为现实中很少有精确等于，更多的是范围和约束。"
            ),
            "question": "你今天的决策中，哪些可以用不等式来描述？",
        },
        concept_data={
            "summary": "不等式用不等号（<、>、≤、≥）表示数量关系，解法和方程类似但乘除负数时方向要反转。不等式组求各不等式解集的公共部分（交集），常用数轴表示解集。",
            "sections": [
                {
                    "title": "一、不等式的概念",
                    "content": lit(
                        "不等号：$<$（小于）、$>$（大于）、$\\leq$（小于等于）、$\\geq$（大于等于）\n"
                        "\n"
                        "不等式的基本性质：\n"
                        "1. 两边同加减同一个数，不等号方向不变\n"
                        "   $a>b$ → $a+c > b+c$\n"
                        "2. 两边同乘除同一个正数，不等号方向不变\n"
                        "   $a>b$ 且 $c>0$ → $ac > bc$\n"
                        "3. 两边同乘除同一个负数，不等号方向要反转！\n"
                        "   $a>b$ 且 $c<0$ → $ac < bc$"
                    ),
                },
                {
                    "title": "二、解不等式",
                    "content": lit(
                        "解法与一元一次方程类似，但注意性质 3！\n"
                        "\n"
                        "例：解 $3x+2 > 8$\n"
                        "  移项：$3x > 8-2$ → $3x > 6$\n"
                        "  系数化 1：$x > 2$（除以正数 3，方向不变）\n"
                        "\n"
                        "例：解 $-2x \\leq 6$\n"
                        "  系数化 1：$x \\geq -3$（除以负数 -2，方向反转！）\n"
                        "\n"
                        "解集表示：\n"
                        "  - 不等式：$x > 2$\n"
                        "  - 数轴：从 2 向右画射线，空心圈（不含 2）\n"
                    ),
                },
                {
                    "title": "三、不等式组",
                    "content": lit(
                        "不等式组：几个不等式联立，求同时满足所有不等式的解\n"
                        "\n"
                        "解法：\n"
                        "1. 分别解每个不等式\n"
                        "2. 在数轴上标出各解集\n"
                        "3. 求公共部分（交集）\n"
                        "\n"
                        "例：$\\begin{cases} x > 2 \\\\ x \\leq 5 \\end{cases}$\n"
                        "  解集：$2 < x \\leq 5$\n"
                    ),
                },
                {
                    "title": "四、应用问题",
                    "content": lit(
                        "常见关键词转化：\n"
                        "  \"至少\"/\"不少于\" → $\\geq$\n"
                        "  \"最多\"/\"不超过\" → $\\leq$\n"
                        "  \"超过\"/\"大于\" → $>$\n"
                        "  \"不足\"/\"小于\" → $<$\n"
                        "\n"
                        "列不等式步骤：\n"
                        "  设未知数 → 找不等关系 → 列不等式 → 求解 → 验证实际意义\n"
                    ),
                },
            ],
        },
        examples_data=[
            {
                "title": "解不等式",
                "problem": '解 $2x - 3 > 5$',
                "steps": [
                    "第 1 步：移项：$2x > 5 + 3 = 8$",
                    "第 2 步：$x > 4$",
                ],
                "answer": "x>4",
            },
            {
                "title": "乘除负数反转方向",
                "problem": '解 $-3x \\geq 9$',
                "steps": [
                    "第 1 步：两边同除以 $-3$（负数）",
                    "第 2 步：不等号方向反转！$x \\leq -3$",
                ],
                "answer": "x≤-3",
            },
            {
                "title": "不等式组",
                "problem": '解 $\\begin{cases} x+1 > 3 \\\\ 2x-1 \\leq 7 \\end{cases}$',
                "steps": [
                    "第 1 步：第一个不等式：$x > 2$",
                    "第 2 步：第二个不等式：$2x \\leq 8$ → $x \\leq 4$",
                    "第 3 步：取交集：$2 < x \\leq 4$",
                ],
                "answer": "2<x≤4",
            },
        ],
        practice_data=[
            {"id": "ineq-prac-001", "stem": '解 $x + 5 > 10$', "answer": "x>5", "hints": ["移项", "不等式方向不变"]},
            {"id": "ineq-prac-002", "stem": '解 $-x < 3$', "answer": "x>-3", "hints": ["两边同乘-1", "方向要反转"]},
            {"id": "ineq-prac-003", "stem": '解 $2x \\leq 6$', "answer": "x≤3", "hints": ["两边同除以2", "正数，方向不变"]},
            {"id": "ineq-prac-004", "stem": '解不等式组 $\\begin{cases} x > 1 \\\\ x < 3 \\end{cases}$', "answer": "1<x<3", "hints": ["分别解", "取交集"]},
            {"id": "ineq-prac-005", "stem": '某个数的 2 倍加 3 不超过 11，求这个数的范围', "answer": "x≤4", "hints": ["不超过→≤", "2x+3≤11"]},
        ],
        test_data=[
            {"id": "ineq-test-001", "stem": '解 $3x - 1 < 5$', "answer": "x<2", "difficulty": 1, "layer": "operation"},
            {"id": "ineq-test-002", "stem": '解 $-2x + 1 \\geq 5$', "answer": "x≤-2", "difficulty": 2, "layer": "operation"},
            {"id": "ineq-test-003", "stem": '解 $\\frac{x}{2} - 1 > 0$', "answer": "x>2", "difficulty": 1, "layer": "operation"},
            {"id": "ineq-test-004", "stem": '解不等式组 $\\begin{cases} 2x - 1 > 3 \\\\ x + 2 < 8 \\end{cases}$', "answer": "2<x<6", "difficulty": 2, "layer": "operation"},
            {"id": "ineq-test-005", "stem": "若 $a<b$，比较 $-3a$ 和 $-3b$ 的大小", "answer": "-3a > -3b（两边乘负数，不等号反转）", "difficulty": 2, "layer": "understand"},
            {"id": "ineq-test-006", "stem": "一个两位数，十位数字比个位数字小 2。如果这个数大于 20 小于 40，求这个数", "answer": "35（十位3个位5）", "difficulty": 3, "layer": "connect"},
            {"id": "ineq-test-007", "stem": "小明有 50 元，买一本 15 元的书后，剩下的钱买每支 3 元的笔，最多能买几支？", "answer": "11支（50-15=35，35÷3=11.67...，最多11支）", "difficulty": 3, "layer": "connect"},
            {"id": "ineq-test-008", "stem": '若不等式组 $\\begin{cases} x > a \\\\ x < 3 \\end{cases}$ 有解，求 $a$ 的取值范围', "answer": "a<3", "difficulty": 3, "layer": "connect"},
        ],
        ai_data={
            "topic_summary": "不等式是方程思想的扩展——从'等于'拓展到'大于/小于/范围'。核心陷阱：乘除负数时不等号方向要反转。不等式组通过数轴求交集，是高中线性规划的基础。不等式也是真实世界最常见的数学工具——约束条件、范围估计、最优化都离不开它。",
            "key_insights": [
                "乘除负数要反转不等号——这是不等式和方程最大的区别",
                "不等式组的解 = 各个不等式解集的交集（数轴上重叠部分）",
                "\"至少\"→≥，\"最多\"→≤，\"超过\"→>，\"不足\"→<",
                "数轴是表示不等式解集最直观的工具：实心圈=包含端点，空心圈=不包含",
            ],
            "common_mistakes": [
                {
                    "mistake": "乘除负数忘记反转不等号",
                    "example": "$-2x > 6$ → $x > -3$",
                    "why": "习惯了方程的做法，忘记不等式的特殊规则",
                    "how_to_explain": "用具体数字验证：x=2 满足 -2x>6 吗？-4>6？不对！x=-4 呢？8>6 ✓。所以 x<-3，方向确实要反转。",
                },
                {
                    "mistake": "不等式组只取到一个不等式的解",
                    "example": "解出 x>2 就说解完了，忘了还要 x<5",
                    "why": "没意识到要同时满足",
                    "how_to_explain": "不等式组 = 多个条件要同时满足。你在数轴上画两个解集，取它们重叠的部分。",
                },
                {
                    "mistake": "混淆开区间和闭区间",
                    "example": "x>2 在数轴上画实心圈",
                    "why": "不清楚≥和>的区别",
                    "how_to_explain": "> 不包含该值 → 空心圈。≥ 包含该值 → 实心圈。≥ = > 包含 = 有等号。",
                },
            ],
            "alternate_explanations": [
                {
                    "method": "天平倾斜法",
                    "when_to_use": "理解不等式的基本性质",
                    "prompt": "天平左边重，右边轻。两边同时加相同的砝码——左边还是重。但同时乘以负数？相当于把左右交换了——轻的变重，重的变轻，不等号方向自然反转。",
                },
                {
                    "method": "数轴直观法",
                    "when_to_use": "表示解集和求交集",
                    "prompt": "把每个不等式的解集在数轴上用颜色标出。不等组就是要求两种颜色重叠的区域——画出来一目了然。",
                },
            ],
            "question_templates": {
                "difficulty_1_2": "出 2 道直接解不等式（注意乘除负数）的题",
                "difficulty_3": "出 1 道不等式组求解或应用题",
                "difficulty_4": "出 1 道含参数的不等式组讨论题",
            },
        },
    )


def make_10_data_collection():
    """10-data-collection: 数据收集整理"""
    return make_node(
        slug="data-collection", num="10", title="数据收集整理", difficulty=1,
        prereqs=["rational-numbers"],
        trigger_info={
            "type": "story",
            "title": "南丁格尔：用统计图拯救生命的护士",
            "text": (
                "1854 年克里米亚战争期间，英国护士南丁格尔发现：\n"
                "战地医院死亡的士兵中，只有一小部分死于战伤，\n"
                "绝大多数死于可以预防的感染疾病。\n"
                "\n"
                "她收集数据、制作统计图——创造性地使用了极坐标面积图（\"玫瑰图\"），\n"
                "向军方高层展示：改善卫生条件可以大幅降低死亡率。\n"
                "\n"
                "她成功了。伤亡率从 42% 降到 2%。\n"
                "一位护士用数据做了将军们做不到的事。\n"
                "数据不是冰冷的数字——是可以救命的力量。"
            ),
            "question": "你最近有没有根据数据做出过什么决策？比如根据天气数据决定穿什么？",
        },
        concept_data={
            "summary": "数据收集整理学习如何收集、整理和展示数据。掌握普查vs抽样调查、条形图/扇形图（饼图）/折线图/直方图的特点和适用场景，以及频数、频率的计算。",
            "sections": [
                {
                    "title": "一、数据的收集",
                    "content": lit(
                        "数据的来源：\n"
                        "  - 直接收集：观察、测量、调查、实验\n"
                        "  - 间接收集：查阅资料、网络搜索\n"
                        "\n"
                        "调查方式：\n"
                        "  - 普查：调查全体对象\n"
                        "    优点：准确；缺点：费时费力\n"
                        "  - 抽样调查：调查部分对象推断整体\n"
                        "    优点：省时省力；缺点：可能有误差\n"
                    ),
                },
                {
                    "title": "二、数据的整理",
                    "content": lit(
                        "频数：每个数据出现的次数\n"
                        "频率：频数 ÷ 数据总数（$0 \\leq f \\leq 1$）\n"
                        "\n"
                        "统计表：把数据按类别整理成表格\n"
                        "  标题 + 表头 + 数据行\n"
                        "\n"
                        "分组：当数据量大时，把数据分成若干组\n"
                        "  组距 = 每组的数据范围\n"
                    ),
                },
                {
                    "title": "三、统计图的选择",
                    "content": lit(
                        "条形图：比较不同类别的数量大小\n"
                        "  → 适合比较：各班成绩、各月销量\n"
                        "\n"
                        "折线图：展示数据的变化趋势\n"
                        "  → 适合看变化：气温变化、成绩趋势\n"
                        "\n"
                        "扇形图（饼图）：展示各部分占总体的百分比\n"
                        "  → 适合看比例：预算分配、成分比例\n"
                        "\n"
                        "直方图：展示连续数据的分布情况\n"
                        "  → 适合看分布：身高分布、成绩分布\n"
                    ),
                },
                {
                    "title": "四、读图和用图",
                    "content": lit(
                        "读图三要素：标题、坐标轴标签、数据来源\n"
                        "\n"
                        "扇形图中：\n"
                        "  圆心角 = 百分比 × 360°\n"
                        "  如：25% → 圆心角 = 0.25 × 360° = 90°\n"
                        "\n"
                        "避免误导：\n"
                        "  - 注意坐标轴是否从 0 开始\n"
                        "  - 注意比例尺是否均匀\n"
                    ),
                },
            ],
        },
        examples_data=[
            {
                "title": "计算频率",
                "problem": "50 个学生中，12 人喜欢篮球。求喜欢篮球的频率",
                "steps": [
                    "第 1 步：频率 = 频数 ÷ 总数",
                    "第 2 步：$12 ÷ 50 = 0.24$",
                ],
                "answer": "0.24",
            },
            {
                "title": "选择统计图",
                "problem": "展示某城市 2018-2023 年人口变化，用什么图最合适？",
                "steps": [
                    "第 1 步：需要看变化趋势",
                    "第 2 步：折线图最适合展示趋势",
                ],
                "answer": "折线图",
            },
            {
                "title": "扇形图计算",
                "problem": "某数据占总体的 30%，在扇形图中圆心角是多少？",
                "steps": [
                    "第 1 步：圆心角 = 百分比 × 360°",
                    "第 2 步：$30\\% × 360° = 108°$",
                ],
                "answer": "108°",
            },
        ],
        practice_data=[
            {"id": "dc-prac-001", "stem": "20 人中有 5 人戴眼镜，频率是多少？", "answer": "0.25", "hints": ["频数÷总数", "5÷20"]},
            {"id": "dc-prac-002", "stem": "比较各班平均分，最适合用什么统计图？", "answer": "条形图", "hints": ["需要比较不同类别的数值", "条形图侧向比较"]},
            {"id": "dc-prac-003", "stem": "普查和抽样调查各有什么优缺点？", "answer": "普查准确但费时，抽样省时但有误差", "hints": ["想想人口普查为什么10年才做一次", "日常调查用什么方式"]},
            {"id": "dc-prac-004", "stem": "扇形图中 25% 的圆心角是多少度？", "answer": "90°", "hints": ["360° × 25%", "360×0.25=90"]},
            {"id": "dc-prac-005", "stem": "展示一周气温变化，用什么图最合适？", "answer": "折线图", "hints": ["要看变化趋势", "折线图表现趋势"]},
        ],
        test_data=[
            {"id": "dc-test-001", "stem": "某班 40 人中，喜欢数学的 16 人，求频率", "answer": "0.4", "difficulty": 1, "layer": "operation"},
            {"id": "dc-test-002", "stem": "下列哪个适合用全面调查（普查）？A:灯泡寿命  B:全国人口  C:全班身高  D:河水污染", "answer": "C", "difficulty": 1, "layer": "understand"},
            {"id": "dc-test-003", "stem": "扇形图中，表示 40% 的扇形的圆心角是？", "answer": "144°", "difficulty": 1, "layer": "operation"},
            {"id": "dc-test-004", "stem": "以下是某班同学成绩分组：60-70分10人，70-80分15人，80-90分12人，90-100分3人。总人数？", "answer": "40人", "difficulty": 1, "layer": "operation"},
            {"id": "dc-test-005", "stem": "如果想展示各部分占整体的比例，应选什么统计图？A:条形图  B:折线图  C:扇形图  D:直方图", "answer": "C", "difficulty": 1, "layer": "understand"},
            {"id": "dc-test-006", "stem": "某样本中 A 的频率为 0.3，B 的频率为 0.5，其余为 C。求 C 的频率", "answer": "0.2", "difficulty": 2, "layer": "operation"},
            {"id": "dc-test-007", "stem": "小明调查了 200 人最喜欢的水果：苹果 60 人，香蕉 50 人，橘子 40 人，其他 50 人。在扇形图中，苹果对应的圆心角是多少？", "answer": "108°", "difficulty": 2, "layer": "connect"},
            {"id": "dc-test-008", "stem": "设计一个调查方案：调查全校学生每天使用手机的时间（写出：调查方式、样本量、统计图选择）", "answer": "抽样调查，随机抽100人，用直方图展示时间分布", "difficulty": 3, "layer": "connect"},
        ],
        ai_data={
            "topic_summary": "数据收集整理是统计的基础。学会区分普查和抽样调查，根据目的选择合适的统计图（条形→比较、折线→趋势、扇形→比例、直方→分布），掌握频数/频率计算和扇形圆心角换算。这是用数据说话的第一课。",
            "key_insights": [
                "普查=全查（准确但费时），抽样=抽查（省时但有误差）",
                "四种统计图各有擅长：比大小用条形，看趋势用折线，看比例用扇形，看分布用直方",
                "频率=频数/总数，所有频率之和=1",
                "扇形圆心角=百分比×360°",
            ],
            "common_mistakes": [
                {
                    "mistake": "混淆条形图和直方图",
                    "example": "把身高分布画成条形图",
                    "why": "条形图柱间有间距，直方柱间无间距",
                    "how_to_explain": "条形图比较不同类别（离散的），柱间有空隙。直方图展示连续数据分布，柱紧挨着。身高是连续数据，用直方图。",
                },
                {
                    "mistake": "频率加起来超过 1",
                    "example": "数出各频率：0.3+0.4+0.3+0.2 = 1.2",
                    "why": "重复计数或计算错误",
                    "how_to_explain": "所有频率之和必须等于 1（100%）。如果超过 1，一定有人被数了两次。",
                },
                {
                    "mistake": "扇形圆心角算错",
                    "example": "30% → 30°",
                    "why": "忘记 100% 对应 360°",
                    "how_to_explain": "1% → 3.6°，30% → 30×3.6=108°，不是 30°。",
                },
            ],
            "alternate_explanations": [
                {
                    "method": "食堂选菜类比",
                    "when_to_use": "理解四种统计图的用途",
                    "prompt": "条形图='今天每个菜卖了多少份'（比多少）；折线图='这一周糖醋排骨的销量变化'（看趋势）；扇形图='每种菜占总销量的比例'（看比例）；直方图='学生饭卡消费金额的分布'（看分布）。",
                },
            ],
            "question_templates": {
                "difficulty_1_2": "出 2 道频数/频率计算和统计图选择题",
                "difficulty_3": "出 1 道扇形图圆心角计算或读图分析题",
                "difficulty_4": "出 1 道需要设计调查方案的综合题",
            },
        },
    )


def make_11_triangle_basics():
    """11-triangle-basics: 三角形（八年级上）"""
    return make_node(
        slug="triangle-basics", num="11", title="三角形", difficulty=2,
        prereqs=["geometry-basics", "parallel-lines"],
        trigger_info={
            "type": "story",
            "title": "三角形：最稳定的结构",
            "text": (
                "为什么自行车架、屋顶桁架、埃菲尔铁塔都大量使用三角形？\n"
                "因为三角形是唯一不会变形的基本多边形。\n"
                "\n"
                "四边形的框架可以被压扁（试试看），\n"
                "但三角形的三条边一旦确定，三个角也就被锁死。\n"
                "这就是\"三角形的稳定性\"——工程学的基石。\n"
                "\n"
                "几何学中，三角形也是最重要的基本图形：\n"
                "任何多边形都可以分割成若干个三角形。\n"
                "掌握了三角形，你就掌握了几何的钥匙。"
            ),
            "question": "观察一下你的周围，能找到几个三角形的结构？",
        },
        concept_data={
            "summary": "三角形是初中几何的核心图形。学习三角形的分类、三边关系（两边之和大于第三边）、内角和为180°、以及高/中线/角平分线等主要线段。",
            "sections": [
                {
                    "title": "一、三角形的分类",
                    "content": lit(
                        "按角分类：\n"
                        "  - 锐角三角形：三个角都是锐角（<90°）\n"
                        "  - 直角三角形：有一个角是 90°\n"
                        "  - 钝角三角形：有一个角是钝角（>90°）\n"
                        "\n"
                        "按边分类：\n"
                        "  - 不等边三角形：三边都不相等\n"
                        "  - 等腰三角形：有两条边相等\n"
                        "  - 等边三角形：三边都相等（特殊的等腰三角形）\n"
                    ),
                },
                {
                    "title": "二、三角形的三边关系",
                    "content": lit(
                        "三角形任意两边之和大于第三边：\n"
                        "  $a + b > c$，$b + c > a$，$a + c > b$\n"
                        "\n"
                        "三角形任意两边之差小于第三边：\n"
                        "  $|a - b| < c$\n"
                        "\n"
                        "判断三条线段能否构成三角形：\n"
                        "  只需检查：最短两边之和 > 最长边\n"
                        "\n"
                        "例：3, 4, 5 → 3+4=7>5 ✓（能构成三角形）\n"
                        "例：2, 3, 6 → 2+3=5<6 ✗（不能构成三角形）\n"
                    ),
                },
                {
                    "title": "三、三角形内角和",
                    "content": lit(
                        "三角形三个内角之和 = 180°\n"
                        "$\\angle A + \\angle B + \\angle C = 180°$\n"
                        "\n"
                        "推论：\n"
                        "  - 直角三角形两锐角互余（和为 90°）\n"
                        "  - 一个三角形最多有一个直角或钝角\n"
                        "\n"
                        "外角 = 与它不相邻的两个内角之和：\n"
                        "  $\\angle ACD = \\angle A + \\angle B$\n"
                    ),
                },
                {
                    "title": "四、三角形的主要线段",
                    "content": lit(
                        "高：从顶点向对边（或延长线）作垂线段\n"
                        "中线：顶点到对边中点的连线\n"
                        "角平分线：平分内角且与对边相交的线段\n"
                        "\n"
                        "等腰三角形的性质：\n"
                        "  - 两底角相等\n"
                        "  - 顶角的平分线、底边上的中线和高\"三线合一\"\n"
                    ),
                },
            ],
        },
        examples_data=[
            {
                "title": "判断能否构成三角形",
                "problem": "三段长度 4, 7, 10 能否构成三角形？",
                "steps": [
                    "第 1 步：最短两边：4+7=11",
                    "第 2 步：最长边：10",
                    "第 3 步：11>10 → 能构成三角形",
                ],
                "answer": "能",
            },
            {
                "title": "求角度",
                "problem": '已知三角形两个角分别为 50° 和 60°，求第三个角',
                "steps": [
                    "第 1 步：内角和 = 180°",
                    "第 2 步：$180° - 50° - 60° = 70°$",
                ],
                "answer": "70°",
            },
            {
                "title": "外角定理",
                "problem": '三角形中 $\\angle A = 40°$，$\\angle B = 60°$，求 $\\angle C$ 处的外角',
                "steps": [
                    "第 1 步：$\\angle C = 180°-40°-60° = 80°$",
                    "第 2 步：外角 $= 180° - 80° = 100°$",
                    "或直接用外角定理：外角 = 不相邻两内角之和 = 40°+60°=100°",
                ],
                "answer": "100°",
            },
        ],
        practice_data=[
            {"id": "tri-prac-001", "stem": "三段长度 2, 3, 6 能构成三角形吗？", "answer": "不能（2+3=5<6）", "hints": ["检查：最短两边之和 > 最长边？", "2+3=5，和 6 比较"]},
            {"id": "tri-prac-002", "stem": '三角形两角分别为 45° 和 45°，求第三个角，这是什么三角形？', "answer": "90°，直角三角形", "hints": ["180°-45°-45°", "有一个角是90°"]},
            {"id": "tri-prac-003", "stem": "一个三角形最多有几个钝角？", "answer": "1 个", "hints": ["钝角>90°", "两个钝角和>180°"]},
            {"id": "tri-prac-004", "stem": '等腰三角形的一个底角是 40°，求顶角', "answer": "100°", "hints": ["两底角相等=40°", "180°-40°-40°"]},
            {"id": "tri-prac-005", "stem": '若三角形两边分别为 5 和 8，第三边可能是？A:2  B:3  C:6  D:15', "answer": "C", "hints": ["第三边必须满足：|8-5|<c<8+5", "即 3<c<13"]},
        ],
        test_data=[
            {"id": "tri-test-001", "stem": "判断 6, 8, 13 能否构成三角形", "answer": "能（6+8=14>13）", "difficulty": 1, "layer": "operation"},
            {"id": "tri-test-002", "stem": '已知 $\\angle A = 30°$，$\\angle B = 70°$，求 $\\angle C$', "answer": "80°", "difficulty": 1, "layer": "operation"},
            {"id": "tri-test-003", "stem": "等腰三角形顶角 120°，求底角", "answer": "30°（(180-120)/2=30）", "difficulty": 2, "layer": "operation"},
            {"id": "tri-test-004", "stem": "下列哪组能构成三角形？A:1,2,3  B:2,3,4  C:1,2,4  D:3,3,7", "answer": "B", "difficulty": 1, "layer": "understand"},
            {"id": "tri-test-005", "stem": "三角形的一个外角为 120°，与它相邻的内角是多少度？", "answer": "60°（相邻内外角互补）", "difficulty": 2, "layer": "operation"},
            {"id": "tri-test-006", "stem": "若三角形两边分别为 3 和 9，且第三边为奇数，求第三边可能的值", "answer": "7, 9, 11（需满足 6<c<12 且为奇数）", "difficulty": 3, "layer": "connect"},
            {"id": "tri-test-007", "stem": "证明：三角形三个外角之和 = 360°", "answer": "每个外角=180°-对应内角，三个外角和=540°-180°=360°", "difficulty": 3, "layer": "connect"},
            {"id": "tri-test-008", "stem": "一个三角形的三个内角的比为 2:3:4，求三个角各是多少度", "answer": "40°, 60°, 80°", "difficulty": 3, "layer": "connect"},
        ],
        ai_data={
            "topic_summary": "三角形是几何学的核心图形。三边关系（两边之和>第三边）是判定三条线段能否构成三角形的依据。内角和180°是最重要的角度定理。理解高、中线、角平分线是为后续全等三角形、勾股定理等内容做准备。",
            "key_insights": [
                "三边关系：最短两边之和 > 最长边 → 能构成三角形",
                "内角和 = 180° 是最基础的角度关系",
                "外角 = 不相邻两内角之和（外角定理）",
                "三角形是最稳定的结构——工程学广泛应用",
            ],
            "common_mistakes": [
                {
                    "mistake": "判断三边关系时忽略'任意'两个字",
                    "example": "3, 5, 9：说 3+5=8<9, 不能构成三角形（这个判断对了），但 3, 5, 7：3+5=8>7, 就认为可以（实际可以），但只检查了一组",
                    "why": "只检查了最大边和另外两边之和",
                    "how_to_explain": "其实只需要检查最短两边之和是否大于最长边就够了。因为如果最短两边之和>最长边，另外两组自动满足。",
                },
                {
                    "mistake": "内角和外角混淆",
                    "example": "外角=180°-相邻内角（对），但不等于不相邻两内角之和（这个规则忘了用）",
                    "why": "把补角和外角搞混了",
                    "how_to_explain": "外角是延长三角形的一边形成的角。外角 = 不相邻的两个内角之和（因为三个内角和180°，外角+相邻内角=180°）。",
                },
                {
                    "mistake": "等腰三角形漏考虑",
                    "example": "已知三角形两角都是50°，求第三角 → 写 80°没错，但没说这是什么三角形",
                    "why": "不会通过角的关系判断三角形类型",
                    "how_to_explain": "两角相等（50°=50°）→ 两边相等 → 等腰三角形。一个角=90°→直角三角形。",
                },
            ],
            "alternate_explanations": [
                {
                    "method": "撕角拼图法",
                    "when_to_use": "证明内角和=180°",
                    "prompt": "拿一个纸质三角形，把三个角撕下来，拼在一起——你会发现它们正好构成一个平角（180°）。",
                },
                {
                    "method": "建筑三角形法",
                    "when_to_use": "理解三角形的稳定性",
                    "prompt": "用吸管和绳做一个三角形和一个四边形框架。四边形一推就变形，三角形纹丝不动。这就是为什么桥梁必须是三角形的。",
                },
            ],
            "question_templates": {
                "difficulty_1_2": "出 2 道三边关系判断和角度计算题",
                "difficulty_3": "出 1 道综合角度计算和三角形分类题",
                "difficulty_4": "出 1 道几何证明或开放推理题",
            },
        },
    )


def make_12_congruent_triangles():
    """12-congruent-triangles: 全等三角形"""
    return make_node(
        slug="congruent-triangles", num="12", title="全等三角形", difficulty=3,
        prereqs=["triangle-basics"],
        trigger_info={
            "type": "story",
            "title": "全等：证明两个图形完全相同的唯一标准",
            "text": (
                "如果你要复制一个三角形——不需要量所有6个要素（3条边+3个角）。\n"
                "只要知道其中3个就可以完全确定它！\n"
                "\n"
                "这就是全等三角形的判定定理：\n"
                "SSS、SAS、ASA、AAS、HL（直角三角形）。\n"
                "\n"
                "为什么是3个？因为三角形的3个自由度（形状+大小）\n"
                "正好需要3个约束条件来唯一确定。\n"
                "这个思想——用最短的信息量唯一确定一个对象——\n"
                "是现代信息论和数据压缩的雏形。"
            ),
            "question": "给你一个三角形，你最少需要量几个要素（边或角）才能复制出一个一模一样的？",
        },
        concept_data={
            "summary": "全等三角形是几何证明的核心工具。两个三角形全等意味着形状和大小完全相同。5个判定定理（SSS/SAS/ASA/AAS/HL）是证明边角相等的主要手段。",
            "sections": [
                {
                    "title": "一、什么是全等",
                    "content": lit(
                        "全等：两个图形完全重合（形状相同，大小相同）\n"
                        "  记作：$\\triangle ABC \\cong \\triangle DEF$\n"
                        "\n"
                        "全等三角形的性质：\n"
                        "  - 对应边相等：$AB = DE$，$BC = EF$，$AC = DF$\n"
                        "  - 对应角相等：$\\angle A = \\angle D$，$\\angle B = \\angle E$，$\\angle C = \\angle F$\n"
                        "\n"
                        "注意：全等符号 $\\cong$ 中，对应顶点必须对应写！\n"
                    ),
                },
                {
                    "title": "二、判定定理（5个）",
                    "content": lit(
                        "SSS（边边边）：三边分别相等 → 全等\n"
                        "  \"三条边都确定了，三角形就唯一了\"\n"
                        "\n"
                        "SAS（边角边）：两边及其夹角分别相等 → 全等\n"
                        "  \"注意：必须是夹角！两边和不是夹角的角不够\"\n"
                        "\n"
                        "ASA（角边角）：两角及其夹边分别相等 → 全等\n"
                        "\n"
                        "AAS（角角边）：两角及其中一角的对边分别相等 → 全等\n"
                        "\n"
                        "HL（斜边-直角边）：只适用于直角三角形\n"
                        "  斜边和一条直角边分别相等 → 全等\n"
                    ),
                },
                {
                    "title": "三、用全等做证明",
                    "content": lit(
                        "证明边相等：先证三角形全等 → 对应边相等\n"
                        "证明角相等：先证三角形全等 → 对应角相等\n"
                        "\n"
                        "证明步骤模板：\n"
                        "1. 观察图形，找到可能全等的两个三角形\n"
                        "2. 找出三个相等条件\n"
                        "3. 写出判定定理\n"
                        "4. 由全等推出要证的结论\n"
                    ),
                },
                {
                    "title": "四、常见辅助线",
                    "content": lit(
                        "连接两点 → 产生公共边\n"
                        "作高 → 产生直角\n"
                        "作中线 → 产生相等线段\n"
                        "延长线 → 创造更多已知条件\n"
                        "\n"
                        "辅助线的艺术：把分散的条件聚到两个三角形中\n"
                    ),
                },
            ],
        },
        examples_data=[
            {
                "title": "SSS判定",
                "problem": '已知 $AB=DE=3$，$BC=EF=4$，$AC=DF=5$，判断是否全等',
                "steps": [
                    "第 1 步：三组边分别相等",
                    "第 2 步：SSS → $\\triangle ABC \\cong \\triangle DEF$",
                ],
                "answer": "全等（SSS）",
            },
            {
                "title": "公共边技巧",
                "problem": '$AB=CD$，$AD=BC$，求证 $\\triangle ABD \\cong \\triangle CDB$',
                "steps": [
                    "第 1 步：$AB=CD$（已知）",
                    "第 2 步：$AD=BC$（已知）",
                    "第 3 步：$BD$ 是公共边（$BD=BD$）",
                    "第 4 步：SSS → 全等",
                ],
                "answer": "SSS判定全等",
            },
            {
                "title": "HL判定",
                "problem": '$\\triangle ABC$ 和 $\\triangle DEF$ 都是直角三角形，$\\angle B=\\angle E=90°$，$AC=DF=10$，$AB=DE=6$，判断全等',
                "steps": [
                    "第 1 步：都是直角三角形（直角相等）",
                    "第 2 步：斜边 $AC=DF=10$",
                    "第 3 步：直角边 $AB=DE=6$",
                    "第 4 步：HL → 全等",
                ],
                "answer": "全等（HL）",
            },
        ],
        practice_data=[
            {"id": "ct-prac-001", "stem": "两个三角形的三边分别相等，它们一定全等吗？", "answer": "是（SSS）", "hints": ["想想判定定理", "哪个定理用三边？"]},
            {"id": "ct-prac-002", "stem": "为什么'边边角'（SSA）不能判定全等？", "answer": "因为已知两边和不是夹角的那角，可能画出两个不同的三角形", "hints": ["拿两根棍子，固定一个非夹角", "可以摆动出两个形状"]},
            {"id": "ct-prac-003", "stem": '$\\triangle ABC \\cong \\triangle DEF$，$AB=5$，那么 $DE$ 是多少？', "answer": "5（对应边相等）", "hints": ["全等三角形的对应边相等", "A对应D，B对应E"]},
            {"id": "ct-prac-004", "stem": "直角三角形全等的特殊判定定理是什么？", "answer": "HL（斜边-直角边）", "hints": ["不需要 SSS 或 SAS", "有一条特殊的判定法"]},
            {"id": "ct-prac-005", "stem": "全等符号 $\\cong$ 中的对应顶点为什么要对应写？", "answer": "因为对应关系决定哪些边和角相等", "hints": ["△ABC≅△DEF → A对D", "如果写颠倒了，对应关系就不对"]},
        ],
        test_data=[
            {"id": "ct-test-001", "stem": "下列哪个能判定两个三角形全等？A:SSA  B:AAA  C:SAS  D:两边一角（非夹角）", "answer": "C", "difficulty": 1, "layer": "understand"},
            {"id": "ct-test-002", "stem": '如图，$AB=AC$，$\\angle BAD=\\angle CAD$，求证 $BD=CD$', "answer": "SAS：AB=AC, ∠BAD=∠CAD, AD=AD(公共边) → △ABD≅△ACD → BD=CD", "difficulty": 2, "layer": "connect"},
            {"id": "ct-test-003", "stem": "两个直角三角形，斜边和一个锐角分别相等，下列说法正确的是？", "answer": "全等（AAS：直角+锐角+斜边，或HL+锐角）", "difficulty": 2, "layer": "understand"},
            {"id": "ct-test-004", "stem": '如图，$AD$ 是 $\\triangle ABC$ 的中线，$AB=AC$。求证 $\\triangle ABD \\cong \\triangle ACD$', "answer": "SSS: AB=AC, BD=CD(D是中点), AD=AD(公共边)", "difficulty": 2, "layer": "connect"},
            {"id": "ct-test-005", "stem": '如图，$\\angle 1 = \\angle 2$，$\\angle 3 = \\angle 4$。求证 $AB = CD$', "answer": "ASA:用公共边和两角证两个三角形全等，得AB=CD", "difficulty": 3, "layer": "connect"},
            {"id": "ct-test-006", "stem": "试说明：为什么AAA（三角相等）不能判定两个三角形全等？", "answer": "三角相等只能保证形状相同，不能保证大小相同（例如放大的相似三角形）", "difficulty": 3, "layer": "understand"},
        ],
        ai_data={
            "topic_summary": "全等三角形是初中几何证明的核心。5个判定定理（SSS/SAS/ASA/AAS/HL）是证明边等、角等的主要工具。注意SSA和AAA不能判定全等。全等证明训练的是逻辑推理能力——从已知条件一步步推到结论。",
            "key_insights": [
                "全等=完全重合，6个要素（3边3角）都相等",
                "判定只需3个条件，但不是任意3个——有5种正确组合",
                "SSA不能判定（可能画出两个不同的三角形）",
                "全等证明是几何证明的基础——大部分边等角等的问题最终都归结为全等",
            ],
            "common_mistakes": [
                {
                    "mistake": "用SSA判定全等",
                    "example": "已知 AB=DE, BC=EF, ∠A=∠D → 宣称全等",
                    "why": "SSA在教材中被明确排除——它不能保证唯一",
                    "how_to_explain": "用两根固定长度的棍子一端相连，夹角不固定——另一边可以有两个位置。这就是SSA的歧义性。",
                },
                {
                    "mistake": "对应顶点写错",
                    "example": "△ABC≅△DEF但证明时用 AB=EF",
                    "why": "没有严格按对应关系",
                    "how_to_explain": "全等符号中字母的位置蕴含了对应关系。A对D，B对E，C对F。写错了全盘皆输。",
                },
                {
                    "mistake": "忽略公共边/公共角",
                    "example": "找不到第三组相等条件就放弃了",
                    "why": "没有注意到图形中隐含的公共边或公共角",
                    "how_to_explain": "观察图形：有没有两个三角形共用一条边？这条边自动相等！公共角同理。这是证明中的免费条件。",
                },
            ],
            "alternate_explanations": [
                {
                    "method": "三角板比较法",
                    "when_to_use": "直观理解全等",
                    "prompt": "拿两个一样的三角板——它们是全等的。现在只给你三个条件（比如两边一夹角），你能不能确定三角板的形状和大小？试试看。",
                },
                {
                    "method": "建筑测量法",
                    "when_to_use": "理解全等在实际中的应用",
                    "prompt": "测量河对岸的一棵树到你的距离——你过不去怎么办？用全等三角形：在岸这边构造一个和河对岸三角形全等的三角形，量这边就等于量那边。这就是古代测量师的智慧。",
                },
            ],
            "question_templates": {
                "difficulty_1_2": "出 1 道判定定理选择题和 1 道简单证明题",
                "difficulty_3": "出 1 道需要辅助线的全等证明题",
                "difficulty_4": "出 1 道开放性的全等构造题",
            },
        },
    )


# We'll continue defining more modules. Let me continue with the remaining ones.
# To keep this file manageable, I'll use a systematic approach.


print("Script structure established. Continuing with remaining modules...")
print("This is a large script — remaining module definitions will be added.")

# -*- coding: utf-8 -*-
"""Generate all 20 content YAML files with proper syntax."""
import yaml
from pathlib import Path

BASE = Path(__file__).parent.parent / "content"


def wy(rel_path: str, data: dict):
    path = BASE / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=200)


# ═══════════════════════════════════════
# MATH NODES
# ═══════════════════════════════════════

wy("nodes/math/01-rational-numbers.yaml", {
    "slug": "rational-numbers", "subject": "math", "title": "有理数", "tier": "core", "difficulty": 1,
    "prerequisites": [], "estimated_min": 25,
    "trigger": {
        "type": "story", "title": "负数：一个被骂了 1000 年的天才想法",
        "content": {
            "text": '公元 7 世纪，印度数学家婆罗摩笈多第一个认真对待了"负数"。\n他在书中写道："财产减去债务等于负数。"\n\n但欧洲人直到 17 世纪还拒绝负数。\n笛卡尔——就是发明坐标系的那个笛卡尔——叫它"假数"（false number）。\n帕斯卡说："0 减去 4 等于 0，因为没有什么比什么都没有更小了。"\n\n今天你觉得 -5 很自然？那是因为你站在巨人的肩膀上。\n',
            "question": "为什么负数乘负数等于正数？你能想出一个生活中的例子来说明吗？",
        },
    },
    "content": {
        "operation": {
            "text": "## 有理数：能写成分数形式的数\n\n**定义**：有理数 = 能表示为 a/b 的数（a、b 为整数，b≠0）\n\n**包含**：整数（3 = 3/1）、分数（1/2）、有限小数（0.5 = 1/2）、无限循环小数（0.333... = 1/3）\n\n**不包含**：π（无限不循环）、√2（无限不循环）\n\n**运算法则**：\n- 加法：同号相加，异号相减，取绝对值大的符号\n- 减法：a - b = a + (-b)，转化为加法\n- 乘法：同号得正，异号得负\n- 除法：除以一个数 = 乘以它的倒数\n\n**绝对值**：|a| 表示数轴上 a 到原点的距离。|−5| = 5，|3| = 3\n",
            "examples": [
                {"input": "(-3) + (-5)", "output": "-8", "method": "同号相加：3+5=8，取负号"},
                {"input": "(-3) × (-4)", "output": "12", "method": "同号得正"},
                {"input": "(-6) ÷ 2", "output": "-3", "method": "异号得负"},
            ],
        },
        "understand": {
            "text": '## 为什么负负得正？\n\n不是"规定"——可以严格证明：\n\n(-1) × (1 - 1) = (-1) × 0 = 0\n\n同时：\n(-1) × (1 - 1) = (-1)×1 + (-1)×(-1) = -1 + 正数\n\n要得到 0，这个正数必须是 1！\n\n所以 (-1) × (-1) = 1，推广即得"负负得正"。\n\n**如果负负得负会怎样？**\n数学大厦会从地基崩塌——分配律失效，方程可能无解也可能无穷多解。\n',
            "highlights": ["负负得正不是规定，是可以证明的", "如果负负得负，整个数学体系会崩塌", "你手机里的 GPS 定位依赖负数运算"],
        },
        "connect": {
            "text": '## 负数在真实世界中无处不在\n\n- 温度：-5°C 比 0°C 冷\n- 银行账户：-200 元 = 欠款 200 元\n- 海拔：死海海拔 -430 米\n- 物理：电荷的正负、速度的方向\n- 游戏：血条减少显示为负值\n\n没有负数，你连"后退一步"都没法描述。\n\n**更深一层**：数学中还有"虚数"——负数的平方根。\n虽然叫"虚"，但交流电、量子力学、信号处理都离不开它。\n"假数"在 100 年后成了真数学。\n',
            "thought_seeds": ['虚数 i² = -1——比负数更"假"但更强大', "交流电用复数表示——没有虚数就没有现代电网", '数学中"假"的概念最终往往变成真工具'],
        },
    },
    "feynman": {
        "base_prompt": "用你自己的话解释：什么是有理数？负负得正为什么是对的（不是背规则）？",
        "key_elements": ["能写成分数形式", "包含整数和分数", "负负得正可以从分配律证明", "现实生活中负数很有用"],
        "deep_questions": ["如果让你说服一个不相信负数的小学生，你第一句话说什么？", "你觉得古人为什么拒绝负数？如果你活在 1600 年，你会相信负数吗？"],
        "missing_hints": {
            "能写成分数形式": "有理数的定义是什么？能写成什么形式？", "包含整数和分数": "整数和分数都属于有理数吗？举个例子。",
            "负负得正可以从分配律证明": "(-1)×(1-1) 用两种方式算，能得到什么？", "现实生活中负数很有用": "除了欠钱，生活中还有哪里用负数？",
        },
    },
    "thought_card": "今天学到的哪一点最让你意外？为什么？",
})

wy("nodes/math/02-polynomials.yaml", {
    "slug": "polynomials", "subject": "math", "title": "整式的加减", "tier": "core", "difficulty": 1,
    "prerequisites": ["rational-numbers"], "estimated_min": 25,
    "trigger": {
        "type": "story", "title": "代数：把话说给全世界听",
        "content": {
            "text": '16 世纪，法国数学家韦达（François Viète）做了一件了不起的事：\n他用字母代替数字来写数学。\n\n在此之前，每个国家的数学书都用自己的语言描述："某个数加上另一个数"。\n韦达用 $a + b$ 就搞定了——全世界都能看懂。\n\n从那天起，数学真正成了"通用语言"。\n',
            "question": "为什么要用字母表示数？用数字不好吗？",
        },
    },
    "content": {
        "operation": {
            "text": "## 整式：由数和字母通过加减乘组成的式子\n\n**单项式**：数 × 字母的乘积，如 $3x^2$、$-5ab$\n\n**多项式**：多个单项式的和，如 $3x^2 - 5x + 2$\n\n**同类项**：字母部分完全相同的项，如 $3x^2$ 和 $-2x^2$\n\n**合并同类项**：系数相加，字母部分不变\n- $3x^2 + 5x^2 = 8x^2$\n- $7ab - 3ab = 4ab$\n\n**去括号**：\n- $+(a+b) = a+b$\n- $-(a+b) = -a-b$（括号前是负号，里面每项都要变号）\n",
            "examples": [
                {"input": "合并：3x + 5x - 2x", "output": "6x", "method": "(3+5-2)x = 6x"},
                {"input": "化简：-(x - y)", "output": "-x + y", "method": "每项变号"},
            ],
        },
        "understand": {
            "text": "## 为什么 $-(a-b)$ 等于 $-a+b$？\n\n括号前面的负号本质是"乘以 -1"：\n$$-(a-b) = (-1) \\times (a-b) = (-1)\\times a + (-1)\\times(-b) = -a + (+b) = -a + b$$\n\n关键在最后一步：$(-1) \\times (-b) = +b$——负负得正！\n\n**常见错误**：$- (x + 3)$ 写成 $-x + 3$。错！$-(x+3) = -x - 3$\n",
            "highlights": ["去括号的负号规则本质是分配律 + 负负得正", "代数让数学从具体数字走向了一般规律"],
        },
        "connect": {
            "text": "## 整式运算的威力：从算术到方程\n\n整式是学方程的基础。没有整式的化简能力，你无法解：\n$$3(x+2) - 2(x-1) = 14$$\n\n化简后：$3x + 6 - 2x + 2 = x + 8 = 14$\n\n**物理学中的应用**：自由落体高度公式 $h = -\\frac{1}{2}gt^2 + v_0t + h_0$ 就是整式。\n",
            "thought_seeds": ["代数让'找规律'从猜变成了算", "所有科学公式本质上都是整式的组合"],
        },
    },
    "feynman": {
        "base_prompt": "用你自己的话解释：什么是同类项？去括号时为什么括号前是负号就要变号？",
        "key_elements": ["同类项是字母部分完全相同的项", "合并同类项是系数相加", "负号去括号每项都变号", "因为负号相当于乘以-1"],
        "deep_questions": ["如果去掉括号 $-(a+b+c)$，结果是什么？为什么？", "你觉得代数和算术最大的区别是什么？"],
        "missing_hints": {
            "同类项是字母部分完全相同的项": "3x²和5x²有什么共同点？3x²和3x呢？", "合并同类项是系数相加": "把同类项合并时，字母部分怎么办？",
            "负号去括号每项都变号": "-(x+y) 展开后是什么？里面的每一项发生了什么？", "因为负号相当于乘以-1": "去掉括号本质上是用了什么运算律？",
        },
    },
    "thought_card": '今天你学到了什么让你觉得"原来如此"的东西？',
})

wy("nodes/math/03-linear-equation.yaml", {
    "slug": "linear-equation", "subject": "math", "title": "一元一次方程", "tier": "core", "difficulty": 2,
    "prerequisites": ["rational-numbers", "polynomials"], "estimated_min": 25,
    "trigger": {
        "type": "story", "title": "未知数：人类最强大的思维工具",
        "content": {
            "text": '古埃及人在《莱因德纸草书》（公元前 1650 年）中就解过方程。\n他们用"堆"（aha）来代表未知数。\n\n比如："一堆加上它的 1/4 等于 15，这堆是多少？"\n用今天的写法：$x + x/4 = 15$ → $x = 12$\n\n古人没学过代数，但他们发现：承认"有个我们不知道的数"存在，\n我们就可以通过已知关系把它"逼"出来。\n',
            "question": "如果你不知道一个数是多少，你怎么可能算出来它？",
        },
    },
    "content": {
        "operation": {
            "text": "## 一元一次方程：一个未知数 + 最高次数 1\n\n**标准形式**：$ax + b = 0$（a ≠ 0）\n\n**解方程的核心思想**：等式两边同时做相同的运算，天平平衡\n\n**基本步骤（五步法）**：\n1. 去分母（同乘最小公分母）\n2. 去括号\n3. 移项（过等号变号）\n4. 合并同类项\n5. 系数化为 1\n\n**示例**：解 $\\frac{x+1}{2} - \\frac{x-2}{3} = 1$\n→ 去分母 ×6：$3(x+1) - 2(x-2) = 6$\n→ $3x + 3 - 2x + 4 = 6$\n→ $x + 7 = 6$\n→ $x = -1$\n",
            "examples": [{"input": "解 2x+3=7", "output": "x=2", "method": "移项：2x=7-3=4, x=2"}],
        },
        "understand": {
            "text": '## 为什么"移项过等号要变号"？\n\n移项的本质是"等式的两边同时做同一件事"。\n\n$2x + 3 = 7$\n\n两边同时减 3：\n$2x + 3 - 3 = 7 - 3$\n$2x = 4$\n\n看到 3 从左边"移到"右边变成 -3——这只是表象。\n**真相**是：两边同时做了减法。移项是"等式性质"的简记法。\n\n**为什么两边可以做同样的事？**\n因为等号表示"左右相等"。如果你只改变一边，天平就倾了。\n',
            "highlights": ["移项变号不是死记硬背，是等式两边同时操作的结果", "方程本质是：未知数必须满足什么条件"],
        },
        "connect": {
            "text": "## 方程思维：用已知求未知\n\n方程不只是数学题——它是一种思维方式：\n- 侦探破案：已知线索 → 未知凶手\n- 医生诊断：已知症状 → 未知病因\n- 工程：已知受力 → 未知材料强度\n\n每次你问"在什么条件下这件事会发生"，你都在用方程思维。\n\n**延伸到二元一次方程**：$y = 2x + 1$ 不仅仅是方程——它是直线的方程，连接了代数和几何。笛卡尔发明坐标系的那一刻，代数和几何就结婚了。\n",
            "thought_seeds": ["方程 = 天平，等号两边永远相等", "笛卡尔用坐标系把代数变成了图像"],
        },
    },
    "feynman": {
        "base_prompt": "用你自己的话解释：解方程的核心思想是什么？为什么移项要变号？",
        "key_elements": ["等式两边同时做相同的运算", "移项变号是等式性质的结果", "最终求出未知数的值", "方程可以用来解实际问题"],
        "deep_questions": ['如果你来教一个从没学过方程的同学，你会怎么解释"等式两边同时加减"？', "方程和算术最大的区别是什么？"],
        "missing_hints": {
            "等式两边同时做相同的运算": "天平两边如果一边拿走砝码，另一边应该怎么办？", "移项变号是等式性质的结果": "移项到底做了什么？有没有更本质的解释？",
            "最终求出未知数的值": "解方程的目标是什么？", "方程可以用来解实际问题": "除了数学题，生活中什么时候需要解方程？",
        },
    },
    "thought_card": "今天学到的哪一点最让你意外？为什么？",
})

wy("nodes/math/14-factorization.yaml", {
    "slug": "factorization", "subject": "math", "title": "因式分解", "tier": "core", "difficulty": 3,
    "prerequisites": ["polynomials"], "estimated_min": 25,
    "trigger": {
        "type": "story", "title": "RSA加密：你的密码靠因式分解保护",
        "content": {
            "text": "你每次登录微信、网购支付——背后都有一个数学操作在保护你：因式分解。\n\nRSA 加密的核心是：两个大质数相乘很容易，但把一个巨大的乘积\n拆回原来的两个质数极难——即使是最快的计算机也要算几万年。\n\n这就是"正向容易、逆向极难"的魔力。\n而这种"拆分"的思维，就是因式分解。\n",
            "question": "为什么把东西拆开有时候比拼起来难得多？",
        },
    },
    "content": {
        "operation": {
            "text": "## 因式分解：把多项式还原成乘积形式\n\n整式乘法：$(x+2)(x+3) = x^2 + 5x + 6$\n因式分解：$x^2 + 5x + 6 = (x+2)(x+3)$ ← 逆过程！\n\n**三大基本方法**：\n\n1. **提公因式**：$ab + ac = a(b+c)$\n   例：$3x^2 + 6x = 3x(x + 2)$\n\n2. **公式法**：\n   - 平方差：$a^2 - b^2 = (a+b)(a-b)$\n   - 完全平方：$a^2 + 2ab + b^2 = (a+b)^2$\n   - 完全平方：$a^2 - 2ab + b^2 = (a-b)^2$\n\n3. **十字相乘法**（$x^2$ 系数为 1 时）：\n   $x^2 + (p+q)x + pq = (x+p)(x+q)$\n   例：$x^2 + 5x + 6 = (x+2)(x+3)$\n",
            "examples": [{"input": "分解 $x^2-9$", "output": "$(x+3)(x-3)$", "method": "平方差公式"}],
        },
        "understand": {
            "text": "## 为什么因式分解这么有用？\n\n因式分解的核心威力：**把一个难的问题拆成几个简单的问题**。\n\n**解方程的应用**：\n$x^2 + 5x + 6 = 0$\n→ $(x+2)(x+3) = 0$\n→ $x = -2$ 或 $x = -3$（乘积为 0 ⇔ 至少一个因子为 0）\n\n没有因式分解，二次方程很难解——这就是为什么古人要发明它。\n\n**为什么 RSA 加密依赖因式分解困难？**\n因为"正向乘"是 O(n²) 的计算量，"逆向分解"可能是指数级的。\n这种**不对称性**正是密码学的基石。\n",
            "highlights": ["因式分解让解二次方程从'猜'变成了'算'", "乘积为 0 则至少一个因子为 0 —— 这是因式分解解方程的关键逻辑"],
        },
        "connect": {
            "text": "## 因式分解的跨学科意义\n\n- **密码学**：RSA 加密 = 大数质因数分解的困难性\n- **信号处理**：傅里叶变换本质上是把信号"因式分解"成不同频率\n- **化学**：化学方程式配平 = 线性方程组的整数解\n\n**更深一层**："分解→分析→重构"是解决所有复杂问题的通用方法，\n因式分解只是这个思维模式的数学表达。\n",
            "thought_seeds": ["解方程是数学中最常见的操作，因式分解让它变简单", "逆向思维：不是算出来，而是退回去"],
        },
    },
    "feynman": {
        "base_prompt": "用你自己的话解释：因式分解是什么？为什么它能让解方程变简单？",
        "key_elements": ["把多项式拆成乘积", "是乘法分配律的逆运算", "可以用来解方程", "和分解质因数类似"],
        "deep_questions": ["如果你来设计一个加密方法，你会用因式分解的哪个特性？", '一个完全不懂数学的人问你"因式分解有什么卵用"，你怎么回答？'],
        "missing_hints": {
            "把多项式拆成乘积": "因式分解的结果是什么形式的？", "是乘法分配律的逆运算": "整式乘法和因式分解是什么关系？",
            "可以用来解方程": "$(x+2)(x+3)=0$ 的解是多少？为什么？", "和分解质因数类似": "12 的质因数分解和 x²-9 的因式分解有什么相似？",
        },
    },
    "thought_card": '今天你学到了什么让你觉得"原来如此"的东西？',
})

wy("nodes/math/17-pythagorean.yaml", {
    "slug": "pythagorean", "subject": "math", "title": "勾股定理", "tier": "core", "difficulty": 2,
    "prerequisites": ["rational-numbers"], "estimated_min": 25,
    "trigger": {
        "type": "story", "title": "勾股定理：人类最早的'大数据'",
        "content": {
            "text": '勾股定理是人类历史上证明方法最多的定理——超过 400 种！\n\n从中国的《周髀算经》（"勾三股四弦五"）到古希腊的毕达哥拉斯，\n从印度的《绳法经》到阿拉伯的代数证明——\n每个文明都独立发现了它。\n\n最惊艳的证明之一来自美国总统加菲尔德（1881年），\n他用梯形的面积公式就证出来了。\n\n一个定理，跨越 3000 年、6 个大陆，被反复证明——\n它在人类知识中有什么魔力？\n',
            "question": "为什么勾股定理是人类历史上证明方法最多的定理？",
        },
    },
    "content": {
        "operation": {
            "text": "## 勾股定理：直角边的平方和等于斜边的平方\n\n$$a^2 + b^2 = c^2$$\n\n其中 c 是斜边（直角对边），a 和 b 是直角边。\n\n**常用勾股数**：\n- 3-4-5：$3^2 + 4^2 = 9 + 16 = 25 = 5^2$\n- 5-12-13：$25 + 144 = 169 = 13^2$\n- 6-8-10：$36 + 64 = 100 = 10^2$（3-4-5 的 2 倍）\n- 8-15-17：$64 + 225 = 289 = 17^2$\n\n**判断直角三角形**：如果三角形三边满足 $a^2+b^2=c^2$，就是直角三角形（逆定理也成立）。\n",
            "examples": [{"input": "直角边 3 和 4，求斜边", "output": "5", "method": "c = √(9+16) = √25 = 5"}],
        },
        "understand": {
            "text": "## 为什么 $a^2+b^2=c^2$ 是对的？\n\n**面积法直觉证明**：\n\n想象一个边长为 a+b 的大正方形，里面画 4 个全等的直角三角形。\n- 中间空出一个边长为 c 的小正方形\n- 大正方形面积 = 4 个三角形 + c²\n- $(a+b)^2 = 4 × (ab/2) + c^2$\n- $a^2 + 2ab + b^2 = 2ab + c^2$\n- **$a^2 + b^2 = c^2$** ✓\n\n**本质**：面积不变，用两种方式算同一块面积——巧妙！\n",
            "highlights": ["400+种证明，因为它是几何和代数之间的桥梁", "面积法证明是最优雅的方式之一"],
        },
        "connect": {
            "text": "## 勾股定理无处不在\n\n- **GPS 导航**：你的手机计算你和卫星的距离，用的就是勾股定理（三维版）\n- **建筑**：古代埃及人用 3-4-5 绳子做直角\n- **物理**：相对论中的"时空间隔"公式 $Δs^2 = Δt^2 - Δx^2$ 就是勾股定理的变体\n- **计算机图形**：屏幕上两点之间的距离就是勾股定理\n\n**更深一层**：勾股定理把"直角"和"距离"联系在了一起。\n没有它，我们无法统一地定义"两点之间的距离"。\n",
            "thought_seeds": ["3-4-5 三角形是古代测量直角的标准工具", "相对论中的时空间隔本质上是勾股定理的推广"],
        },
    },
    "feynman": {
        "base_prompt": "用你自己的话解释：勾股定理说的是什么？为什么它是对的？（不用背证明，用你的理解）",
        "key_elements": ["直角三角形斜边的平方等于两直角边的平方和", "可以用于求某一边的长度", "逆定理可以判定直角三角形", "在生活中有广泛应用"],
        "deep_questions": ["如果勾股定理不成立，我们生活的世界会是什么样？", "你觉得为什么每个文明都独立发现了它？"],
        "missing_hints": {
            "直角三角形斜边的平方等于两直角边的平方和": "直角三角型的三条边中哪条最长？长的和其他两条有什么关系？",
            "可以用于求某一边的长度": "知道两条直角边，能求什么？", "逆定理可以判定直角三角形": "如果三边满足 a²+b²=c²，这个三角形是什么三角形？",
            "在生活中有广泛应用": "除了数学题，哪里用到勾股定理？",
        },
    },
    "thought_card": '今天你学到了什么让你觉得"原来如此"的东西？',
})

# ═══════════════════════════════════════
# ENGLISH NODES
# ═══════════════════════════════════════

wy("nodes/english/01-phonetics.yaml", {
    "slug": "phonetics", "subject": "english", "title": "音标与拼读", "tier": "core", "difficulty": 1,
    "prerequisites": [], "estimated_min": 25,
    "trigger": {
        "type": "story", "title": "你为什么能读出没见过的单词？",
        "content": {
            "text": '英语有 44 个音素，但只有 26 个字母。\n\n这意味着同一个字母在不同单词里读不同的音——\n"ghoti" 完全可以读成 "fish"：\n- gh 像 enough 里的 /f/\n- o 像 women 里的 /ɪ/\n- ti 像 nation 里的 /ʃ/\n\n这就是为什么你需要音标——它是英语发音的"拼音系统"。\n一旦掌握，你就能读任何不认识的单词。\n',
            "question": "为什么英语的拼写和发音常常不一致？",
        },
    },
    "content": {
        "operation": {
            "text": "## 国际音标（IPA）基础\n\n**48 个音标 = 20 个元音 + 28 个辅音**\n\n**元音（Vowels）**：\n- 单元音：/iː/ (see)、/ɪ/ (sit)、/e/ (bed)、/æ/ (cat)、/ʌ/ (cup)、/ɑː/ (car)、/ɒ/ (hot)、/ɔː/ (door)、/ʊ/ (book)、/uː/ (too)、/ɜː/ (bird)、/ə/ (about)\n- 双元音：/aɪ/ (my)、/eɪ/ (day)、/ɔɪ/ (boy)、/aʊ/ (now)、/əʊ/ (go)、/ɪə/ (here)、/eə/ (hair)、/ʊə/ (tour)\n\n**辅音（Consonants）**：\n- 清辅音：/p/ /t/ /k/ /f/ /θ/ /s/ /ʃ/ /tʃ/ /tr/ /ts/ /h/\n- 浊辅音：/b/ /d/ /g/ /v/ /ð/ /z/ /ʒ/ /dʒ/ /dr/ /dz/ /r/\n- 鼻音和半元音：/m/ /n/ /ŋ/ /l/ /w/ /j/\n\n**拼读规则**：\n- 开音节（以元音结尾）：元音读本音，如 go、she、hi\n- 闭音节（以辅音结尾）：元音读短音，如 cat、bed、sit\n",
            "examples": [
                {"input": "name 为什么读 /neɪm/？", "output": "末尾有 e → 开音节 → a 读 /eɪ/"},
                {"input": "cat 为什么读 /kæt/？", "output": "以辅音 t 结尾 → 闭音节 → a 读 /æ/"},
            ],
        },
        "understand": {
            "text": '## 为什么"音标"和"字母"不是一回事？\n\n英语在历史上被多次"入侵"——日耳曼语、拉丁语、法语、希腊语——\n每次入侵都带来新的单词和拼写规则。\n\n结果就是：英语的拼写大约定型于 15 世纪（印刷术出现），\n但发音一直在变化。所以写和读脱节了。\n\n**great vowel shift（元音大推移）**：\n14-18 世纪，英语长元音的发音发生了系统性变化：\n- name 原本读 /naːmə/ → 现在读 /neɪm/\n- feet 原本读 /feːt/ → 现在读 /fiːt/\n\n拼写没跟上发音的变化——这就是一切混乱的根源。\n',
            "highlights": ["英语拼写混乱是因为拼写在 500 年前就定型了，发音却一直在变", "音标是'作弊码'——学会就能读任何单词"],
        },
        "connect": {
            "text": "## 音标不只是学英语的工具\n\n- **语言学**：所有语言都可以用 IPA 来记音\n- **演戏/播音**：演员和播音员需要音标来学习方言和外语口音\n- **AI 语音**：Siri/Alexa 用音素序列来合成语音\n- **语言康复**：听力障碍者通过音标视觉线索学习发音\n\n**更深一层**：音标让你意识到——发音是可以被"看见"的。\n把声音变成视觉符号，这是人类的一大发明。\n",
            "thought_seeds": ["国际音标可以标注世界上任何一种语言的发音", "你的手机里的语音助手就是一个'音标引擎'"],
        },
    },
    "feynman": {
        "base_prompt": "用你自己的话解释：什么是音标？为什么英语需要音标而中文不需要？",
        "key_elements": ["音标记录发音", "英语拼写和发音不一致", "开音节/闭音节规律", "学会音标能读任何新单词"],
        "deep_questions": ["如果要你设计一套新的英语拼写系统（完全照读音写），你会怎么设计？会遇到什么问题？", "你觉得中文为什么不需要音标（拼音是后来发明的）？"],
        "missing_hints": {
            "音标记录发音": "音标的作用是什么？和字母有什么区别？", "英语拼写和发音不一致": "同一个字母在不同单词里读法一样吗？举例。",
            "开音节/闭音节规律": "结尾的 e 会影响前面的元音发音吗？", "学会音标能读任何新单词": "遇到不认识单词，你有音标就能做到什么？",
        },
    },
    "thought_card": "你今天学到了什么以前不知道的发音规律？",
})

wy("nodes/english/02-nouns-articles.yaml", {
    "slug": "nouns-articles", "subject": "english", "title": "名词与冠词", "tier": "core", "difficulty": 1,
    "prerequisites": ["phonetics"], "estimated_min": 25,
    "trigger": {
        "type": "story", "title": "the 是英语中最常用的词——但你用对了吗？",
        "content": {
            "text": "英语中最常见的词不是 I、you 或 hello，而是——**the**。\n\n这个只有三个字母的小词，每天被全球数十亿人使用。\n但它背后的逻辑却让无数学习者困惑：\n\n\"the sun\" 但不说 \"a sun\"（因为只有一个太阳）\n\"I saw a dog\" 但不说 \"I saw the dog\"（除非你知道是哪只狗）\n\n中文没有冠词，所以中国学习者尤其需要建立一种新直觉。\n好消息是：一旦学会，你就再也不会用错了。\n",
            "question": "你能感受到 the 和 a/an 的区别吗？试着用中文解释一下？",
        },
    },
    "content": {
        "operation": {
            "text": "## 名词分类和冠词使用\n\n**名词分类**：\n\n1. **可数名词**：有单复数\n   - book → books, child → children\n   - 单数可数名词不能单独出现 → 必须加 a/an/the\n   - ✗ \"I have book\" → ✓ \"I have a book\"\n\n2. **不可数名词**：没有复数形式\n   - water, information, music, furniture\n   - 不可数名词前面不加 a/an\n   - ✗ \"a water\" → ✓ \"water\" 或 \"some water\"\n\n**冠词规则**：\n\n| 冠词 | 用法 | 例子 |\n|------|------|------|\n| a/an | 泛指、第一次提到、单数可数 | a book, an apple |\n| the | 特指、双方都知道的、唯一的 | the sun, the book I bought |\n| 零冠词 | 不可数泛指、复数泛指 | water, books |\n",
            "examples": [{"input": "\"I saw dog in park\" 哪里错？", "output": "→ I saw a dog in the park（第一次提到狗用 a，公园是特定的用 the）"}],
        },
        "understand": {
            "text": "## 为什么中文没有冠词而英语必须有？\n\n英语冠词做了一件事：**标记信息的新旧**。\n\n- **a/an** = "注意！这是我第一次提到这个东西"（新信息）\n- **the** = "你应该知道我说的是哪个"（已知信息）\n\n中文没有这种语法标记，但我们会用"那个"、"一个"来表达类似的含义。\n区别是：在英语中，这不是可选的——是语法要求。\n\n**有趣的事实**：\n英语是少数有冠词的语言。世界上大多数语言（包括汉语、日语、俄语、\n印地语）都没有冠词。有冠词的语言主要分布在欧洲。\n",
            "highlights": ["a/an 标记'新信息'，the 标记'已知信息'", "冠词是强制性的——不能用'听起来自然'来判断"],
        },
        "connect": {
            "text": "## 冠词错误能改变意思\n\n- \"Go to school\"（去上学）vs \"Go to the school\"（去学校那个建筑——可能是去接人）\n- \"in hospital\"（住院治疗）vs \"in the hospital\"（在医院里——可能是访客）\n- \"out of question\"（毫无疑问）vs \"out of the question\"（绝不可能）\n\n这些细微差别的冠词能让意思完全反转！\n\n**更深一层**：冠词系统反映了语言如何编码"共有知识"——\n一个社群中大家都知道的事不需要特别标记，新信息则需要。\n这其实是人类认知的基本模式。\n",
            "thought_seeds": ["the 用来标记'我们双方都知道的东西'", "冠词错误是最常见的中式英语特征之一"],
        },
    },
    "feynman": {
        "base_prompt": "用你自己的话解释：a/an 和 the 的本质区别是什么？为什么 a water 是错的？",
        "key_elements": ["a/an 用于泛指/第一次提到", "the 用于特指/已知的", "不可数名词不加 a/an", "中文没有冠词系统"],
        "deep_questions": ["如果让你教一个外星人学英语冠词，第一个例子你会用什么？", "你觉得是中文'不需要'冠词，还是中文用其他方式表达了同样的意思？"],
        "missing_hints": {
            "a/an 用于泛指/第一次提到": "第一次说一只狗时用 a 还是 the？", "the 用于特指/已知的": "说到太阳时为什么用 the？",
            "不可数名词不加 a/an": "为什么不能说 a water？water 是什么类型的名词？",
            "中文没有冠词系统": "中文怎么表达'一个'和'那个'？这和英语冠词有什么不同？",
        },
    },
    "thought_card": "今天你学会了哪个冠词用法是以前用错的？",
})

wy("nodes/english/04-tenses-basic.yaml", {
    "slug": "tenses-basic", "subject": "english", "title": "四大基础时态", "tier": "core", "difficulty": 2,
    "prerequisites": ["nouns-articles"], "estimated_min": 25,
    "trigger": {
        "type": "story", "title": "中文没有时态——那你怎么知道事情发生在什么时候？",
        "content": {
            "text": '中文用"了"、"过"、"正在"、"将"来表示时间，但动词本身不变：\n- 我**吃了**饭 / 我**吃过**饭 / 我**正在吃**饭 / 我**要吃**饭\n\n英语完全不同——动词本身要变形：\n- I **ate** / I **have eaten** / I **am eating** / I **will eat**\n\n这意味着说英语时，你每说一个动词就要考虑时间。\n听起来很累？但一旦内化，你就有了一个"时间GPS"，\n能精确表达任何时刻的动作。\n',
            "question": "你觉得中文用时间词、英语用动词变形——哪种更'聪明'？为什么？",
        },
    },
    "content": {
        "operation": {
            "text": "## 四大基础时态\n\n### 1. 一般现在时（Present Simple）\n- 用法：习惯、事实、规律\n- 形式：do/does + 动词原形（三单+s/es）\n- 标志：always, usually, every day\n- 例：I **go** to school every day. She **goes** to school every day.\n\n### 2. 一般过去时（Past Simple）\n- 用法：过去完成的动作\n- 形式：动词过去式（规则+ed、不规则变化）\n- 标志：yesterday, last week, in 2020\n- 例：I **went** to school yesterday.\n\n### 3. 现在进行时（Present Continuous）\n- 用法：正在进行的动作\n- 形式：am/is/are + V-ing\n- 标志：now, at the moment\n- 例：I **am studying** now.\n\n### 4. 一般将来时（Future Simple）\n- 用法：将要发生的动作\n- 形式：will + 动词原形 / be going to + 动词原形\n- 标志：tomorrow, next week, in the future\n- 例：I **will go** to school tomorrow.\n",
            "examples": [
                {"input": "every day 用哪个时态？", "output": "一般现在时 → I play basketball every day."},
                {"input": "yesterday + 动作 → 什么时态？", "output": "一般过去时 → I played basketball yesterday."},
            ],
        },
        "understand": {
            "text": '## "will" 和 "be going to" 有什么区别？\n\n两者都表示将来，但细微区别很重要：\n\n- **will**：说话时当场决定的、预测的\n  - "It\'s cold" → "I **will** close the window."（刚才决定的）\n\n- **be going to**：事先计划好的、有迹象的\n  - "I **am going to** visit my grandma tomorrow."（已经计划好了）\n  - "Look at the clouds! It **is going to** rain."（有迹象）\n\n**为什么英语需要这么多时态？**\n因为英语缺少中文那样的时间状语灵活性——\n中文说"我明天去学校"，动词"去"不需要变。\n英语必须在动词上体现时间信息。\n',
            "highlights": ["will = 当场决定，be going to = 事先计划", "时间标志词是判断时态的最快方法"],
        },
        "connect": {
            "text": "## 时间语法与思维方式\n\n语言学家发现：语言如何表达时间，会影响人们如何感知时间。\n\n英语强制标记时间（每个动词都要有时态），英语母语者\n普遍对时间的"点"和"段"更敏感。\n\n而中文不必标记时间，中文母语者更容易看到事件的"关联性"而不是"先后性"。\n\n这不是谁好谁坏——而是不同的思维工具。\n",
            "thought_seeds": ["语言影响思维——强制标记时间的语言使用者在时间感知上更精确", "12 种时态其实只有 3 个时间×4 个状态，记忆时用矩阵法更高效"],
        },
    },
    "feynman": {
        "base_prompt": "用你自己的话解释：四大基础时态分别什么时候用？will 和 be going to 有什么区别？",
        "key_elements": ["一般现在时表习惯和事实", "一般过去时表过去的动作", "现在进行时表正在发生", "一般将来时表将要发生"],
        "deep_questions": ["如果英语取消时态，改用时间词（like 中文），你觉得会更简单还是更复杂？", "你觉得时态最难的地方在哪里？你用什么方法克服？"],
        "missing_hints": {
            "一般现在时表习惯和事实": "I ___ (get) up at 7 every day. 用什么时态？",
            "一般过去时表过去的动作": "yesterday 出现通常用什么时态？",
            "现在进行时表正在发生": "look!/now 出现通常用什么时态？",
            "一般将来时表将要发生": "tomorrow/next week 出现通常用什么时态？",
        },
    },
    "thought_card": "今天学到的哪个时态细节是你以前没注意到的？",
})

wy("nodes/english/11-present-perfect.yaml", {
    "slug": "present-perfect", "subject": "english", "title": "现在完成时", "tier": "trunk", "difficulty": 3,
    "prerequisites": ["tenses-basic"], "estimated_min": 25,
    "trigger": {
        "type": "story", "title": "一种让英语母语者也解释不清的时态",
        "content": {
            "text": "如果问一个英国人\"现在完成时是什么\"，他很可能会说\"I have no idea, I just use it.\"\n\n这就是母语者的秘密——他们用语法但从不想语法。\n\n但对学习者来说，现在完成时是英语时态中最微妙的一个：\n它不是\"过去\"，也不是\"现在\"——而是\"过去对现在的影响\"。\n\n比如：\n\"I lost my key\"（过去某个时候丢了）——可能已经找回来了\n\"I have lost my key\"（已经丢了）——现在还在找\n\n两句话描述的是同一件事，但\"现在完成时\"把过去和现在连在了一起。\n",
            "question": "你能感觉到 'I lost' 和 'I have lost' 的区别吗？",
        },
    },
    "content": {
        "operation": {
            "text": "## 现在完成时（Present Perfect）\n\n**形式**：have/has + 过去分词（V3）\n\n**三种核心用法**：\n\n### 1. 完成用法（Result）：过去动作对现在有结果/影响\n- I **have lost** my key.（现在钥匙还没找到）\n- She **has finished** her homework.（现在作业已经完成了）\n\n### 2. 经历用法（Experience）：到目前为止的经历\n- I **have been** to Beijing three times.（到目前为止去过 3 次）\n- **Have** you ever **eaten** sushi?（你这辈子吃过寿司吗？）\n\n### 3. 持续用法（Duration）：从过去持续到现在\n- I **have lived** here for 10 years.（10 年前开始住，现在还在住）\n- She **has known** him since 2015.（2015 年认识，现在还认识）\n",
            "examples": [
                {"input": "I lost my key vs I have lost my key", "output": "前者=过去丢了（可能找到了），后者=已经丢了（现在还在找）"},
                {"input": "for 10 years 用什么时态？", "output": "现在完成时 → I have studied English for 10 years."},
            ],
        },
        "understand": {
            "text": "## 现在完成时 vs 一般过去时 —— 终极区别\n\n| 时态 | 聚焦 | 时间词示例 |\n|------|------|-----------|\n| 一般过去时 | 过去的动作 | yesterday, last week, in 2010, 3 days ago |\n| 现在完成时 | 过去→现在的连接 | just, already, yet, ever, never, since, for |\n\n**关键判别法**：问自己 —— \"这个动作和现在有关吗？\"\n\n- \"I ate breakfast at 7am.\" → 现在中午了，和现在无关 → 一般过去时 ✓\n- \"I have already eaten breakfast.\" → 现在不饿了，和现在有关 → 现在完成时 ✓\n\n**中式英语常见错误**：\n✗ \"I have seen him yesterday.\" → 有具体过去时间 yesterday → 必须用一般过去时\n",
            "highlights": ["现在完成时 = 过去和现在之间的桥梁", "有具体过去时间（yesterday/ago）永远不用现在完成时"],
        },
        "connect": {
            "text": '## 为什么每种语言都需要表达"完成"的概念？\n\n几乎每种语言都有"完成体"（perfective aspect），只是实现方式不同：\n- 英语：have + V3\n- 中文：了（动态助词）\n- 日语：〜た形\n- 西班牙语：haber + participio\n\n**深层的认知需求**：人类需要区分"事情本身"和"事情的后果"。\n"我丢了钥匙"可以是告诉你一个过去的事件，\n也可以是在解释为什么我现在进不了门——这是两个完全不同的沟通目的。\n\n现在完成时就是后者的语法化。\n',
            "thought_seeds": ["现在完成时关注的是'结果'和'影响'", "有具体过去时间 → 绝不能用现在完成时"],
        },
    },
    "feynman": {
        "base_prompt": "用你自己的话解释：现在完成时和一般过去时有什么本质区别？什么时候必须用现在完成时？",
        "key_elements": ["have/has + 过去分词", "强调过去对现在的影响", "和 already/just/ever/never/for/since 搭配", "有具体过去时间时不能用"],
        "deep_questions": ["如果你来给现在完成时取一个更直觉的中文名字，你会叫什么？", "你觉得中文的'了'和英语的现在完成时有什么相同和不同？"],
        "missing_hints": {
            "have/has + 过去分词": "现在完成时由什么助动词 + 什么形式？",
            "强调过去对现在的影响": "I have lost my key 和 I lost my key 感觉有什么不同？",
            "和 already/just/ever/never/for/since 搭配": "看到哪些词最常用现在完成时？",
            "有具体过去时间时不能用": "I have seen him yesterday 为什么是错的？",
        },
    },
    "thought_card": "今天你学会了哪个以前一直混淆的现在完成时用法？",
})

wy("nodes/english/16-object-clause.yaml", {
    "slug": "object-clause", "subject": "english", "title": "宾语从句", "tier": "trunk", "difficulty": 3,
    "prerequisites": ["tenses-basic"], "estimated_min": 25,
    "trigger": {
        "type": "story", "title": "把一句话塞进另一句话里",
        "content": {
            "text": "人类语言最神奇的能力之一是**递归**——无限嵌套：\n\"他说...\"\n\"他说她认为...\"\n\"他说她认为我知道...\"\n\"他说她认为我知道你在想...\"\n可以一直嵌套下去！\n\n宾语从句就是这种嵌套能力的语法体现。\n它让你能把一个完整的句子变成另一个句子的\"宾语\"——\n就像俄罗斯套娃。\n\n中文也做同样的事：\"他说她明天会来。\"\n但英语的玩法不同——你必须处理词序、时态、连接词。\n",
            "question": "你觉得语言为什么需要嵌套句子的能力？如果禁止嵌套会怎样？",
        },
    },
    "content": {
        "operation": {
            "text": "## 宾语从句：用句子做宾语\n\n**结构**：主句 + that/whether/wh-词 + 从句\n\n### 三种连接词\n\n1. **that**（陈述事实，常可省略）\n   - I know **(that)** he is right.\n   - She said **(that)** she would come.\n\n2. **whether / if**（是否，不确定）\n   - I don't know **whether/if** he will come.\n   - He asked me **if** I liked music.\n\n3. **wh-词**（what/who/when/where/why/how）\n   - Do you know **where** he lives?\n   - I wonder **what** she wants.\n\n### 关键规则\n- **词序**：从句永远用**陈述句语序**（主语+谓语）\n  - ✗ \"I don't know where does he live.\"\n  - ✓ \"I don't know where he lives.\"\n- **时态呼应**：主句过去时 → 从句也过去时\n  - She said she **was** tired.\n",
            "examples": [{"input": "\"Do you know where does she live?\" 哪里错？", "output": "→ Do you know where she lives?（从句用陈述语序）"}],
        },
        "understand": {
            "text": '## 为什么从句不能用疑问句语序？\n\n英语有一个铁律：**从句永远用陈述句语序**。\n\n这其实很合理——从句是"嵌套在另一个句子里的陈述"，\n它不是真正的问句，只是在提供信息。\n\n对比：\n- 直接问句：**Where does** he live? ← 主语和助动词倒装\n- 宾语从句：I don\'t know **where he lives**. ← 陈述语序\n\n**为什么英语要区分？**\n因为英语用词序来标记句子类型。问句倒装是一个"信号"——\n告诉听者"这是一个问题"。而从句是陈述的一部分，不需要这个信号。\n\n**时态呼应的逻辑**：\nShe **said** she **was** tired.（主句过去 → 从句过去）\n逻辑：她说话的时候是过去，她累也是当时——所以从句也用过去。\n',
            "highlights": ["从句永远用陈述语序 = 英语最铁的铁律之一", "主句过去 → 从句也过去（时态呼应）"],
        },
        "connect": {
            "text": "## 嵌套句子的能力是语言进化的重要一步\n\n人类是唯一能用语言递归嵌套的物种。动物可以发出警告信号，\n但没有任何动物能说\"我昨天看到的那个人告诉我明天会下雨\"——\n因为这需要在一个句子中嵌套时间、空间、和另一个人的视角。\n\n**宾语从句的本质**：在说话者的视角中嵌入另一个人的视角。\n这是人类独有的认知能力——心理理论（Theory of Mind）。\n\n你能理解\"他以为我不知道他知道\"吗？\n这就是三层嵌套——而你对宾语从句的掌握，正是这种认知能力的语言基础。\n",
            "thought_seeds": ["宾语从句 = 把一个完整句子当成一个名词来用", "从句用陈述语序，永远记住"],
        },
    },
    "feynman": {
        "base_prompt": "用你自己的话解释：宾语从句有哪三种连接词？为什么从句不能用问句语序？",
        "key_elements": ["that 连接陈述", "whether/if 表示'是否'", "wh-词引导特殊疑问", "从句用陈述语序"],
        "deep_questions": ["如果英语规则改成'从句也用问句语序'，你觉得会更容易还是更难？", "你能造一个三层嵌套的宾语从句吗？（例：I think that she knows that he said that...）"],
        "missing_hints": {
            "that 连接陈述": "表达一个确定的事实时用什么连接词？可以省略吗？",
            "whether/if 表示'是否'": "表达不确定/选择时用什么连接词？",
            "wh-词引导特殊疑问": "要问'在哪里'/'什么时候'/'为什么'，用什么词引导从句？",
            "从句用陈述语序": "主语和谓语在从句中应该是什么顺序？",
        },
    },
    "thought_card": "今天学到的宾语从句规则中，哪一条你最需要记住？",
})

print("All 10 nodes written successfully!")

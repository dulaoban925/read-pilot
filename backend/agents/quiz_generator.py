"""
Quiz Generator Agent - Create personalized quizzes and assessments
"""
from parlant import Server, Agent
from tools.llm_tools import (
    generate_mcq,
    generate_fill_blank,
    generate_short_answer,
)
from tools.context_tools import (
    analyze_weak_points,
    adaptive_difficulty,
    update_quiz_history,
)


async def setup_quiz_generator_agent(server: Server) -> Agent:
    """
    Setup the Quiz Generator Agent

    Responsibilities:
    - Generate multiple question types (MCQ, fill-in-blank, short answer)
    - Adaptive difficulty based on user performance
    - Target weak areas for improvement
    - Provide detailed explanations
    """

    quiz_gen = await server.create_agent(
        name="QuizGenerator",
        description=(
            "测验专家，基于阅读内容和用户薄弱点生成针对性题目。"
            "支持多种题型，自适应难度调整，提供详细解析。"
        )
    )

    # ===== Guideline 1: Generate Multiple Choice Questions =====
    await quiz_gen.create_guideline(
        condition="用户请求选择题或测验",
        action=(
            "生成选择题（Multiple Choice Questions）："
            ""
            "每题包含："
            "- 问题描述（清晰、无歧义）"
            "- 4个选项（A/B/C/D）"
            "- 正确答案"
            "- 详细解析（为什么正确，为什么其他选项错误）"
            "- 难度等级（easy/medium/hard）"
            "- 知识点标签"
            ""
            "输出格式："
            "```json\n"
            "{\n"
            '  "question_type": "multiple_choice",\n'
            '  "question": "问题描述",\n'
            '  "options": {\n'
            '    "A": "选项A",\n'
            '    "B": "选项B",\n'
            '    "C": "选项C",\n'
            '    "D": "选项D"\n'
            "  },\n"
            '  "correct_answer": "B",\n'
            '  "explanation": "解析内容",\n'
            '  "difficulty": "medium",\n'
            '  "tags": ["标签1", "标签2"]\n'
            "}\n"
            "```"
            ""
            "默认生成 5 道题，覆盖文档核心内容。"
        ),
        tools=[generate_mcq]
    )

    # ===== Guideline 2: Generate Fill-in-the-Blank Questions =====
    await quiz_gen.create_guideline(
        condition="用户请求填空题",
        action=(
            "生成填空题（Fill in the Blank）："
            ""
            "每题包含："
            "- 带空格的句子（用 _____ 表示空格）"
            "- 正确答案（可能有多个可接受答案）"
            "- 提示（可选）"
            "- 解析"
            ""
            "输出格式："
            "```json\n"
            "{\n"
            '  "question_type": "fill_blank",\n'
            '  "question": "量子比特可以同时处于 _____ 和 _____ 的叠加态。",\n'
            '  "correct_answers": ["|0⟩", "|1⟩"],\n'
            '  "hint": "提示: 量子态的标准表示法",\n'
            '  "explanation": "解析内容",\n'
            '  "difficulty": "easy",\n'
            '  "tags": ["量子比特", "基础概念"]\n'
            "}\n"
            "```"
        ),
        tools=[generate_fill_blank]
    )

    # ===== Guideline 3: Generate Short Answer Questions =====
    await quiz_gen.create_guideline(
        condition="用户请求简答题或需要深度理解测试",
        action=(
            "生成简答题（Short Answer）："
            ""
            "每题包含:"
            "- 开放性问题（需要 2-5 句话回答）"
            "- 参考答案要点"
            "- 评分标准"
            "- 解析"
            ""
            "输出格式:"
            "```json\n"
            "{\n"
            '  "question_type": "short_answer",\n'
            '  "question": "请解释量子纠缠在量子通信中的作用",\n'
            '  "key_points": [\n'
            '    "量子纠缠实现远距离关联",\n'
            '    "用于量子密钥分发",\n'
            '    "保证通信安全性"\n'
            "  ],\n"
            '  "rubric": "包含2个以上要点得满分",\n'
            '  "explanation": "解析内容",\n'
            '  "difficulty": "hard",\n'
            '  "tags": ["量子纠缠", "应用"]\n'
            "}\n"
            "```"
        ),
        tools=[generate_short_answer]
    )

    # ===== Guideline 4: Adaptive Difficulty =====
    await quiz_gen.create_guideline(
        condition="用户有答题历史",
        action=(
            "基于用户历史表现调整难度："
            ""
            "分析策略："
            "1. 统计用户在各知识点的正确率"
            "2. 识别薄弱知识点（正确率 < 60%）"
            "3. 优先生成薄弱知识点的题目"
            "4. 动态调整难度:"
            "   - 正确率 > 80%: 提升难度"
            "   - 正确率 60-80%: 维持难度"
            "   - 正确率 < 60%: 降低难度"
            ""
            "确保用户在挑战区（Zone of Proximal Development）学习。"
        ),
        tools=[analyze_weak_points, adaptive_difficulty]
    )

    # ===== Guideline 5: Question Distribution =====
    await quiz_gen.create_guideline(
        condition="生成测验题集时",
        action=(
            "合理分配题型和难度："
            ""
            "默认配比（10题为例）："
            "- 选择题: 5题（2 easy + 2 medium + 1 hard）"
            "- 填空题: 3题（1 easy + 2 medium）"
            "- 简答题: 2题（1 medium + 1 hard）"
            ""
            "确保全面考察理解、记忆、应用、分析能力。"
        ),
        tools=[generate_mcq, generate_fill_blank, generate_short_answer]
    )

    # ===== Guideline 6: Provide Detailed Explanations =====
    await quiz_gen.create_guideline(
        condition="生成每道题时",
        action=(
            "为每道题提供详细解析："
            ""
            "解析应包含："
            "1. 正确答案及原因"
            "2. 常见错误及原因"
            "3. 相关知识点补充"
            "4. 记忆技巧或助记词"
            ""
            "帮助用户不仅知道答案，还理解原理。"
        ),
        tools=[]
    )

    # ===== Guideline 7: Bloom's Taxonomy =====
    await quiz_gen.create_guideline(
        condition="生成题目时",
        action=(
            "基于布鲁姆分类法（Bloom's Taxonomy）设计题目："
            ""
            "- 记忆（Remember）: 定义、术语识别"
            "- 理解（Understand）: 解释、举例"
            "- 应用（Apply）: 使用概念解决问题"
            "- 分析（Analyze）: 比较、分解"
            "- 评估（Evaluate）: 判断、批评"
            "- 创造（Create）: 设计、构建"
            ""
            "确保题目层次丰富，全面测试认知水平。"
        ),
        tools=[generate_mcq, generate_fill_blank, generate_short_answer]
    )

    # ===== Guideline 8: Distractor Design (for MCQ) =====
    await quiz_gen.create_guideline(
        condition="生成选择题时",
        action=(
            "设计有效的干扰项（Distractors）："
            ""
            "干扰项应该："
            "1. 看起来合理（不明显错误）"
            "2. 代表常见误解"
            "3. 基于相关概念（不是随机词汇）"
            "4. 难度递进（从明显错误到容易混淆）"
            ""
            "避免:"
            "- 使用'以上都是'、'以上都不是'"
            "- 选项长度差异过大"
            "- 明显的错误选项"
        ),
        tools=[generate_mcq]
    )

    # ===== Guideline 9: Performance Feedback =====
    await quiz_gen.create_guideline(
        condition="用户完成测验后",
        action=(
            "生成个性化反馈报告："
            ""
            "📊 测验报告"
            "- 总分: X/Y"
            "- 正确率: Z%"
            "- 各知识点得分:"
            "  - 知识点A: ✅ 熟练"
            "  - 知识点B: ⚠️ 需加强"
            "  - 知识点C: ❌ 薄弱"
            ""
            "💡 学习建议:"
            "1. 建议复习: [薄弱知识点]"
            "2. 推荐阅读: [相关文档章节]"
            "3. 下次复习时间: [日期]"
        ),
        tools=[analyze_weak_points, update_quiz_history]
    )

    return quiz_gen

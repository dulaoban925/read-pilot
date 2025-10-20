"""
LLM calling tools for various tasks
"""
from parlant import tool, ToolContext, ToolResult
from typing import List, Dict, Optional
from config import settings
import openai
import anthropic


async def _call_openai(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7
) -> str:
    """Call OpenAI API"""
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model=model or settings.DEFAULT_MODEL,
        messages=messages,
        temperature=temperature
    )

    return response.choices[0].message.content


async def _call_anthropic(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: str = "claude-3-sonnet-20240229",
    temperature: float = 0.7
) -> str:
    """Call Anthropic Claude API"""
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    response = await client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt or "",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )

    return response.content[0].text


@tool
async def generate_hierarchical_summary(
    context: ToolContext,
    text: str,
    detail_level: str = "medium"
) -> ToolResult:
    """
    Generate hierarchical summary

    Args:
        context: Parlant tool context
        text: Text to summarize
        detail_level: 'low', 'medium', or 'high'

    Returns:
        Hierarchical summary
    """
    user_style = context.variables.get("summary_style", "concise")

    prompt = f"""
请对以下文本生成结构化摘要：

文本:
{text[:4000]}  # Limit text length

要求:
1. 一句话概要（Abstract）- 20字内精炼总结
2. 核心要点（Key Insights）- 3-5个主要观点
3. 重要概念解释（Concepts）- 关键术语和定义
4. 典型例子（Examples）- 具体案例或应用

用户偏好风格: {user_style}
详细程度: {detail_level}

输出JSON格式。
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        # Store in context
        context.variables["last_summary"] = response

        return ToolResult(success=True, data={"summary": response})

    except Exception as e:
        return ToolResult(success=False, message=f"摘要生成失败: {str(e)}")


@tool
async def generate_technical_summary(
    context: ToolContext,
    text: str
) -> ToolResult:
    """Generate technical/academic summary"""

    prompt = f"""
请对以下技术/学术文档生成专业摘要：

文本:
{text[:4000]}

要求:
1. 研究背景和问题
2. 方法论和实验设计
3. 主要发现和结果
4. 结论和未来方向

保持专业术语，不过度简化。输出JSON格式。
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        return ToolResult(success=True, data={"summary": response})

    except Exception as e:
        return ToolResult(success=False, message=f"技术摘要生成失败: {str(e)}")


@tool
async def generate_narrative_summary(
    context: ToolContext,
    text: str
) -> ToolResult:
    """Generate narrative/news summary"""

    prompt = f"""
请对以下叙事类/新闻类文本生成通俗摘要：

文本:
{text[:4000]}

要求:
1. 主要事件和情节
2. 关键人物和角色
3. 时间线和因果关系
4. 影响和意义

使用易懂的表达，避免专业术语。输出JSON格式。
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        return ToolResult(success=True, data={"summary": response})

    except Exception as e:
        return ToolResult(success=False, message=f"叙事摘要生成失败: {str(e)}")


@tool
async def generate_answer(
    context: ToolContext,
    question: str,
    passages: Optional[List[Dict]] = None
) -> ToolResult:
    """Generate answer based on context passages"""

    if passages is None:
        passages = context.variables.get("retrieved_passages", [])

    conversation_history = context.variables.get("conversation_history", [])[-3:]

    context_text = "\n\n".join([p.get("text", "") for p in passages])
    history_text = "\n".join([
        f"{h['role']}: {h['message']}" for h in conversation_history
    ])

    prompt = f"""
基于以下文档内容回答用户问题：

相关文档段落:
{context_text}

对话历史:
{history_text}

用户问题: {question}

要求:
1. 基于文档内容准确回答
2. 如果文档中找不到答案，诚实说明
3. 提供详细解释
4. 引用具体段落
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        return ToolResult(success=True, data={"answer": response})

    except Exception as e:
        return ToolResult(success=False, message=f"答案生成失败: {str(e)}")


@tool
async def generate_follow_up_questions(
    context: ToolContext,
    question: str,
    answer: str
) -> ToolResult:
    """Generate follow-up questions"""

    prompt = f"""
基于以下问答，生成1-2个引导性的延伸问题：

原问题: {question}
回答: {answer}

要求:
- 延伸问题应探索相关概念
- 帮助用户深入思考
- 具有启发性

输出格式: JSON数组
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        return ToolResult(success=True, data={"questions": response})

    except Exception as e:
        return ToolResult(success=False, message=f"问题生成失败: {str(e)}")


@tool
async def deep_dive_answer(
    context: ToolContext,
    follow_up: str
) -> ToolResult:
    """Generate deep-dive answer for follow-up questions"""

    conversation_history = context.variables.get("conversation_history", [])[-5:]
    history_text = "\n".join([
        f"{h['role']}: {h['message']}" for h in conversation_history
    ])

    prompt = f"""
基于对话历史，对用户的追问进行深入解释：

对话历史:
{history_text}

用户追问: {follow_up}

要求:
- 基于上文深入展开
- 提供更多细节或例子
- 保持连贯性
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        return ToolResult(success=True, data={"answer": response})

    except Exception as e:
        return ToolResult(success=False, message=f"深入解答失败: {str(e)}")


@tool
async def extract_key_concepts(
    context: ToolContext,
    text: str,
    max_concepts: int = 10
) -> ToolResult:
    """Extract key concepts from text"""

    prompt = f"""
从以下文本中提取关键概念和定义：

文本:
{text[:4000]}

要求:
- 提取核心概念（不超过{max_concepts}个）
- 为每个概念提供简洁定义
- 输出JSON格式: {{"concepts": [{{"name": "概念名", "definition": "定义"}}]}}
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        return ToolResult(success=True, data={"concepts": response})

    except Exception as e:
        return ToolResult(success=False, message=f"概念提取失败: {str(e)}")


@tool
async def create_flashcards(
    context: ToolContext,
    concepts: List[Dict],
    target_count: int = 10
) -> ToolResult:
    """Create Anki-style flashcards"""

    concepts_text = "\n".join([
        f"- {c['name']}: {c.get('definition', '')}" for c in concepts
    ])

    prompt = f"""
基于以下概念，生成{target_count}张知识卡片（Flashcards）：

概念:
{concepts_text}

要求:
每张卡片包含:
- front: 问题或提示
- back: 答案或解释
- difficulty: easy/medium/hard
- tags: 分类标签

输出JSON数组格式。
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        context.variables["generated_flashcards"] = response

        return ToolResult(success=True, data={"flashcards": response})

    except Exception as e:
        return ToolResult(success=False, message=f"卡片生成失败: {str(e)}")


@tool
async def generate_markdown_notes(
    context: ToolContext,
    text: str
) -> ToolResult:
    """Generate structured markdown notes"""

    prompt = f"""
将以下内容转化为结构化的Markdown笔记：

内容:
{text[:4000]}

要求格式:
## 核心概念
## 关键公式/定义
## 重要关系图
## 记忆要点
## 标签

使用清晰的Markdown格式。
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        return ToolResult(success=True, data={"notes": response})

    except Exception as e:
        return ToolResult(success=False, message=f"笔记生成失败: {str(e)}")


@tool
async def generate_mcq(
    context: ToolContext,
    text: str,
    num_questions: int = 5,
    difficulty: str = "medium"
) -> ToolResult:
    """Generate multiple choice questions"""

    weak_topics = context.variables.get("weak_topics", [])

    prompt = f"""
基于以下内容生成{num_questions}道选择题：

内容:
{text[:4000]}

难度: {difficulty}
重点关注主题: {", ".join(weak_topics) if weak_topics else "全部内容"}

每题包含:
- question: 问题描述
- options: {{A, B, C, D}}
- correct_answer: 正确选项
- explanation: 详细解析
- difficulty: easy/medium/hard
- tags: 知识点标签

输出JSON数组格式。
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        return ToolResult(success=True, data={"questions": response})

    except Exception as e:
        return ToolResult(success=False, message=f"选择题生成失败: {str(e)}")


@tool
async def generate_fill_blank(
    context: ToolContext,
    text: str,
    num_questions: int = 3
) -> ToolResult:
    """Generate fill-in-the-blank questions"""

    prompt = f"""
基于以下内容生成{num_questions}道填空题：

内容:
{text[:4000]}

每题包含:
- question: 带空格的句子（用 _____ 表示）
- correct_answers: 正确答案（数组）
- hint: 提示（可选）
- explanation: 解析
- difficulty: easy/medium/hard
- tags: 知识点标签

输出JSON数组格式。
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        return ToolResult(success=True, data={"questions": response})

    except Exception as e:
        return ToolResult(success=False, message=f"填空题生成失败: {str(e)}")


@tool
async def generate_short_answer(
    context: ToolContext,
    text: str,
    num_questions: int = 2
) -> ToolResult:
    """Generate short answer questions"""

    prompt = f"""
基于以下内容生成{num_questions}道简答题：

内容:
{text[:4000]}

每题包含:
- question: 开放性问题
- key_points: 参考答案要点（数组）
- rubric: 评分标准
- explanation: 解析
- difficulty: medium/hard
- tags: 知识点标签

输出JSON数组格式。
"""

    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            response = await _call_openai(prompt)
        else:
            response = await _call_anthropic(prompt)

        return ToolResult(success=True, data={"questions": response})

    except Exception as e:
        return ToolResult(success=False, message=f"简答题生成失败: {str(e)}")

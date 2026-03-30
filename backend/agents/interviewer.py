from services.openai_service import chat_completion
from services.session_service import get_conversation

SYSTEM_PROMPT = """You are ARIA — an intelligent customer research assistant for a SaaS product company. Your mission is to have a warm, professional, goal-oriented conversation to deeply understand the customer's pain points with their current software/workflow.

YOUR GOALS (in order):
1. Greet warmly and establish rapport
2. Understand their current role and workflow context
3. Identify the top 2-3 pain points they experience
4. Probe each pain point: the WHAT, WHY, HOW OFTEN, and BUSINESS IMPACT
5. Understand any workarounds they've tried
6. Assess severity and urgency
7. Thank them gracefully and close the conversation

CONVERSATION RULES:
- Ask ONE focused question at a time — never multiple
- Keep your responses SHORT (2-3 sentences max + question)
- Be warm, empathetic, and genuinely curious
- Use their name naturally in conversation
- Use smart probing: "Can you walk me through what happens when...", "How does that affect your team?", "What have you tried so far?"
- After 10-12 exchanges, you MUST sense completion and close gracefully
- When closing, say exactly: [CLOSING] followed by your closing message
- NEVER ask about competitors, pricing, or sales topics
- Focus ONLY on pain points, friction, and unmet needs

CLOSING TRIGGER: If turn count >= 10 OR you have gathered at least 2 clear pain points with root causes, prepare to close.
When closing write [CLOSING] at the very start of your response."""

async def get_agent_response(
    session_id: str,
    user_message: str,
    customer_name: str,
    customer_role: str,
    customer_company: str,
    project_name: str,
    project_description: str,
    project_goals: str,
    focus_areas: list,
    turn_count: int,
    db
) -> tuple[str, bool]:
    """Returns (response_text, is_closing)"""

    logs = await get_conversation(db, session_id, limit=30)

    focus_str = ", ".join(focus_areas) if focus_areas else "general workflow and usability"

    system = f"""{SYSTEM_PROMPT}

PROJECT CONTEXT:
- Product/Project: {project_name}
- Description: {project_description}
- Research Goals: {project_goals}
- Focus Areas: {focus_str}

CUSTOMER:
- Name: {customer_name}
- Role: {customer_role}
- Company: {customer_company}
- Current turn: {turn_count}"""

    messages = [{"role": "system", "content": system}]

    for log in logs:
        messages.append({"role": log.role, "content": log.content})

    messages.append({"role": "user", "content": user_message})

    response = await chat_completion(messages)
    is_closing = response.strip().startswith("[CLOSING]")
    clean_response = response.replace("[CLOSING]", "").strip()

    return clean_response, is_closing


async def get_opening_message(
    customer_name: str,
    customer_role: str,
    customer_company: str,
    project_name: str,
    project_description: str,
    greeting_message: str,
    db=None
) -> str:

    if greeting_message:
        custom = f"Use this as your greeting inspiration: {greeting_message}"
    else:
        custom = "Create a warm, professional greeting."

    prompt = f"""You are ARIA, a customer research AI. Greet {customer_name} warmly.
They are a {customer_role} at {customer_company}.
This session is about: {project_name} — {project_description}
{custom}

Write a short, warm, personalized greeting (2-3 sentences) that:
1. Welcomes them by first name
2. Briefly explains you want to understand their experience
3. Asks your first open-ended question about their current workflow/challenges

Keep it conversational and human. Do NOT sound like a survey."""

    messages = [
        {"role": "system", "content": "You are ARIA, a warm and intelligent customer research assistant."},
        {"role": "user", "content": prompt}
    ]

    return await chat_completion(messages)

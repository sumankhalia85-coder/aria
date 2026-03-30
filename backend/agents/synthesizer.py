import json
from services.openai_service import chat_completion
from services.session_service import get_conversation
from models.schemas import UXBriefOutput, PainPoint, UXRequirement, ArchitectureNote

SYSTEM_PROMPT = """You are a Senior UX Research Analyst and Solution Architect. Analyze this customer interview and produce a comprehensive UX brief.

Return ONLY valid JSON matching this exact schema:
{
  "pain_points": [
    {
      "title": "Short descriptive title",
      "description": "Detailed description of the pain point",
      "severity": "critical|high|medium|low",
      "frequency": "daily|weekly|occasionally|rarely",
      "root_cause": "The underlying root cause",
      "business_impact": "Impact on the business or users"
    }
  ],
  "root_causes": ["List of fundamental root causes identified"],
  "severity_map": {
    "critical": ["pain point titles"],
    "high": ["pain point titles"],
    "medium": ["pain point titles"],
    "low": ["pain point titles"]
  },
  "user_journey": [
    "Step 1: Customer does X...",
    "Step 2: They encounter Y friction...",
    "Step 3: They workaround by..."
  ],
  "ux_requirements": [
    {
      "category": "navigation|interaction|information|performance|accessibility",
      "requirement": "Specific UX requirement",
      "priority": "must-have|should-have|nice-to-have",
      "rationale": "Why this requirement exists based on the interview"
    }
  ],
  "architecture_notes": [
    {
      "area": "API|Database|Integration|Security|Performance|Infrastructure",
      "finding": "What was discovered",
      "recommendation": "Technical recommendation",
      "priority": "critical|high|medium|low"
    }
  ],
  "recommended_solutions": [
    "Specific, actionable solution recommendation"
  ],
  "executive_summary": "3-4 paragraph executive summary covering: who was interviewed, key pain points found, severity, recommended next steps for UX and engineering teams"
}

Rules:
- pain_points: 2-5 items grounded in the conversation
- ux_requirements: 4-8 specific, actionable requirements
- architecture_notes: 2-5 technical findings
- recommended_solutions: 3-6 specific solutions
- Be specific and grounded — no generic recommendations
- Return ONLY the JSON object"""


async def synthesize_ux_brief(
    session_id: str,
    customer_name: str,
    customer_role: str,
    customer_company: str,
    project_name: str,
    project_description: str,
    db
) -> UXBriefOutput:

    logs = await get_conversation(db, session_id, limit=100)
    if not logs:
        raise ValueError("No conversation to synthesize")

    transcript = "\n".join([f"[{l.role.upper()}]: {l.content}" for l in logs])

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""Customer: {customer_name} ({customer_role} at {customer_company})
Project: {project_name}
Description: {project_description}

Full Interview Transcript:
{transcript}

Generate the complete UX brief JSON."""}
    ]

    raw = await chat_completion(messages, json_mode=True)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])

    return UXBriefOutput(
        pain_points=[PainPoint(**p) for p in data.get("pain_points", [])],
        root_causes=data.get("root_causes", []),
        severity_map=data.get("severity_map", {}),
        user_journey=data.get("user_journey", []),
        ux_requirements=[UXRequirement(**u) for u in data.get("ux_requirements", [])],
        architecture_notes=[ArchitectureNote(**a) for a in data.get("architecture_notes", [])],
        recommended_solutions=data.get("recommended_solutions", []),
        executive_summary=data.get("executive_summary", "")
    )

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    industry: str = "SaaS"
    goals: str = ""
    focus_areas: List[str] = []
    greeting_message: str = ""
    max_turns: int = 12

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    industry: str
    goals: str
    focus_areas: List[str]
    greeting_message: str
    max_turns: int
    is_active: bool
    created_at: Optional[datetime] = None

class SessionStart(BaseModel):
    project_id: str
    customer_name: str
    customer_role: str = ""
    customer_company: str = ""

class ChatMessage(BaseModel):
    session_id: str
    message: str

class PainPoint(BaseModel):
    title: str = Field(description="Short title of the pain point")
    description: str = Field(description="Detailed description")
    severity: str = Field(description="critical/high/medium/low")
    frequency: str = Field(description="daily/weekly/occasionally/rarely")
    root_cause: str = Field(description="Underlying root cause")
    business_impact: str = Field(description="Impact on business/users")

class UXRequirement(BaseModel):
    category: str = Field(description="navigation/interaction/information/performance/accessibility")
    requirement: str
    priority: str = Field(description="must-have/should-have/nice-to-have")
    rationale: str

class ArchitectureNote(BaseModel):
    area: str = Field(description="Technical area: API/Database/Integration/Security/Performance")
    finding: str
    recommendation: str
    priority: str

class UXBriefOutput(BaseModel):
    pain_points: List[PainPoint]
    root_causes: List[str]
    severity_map: dict
    user_journey: List[str]
    ux_requirements: List[UXRequirement]
    architecture_notes: List[ArchitectureNote]
    recommended_solutions: List[str]
    executive_summary: str

from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Boolean
from sqlalchemy.sql import func
from core.database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    industry = Column(String, default="SaaS")
    goals = Column(Text, default="")
    focus_areas = Column(JSON, default=list)
    greeting_message = Column(Text, default="")
    max_turns = Column(Integer, default=12)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CustomerSession(Base):
    __tablename__ = "customer_sessions"
    id = Column(String, primary_key=True)
    project_id = Column(String, index=True)
    customer_name = Column(String)
    customer_role = Column(String, default="")
    customer_company = Column(String, default="")
    status = Column(String, default="active")  # active, completed
    turn_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    id = Column(String, primary_key=True)
    session_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class UXReport(Base):
    __tablename__ = "ux_reports"
    id = Column(String, primary_key=True)
    session_id = Column(String, index=True, unique=True)
    project_id = Column(String, index=True)
    customer_name = Column(String)
    customer_role = Column(String)
    customer_company = Column(String)
    pain_points = Column(JSON)
    root_causes = Column(JSON)
    severity_map = Column(JSON)
    user_journey = Column(JSON)
    ux_requirements = Column(JSON)
    architecture_notes = Column(JSON)
    executive_summary = Column(Text)
    recommended_solutions = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

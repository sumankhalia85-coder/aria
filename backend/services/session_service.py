import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.db_models import Project, CustomerSession, ConversationLog, UXReport
from models.schemas import UXBriefOutput

async def create_project(db: AsyncSession, data) -> Project:
    project = Project(id=str(uuid.uuid4()), **data.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

async def get_project(db: AsyncSession, project_id: str) -> Optional[Project]:
    r = await db.execute(select(Project).where(Project.id == project_id))
    return r.scalar_one_or_none()

async def list_projects(db: AsyncSession) -> List[Project]:
    r = await db.execute(select(Project).where(Project.is_active == True).order_by(Project.created_at.desc()))
    return r.scalars().all()

async def create_session(db: AsyncSession, project_id: str, customer_name: str,
                         customer_role: str, customer_company: str) -> CustomerSession:
    session = CustomerSession(
        id=str(uuid.uuid4()), project_id=project_id,
        customer_name=customer_name, customer_role=customer_role,
        customer_company=customer_company
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

async def get_session(db: AsyncSession, session_id: str) -> Optional[CustomerSession]:
    r = await db.execute(select(CustomerSession).where(CustomerSession.id == session_id))
    return r.scalar_one_or_none()

async def increment_turn(db: AsyncSession, session_id: str):
    session = await get_session(db, session_id)
    if session:
        session.turn_count += 1
        await db.commit()

async def complete_session(db: AsyncSession, session_id: str):
    from datetime import datetime, timezone
    session = await get_session(db, session_id)
    if session:
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        await db.commit()

async def add_message(db: AsyncSession, session_id: str, role: str, content: str) -> ConversationLog:
    log = ConversationLog(id=str(uuid.uuid4()), session_id=session_id, role=role, content=content)
    db.add(log)
    await db.commit()
    return log

async def get_conversation(db: AsyncSession, session_id: str, limit: int = 50) -> List[ConversationLog]:
    r = await db.execute(
        select(ConversationLog).where(ConversationLog.session_id == session_id)
        .order_by(ConversationLog.timestamp.asc()).limit(limit)
    )
    return r.scalars().all()

async def save_report(db: AsyncSession, session_id: str, project_id: str,
                      customer: CustomerSession, brief: UXBriefOutput) -> UXReport:
    existing = await db.execute(select(UXReport).where(UXReport.session_id == session_id))
    report = existing.scalar_one_or_none()
    data = dict(
        project_id=project_id,
        customer_name=customer.customer_name,
        customer_role=customer.customer_role,
        customer_company=customer.customer_company,
        pain_points=[p.model_dump() for p in brief.pain_points],
        root_causes=brief.root_causes,
        severity_map=brief.severity_map,
        user_journey=brief.user_journey,
        ux_requirements=[u.model_dump() for u in brief.ux_requirements],
        architecture_notes=[a.model_dump() for a in brief.architecture_notes],
        executive_summary=brief.executive_summary,
        recommended_solutions=brief.recommended_solutions,
    )
    if report:
        for k, v in data.items():
            setattr(report, k, v)
    else:
        report = UXReport(id=str(uuid.uuid4()), session_id=session_id, **data)
        db.add(report)
    await db.commit()
    await db.refresh(report)
    return report

async def get_report(db: AsyncSession, session_id: str) -> Optional[UXReport]:
    r = await db.execute(select(UXReport).where(UXReport.session_id == session_id))
    return r.scalar_one_or_none()

async def list_reports(db: AsyncSession, project_id: str) -> List[UXReport]:
    r = await db.execute(
        select(UXReport).where(UXReport.project_id == project_id)
        .order_by(UXReport.created_at.desc())
    )
    return r.scalars().all()

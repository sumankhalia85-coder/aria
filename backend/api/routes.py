import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.orchestrator import orchestrator
from models.schemas import ProjectCreate, SessionStart, ChatMessage
from services.session_service import (
    create_project, list_projects, get_project,
    get_session, get_conversation, get_report, list_reports
)
from services.pdf_service import build_ux_report

router = APIRouter()

# ── ADMIN: Projects ─────────────────────────────────────────

@router.post("/projects")
async def create_project_route(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    try:
        project = await create_project(db, data)
        return {"id": project.id, "name": project.name, "message": "Project created"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/projects")
async def get_projects(db: AsyncSession = Depends(get_db)):
    projects = await list_projects(db)
    return [{"id": p.id, "name": p.name, "description": p.description,
             "industry": p.industry, "focus_areas": p.focus_areas,
             "max_turns": p.max_turns, "created_at": p.created_at} for p in projects]

@router.get("/projects/{project_id}")
async def get_project_route(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return {
        "id": project.id, "name": project.name, "description": project.description,
        "industry": project.industry, "goals": project.goals,
        "focus_areas": project.focus_areas, "greeting_message": project.greeting_message,
        "max_turns": project.max_turns
    }

# ── CUSTOMER: Sessions ───────────────────────────────────────

@router.post("/sessions/start")
async def start_session(data: SessionStart, db: AsyncSession = Depends(get_db)):
    try:
        return await orchestrator.start_session(
            db, data.project_id, data.customer_name,
            data.customer_role, data.customer_company
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/sessions/chat")
async def chat(data: ChatMessage, db: AsyncSession = Depends(get_db)):
    try:
        return await orchestrator.chat(db, data.session_id, data.message)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/sessions/voice")
async def voice_chat(
    session_id: str = Form(...),
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        audio_bytes = await audio.read()
        return await orchestrator.voice_chat(db, session_id, audio_bytes)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/sessions/{session_id}")
async def get_session_route(session_id: str, db: AsyncSession = Depends(get_db)):
    session = await get_session(db, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return {
        "id": session.id, "project_id": session.project_id,
        "customer_name": session.customer_name, "customer_role": session.customer_role,
        "customer_company": session.customer_company, "status": session.status,
        "turn_count": session.turn_count
    }

@router.get("/sessions/{session_id}/conversation")
async def get_conversation_route(session_id: str, db: AsyncSession = Depends(get_db)):
    logs = await get_conversation(db, session_id)
    return [{"role": l.role, "content": l.content, "timestamp": l.timestamp} for l in logs]

# ── REPORTS ──────────────────────────────────────────────────

@router.post("/reports/generate/{session_id}")
async def generate_report(session_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await orchestrator.generate_report(db, session_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/reports/{session_id}")
async def get_report_route(session_id: str, db: AsyncSession = Depends(get_db)):
    report = await get_report(db, session_id)
    if not report:
        raise HTTPException(404, "Report not found")
    return {
        "session_id": session_id, "customer_name": report.customer_name,
        "customer_role": report.customer_role, "customer_company": report.customer_company,
        "pain_points": report.pain_points, "root_causes": report.root_causes,
        "severity_map": report.severity_map, "user_journey": report.user_journey,
        "ux_requirements": report.ux_requirements, "architecture_notes": report.architecture_notes,
        "recommended_solutions": report.recommended_solutions,
        "executive_summary": report.executive_summary
    }

@router.get("/reports/export/pdf/{session_id}")
async def export_pdf(session_id: str, db: AsyncSession = Depends(get_db)):
    report = await get_report(db, session_id)
    if not report:
        raise HTTPException(404, "No report found. Generate report first.")
    try:
        pdf_bytes = build_ux_report(report)
        return Response(
            content=pdf_bytes, media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=ux_brief_{session_id[:8]}.pdf"}
        )
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/admin/reports/{project_id}")
async def list_project_reports(project_id: str, db: AsyncSession = Depends(get_db)):
    reports = await list_reports(db, project_id)
    return [{
        "session_id": r.session_id, "customer_name": r.customer_name,
        "customer_role": r.customer_role, "customer_company": r.customer_company,
        "pain_points_count": len(r.pain_points or []),
        "created_at": r.created_at
    } for r in reports]

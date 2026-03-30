from sqlalchemy.ext.asyncio import AsyncSession
from agents.interviewer import get_agent_response, get_opening_message
from agents.synthesizer import synthesize_ux_brief
from services.session_service import (
    create_session, get_session, get_project,
    add_message, increment_turn, complete_session,
    save_report, get_report
)
from services.openai_service import text_to_speech, transcribe_audio
import base64

class PainPointOrchestrator:

    async def start_session(self, db: AsyncSession, project_id: str, customer_name: str,
                            customer_role: str, customer_company: str) -> dict:
        project = await get_project(db, project_id)
        if not project:
            raise ValueError("Project not found")

        session = await create_session(db, project_id, customer_name, customer_role, customer_company)

        opening = await get_opening_message(
            customer_name, customer_role, customer_company,
            project.name, project.description, project.greeting_message
        )

        await add_message(db, session.id, "assistant", opening)

        # Generate TTS for opening
        audio_b64 = None
        try:
            audio_bytes = await text_to_speech(opening)
            audio_b64 = base64.b64encode(audio_bytes).decode()
        except Exception:
            pass

        return {
            "session_id": session.id,
            "opening_message": opening,
            "audio_base64": audio_b64,
            "max_turns": project.max_turns
        }

    async def chat(self, db: AsyncSession, session_id: str, user_message: str) -> dict:
        session = await get_session(db, session_id)
        if not session:
            raise ValueError("Session not found")
        if session.status == "completed":
            raise ValueError("Session already completed")

        project = await get_project(db, session.project_id)
        if not project:
            raise ValueError("Project not found")

        await add_message(db, session_id, "user", user_message)
        await increment_turn(db, session_id)

        # Refresh turn count
        session = await get_session(db, session_id)

        response, is_closing = await get_agent_response(
            session_id=session_id,
            user_message=user_message,
            customer_name=session.customer_name,
            customer_role=session.customer_role,
            customer_company=session.customer_company,
            project_name=project.name,
            project_description=project.description,
            project_goals=project.goals,
            focus_areas=project.focus_areas or [],
            turn_count=session.turn_count,
            db=db
        )

        await add_message(db, session_id, "assistant", response)

        # Auto-complete if closing
        if is_closing or session.turn_count >= project.max_turns:
            await complete_session(db, session_id)

        # TTS
        audio_b64 = None
        try:
            audio_bytes = await text_to_speech(response)
            audio_b64 = base64.b64encode(audio_bytes).decode()
        except Exception:
            pass

        return {
            "session_id": session_id,
            "response": response,
            "audio_base64": audio_b64,
            "is_closing": is_closing or session.turn_count >= project.max_turns,
            "turn_count": session.turn_count
        }

    async def voice_chat(self, db: AsyncSession, session_id: str, audio_bytes: bytes) -> dict:
        transcript = await transcribe_audio(audio_bytes)
        result = await self.chat(db, session_id, transcript)
        result["transcript"] = transcript
        return result

    async def generate_report(self, db: AsyncSession, session_id: str) -> dict:
        session = await get_session(db, session_id)
        if not session:
            raise ValueError("Session not found")

        project = await get_project(db, session.project_id)

        brief = await synthesize_ux_brief(
            session_id, session.customer_name, session.customer_role,
            session.customer_company, project.name, project.description, db
        )

        report = await save_report(db, session_id, session.project_id, session, brief)

        return {
            "session_id": session_id,
            "report_id": report.id,
            "pain_points": [p.model_dump() for p in brief.pain_points],
            "root_causes": brief.root_causes,
            "severity_map": brief.severity_map,
            "user_journey": brief.user_journey,
            "ux_requirements": [u.model_dump() for u in brief.ux_requirements],
            "architecture_notes": [a.model_dump() for a in brief.architecture_notes],
            "recommended_solutions": brief.recommended_solutions,
            "executive_summary": brief.executive_summary,
            "customer_name": session.customer_name,
            "customer_role": session.customer_role,
            "customer_company": session.customer_company,
        }

    async def get_report(self, db: AsyncSession, session_id: str):
        return await get_report(db, session_id)

orchestrator = PainPointOrchestrator()

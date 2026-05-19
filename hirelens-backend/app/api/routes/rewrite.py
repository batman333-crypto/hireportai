"""Resume rewrite endpoints."""
from fastapi import APIRouter, HTTPException
from app.models.request_models import RewriteRequest
from app.schemas.requests import ResumeChatRequest
from app.models.response_models import RewriteResponse
from app.services.nlp import extract_job_requirements, extract_skills
from app.services.keywords import match_keywords

router = APIRouter()


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_resume(body: RewriteRequest) -> RewriteResponse:
    """Generate an ATS-optimized rewrite tailored to the candidate's resume."""
    try:
        from app.services.gpt_service import generate_resume_rewrite
    except ImportError:
        raise HTTPException(status_code=501, detail="GPT service not available.")

    resume_skills = extract_skills(body.resume_text)
    resume_data = {
        "full_text": body.resume_text,
        "skills": resume_skills,
        "sections": {},
    }
    jd_requirements = extract_job_requirements(body.job_description)
    jd_skills = jd_requirements.get("all_skills", [])

    keyword_results = match_keywords(
        resume_text=body.resume_text,
        jd_text=body.job_description,
        jd_skills=jd_skills,
    )
    missing_keywords = keyword_results.get("missing", [])

    resume_skills_lower = {s.lower() for s in resume_skills}
    missing_skills = [s for s in jd_skills if s.lower() not in resume_skills_lower]

    try:
        result = generate_resume_rewrite(
            resume_data,
            jd_requirements,
            missing_keywords=missing_keywords,
            missing_skills=missing_skills,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rewrite failed: {str(e)}")


@router.post("/rewrite/chat", response_model=RewriteResponse)
async def chat_edit_resume(body: ResumeChatRequest) -> RewriteResponse:
    """Apply a conversational edit instruction to the current resume.

    Accepts the current resume JSON, a user message, and optional job description.
    Returns the updated resume with only the requested change applied.
    """
    try:
        from app.services.gpt_service import chat_resume_edit
    except ImportError:
        raise HTTPException(status_code=501, detail="GPT service not available.")

    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        result = chat_resume_edit(
            current_resume=body.current_resume,
            message=body.message,
            job_description=body.job_description,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat edit failed: {str(e)}")

"""Recruiter Roast / Red Team route — cynical recruiter audit."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.nlp import extract_job_requirements, extract_skills
from app.services.red_team import run_red_team

router = APIRouter()


class RedTeamRequest(BaseModel):
    resume_text: str = Field(..., min_length=50)
    job_description: str = Field(..., min_length=20)


@router.post("/red-team")
async def red_team(body: RedTeamRequest):
    """Run a cynical recruiter pass over the resume + JD and return red flags."""
    try:
        resume_data = {
            "full_text": body.resume_text,
            "skills": extract_skills(body.resume_text),
        }
        jd_requirements = extract_job_requirements(body.job_description)
        return run_red_team(resume_data, jd_requirements)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Red team failed: {str(e)}")

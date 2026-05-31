"""LinkedIn About audit — public viral hook (no signup)."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.linkedin_audit import audit_linkedin_about

router = APIRouter()


class LinkedInAuditRequest(BaseModel):
    about_text: str = Field(..., min_length=1, max_length=4000)


@router.post("/linkedin-audit")
async def linkedin_audit(body: LinkedInAuditRequest):
    """Score a LinkedIn About section like a cynical recruiter. No auth required."""
    return audit_linkedin_about(body.about_text)

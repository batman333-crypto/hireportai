"""ATS Diagnosis endpoint — full 4-area resume diagnostic."""
from fastapi import APIRouter, HTTPException

from app.schemas.requests import DiagnosisRequest
from app.schemas.responses import DiagnosisResponse

router = APIRouter()


@router.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose_resume(body: DiagnosisRequest) -> DiagnosisResponse:
    """Run a deep ATS diagnostic on the resume against the job description.

    Returns:
    - ats_killers: formatting/parsing issues that trigger auto-rejection
    - section_diagnosis: weakest item per section with fix
    - missing_signals: keywords / credentials absent for the role
    - top_fixes: ranked XYZ-formula rewrites with before/after
    """
    from app.services.gpt_service import generate_ats_diagnosis

    try:
        return generate_ats_diagnosis(
            resume_text=body.resume_text,
            job_description=body.job_description,
            target_role=body.target_role,
            industry=body.industry,
            seniority=body.seniority,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Diagnosis failed: {exc}")

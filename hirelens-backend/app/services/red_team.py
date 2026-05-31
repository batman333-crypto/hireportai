"""Recruiter Roast / Red Team service.

Runs a cynical recruiter pass over a resume + JD and returns red flags
the user must fix before submitting. Negative feedback is the moat.
"""
import json
from typing import Any, Dict, List

from app.services.gpt_service import _generate
from app.services.seniority import infer_seniority


def run_red_team(resume_data: Dict[str, Any], jd_requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Have a cynical recruiter try to reject the resume. Returns structured red flags."""
    resume_text = (resume_data.get("full_text") or "")[:5000]
    jd_title = jd_requirements.get("job_title", "the role")
    required_skills = ", ".join(jd_requirements.get("required_skills", [])[:15])
    seniority = infer_seniority(resume_data)

    prompt = f"""You are a CYNICAL Fortune 500 recruiter who screens 400 resumes a day for a {jd_title} role.
You are paid to REJECT, not accept. Your bonus depends on your reject rate.
Read this resume against the job description and surface every red flag a hiring manager would catch in 6 seconds.

Be brutal. Be specific. Be quotable. Do NOT be polite.

CANDIDATE TIER: {seniority['tier'].upper()} (~{seniority['yoe']} YoE)
TARGET ROLE: {jd_title}
REQUIRED SKILLS: {required_skills}

═══ THINGS TO HUNT FOR ═══
1. Unverifiable / fabricated metrics ("increased revenue 300%" with no baseline)
2. Career gaps with no explanation
3. Title inflation vs YoE mismatch
4. Buzzword salad ("passionate", "team player", "results-driven", "synergy")
5. Missing quantification (bullets with no numbers, %, $, or scope)
6. Job hopping without context (< 12 months at multiple recent roles)
7. Skill gaps vs required skills for this specific JD
8. Weak action verbs ("responsible for", "helped with", "worked on")
9. Outdated tech for the role (e.g., jQuery for a senior React role)
10. Tier mismatch (e.g., a "Senior Lead Architect" with 2 YoE, or no leadership signal at director tier)
11. Formatting / readability issues (walls of text, no quantification, uneven structure)
12. Missing must-have credentials (degree, certification, clearance)

═══ RESUME ═══
{resume_text}

═══ OUTPUT (JSON ONLY) ═══
{{
  "reject_probability": 0.0-1.0,
  "verdict": "PASS" | "BORDERLINE" | "REJECT",
  "cynical_summary": "1-3 sentence brutal summary in the voice of a recruiter who has seen 10,000 resumes",
  "red_flags": [
    {{
      "severity": "critical" | "high" | "medium" | "low",
      "category": "credibility" | "career_gap" | "title_inflation" | "buzzwords" | "quantification" | "job_hopping" | "skill_gap" | "weak_verbs" | "outdated" | "tier_mismatch" | "formatting" | "missing_credential",
      "finding": "what's wrong, in plain English",
      "recruiter_quote": "the brutal one-liner a recruiter would actually say",
      "fix_suggestion": "concrete, specific fix the candidate can apply right now"
    }}
  ],
  "top_3_fixes_to_unblock": ["fix 1", "fix 2", "fix 3"]
}}

Find AT LEAST 5 red flags. Be specific to THIS resume — no generic advice.
"""

    fallback = {
        "reject_probability": 0.55,
        "verdict": "BORDERLINE",
        "cynical_summary": "Insufficient signal to evaluate. Resume is too short or AI service unavailable — re-run after adding content.",
        "red_flags": [
            {
                "severity": "high",
                "category": "quantification",
                "finding": "Most bullets lack a number, %, or $ amount. Recruiters scan for impact in 6 seconds.",
                "recruiter_quote": "If you can't quantify it, it didn't happen.",
                "fix_suggestion": "Add a metric to every bullet — team size, %, $, users, time saved.",
            },
        ],
        "top_3_fixes_to_unblock": [
            "Quantify every bullet with a number, %, or $",
            "Cut buzzwords ('passionate', 'team player', 'results-driven')",
            "Tighten action verbs — replace 'responsible for' with a strong past-tense verb",
        ],
        "seniority": seniority,
    }

    try:
        resp = _generate(prompt, temperature=0.6, max_tokens=2500, json_mode=True)
        data = json.loads(resp)
        # Sanitize
        flags: List[Dict[str, Any]] = []
        for f in data.get("red_flags", [])[:15]:
            sev = (f.get("severity") or "medium").lower()
            if sev not in {"critical", "high", "medium", "low"}:
                sev = "medium"
            flags.append({
                "severity": sev,
                "category": f.get("category", "credibility"),
                "finding": f.get("finding", "")[:400],
                "recruiter_quote": f.get("recruiter_quote", "")[:240],
                "fix_suggestion": f.get("fix_suggestion", "")[:400],
            })
        return {
            "reject_probability": float(data.get("reject_probability") or 0.5),
            "verdict": data.get("verdict", "BORDERLINE"),
            "cynical_summary": data.get("cynical_summary", ""),
            "red_flags": flags,
            "top_3_fixes_to_unblock": data.get("top_3_fixes_to_unblock", [])[:3],
            "seniority": seniority,
        }
    except Exception:
        return fallback

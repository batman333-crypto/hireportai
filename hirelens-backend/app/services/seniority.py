"""Seniority inference + dynamic ATS scoring weights.

A 22-year CTO and a 0-year CS senior should NOT be scored on the same axes.
This module infers a seniority tier from the resume and returns a tier-specific
weight map that the scorer (and the AI rewrite prompt) can consume.
"""

import re
from datetime import date
from typing import Any, Dict, List, Tuple

SENIORITY_TIERS = ("student", "ic", "manager", "director", "executive")

# Dynamic ATS component weights per tier (sum to 100, includes Leadership Signal).
TIER_WEIGHTS: Dict[str, Dict[str, int]] = {
    "student":   {"keyword_match": 35, "skills_coverage": 30, "experience_alignment": 10, "bullet_strength": 10, "leadership_signal": 0,  "formatting": 15},
    "ic":        {"keyword_match": 35, "skills_coverage": 25, "experience_alignment": 20, "bullet_strength": 15, "leadership_signal": 5,  "formatting": 0},
    "manager":   {"keyword_match": 30, "skills_coverage": 20, "experience_alignment": 25, "bullet_strength": 15, "leadership_signal": 10, "formatting": 0},
    "director":  {"keyword_match": 25, "skills_coverage": 15, "experience_alignment": 30, "bullet_strength": 15, "leadership_signal": 15, "formatting": 0},
    "executive": {"keyword_match": 20, "skills_coverage": 10, "experience_alignment": 30, "bullet_strength": 15, "leadership_signal": 25, "formatting": 0},
}

TIER_GUIDANCE: Dict[str, str] = {
    "student":   "Lead with coursework, projects, internships, and quantified academic outcomes. Use STEM/business action verbs.",
    "ic":        "Lead with technologies owned, system scope, individual delivery metrics, and named tools.",
    "manager":   "Lead with team size, budget owned, people developed, hiring, cross-functional outcomes.",
    "director":  "Lead with org scope (headcount, $ budget), P&L outcomes, strategic initiatives, multi-team alignment.",
    "executive": "Lead with board narrative, P&L $, fundraising $, M&A activity, shareholder/exit value, headcount of 100+.",
}

EXEC_TITLE_PATTERNS = re.compile(
    r"\b(chief|cto|ceo|cfo|coo|ciso|cmo|cpo|chro|svp|evp|vp|vice president|head of|founder|president|managing director|partner)\b",
    re.IGNORECASE,
)
DIRECTOR_TITLE_PATTERNS = re.compile(r"\b(director|sr\.? director|senior director|principal)\b", re.IGNORECASE)
MANAGER_TITLE_PATTERNS = re.compile(r"\b(manager|sr\.? manager|lead|tech lead|engineering lead|team lead|head)\b", re.IGNORECASE)


_DATE_RE = re.compile(
    r"(?P<m1>jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)?\.?\s*(?P<y1>\d{4})\s*[-–to]+\s*"
    r"(?P<end>(?P<m2>jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)?\.?\s*(?P<y2>\d{4})|present|current|now)",
    re.IGNORECASE,
)


def _estimate_yoe_from_text(text: str) -> float:
    """Crude but resilient YoE estimator: scans for date ranges in the resume text."""
    if not text:
        return 0.0
    today = date.today()
    spans: List[Tuple[int, int]] = []
    for m in _DATE_RE.finditer(text):
        try:
            y1 = int(m.group("y1"))
            end = m.group("end").lower()
            if "present" in end or "current" in end or "now" in end:
                y2 = today.year
            else:
                y2 = int(m.group("y2"))
            if 1970 <= y1 <= today.year and 1970 <= y2 <= today.year + 1 and y2 >= y1:
                spans.append((y1, y2))
        except Exception:
            continue
    if not spans:
        return 0.0
    # Merge overlapping spans (cap double-counting)
    spans.sort()
    merged = [spans[0]]
    for s, e in spans[1:]:
        ls, le = merged[-1]
        if s <= le:
            merged[-1] = (ls, max(le, e))
        else:
            merged.append((s, e))
    return float(sum(e - s for s, e in merged))


def infer_seniority(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return {'tier', 'yoe', 'weights', 'guidance', 'signals'}."""
    text = (resume_data.get("full_text") or "")[:8000]
    yoe = _estimate_yoe_from_text(text)

    has_exec = bool(EXEC_TITLE_PATTERNS.search(text))
    has_director = bool(DIRECTOR_TITLE_PATTERNS.search(text))
    has_manager = bool(MANAGER_TITLE_PATTERNS.search(text))

    if has_exec or yoe >= 22:
        tier = "executive"
    elif has_director or yoe >= 15:
        tier = "director"
    elif has_manager or yoe >= 8:
        tier = "manager"
    elif yoe >= 3:
        tier = "ic"
    else:
        tier = "student"

    return {
        "tier": tier,
        "yoe": round(yoe, 1),
        "weights": TIER_WEIGHTS[tier],
        "guidance": TIER_GUIDANCE[tier],
        "signals": {
            "has_exec_title": has_exec,
            "has_director_title": has_director,
            "has_manager_title": has_manager,
        },
    }


def render_seniority_block(seniority: Dict[str, Any]) -> str:
    """Render a seniority context block for injection into the AI rewrite prompt."""
    w = seniority["weights"]
    return (
        f"SENIORITY TIER: {seniority['tier'].upper()} (~{seniority['yoe']} YoE)\n"
        f"TIER GUIDANCE: {seniority['guidance']}\n"
        f"DYNAMIC SCORING WEIGHTS (use these to prioritize what to optimize):\n"
        f"  • Keyword Match: {w['keyword_match']}%\n"
        f"  • Skills Coverage: {w['skills_coverage']}%\n"
        f"  • Experience Alignment: {w['experience_alignment']}%\n"
        f"  • Bullet Strength: {w['bullet_strength']}%\n"
        f"  • Leadership Signal: {w['leadership_signal']}%\n"
    )

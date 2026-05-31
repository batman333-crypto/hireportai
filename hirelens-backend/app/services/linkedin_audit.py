"""LinkedIn 'About' section audit — the viral hook.

A 3-second public scan with no signup required. Returns a brutal
'Recruiter Impression Score' designed to be screenshot-shareable on LinkedIn itself.
"""
import json
import re
from typing import Any, Dict

from app.services.gpt_service import _generate

BUZZWORDS = {
    "passionate", "results-driven", "team player", "self-starter", "go-getter",
    "synergy", "synergies", "thought leader", "thought leadership",
    "guru", "ninja", "rockstar", "wizard", "best of breed", "outside the box",
    "game changer", "game-changer", "value add", "value-add", "core competency",
    "leverage", "leveraging", "circle back", "deep dive", "low hanging fruit",
    "move the needle", "drive results", "results oriented", "results-oriented",
    "hard worker", "detail oriented", "detail-oriented", "proven track record",
    "dynamic", "motivated", "innovative", "strategic thinker",
}


def _heuristic_score(text: str) -> Dict[str, Any]:
    """Fast deterministic baseline score (works even when AI is unavailable)."""
    t = (text or "").strip()
    if len(t) < 30:
        return {
            "score": 0,
            "verdict": "Too short — recruiters expect at least 80 words.",
            "buzzword_count": 0,
            "buzzwords_found": [],
            "has_quantification": False,
            "word_count": len(t.split()),
        }

    lower = t.lower()
    buzzwords_found = sorted({b for b in BUZZWORDS if b in lower})
    word_count = len(re.findall(r"\b\w+\b", t))
    numbers = re.findall(r"(\$\d|\d+%|\d{2,})", t)
    has_quant = len(numbers) >= 2

    score = 100
    score -= min(40, len(buzzwords_found) * 7)         # buzzwords are death
    if not has_quant:
        score -= 20
    if word_count < 80:
        score -= 15
    if word_count > 350:
        score -= 10
    if t.count("I ") + t.count("my ") < 2:
        score -= 5  # too detached
    score = max(5, min(100, score))

    if score >= 85:
        verdict = "Strong. A recruiter would read this in full."
    elif score >= 65:
        verdict = "Solid foundation. Cut the fluff and quantify more."
    elif score >= 45:
        verdict = "Recruiter eye-roll territory. Too many buzzwords, not enough proof."
    else:
        verdict = "Hard pass in 6 seconds. Rewrite from scratch."

    return {
        "score": score,
        "verdict": verdict,
        "buzzword_count": len(buzzwords_found),
        "buzzwords_found": buzzwords_found[:8],
        "has_quantification": has_quant,
        "word_count": word_count,
    }


def audit_linkedin_about(text: str) -> Dict[str, Any]:
    """Score a LinkedIn About section like a cynical recruiter."""
    base = _heuristic_score(text)

    if len(text or "") < 30:
        return {
            **base,
            "top_issues": ["Section is too short — write at least 80 words."],
            "top_strengths": [],
            "rewritten_first_sentence": "",
            "shareable_summary": f"LinkedIn About Score: {base['score']}/100 — too short to evaluate.",
        }

    prompt = f"""You are a cynical Fortune 500 recruiter. Read this LinkedIn 'About' section and judge it in 6 seconds.

═══ ABOUT SECTION ═══
{text[:2000]}

═══ HEURISTIC FLAGS ═══
- Word count: {base['word_count']}
- Buzzwords found: {", ".join(base['buzzwords_found']) or "none"}
- Quantification present: {base['has_quantification']}

Return STRICT JSON:
{{
  "top_issues": ["3 specific things wrong, in plain English"],
  "top_strengths": ["1-3 things that DO work"],
  "rewritten_first_sentence": "a punchy, quantified rewrite of their opening line — no buzzwords",
  "shareable_summary": "one tweetable line the user could screenshot ('Recruiter Impression Score: 47/100. ...')"
}}
Be brutal. Be specific. No generic advice."""

    try:
        resp = _generate(prompt, temperature=0.6, max_tokens=900, json_mode=True)
        data = json.loads(resp)
        return {
            **base,
            "top_issues": data.get("top_issues", [])[:5],
            "top_strengths": data.get("top_strengths", [])[:3],
            "rewritten_first_sentence": data.get("rewritten_first_sentence", "")[:400],
            "shareable_summary": data.get("shareable_summary", f"LinkedIn About Score: {base['score']}/100"),
        }
    except Exception:
        return {
            **base,
            "top_issues": [
                f"{base['buzzword_count']} buzzwords detected" if base['buzzwords_found'] else "Generic phrasing throughout",
                "Missing quantification — no numbers, %, or $" if not base['has_quantification'] else "Could use more specific outcomes",
                "Opens with passive description instead of a hook",
            ],
            "top_strengths": [],
            "rewritten_first_sentence": "",
            "shareable_summary": f"LinkedIn About Score: {base['score']}/100 — {base['verdict']}",
        }

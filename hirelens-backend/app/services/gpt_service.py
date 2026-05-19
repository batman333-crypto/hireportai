"""Google Gemini service for AI-powered resume optimization features."""
import json
from typing import Any, Dict, List, Optional

from app.models.response_models import (
    CoverLetterResponse,
    InterviewPrepResponse,
    InterviewQuestion,
    RewriteEntry,
    RewriteHeader,
    RewriteResponse,
    RewriteSection,
)


def _get_client():
    """Lazy-load the Gemini client."""
    try:
        from google import genai
        from app.config import get_settings
        settings = get_settings()
        if not settings.gemini_api_key:
            return None, None
        client = genai.Client(api_key=settings.gemini_api_key)
        return client, settings.gemini_model
    except Exception:
        return None, None


def _extract_json(text: str) -> str:
    """Strip markdown code fences and extract raw JSON from model output."""
    import re as _re
    text = text.strip()
    # Strip ```json ... ``` or ``` ... ``` wrappers
    fenced = _re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if fenced:
        return fenced.group(1).strip()
    # Find the outermost { ... } block
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text


def _generate(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    json_mode: bool = False,
) -> str:
    """Send a prompt to Gemini and return the response text."""
    from google.genai import types

    client, model_name = _get_client()
    if client is None:
        raise RuntimeError("Gemini API key not configured")

    config_kwargs: Dict[str, Any] = {
        "temperature": temperature,
        "max_output_tokens": max_tokens,
    }
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    raw = response.text or ""
    # Always clean JSON output so markdown fences never break parsing
    if json_mode:
        raw = _extract_json(raw)
    return raw


def generate_job_fit_explanation(
    resume_data: Dict[str, Any],
    jd_requirements: Dict[str, Any],
    ats_score: int,
    matched_keywords: List[str],
    missing_keywords: List[str],
) -> Dict[str, Any]:
    """Generate a natural language job fit explanation."""
    prompt = f"""You are an expert career coach and ATS specialist. Analyze how well a candidate's resume matches a job description and provide a clear, honest assessment.

Resume Skills: {', '.join(resume_data.get('skills', [])[:20])}
Resume Sections: {list(resume_data.get('sections', {}).keys())}
JD Required Skills: {', '.join(jd_requirements.get('required_skills', [])[:20])}
JD Title: {jd_requirements.get('job_title', 'N/A')}
ATS Score: {ats_score}/100
Matched Keywords: {', '.join(matched_keywords[:15])}
Missing Keywords: {', '.join(missing_keywords[:15])}

Respond with a JSON object containing:
1. "explanation": A 2-3 sentence honest assessment of fit (150-200 words)
2. "top_strengths": Array of exactly 3 specific strengths as short strings
3. "top_gaps": Array of exactly 3 specific gaps/improvements as short strings
4. "improvement_plan": A 3-step 30-day action plan as array of strings

Be specific, direct, and constructive. Focus on actionable insights."""

    try:
        response_text = _generate(prompt, temperature=0.6, max_tokens=800, json_mode=True)
        data = json.loads(response_text)
        return {
            "explanation": data.get("explanation", ""),
            "top_strengths": data.get("top_strengths", [])[:3],
            "top_gaps": data.get("top_gaps", [])[:3],
            "improvement_plan": data.get("improvement_plan", []),
        }
    except Exception:
        return {
            "explanation": (
                f"Your resume shows {ats_score}% ATS compatibility with this role. "
                f"You matched {len(matched_keywords)} key terms but are missing {len(missing_keywords)} "
                "important keywords. Focus on incorporating the missing skills into your experience descriptions."
            ),
            "top_strengths": matched_keywords[:3] if matched_keywords else ["Technical background", "Relevant experience", "Education"],
            "top_gaps": missing_keywords[:3] if missing_keywords else ["Keyword optimization needed"],
            "improvement_plan": [
                "Add missing keywords naturally into your experience bullets",
                "Quantify your achievements with specific metrics",
                "Ensure your skills section covers all required technologies",
            ],
        }


def generate_resume_rewrite(
    resume_data: Dict[str, Any],
    jd_requirements: Dict[str, Any],
    template_type: str = "general",
    major: Optional[str] = None,
    missing_keywords: Optional[List[str]] = None,
    missing_skills: Optional[List[str]] = None,
) -> RewriteResponse:
    """Generate an ATS-optimized rewrite of the resume.

    Automatically analyzes the resume content to determine the best structure
    and sections. Returns structured data (header, sections with typed entries)
    so the frontend can render a properly formatted resume.
    """
    resume_text = resume_data.get("full_text", "")[:4000]
    resume_skills = resume_data.get("skills", [])
    jd_skills = ", ".join(jd_requirements.get("all_skills", [])[:30])
    jd_title = jd_requirements.get("job_title", "the role")
    required_skills = ", ".join(jd_requirements.get("required_skills", [])[:20])
    responsibilities = jd_requirements.get("responsibilities", [])[:10]

    # Build gap analysis context for the AI
    missing_kw_str = ", ".join((missing_keywords or [])[:30])
    missing_sk_str = ", ".join((missing_skills or [])[:20])
    resume_sk_str = ", ".join(resume_skills[:30])
    resp_str = "\n".join(f"- {r}" for r in responsibilities) if responsibilities else "N/A"

    prompt = f"""You are an elite ATS optimization expert and professional resume writer. Rewrite this resume to achieve the HIGHEST POSSIBLE ATS score for the target role while keeping it on ONE PAGE.

═══ ATS SCORING CRITERIA ═══

1. KEYWORD MATCH (35%): Weave EVERY missing keyword below into bullets and the skills section using exact phrasing.
   MISSING KEYWORDS: [{missing_kw_str}]

2. SKILLS COVERAGE (25%): The skills section is machine-parsed. Add every plausible missing skill.
   HAVE: [{resume_sk_str}]
   ADD: [{missing_sk_str}]
   → Infer adjacent skills from context: Python user likely knows Git, pip, venv; React dev likely knows HTML/CSS/JS; team lead likely has Agile, Project Management.

3. EXPERIENCE ALIGNMENT (20%): Frame every bullet to mirror the JD's language and responsibilities. Reword experience to speak directly to what the employer is hiring for.

4. FORMATTING (10%): Single column, standard headings, no tables/graphics. ATS parsers fail on complex layouts.

5. BULLET STRENGTH (10%): Action verb + specific task + quantified result + JD keyword. Every bullet.

═══ JOB CONTEXT ═══

TARGET ROLE: {jd_title}
ALL JD SKILLS: {jd_skills}
REQUIRED SKILLS: {required_skills}
KEY RESPONSIBILITIES:
{resp_str}

═══ ONE-PAGE RULES (CRITICAL) ═══

This resume MUST fit on a single page. To achieve this:
- MAX 3-4 bullets per experience entry (keep each under 120 characters)
- Education: org + degree + GPA + 1 line of relevant coursework (no more)
- Projects: 2 bullets each maximum
- Skills: single-line categories, no redundancy
- Omit sections with no content relevant to this role
- Prioritize: EXPERIENCE > SKILLS > EDUCATION > PROJECTS > LEADERSHIP (reorder for the role)

═══ FORMAT (matching professional UT-style template) ═══

Header: Name (centered, bold) + contact line (phone | email | linkedin | City, State)
Sections: Bold underlined header left-aligned, company bold + date right-aligned, title italic
Bullets: •  action verb + task + metric + keyword (no period at end)

═══ CRITICAL RULES ═══

1. NEVER FABRICATE new jobs, degrees, or projects. Only reword what EXISTS in the original.
2. REAL DATA ONLY: Extract name, email, phone, LinkedIn, GPA from the original. Never use placeholders.
3. ORG NAMES: Copy exactly from original resume.
4. METRICS: If original says "improved X", you may add "by ~20-30%" if reasonable context supports it.
5. SKILLS SECTION: Group by category (e.g., "Programming: Python, SQL, R | Tools: Excel, Tableau | Soft Skills: Leadership, Communication").
6. ENTRIES use "entries" array. SKILLS/HONORS use "content" string.

═══ JSON OUTPUT ═══

{{
  "header": {{"name": "Full Name", "contact": "phone | email | linkedin | City, State"}},
  "sections": [
    {{"title": "EDUCATION", "content": "", "entries": [{{"org": "University Name, City, State", "date": "May 2027", "title": "Bachelor of Science in Major, GPA: X.XX", "details": ["Relevant Coursework: Course1, Course2"], "bullets": []}}]}},
    {{"title": "EXPERIENCE", "content": "", "entries": [{{"org": "Company Name, City, State", "date": "June 2023 – Present", "title": "Job Title", "details": [], "bullets": ["Led development of X using Python and AWS, reducing processing time by 35% and saving 10 engineering hours weekly", "Implemented Y algorithm resulting in 20% improvement in Z metric"]}}]}},
    {{"title": "SKILLS", "content": "Programming Languages: Python, Java, SQL | Frameworks: React, FastAPI | Tools: Git, Docker, AWS | Soft Skills: Leadership, Agile, Communication", "entries": []}}
  ],
  "full_text": "Complete resume as plain text (same content as structured data above)"
}}

═══ ORIGINAL RESUME ═══

{resume_text}"""

    ai_output = ""
    try:
        ai_output = _generate(prompt, temperature=0.4, max_tokens=6000, json_mode=True)
        data = json.loads(ai_output)

        header = RewriteHeader(
            name=data.get("header", {}).get("name", ""),
            contact=data.get("header", {}).get("contact", ""),
        )

        sections = []
        for s in data.get("sections", []):
            entries = []
            for e in s.get("entries", []):
                bullets = e.get("bullets", [])
                if bullets and isinstance(bullets[0], dict):
                    bullets = [b.get("text", str(b)) for b in bullets]
                entries.append(RewriteEntry(
                    org=e.get("org", ""),
                    location=e.get("location", ""),
                    date=e.get("date", ""),
                    title=e.get("title", ""),
                    bullets=[str(b) for b in bullets],
                    details=[str(d) for d in e.get("details", [])],
                ))
            sections.append(RewriteSection(
                title=s.get("title", ""),
                content=s.get("content", ""),
                entries=entries,
            ))

        if not sections:
            sections = _parse_plain_text_to_sections(data.get("full_text", resume_text))

        return RewriteResponse(
            header=header,
            sections=sections,
            full_text=data.get("full_text", resume_text),
            template_type=template_type,
        )
    except Exception:
        # Use the AI's raw output (even if not valid JSON) so the user sees
        # the rewritten content, not just their original resume.
        fallback_text = ai_output if ai_output.strip() else resume_text
        # Strip any leftover JSON syntax so it reads as plain text
        import re as _re
        fallback_text = _re.sub(r'^\s*\{.*?"full_text"\s*:\s*"', '', fallback_text, flags=_re.DOTALL)
        fallback_text = fallback_text.strip().strip('"').strip()
        if not fallback_text or len(fallback_text) < 50:
            fallback_text = resume_text
        return RewriteResponse(
            header=RewriteHeader(),
            sections=[],          # empty → frontend uses PlainTextFallback
            full_text=fallback_text,
            template_type=template_type,
        )


def _parse_plain_text_to_sections(text: str) -> List[RewriteSection]:
    """Convert plain-text resume into structured RewriteSection list."""
    import re as _re
    SECTION_HEADERS = {
        "EDUCATION", "EXPERIENCE", "WORK EXPERIENCE", "PROJECTS",
        "SKILLS", "TECHNICAL SKILLS", "LEADERSHIP", "LEADERSHIP EXPERIENCE",
        "LEADERSHIP & COMMUNITY INVOLVEMENT", "LEADERSHIP EXPERIENCE AND ACTIVITIES",
        "CAMPUS INVOLVEMENT", "COMMUNITY INVOLVEMENT", "HONORS", "HONORS & AWARDS",
        "AWARDS", "CERTIFICATIONS", "RESEARCH", "RESEARCH EXPERIENCE",
        "VOLUNTEER", "VOLUNTEER EXPERIENCE", "ACTIVITIES",
    }

    lines = text.split("\n")
    sections: List[RewriteSection] = []
    current_title = ""
    current_lines: List[str] = []
    name_line = ""
    contact_line = ""

    # Try to extract header (first 3 non-empty lines before first section)
    header_lines = []
    first_section_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.upper() in SECTION_HEADERS or any(stripped.upper().startswith(h) for h in SECTION_HEADERS):
            first_section_idx = i
            break
        if stripped:
            header_lines.append(stripped)

    if header_lines:
        name_line = header_lines[0] if header_lines else ""
        contact_line = " | ".join(header_lines[1:3]) if len(header_lines) > 1 else ""

    def flush():
        if current_title and current_lines:
            content = "\n".join(current_lines).strip()
            sections.append(RewriteSection(title=current_title, content=content, entries=[]))

    for line in lines[first_section_idx:]:
        stripped = line.strip()
        if not stripped:
            continue
        upper = stripped.upper()
        if upper in SECTION_HEADERS or any(upper == h for h in SECTION_HEADERS):
            flush()
            current_title = stripped.upper()
            current_lines = []
        else:
            current_lines.append(stripped)
    flush()

    # Build a dummy header section so the name/contact renders
    if name_line and not any(s.title == "HEADER" for s in sections):
        sections.insert(0, RewriteSection(
            title="__HEADER__",
            content=f"{name_line}\n{contact_line}",
            entries=[],
        ))

    return sections if sections else [RewriteSection(title="RESUME", content=text, entries=[])]


def generate_cover_letter(
    resume_data: Dict[str, Any],
    jd_requirements: Dict[str, Any],
    tone: str = "professional",
) -> CoverLetterResponse:
    """Generate a personalized cover letter following a professional format."""
    resume_text = resume_data.get("full_text", "")[:2500]
    jd_title = jd_requirements.get("job_title", "this role")
    required_skills = ", ".join(jd_requirements.get("required_skills", [])[:15])
    all_skills = ", ".join(jd_requirements.get("all_skills", [])[:20])

    tone_instructions = {
        "professional": "formal and polished, using professional business language",
        "confident": "assertive and direct, highlighting achievements boldly without arrogance",
        "conversational": "warm and personable, showing personality while remaining professional",
    }
    tone_desc = tone_instructions.get(tone, tone_instructions["professional"])

    prompt = f"""You are a professional career coach. Write a cover letter following this EXACT template format.

CANDIDATE RESUME:
---
{resume_text}
---

TARGET ROLE: {jd_title}
REQUIRED SKILLS: {required_skills}
JD KEYWORDS: {all_skills}
TONE: {tone_desc}

OUTPUT THIS EXACT FORMAT (fill in real data, no placeholders or brackets):

[Candidate's Full Name]
[City, State] | [Phone] | [Email] | [LinkedIn URL]

[Today's Date written as: Month Day, Year]

Dear Hiring Manager,

[INTRO PARAGRAPH - 3-4 sentences: Who you are, what role you're applying for, why you're excited about this specific position. If relevant, mention your major/degree and how it connects to the role.]

[MIDDLE PARAGRAPH - 4-5 sentences: Highlight 2-3 specific experiences from your resume with concrete examples. Show how your transferable and technical skills match the job requirements. Use specific numbers/metrics where possible. Do NOT copy resume bullets verbatim — expand on them.]

[CLOSING PARAGRAPH - 2-3 sentences: Summarize your qualifications, reiterate interest in the role, express enthusiasm about contributing to the team. Thank them for considering your application.]

Respectfully yours,

[Candidate's Full Name]

RULES:
- Extract the candidate's REAL name, contact info from the resume. NO placeholders.
- Tone: {tone_desc}
- Length: 250-350 words (body only, not counting header/sign-off)
- No generic filler ("I am a hard worker", "I am passionate")
- Only reference real experiences from the resume
- Make it specific to the target role and required skills
- End with "Respectfully yours," followed by the candidate's name"""

    try:
        cover_letter = _generate(prompt, temperature=0.7, max_tokens=900)
        return CoverLetterResponse(cover_letter=cover_letter.strip(), tone=tone)
    except Exception:
        return CoverLetterResponse(
            cover_letter=(
                f"Dear Hiring Manager,\n\nI am writing to express my strong interest in the {jd_title} position. "
                f"My background aligns well with the requirements you have outlined, particularly in {required_skills[:100]}. "
                "I am eager to bring my expertise to your team and contribute meaningfully to your organization's goals.\n\n"
                "Throughout my career, I have consistently delivered results through my technical expertise and collaborative approach. "
                "I have developed strong competencies that directly align with the skills your team is seeking, and I am confident "
                "these experiences position me well for this opportunity.\n\n"
                "I would welcome the opportunity to further discuss how my skills and experiences align with your team's goals. "
                "Thank you for your time and consideration.\n\nSincerely,\nThe Applicant"
            ),
            tone=tone,
        )


def generate_interview_questions(
    resume_data: Dict[str, Any],
    jd_requirements: Dict[str, Any],
) -> InterviewPrepResponse:
    """Generate likely interview questions with STAR method frameworks."""
    resume_text = resume_data.get("full_text", "")[:1500]
    jd_title = jd_requirements.get("job_title", "this role")
    required_skills = ", ".join(jd_requirements.get("required_skills", [])[:10])

    prompt = f"""Generate 10 likely interview questions for a candidate applying for the role of {jd_title}.
The role requires: {required_skills}
Candidate background: {resume_text[:800]}

For each question, provide a STAR method answer framework (guidance on what to cover, not a full answer).

Return a JSON object:
{{
  "questions": [
    {{
      "question": "The interview question",
      "star_framework": "Situation: ... | Task: ... | Action: ... | Result: ..."
    }}
  ]
}}

Mix: behavioral (3), technical (4), situational (2), culture fit (1).
Make questions specific to the role and candidate's background."""

    try:
        response_text = _generate(prompt, temperature=0.7, max_tokens=2000, json_mode=True)
        data = json.loads(response_text)
        questions = [
            InterviewQuestion(question=q["question"], star_framework=q["star_framework"])
            for q in data.get("questions", [])[:10]
        ]
        return InterviewPrepResponse(questions=questions)
    except Exception:
        default_questions = [
            InterviewQuestion(
                question=f"Tell me about your experience with {required_skills.split(',')[0].strip() if required_skills else 'your main technical stack'}.",
                star_framework="Situation: Describe a specific project | Task: Your role and the challenge | Action: Technologies used and decisions made | Result: Impact and learnings",
            ),
            InterviewQuestion(
                question="Describe a time you had to learn a new technology quickly.",
                star_framework="Situation: The project requiring new tech | Task: What you needed to learn | Action: Learning approach and resources | Result: How quickly you became productive",
            ),
            InterviewQuestion(
                question="Tell me about your most challenging technical project.",
                star_framework="Situation: Project complexity and constraints | Task: Your specific responsibilities | Action: Problem-solving approach | Result: Outcome and impact",
            ),
            InterviewQuestion(
                question="How do you handle disagreements with team members about technical decisions?",
                star_framework="Situation: A specific disagreement | Task: Finding the right solution | Action: Communication and compromise | Result: Team outcome",
            ),
            InterviewQuestion(
                question="Where do you see yourself in 5 years?",
                star_framework="Focus on growth in this field, leadership aspirations, and alignment with company mission",
            ),
        ]
        return InterviewPrepResponse(questions=default_questions)


def chat_resume_edit(
    current_resume: dict,
    message: str,
    job_description: str = "",
) -> "RewriteResponse":
    """Apply a conversational edit instruction to the current resume.

    The user can say things like:
    - "Add a bullet about my Python experience in the software role"
    - "Remove the honors section"
    - "Make the experience section more focused on data analysis"
    - "Change my GPA to 3.7"
    - "Add SQL to my skills"

    Returns an updated RewriteResponse.
    """
    import json as _json

    # Serialize the current resume to a readable format for the prompt
    resume_json = _json.dumps(current_resume, indent=2)

    prompt = f"""You are an expert resume editor. The user has an ATS-optimized resume and wants to make a specific change.

CURRENT RESUME (JSON structure):
{resume_json}

JOB DESCRIPTION CONTEXT:
{job_description[:1000] if job_description else "Not provided"}

USER REQUEST:
"{message}"

Apply EXACTLY what the user requested — nothing more, nothing less. Preserve all other content.

Rules:
1. Only change what the user asked for. Keep everything else identical.
2. Maintain ATS-friendly formatting (action verbs, metrics, keywords).
3. Keep the resume to ONE PAGE worth of content.
4. If the user asks to add a skill, add it to the appropriate skills category.
5. If the user asks to add a bullet, make it start with an action verb and include a metric where possible.
6. If the user asks to remove something, delete it completely.
7. NEVER invent new jobs, companies, or degrees.

Return the COMPLETE updated resume in the exact same JSON structure:
{{
  "header": {{"name": "...", "contact": "..."}},
  "sections": [...],
  "full_text": "complete plain text version"
}}"""

    try:
        response_text = _generate(prompt, temperature=0.3, max_tokens=4000, json_mode=True)
        data = _json.loads(response_text)

        header = RewriteHeader(
            name=data.get("header", {}).get("name", current_resume.get("header", {}).get("name", "")),
            contact=data.get("header", {}).get("contact", current_resume.get("header", {}).get("contact", "")),
        )

        sections = []
        for s in data.get("sections", []):
            entries = []
            for e in s.get("entries", []):
                entries.append(RewriteEntry(
                    org=e.get("org", ""),
                    location=e.get("location", ""),
                    date=e.get("date", ""),
                    title=e.get("title", ""),
                    bullets=e.get("bullets", []),
                    details=e.get("details", []),
                ))
            sections.append(RewriteSection(
                title=s.get("title", ""),
                content=s.get("content", ""),
                entries=entries,
            ))

        return RewriteResponse(
            header=header,
            sections=sections,
            full_text=data.get("full_text", ""),
            template_type=current_resume.get("template_type", "general"),
        )
    except Exception:
        # Return current resume unchanged on failure
        sections = []
        for s in current_resume.get("sections", []):
            entries = [
                RewriteEntry(**e) for e in s.get("entries", [])
            ]
            sections.append(RewriteSection(
                title=s.get("title", ""),
                content=s.get("content", ""),
                entries=entries,
            ))
        return RewriteResponse(
            header=RewriteHeader(**current_resume.get("header", {})),
            sections=sections,
            full_text=current_resume.get("full_text", ""),
            template_type=current_resume.get("template_type", "general"),
        )


def rewrite_bullets_gpt(
    bullets: List[str],
    jd_text: str,
) -> List[str]:
    """Use Gemini to rewrite resume bullet points for maximum ATS impact."""
    if not bullets:
        return []

    bullets_formatted = "\n".join(f"- {b}" for b in bullets[:10])

    prompt = f"""Rewrite these resume bullet points to maximize ATS compatibility and hiring manager appeal.

ORIGINAL BULLETS:
{bullets_formatted}

JOB CONTEXT: {jd_text[:500]}

Rules:
1. Start each bullet with a strong past-tense action verb
2. Add quantification where naturally implied (%, $, team sizes, timeframes)
3. Use X-Y-Z formula: "Accomplished [X] as measured by [Y], by doing [Z]"
4. Incorporate relevant keywords from job context where they genuinely apply
5. Keep the same core facts — NEVER fabricate achievements or metrics
6. Keep each bullet under 120 characters for ATS compatibility

Return a JSON object: {{"bullets": ["rewritten bullet 1", "rewritten bullet 2", ...]}}"""

    try:
        response_text = _generate(prompt, temperature=0.5, max_tokens=1000, json_mode=True)
        data = json.loads(response_text)
        return data.get("bullets", bullets)
    except Exception:
        return bullets

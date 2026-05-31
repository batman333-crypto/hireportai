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
from app.schemas.responses import (
    ATSKiller,
    DiagnosisResponse,
    SectionDiagnosis,
    TopFix,
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

    prompt = f"""You are an elite ATS optimization expert and professional resume writer. Your job is to rewrite this resume to fill a FULL PAGE and achieve the HIGHEST POSSIBLE ATS score for the target role.

═══ ATS SCORING CRITERIA ═══

1. KEYWORD MATCH (35%): Weave EVERY missing keyword below into bullets and the skills section using exact phrasing.
   MISSING KEYWORDS: [{missing_kw_str}]

2. SKILLS COVERAGE (25%): The skills section is machine-parsed. Add every plausible missing skill.
   HAVE: [{resume_sk_str}]
   ADD: [{missing_sk_str}]
   → Infer adjacent skills from context: Python user likely knows Git, pip, venv; React dev likely knows HTML/CSS/JS; team lead likely has Agile, Project Management.

3. EXPERIENCE ALIGNMENT (20%): Frame every bullet to mirror the JD's language and responsibilities. Reword experience to speak directly to what the employer is hiring for.

4. FORMATTING (10%): Single column, standard headings, no tables/graphics. ATS parsers fail on complex layouts.

5. BULLET STRENGTH (10%): Use the Google XYZ formula for EVERY bullet: "Accomplished [X] as measured by [Y], by doing [Z]". Action verb + specific task + quantified result + JD keyword.

═══ JOB CONTEXT ═══

TARGET ROLE: {jd_title}
ALL JD SKILLS: {jd_skills}
REQUIRED SKILLS: {required_skills}
KEY RESPONSIBILITIES:
{resp_str}

═══ FULL-PAGE RULES (CRITICAL) ═══

The resume MUST fill a full US Letter page (≈55–70 lines of content). To achieve this:
- ALWAYS start with a PROFESSIONAL SUMMARY section (3–4 strong sentences tailored to the role)
- MINIMUM 5–6 bullets per experience entry — expand and enrich every bullet using the XYZ formula
- Each bullet must be 1–2 full lines long (100–150 characters), not a short fragment
- Education: org + degree + GPA (if available) + Relevant Coursework line with 6–8 courses
- Skills: expand to include ALL plausible related skills grouped into 6–8 categories
- If the resume has Projects mentioned anywhere, add them as a Projects section with 3 bullets each
- If the resume has Leadership / Activities / Certifications, include them
- Do NOT omit sections — include everything and enrich it
- Prioritize: SUMMARY > EXPERIENCE > SKILLS > EDUCATION > PROJECTS > LEADERSHIP

═══ FORMAT (matching professional template) ═══

Header: Name (centered, bold) + contact line (phone | email | linkedin | City, State)
Sections: Bold underlined header left-aligned, company bold + date right-aligned, title italic
Bullets: •  action verb + task + metric + keyword (no period at end)

═══ CRITICAL RULES ═══

1. NEVER FABRICATE new jobs, degrees, or companies. Only reword/expand what EXISTS in the original.
2. REAL DATA ONLY: Extract name, email, phone, LinkedIn, GPA from the original. Never use placeholders.
3. ORG NAMES: Copy exactly from original resume.
4. METRICS: If original says "improved X", you MUST add a specific percentage or number (e.g., "by 30%") — use reasonable estimates based on context.
5. SKILLS SECTION: Group by category (e.g., "Programming: Python, SQL, R | Tools: Excel, Tableau | Soft Skills: Leadership, Communication").
6. ENTRIES use "entries" array. SKILLS/SUMMARY/HONORS use "content" string.
7. PROFESSIONAL SUMMARY uses "content" field (no entries), 3–4 sentences.

═══ JSON OUTPUT ═══

{{
  "header": {{"name": "Full Name", "contact": "phone | email | linkedin | City, State"}},
  "sections": [
    {{"title": "PROFESSIONAL SUMMARY", "content": "Results-driven AI Engineer with 3+ years of experience building LLM-powered applications and RAG pipelines at scale. Proven track record of deploying production GenAI systems using LangChain, LlamaIndex, and vector databases that reduced manual processing time by 40%. Deep expertise in fine-tuning transformer models and architecting agentic workflows aligned with enterprise reliability standards.", "entries": []}},
    {{"title": "EXPERIENCE", "content": "", "entries": [{{"org": "Company Name, City, State", "date": "June 2023 – Present", "title": "Job Title", "details": [], "bullets": ["Architected and deployed RAG pipeline using LangChain and ChromaDB, improving document retrieval precision by 38% and reducing hallucination rate by 22% across 50K daily queries", "Led cross-functional team of 6 engineers to integrate GPT-4 and Gemini APIs into core product, cutting customer onboarding time by 45% and generating $1.2M in annual efficiency savings", "Implemented LoRA fine-tuning on Llama 3 model using QLoRA technique, achieving 91% task accuracy on domain-specific benchmarks while reducing GPU memory usage by 60%", "Designed LangGraph-based agentic workflow automating 12 financial reporting processes, eliminating 80 hours of manual work per month and reducing error rate to 0.3%", "Built evaluation framework using RAGAS and LangSmith, establishing automated regression testing that caught 94% of model degradation issues before production deployment"]}}]}},
    {{"title": "EDUCATION", "content": "", "entries": [{{"org": "University Name, City, State", "date": "May 2027", "title": "Bachelor of Science in Major, GPA: X.XX", "details": ["Relevant Coursework: Machine Learning, Deep Learning, Natural Language Processing, Data Structures, Cloud Computing, Statistics"], "bullets": []}}]}},
    {{"title": "SKILLS", "content": "GenAI & LLMs: GPT-4, Gemini, Llama 3, BERT, Claude | Agentic Frameworks: LangChain, LlamaIndex, LangGraph | RAG & Retrieval: RAG, Hybrid Search, Semantic Search | Vector Databases: ChromaDB, FAISS, Pinecone | Fine-Tuning: LoRA, QLoRA, PEFT | LLM Serving: vLLM, TGI, Ollama | Evaluation: RAGAS, LangSmith, MLflow | Programming: Python, SQL, R | Cloud & MLOps: AWS, GCP, Docker, Kubernetes | Databases: MongoDB, PostgreSQL, Redis | Data Engineering: Kafka, Spark, Airflow", "entries": []}}
  ],
  "full_text": "Complete resume as plain text (same content as structured data above)"
}}

═══ ORIGINAL RESUME ═══

{resume_text}"""

    ai_output = ""
    try:
        ai_output = _generate(prompt, temperature=0.4, max_tokens=8000, json_mode=True)
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


def generate_ats_diagnosis(
    resume_text: str,
    job_description: str,
    target_role: str = "",
    industry: str = "",
    seniority: str = "entry",
) -> DiagnosisResponse:
    """Run a brutal 4-area ATS diagnostic on the resume.

    Mirrors what enterprise ATS systems (Workday, Taleo, iCIMS, Greenhouse)
    actually penalise: formatting killers, weak bullets, missing signals, ranked fixes.
    """
    role_label = target_role or "the target role"
    industry_label = industry or "the relevant industry"
    seniority_label = seniority or "entry-level"

    prompt = f"""You are a senior ATS evaluator and resume diagnostics expert who has reviewed 10,000+ resumes for {role_label} positions across companies of every size. You think and reason like Workday, Taleo, iCIMS, and Greenhouse combined.

Your job: diagnose this resume with zero softening. Be brutally specific. Quote the candidate's ACTUAL lines back. If something is broken, say exactly what line is broken and why.

═══ RESUME ═══
{resume_text[:4000]}

═══ JOB DESCRIPTION ═══
{job_description[:2000]}

═══ CONTEXT ═══
Target Role: {role_label}
Industry: {industry_label}
Seniority: {seniority_label}

═══ YOUR DIAGNOSIS — FOUR AREAS ═══

AREA 1 — ATS-KILLERS
Formatting, parsing, or layout issues that cause auto-rejection or score burial:
- Tables, multi-column layouts, text boxes, headers/footers, graphics
- Non-standard fonts, special characters that break parsing
- Missing or ambiguous dates (ATS needs MM/YYYY or Month YYYY)
- File-type risks, missing section labels ATS expects
- Anything an ATS parser cannot extract cleanly

AREA 2 — SECTION-BY-SECTION DIAGNOSIS
For EACH section present (Summary, Experience, Skills, Education, Projects, Leadership):
- Quote the weakest bullet or sentence EXACTLY as written
- Explain precisely why it fails: no metrics, no keywords, weak verb, too vague, redundant, etc.
- Provide a single specific fix

AREA 3 — MISSING SIGNALS
What hiring managers and ATS systems for {role_label} expect to see that is ABSENT:
- Missing keywords/skills that appear in 80%+ of {role_label} job postings
- Missing quantification patterns (%, $, time saved, users impacted)
- Missing credentials, tools, methodologies for this role/seniority

AREA 4 — TOP 5 FIXES RANKED BY IMPACT
Rank by ATS score impact. For fix #1, provide a full before/after bullet rewrite using Google's XYZ formula:
"Accomplished [X] as measured by [Y], by doing [Z]"
For fixes #2-5, explain exactly what to change.

═══ JSON OUTPUT ═══

Return ONLY this JSON (no markdown, no preamble):
{{
  "ats_killers": [
    {{
      "issue": "exact issue name",
      "impact": "specific consequence on ATS scoring or parsing",
      "fix": "exact action to fix it"
    }}
  ],
  "section_diagnosis": [
    {{
      "section": "SECTION NAME",
      "weakest_item": "exact quoted line from the resume",
      "reason": "specific technical reason this fails ATS or recruiter scan",
      "fix": "exact rewrite or action"
    }}
  ],
  "missing_signals": [
    "specific keyword, metric pattern, or credential that is absent"
  ],
  "top_fixes": [
    {{
      "rank": 1,
      "title": "short action title",
      "impact": "HIGH",
      "before": "exact original line",
      "after": "XYZ-formula rewrite with action verb + metric + method",
      "why": "why this rewrite beats ATS scoring"
    }}
  ],
  "overall_verdict": "2-sentence brutal verdict: current ATS pass probability and #1 reason this resume gets buried"
}}"""

    try:
        raw = _generate(prompt, temperature=0.3, max_tokens=4000, json_mode=True)
        data = json.loads(raw)

        ats_killers = [
            ATSKiller(
                issue=k.get("issue", ""),
                impact=k.get("impact", ""),
                fix=k.get("fix", ""),
            )
            for k in data.get("ats_killers", [])
        ]

        section_diagnosis = [
            SectionDiagnosis(
                section=s.get("section", ""),
                weakest_item=s.get("weakest_item", ""),
                reason=s.get("reason", ""),
                fix=s.get("fix", ""),
            )
            for s in data.get("section_diagnosis", [])
        ]

        top_fixes = [
            TopFix(
                rank=f.get("rank", i + 1),
                title=f.get("title", ""),
                impact=f.get("impact", "MEDIUM"),
                before=f.get("before", ""),
                after=f.get("after", ""),
                why=f.get("why", ""),
            )
            for i, f in enumerate(data.get("top_fixes", []))
        ]

        return DiagnosisResponse(
            ats_killers=ats_killers,
            section_diagnosis=section_diagnosis,
            missing_signals=data.get("missing_signals", []),
            top_fixes=top_fixes,
            target_role=role_label,
            overall_verdict=data.get("overall_verdict", ""),
        )

    except Exception:
        return DiagnosisResponse(
            ats_killers=[],
            section_diagnosis=[],
            missing_signals=[],
            top_fixes=[],
            target_role=role_label,
            overall_verdict="Diagnosis failed — please try again.",
        )


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


def _rebuild_sections_from_dict(sections_raw: list) -> List[RewriteSection]:
    """Reconstruct RewriteSection list from raw dicts (for fallback paths)."""
    sections = []
    for s in (sections_raw or []):
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
    return sections


def chat_resume_edit(
    current_resume: dict,
    message: str,
    job_description: str = "",
) -> "RewriteResponse":
    """Apply a conversational edit to the current resume.

    Handles any instruction: add/remove/reword bullets, change skills,
    reformat sections, update GPA, alter tone, etc.
    """
    import json as _json

    # Build a clean plain-text view of the resume for the prompt,
    # so Gemini can reason about content without being confused by JSON escaping.
    current_full_text = current_resume.get("full_text", "")
    current_header = current_resume.get("header", {})
    current_sections_raw = current_resume.get("sections", [])

    # Also pass the compact JSON so Gemini knows the exact structure to return.
    resume_json = _json.dumps(current_resume, indent=2)[:6000]

    prompt = f"""You are a precision resume editor. Your ONLY job is to apply the user's requested change to the resume below and return the COMPLETE updated resume in JSON.

═══ CURRENT RESUME (JSON) ═══
{resume_json}

═══ USER'S REQUESTED CHANGE ═══
"{message}"

═══ JOB CONTEXT (optional) ═══
{job_description[:800] if job_description else "N/A"}

═══ HOW TO APPLY THE CHANGE ═══

Identify exactly what the user wants:
- ADD bullet → insert a new bullet starting with an action verb + metric into the right section/entry
- REMOVE bullet/section/skill → delete it entirely, leave everything else intact
- REWORD/EDIT text → change only that specific text
- ADD skill → append to the appropriate skill category in the SKILLS section content string
- CHANGE format → apply the formatting change (e.g. reorder sections, change header layout)
- CHANGE content → update only the specific field the user mentioned

═══ RULES ═══
1. Apply ONLY what was requested — do NOT rewrite or touch anything else
2. Preserve all other sections, bullets, entries, and formatting exactly as-is
3. Every bullet must start with a strong action verb (Led, Built, Designed, Implemented, Analyzed…)
4. Keep bullets under 120 characters each
5. NEVER fabricate new companies, degrees, or jobs
6. Skills section uses "content" string format: "Category: skill1, skill2 | Category2: skill3"
7. Update "full_text" to accurately reflect ALL changes in plain text form

═══ REQUIRED JSON OUTPUT ═══

Return this EXACT structure (no extra keys, no markdown fences):
{{
  "header": {{
    "name": "{current_header.get('name', 'Full Name')}",
    "contact": "{current_header.get('contact', 'phone | email | linkedin | City, State')}"
  }},
  "sections": [
    {{
      "title": "SECTION NAME",
      "content": "",
      "entries": [
        {{
          "org": "Organization Name, City, State",
          "location": "",
          "date": "Month YYYY – Month YYYY",
          "title": "Job/Degree Title",
          "details": ["Relevant Coursework: ..."],
          "bullets": [
            "Action verb + specific task + quantified result"
          ]
        }}
      ]
    }},
    {{
      "title": "SKILLS",
      "content": "Programming: Python, SQL | Tools: Git, Docker | Soft Skills: Leadership",
      "entries": []
    }}
  ],
  "full_text": "Complete resume as clean plain text — same content as sections above"
}}"""

    try:
        response_text = _generate(prompt, temperature=0.2, max_tokens=6000, json_mode=True)
        data = _json.loads(response_text)

        # Fallback header values to current if AI dropped them
        cur_h = current_resume.get("header", {})
        header = RewriteHeader(
            name=data.get("header", {}).get("name", "") or cur_h.get("name", ""),
            contact=data.get("header", {}).get("contact", "") or cur_h.get("contact", ""),
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

        # If AI returned no sections, preserve the original
        if not sections:
            sections = _rebuild_sections_from_dict(current_sections_raw)

        updated_full_text = data.get("full_text", "") or current_full_text

        return RewriteResponse(
            header=header,
            sections=sections,
            full_text=updated_full_text,
            template_type=current_resume.get("template_type", "general"),
        )

    except Exception as _exc:
        # Preserve the current resume exactly — never silently drop content
        sections = _rebuild_sections_from_dict(current_sections_raw)
        return RewriteResponse(
            header=RewriteHeader(
                name=current_header.get("name", ""),
                contact=current_header.get("contact", ""),
            ),
            sections=sections,
            full_text=current_full_text,
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

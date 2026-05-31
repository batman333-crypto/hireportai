"""Role-specific resume templates for AI-powered rewriting.

Modeled on the UT Austin Career Services resume templates / industry samples
(https://careerservices.cns.utexas.edu/resources/resumes/templates). Each
template defines the canonical section order and per-section guidance the
AI should follow when rewriting a user's resume for that role.
"""

from typing import Any, Dict, List

TEMPLATES: Dict[str, Dict[str, Any]] = {
    # ─────────────────────────────────────────────────────────────
    "technical": {
        "name": "Technical (CS / Software / Data)",
        "description": "Computer science, software engineering, and data-focused roles. Technical skills sit high so ATS picks them up immediately.",
        "sections_order": [
            "EDUCATION",
            "TECHNICAL SKILLS",
            "EXPERIENCE",
            "PROJECTS",
            "LEADERSHIP & ACTIVITIES",
        ],
        "section_guidelines": {
            "EDUCATION": "University, City, ST · graduation Month Year. Degree in {major}, GPA. Relevant Coursework: 4–6 most relevant courses.",
            "TECHNICAL SKILLS": "Place IMMEDIATELY after Education. Group as: Languages, Frameworks/Libraries, Tools/Platforms, Databases, Cloud. Use exact technology names from the JD.",
            "EXPERIENCE": "Reverse chronological. Bullets must name specific languages, frameworks, systems, and quantified impact (latency, throughput, users, $). Use action verbs: Engineered, Architected, Optimized, Deployed, Automated.",
            "PROJECTS": "Each project: name, stack in parens, 1–2 bullets describing what was built, technologies used, and measurable outcomes (stars, users, accuracy %).",
            "LEADERSHIP & ACTIVITIES": "Tech clubs, hackathons, open-source contributions.",
        },
    },
    # ─────────────────────────────────────────────────────────────
    "engineering": {
        "name": "Engineering (Mechanical / Electrical / Civil / Chemical)",
        "description": "Traditional engineering disciplines. Emphasizes technical projects, lab work, and hands-on tools.",
        "sections_order": [
            "EDUCATION",
            "RELEVANT COURSEWORK",
            "ENGINEERING EXPERIENCE",
            "PROJECTS",
            "TECHNICAL SKILLS",
            "LEADERSHIP & PROFESSIONAL SOCIETIES",
        ],
        "section_guidelines": {
            "EDUCATION": "University, City, ST · graduation Month Year. BS in {major}, GPA. Include certifications (EIT/FE/PE).",
            "RELEVANT COURSEWORK": "Comma-separated list of 6–8 advanced courses relevant to the target role.",
            "ENGINEERING EXPERIENCE": "Internships, co-ops, lab assistant roles. Bullets emphasize design cycles, simulations, testing protocols, safety/compliance, and quantified outcomes (tolerance, efficiency %, cost savings).",
            "PROJECTS": "Capstone, design competitions (FSAE, robotics, etc.). Mention CAD tools, prototyping, materials, and results.",
            "TECHNICAL SKILLS": "Software (SolidWorks, MATLAB, AutoCAD, ANSYS, LabVIEW, PSpice), Lab techniques, Manufacturing processes, Standards (ASME, IEEE, ASTM).",
            "LEADERSHIP & PROFESSIONAL SOCIETIES": "ASME, IEEE, SWE, NSBE, AIChE etc. Officer roles and project teams.",
        },
    },
    # ─────────────────────────────────────────────────────────────
    "business": {
        "name": "Business (Finance / Marketing / Management)",
        "description": "Business, finance, marketing, accounting, and general management roles.",
        "sections_order": [
            "EDUCATION",
            "EXPERIENCE",
            "LEADERSHIP & CAMPUS INVOLVEMENT",
            "SKILLS & CERTIFICATIONS",
        ],
        "section_guidelines": {
            "EDUCATION": "University, City, ST · graduation Month Year. BBA in {major}, GPA. Concentrations / minors. Study abroad if relevant.",
            "EXPERIENCE": "Bullets emphasize business outcomes: revenue, cost savings, margin, growth %, deal size, stakeholder count. Lead with action verbs (Analyzed, Negotiated, Forecasted, Pitched, Closed). Mention frameworks (DCF, SWOT, A/B testing, segmentation).",
            "LEADERSHIP & CAMPUS INVOLVEMENT": "Business fraternities, case competitions, student government, finance/marketing/consulting clubs. Quantify impact (members managed, $ raised).",
            "SKILLS & CERTIFICATIONS": "Excel (VLOOKUP, pivot tables, modeling), PowerPoint, Bloomberg, Tableau, SQL, CRM (Salesforce/HubSpot), Google Analytics. CFA/CPA progress, Series exams, languages.",
        },
    },
    # ─────────────────────────────────────────────────────────────
    "consulting": {
        "name": "Consulting (Strategy / Management)",
        "description": "Management consulting, strategy, and advisory roles. Emphasis on quantified impact, leadership, and case-style storytelling.",
        "sections_order": [
            "EDUCATION",
            "EXPERIENCE",
            "LEADERSHIP",
            "ADDITIONAL",
        ],
        "section_guidelines": {
            "EDUCATION": "University, City, ST · graduation Month Year. Degree, GPA, standardized test scores (GMAT/GRE if strong). Honors. Case competition wins go HERE if prestigious.",
            "EXPERIENCE": "MBB-style bullets: led/owned a workstream → analytical method → quantified business impact. Format: 'Action verb + scope + method + result ($/% impact).' Each bullet should sound like a mini case study. Highlight client-facing work, executive presentations, and team leadership.",
            "LEADERSHIP": "Team captain roles, founder of initiative, club president. Show ownership, scale (people/budget managed), and outcome.",
            "ADDITIONAL": "Languages (with fluency), certifications, interests (sports, travel — useful for consulting fit conversations).",
        },
    },
    # ─────────────────────────────────────────────────────────────
    "education": {
        "name": "Education (Teaching / EdTech / Curriculum)",
        "description": "Teaching, tutoring, curriculum design, and education-sector roles.",
        "sections_order": [
            "EDUCATION",
            "CERTIFICATIONS & LICENSURE",
            "TEACHING EXPERIENCE",
            "RELATED EXPERIENCE",
            "PROFESSIONAL DEVELOPMENT",
            "SKILLS",
        ],
        "section_guidelines": {
            "EDUCATION": "University, City, ST · graduation Month Year. BS/BA/M.Ed in {major}, GPA. Student teaching placements.",
            "CERTIFICATIONS & LICENSURE": "State teaching certification, grade levels, subject endorsements, ESL/SPED, CPR.",
            "TEACHING EXPERIENCE": "Reverse chronological. School, City, ST. Grade level / subject. Bullets cover lesson planning, differentiated instruction, classroom management, assessment data, parent communication, and measurable student outcomes (test score growth %, attendance).",
            "RELATED EXPERIENCE": "Tutoring, camp counselor, after-school programs, TA roles.",
            "PROFESSIONAL DEVELOPMENT": "Workshops, conferences, PLCs.",
            "SKILLS": "Curriculum frameworks (Common Core, TEKS), LMS (Canvas, Schoology, Google Classroom), assessment tools, languages.",
        },
    },
    # ─────────────────────────────────────────────────────────────
    "healthcare": {
        "name": "Healthcare / Pre-Health",
        "description": "Pre-med, nursing, public health, and clinical roles. Emphasizes clinical hours and patient care.",
        "sections_order": [
            "EDUCATION",
            "CLINICAL EXPERIENCE",
            "RESEARCH EXPERIENCE",
            "VOLUNTEER & COMMUNITY SERVICE",
            "LEADERSHIP",
            "CERTIFICATIONS & SKILLS",
        ],
        "section_guidelines": {
            "EDUCATION": "University, City, ST · graduation Month Year. Degree in {major}, GPA, science GPA. MCAT/NCLEX if applicable.",
            "CLINICAL EXPERIENCE": "Setting (hospital/clinic), role (scribe, CNA, EMT, shadowing). Total HOURS in parens. Bullets describe patient interaction, procedures observed/performed, EMR systems used.",
            "RESEARCH EXPERIENCE": "Lab, PI name, dates. Bullets on hypothesis, methods, techniques (PCR, ELISA, cell culture), and publications/presentations.",
            "VOLUNTEER & COMMUNITY SERVICE": "Hours, organization, role, population served.",
            "LEADERSHIP": "Pre-health societies, peer mentoring, club officer roles.",
            "CERTIFICATIONS & SKILLS": "BLS, ACLS, CNA, EMT-B, phlebotomy, Spanish proficiency, lab techniques.",
        },
    },
    # ─────────────────────────────────────────────────────────────
    "research": {
        "name": "Research / Academic / Graduate School",
        "description": "Research positions, graduate school applications, and academic roles.",
        "sections_order": [
            "EDUCATION",
            "RESEARCH EXPERIENCE",
            "PUBLICATIONS & PRESENTATIONS",
            "TEACHING EXPERIENCE",
            "TECHNICAL SKILLS",
            "HONORS & AWARDS",
        ],
        "section_guidelines": {
            "EDUCATION": "University, City, ST · graduation Month Year. Degree, GPA. Thesis title and advisor.",
            "RESEARCH EXPERIENCE": "Lab, PI, dates. Bullets cover research question, methodology, techniques, datasets/sample size, and findings. Use scientific language.",
            "PUBLICATIONS & PRESENTATIONS": "Full citations in a consistent format (APA/MLA/Chicago). Posters, conference talks, preprints.",
            "TEACHING EXPERIENCE": "TA roles, sections taught, student counts, evaluation scores.",
            "TECHNICAL SKILLS": "Lab techniques, statistical software (R, SPSS, SAS, Stata), programming (Python, MATLAB), instrumentation.",
            "HONORS & AWARDS": "Fellowships, grants ($ amount), competitive scholarships, dean's list.",
        },
    },
    # ─────────────────────────────────────────────────────────────
    "communications": {
        "name": "Communications / Media / PR",
        "description": "Journalism, PR, marketing communications, content, and media roles.",
        "sections_order": [
            "EDUCATION",
            "EXPERIENCE",
            "PORTFOLIO & PUBLICATIONS",
            "LEADERSHIP & INVOLVEMENT",
            "SKILLS",
        ],
        "section_guidelines": {
            "EDUCATION": "University, City, ST · graduation Month Year. Degree in {major}, GPA. Concentration (PR, Journalism, Advertising).",
            "EXPERIENCE": "Bullets emphasize audience reach, engagement metrics, impressions, follower growth, campaigns launched, stories published. Lead with verbs: Wrote, Edited, Pitched, Produced, Directed, Launched.",
            "PORTFOLIO & PUBLICATIONS": "Bylines with publication name and dates. Link to online portfolio.",
            "LEADERSHIP & INVOLVEMENT": "Student newspaper, radio, PRSSA, ad club. Officer roles.",
            "SKILLS": "Adobe Creative Suite (InDesign, Photoshop, Premiere), AP Style, social platforms, analytics (GA, Sprout, Hootsuite), CMS (WordPress), languages.",
        },
    },
    # ─────────────────────────────────────────────────────────────
    "executive": {
        "name": "Executive / Board",
        "description": "C-suite, VP+, and board candidates. Narrative format optimized for board narrative, P&L, and shareholder value.",
        "sections_order": [
            "EXECUTIVE SUMMARY",
            "BOARD & ADVISORY ROLES",
            "EXECUTIVE EXPERIENCE",
            "VALUE CREATED",
            "EDUCATION",
            "RECOGNITION",
        ],
        "section_guidelines": {
            "EXECUTIVE SUMMARY": "3–4 line narrative: tenure, scale (headcount, $ revenue/AUM), industry, signature outcome (exit, IPO, turnaround, 10x growth).",
            "BOARD & ADVISORY ROLES": "Company, board type (Board of Directors / Advisory), tenure, committee chair roles.",
            "EXECUTIVE EXPERIENCE": "Each role: Title, Company ($X revenue, N employees), tenure. Bullets emphasize P&L, M&A, fundraising rounds with $, exit value, headcount scaled, geographic expansion. Reverse chronological.",
            "VALUE CREATED": "Aggregate impact across career: $ raised, $ ARR added, exits, market cap created, headcount built.",
            "EDUCATION": "Degree, school. MBA, executive programs. Brief.",
            "RECOGNITION": "Forbes/Inc lists, industry awards, keynote speaker, published author, board appointments.",
        },
    },
    "trade": {
        "name": "Trade & Vocational",
        "description": "Skilled trades (electrician, welder, HVAC, CDL, plumber, mechanic). Certifications-first, equipment + safety record front and center.",
        "sections_order": [
            "CERTIFICATIONS & LICENSES",
            "WORK EXPERIENCE",
            "EQUIPMENT & TOOLS",
            "SAFETY RECORD",
            "EDUCATION & TRAINING",
            "UNION / PROFESSIONAL AFFILIATIONS",
        ],
        "section_guidelines": {
            "CERTIFICATIONS & LICENSES": "License #, issuing state, expiration. OSHA, EPA, NCCER, ASE, IBEW journeyman, CDL Class A/B, etc. List FIRST — this is what gets you hired.",
            "WORK EXPERIENCE": "Employer, City, ST, dates. Bullets cover job types completed, scope (residential/commercial/industrial), code compliance, downtime reduction, customer satisfaction, on-time completion %.",
            "EQUIPMENT & TOOLS": "Specific equipment / tools / machinery operated (CNC, MIG/TIG welders, HVAC diagnostic tools, lift trucks, etc.).",
            "SAFETY RECORD": "Years incident-free, OSHA training completed, safety committees served on.",
            "EDUCATION & TRAINING": "Trade school, apprenticeship hours, continuing education credits.",
            "UNION / PROFESSIONAL AFFILIATIONS": "Union locals, professional associations, journeyman status.",
        },
    },
    "international": {
        "name": "International CV (EMEA / APAC)",
        "description": "International CV format with locale-specific fields (photo optional, DOB where legal, nationality, GDPR clause). Defaults to A4.",
        "sections_order": [
            "PERSONAL DETAILS",
            "PROFESSIONAL PROFILE",
            "EDUCATION",
            "PROFESSIONAL EXPERIENCE",
            "SKILLS & LANGUAGES",
            "REFERENCES",
        ],
        "section_guidelines": {
            "PERSONAL DETAILS": "Full name, address (city, country), phone (+country code), email, LinkedIn, nationality, date of birth (only where legally customary, e.g., DE/AT/CH/JP). Optional small photo (top-right) where customary.",
            "PROFESSIONAL PROFILE": "3–4 line summary in formal British English. Mention years of experience, sector, languages.",
            "EDUCATION": "Reverse chronological. Institution, City, Country. Degree title with classification (First Class, 2:1, summa cum laude). Thesis title.",
            "PROFESSIONAL EXPERIENCE": "Reverse chronological. Employer, City, Country, dates (Month YYYY – Month YYYY). Bullets in past tense, formal tone. Quantified outcomes with €/£ where appropriate.",
            "SKILLS & LANGUAGES": "Technical skills + Languages with CEFR levels (A1–C2 / native).",
            "REFERENCES": "'Available upon request' OR 2 named referees with title, organisation, email (common in UK/IN/AU).",
        },
        "locale_rules": {
            "page_size": "A4",
            "include_photo": "optional",
            "include_dob": True,
            "include_nationality": True,
            "gdpr_clause": "I consent to the processing of my personal data for the purposes of recruitment per GDPR Art. 6(1)(a).",
            "language": "British English",
        },
    },
    "federal": {
        "name": "Federal / Government (USAJobs)",
        "description": "US Federal resume format for USAJobs.gov. Long-form (3–5 pages), KSA blocks, GS-grade alignment, security clearance section.",
        "sections_order": [
            "CANDIDATE INFORMATION",
            "OBJECTIVE / TARGET POSITION",
            "PROFESSIONAL EXPERIENCE",
            "KNOWLEDGE, SKILLS & ABILITIES (KSAs)",
            "EDUCATION",
            "CERTIFICATIONS & TRAINING",
            "SECURITY CLEARANCE",
            "VETERANS' PREFERENCE",
        ],
        "section_guidelines": {
            "CANDIDATE INFORMATION": "Full legal name, mailing address, phone, email, country of citizenship, federal employment status (current fed / former fed / never fed).",
            "OBJECTIVE / TARGET POSITION": "Target announcement number, series and grade (e.g., 'GS-2210-13'), agency.",
            "PROFESSIONAL EXPERIENCE": "Each role: Employer, City/State, dates (MM/YYYY – MM/YYYY), hours per week, supervisor name + 'may contact: yes/no', salary. Bullets in long-form prose detailing scope, outcomes, authorities held, regulations followed.",
            "KNOWLEDGE, SKILLS & ABILITIES (KSAs)": "Address EACH KSA from the announcement explicitly with a CCAR-format response (Context, Challenge, Action, Result).",
            "EDUCATION": "Institution, degree, GPA, semester credit hours (federal hires often require credit-hour proof).",
            "CERTIFICATIONS & TRAINING": "Federal training (DAU, FAI), industry certs, hours of training.",
            "SECURITY CLEARANCE": "Active clearance level (Public Trust / Secret / TS / TS/SCI), agency that granted it, year, polygraph status.",
            "VETERANS' PREFERENCE": "VRA, 5-pt, 10-pt preference; DD-214 available.",
        },
    },
    "academic": {
        "name": "Academic CV",
        "description": "Tenure-track, postdoc, and graduate faculty applications. Publications-first, multi-page format.",
        "sections_order": [
            "EDUCATION",
            "ACADEMIC APPOINTMENTS",
            "RESEARCH INTERESTS",
            "PUBLICATIONS",
            "GRANTS & FUNDING",
            "TEACHING EXPERIENCE",
            "INVITED TALKS & PRESENTATIONS",
            "PROFESSIONAL SERVICE",
            "AWARDS & HONORS",
            "PROFESSIONAL MEMBERSHIPS",
        ],
        "section_guidelines": {
            "EDUCATION": "Reverse chronological. Institution, degree, year. Dissertation title and advisor for PhD.",
            "ACADEMIC APPOINTMENTS": "Title (Postdoctoral Fellow, Assistant Professor, etc.), department, institution, dates.",
            "RESEARCH INTERESTS": "3–6 short phrases describing research agenda.",
            "PUBLICATIONS": "Subdivide: Peer-reviewed journals / Book chapters / Conference proceedings / Preprints. Use a consistent citation style (APA/Chicago). Bold the candidate's name. Include DOI.",
            "GRANTS & FUNDING": "Funder, grant title, role (PI/Co-PI), $ amount, dates.",
            "TEACHING EXPERIENCE": "Course title, institution, semester, role (Instructor of Record / TA), enrollment, course evaluation score.",
            "INVITED TALKS & PRESENTATIONS": "Title, venue, location, date.",
            "PROFESSIONAL SERVICE": "Journal peer review, conference organizing, departmental committees.",
            "AWARDS & HONORS": "Fellowships (with $ amount), best paper, dean's awards.",
            "PROFESSIONAL MEMBERSHIPS": "Scholarly societies (ACM, IEEE, AERA, etc.).",
        },
    },
    "returnship": {
        "name": "Returnship / Career Re-entry",
        "description": "For candidates returning to the workforce after a parenting / caregiving / health break. Frames the gap as a strength.",
        "sections_order": [
            "PROFESSIONAL SUMMARY",
            "CAREER BREAK",
            "RECENT UPSKILLING",
            "PROFESSIONAL EXPERIENCE",
            "SKILLS",
            "EDUCATION",
            "VOLUNTEER & COMMUNITY",
        ],
        "section_guidelines": {
            "PROFESSIONAL SUMMARY": "3–4 lines: years of pre-break experience, target return role, what's been refreshed during the break. Confident, non-apologetic.",
            "CAREER BREAK": "Explicit single line: 'Career Break (YYYY–YYYY) — Caregiver / Parental Leave / Health / Sabbatical.' Optional 1 line on transferable competencies built (project management, budgeting, advocacy).",
            "RECENT UPSKILLING": "Courses, certifications, bootcamps completed during the break with dates. List FIRST — proves currency.",
            "PROFESSIONAL EXPERIENCE": "Pre-break roles in reverse chronological. Bullets emphasize transferable, evergreen skills, NOT outdated tech.",
            "SKILLS": "Refreshed tools / tech / methodologies, with year-of-most-recent-use noted where helpful.",
            "EDUCATION": "Standard.",
            "VOLUNTEER & COMMUNITY": "Board roles, PTA, nonprofit leadership, freelance projects done during the break — all signal continued engagement.",
        },
    },
    # ─────────────────────────────────────────────────────────────
    "general": {
        "name": "General",
        "description": "Versatile template for jobs, internships, research, and grad school applications when no specialized template fits.",
        "sections_order": [
            "EDUCATION",
            "EXPERIENCE",
            "PROJECTS",
            "LEADERSHIP & COMMUNITY INVOLVEMENT",
            "SKILLS",
            "HONORS & AWARDS",
        ],
        "section_guidelines": {
            "EDUCATION": "University, City, ST · graduation Month Year. Degree, GPA. Relevant coursework.",
            "EXPERIENCE": "Reverse chronological. Strong action verbs + quantified results.",
            "PROJECTS": "Academic or personal projects relevant to the target role.",
            "LEADERSHIP & COMMUNITY INVOLVEMENT": "Student orgs, volunteering, campus engagement.",
            "SKILLS": "Technical skills, languages, certifications.",
            "HONORS & AWARDS": "Brief list, name only.",
        },
    },
}

# Backward-compatible aliases for older callers
TEMPLATES["data_science"] = TEMPLATES["technical"]


def get_template(template_type: str) -> Dict[str, Any]:
    """Return the template dict for the given type, defaulting to 'general'."""
    return TEMPLATES.get(template_type, TEMPLATES["general"])


def get_template_names() -> List[Dict[str, str]]:
    """Return list of available template names and descriptions (excludes aliases)."""
    seen_names = set()
    out: List[Dict[str, str]] = []
    for key, val in TEMPLATES.items():
        if val["name"] in seen_names:
            continue
        seen_names.add(val["name"])
        out.append({"id": key, "name": val["name"], "description": val["description"]})
    return out


def render_template_guidance(template_type: str) -> str:
    """Render a template's section order + per-section guidance as a prompt block."""
    tpl = get_template(template_type)
    lines = [f"TEMPLATE: {tpl['name']}", f"PURPOSE: {tpl['description']}", "", "SECTION ORDER (use these exact section titles, in this order, only if the user has matching content):"]
    for i, s in enumerate(tpl["sections_order"], 1):
        lines.append(f"  {i}. {s}")
    lines.append("")
    lines.append("PER-SECTION GUIDANCE:")
    for sec, guide in tpl["section_guidelines"].items():
        lines.append(f"  • {sec}: {guide}")
    return "\n".join(lines)


ROI_FRAMEWORKS: Dict[str, str] = {
    "executive":     "SHAREHOLDER VALUE: P&L $, headcount, fundraising $ raised, exit value, board outcomes, market cap created, M&A.",
    "consulting":    "CLIENT IMPACT: $ saved, % efficiency gain, executive audience, scope of engagement, framework applied, recommendation adopted.",
    "business":      "FINANCIAL ROI: revenue $, margin %, cost saved $, deal size $, growth rate %, customers acquired, retention %.",
    "technical":     "ARCHITECTURE INTEGRITY: latency ms, throughput RPS, uptime %, users served, infra $ saved, deploys/day, test coverage %.",
    "engineering":   "DESIGN IMPACT: tolerance achieved, efficiency %, safety record, cost reduction $, parts shipped, cycle time reduction.",
    "education":     "STUDENT OUTCOMES: test score growth %, graduation rate, students taught, parent satisfaction %, attendance %.",
    "healthcare":    "PATIENT IMPACT: patient volume, clinical hours, accuracy %, protocol adherence, readmission rate %.",
    "research":      "ACADEMIC IMPACT: citations, h-index, publications, grant $ won, dataset size, reproducibility.",
    "communications":"AUDIENCE IMPACT: impressions, engagement %, follower growth, campaign reach, earned media $, click-through %.",
    "trade":         "OPERATIONAL IMPACT: jobs completed, downtime reduction, safety incidents (target: 0), code compliance %, on-time %.",
    "international": "FINANCIAL ROI in local currency (€/£/¥): revenue, margin, cost reduction, stakeholder reach.",
    "federal":       "MISSION IMPACT: regulations enforced, $ stewarded, taxpayer savings, citizens served, audits passed, FAR/FAC compliance.",
    "academic":      "ACADEMIC IMPACT: citations, h-index, publications in tier-1 venues, grant $ won, students mentored, courses developed.",
    "returnship":    "TRANSFERABLE COMPETENCY: scope managed, $ budget, stakeholders aligned, courses completed during break, currency demonstrated.",
    "general":       "QUANTIFIED OUTCOMES: %, $, scope, time saved, people impacted, throughput.",
}


def get_roi_framework(template_type: str) -> str:
    """Return the ROI framework string for a template (for prompt injection)."""
    return ROI_FRAMEWORKS.get(template_type, ROI_FRAMEWORKS["general"])


def auto_select_template(major: str, job_title: str) -> str:
    """Auto-select the best template based on the user's major and target job."""
    combined = f"{major} {job_title}".lower()

    keyword_map = [
        ("executive", {"chief", "cto", "ceo", "cfo", "coo", "ciso", "cmo", "vp ", "vice president", "svp", "evp", "head of", "founder", "managing director"}),
        ("federal", {"usajobs", "federal", "gs-", "department of", "agency", "civil service", "ksa"}),
        ("academic", {"tenure", "tenure-track", "postdoc", "post-doc", "assistant professor", "associate professor", "faculty"}),
        ("trade", {"electrician", "welder", "hvac", "plumber", "mechanic", "carpenter", "cdl", "ironworker", "machinist"}),
        ("returnship", {"returnship", "return to work", "career re-entry", "career break", "relauncher"}),
        ("international", {"european union", "uk graduate", "british english", "europass", "eu cv", "international cv"}),
        ("consulting", {"consulting", "consultant", "strategy", "advisory", "mbb"}),
        ("technical", {
            "software", "developer", "engineer intern", "data science", "data analyst",
            "data engineer", "machine learning", "analytics", "ai ", "artificial intelligence",
            "deep learning", "nlp", "computer science", "swe", "backend", "frontend", "full stack",
            "devops", "cloud", "sre",
        }),
        ("engineering", {
            "mechanical", "electrical", "civil", "chemical", "aerospace", "biomedical",
            "industrial engineering", "petroleum", "materials", "manufacturing",
        }),
        ("healthcare", {
            "pre-med", "premed", "nursing", "clinical", "public health", "health science",
            "medical", "physician", "pharmacy", "dental",
        }),
        ("education", {
            "teacher", "teaching", "education", "curriculum", "instructional", "tutor", "edtech",
        }),
        ("research", {
            "research", "phd", "graduate school", "lab assistant", "scientist",
        }),
        ("communications", {
            "communications", "journalism", "public relations", "pr ", "marketing communications",
            "media", "content", "copywriter", "editor", "broadcast",
        }),
        ("business", {
            "business", "finance", "marketing", "accounting", "management",
            "economics", "mba", "entrepreneurship", "supply chain", "operations",
            "human resources", "hr ", "sales", "real estate",
        }),
    ]

    for template_id, kws in keyword_map:
        for kw in kws:
            if kw in combined:
                return template_id

    return "general"

# HireLens AI

> AI-powered career intelligence platform — ATS scoring, keyword gap analysis, role-specific resume rewriting, cover letter generation, interview prep, resume comparison, and a job application tracker.

HireLens AI helps job seekers understand exactly how their resume performs against an Applicant Tracking System for a specific job description, then gives them the tools to fix the gaps: AI-rewritten bullets, role-specific resume templates, tailored cover letters, STAR-framework interview questions, and a Kanban-style application tracker.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Quick Start](#quick-start)
6. [Environment Variables](#environment-variables)
7. [API Reference](#api-reference)
8. [Frontend Routes](#frontend-routes)
9. [ATS Scoring Model](#ats-scoring-model)
10. [Role-Specific Resume Templates](#role-specific-resume-templates)
11. [Pricing & Plan Gating](#pricing--plan-gating)
12. [Testing](#testing)
13. [Docker](#docker)
14. [Common Issues](#common-issues)

---

## Features

| Area | Capability |
|---|---|
| **Resume ingestion** | PDF + DOCX upload (5 MB cap), in-memory parsing — no persistent storage |
| **ATS scoring** | 0–100 score across 5 weighted components with pass-probability rating |
| **Keyword analysis** | TF-IDF + spaCy keyword extraction, matched vs missing keywords |
| **Skill gap detection** | Critical / recommended / nice-to-have classification + curated learning links for ~60 skills |
| **Bullet analyzer** | Action-verb detection, quantification scoring, JD-keyword overlap |
| **AI Resume Rewrite** | Gemini-powered rewrite with 9 role-specific templates (Technical, Engineering, Business, Consulting, Education, Healthcare, Research, Communications, General) |
| **Cover letter generation** | 3 tones (professional, confident, conversational) |
| **Interview prep** | 10 AI-generated questions categorized as behavioral / technical / role-specific, each with a STAR framework answer guide |
| **Resume comparison** | Side-by-side scoring of two resumes against the same JD |
| **PDF / DOCX export** | jsPDF auto-scales the optimized resume to a single page; DOCX via the `docx` library |
| **Job application tracker** | SQLite-backed CRUD with Kanban statuses (Applied, Interviewing, Rejected, Offer) |
| **Auth** | Google Sign-In via `@react-oauth/google` |
| **Plan gating** | Free / Pro / Premium tiers with `localStorage`-backed usage tracking |

---

## Architecture

```
┌─────────────────┐         ┌─────────────────────┐         ┌─────────────────┐
│   React + Vite  │  HTTP   │   FastAPI Backend   │  HTTPS  │   Gemini API    │
│   (port 5199)   ├────────►│   (port 8000)       ├────────►│ gemini-2.0-flash│
│                 │  /api   │                     │         │                 │
└─────────────────┘         └──────────┬──────────┘         └─────────────────┘
                                       │
                                       │ aiosqlite
                                       ▼
                              ┌─────────────────┐
                              │  SQLite tracker │
                              │  data/hirelens  │
                              └─────────────────┘
```

Core flow:

1. User uploads a resume (PDF/DOCX) and pastes a job description.
2. Backend parses the resume (`pdfplumber` / `python-docx`) and runs spaCy NLP on the JD.
3. Scoring engine computes the 5-component ATS score.
4. Gap detector classifies missing skills by importance.
5. (Premium) Gemini generates a role-specific resume rewrite, cover letter, and STAR interview questions.
6. Frontend renders dashboards (gauge, radar, bar charts) and allows in-place editing + PDF/DOCX export.

---

## Tech Stack

**Backend**
- FastAPI 0.109 + Uvicorn (ASGI)
- Google `google-genai` SDK → `gemini-2.0-flash`
- spaCy 3.7 (`en_core_web_sm`)
- scikit-learn TF-IDF
- pdfplumber, python-docx
- aiosqlite + SQLite
- Pydantic v2 settings

**Frontend**
- React 18 + TypeScript 5 + Vite 5
- Tailwind CSS, Framer Motion
- Zustand (state), Axios, React Router v6
- Recharts (gauge, radar, bar charts)
- react-dropzone, html2pdf.js, jspdf, docx
- `@react-oauth/google`

---

## Project Structure

```
hirelensai/
├── hirelens-backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app factory + CORS
│   │   ├── config.py                  # Pydantic settings
│   │   ├── api/routes/                # analyze, rewrite, compare, interview, tracker, cover_letter
│   │   ├── services/
│   │   │   ├── gpt_service.py         # Gemini calls (rewrite, cover letter, interview)
│   │   │   ├── scorer.py              # 5-component ATS scoring
│   │   │   ├── nlp.py                 # spaCy skill / requirement extraction
│   │   │   ├── parser.py              # PDF / DOCX parsing
│   │   │   ├── gap_detector.py        # skill-gap classification
│   │   │   ├── bullet_analyzer.py     # bullet impact scoring
│   │   │   └── resume_templates.py    # 9 role-specific templates
│   │   ├── schemas/                   # Pydantic request/response models
│   │   └── db/database.py             # SQLite tracker init
│   ├── tests/
│   ├── data/hirelens.db               # SQLite (auto-created)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── hirelens-frontend/
│   ├── src/
│   │   ├── pages/                     # Landing, Analyze, Results, Rewrite, Tracker, Pricing, Interview, Compare
│   │   ├── components/
│   │   │   ├── dashboard/             # MissingSkillsPanel, KeywordChart, ScoreGauge, etc.
│   │   │   ├── rewrite/               # ResumeEditor, ResumePDFTemplate, CoverLetterViewer
│   │   │   └── ui/                    # AnimatedCard, GlowButton, etc.
│   │   ├── context/                   # AnalysisContext, UsageContext, AuthContext
│   │   ├── hooks/                     # useRewrite, useInterview, useAnalysis
│   │   ├── services/api.ts            # Axios client
│   │   ├── utils/                     # formatters, skillResources, docxExport
│   │   └── types/index.ts
│   ├── vite.config.ts                 # /api proxy → :8000
│   └── package.json
├── scripts/
│   ├── start.sh                       # Boots both services, kills stale ports
│   └── stop.sh
└── logs/                              # backend.log, frontend.log
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node 18+
- A Google Gemini API key

### One-shot start

```bash
./scripts/start.sh
```

This script:
- Creates and activates the Python venv if missing
- Installs dependencies + downloads `en_core_web_sm`
- Kills any stale processes on ports 8000 / 5199
- Starts FastAPI + Vite in the background
- Tails logs to `logs/backend.log` and `logs/frontend.log`

### Stop everything
```bash
./scripts/stop.sh
```

### Manual start
```bash
# Backend
cd hirelens-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000

# Frontend
cd hirelens-frontend
npm install
npm run dev -- --port 5199
```

### Local URLs
| Service | URL |
|---|---|
| Frontend | http://localhost:5199 |
| Backend API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health | http://localhost:8000/health |

---

## Environment Variables

**`hirelens-backend/.env`** (copy from `.env.example`):
```
GEMINI_API_KEY=<your-key>
GEMINI_MODEL=gemini-2.0-flash
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5199
ENABLE_SQLITE_TRACKER=true
MAX_UPLOAD_SIZE_MB=5
```

**`hirelens-frontend/.env`** (copy from `.env.example`):
```
VITE_API_BASE_URL=               # leave blank in dev (Vite proxies /api → :8000)
VITE_GOOGLE_CLIENT_ID=           # optional — enables Google Sign-In
```

To enable Google Sign-In:
1. Create an OAuth 2.0 Client ID in https://console.cloud.google.com/
2. Add `http://localhost:5199` to Authorized JavaScript origins
3. Paste the Client ID into `VITE_GOOGLE_CLIENT_ID`

---

## API Reference

All endpoints are prefixed with `/api`.

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/analyze` | Resume + JD analysis (score, keywords, gaps, bullets) |
| `POST` | `/api/compare` | Side-by-side comparison of two resumes vs the same JD |
| `POST` | `/api/rewrite` | AI rewrite with role-specific template (`technical`, `engineering`, `business`, `consulting`, `education`, `healthcare`, `research`, `communications`, `general`) |
| `GET` | `/api/rewrite/templates` | List all available role templates |
| `POST` | `/api/cover-letter` | Cover letter generation (tone: professional / confident / conversational) |
| `POST` | `/api/interview-prep` | 10 interview questions categorized by type with STAR-framework answers |
| `GET` | `/api/tracker` | List job applications |
| `POST` | `/api/tracker` | Create application |
| `PATCH` | `/api/tracker/{id}` | Update status |
| `DELETE` | `/api/tracker/{id}` | Delete application |
| `GET` | `/health` | Health check |

### Example: `/api/rewrite` request
```json
{
  "resume_text": "...",
  "job_description": "...",
  "template_type": "consulting",
  "major": "Economics"
}
```
If `template_type` is omitted or `"general"`, the backend auto-detects the best template from the major + job title.

---

## Frontend Routes

| Path | Page |
|---|---|
| `/` | Landing |
| `/analyze` | Upload + JD entry |
| `/results` | Three-column ATS dashboard |
| `/rewrite` | AI Rewrite + Cover Letter (Premium) |
| `/interview` | Interview Prep |
| `/compare` | Resume Compare |
| `/tracker` | Application Kanban |
| `/pricing` | Plan upgrade |

---

## ATS Scoring Model

Range: **0–100**, weighted across 5 components.

| Component | Weight |
|---|---|
| Keyword Match | 40% |
| Skill Coverage | 25% |
| Experience Alignment | 20% |
| Bullet Strength | 10% |
| Formatting | 5% |

**Pass probability rating**
- 90–100 → Excellent compatibility
- 75–89 → Likely passes ATS
- 60–74 → Risky
- < 60 → Likely rejected

---

## Role-Specific Resume Templates

When the user clicks **Generate AI Rewrite**, they pick a role template (or let the system auto-detect from the JD). Each template defines a canonical section order plus per-section guidance the AI follows.

| Template | Best for | Characteristic sections |
|---|---|---|
| **Technical** | CS / Software / Data | TECHNICAL SKILLS placed immediately after Education |
| **Engineering** | Mechanical / Electrical / Civil / Chemical | RELEVANT COURSEWORK + ENGINEERING EXPERIENCE + Professional Societies |
| **Business** | Finance / Marketing / Management | EXPERIENCE emphasizes revenue / margin / growth |
| **Consulting** | Strategy / Advisory | MBB-style bullets; Ownership + Method + Quantified Impact |
| **Education** | Teaching / Curriculum / EdTech | CERTIFICATIONS & LICENSURE + TEACHING EXPERIENCE |
| **Healthcare** | Pre-Med / Nursing / Public Health | CLINICAL EXPERIENCE with hours, RESEARCH + Volunteer hours |
| **Research** | PhD / Grad school / Academic | PUBLICATIONS & PRESENTATIONS, advisors, grant amounts |
| **Communications** | Journalism / PR / Media | PORTFOLIO & PUBLICATIONS, audience + engagement metrics |
| **General** | Anything else | Versatile fallback |

Templates are defined in `hirelens-backend/app/services/resume_templates.py` and modeled on the UT Austin Career Services resume template categories.

---

## Pricing & Plan Gating

| Plan | Price | Highlights |
|---|---|---|
| **Free** | $0 | 3 ATS scans, no rewrite, no cover letter |
| **Pro** | $10/mo | Unlimited scans, full analytics, AI bullet suggestions |
| **Premium** | $15/mo | Everything + AI rewrite, cover letter, role templates, PDF/DOCX export |

Plan state lives in `localStorage` (`hireport_usage`) via `UsageContext`. The `/rewrite` page is gated behind Premium. Pricing CTAs use a mock `upgradePlan()` — no real Stripe integration yet.

---

## Testing

```bash
cd hirelens-backend
source venv/bin/activate
pytest tests/
```

Test files: `tests/test_nlp.py`, `tests/test_parser.py`, `tests/test_scorer.py`.

---

## Docker

```bash
cd hirelens-backend
docker-compose up
```

Exposes port 8000, downloads `en_core_web_sm` on build, health check on `GET /health`.

---

## Common Issues

| Problem | Fix |
|---|---|
| Port already in use | `./scripts/stop.sh` or `lsof -ti tcp:8000 \| xargs kill -9` |
| spaCy model missing | `python -m spacy download en_core_web_sm` |
| `GEMINI_API_KEY` not set | Edit `hirelens-backend/.env` |
| Frontend can't reach API | Ensure backend is running; Vite proxies `/api` → `:8000` |
| AI features return fallback text | Check Gemini key validity + model name |
| Google Sign-In not showing | Set `VITE_GOOGLE_CLIENT_ID` |
| PDF export blank | `npm install html2pdf.js jspdf docx` |

---

## License

Internal project. All rights reserved.

# Product Requirements Document — HireLens AI

| Field | Value |
|---|---|
| **Product** | HireLens AI |
| **Version** | 1.0 |
| **Status** | Built — pre-launch |
| **Owner** | HireLens AI Team |
| **Last updated** | 2026-04-07 |

---

## 1. Executive Summary

HireLens AI is an AI-powered career intelligence platform that helps job seekers diagnose and fix the gap between their resume and a specific job description. The product combines deterministic ATS scoring (TF-IDF + spaCy NLP) with generative AI (Google Gemini) to deliver:

1. A transparent ATS compatibility score broken into 5 weighted components.
2. Role-specific AI resume rewriting across 9 industry templates.
3. Tailored cover letters in 3 tones.
4. Categorized interview prep with STAR-framework answer guides.
5. Side-by-side resume comparison.
6. A lightweight Kanban-style application tracker.

The product is positioned as a modern SaaS dashboard (Stripe / Linear / Vercel aesthetic) with three pricing tiers: Free, Pro, and Premium.

---

## 2. Problem Statement

Job seekers are evaluated by Applicant Tracking Systems before a human ever sees their resume. Most candidates:

- Don't know how their resume scores against a specific JD.
- Can't tell which keywords or skills they're missing.
- Lack the writing skill or time to rewrite bullets in ATS-optimized form.
- Get generic advice that doesn't account for the role they're targeting (a Mechanical Engineer needs a very different resume than a Management Consultant).
- Treat each application in isolation with no system to track outcomes.

Existing tools either give a vague "score out of 100" with no actionable detail, or charge premium prices for one-shot rewrites that ignore the target role's conventions.

---

## 3. Goals & Non-Goals

### Goals
- **G1.** Give every user a transparent, component-level ATS score in under 10 seconds.
- **G2.** Surface exactly which keywords and skills are missing, ranked by importance.
- **G3.** Generate an ATS-optimized resume rewrite that respects the conventions of the target role.
- **G4.** Provide cover letter and interview prep generation tied to the same resume + JD context.
- **G5.** Let users compare two resumes head-to-head against a single JD.
- **G6.** Track applications with status updates without forcing the user into a complex CRM.
- **G7.** Process resumes in-memory only — no persistent file storage — for privacy.

### Non-Goals (v1)
- LinkedIn / job-board scraping or auto-apply.
- Real Stripe billing (mock upgrade only in v1).
- Backend JWT auth (frontend Google Sign-In only; APIs are public in v1).
- Multi-user collaboration on a single resume.
- Mobile native apps.

---

## 4. Target Users

| Persona | Description | Primary needs |
|---|---|---|
| **Recent grad** | First job hunt, no industry network | ATS score, role-specific template, interview prep |
| **Career switcher** | Moving from one industry to another | Skill gap analysis, rewrite that reframes existing experience |
| **Active applier** | Applying to 20+ jobs/month | Tracker, fast scan, resume comparison |
| **International student** | English isn't first language | Bullet rewriting, cover letter generation |

---

## 5. User Stories

| ID | Story | Acceptance |
|---|---|---|
| US-1 | As a user, I upload my resume + paste a JD and get an ATS score. | Score 0–100 + 5-component breakdown displayed within 10s |
| US-2 | I see the keywords I'm missing ranked by importance. | Critical / Recommended / Nice-to-have buckets with curated learning links |
| US-3 | I pick a role (technical, business, consulting, etc.) and the AI rewrites my resume in that style. | 9 role templates available; rewrite preserves all original orgs/dates |
| US-4 | I export the optimized resume as PDF or DOCX. | Single-page auto-scaled PDF + editable DOCX |
| US-5 | I generate a cover letter in 3 different tones. | Professional / Confident / Conversational |
| US-6 | I get interview questions categorized as Behavioral / Technical / Role-Specific. | 10 questions; each with a STAR framework answer guide |
| US-7 | I compare two versions of my resume against the same JD. | Side-by-side dashboard with score deltas |
| US-8 | I track my applications by status. | Kanban board with Applied / Interviewing / Rejected / Offer columns |
| US-9 | I upgrade my plan from Free to Premium. | Plan persists in localStorage; gated features unlock immediately |

---

## 6. Functional Requirements

### 6.1 Resume Ingestion
- Accept PDF or DOCX up to 5 MB.
- Parse text via `pdfplumber` (PDF) or `python-docx` (DOCX).
- Files are processed in-memory only — never persisted to disk.

### 6.2 NLP & Scoring
- spaCy `en_core_web_sm` for tokenization, lemmatization, noun-phrase extraction.
- TF-IDF (scikit-learn) for keyword importance ranking from the JD.
- Skill extraction matched against a curated skill taxonomy.
- 5-component weighted score:
  - Keyword Match — 40%
  - Skill Coverage — 25%
  - Experience Alignment — 20%
  - Bullet Strength — 10%
  - Formatting — 5%
- Pass-probability label: Excellent (90+), Likely Pass (75–89), Risky (60–74), Likely Rejected (<60).

### 6.3 AI Resume Rewrite
- Powered by Gemini 2.0 Flash via `google-genai` SDK.
- Accepts an optional `template_type` parameter; auto-detects from major + job title if absent.
- 9 role templates: Technical, Engineering, Business, Consulting, Education, Healthcare, Research, Communications, General.
- Each template injects a role-specific section order and per-section guidance into the prompt.
- Hard rules enforced in prompt:
  - Never fabricate jobs, dates, or organizations.
  - Include every original entry (no merging or dropping).
  - Add plausible inferred metrics where context supports it.
  - 2–3 bullets per entry, every bullet starts with a strong action verb and contains a quantified result.
- Returns structured JSON: header + sections (with typed entries) + plain-text fallback.

### 6.4 Cover Letter Generation
- 3 tones: Professional, Confident, Conversational.
- Single-page format pulled from the same resume + JD context.

### 6.5 Interview Prep
- 10 questions per session: 3 behavioral, 4 technical, 2 situational, 1 culture-fit.
- Each question categorized by the AI as `behavioral` / `technical` / `role-specific`.
- Each includes a STAR (Situation / Task / Action / Result) framework answer guide.
- Frontend filter tabs: All / Behavioral / Technical / Role-Specific.

### 6.6 Resume Comparison
- Accept 2 resumes + 1 JD.
- Returns 2 full ATS analyses + a delta summary.
- Frontend displays side-by-side scores and component breakdown.

### 6.7 Job Application Tracker
- SQLite (`aiosqlite`) at `data/hirelens.db`.
- Columns: id, company, role, date_applied, ats_score, status, created_at.
- Statuses: Applied, Interviewing, Rejected, Offer.
- Kanban-style frontend with drag-to-update status.

### 6.8 Plan Gating
- 3 tiers stored in `localStorage` (`hireport_usage`).
  - **Free** ($0): 3 scans, no rewrite, no cover letter.
  - **Pro** ($10/mo): Unlimited scans, full analytics, AI bullet suggestions.
  - **Premium** ($15/mo): Everything + AI rewrite, cover letter, role templates, PDF/DOCX export.
- `/rewrite` page is gated behind Premium with an upgrade modal.
- Pricing page CTAs use a mock `upgradePlan()` — no real payment integration in v1.

### 6.9 Authentication
- Google Sign-In via `@react-oauth/google` (optional, requires `VITE_GOOGLE_CLIENT_ID`).
- Backend APIs are public in v1 — no JWT verification.

### 6.10 Export
- **PDF:** jsPDF auto-scaling algorithm fits resume to a single Letter-size page (font scaling between 48% and 100%).
- **DOCX:** Generated via the `docx` library with bold/italic/size styling preserved.

---

## 7. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | Analyze + score in < 10s; AI rewrite in < 30s |
| **Privacy** | Resume files processed in-memory only; no persistent file storage |
| **Reliability** | Graceful fallback responses if Gemini API fails |
| **Compatibility** | Latest Chrome, Safari, Firefox, Edge |
| **Accessibility** | All buttons have `aria-label`s; color contrast meets WCAG AA |
| **Security** | CORS restricted via `ALLOWED_ORIGINS`; file size capped at 5 MB |
| **Observability** | Logs to `logs/backend.log` and `logs/frontend.log`; `/health` endpoint |

---

## 8. System Architecture

```
┌─────────────────┐         ┌─────────────────────┐         ┌─────────────────┐
│   React + Vite  │  HTTP   │   FastAPI Backend   │  HTTPS  │   Gemini API    │
│   (port 5199)   ├────────►│   (port 8000)       ├────────►│ gemini-2.0-flash│
└─────────────────┘  /api   └──────────┬──────────┘         └─────────────────┘
                                       │ aiosqlite
                                       ▼
                              ┌─────────────────┐
                              │  SQLite tracker │
                              └─────────────────┘
```

**Tech stack**
- Backend: FastAPI, google-genai, spaCy, scikit-learn, pdfplumber, python-docx, aiosqlite
- Frontend: React 18, TypeScript, Vite, Tailwind, Framer Motion, Recharts, Zustand, Axios

---

## 9. Data Model

### `RewriteResponse` (backend → frontend)
```ts
{
  header: { name: string, contact: string },
  sections: [{
    title: string,
    content: string,                              // for Skills / Honors
    entries: [{
      org: string, location: string, date: string,
      title: string, bullets: string[], details: string[]
    }]
  }],
  full_text: string,
  template_type: string                           // "technical" | "consulting" | ...
}
```

### `InterviewQuestion`
```ts
{
  question: string,
  star_framework: string,
  category: "behavioral" | "technical" | "role-specific"
}
```

### Tracker schema (SQLite)
```sql
CREATE TABLE tracker_applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company TEXT NOT NULL,
  role TEXT NOT NULL,
  date_applied DATE,
  ats_score INTEGER,
  status TEXT CHECK(status IN ('Applied','Interviewing','Rejected','Offer')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 10. Success Metrics

| Metric | Target |
|---|---|
| Time-to-first-score (upload → dashboard) | < 10s p95 |
| Time-to-rewrite (Premium) | < 30s p95 |
| ATS rewrite score lift (avg before → after) | +20 points |
| Free → Premium conversion | 5% |
| Weekly active users (90 days post-launch) | 1,000 |
| Tracker adoption (% of paid users with ≥3 entries) | 40% |

---

## 11. Release Plan

### v1.0 — current build (✅ complete)
- All 9 features above shipped.
- 9 role-specific resume templates.
- Categorized interview prep (3 categories with backend labeling).
- Mock Premium upgrade.
- Vercel deploy config + Docker.

### v1.1 — next
- Real Stripe billing integration.
- Backend JWT auth (currently APIs are public).
- Per-user persistence (currently `localStorage` only).

### v1.2 — later
- Expand `skillResources.ts` from ~60 → 200+ skill links.
- Multi-resume library per user.
- Slack / email reminders for tracker follow-ups.

---

## 12. Open Questions

1. Do we need a persistent backend store for resumes once auth lands, or stay stateless for privacy?
2. Should the Pro tier include limited (e.g., 5/month) AI rewrites to drive Premium upsell?
3. Which payment processor for v1.1 — Stripe, Lemon Squeezy, or Paddle?
4. Should we support multi-language resumes (Spanish, French) in v1.2?

---

## 13. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Gemini API downtime / overload | AI features fail | Fallback responses + retry; consider Anthropic / OpenAI as backup |
| ATS scoring inaccuracy | Users lose trust | Show component breakdown + explain methodology in tooltip |
| AI fabrication of metrics | Resume credibility damaged | Hard prompt rule: "NEVER fabricate"; show original side-by-side |
| Privacy concerns over resume content | Adoption blocker | In-memory processing only; surface privacy notice on upload |
| No real billing in v1 | Zero revenue | Treat v1 as beta; ship Stripe in v1.1 |

---

## 14. References

- UT Austin Career Services resume templates: https://careerservices.cns.utexas.edu/resources/resumes/templates
- Google Gemini API docs: https://ai.google.dev/
- spaCy `en_core_web_sm`: https://spacy.io/models/en

---

**End of PRD**

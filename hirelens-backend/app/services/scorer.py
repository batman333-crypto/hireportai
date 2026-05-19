"""Enterprise-grade ATS scoring engine matching Workday/Taleo/iCIMS/Greenhouse standards."""
import re
from typing import Any, Dict, List, Optional


class ATSScorer:
    """Scores a resume against a job description for ATS compatibility.

    Scoring breakdown matching enterprise ATS systems:
        - Keyword Match:          35% (TF-IDF weighted, phrase-aware, section-boosted)
        - Skills Coverage:        25% (expanded alias matching, category weights)
        - Experience Alignment:   20% (title similarity, years of experience, seniority)
        - Formatting Compliance:  10% (ATS parser friendliness)
        - Bullet Strength:        10% (action verbs, metrics, keyword density)
    """

    KEYWORD_WEIGHT: float = 0.35
    SKILLS_WEIGHT: float = 0.25
    EXPERIENCE_WEIGHT: float = 0.20
    FORMAT_WEIGHT: float = 0.10
    BULLET_WEIGHT: float = 0.10

    # Hard-skills that are high-value in most tech/business roles
    _HARD_SKILL_PATTERNS = re.compile(
        r"\b(python|java|sql|javascript|typescript|react|node|aws|azure|gcp|docker|kubernetes|"
        r"tableau|excel|r\b|matlab|c\+\+|c#|go|rust|scala|spark|hadoop|tensorflow|pytorch|"
        r"machine learning|deep learning|data science|nlp|computer vision|ci/cd|devops|"
        r"fastapi|django|flask|spring|rails|terraform|ansible|kafka|redis|mongodb|postgres|"
        r"snowflake|dbt|airflow|looker|power bi|salesforce|jira|agile|scrum)\b",
        re.IGNORECASE,
    )

    # Role-family keyword clusters used for title alignment
    _ROLE_FAMILIES = {
        "software": ["software engineer", "developer", "programmer", "swe", "backend", "frontend", "full stack", "full-stack"],
        "data": ["data scientist", "data analyst", "data engineer", "ml engineer", "machine learning", "analytics", "business intelligence"],
        "product": ["product manager", "program manager", "product owner", "pm", "scrum master"],
        "finance": ["finance", "financial analyst", "investment", "accounting", "accounting analyst", "cpa"],
        "marketing": ["marketing", "digital marketing", "brand", "growth", "content", "seo", "social media"],
        "operations": ["operations", "ops", "supply chain", "logistics", "project manager"],
        "research": ["researcher", "research assistant", "research scientist", "ra"],
        "consulting": ["consultant", "consulting", "advisory", "strategy", "management consultant"],
        "healthcare": ["healthcare", "clinical", "medical", "health", "pharma", "biotech"],
        "design": ["designer", "ux", "ui", "product design", "graphic"],
    }

    def score(
        self,
        matched_keywords: List[str],
        jd_keywords: List[str],
        resume_skills: List[str],
        jd_skills: List[str],
        formatting_issues: List[Dict[str, Any]],
        bullets: List[Dict[str, Any]],
        resume_text: str = "",
        jd_requirements: Optional[Dict[str, Any]] = None,
        keyword_frequency_data: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Calculate the full ATS score.

        Args:
            matched_keywords: Keywords present in both resume and JD.
            jd_keywords: All keywords extracted from the JD.
            resume_skills: Skills found in the resume.
            jd_skills: Skills required by the JD.
            formatting_issues: List of formatting issue dicts with severity.
            bullets: List of bullet analysis dicts with score field.
            resume_text: Full resume plain text (for experience alignment).
            jd_requirements: Parsed JD requirements dict (for experience alignment).
            keyword_frequency_data: TF-IDF frequency data from keyword matching service.
        """
        keyword_score = self._score_keywords(
            matched_keywords, jd_keywords, resume_text, keyword_frequency_data
        )
        skills_score = self._score_skills(resume_skills, jd_skills)
        experience_score = self._score_experience_alignment(resume_text, jd_requirements)
        format_score = self._score_formatting(formatting_issues)
        bullet_score = self._score_bullets(bullets)

        total = (
            keyword_score * self.KEYWORD_WEIGHT
            + skills_score * self.SKILLS_WEIGHT
            + experience_score * self.EXPERIENCE_WEIGHT
            + format_score * self.FORMAT_WEIGHT
            + bullet_score * self.BULLET_WEIGHT
        )
        total = max(0.0, min(100.0, total))

        return {
            "total": round(total),
            "grade": self._to_grade(total),
            "breakdown": {
                "keyword_match": round(keyword_score),
                "skills_coverage": round(skills_score),
                "experience_alignment": round(experience_score),
                "formatting_compliance": round(format_score),
                "bullet_strength": round(bullet_score),
            },
        }

    # ── Keyword Match (35%) ────────────────────────────────────────────────────

    def _score_keywords(
        self,
        matched_keywords: List[str],
        jd_keywords: List[str],
        resume_text: str = "",
        frequency_data: Optional[List[Dict[str, Any]]] = None,
    ) -> float:
        """TF-IDF weighted keyword match with section-level boosting."""
        if not jd_keywords:
            return 75.0

        # Build TF-IDF weight map from frequency_data if available
        weight_map: Dict[str, float] = {}
        if frequency_data:
            for item in frequency_data:
                kw = item.get("keyword", "").lower()
                weight_map[kw] = float(item.get("tfidf_score", 1.0))

        # Identify keywords that appear in skills/technical sections of the resume
        # These get a 1.25× boost (enterprise ATS systems weight skills-section matches higher)
        resume_lower = resume_text.lower()
        skills_section_text = self._extract_section(resume_lower, ["skills", "technical skills", "core competencies"])

        total_weight = 0.0
        matched_weight = 0.0
        matched_set_lower = {kw.lower() for kw in matched_keywords}

        for kw in jd_keywords:
            kw_lower = kw.lower()
            base_w = weight_map.get(kw_lower, 1.0)

            # Boost hard skills (enterprise systems prioritize technical keywords)
            if self._HARD_SKILL_PATTERNS.search(kw_lower):
                base_w *= 1.3

            # Boost keywords that are multi-word phrases (more specific = more valuable)
            if " " in kw_lower:
                base_w *= 1.15

            total_weight += base_w
            if kw_lower in matched_set_lower:
                section_boost = 1.25 if kw_lower in skills_section_text else 1.0
                matched_weight += base_w * section_boost

        if total_weight == 0:
            return 75.0

        ratio = min(matched_weight / total_weight, 1.0)

        # Apply a sigmoid-like curve so 60%+ keyword match starts scoring 80+
        # (matching how enterprise ATS normalize scores for shortlisting)
        if ratio >= 0.85:
            score = 95.0 + (ratio - 0.85) * 33.3
        elif ratio >= 0.60:
            score = 75.0 + (ratio - 0.60) * 80.0
        elif ratio >= 0.35:
            score = 45.0 + (ratio - 0.35) * 120.0
        else:
            score = ratio * 128.6

        return min(100.0, max(0.0, score))

    # ── Skills Coverage (25%) ─────────────────────────────────────────────────

    _SKILL_ALIASES: Dict[str, List[str]] = {
        "javascript": ["js", "es6", "es2015", "ecmascript", "vanilla js"],
        "typescript": ["ts"],
        "python": ["py"],
        "react": ["react.js", "reactjs", "react native"],
        "node": ["node.js", "nodejs"],
        "postgresql": ["postgres", "psql"],
        "mongodb": ["mongo"],
        "kubernetes": ["k8s"],
        "machine learning": ["ml"],
        "artificial intelligence": ["ai"],
        "natural language processing": ["nlp"],
        "amazon web services": ["aws"],
        "google cloud platform": ["gcp", "google cloud"],
        "microsoft azure": ["azure"],
        "continuous integration": ["ci", "ci/cd"],
        "continuous deployment": ["cd", "ci/cd"],
        "microsoft excel": ["excel"],
        "microsoft powerpoint": ["powerpoint", "ppt"],
        "microsoft word": ["word", "ms word"],
        "power bi": ["powerbi"],
        "tableau": ["tableau desktop"],
        "sql server": ["mssql", "microsoft sql"],
        "data analysis": ["data analytics", "data analysis"],
        "project management": ["pm", "project mgmt"],
        "agile": ["scrum", "kanban", "agile/scrum"],
        "git": ["github", "gitlab", "version control"],
    }
    # Inverted alias lookup: alias → canonical
    _ALIAS_LOOKUP: Dict[str, str] = {}
    for _canonical, _aliases in _SKILL_ALIASES.items():
        for _alias in _aliases:
            _ALIAS_LOOKUP[_alias] = _canonical

    def _normalize_skill(self, skill: str) -> str:
        """Normalize a skill name to its canonical form."""
        s = skill.lower().strip()
        s_nojssuffix = s.replace(".js", "").replace(".ts", "").replace(".py", "")
        if s in self._ALIAS_LOOKUP:
            return self._ALIAS_LOOKUP[s]
        if s_nojssuffix in self._ALIAS_LOOKUP:
            return self._ALIAS_LOOKUP[s_nojssuffix]
        return s

    def _score_skills(self, resume_skills: List[str], jd_skills: List[str]) -> float:
        """Score skills coverage with alias normalization and category weighting."""
        if not jd_skills:
            return 75.0

        resume_normalized = {self._normalize_skill(s) for s in resume_skills}
        # Also add raw lower forms
        resume_normalized |= {s.lower() for s in resume_skills}

        matched = 0
        hard_skill_matched = 0
        hard_skill_total = 0

        for s in jd_skills:
            s_norm = self._normalize_skill(s)
            s_lower = s.lower()
            s_nojssuffix = s_lower.replace(".js", "").replace(".ts", "")

            is_match = (
                s_norm in resume_normalized
                or s_lower in resume_normalized
                or s_nojssuffix in resume_normalized
            )
            if is_match:
                matched += 1

            is_hard = bool(self._HARD_SKILL_PATTERNS.search(s_lower))
            if is_hard:
                hard_skill_total += 1
                if is_match:
                    hard_skill_matched += 1

        base_ratio = matched / len(jd_skills)

        # Bonus for matching hard skills specifically (enterprise ATS weights technical skills)
        hard_bonus = 0.0
        if hard_skill_total > 0:
            hard_ratio = hard_skill_matched / hard_skill_total
            hard_bonus = hard_ratio * 10.0  # up to 10 bonus points

        score = min(100.0, base_ratio * 100.0 + hard_bonus)
        return score

    # ── Experience Alignment (20%) ────────────────────────────────────────────

    def _score_experience_alignment(
        self, resume_text: str, jd_requirements: Optional[Dict[str, Any]]
    ) -> float:
        """Score how well the candidate's experience aligns with the role.

        Factors (mirroring enterprise ATS hard filters + soft scoring):
          1. Years of experience vs JD requirement  (30 pts)
          2. Role title / function family match     (30 pts)
          3. Seniority level match                  (20 pts)
          4. Responsibility coverage similarity     (20 pts)
        """
        if not resume_text or not jd_requirements:
            return 65.0

        score = 0.0
        resume_lower = resume_text.lower()
        jd_title = jd_requirements.get("job_title", "").lower()
        jd_seniority = jd_requirements.get("seniority_level", "Mid-level")
        jd_responsibilities = jd_requirements.get("responsibilities", [])

        # 1. Years of experience (30 pts)
        resume_years = self._extract_total_years_experience(resume_text)
        required_years = self._extract_required_years(jd_requirements)
        if required_years == 0:
            score += 22  # No requirement stated → neutral/partial credit
        elif resume_years >= required_years:
            score += 30
        elif resume_years > 0:
            score += max(5, 30 * (resume_years / required_years))

        # 2. Role title / function family match (30 pts)
        resume_titles = self._extract_resume_titles(resume_text)
        family_score = self._score_role_family(resume_titles, jd_title)
        score += family_score * 30

        # 3. Seniority match (20 pts)
        resume_seniority = self._detect_resume_seniority(resume_lower)
        seniority_score = self._compare_seniority(resume_seniority, jd_seniority)
        score += seniority_score * 20

        # 4. Responsibility coverage (20 pts)
        if jd_responsibilities:
            resp_text = " ".join(jd_responsibilities).lower()
            resp_words = set(re.findall(r"\b[a-z]{4,}\b", resp_text))
            resume_words = set(re.findall(r"\b[a-z]{4,}\b", resume_lower))
            overlap = resp_words & resume_words
            coverage = len(overlap) / max(len(resp_words), 1)
            score += min(20, coverage * 60)  # 60% overlap → full points

        return min(100.0, max(0.0, score))

    def _extract_total_years_experience(self, resume_text: str) -> float:
        """Estimate total years of professional experience from resume."""
        # Look for date ranges (e.g., "2020 - 2022", "Jan 2021 – Present")
        year_pattern = re.compile(r"\b(20\d{2}|19\d{2})\b")
        years = [int(y) for y in year_pattern.findall(resume_text)]
        if len(years) < 2:
            return 0.0
        return float(max(years) - min(years))

    def _extract_required_years(self, jd_requirements: Dict[str, Any]) -> float:
        """Extract required years of experience from JD requirements."""
        # Check job title for year clues, and responsibilities text
        jd_title = jd_requirements.get("job_title", "")
        resp_text = " ".join(jd_requirements.get("responsibilities", []))
        full_text = (jd_title + " " + resp_text).lower()

        patterns = [
            r"(\d+)\+?\s*(?:to\s*\d+)?\s*years?\s*(?:of\s*)?(?:relevant\s*)?experience",
            r"(\d+)\+\s*yr",
            r"minimum\s*(?:of\s*)?(\d+)\s*years?",
        ]
        for pattern in patterns:
            m = re.search(pattern, full_text)
            if m:
                return float(m.group(1))

        # Infer from seniority if no explicit requirement
        seniority = jd_requirements.get("seniority_level", "Mid-level")
        return {"Junior": 0.0, "Mid-level": 2.0, "Senior": 5.0, "Manager": 7.0}.get(seniority, 2.0)

    def _extract_resume_titles(self, resume_text: str) -> List[str]:
        """Extract job titles from the experience section of the resume."""
        titles: List[str] = []
        lines = resume_text.split("\n")
        in_experience = False
        for line in lines:
            stripped = line.strip()
            if re.search(r"EXPERIENCE|WORK HISTORY|EMPLOYMENT", stripped, re.IGNORECASE):
                in_experience = True
                continue
            if in_experience and re.search(
                r"^(EDUCATION|PROJECTS|SKILLS|LEADERSHIP|VOLUNTEER|RESEARCH|HONORS|AWARDS)",
                stripped, re.IGNORECASE
            ):
                in_experience = False
            if in_experience and stripped:
                # Job titles are typically short italic lines after the company name
                if len(stripped) < 80 and not stripped.startswith("•") and not re.search(r"\d{4}", stripped):
                    titles.append(stripped.lower())
        return titles

    def _score_role_family(self, resume_titles: List[str], jd_title: str) -> float:
        """Return 0-1 score for how well resume titles match the JD role family."""
        if not jd_title:
            return 0.5

        # Find which family the JD belongs to
        jd_family = None
        for family, keywords in self._ROLE_FAMILIES.items():
            if any(kw in jd_title for kw in keywords):
                jd_family = family
                break

        if jd_family is None:
            # Direct word overlap
            jd_words = set(re.findall(r"\b[a-z]{4,}\b", jd_title))
            if not resume_titles or not jd_words:
                return 0.5
            best = max(
                len(jd_words & set(re.findall(r"\b[a-z]{4,}\b", t))) / len(jd_words)
                for t in resume_titles
            ) if resume_titles else 0
            return min(1.0, best)

        family_keywords = self._ROLE_FAMILIES[jd_family]
        for title in resume_titles:
            if any(kw in title for kw in family_keywords):
                return 1.0
        # Partial: any family keyword anywhere in resume
        resume_all = " ".join(resume_titles)
        partial = sum(1 for kw in family_keywords if kw in resume_all)
        return min(0.8, partial / max(len(family_keywords), 1))

    def _detect_resume_seniority(self, resume_lower: str) -> str:
        if any(w in resume_lower for w in ("senior", "sr.", "sr ", "lead ", "principal", "staff engineer", "head of")):
            return "Senior"
        if any(w in resume_lower for w in ("manager", "director", "vp ", "vice president")):
            return "Manager"
        if any(w in resume_lower for w in ("junior", "jr.", "associate", "entry level", "intern")):
            return "Junior"
        return "Mid-level"

    def _compare_seniority(self, resume_seniority: str, jd_seniority: str) -> float:
        rank = {"Junior": 1, "Mid-level": 2, "Senior": 3, "Manager": 4}
        r = rank.get(resume_seniority, 2)
        j = rank.get(jd_seniority, 2)
        diff = abs(r - j)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.65
        else:
            return 0.25

    def _extract_section(self, resume_lower: str, section_names: List[str]) -> str:
        """Extract text from a named section of the resume."""
        for name in section_names:
            pattern = re.compile(
                rf"{re.escape(name)}[\s\S]{{0,2000}}?(?=\n[A-Z]{{4,}}|\Z)",
                re.IGNORECASE,
            )
            m = pattern.search(resume_lower)
            if m:
                return m.group(0)
        return ""

    # ── Formatting Compliance (10%) ───────────────────────────────────────────

    def _score_formatting(self, formatting_issues: List[Dict[str, Any]]) -> float:
        score = 100.0
        for issue in formatting_issues:
            severity = issue.get("severity", "info")
            if severity == "critical":
                score -= 12
            elif severity == "warning":
                score -= 5
            else:
                score -= 2
        return max(0.0, score)

    # ── Bullet Strength (10%) ─────────────────────────────────────────────────

    def _score_bullets(self, bullets: List[Dict[str, Any]]) -> float:
        if not bullets:
            return 55.0
        scores = [b.get("score", 5) for b in bullets]
        avg = sum(scores) / len(scores)
        return min(100.0, (avg / 10.0) * 100.0)

    # ── Grade conversion ──────────────────────────────────────────────────────

    def _to_grade(self, score: float) -> str:
        if score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 67:
            return "D+"
        elif score >= 60:
            return "D"
        else:
            return "F"

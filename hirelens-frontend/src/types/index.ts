// All TypeScript interfaces for HirePort AI

export interface ATSScoreBreakdown {
  keyword_match: number
  skills_coverage: number
  formatting_compliance: number
  bullet_strength: number
}

export interface SkillGap {
  skill: string
  category: 'Technical' | 'Soft' | 'Certification' | 'Tool'
  importance: 'critical' | 'recommended' | 'nice-to-have'
}

export interface BulletAnalysis {
  original: string
  score: number
  issues: string[]
  rewritten: string
}

export interface FormattingIssue {
  issue: string
  severity: 'critical' | 'warning' | 'info'
  fix: string
}

export interface KeywordChartData {
  keyword: string
  resume_count: number
  jd_count: number
  matched: boolean
}

export interface SkillOverlapData {
  subject: string
  resume: number
  jd: number
}

export interface AnalysisResponse {
  ats_score: number
  grade: string
  score_breakdown: ATSScoreBreakdown
  matched_keywords: string[]
  missing_keywords: string[]
  skill_gaps: SkillGap[]
  bullet_analysis: BulletAnalysis[]
  formatting_issues: FormattingIssue[]
  job_fit_explanation: string
  top_strengths: string[]
  top_gaps: string[]
  keyword_chart_data: KeywordChartData[]
  skills_overlap_data: SkillOverlapData[]
  resume_text?: string
}

export interface RewriteEntry {
  org: string
  location: string
  date: string
  title: string
  bullets: string[]
  details: string[]
}

export interface RewriteSection {
  title: string
  content: string
  entries: RewriteEntry[]
}

export interface RewriteHeader {
  name: string
  contact: string
}

export interface RewriteResponse {
  header: RewriteHeader
  sections: RewriteSection[]
  full_text: string
  template_type: string
}

export interface CoverLetterResponse {
  cover_letter: string
  tone: string
}

export interface InterviewQuestion {
  question: string
  star_framework: string
  category?: 'behavioral' | 'technical' | 'role-specific'
}

export interface InterviewPrepResponse {
  questions: InterviewQuestion[]
}

// ─── Recruiter Roast / Red Team ───
export interface RedFlag {
  severity: 'critical' | 'high' | 'medium' | 'low'
  category: string
  finding: string
  recruiter_quote: string
  fix_suggestion: string
}

export interface SeniorityProfile {
  tier: 'student' | 'ic' | 'manager' | 'director' | 'executive'
  yoe: number
  weights: Record<string, number>
  guidance: string
  signals?: Record<string, boolean>
}

export interface RedTeamResponse {
  reject_probability: number
  verdict: 'PASS' | 'BORDERLINE' | 'REJECT'
  cynical_summary: string
  red_flags: RedFlag[]
  top_3_fixes_to_unblock: string[]
  seniority: SeniorityProfile
}

// ─── LinkedIn Audit ───
export interface LinkedInAuditResponse {
  score: number
  verdict: string
  buzzword_count: number
  buzzwords_found: string[]
  has_quantification: boolean
  word_count: number
  top_issues: string[]
  top_strengths: string[]
  rewritten_first_sentence: string
  shareable_summary: string
}

export type ApplicationStatus = 'Applied' | 'Interview' | 'Offer' | 'Rejected'

export interface TrackerApplication {
  id: string
  company: string
  role: string
  date_applied: string
  ats_score: number
  status: ApplicationStatus
  created_at: string
}

export interface AnalysisState {
  isLoading: boolean
  error: string | null
  result: AnalysisResponse | null
  resumeFile: File | null
  jobDescription: string
}

export type AnalysisAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_RESULT'; payload: AnalysisResponse }
  | { type: 'SET_RESUME_FILE'; payload: File | null }
  | { type: 'SET_JD'; payload: string }
  | { type: 'RESET' }


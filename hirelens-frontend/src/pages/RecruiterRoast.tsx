import { useState } from 'react'
import { motion } from 'framer-motion'
import { Flame, AlertOctagon, AlertTriangle, Info, Zap, RefreshCw, ChevronRight } from 'lucide-react'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { GlowButton } from '@/components/ui/GlowButton'
import { useAnalysisContext } from '@/context/AnalysisContext'
import { runRedTeam } from '@/services/api'
import type { RedTeamResponse } from '@/types'

const SEVERITY_STYLES: Record<string, { icon: any; color: string; bg: string; border: string }> = {
  critical: { icon: AlertOctagon, color: '#EF4444', bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.35)' },
  high:     { icon: AlertTriangle, color: '#F59E0B', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.35)' },
  medium:   { icon: Info, color: '#3B82F6', bg: 'rgba(59,130,246,0.08)', border: 'rgba(59,130,246,0.30)' },
  low:      { icon: Info, color: '#94A3B8', bg: 'rgba(148,163,184,0.06)', border: 'rgba(148,163,184,0.25)' },
}

const VERDICT_COLOR: Record<string, string> = {
  PASS: '#10B981',
  BORDERLINE: '#F59E0B',
  REJECT: '#EF4444',
}

export default function RecruiterRoast() {
  const { state } = useAnalysisContext()
  const [result, setResult] = useState<RedTeamResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const resumeText = state.result?.resume_text || ''
  const jobDescription = state.jobDescription || ''
  const canRun = resumeText.length > 50 && jobDescription.length > 20

  const handleRun = async () => {
    if (!canRun) return
    setLoading(true)
    try {
      const r = await runRedTeam(resumeText, jobDescription)
      setResult(r)
    } finally {
      setLoading(false)
    }
  }

  const rejectPct = result ? Math.round(result.reject_probability * 100) : 0
  const verdictColor = result ? VERDICT_COLOR[result.verdict] || '#F59E0B' : '#F59E0B'

  return (
    <PageWrapper className="min-h-screen bg-bg-base">
      <div className="max-w-4xl mx-auto px-4 py-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-2.5 mb-2">
            <div className="w-9 h-9 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center justify-center">
              <Flame size={18} className="text-red-400" />
            </div>
            <h1 className="font-display text-3xl font-bold text-text-primary">
              Recruiter <span className="text-red-400">Roast</span>
            </h1>
          </div>
          <p className="text-text-secondary text-sm max-w-2xl">
            A cynical Fortune 500 recruiter reads your resume and tries to <em>reject</em> it. Get the brutal feedback most AI tools won't give you — before a real recruiter does.
          </p>
        </motion.div>

        {!canRun && (
          <div className="mb-6 p-4 rounded-xl bg-yellow-500/[0.06] border border-yellow-500/20 text-sm text-text-secondary">
            Run an analysis first on the <strong className="text-text-primary">/analyze</strong> page so we have a resume + job description to roast.
          </div>
        )}

        {!result && canRun && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center py-10 gap-4"
          >
            <p className="text-text-secondary text-sm text-center max-w-md">
              Ready when you are. This is brutal — that's the point.
            </p>
            <GlowButton onClick={handleRun} isLoading={loading}>
              <Zap size={14} />
              {loading ? 'Roasting…' : 'Start the Roast'}
            </GlowButton>
          </motion.div>
        )}

        {result && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            {/* Verdict banner */}
            <div
              className="rounded-2xl border p-6"
              style={{ borderColor: `${verdictColor}55`, background: `${verdictColor}0D` }}
            >
              <div className="flex items-start justify-between gap-4 flex-wrap">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span
                      className="text-[11px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-full"
                      style={{ background: `${verdictColor}22`, color: verdictColor }}
                    >
                      {result.verdict}
                    </span>
                    <span className="text-text-muted text-xs">
                      Tier: <span className="text-text-primary capitalize font-semibold">{result.seniority.tier}</span> · {result.seniority.yoe} YoE
                    </span>
                  </div>
                  <p className="text-base text-text-primary leading-relaxed italic max-w-2xl">
                    "{result.cynical_summary}"
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-[10px] uppercase tracking-widest text-text-muted mb-1">Reject Probability</div>
                  <div className="font-display text-4xl font-bold" style={{ color: verdictColor }}>
                    {rejectPct}%
                  </div>
                </div>
              </div>
            </div>

            {/* Top 3 unblocking fixes */}
            {result.top_3_fixes_to_unblock?.length > 0 && (
              <div className="rounded-2xl border border-white/[0.06] bg-bg-surface/50 p-5">
                <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider mb-3">
                  Top 3 Fixes That Unblock You
                </h3>
                <ul className="space-y-2">
                  {result.top_3_fixes_to_unblock.map((fix, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-text-secondary">
                      <span className="flex-shrink-0 w-5 h-5 rounded-full bg-accent-primary/15 text-accent-primary text-[11px] font-bold flex items-center justify-center mt-0.5">
                        {i + 1}
                      </span>
                      <span>{fix}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Red flags */}
            <div>
              <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider mb-3">
                Red Flags ({result.red_flags.length})
              </h3>
              <div className="space-y-3">
                {result.red_flags.map((flag, i) => {
                  const sty = SEVERITY_STYLES[flag.severity] || SEVERITY_STYLES.medium
                  const Icon = sty.icon
                  return (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.04 }}
                      className="rounded-xl border p-4"
                      style={{ borderColor: sty.border, background: sty.bg }}
                    >
                      <div className="flex items-start gap-3">
                        <Icon size={16} style={{ color: sty.color, marginTop: 2 }} className="flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                            <span
                              className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded"
                              style={{ background: `${sty.color}22`, color: sty.color }}
                            >
                              {flag.severity}
                            </span>
                            <span className="text-[11px] text-text-muted capitalize">{flag.category.replace(/_/g, ' ')}</span>
                          </div>
                          <p className="text-sm text-text-primary font-medium leading-relaxed mb-2">{flag.finding}</p>
                          {flag.recruiter_quote && (
                            <p className="text-xs text-text-secondary italic mb-2 border-l-2 pl-3 py-0.5" style={{ borderColor: sty.color }}>
                              "{flag.recruiter_quote}"
                            </p>
                          )}
                          {flag.fix_suggestion && (
                            <div className="flex items-start gap-1.5 text-xs text-text-secondary mt-2">
                              <ChevronRight size={12} className="text-accent-primary flex-shrink-0 mt-0.5" />
                              <span><strong className="text-accent-primary">Fix:</strong> {flag.fix_suggestion}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>

            <div className="text-center pt-4">
              <GlowButton variant="ghost" size="sm" onClick={handleRun} isLoading={loading}>
                <RefreshCw size={13} />
                Roast Again
              </GlowButton>
            </div>
          </motion.div>
        )}
      </div>
    </PageWrapper>
  )
}

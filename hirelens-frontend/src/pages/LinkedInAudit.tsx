import { useState } from 'react'
import { motion } from 'framer-motion'
import { Linkedin, Zap, Share2, AlertTriangle, CheckCircle2, Sparkles } from 'lucide-react'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { GlowButton } from '@/components/ui/GlowButton'
import { runLinkedInAudit } from '@/services/api'
import type { LinkedInAuditResponse } from '@/types'
import toast from 'react-hot-toast'

const SAMPLE = `Passionate, results-driven product leader with a proven track record of driving cross-functional teams to deliver innovative solutions. I am a strategic thinker who leverages data to move the needle and drive results. Looking for my next big opportunity to make an impact.`

function scoreColor(score: number): string {
  if (score >= 85) return '#10B981'
  if (score >= 65) return '#3B82F6'
  if (score >= 45) return '#F59E0B'
  return '#EF4444'
}

export default function LinkedInAudit() {
  const [text, setText] = useState('')
  const [result, setResult] = useState<LinkedInAuditResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const handleAudit = async () => {
    if (text.trim().length < 30) {
      toast.error('Paste at least a few sentences (30+ characters).')
      return
    }
    setLoading(true)
    try {
      const r = await runLinkedInAudit(text)
      setResult(r)
    } finally {
      setLoading(false)
    }
  }

  const handleShare = () => {
    if (!result) return
    navigator.clipboard.writeText(result.shareable_summary + '\n\nGet yours at HireLens AI')
    toast.success('Copied — paste it on LinkedIn 👀')
  }

  const color = result ? scoreColor(result.score) : '#3B82F6'

  return (
    <PageWrapper className="min-h-screen bg-bg-base">
      <div className="max-w-3xl mx-auto px-4 py-10">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-4">
            <Linkedin size={12} />
            Free · No signup
          </div>
          <h1 className="font-display text-4xl sm:text-5xl font-bold text-text-primary mb-3">
            LinkedIn <span className="text-blue-400">About</span> Audit
          </h1>
          <p className="text-text-secondary text-base max-w-xl mx-auto">
            Paste your LinkedIn About section. Get a brutal Recruiter Impression Score in 3 seconds.
          </p>
        </motion.div>

        {/* Input */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl border border-white/[0.08] bg-bg-surface/50 p-5 mb-5"
        >
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your LinkedIn About section here…"
            rows={8}
            className="w-full bg-bg-elevated/60 border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-text-primary placeholder:text-text-muted resize-none focus:outline-none focus:border-blue-400/40 transition-colors"
          />
          <div className="flex items-center justify-between mt-3 flex-wrap gap-2">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setText(SAMPLE)}
                className="text-xs text-text-muted hover:text-accent-primary transition-colors"
              >
                Try a sample
              </button>
              <span className="text-xs text-text-muted">{text.length} chars</span>
            </div>
            <GlowButton onClick={handleAudit} isLoading={loading} size="sm">
              <Zap size={13} />
              Audit Me
            </GlowButton>
          </div>
        </motion.div>

        {/* Result */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-5"
          >
            {/* Score banner */}
            <div
              className="rounded-2xl border p-7 text-center"
              style={{ borderColor: `${color}55`, background: `${color}0D` }}
            >
              <div className="text-[10px] uppercase tracking-widest text-text-muted mb-1">Recruiter Impression Score</div>
              <div className="font-display text-7xl font-bold mb-2" style={{ color }}>
                {result.score}
                <span className="text-2xl text-text-muted">/100</span>
              </div>
              <p className="text-sm text-text-secondary italic">{result.verdict}</p>

              <div className="flex items-center justify-center gap-4 mt-4 text-xs text-text-muted flex-wrap">
                <span>{result.word_count} words</span>
                <span>·</span>
                <span>{result.buzzword_count} buzzwords</span>
                <span>·</span>
                <span>{result.has_quantification ? '✓ quantified' : '✗ no metrics'}</span>
              </div>
            </div>

            {/* Issues */}
            {result.top_issues.length > 0 && (
              <div className="rounded-2xl border border-red-500/20 bg-red-500/[0.04] p-5">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-red-400 uppercase tracking-wider mb-3">
                  <AlertTriangle size={14} />
                  What a recruiter sees in 6 seconds
                </h3>
                <ul className="space-y-2">
                  {result.top_issues.map((issue, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                      <span className="text-red-400 mt-0.5">✗</span>
                      <span>{issue}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Buzzwords */}
            {result.buzzwords_found.length > 0 && (
              <div className="rounded-2xl border border-yellow-500/20 bg-yellow-500/[0.04] p-5">
                <h3 className="text-sm font-semibold text-yellow-400 uppercase tracking-wider mb-3">
                  Buzzwords to cut
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.buzzwords_found.map((b) => (
                    <span key={b} className="text-xs px-2 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/30 text-yellow-300">
                      {b}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Strengths */}
            {result.top_strengths.length > 0 && (
              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/[0.04] p-5">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-emerald-400 uppercase tracking-wider mb-3">
                  <CheckCircle2 size={14} />
                  What's working
                </h3>
                <ul className="space-y-1.5">
                  {result.top_strengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                      <span className="text-emerald-400 mt-0.5">✓</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* AI rewrite of opening line */}
            {result.rewritten_first_sentence && (
              <div className="rounded-2xl border border-accent-primary/20 bg-accent-primary/[0.04] p-5">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-accent-primary uppercase tracking-wider mb-3">
                  <Sparkles size={14} />
                  Punchier opening line
                </h3>
                <p className="text-base text-text-primary italic leading-relaxed">
                  "{result.rewritten_first_sentence}"
                </p>
              </div>
            )}

            {/* Share + upsell */}
            <div className="flex items-center justify-between gap-3 flex-wrap pt-2">
              <GlowButton variant="ghost" size="sm" onClick={handleShare}>
                <Share2 size={13} />
                Copy shareable summary
              </GlowButton>
              <a
                href="/analyze"
                className="text-sm text-accent-primary hover:underline font-medium"
              >
                Get your full resume score →
              </a>
            </div>
          </motion.div>
        )}
      </div>
    </PageWrapper>
  )
}

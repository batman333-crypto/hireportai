import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Zap,
  Search,
  ListChecks,
  Wrench,
  ArrowRight,
  Loader2,
  CheckCircle2,
  XCircle,
  AlertCircle,
} from 'lucide-react'
import { diagnoseResume } from '@/services/api'
import type { DiagnosisResponse, TopFix } from '@/types'

interface ATSDiagnosisProps {
  resumeText: string
  jobDescription: string
  targetRole?: string
}

// ── Helpers ──────────────────────────────────────────────────────────────────

const IMPACT_CONFIG = {
  HIGH: { color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20', dot: 'bg-red-400' },
  MEDIUM: { color: 'text-yellow-400', bg: 'bg-yellow-500/10 border-yellow-500/20', dot: 'bg-yellow-400' },
  LOW: { color: 'text-green-400', bg: 'bg-green-500/10 border-green-500/20', dot: 'bg-green-400' },
}

function ImpactBadge({ impact }: { impact: string }) {
  const cfg = IMPACT_CONFIG[impact as keyof typeof IMPACT_CONFIG] ?? IMPACT_CONFIG.MEDIUM
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${cfg.bg} ${cfg.color}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {impact}
    </span>
  )
}

function SectionHeader({ icon, label, count, color }: { icon: React.ReactNode; label: string; count?: number; color: string }) {
  return (
    <div className={`flex items-center gap-2 mb-4`}>
      <span className={`p-1.5 rounded-lg ${color}`}>{icon}</span>
      <h3 className="font-semibold text-white text-sm tracking-wide uppercase">{label}</h3>
      {count !== undefined && (
        <span className="ml-auto text-xs font-bold bg-white/10 text-gray-300 px-2 py-0.5 rounded-full">
          {count}
        </span>
      )}
    </div>
  )
}

// ── ATS Killers ───────────────────────────────────────────────────────────────

function ATSKillersPanel({ killers }: { killers: DiagnosisResponse['ats_killers'] }) {
  return (
    <div className="bg-[#161b22] border border-red-500/20 rounded-2xl p-5">
      <SectionHeader
        icon={<XCircle className="w-4 h-4 text-red-400" />}
        label="ATS Killers"
        count={killers.length}
        color="bg-red-500/10"
      />
      {killers.length === 0 ? (
        <p className="text-sm text-green-400 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" /> No ATS killers detected — formatting looks clean.
        </p>
      ) : (
        <div className="space-y-3">
          {killers.map((k, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.06 }}
              className="border border-red-500/15 rounded-xl p-4 bg-red-500/5"
            >
              <p className="text-sm font-semibold text-red-300 mb-1">{k.issue}</p>
              <p className="text-xs text-gray-400 mb-2 leading-relaxed">{k.impact}</p>
              <div className="flex items-start gap-2 text-xs text-emerald-400">
                <ArrowRight className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                <span>{k.fix}</span>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Section Diagnosis ─────────────────────────────────────────────────────────

function SectionDiagnosisPanel({ sections }: { sections: DiagnosisResponse['section_diagnosis'] }) {
  const [expanded, setExpanded] = useState<number | null>(null)

  return (
    <div className="bg-[#161b22] border border-yellow-500/20 rounded-2xl p-5">
      <SectionHeader
        icon={<Search className="w-4 h-4 text-yellow-400" />}
        label="Section-by-Section Diagnosis"
        count={sections.length}
        color="bg-yellow-500/10"
      />
      <div className="space-y-2">
        {sections.map((s, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="border border-white/5 rounded-xl overflow-hidden"
          >
            <button
              onClick={() => setExpanded(expanded === i ? null : i)}
              className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-white/5 transition-colors"
            >
              <div className="flex items-center gap-3">
                <AlertCircle className="w-4 h-4 text-yellow-400 shrink-0" />
                <span className="text-sm font-medium text-white">{s.section}</span>
              </div>
              {expanded === i
                ? <ChevronUp className="w-4 h-4 text-gray-500" />
                : <ChevronDown className="w-4 h-4 text-gray-500" />}
            </button>
            <AnimatePresence>
              {expanded === i && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="px-4 pb-4 space-y-3 border-t border-white/5 pt-3">
                    <div>
                      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Weakest Item</p>
                      <p className="text-sm text-yellow-300 italic">"{s.weakest_item}"</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Why It Fails</p>
                      <p className="text-sm text-gray-300 leading-relaxed">{s.reason}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Fix</p>
                      <p className="text-sm text-emerald-400 leading-relaxed">{s.fix}</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// ── Missing Signals ───────────────────────────────────────────────────────────

function MissingSignalsPanel({ signals }: { signals: string[] }) {
  return (
    <div className="bg-[#161b22] border border-purple-500/20 rounded-2xl p-5">
      <SectionHeader
        icon={<ListChecks className="w-4 h-4 text-purple-400" />}
        label="Missing Signals"
        count={signals.length}
        color="bg-purple-500/10"
      />
      {signals.length === 0 ? (
        <p className="text-sm text-green-400 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" /> All key signals present for this role.
        </p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {signals.map((s, i) => (
            <motion.span
              key={i}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.03 }}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-purple-500/10 border border-purple-500/20 text-purple-300"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
              {s}
            </motion.span>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Top Fix Card ──────────────────────────────────────────────────────────────

function TopFixCard({ fix }: { fix: TopFix }) {
  const [showAfter, setShowAfter] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: fix.rank * 0.07 }}
      className="border border-white/8 rounded-2xl overflow-hidden bg-[#0d1117]"
    >
      {/* Header */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-white/5">
        <span className="flex items-center justify-center w-7 h-7 rounded-full bg-blue-500/20 text-blue-400 text-xs font-bold shrink-0">
          {fix.rank}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white truncate">{fix.title}</p>
        </div>
        <ImpactBadge impact={fix.impact} />
      </div>

      {/* Before / After */}
      <div className="p-5 space-y-3">
        <div className="bg-red-500/5 border border-red-500/15 rounded-xl p-3">
          <p className="text-xs text-red-400 uppercase tracking-wider mb-1.5 font-medium">Before</p>
          <p className="text-sm text-gray-300 leading-relaxed">{fix.before}</p>
        </div>

        <button
          onClick={() => setShowAfter(!showAfter)}
          className="w-full flex items-center justify-center gap-2 py-2 text-xs text-blue-400 hover:text-blue-300 transition-colors"
        >
          {showAfter ? 'Hide fix' : 'Show optimized version'}
          {showAfter ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        <AnimatePresence>
          {showAfter && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden space-y-3"
            >
              <div className="bg-emerald-500/5 border border-emerald-500/15 rounded-xl p-3">
                <p className="text-xs text-emerald-400 uppercase tracking-wider mb-1.5 font-medium">After (XYZ Formula)</p>
                <p className="text-sm text-gray-200 leading-relaxed">{fix.after}</p>
              </div>
              <div className="bg-blue-500/5 border border-blue-500/10 rounded-xl p-3">
                <p className="text-xs text-blue-400 uppercase tracking-wider mb-1.5 font-medium">Why This Works</p>
                <p className="text-sm text-gray-400 leading-relaxed">{fix.why}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

// ── Top Fixes Panel ────────────────────────────────────────────────────────────

function TopFixesPanel({ fixes }: { fixes: TopFix[] }) {
  return (
    <div className="bg-[#161b22] border border-blue-500/20 rounded-2xl p-5">
      <SectionHeader
        icon={<Wrench className="w-4 h-4 text-blue-400" />}
        label="Top Fixes — XYZ Formula Rewrites"
        count={fixes.length}
        color="bg-blue-500/10"
      />
      <div className="space-y-3">
        {fixes.map((f) => (
          <TopFixCard key={f.rank} fix={f} />
        ))}
      </div>
    </div>
  )
}

// ── Overall Verdict ────────────────────────────────────────────────────────────

function VerdictBanner({ verdict, role }: { verdict: string; role: string }) {
  return (
    <div className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 border border-blue-500/20 rounded-2xl p-5">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-xl bg-blue-500/20 shrink-0">
          <Zap className="w-5 h-5 text-blue-400" />
        </div>
        <div>
          {role && (
            <p className="text-xs text-blue-400 uppercase tracking-wider mb-1 font-medium">
              Target: {role}
            </p>
          )}
          <p className="text-sm text-gray-200 leading-relaxed">{verdict}</p>
        </div>
      </div>
    </div>
  )
}

// ── Main Component ─────────────────────────────────────────────────────────────

export default function ATSDiagnosis({ resumeText, jobDescription, targetRole = '' }: ATSDiagnosisProps) {
  const [isRunning, setIsRunning] = useState(false)
  const [result, setResult] = useState<DiagnosisResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runDiagnosis = async () => {
    setIsRunning(true)
    setError(null)
    try {
      const data = await diagnoseResume({
        resume_text: resumeText,
        job_description: jobDescription,
        target_role: targetRole,
      })
      setResult(data)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Diagnosis failed — please try again.'
      setError(message)
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Trigger button */}
      {!result && !isRunning && (
        <motion.button
          onClick={runDiagnosis}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          className="w-full flex items-center justify-center gap-3 py-4 px-6 rounded-2xl font-semibold text-sm
            bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500
            text-white shadow-lg shadow-red-900/30 transition-all duration-200"
        >
          <AlertTriangle className="w-5 h-5" />
          Run Full ATS Diagnosis
          <span className="text-xs opacity-75 font-normal">(finds everything killing your resume)</span>
        </motion.button>
      )}

      {/* Error state */}
      {error && !isRunning && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-sm text-red-400">
          {error}
          <button onClick={runDiagnosis} className="ml-3 underline text-red-300 hover:text-red-200">
            Retry
          </button>
        </div>
      )}

      {/* Loading state */}
      {isRunning && (
        <div className="flex flex-col items-center justify-center gap-4 py-12">
          <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
          <div className="text-center">
            <p className="text-sm font-semibold text-white mb-1">Diagnosing your resume…</p>
            <p className="text-xs text-gray-500">Running full ATS + keyword + section analysis. Takes ~30s.</p>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Verdict */}
          {result.overall_verdict && (
            <VerdictBanner verdict={result.overall_verdict} role={result.target_role} />
          )}

          {/* ATS Killers */}
          <ATSKillersPanel killers={result.ats_killers} />

          {/* Section Diagnosis */}
          {result.section_diagnosis.length > 0 && (
            <SectionDiagnosisPanel sections={result.section_diagnosis} />
          )}

          {/* Missing Signals */}
          <MissingSignalsPanel signals={result.missing_signals} />

          {/* Top Fixes */}
          {result.top_fixes.length > 0 && (
            <TopFixesPanel fixes={result.top_fixes} />
          )}

          {/* Re-run */}
          <button
            onClick={runDiagnosis}
            disabled={isRunning}
            className="w-full text-xs text-gray-500 hover:text-gray-400 py-2 transition-colors"
          >
            Re-run diagnosis
          </button>
        </motion.div>
      )}
    </div>
  )
}

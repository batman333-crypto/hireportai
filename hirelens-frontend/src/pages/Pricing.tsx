import { useCallback, useRef } from 'react'
import { motion, useMotionValue, useSpring } from 'framer-motion'
import { Check, X, Sparkles, Zap, Crown, CheckCircle2, Rocket, Shield } from 'lucide-react'
import { Link } from 'react-router-dom'
import clsx from 'clsx'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { useUsage } from '@/context/UsageContext'
import type { PlanType } from '@/context/UsageContext'

// ─── 3D Tilt Card ───
function TiltCard({ children, className = '', intensity = 6 }: { children: React.ReactNode; className?: string; intensity?: number }) {
  const ref = useRef<HTMLDivElement>(null)
  const rotateX = useMotionValue(0)
  const rotateY = useMotionValue(0)
  const springX = useSpring(rotateX, { stiffness: 200, damping: 20 })
  const springY = useSpring(rotateY, { stiffness: 200, damping: 20 })

  const handleMouse = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const el = ref.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    const x = (e.clientX - rect.left) / rect.width - 0.5
    const y = (e.clientY - rect.top) / rect.height - 0.5
    rotateX.set(y * -intensity)
    rotateY.set(x * intensity)
  }, [rotateX, rotateY, intensity])

  const handleLeave = useCallback(() => {
    rotateX.set(0)
    rotateY.set(0)
  }, [rotateX, rotateY])

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouse}
      onMouseLeave={handleLeave}
      style={{ rotateX: springX, rotateY: springY, transformPerspective: 1000 }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

interface PlanFeature {
  text: string
  included: boolean
}

interface PlanConfig {
  name: string
  planKey: PlanType
  price: number
  period: string
  description: string
  icon: React.ElementType
  features: PlanFeature[]
  cta: string
  popular?: boolean
  accent: string
}

const plans: PlanConfig[] = [
  {
    name: 'Free',
    planKey: 'free',
    price: 0,
    period: '',
    description: 'Try the platform with 3 free resume analyses.',
    icon: Zap,
    accent: 'text-text-secondary',
    cta: 'Start Free',
    features: [
      { text: '3 resume analyses', included: true },
      { text: 'ATS match score', included: true },
      { text: 'Matched keywords', included: true },
      { text: 'Missing keywords', included: true },
      { text: 'Basic dashboard results', included: true },
      { text: 'Unlimited scans', included: false },
      { text: 'AI resume rewriting', included: false },
      { text: 'Cover letter generation', included: false },
      { text: 'Optimized resume download', included: false },
    ],
  },
  {
    name: 'Pro',
    planKey: 'pro',
    price: 10,
    period: '/mo',
    description: 'Unlimited ATS scans with full analytics dashboard.',
    icon: Sparkles,
    accent: 'text-accent-primary',
    cta: 'Upgrade to Pro',
    popular: true,
    features: [
      { text: 'Unlimited ATS scans', included: true },
      { text: 'Full ATS compatibility score', included: true },
      { text: 'Keyword match analysis', included: true },
      { text: 'Missing skills detection', included: true },
      { text: 'Skill gap insights', included: true },
      { text: 'ATS pass probability rating', included: true },
      { text: 'Detailed dashboard analytics', included: true },
      { text: 'AI bullet point suggestions', included: true },
      { text: 'Full AI resume rewrite', included: false },
      { text: 'Formatted resume download', included: false },
      { text: 'Cover letter generation', included: false },
    ],
  },
  {
    name: 'Premium',
    planKey: 'premium',
    price: 15,
    period: '/mo',
    description: 'Full automation — rewrite, cover letter, and export.',
    icon: Crown,
    accent: 'text-accent-secondary',
    cta: 'Get Premium',
    features: [
      { text: 'Everything in Pro', included: true },
      { text: 'AI resume rewriting', included: true },
      { text: 'Optimized bullet generation', included: true },
      { text: 'Auto-tailored resume for JD', included: true },
      { text: 'Export improved resume as PDF', included: true },
      { text: 'Professional resume formatting', included: true },
      { text: 'AI-generated cover letter', included: true },
      { text: 'Multiple cover letter tones', included: true },
      { text: 'Priority processing', included: true },
    ],
  },
]

const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
}

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] } },
}

export default function Pricing() {
  const { usage, upgradePlan, addRushCredits } = useUsage()

  const handleCta = (plan: PlanConfig) => {
    if (plan.planKey === 'free') return
    if (usage.plan === plan.planKey) return
    upgradePlan(plan.planKey)
  }

  return (
    <PageWrapper className="min-h-screen bg-bg-base relative overflow-hidden">
      {/* Aurora background */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div
          className="aurora-blob w-[600px] h-[600px] top-[-15%] left-[10%] opacity-[0.08]"
          style={{ background: 'radial-gradient(circle, #DC2626, transparent 65%)' }}
        />
        <div
          className="aurora-blob aurora-blob-2 w-[500px] h-[500px] bottom-[-10%] right-[-5%] opacity-[0.06]"
          style={{ background: 'radial-gradient(circle, #7C3AED, transparent 65%)' }}
        />
        <div className="absolute inset-0 grid-pattern opacity-20" />
      </div>

      <div className="max-w-5xl mx-auto px-5 py-20 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full border border-accent-primary/15 text-accent-primary text-xs font-medium mb-6 glow-hover"
            style={{ background: 'rgba(220,38,38,0.06)' }}
          >
            <Sparkles size={11} />
            Simple, transparent pricing
          </motion.div>
          <h1 className="font-display text-4xl sm:text-5xl font-bold tracking-tight mb-4">
            Choose your{' '}
            <span className="shimmer-text">plan</span>
          </h1>
          <p className="text-text-secondary text-base max-w-lg mx-auto leading-relaxed">
            Start free with 3 scans. Upgrade for unlimited analysis, AI rewriting, and full automation.
          </p>
          {/* Current plan indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="mt-5 inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full border border-white/[0.08] text-text-muted text-xs"
            style={{ background: 'rgba(255,255,255,0.03)' }}
          >
            Current plan: <span className="font-semibold text-text-primary ml-1 capitalize">{usage.plan}</span>
          </motion.div>
        </motion.div>

        {/* Pricing cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-3 gap-5 items-start pt-6"
        >
          {plans.map((plan) => {
            const isCurrentPlan = usage.plan === plan.planKey
            return (
              <motion.div key={plan.name} variants={cardVariants}>
                <TiltCard className="h-full" intensity={plan.popular ? 4 : 6}>
                  <div
                    className={clsx(
                      'relative rounded-2xl border transition-all duration-300 h-full',
                      plan.popular
                        ? 'border-accent-primary/25 md:-mt-4 md:mb-0'
                        : 'border-white/[0.06] hover:border-white/[0.12]',
                      isCurrentPlan && 'ring-2 ring-accent-secondary/60 shadow-[0_0_40px_rgba(139,92,246,0.25)] border-accent-secondary/40'
                    )}
                    style={{
                      background: plan.popular
                        ? 'linear-gradient(135deg, rgba(17,17,19,0.95), rgba(22,22,24,0.9))'
                        : 'linear-gradient(135deg, rgba(17,17,19,0.8), rgba(14,14,16,0.9))',
                    }}
                  >
                    {/* Gradient top border for popular (inner wrapper masks overflow so badges stay visible) */}
                    {plan.popular && (
                      <div className="absolute inset-0 rounded-2xl overflow-hidden pointer-events-none">
                        <div className="absolute top-0 left-0 right-0 h-px animated-gradient-line" />
                        <div className="absolute inset-0"
                          style={{ background: 'radial-gradient(ellipse at 50% 0%, rgba(220,38,38,0.08) 0%, transparent 60%)' }} />
                      </div>
                    )}

                    {/* Popular badge */}
                    {plan.popular && !isCurrentPlan && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-10">
                        <div
                          className="relative px-4 py-1 rounded-full text-white text-[11px] font-semibold tracking-wide uppercase overflow-hidden"
                          style={{
                            background: 'linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)',
                            boxShadow: '0 4px 16px rgba(220,38,38,0.3)',
                          }}
                        >
                          <span className="relative z-10">Most Popular</span>
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" style={{ backgroundSize: '200% 100%' }} />
                        </div>
                      </div>
                    )}

                    {/* Current plan badge */}
                    {isCurrentPlan && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-20 whitespace-nowrap">
                        <div
                          className="flex items-center gap-1.5 px-4 py-1 rounded-full text-white text-[11px] font-semibold tracking-wide uppercase"
                          style={{
                            background: 'linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%)',
                            boxShadow: '0 4px 16px rgba(124,58,237,0.45)',
                          }}
                        >
                          <CheckCircle2 size={11} />
                          Current Plan
                        </div>
                      </div>
                    )}

                    <div className="p-7 relative">
                      {/* Plan header */}
                      <div className="flex items-center gap-2.5 mb-4">
                        <div className={clsx(
                          'w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-300',
                          plan.popular
                            ? 'bg-accent-primary/10 border border-accent-primary/20'
                            : plan.name === 'Premium'
                              ? 'bg-accent-secondary/10 border border-accent-secondary/20'
                              : 'bg-white/[0.04] border border-white/[0.08]'
                        )}>
                          <plan.icon size={16} className={plan.accent} strokeWidth={1.8} />
                        </div>
                        <span className="font-display font-semibold text-text-primary text-base">
                          {plan.name}
                        </span>
                      </div>

                      {/* Price */}
                      <div className="mb-5">
                        <div className="flex items-baseline gap-1">
                          <span
                            className="font-display text-5xl font-bold tracking-tight"
                            style={plan.popular ? {
                              background: 'linear-gradient(135deg, #FAFAFA 0%, #DC2626 150%)',
                              WebkitBackgroundClip: 'text',
                              WebkitTextFillColor: 'transparent',
                            } : {
                              color: '#FAFAFA',
                            }}
                          >
                            ${plan.price}
                          </span>
                          {plan.period && (
                            <span className="text-sm text-text-muted font-medium">{plan.period}</span>
                          )}
                        </div>
                        <p className="text-sm text-text-secondary mt-2 leading-relaxed">
                          {plan.description}
                        </p>
                      </div>

                      {/* CTA */}
                      {plan.planKey === 'free' ? (
                        <Link
                          to="/analyze"
                          className="block w-full text-center py-3 rounded-xl text-sm font-medium transition-all duration-300 bg-white/[0.04] border border-white/[0.08] text-text-secondary hover:bg-white/[0.06] hover:text-text-primary hover:border-white/[0.14] glow-hover"
                        >
                          {isCurrentPlan ? 'Currently Active' : plan.cta}
                        </Link>
                      ) : (
                        <button
                          onClick={() => handleCta(plan)}
                          disabled={isCurrentPlan}
                          className={clsx(
                            'relative block w-full text-center py-3 rounded-xl text-sm font-semibold transition-all duration-300 disabled:opacity-60 disabled:cursor-default overflow-hidden',
                            plan.popular
                              ? 'text-white'
                              : 'bg-accent-secondary/10 border border-accent-secondary/20 text-accent-secondary hover:bg-accent-secondary/18 glow-hover'
                          )}
                          style={plan.popular ? {
                            background: 'linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)',
                            boxShadow: '0 4px 20px rgba(220,38,38,0.25)',
                          } : undefined}
                        >
                          <span className="relative z-10">
                            {isCurrentPlan ? 'Currently Active' : plan.cta}
                          </span>
                          {plan.popular && !isCurrentPlan && (
                            <div className="absolute inset-0 -translate-x-full hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                          )}
                        </button>
                      )}

                      {/* Divider */}
                      <div className="my-6">
                        {plan.popular ? (
                          <div className="animated-gradient-line opacity-60" />
                        ) : (
                          <div className="h-px bg-white/[0.06]" />
                        )}
                      </div>

                      {/* Features */}
                      <ul className="space-y-3">
                        {plan.features.map((feature, fi) => (
                          <motion.li
                            key={feature.text}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.4 + fi * 0.04, duration: 0.3 }}
                            className="flex items-start gap-2.5"
                          >
                            {feature.included ? (
                              <div className={clsx(
                                'mt-0.5 flex-shrink-0 w-4 h-4 rounded-full flex items-center justify-center',
                                plan.popular
                                  ? 'bg-accent-primary/15'
                                  : plan.name === 'Premium'
                                    ? 'bg-accent-secondary/15'
                                    : 'bg-white/[0.06]'
                              )}>
                                <Check
                                  size={10}
                                  strokeWidth={3}
                                  className={clsx(
                                    plan.popular ? 'text-accent-primary' : plan.name === 'Premium' ? 'text-accent-secondary' : 'text-text-muted'
                                  )}
                                />
                              </div>
                            ) : (
                              <div className="mt-0.5 flex-shrink-0 w-4 h-4 rounded-full flex items-center justify-center bg-white/[0.03]">
                                <X size={10} strokeWidth={2} className="text-text-muted/30" />
                              </div>
                            )}
                            <span
                              className={clsx(
                                'text-[13px] leading-snug',
                                feature.included ? 'text-text-secondary' : 'text-text-muted/40'
                              )}
                            >
                              {feature.text}
                            </span>
                          </motion.li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </TiltCard>
              </motion.div>
            )
          })}
        </motion.div>

        {/* ─── Hybrid revenue add-ons ─── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-20"
        >
          <div className="text-center mb-8">
            <h2 className="font-display text-3xl font-bold text-text-primary mb-2">
              Or pay <span className="shimmer-text">your way</span>
            </h2>
            <p className="text-text-secondary text-sm max-w-md mx-auto">
              Not ready for a subscription? Buy what you need, when you need it.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Rush Credits — $9 one-time */}
            <div className="rounded-2xl border border-accent-primary/25 bg-gradient-to-br from-accent-primary/[0.06] to-transparent p-7 relative">
              <div className="flex items-center gap-2.5 mb-3">
                <div className="w-9 h-9 rounded-xl bg-accent-primary/10 border border-accent-primary/20 flex items-center justify-center">
                  <Rocket size={16} className="text-accent-primary" />
                </div>
                <span className="font-display font-semibold text-text-primary text-base">Rush Credit</span>
                <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-accent-primary/15 text-accent-primary font-bold">
                  One-time
                </span>
              </div>
              <div className="flex items-baseline gap-1 mb-2">
                <span className="font-display text-4xl font-bold text-text-primary">$9</span>
                <span className="text-sm text-text-muted">/ deep dive</span>
              </div>
              <p className="text-sm text-text-secondary mb-4 leading-relaxed">
                Got a single high-stakes role? Get the full toolkit for one job — no subscription.
              </p>
              <ul className="space-y-2 mb-5 text-[13px] text-text-secondary">
                <li className="flex items-center gap-2"><Check size={12} className="text-accent-primary" /> 1× full ATS analysis + Recruiter Roast</li>
                <li className="flex items-center gap-2"><Check size={12} className="text-accent-primary" /> 1× role-specific AI rewrite</li>
                <li className="flex items-center gap-2"><Check size={12} className="text-accent-primary" /> 1× tailored cover letter</li>
                <li className="flex items-center gap-2"><Check size={12} className="text-accent-primary" /> 1× interview prep set (10 Qs)</li>
                <li className="flex items-center gap-2"><Check size={12} className="text-accent-primary" /> PDF + DOCX export, watermark-free</li>
              </ul>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => addRushCredits(1)}
                  className="flex-1 py-2.5 rounded-xl bg-accent-primary text-white text-sm font-semibold hover:bg-accent-primary/90 transition-all"
                >
                  Buy 1 — $9
                </button>
                <button
                  onClick={() => addRushCredits(3)}
                  className="flex-1 py-2.5 rounded-xl bg-accent-primary/10 border border-accent-primary/30 text-accent-primary text-sm font-semibold hover:bg-accent-primary/15 transition-all"
                >
                  Buy 3 — $24
                </button>
              </div>
              {usage.rushCredits > 0 && (
                <p className="text-xs text-accent-primary mt-3 text-center">
                  You have <strong>{usage.rushCredits}</strong> rush credit{usage.rushCredits === 1 ? '' : 's'} available
                </p>
              )}
            </div>

            {/* Career Guard — $49/year */}
            <div className="rounded-2xl border border-emerald-500/25 bg-gradient-to-br from-emerald-500/[0.06] to-transparent p-7 relative">
              <div className="flex items-center gap-2.5 mb-3">
                <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                  <Shield size={16} className="text-emerald-400" />
                </div>
                <span className="font-display font-semibold text-text-primary text-base">Career Guard</span>
                <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 font-bold">
                  Career Insurance
                </span>
              </div>
              <div className="flex items-baseline gap-1 mb-2">
                <span className="font-display text-4xl font-bold text-text-primary">$49</span>
                <span className="text-sm text-text-muted">/ year</span>
              </div>
              <p className="text-sm text-text-secondary mb-4 leading-relaxed">
                Not job hunting — staying employable. We monitor the market for you.
              </p>
              <ul className="space-y-2 mb-5 text-[13px] text-text-secondary">
                <li className="flex items-center gap-2"><Check size={12} className="text-emerald-400" /> Monthly resume vs market scan</li>
                <li className="flex items-center gap-2"><Check size={12} className="text-emerald-400" /> Skill-decay alerts in real-time</li>
                <li className="flex items-center gap-2"><Check size={12} className="text-emerald-400" /> Quarterly salary benchmark for your role</li>
                <li className="flex items-center gap-2"><Check size={12} className="text-emerald-400" /> LinkedIn About refresh suggestions</li>
                <li className="flex items-center gap-2"><Check size={12} className="text-emerald-400" /> 2 Rush Credits / year included</li>
              </ul>
              <button
                onClick={() => upgradePlan('guard')}
                disabled={usage.plan === 'guard'}
                className="w-full py-2.5 rounded-xl bg-emerald-500 text-white text-sm font-semibold hover:bg-emerald-500/90 transition-all disabled:opacity-60 disabled:cursor-default"
              >
                {usage.plan === 'guard' ? 'Currently Active' : 'Subscribe — $49/year'}
              </button>
            </div>
          </div>
        </motion.div>

        {/* Trust / FAQ */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mt-16 text-center"
        >
          <div className="inline-flex items-center gap-6 flex-wrap justify-center">
            {['No credit card required', 'Cancel anytime', 'Privacy-first'].map((t) => (
              <span key={t} className="flex items-center gap-1.5 text-[12px] text-text-muted">
                <Check size={12} className="text-success/50" strokeWidth={2.5} />
                {t}
              </span>
            ))}
          </div>
          <p className="text-xs text-text-muted/40 mt-4">
            Demo mode — no real payments. Plan saved locally.
          </p>
        </motion.div>
      </div>
    </PageWrapper>
  )
}

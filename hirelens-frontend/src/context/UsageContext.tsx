import { createContext, useContext, useState, useCallback } from 'react'
import type { ReactNode } from 'react'
import toast from 'react-hot-toast'

export type PlanType = 'free' | 'pro' | 'premium' | 'guard'

interface UsageState {
  plan: PlanType
  scansUsed: number
  maxScans: number  // 3 for free, Infinity for pro/premium/guard
  rushCredits: number  // one-time "Single-Job Deep Dive" credits
}

interface UsageContextValue {
  usage: UsageState
  canScan: boolean
  canUsePro: boolean
  canUsePremium: boolean       // premium OR rush credit available
  incrementScan: () => void
  upgradePlan: (plan: PlanType) => void
  addRushCredits: (count: number) => void
  consumeRushCredit: () => boolean
  showUpgradeModal: boolean
  setShowUpgradeModal: (show: boolean) => void
  checkAndPromptUpgrade: () => boolean
}

const STORAGE_KEY = 'hireport_usage'

const PLAN_LABELS: Record<PlanType, string> = {
  free: 'Free',
  pro: 'Pro',
  premium: 'Premium',
  guard: 'Career Guard',
}

function loadUsage(): UsageState {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      const plan: PlanType = parsed.plan || 'free'
      return {
        plan,
        scansUsed: parsed.scansUsed || 0,
        maxScans: plan === 'free' ? 3 : Infinity,
        rushCredits: parsed.rushCredits || 0,
      }
    }
  } catch {
    // ignore
  }
  return { plan: 'free', scansUsed: 0, maxScans: 3, rushCredits: 0 }
}

function saveUsage(usage: UsageState) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    plan: usage.plan,
    scansUsed: usage.scansUsed,
    rushCredits: usage.rushCredits,
  }))
}

const UsageContext = createContext<UsageContextValue | null>(null)

export function UsageProvider({ children }: { children: ReactNode }) {
  const [usage, setUsage] = useState<UsageState>(loadUsage)
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)

  const canScan = usage.plan !== 'free' || usage.scansUsed < usage.maxScans
  const canUsePro = usage.plan === 'pro' || usage.plan === 'premium' || usage.plan === 'guard'
  const canUsePremium = usage.plan === 'premium' || usage.rushCredits > 0

  const incrementScan = useCallback(() => {
    setUsage((prev) => {
      const next = { ...prev, scansUsed: prev.scansUsed + 1 }
      saveUsage(next)
      return next
    })
  }, [])

  const upgradePlan = useCallback((plan: PlanType) => {
    setUsage((prev) => {
      const next: UsageState = {
        plan,
        scansUsed: prev.scansUsed,
        maxScans: plan === 'free' ? 3 : Infinity,
        rushCredits: prev.rushCredits,
      }
      saveUsage(next)
      return next
    })
    toast.success(`Upgraded to ${PLAN_LABELS[plan]}! 🎉`, { duration: 3000 })
  }, [])

  const addRushCredits = useCallback((count: number) => {
    setUsage((prev) => {
      const next = { ...prev, rushCredits: prev.rushCredits + count }
      saveUsage(next)
      return next
    })
    toast.success(`+${count} Rush Credit${count === 1 ? '' : 's'} added`, { duration: 2500 })
  }, [])

  const consumeRushCredit = useCallback((): boolean => {
    let consumed = false
    setUsage((prev) => {
      if (prev.rushCredits <= 0) return prev
      consumed = true
      const next = { ...prev, rushCredits: prev.rushCredits - 1 }
      saveUsage(next)
      return next
    })
    return consumed
  }, [])

  const checkAndPromptUpgrade = useCallback((): boolean => {
    if (!canScan) {
      setShowUpgradeModal(true)
      return false
    }
    return true
  }, [canScan])

  return (
    <UsageContext.Provider
      value={{
        usage,
        canScan,
        canUsePro,
        canUsePremium,
        incrementScan,
        upgradePlan,
        addRushCredits,
        consumeRushCredit,
        showUpgradeModal,
        setShowUpgradeModal,
        checkAndPromptUpgrade,
      }}
    >
      {children}
    </UsageContext.Provider>
  )
}

export function useUsage(): UsageContextValue {
  const ctx = useContext(UsageContext)
  if (!ctx) throw new Error('useUsage must be used within UsageProvider')
  return ctx
}

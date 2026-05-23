import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Copy, Check, FileText, Download, FileDown, Send, Bot, User, Sparkles, RefreshCw } from 'lucide-react'
import type { RewriteResponse } from '@/types'
import { chatEditResume } from '@/services/api'
import { useAnalysisContext } from '@/context/AnalysisContext'

interface ResumeEditorProps {
  original: string
  rewrite: RewriteResponse | null
  isLoading: boolean
  onDownloadPDF?: () => void
  onDownloadDocx?: () => void
  isExportingPDF?: boolean
  onRewriteUpdate?: (updated: RewriteResponse) => void
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  isError?: boolean
}

// Matches a date (or date range) at the end of a line, e.g. "June 2025 – August 2025" or "May 2024 - Present"
const DATE_AT_END_RE =
  /((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}(?:\s*[–\-]\s*(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|Present))?)$/i

type LineBlock =
  | { type: 'orgdate'; org: string; date: string }
  | { type: 'title'; text: string }
  | { type: 'bullet'; text: string }
  | { type: 'detail'; text: string }
  | { type: 'text'; text: string }

function parseContentLines(content: string): LineBlock[] {
  const blocks: LineBlock[] = []
  let lastWasOrgDate = false
  content.split('\n').forEach((raw) => {
    const line = raw.trim()
    if (!line) { lastWasOrgDate = false; return }
    if (/^[•\-\*]/.test(line)) {
      blocks.push({ type: 'bullet', text: line.replace(/^[•\-\*]\s*/, '') })
      lastWasOrgDate = false
    } else if (/^(?:Relevant Coursework|GPA|Courses):/i.test(line)) {
      blocks.push({ type: 'detail', text: line })
      lastWasOrgDate = false
    } else {
      const m = DATE_AT_END_RE.exec(line)
      if (m) {
        const dateStr = m[1]
        const org = line.slice(0, line.lastIndexOf(dateStr)).trim()
        blocks.push({ type: 'orgdate', org, date: dateStr })
        lastWasOrgDate = true
      } else if (lastWasOrgDate) {
        blocks.push({ type: 'title', text: line })
        lastWasOrgDate = false
      } else {
        blocks.push({ type: 'text', text: line })
        lastWasOrgDate = false
      }
    }
  })
  return blocks
}

/**
 * Render section content text with UT-style formatting.
 * Used for Skills/Honors sections that have a `content` string instead of entries[].
 */
function SectionContentRenderer({ content }: { content: string }) {
  const blocks = parseContentLines(content)
  return (
    <div style={{ fontSize: '12px', color: '#222', lineHeight: '1.45' }}>
      {blocks.map((b, i) => {
        if (b.type === 'orgdate')
          return (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '8px', marginTop: '8px' }}>
              <span style={{ fontWeight: 'bold', fontSize: '13px', color: '#111' }}>{b.org}</span>
              <span style={{ fontSize: '12px', color: '#333', whiteSpace: 'nowrap', flexShrink: 0 }}>{b.date}</span>
            </div>
          )
        if (b.type === 'title')
          return <p key={i} style={{ fontStyle: 'italic', fontSize: '12.5px', color: '#333', margin: '1px 0' }}>{b.text}</p>
        if (b.type === 'bullet')
          return (
            <div key={i} style={{ display: 'flex', gap: '8px', marginTop: '2px' }}>
              <span style={{ flexShrink: 0 }}>•</span>
              <span>{b.text}</span>
            </div>
          )
        if (b.type === 'detail')
          return <p key={i} style={{ paddingLeft: '16px', margin: '2px 0', color: '#444' }}>{b.text}</p>
        return <p key={i} style={{ margin: '2px 0' }}>{b.text}</p>
      })}
    </div>
  )
}

/** Full formatted resume preview matching UT/professional template */
function ResumePreview({ rewrite }: { rewrite: RewriteResponse }) {
  const hasStructuredHeader = !!(rewrite.header?.name?.trim())
  const hasStructuredEntries = rewrite.sections.some((s) =>
    s.entries?.some((e) => e.org || e.title || (e.bullets && e.bullets.length > 0))
  )

  if ((!hasStructuredHeader || !hasStructuredEntries) && rewrite.full_text) {
    return <PlainTextFallback text={rewrite.full_text} />
  }

  return (
    <div
      className="bg-white rounded-xl shadow-lg"
      style={{
        fontFamily: "'Times New Roman', Times, serif",
        padding: '40px 48px',
        maxWidth: '780px',
        margin: '0 auto',
      }}
    >
      {/* Header */}
      {hasStructuredHeader && (
        <div className="text-center pb-3 mb-4" style={{ borderBottom: '1.5px solid #1a1a1a' }}>
          <h1
            style={{
              fontSize: '22px',
              fontWeight: 'bold',
              color: '#111',
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
              margin: 0,
            }}
          >
            {rewrite.header.name}
          </h1>
          {rewrite.header.contact && (
            <p style={{ fontSize: '12px', color: '#444', marginTop: '6px' }}>
              {rewrite.header.contact}
            </p>
          )}
        </div>
      )}

      {/* Sections */}
      {rewrite.sections.map((section, i) => {
        if (section.title === '__HEADER__') return null
        const hasEntries = section.entries?.some(
          (e) => e.org || e.title || (e.bullets && e.bullets.length > 0)
        )
        const hasContent = section.content?.trim()
        if (!hasEntries && !hasContent) return null

        return (
          <div key={i} style={{ marginTop: i === 0 ? '0' : '14px' }}>
            {/* Section heading */}
            <div style={{ borderBottom: '1px solid #1a1a1a', marginBottom: '6px' }}>
              <h2
                style={{
                  fontSize: '13px',
                  fontWeight: 'bold',
                  color: '#111',
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  margin: '0 0 2px 0',
                }}
              >
                {section.title}
              </h2>
            </div>

            {/* Structured entries */}
            {hasEntries &&
              section.entries.map((entry, j) => (
                <div key={j} style={{ marginTop: j === 0 ? '4px' : '10px' }}>
                  {(entry.org || entry.date) && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '8px' }}>
                      <span style={{ fontWeight: 'bold', fontSize: '13px', color: '#111' }}>{entry.org}</span>
                      {entry.date && (
                        <span style={{ fontSize: '12px', color: '#333', whiteSpace: 'nowrap', flexShrink: 0 }}>
                          {entry.date}
                        </span>
                      )}
                    </div>
                  )}
                  {entry.title && (
                    <p style={{ fontStyle: 'italic', fontSize: '12.5px', color: '#333', margin: '1px 0' }}>
                      {entry.title}
                    </p>
                  )}
                  {entry.details?.map((d, k) =>
                    d.trim() ? (
                      <p key={k} style={{ fontSize: '12px', color: '#444', paddingLeft: '16px', margin: '2px 0' }}>{d}</p>
                    ) : null
                  )}
                  {entry.bullets && entry.bullets.length > 0 && (
                    <ul style={{ margin: '4px 0 0 0', padding: 0, listStyle: 'none' }}>
                      {entry.bullets.map((b, k) => (
                        <li key={k} style={{ display: 'flex', gap: '8px', fontSize: '12px', color: '#222', lineHeight: '1.45', marginTop: '2px' }}>
                          <span style={{ flexShrink: 0 }}>•</span>
                          <span>{b}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}

            {hasContent && !hasEntries && <SectionContentRenderer content={section.content} />}
          </div>
        )
      })}
    </div>
  )
}

/** Last-resort renderer: parse and format plain full_text into UT template layout */
function PlainTextFallback({ text }: { text: string }) {
  const SECTION_RE =
    /^(EDUCATION|EXPERIENCE|WORK EXPERIENCE|PROJECTS|SKILLS|TECHNICAL SKILLS|LEADERSHIP.*|CAMPUS INVOLVEMENT|HONORS.*|AWARDS|CERTIFICATIONS|RESEARCH.*|VOLUNTEER.*|ACTIVITIES)$/i

  type FallbackBlock =
    | { type: 'header'; text: string }
    | { type: 'section'; text: string }
    | { type: 'orgdate'; org: string; date: string }
    | { type: 'title'; text: string }
    | { type: 'bullet'; text: string }
    | { type: 'detail'; text: string }
    | { type: 'text'; text: string }

  const lines = text.split('\n')
  const blocks: FallbackBlock[] = []
  let headerDone = false
  let lastWasOrgDate = false

  lines.forEach((raw) => {
    const line = raw.trim()
    if (!line) { lastWasOrgDate = false; return }

    if (!headerDone) {
      if (SECTION_RE.test(line)) {
        headerDone = true
      } else {
        blocks.push({ type: 'header', text: line })
        return
      }
    }

    if (SECTION_RE.test(line)) {
      blocks.push({ type: 'section', text: line.toUpperCase() })
      lastWasOrgDate = false
    } else if (/^[•\-\*]/.test(line)) {
      blocks.push({ type: 'bullet', text: line.replace(/^[•\-\*]\s*/, '') })
      lastWasOrgDate = false
    } else if (/^(?:Relevant Coursework|GPA|Courses):/i.test(line)) {
      blocks.push({ type: 'detail', text: line })
      lastWasOrgDate = false
    } else {
      const m = DATE_AT_END_RE.exec(line)
      if (m) {
        const dateStr = m[1]
        const org = line.slice(0, line.lastIndexOf(dateStr)).trim()
        blocks.push({ type: 'orgdate', org, date: dateStr })
        lastWasOrgDate = true
      } else if (lastWasOrgDate) {
        blocks.push({ type: 'title', text: line })
        lastWasOrgDate = false
      } else {
        blocks.push({ type: 'text', text: line })
        lastWasOrgDate = false
      }
    }
  })

  const headerBlocks = blocks.filter((b) => b.type === 'header') as { type: 'header'; text: string }[]
  const [nameBlock, ...contactBlocks] = headerBlocks
  const bodyBlocks = blocks.filter((b) => b.type !== 'header')

  return (
    <div
      className="bg-white rounded-xl shadow-lg"
      style={{
        fontFamily: "'Times New Roman', Times, serif",
        padding: '40px 48px',
        maxWidth: '780px',
        margin: '0 auto',
      }}
    >
      {nameBlock && (
        <div className="text-center pb-3 mb-4" style={{ borderBottom: '1.5px solid #1a1a1a' }}>
          <h1 style={{ fontSize: '22px', fontWeight: 'bold', color: '#111', textTransform: 'uppercase', letterSpacing: '0.1em', margin: 0 }}>
            {nameBlock.text}
          </h1>
          {contactBlocks.length > 0 && (
            <p style={{ fontSize: '12px', color: '#444', marginTop: '6px' }}>
              {contactBlocks.map((b) => b.text).join(' | ')}
            </p>
          )}
        </div>
      )}
      <div>
        {bodyBlocks.map((b, i) => {
          if (b.type === 'section')
            return (
              <div key={i} style={{ borderBottom: '1px solid #1a1a1a', marginTop: '14px', marginBottom: '6px' }}>
                <h2 style={{ fontSize: '13px', fontWeight: 'bold', color: '#111', textTransform: 'uppercase', letterSpacing: '0.08em', margin: '0 0 2px 0' }}>
                  {b.text}
                </h2>
              </div>
            )
          if (b.type === 'orgdate')
            return (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '8px', marginTop: '8px' }}>
                <span style={{ fontWeight: 'bold', fontSize: '13px', color: '#111' }}>{b.org}</span>
                <span style={{ fontSize: '12px', color: '#333', whiteSpace: 'nowrap', flexShrink: 0 }}>{b.date}</span>
              </div>
            )
          if (b.type === 'title')
            return <p key={i} style={{ fontStyle: 'italic', fontSize: '12.5px', color: '#333', margin: '1px 0' }}>{b.text}</p>
          if (b.type === 'bullet')
            return (
              <div key={i} style={{ display: 'flex', gap: '8px', fontSize: '12px', color: '#222', lineHeight: '1.45', marginTop: '2px' }}>
                <span style={{ flexShrink: 0 }}>•</span>
                <span>{b.text}</span>
              </div>
            )
          if (b.type === 'detail')
            return <p key={i} style={{ fontSize: '12px', color: '#444', paddingLeft: '16px', margin: '2px 0' }}>{b.text}</p>
          return <p key={i} style={{ fontSize: '12px', color: '#222', lineHeight: '1.45', margin: '2px 0' }}>{b.text}</p>
        })}
      </div>
    </div>
  )
}

/** AI Chat panel for post-rewrite editing */
function ResumeChat({
  rewrite,
  onUpdate,
  jobDescription,
}: {
  rewrite: RewriteResponse
  onUpdate: (updated: RewriteResponse) => void
  jobDescription: string
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'intro',
      role: 'assistant',
      content:
        'Your resume is ready! Tell me what to change — I can add bullets, remove sections, adjust skills, reword anything, or tailor it further for the role.',
    },
  ])
  const [input, setInput] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isThinking])

  const send = async () => {
    const text = input.trim()
    if (!text || isThinking) return

    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setIsThinking(true)

    try {
      const updated = await chatEditResume(rewrite, text, jobDescription)
      onUpdate(updated)

      // Build a contextual reply that references what the user asked for
      const lower = text.toLowerCase()
      let reply = "Done! I've applied your change — check the preview on the right. What else would you like to adjust?"
      if (lower.includes('add') && lower.includes('bullet')) {
        reply = "Added the bullet. It leads with an action verb and includes a metric where possible. Want me to tweak the wording?"
      } else if (lower.includes('remove') || lower.includes('delete')) {
        reply = "Removed. The rest of your resume is untouched. Anything else to clean up?"
      } else if (lower.includes('reword') || lower.includes('rephrase') || lower.includes('change the wording')) {
        reply = "Reworded it. Take a look at the preview — let me know if you want a different angle."
      } else if (lower.includes('skill') || lower.includes('add') && lower.includes('skill')) {
        reply = "Added to your skills section. Want me to group it under a specific category?"
      } else if (lower.includes('gpa') || lower.includes('grade')) {
        reply = "Updated your GPA. Anything else in the education section to change?"
      } else if (lower.includes('summary') || lower.includes('objective')) {
        reply = "Added the summary at the top. Want me to adjust the tone or length?"
      } else if (lower.includes('format') || lower.includes('reorder') || lower.includes('move')) {
        reply = "Reformatted as requested. Check the preview — want any other layout changes?"
      }

      setMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), role: 'assistant', content: reply },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: "Hmm, something went wrong applying that change. Try rephrasing — e.g. \"Add a bullet to Bank of America: Led X to achieve Y\"",
          isError: true,
        },
      ])
    } finally {
      setIsThinking(false)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="flex flex-col border border-white/[0.08] rounded-2xl bg-bg-surface/60 overflow-hidden h-[420px]">
      {/* Header */}
      <div className="flex items-center gap-2.5 px-4 py-3 border-b border-white/[0.06] bg-bg-elevated/40">
        <div className="w-7 h-7 rounded-lg bg-accent-primary/15 flex items-center justify-center">
          <Sparkles size={13} className="text-accent-primary" />
        </div>
        <div>
          <p className="text-sm font-semibold text-text-primary">AI Resume Editor</p>
          <p className="text-[10px] text-text-muted">Ask me to add, remove, or change anything</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            <div
              className={`w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center mt-0.5 ${
                msg.role === 'user'
                  ? 'bg-accent-primary/20'
                  : 'bg-accent-secondary/20'
              }`}
            >
              {msg.role === 'user' ? (
                <User size={11} className="text-accent-primary" />
              ) : (
                <Bot size={11} className="text-accent-secondary" />
              )}
            </div>
            <div
              className={`max-w-[80%] px-3 py-2 rounded-xl text-xs leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-accent-primary/15 text-text-primary rounded-tr-sm'
                  : msg.isError
                  ? 'bg-red-500/10 text-red-400 rounded-tl-sm'
                  : 'bg-white/[0.05] text-text-secondary rounded-tl-sm'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {isThinking && (
          <div className="flex gap-2.5">
            <div className="w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center mt-0.5 bg-accent-secondary/20">
              <Bot size={11} className="text-accent-secondary" />
            </div>
            <div className="px-3 py-2 rounded-xl rounded-tl-sm bg-white/[0.05]">
              <div className="flex gap-1 items-center h-4">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-1.5 h-1.5 rounded-full bg-accent-secondary/60 animate-bounce"
                    style={{ animationDelay: `${i * 150}ms` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-3 py-3 border-t border-white/[0.06] bg-bg-elevated/20">
        <div className="flex gap-2 items-center">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            disabled={isThinking}
            placeholder='e.g. "Add a bullet to Google: Led migration to AWS reducing costs 30%" or "Remove honors section"'
            className="flex-1 bg-white/[0.04] border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-text-primary placeholder:text-text-muted outline-none focus:border-accent-primary/40 focus:bg-white/[0.07] transition-all disabled:opacity-50"
          />
          <button
            onClick={send}
            disabled={!input.trim() || isThinking}
            className="w-8 h-8 rounded-xl bg-accent-primary flex items-center justify-center hover:bg-accent-primary/80 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
          >
            {isThinking ? (
              <RefreshCw size={13} className="text-bg-base animate-spin" />
            ) : (
              <Send size={13} className="text-bg-base" />
            )}
          </button>
        </div>
        <p className="text-[10px] text-text-muted mt-1.5 px-1">
          Press Enter to send · Changes appear in the preview instantly
        </p>
      </div>
    </div>
  )
}

export function ResumeEditor({
  original,
  rewrite: initialRewrite,
  isLoading,
  onDownloadPDF,
  onDownloadDocx,
  isExportingPDF,
  onRewriteUpdate,
}: ResumeEditorProps) {
  const { state } = useAnalysisContext()
  const [copiedFull, setCopiedFull] = useState(false)
  const [currentRewrite, setCurrentRewrite] = useState<RewriteResponse | null>(initialRewrite)

  // Sync when parent passes a new rewrite (e.g., after fresh generation)
  useEffect(() => {
    setCurrentRewrite(initialRewrite)
  }, [initialRewrite])

  const handleUpdate = (updated: RewriteResponse) => {
    setCurrentRewrite(updated)
    onRewriteUpdate?.(updated)
  }

  const handleCopyFull = async () => {
    if (!currentRewrite) return
    await navigator.clipboard.writeText(currentRewrite.full_text)
    setCopiedFull(true)
    setTimeout(() => setCopiedFull(false), 2000)
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2].map((i) => (
            <div key={i} className="space-y-3 p-6 bg-bg-surface/50 rounded-2xl border border-white/[0.06]">
              <div className="h-5 w-32 bg-bg-elevated rounded-full animate-pulse" />
              <div className="h-px bg-bg-elevated" />
              {[...Array(12)].map((_, j) => (
                <div
                  key={j}
                  className={`h-3 bg-bg-elevated rounded-full animate-pulse ${j % 3 === 2 ? 'w-3/4' : 'w-full'}`}
                  style={{ animationDelay: `${j * 80}ms` }}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!currentRewrite) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="w-16 h-16 rounded-2xl bg-accent-primary/8 border border-accent-primary/15 flex items-center justify-center mb-5">
          <FileText size={28} className="text-accent-primary/60" />
        </div>
        <h3 className="font-display text-lg font-semibold text-text-primary mb-2">No Rewrite Yet</h3>
        <p className="text-sm text-text-secondary max-w-sm leading-relaxed">
          Click "Generate AI Rewrite" to get a one-page, ATS-optimized version of your resume tailored to this role.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Action bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent-primary animate-pulse" />
          <span className="text-xs font-medium text-accent-primary uppercase tracking-wider">
            ATS-Optimized · One Page
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleCopyFull}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs text-text-secondary hover:text-accent-primary hover:bg-accent-primary/5 transition-colors"
          >
            {copiedFull ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
            {copiedFull ? 'Copied!' : 'Copy Text'}
          </button>
          {onDownloadPDF && (
            <button
              onClick={onDownloadPDF}
              disabled={isExportingPDF}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium bg-accent-primary/10 text-accent-primary hover:bg-accent-primary/20 transition-colors disabled:opacity-50"
            >
              <Download size={12} />
              {isExportingPDF ? 'Exporting...' : 'PDF'}
            </button>
          )}
          {onDownloadDocx && (
            <button
              onClick={onDownloadDocx}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium bg-accent-primary/10 text-accent-primary hover:bg-accent-primary/20 transition-colors"
            >
              <FileDown size={12} />
              DOCX
            </button>
          )}
        </div>
      </div>

      {/* Rewrite preview — full width */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <div className="w-2 h-2 rounded-full bg-accent-primary animate-pulse" />
          <h3 className="text-xs font-medium text-accent-primary uppercase tracking-wider">
            ATS-Optimized · Formatted Preview
          </h3>
        </div>
        <AnimatePresence mode="wait">
          <motion.div
            key={JSON.stringify(currentRewrite.header)}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            <ResumePreview rewrite={currentRewrite} />
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Original (collapsible / below) */}
      <details className="group">
        <summary className="flex items-center gap-2 cursor-pointer list-none mb-2">
          <div className="w-2 h-2 rounded-full bg-text-muted" />
          <h3 className="text-xs font-medium text-text-muted uppercase tracking-wider">
            Original Resume
          </h3>
          <span className="text-[10px] text-text-muted ml-1 group-open:hidden">(click to expand)</span>
          <span className="text-[10px] text-text-muted ml-1 hidden group-open:inline">(click to collapse)</span>
        </summary>
        <div className="p-5 bg-bg-surface/50 border border-white/[0.06] rounded-2xl mt-2">
          <pre className="font-mono text-[11px] text-text-secondary whitespace-pre-wrap leading-relaxed">
            {original.slice(0, 3000) || 'Original resume text not available.'}
          </pre>
        </div>
      </details>

      {/* AI Chat Panel */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Sparkles size={13} className="text-accent-secondary" />
          <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider">
            Edit with AI
          </h3>
          <span className="text-[10px] text-text-muted">— tell the AI what to change</span>
        </div>
        <ResumeChat
          rewrite={currentRewrite}
          onUpdate={handleUpdate}
          jobDescription={state.jobDescription || ''}
        />
      </div>
    </div>
  )
}

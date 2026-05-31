import { useState, useRef, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Copy, Check, FileText, Download, FileDown, Pencil, Eye } from 'lucide-react'
import type { RewriteResponse, RewriteSection, RewriteEntry } from '@/types'

interface ResumeEditorProps {
  original: string
  rewrite: RewriteResponse | null
  isLoading: boolean
  onDownloadPDF?: () => void
  onDownloadDocx?: () => void
  isExportingPDF?: boolean
  onUpdate?: (updated: RewriteResponse) => void
}

/** Inline editable text span — blurs on Enter, calls onChange with new value */
function EditableText({
  value,
  onChange,
  className,
  tag: Tag = 'span',
  editing,
}: {
  value: string
  onChange: (v: string) => void
  className?: string
  tag?: 'span' | 'p' | 'h1' | 'h2' | 'li'
  editing: boolean
}) {
  const ref = useRef<HTMLElement>(null)

  const handleBlur = () => {
    const text = ref.current?.innerText ?? ''
    if (text !== value) onChange(text)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      ref.current?.blur()
    }
  }

  return (
    <Tag
      ref={ref as any}
      contentEditable={editing}
      suppressContentEditableWarning
      onBlur={handleBlur}
      onKeyDown={handleKeyDown}
      className={`${className ?? ''} ${editing ? 'outline-none focus:ring-1 focus:ring-blue-400/40 rounded px-0.5 -mx-0.5 hover:bg-blue-50/60 cursor-text' : ''}`}
      style={editing ? { minWidth: '2ch' } : undefined}
    >
      {value}
    </Tag>
  )
}

/** Full formatted resume preview — optionally editable */
function ResumePreview({
  rewrite,
  editing,
  onUpdate,
}: {
  rewrite: RewriteResponse
  editing: boolean
  onUpdate: (r: RewriteResponse) => void
}) {
  const updateHeader = useCallback(
    (field: 'name' | 'contact', value: string) => {
      onUpdate({
        ...rewrite,
        header: { ...rewrite.header, [field]: value },
      })
    },
    [rewrite, onUpdate],
  )

  const updateSection = useCallback(
    (si: number, patch: Partial<RewriteSection>) => {
      const sections = rewrite.sections.map((s, i) => (i === si ? { ...s, ...patch } : s))
      onUpdate({ ...rewrite, sections })
    },
    [rewrite, onUpdate],
  )

  const updateEntry = useCallback(
    (si: number, ei: number, patch: Partial<RewriteEntry>) => {
      const sections = rewrite.sections.map((s, i) => {
        if (i !== si) return s
        const entries = s.entries.map((e, j) => (j === ei ? { ...e, ...patch } : e))
        return { ...s, entries }
      })
      onUpdate({ ...rewrite, sections })
    },
    [rewrite, onUpdate],
  )

  const updateBullet = useCallback(
    (si: number, ei: number, bi: number, value: string) => {
      const sections = rewrite.sections.map((s, i) => {
        if (i !== si) return s
        const entries = s.entries.map((e, j) => {
          if (j !== ei) return e
          const bullets = e.bullets.map((b, k) => (k === bi ? value : b))
          return { ...e, bullets }
        })
        return { ...s, entries }
      })
      onUpdate({ ...rewrite, sections })
    },
    [rewrite, onUpdate],
  )

  const updateDetail = useCallback(
    (si: number, ei: number, di: number, value: string) => {
      const sections = rewrite.sections.map((s, i) => {
        if (i !== si) return s
        const entries = s.entries.map((e, j) => {
          if (j !== ei) return e
          const details = e.details.map((d, k) => (k === di ? value : d))
          return { ...e, details }
        })
        return { ...s, entries }
      })
      onUpdate({ ...rewrite, sections })
    },
    [rewrite, onUpdate],
  )

  return (
    <div
      className={`p-8 bg-white rounded-2xl shadow-card min-h-[400px] ${editing ? 'ring-2 ring-blue-400/30' : ''}`}
      style={{ fontFamily: 'Times New Roman, serif' }}
    >
      {/* Header */}
      {rewrite.header?.name && (
        <div className="text-center mb-5 pb-3 border-b-2 border-gray-800">
          <EditableText
            tag="h1"
            value={rewrite.header.name}
            onChange={(v) => updateHeader('name', v)}
            className="text-[20px] font-bold text-gray-900 tracking-wide uppercase"
            editing={editing}
          />
          {rewrite.header.contact && (
            <EditableText
              tag="p"
              value={rewrite.header.contact}
              onChange={(v) => updateHeader('contact', v)}
              className="text-[11px] text-gray-600 mt-1.5 tracking-wide"
              editing={editing}
            />
          )}
        </div>
      )}

      {/* Sections — dedupe by normalized title and skip empty sections.
          We keep the ORIGINAL index so edits write back to the right place. */}
      {(() => {
        const seen = new Set<string>()
        return rewrite.sections
          .map((s, originalIdx) => ({ s, originalIdx }))
          .filter(({ s }) => {
            const key = (s.title || '').trim().toLowerCase().replace(/\s+/g, ' ')
            if (!key) return false
            const hasEntries = s.entries?.some(
              (e) => e.org || e.title || (e.bullets && e.bullets.length > 0)
            )
            const hasContent = s.content && s.content.trim().length > 0
            if (!hasEntries && !hasContent) return false
            if (seen.has(key)) return false
            seen.add(key)
            return true
          })
      })().map(({ s: section, originalIdx: si }, displayIdx) => (
        <div key={si} style={{ marginTop: displayIdx === 0 ? 0 : '14px' }}>
          {/* Section heading */}
          <EditableText
            tag="h2"
            value={section.title}
            onChange={(v) => updateSection(si, { title: v })}
            className="text-[12px] font-bold text-gray-900 tracking-[0.15em] uppercase border-b border-gray-800 pb-1 mb-3"
            editing={editing}
          />

          {/* Entries */}
          {section.entries?.length > 0 &&
            section.entries.map((entry, ei) => (
              <div key={ei} className="mb-4">
                {entry.org && (
                  <div className="flex justify-between items-baseline gap-4">
                    <EditableText
                      value={entry.org}
                      onChange={(v) => updateEntry(si, ei, { org: v })}
                      className="font-bold text-gray-900 text-[11px]"
                      editing={editing}
                    />
                    {entry.date && (
                      <EditableText
                        value={entry.date}
                        onChange={(v) => updateEntry(si, ei, { date: v })}
                        className="text-gray-600 text-[10.5px] whitespace-nowrap"
                        editing={editing}
                      />
                    )}
                  </div>
                )}
                {entry.title && (
                  <EditableText
                    tag="p"
                    value={entry.title}
                    onChange={(v) => updateEntry(si, ei, { title: v })}
                    className="text-gray-700 text-[11px] italic mt-0.5"
                    editing={editing}
                  />
                )}
                {entry.details?.map((d, di) => (
                  <EditableText
                    key={di}
                    tag="p"
                    value={d}
                    onChange={(v) => updateDetail(si, ei, di, v)}
                    className="text-gray-600 text-[10.5px] mt-0.5"
                    editing={editing}
                  />
                ))}
                {entry.bullets?.length > 0 && (
                  <ul className="mt-1.5 space-y-1">
                    {entry.bullets.map((b, bi) => (
                      <li key={bi} className="flex gap-2 text-[10.5px] text-gray-700 leading-relaxed">
                        <span className="flex-shrink-0 mt-0.5">•</span>
                        <EditableText
                          value={b}
                          onChange={(v) => updateBullet(si, ei, bi, v)}
                          className="flex-1"
                          editing={editing}
                        />
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}

          {/* Content fallback (Skills, Honors) */}
          {section.content && (!section.entries || section.entries.length === 0) && (
            editing ? (
              <EditableContent
                value={section.content}
                onChange={(v) => updateSection(si, { content: v })}
              />
            ) : (
              <p className="text-[10.5px] text-gray-700 leading-relaxed whitespace-pre-wrap">
                {section.content}
              </p>
            )
          )}
        </div>
      ))}
    </div>
  )
}

/** Multi-line editable content block for skills/content sections */
function EditableContent({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const ref = useRef<HTMLDivElement>(null)
  const handleBlur = () => {
    const text = ref.current?.innerText ?? ''
    if (text !== value) onChange(text)
  }
  return (
    <div
      ref={ref}
      contentEditable
      suppressContentEditableWarning
      onBlur={handleBlur}
      className="text-[10.5px] text-gray-700 leading-relaxed whitespace-pre-wrap outline-none focus:ring-1 focus:ring-blue-400/40 rounded px-0.5 -mx-0.5 hover:bg-blue-50/60 cursor-text"
    >
      {value}
    </div>
  )
}

export function ResumeEditor({ original, rewrite, isLoading, onDownloadPDF, onDownloadDocx, isExportingPDF, onUpdate }: ResumeEditorProps) {
  const [copiedFull, setCopiedFull] = useState(false)
  const [editing, setEditing] = useState(false)

  const handleCopyFull = async () => {
    if (!rewrite) return
    await navigator.clipboard.writeText(rewrite.full_text)
    setCopiedFull(true)
    setTimeout(() => setCopiedFull(false), 2000)
  }

  const handleUpdate = useCallback(
    (updated: RewriteResponse) => {
      onUpdate?.(updated)
    },
    [onUpdate],
  )

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2].map((i) => (
            <div key={i} className="space-y-3 p-6 bg-bg-surface/50 rounded-2xl border border-white/[0.06]">
              <div className="h-5 w-32 bg-bg-elevated rounded-full animate-pulse" />
              <div className="h-px bg-bg-elevated" />
              {[...Array(10)].map((_, j) => (
                <div
                  key={j}
                  className={`h-3 bg-bg-elevated rounded-full animate-pulse ${j % 3 === 2 ? 'w-3/4' : 'w-full'}`}
                  style={{ animationDelay: `${j * 100}ms` }}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!rewrite) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="w-16 h-16 rounded-2xl bg-accent-primary/8 border border-accent-primary/15 flex items-center justify-center mb-5">
          <FileText size={28} className="text-accent-primary/60" />
        </div>
        <h3 className="font-display text-lg font-semibold text-text-primary mb-2">
          No Rewrite Yet
        </h3>
        <p className="text-sm text-text-secondary max-w-sm leading-relaxed">
          Select a template, enter your major, then click &quot;Generate AI Rewrite&quot; to get an ATS-optimized version of your resume.
        </p>
      </div>
    )
  }

  return (
    <div>
      {/* Action bar */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent-primary animate-pulse" />
          <span className="text-xs font-medium text-accent-primary uppercase tracking-wider">
            AI Optimized — {rewrite.template_type === 'data_science' ? 'Data Science' : rewrite.template_type === 'business' ? 'Business' : 'General/STEM'} Template
          </span>
        </div>
        <div className="flex items-center gap-1">
          {/* Edit / Preview toggle */}
          <button
            onClick={() => setEditing((prev) => !prev)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
              editing
                ? 'bg-blue-500/15 text-blue-400 hover:bg-blue-500/25'
                : 'text-text-secondary hover:text-accent-primary hover:bg-accent-primary/5'
            }`}
          >
            {editing ? <Eye size={12} /> : <Pencil size={12} />}
            {editing ? 'Preview' : 'Edit'}
          </button>
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

      {/* Edit mode hint */}
      {editing && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="mb-4 px-4 py-2.5 rounded-xl bg-blue-500/8 border border-blue-400/15 text-xs text-blue-300 flex items-center gap-2"
        >
          <Pencil size={11} />
          Click any text on the resume to edit. Changes auto-save and will be included in PDF/DOCX downloads.
        </motion.div>
      )}

      {/* Two column: original vs formatted rewrite */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Original */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 rounded-full bg-text-muted" />
            <h3 className="text-xs font-medium text-text-muted uppercase tracking-wider">Original</h3>
          </div>
          <div className="p-5 bg-bg-surface/50 border border-white/[0.06] rounded-2xl shadow-card min-h-[400px]">
            <pre className="font-mono text-[11px] text-text-secondary whitespace-pre-wrap leading-relaxed">
              {original.slice(0, 3000) || 'Original resume text not available.'}
            </pre>
          </div>
        </div>

        {/* Formatted rewrite */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 rounded-full bg-accent-primary animate-pulse" />
            <h3 className="text-xs font-medium text-accent-primary uppercase tracking-wider">
              ATS-Optimized Resume
            </h3>
          </div>
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <ResumePreview rewrite={rewrite} editing={editing} onUpdate={handleUpdate} />
          </motion.div>
        </div>
      </div>
    </div>
  )
}

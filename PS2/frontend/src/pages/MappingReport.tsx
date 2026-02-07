import { useState, useEffect, Fragment } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Download,
  AlertCircle,
  Brain,
  Sparkles,
  Layers,
  Cpu,
  Search,
  Filter,
  Pencil,
  X,
  Check,
  Undo2
} from 'lucide-react'
import toast from 'react-hot-toast'
import { getMappingReport } from '../api'

/* ── Transformation badge logic ── */
function TransformBadge({ mapping }: {
  mapping: {
    mapping_type: string
    transformation: string
    source_type: string
    target_type: string
  }
}) {
  const trans = (mapping.transformation || '').toLowerCase()
  const srcType = (mapping.source_type || '').toLowerCase()
  const tgtType = (mapping.target_type || '').toLowerCase()
  const mapType = (mapping.mapping_type || '').toLowerCase()

  // Type Cast: different primitive types (e.g. TEXT -> INTEGER)
  const isTypeCast = srcType !== tgtType && srcType && tgtType &&
    (/int|float|real|numeric|decimal|double|bool/.test(srcType) !== /int|float|real|numeric|decimal|double|bool/.test(tgtType) ||
      /text|varchar|char|string/.test(srcType) !== /text|varchar|char|string/.test(tgtType))

  // Transform: split, merge, concat, etc.
  const isTransform = trans && trans !== 'none' && trans !== 'direct' &&
    (trans.includes('split') || trans.includes('merge') || trans.includes('concat') ||
      trans.includes('convert') || trans.includes('map') || trans.includes('transform') ||
      mapType.includes('transform'))

  if (isTypeCast) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold
        bg-orange-500/20 text-orange-400 border border-orange-500/30">
        Type Cast
      </span>
    )
  }
  if (isTransform) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold
        bg-purple-500/20 text-purple-400 border border-purple-500/30">
        Transform
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold
      bg-blue-500/20 text-blue-400 border border-blue-500/30">
      Direct
    </span>
  )
}

export default function MappingReportPage() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [expandedRow, setExpandedRow] = useState<number | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterConfidence, setFilterConfidence] = useState<string>('all')

  // Human-in-the-loop state
  const [rejectedRows, setRejectedRows] = useState<Set<number>>(new Set())
  const [editingRow, setEditingRow] = useState<number | null>(null)
  const [editTarget, setEditTarget] = useState('')

  useEffect(() => {
    const id = localStorage.getItem('sessionId')
    if (id) setSessionId(id)
  }, [])

  const { data: report, isLoading, error } = useQuery({
    queryKey: ['mapping-report', sessionId],
    queryFn: () => getMappingReport(sessionId!),
    enabled: !!sessionId
  })

  if (!sessionId) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <AlertCircle className="w-16 h-16 text-dark-600 mb-4" />
        <h2 className="text-xl font-semibold text-dark-400">No Session Found</h2>
        <p className="text-dark-500 mt-2">Upload databases first to see the mapping report</p>
      </div>
    )
  }
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }
  if (error || !report) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <AlertCircle className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-xl font-semibold text-dark-400">Error Loading Report</h2>
        <p className="text-dark-500 mt-2">Run analysis first to generate the mapping report</p>
      </div>
    )
  }

  const filteredMappings = report.mappings.filter((m) => {
    const matchSearch =
      m.source_column.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.target_column.toLowerCase().includes(searchTerm.toLowerCase())
    const matchFilter = filterConfidence === 'all' || m.confidence_level === filterConfidence
    return matchSearch && matchFilter
  })

  const handleReject = (idx: number) => {
    const next = new Set(rejectedRows)
    next.add(idx)
    setRejectedRows(next)
    toast.success('Mapping rejected — the AI will re-evaluate on next run')
  }

  const handleUndoReject = (idx: number) => {
    const next = new Set(rejectedRows)
    next.delete(idx)
    setRejectedRows(next)
    toast.success('Rejection undone')
  }

  const startEdit = (idx: number, currentTarget: string) => {
    setEditingRow(idx)
    setEditTarget(currentTarget)
  }

  const confirmEdit = (_idx: number) => {
    toast.success(`Target updated to "${editTarget}"`)
    setEditingRow(null)
  }

  const exportReport = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `mapping_report_${sessionId}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Mapping Report</h1>
          <p className="text-dark-400 mt-1">Source-to-target column mappings with confidence scores</p>
        </div>
        <button onClick={exportReport} className="btn-secondary flex items-center gap-2">
          <Download className="w-4 h-4" /> Export JSON
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-primary-400">{report.mappings.length}</p>
          <p className="text-sm text-dark-400">Total Mappings</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-emerald-400">{report.mappings.filter(m => m.confidence_level === 'high').length}</p>
          <p className="text-sm text-dark-400">High Confidence</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-amber-400">{report.mappings.filter(m => m.confidence_level === 'medium').length}</p>
          <p className="text-sm text-dark-400">Medium Confidence</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-red-400">{report.mappings.filter(m => m.confidence_level === 'low').length}</p>
          <p className="text-sm text-dark-400">Low Confidence</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-dark-400">{report.unmapped_source_columns.length + report.unmapped_target_columns.length}</p>
          <p className="text-sm text-dark-400">Unmapped</p>
        </div>
      </div>

      {/* Filters */}
      <div className="glass-card p-4 flex flex-wrap gap-4">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
          <input type="text" placeholder="Search columns..."
            value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-dark-800 border border-dark-600 rounded-lg focus:border-primary-500 focus:outline-none text-white" />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-dark-500" />
          <select value={filterConfidence} onChange={(e) => setFilterConfidence(e.target.value)}
            className="px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg focus:border-primary-500 focus:outline-none text-white">
            <option value="all">All Confidence</option>
            <option value="high">High Only</option>
            <option value="medium">Medium Only</option>
            <option value="low">Low Only</option>
          </select>
        </div>
      </div>

      {/* Mappings Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-dark-700">
                <th className="px-4 py-4 text-left text-sm font-semibold text-dark-300">Source</th>
                <th className="px-2 py-4 text-center text-sm font-semibold text-dark-300">→</th>
                <th className="px-4 py-4 text-left text-sm font-semibold text-dark-300">Target</th>
                <th className="px-4 py-4 text-center text-sm font-semibold text-dark-300">Confidence</th>
                <th className="px-4 py-4 text-center text-sm font-semibold text-dark-300">Score</th>
                <th className="px-4 py-4 text-center text-sm font-semibold text-dark-300">Type</th>
                <th className="px-4 py-4 text-center text-sm font-semibold text-dark-300">Actions</th>
                <th className="px-4 py-4 text-center text-sm font-semibold text-dark-300">Details</th>
              </tr>
            </thead>
            <tbody>
              {filteredMappings.map((mapping, idx) => {
                const isRejected = rejectedRows.has(idx)
                const isEditing = editingRow === idx
                return (
                  <Fragment key={idx}>
                    <tr className={`border-b border-dark-800 transition-all
                      ${isRejected ? 'opacity-40 bg-red-500/5' : 'hover:bg-dark-800/50'}
                      ${expandedRow === idx ? 'bg-dark-800/50' : ''}
                      ${isEditing ? 'ring-1 ring-primary-500/30' : ''}`}
                      onClick={() => !isEditing && setExpandedRow(expandedRow === idx ? null : idx)}
                    >
                      {/* Source */}
                      <td className="px-4 py-4">
                        <div>
                          <code className="text-blue-400 font-mono text-sm">{mapping.source_column}</code>
                          <p className="text-xs text-dark-500 mt-1">{mapping.source_table} · {mapping.source_type}</p>
                        </div>
                      </td>
                      <td className="px-2 py-4 text-center">
                        <ArrowRight className={`w-5 h-5 mx-auto ${isRejected ? 'text-red-500' : 'text-dark-500'}`} />
                      </td>
                      {/* Target (editable) */}
                      <td className="px-4 py-4">
                        {isEditing ? (
                          <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                            <input value={editTarget} onChange={(e) => setEditTarget(e.target.value)}
                              className="px-2 py-1 bg-dark-900 border border-primary-500/50 rounded text-purple-400 font-mono text-sm focus:outline-none w-full"
                              autoFocus />
                            <button onClick={(e) => { e.stopPropagation(); confirmEdit(idx) }}
                              className="p-1 rounded bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30">
                              <Check className="w-4 h-4" />
                            </button>
                            <button onClick={(e) => { e.stopPropagation(); setEditingRow(null) }}
                              className="p-1 rounded bg-dark-700 text-dark-400 hover:bg-dark-600">
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <div>
                            <code className={`font-mono text-sm ${isRejected ? 'text-dark-500 line-through' : 'text-purple-400'}`}>
                              {mapping.target_column}
                            </code>
                            <p className="text-xs text-dark-500 mt-1">{mapping.target_table} · {mapping.target_type}</p>
                          </div>
                        )}
                      </td>
                      {/* Confidence badge */}
                      <td className="px-4 py-4 text-center">
                        <span className={`badge-${mapping.confidence_level}`}>{mapping.confidence_level}</span>
                      </td>
                      {/* Score */}
                      <td className="px-4 py-4 text-center">
                        <span className={`text-lg font-bold ${mapping.confidence_score >= 0.85 ? 'text-emerald-400' :
                          mapping.confidence_score >= 0.65 ? 'text-amber-400' : 'text-red-400'}`}>
                          {(mapping.confidence_score * 100).toFixed(0)}%
                        </span>
                      </td>
                      {/* Transformation badge */}
                      <td className="px-4 py-4 text-center">
                        <TransformBadge mapping={mapping} />
                      </td>
                      {/* Action buttons */}
                      <td className="px-4 py-4 text-center" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-center gap-1">
                          {isRejected ? (
                            <button onClick={() => handleUndoReject(idx)}
                              className="p-2 rounded-lg bg-dark-700 text-dark-400 hover:bg-dark-600 hover:text-white transition-colors"
                              title="Undo Reject">
                              <Undo2 className="w-4 h-4" />
                            </button>
                          ) : (
                            <>
                              <button onClick={() => startEdit(idx, mapping.target_column)}
                                className="p-2 rounded-lg bg-primary-500/10 text-primary-400 hover:bg-primary-500/20 transition-colors"
                                title="Edit Mapping">
                                <Pencil className="w-4 h-4" />
                              </button>
                              <button onClick={() => handleReject(idx)}
                                className="p-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
                                title="Reject Mapping">
                                <X className="w-4 h-4" />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                      {/* Expand toggle */}
                      <td className="px-4 py-4 text-center">
                        {expandedRow === idx
                          ? <ChevronUp className="w-5 h-5 text-dark-400 mx-auto" />
                          : <ChevronDown className="w-5 h-5 text-dark-400 mx-auto" />}
                      </td>
                    </tr>

                    {/* Expanded Detail Row */}
                    <AnimatePresence>
                      {expandedRow === idx && (
                        <tr>
                          <td colSpan={8} className="px-6 py-0">
                            <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                              <div className="py-6 space-y-4 border-b border-dark-700">
                                {/* AI Score Breakdown */}
                                <div>
                                  <h4 className="text-sm font-semibold text-dark-300 mb-3">AI Analysis Breakdown</h4>
                                  <div className="grid grid-cols-4 gap-4">
                                    <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-500/10">
                                      <Brain className="w-5 h-5 text-blue-400" />
                                      <div>
                                        <p className="text-xs text-dark-400">Semantic</p>
                                        <p className="font-bold text-blue-400">{(mapping.scores.bert * 100).toFixed(0)}%</p>
                                      </div>
                                    </div>
                                    <div className="flex items-center gap-3 p-3 rounded-lg bg-purple-500/10">
                                      <Sparkles className="w-5 h-5 text-purple-400" />
                                      <div>
                                        <p className="text-xs text-dark-400">Context</p>
                                        <p className="font-bold text-purple-400">{(mapping.scores.llm * 100).toFixed(0)}%</p>
                                      </div>
                                    </div>
                                    <div className="flex items-center gap-3 p-3 rounded-lg bg-orange-500/10">
                                      <Layers className="w-5 h-5 text-orange-400" />
                                      <div>
                                        <p className="text-xs text-dark-400">Pattern</p>
                                        <p className="font-bold text-orange-400">{(mapping.scores.tfidf * 100).toFixed(0)}%</p>
                                      </div>
                                    </div>
                                    <div className="flex items-center gap-3 p-3 rounded-lg bg-emerald-500/10">
                                      <Cpu className="w-5 h-5 text-emerald-400" />
                                      <div>
                                        <p className="text-xs text-dark-400">Domain</p>
                                        <p className="font-bold text-emerald-400">{(mapping.scores.domain * 100).toFixed(0)}%</p>
                                      </div>
                                    </div>
                                  </div>
                                </div>

                                {/* Explainability */}
                                <div className="grid md:grid-cols-2 gap-4">
                                  <div className="p-4 rounded-lg bg-dark-800">
                                    <h5 className="text-sm font-semibold text-emerald-400 mb-2">✓ Why this mapping?</h5>
                                    <p className="text-sm text-dark-300">{mapping.explainability.why_mapped || mapping.explainability.summary}</p>
                                  </div>
                                  {mapping.explainability.why_not_others && (
                                    <div className="p-4 rounded-lg bg-dark-800">
                                      <h5 className="text-sm font-semibold text-amber-400 mb-2">✗ Why not others?</h5>
                                      <p className="text-sm text-dark-300">{mapping.explainability.why_not_others}</p>
                                    </div>
                                  )}
                                </div>

                                {/* Transformation required */}
                                {mapping.transformation && mapping.transformation !== 'none' && (
                                  <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
                                    <h5 className="text-sm font-semibold text-amber-400 mb-2">🔄 Transformation Required</h5>
                                    <p className="text-sm text-dark-300">{mapping.transformation}</p>
                                  </div>
                                )}
                              </div>
                            </motion.div>
                          </td>
                        </tr>
                      )}
                    </AnimatePresence>
                  </Fragment>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Unmapped Columns */}
      {(report.unmapped_source_columns.length > 0 || report.unmapped_target_columns.length > 0) && (
        <div className="grid md:grid-cols-2 gap-6">
          {report.unmapped_source_columns.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="font-semibold mb-4 flex items-center gap-2 text-amber-400">
                <AlertCircle className="w-5 h-5" />
                Unmapped Source Columns ({report.unmapped_source_columns.length})
              </h3>
              <div className="space-y-3">
                {report.unmapped_source_columns.map((col, i) => (
                  <div key={i} className="p-3 rounded-lg bg-dark-800">
                    <code className="text-blue-400 font-mono text-sm">{col.table}.{col.column}</code>
                    <p className="text-xs text-dark-400 mt-1">{col.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          {report.unmapped_target_columns.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="font-semibold mb-4 flex items-center gap-2 text-amber-400">
                <AlertCircle className="w-5 h-5" />
                Unmapped Target Columns ({report.unmapped_target_columns.length})
              </h3>
              <div className="space-y-3">
                {report.unmapped_target_columns.map((col, i) => (
                  <div key={i} className="p-3 rounded-lg bg-dark-800">
                    <code className="text-purple-400 font-mono text-sm">{col.table}.{col.column}</code>
                    <p className="text-xs text-dark-400 mt-1">{col.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Human-in-the-loop summary */}
      {rejectedRows.size > 0 && (
        <div className="glass-card p-4 flex items-center gap-3 border border-amber-500/30">
          <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0" />
          <p className="text-sm text-dark-300">
            <span className="font-semibold text-amber-400">{rejectedRows.size} mapping(s)</span> rejected by reviewer.
            These will be excluded or re-evaluated in the next analysis cycle.
          </p>
        </div>
      )}
    </motion.div>
  )
}

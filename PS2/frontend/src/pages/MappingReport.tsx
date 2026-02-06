import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { 
  GitBranch, 
  ArrowRight, 
  ChevronDown, 
  ChevronUp,
  Download,
  AlertCircle,
  CheckCircle,
  Brain,
  Sparkles,
  Layers,
  Cpu,
  Search,
  Filter
} from 'lucide-react'
import { getMappingReport, MappingReport } from '../api'

export default function MappingReportPage() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [expandedRow, setExpandedRow] = useState<number | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterConfidence, setFilterConfidence] = useState<string>('all')

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

  // Filter mappings
  const filteredMappings = report.mappings.filter(m => {
    const matchesSearch = 
      m.source_column.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.target_column.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterConfidence === 'all' || m.confidence_level === filterConfidence
    return matchesSearch && matchesFilter
  })

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
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Mapping Report</h1>
          <p className="text-dark-400 mt-1">Source-to-target column mappings with confidence scores</p>
        </div>
        <button onClick={exportReport} className="btn-secondary flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export JSON
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-primary-400">{report.mappings.length}</p>
          <p className="text-sm text-dark-400">Total Mappings</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-emerald-400">
            {report.mappings.filter(m => m.confidence_level === 'high').length}
          </p>
          <p className="text-sm text-dark-400">High Confidence</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-amber-400">
            {report.mappings.filter(m => m.confidence_level === 'medium').length}
          </p>
          <p className="text-sm text-dark-400">Medium Confidence</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-red-400">
            {report.mappings.filter(m => m.confidence_level === 'low').length}
          </p>
          <p className="text-sm text-dark-400">Low Confidence</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-dark-400">
            {report.unmapped_source_columns.length + report.unmapped_target_columns.length}
          </p>
          <p className="text-sm text-dark-400">Unmapped</p>
        </div>
      </div>

      {/* Filters */}
      <div className="glass-card p-4 flex flex-wrap gap-4">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
          <input
            type="text"
            placeholder="Search columns..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-dark-800 border border-dark-600 rounded-lg
                     focus:border-primary-500 focus:outline-none text-white"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-dark-500" />
          <select
            value={filterConfidence}
            onChange={(e) => setFilterConfidence(e.target.value)}
            className="px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg
                     focus:border-primary-500 focus:outline-none text-white"
          >
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
                <th className="px-6 py-4 text-left text-sm font-semibold text-dark-300">Source</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-dark-300">→</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-dark-300">Target</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-dark-300">Confidence</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-dark-300">Score</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-dark-300">Type</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-dark-300">Details</th>
              </tr>
            </thead>
            <tbody>
              {filteredMappings.map((mapping, idx) => (
                <>
                  <tr 
                    key={idx}
                    className={`border-b border-dark-800 hover:bg-dark-800/50 cursor-pointer
                      ${expandedRow === idx ? 'bg-dark-800/50' : ''}`}
                    onClick={() => setExpandedRow(expandedRow === idx ? null : idx)}
                  >
                    <td className="px-6 py-4">
                      <div>
                        <code className="text-blue-400 font-mono text-sm">{mapping.source_column}</code>
                        <p className="text-xs text-dark-500 mt-1">{mapping.source_table} • {mapping.source_type}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <ArrowRight className="w-5 h-5 text-dark-500 mx-auto" />
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <code className="text-purple-400 font-mono text-sm">{mapping.target_column}</code>
                        <p className="text-xs text-dark-500 mt-1">{mapping.target_table} • {mapping.target_type}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`badge-${mapping.confidence_level}`}>
                        {mapping.confidence_level}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`text-lg font-bold ${
                        mapping.confidence_score >= 0.85 ? 'text-emerald-400' :
                        mapping.confidence_score >= 0.65 ? 'text-amber-400' : 'text-red-400'
                      }`}>
                        {(mapping.confidence_score * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-sm text-dark-400">{mapping.mapping_type}</span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      {expandedRow === idx ? (
                        <ChevronUp className="w-5 h-5 text-dark-400 mx-auto" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-dark-400 mx-auto" />
                      )}
                    </td>
                  </tr>
                  
                  {/* Expanded Details */}
                  <AnimatePresence>
                    {expandedRow === idx && (
                      <tr>
                        <td colSpan={7} className="px-6 py-0">
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden"
                          >
                            <div className="py-6 space-y-4 border-b border-dark-700">
                              {/* Model Scores */}
                              <div>
                                <h4 className="text-sm font-semibold text-dark-300 mb-3">Model Scores</h4>
                                <div className="grid grid-cols-4 gap-4">
                                  <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-500/10">
                                    <Brain className="w-5 h-5 text-blue-400" />
                                    <div>
                                      <p className="text-xs text-dark-400">BERT</p>
                                      <p className="font-bold text-blue-400">
                                        {(mapping.scores.bert * 100).toFixed(0)}%
                                      </p>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-3 p-3 rounded-lg bg-purple-500/10">
                                    <Sparkles className="w-5 h-5 text-purple-400" />
                                    <div>
                                      <p className="text-xs text-dark-400">Gemini</p>
                                      <p className="font-bold text-purple-400">
                                        {(mapping.scores.gemini * 100).toFixed(0)}%
                                      </p>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-3 p-3 rounded-lg bg-orange-500/10">
                                    <Layers className="w-5 h-5 text-orange-400" />
                                    <div>
                                      <p className="text-xs text-dark-400">TF-IDF</p>
                                      <p className="font-bold text-orange-400">
                                        {(mapping.scores.tfidf * 100).toFixed(0)}%
                                      </p>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-3 p-3 rounded-lg bg-emerald-500/10">
                                    <Cpu className="w-5 h-5 text-emerald-400" />
                                    <div>
                                      <p className="text-xs text-dark-400">Domain</p>
                                      <p className="font-bold text-emerald-400">
                                        {(mapping.scores.domain * 100).toFixed(0)}%
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              </div>
                              
                              {/* Explainability */}
                              <div className="grid md:grid-cols-2 gap-4">
                                <div className="p-4 rounded-lg bg-dark-800">
                                  <h5 className="text-sm font-semibold text-emerald-400 mb-2">
                                    ✓ Why this mapping?
                                  </h5>
                                  <p className="text-sm text-dark-300">
                                    {mapping.explainability.why_mapped || mapping.explainability.summary}
                                  </p>
                                </div>
                                {mapping.explainability.why_not_others && (
                                  <div className="p-4 rounded-lg bg-dark-800">
                                    <h5 className="text-sm font-semibold text-amber-400 mb-2">
                                      ✗ Why not others?
                                    </h5>
                                    <p className="text-sm text-dark-300">
                                      {mapping.explainability.why_not_others}
                                    </p>
                                  </div>
                                )}
                              </div>
                              
                              {/* Transformation */}
                              {mapping.transformation && mapping.transformation !== 'none' && (
                                <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
                                  <h5 className="text-sm font-semibold text-amber-400 mb-2">
                                    🔄 Transformation Required
                                  </h5>
                                  <p className="text-sm text-dark-300">{mapping.transformation}</p>
                                </div>
                              )}
                            </div>
                          </motion.div>
                        </td>
                      </tr>
                    )}
                  </AnimatePresence>
                </>
              ))}
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
                {report.unmapped_source_columns.map((col, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-dark-800">
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
                {report.unmapped_target_columns.map((col, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-dark-800">
                    <code className="text-purple-400 font-mono text-sm">{col.table}.{col.column}</code>
                    <p className="text-xs text-dark-400 mt-1">{col.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </motion.div>
  )
}

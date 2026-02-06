import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  GitBranch,
  ChevronDown,
  ChevronRight,
  Brain,
  Sparkles,
  Layers,
  Cpu,
  ArrowRight,
  Info,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'
import { ColumnMapping } from '../api'

export default function Mappings() {
  const [result, setResult] = useState<any>(null)
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set())
  const [selectedMapping, setSelectedMapping] = useState<ColumnMapping | null>(null)
  const [filterConfidence, setFilterConfidence] = useState<string>('all')

  useEffect(() => {
    const stored = localStorage.getItem('analysisResult')
    if (stored) {
      setResult(JSON.parse(stored))
    }
  }, [])

  const toggleTable = (table: string) => {
    const newExpanded = new Set(expandedTables)
    if (newExpanded.has(table)) {
      newExpanded.delete(table)
    } else {
      newExpanded.add(table)
    }
    setExpandedTables(newExpanded)
  }

  const getConfidenceColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30'
      case 'medium': return 'text-amber-400 bg-amber-500/20 border-amber-500/30'
      case 'low': return 'text-red-400 bg-red-500/20 border-red-500/30'
      default: return 'text-dark-400 bg-dark-700 border-dark-600'
    }
  }

  const getFilteredMappings = (mappings: ColumnMapping[]) => {
    if (filterConfidence === 'all') return mappings
    return mappings.filter(m => m.confidence_level === filterConfidence)
  }

  if (!result) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center justify-center h-96"
      >
        <GitBranch className="w-16 h-16 text-dark-600 mb-4" />
        <h2 className="text-xl font-semibold text-dark-400">No Analysis Results</h2>
        <p className="text-dark-500 mt-2">Run an analysis first to see column mappings</p>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Column Mappings</h1>
          <p className="text-dark-400 mt-2">
            {result.total_mappings} mappings detected across {Object.keys(result.grouped_mappings).length} table pairs
          </p>
        </div>

        {/* Filter */}
        <select
          value={filterConfidence}
          onChange={(e) => setFilterConfidence(e.target.value)}
          className="input-field w-auto"
        >
          <option value="all">All Confidence Levels</option>
          <option value="high">High Confidence</option>
          <option value="medium">Medium Confidence</option>
          <option value="low">Low Confidence</option>
        </select>
      </div>

      {/* Table Groups */}
      <div className="space-y-4">
        {Object.entries(result.grouped_mappings).map(([tableKey, mappings]: [string, any]) => {
          const filtered = getFilteredMappings(mappings)
          if (filtered.length === 0) return null
          
          const isExpanded = expandedTables.has(tableKey)
          
          return (
            <motion.div
              key={tableKey}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card overflow-hidden"
            >
              {/* Table Header */}
              <button
                onClick={() => toggleTable(tableKey)}
                className="w-full flex items-center justify-between p-4 hover:bg-dark-700/30 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {isExpanded ? (
                    <ChevronDown className="w-5 h-5 text-primary-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-dark-400" />
                  )}
                  <GitBranch className="w-5 h-5 text-primary-400" />
                  <span className="font-semibold">{tableKey}</span>
                  <span className="text-dark-500 text-sm">({filtered.length} mappings)</span>
                </div>
                
                <div className="flex items-center gap-2">
                  {filtered.filter(m => m.confidence_level === 'high').length > 0 && (
                    <span className="badge-success text-xs">
                      {filtered.filter(m => m.confidence_level === 'high').length} High
                    </span>
                  )}
                  {filtered.filter(m => m.confidence_level === 'medium').length > 0 && (
                    <span className="badge-warning text-xs">
                      {filtered.filter(m => m.confidence_level === 'medium').length} Med
                    </span>
                  )}
                  {filtered.filter(m => m.confidence_level === 'low').length > 0 && (
                    <span className="badge-error text-xs">
                      {filtered.filter(m => m.confidence_level === 'low').length} Low
                    </span>
                  )}
                </div>
              </button>

              {/* Mapping List */}
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="border-t border-dark-700"
                  >
                    {filtered.map((mapping: ColumnMapping, idx: number) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        onClick={() => setSelectedMapping(mapping)}
                        className="flex items-center justify-between p-4 border-b border-dark-700/50
                                 hover:bg-dark-700/30 cursor-pointer transition-colors"
                      >
                        <div className="flex items-center gap-4">
                          {/* Source Column */}
                          <div className="min-w-[150px]">
                            <code className="text-blue-400 font-mono text-sm">
                              {mapping.source_column}
                            </code>
                          </div>
                          
                          <ArrowRight className="w-4 h-4 text-dark-500" />
                          
                          {/* Target Column */}
                          <div className="min-w-[150px]">
                            <code className="text-purple-400 font-mono text-sm">
                              {mapping.target_column}
                            </code>
                          </div>
                        </div>

                        {/* Scores */}
                        <div className="flex items-center gap-4">
                          {/* Model Score Pills */}
                          <div className="hidden md:flex items-center gap-2 text-xs">
                            <div className="flex items-center gap-1 px-2 py-1 rounded bg-blue-500/10">
                              <Brain className="w-3 h-3 text-blue-400" />
                              <span className="text-blue-400">{(mapping.bert_score * 100).toFixed(0)}%</span>
                            </div>
                            {mapping.llm_score > 0 && (
                              <div className="flex items-center gap-1 px-2 py-1 rounded bg-purple-500/10">
                                <Sparkles className="w-3 h-3 text-purple-400" />
                                <span className="text-purple-400">{(mapping.llm_score * 100).toFixed(0)}%</span>
                              </div>
                            )}
                            <div className="flex items-center gap-1 px-2 py-1 rounded bg-orange-500/10">
                              <Layers className="w-3 h-3 text-orange-400" />
                              <span className="text-orange-400">{(mapping.tfidf_score * 100).toFixed(0)}%</span>
                            </div>
                            <div className="flex items-center gap-1 px-2 py-1 rounded bg-emerald-500/10">
                              <Cpu className="w-3 h-3 text-emerald-400" />
                              <span className="text-emerald-400">{(mapping.domain_score * 100).toFixed(0)}%</span>
                            </div>
                          </div>

                          {/* Ensemble Score */}
                          <div className={`px-3 py-1.5 rounded-lg border font-semibold
                                        ${getConfidenceColor(mapping.confidence_level)}`}>
                            {(mapping.ensemble_score * 100).toFixed(0)}%
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )
        })}
      </div>

      {/* Detail Panel */}
      <AnimatePresence>
        {selectedMapping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedMapping(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="glass-card p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            >
              <h2 className="text-2xl font-bold mb-6">Mapping Details</h2>

              {/* Columns */}
              <div className="flex items-center justify-center gap-4 mb-8">
                <div className="text-center">
                  <p className="text-dark-400 text-sm mb-1">Source</p>
                  <code className="text-xl font-mono text-blue-400">{selectedMapping.source_column}</code>
                </div>
                <ArrowRight className="w-6 h-6 text-primary-400" />
                <div className="text-center">
                  <p className="text-dark-400 text-sm mb-1">Target</p>
                  <code className="text-xl font-mono text-purple-400">{selectedMapping.target_column}</code>
                </div>
              </div>

              {/* Score Breakdown */}
              <div className="space-y-4 mb-8">
                <h3 className="font-semibold">Model Scores</h3>
                
                {[
                  { name: 'BERT Semantic', score: selectedMapping.bert_score, weight: 35, icon: Brain, color: 'blue' },
                  { name: 'LLM Reasoning', score: selectedMapping.llm_score, weight: 30, icon: Sparkles, color: 'purple' },
                  { name: 'TF-IDF', score: selectedMapping.tfidf_score, weight: 15, icon: Layers, color: 'orange' },
                  { name: 'Domain', score: selectedMapping.domain_score, weight: 20, icon: Cpu, color: 'emerald' },
                ].map((model) => (
                  <div key={model.name} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2">
                        <model.icon className={`w-4 h-4 text-${model.color}-400`} />
                        {model.name}
                        <span className="text-dark-500">({model.weight}% weight)</span>
                      </span>
                      <span className="font-semibold">{(model.score * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${model.score * 100}%` }}
                        transition={{ duration: 0.5 }}
                        className={`h-full bg-${model.color}-500`}
                      />
                    </div>
                  </div>
                ))}

                {/* Ensemble */}
                <div className="pt-4 border-t border-dark-700">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">Ensemble Score</span>
                    <span className={`text-2xl font-bold ${
                      selectedMapping.confidence_level === 'high' ? 'text-emerald-400' :
                      selectedMapping.confidence_level === 'medium' ? 'text-amber-400' : 'text-red-400'
                    }`}>
                      {(selectedMapping.ensemble_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* LLM Reasoning */}
              {selectedMapping.llm_reasoning && (
                <div className="bg-dark-800/50 rounded-xl p-4 mb-6">
                  <h3 className="font-semibold flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-purple-400" />
                    LLM Reasoning
                  </h3>
                  <p className="text-dark-300">{selectedMapping.llm_reasoning}</p>
                </div>
              )}

              {/* Confidence Badge */}
              <div className="flex items-center justify-center">
                {selectedMapping.confidence_level === 'high' ? (
                  <div className="badge-success flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    High Confidence - Automatic Mapping Recommended
                  </div>
                ) : selectedMapping.confidence_level === 'medium' ? (
                  <div className="badge-warning flex items-center gap-2">
                    <Info className="w-4 h-4" />
                    Medium Confidence - Review Recommended
                  </div>
                ) : (
                  <div className="badge-error flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" />
                    Low Confidence - Manual Review Required
                  </div>
                )}
              </div>

              <button
                onClick={() => setSelectedMapping(null)}
                className="btn-secondary w-full mt-6"
              >
                Close
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

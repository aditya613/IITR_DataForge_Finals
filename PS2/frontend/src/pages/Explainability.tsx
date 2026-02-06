import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { 
  MessageCircle, 
  HelpCircle,
  CheckCircle,
  XCircle,
  ArrowRight,
  AlertCircle,
  Brain,
  Download,
  ChevronDown,
  ChevronUp,
  Sparkles,
  RefreshCw,
  FileText
} from 'lucide-react'
import { getExplainabilityReport, ExplainabilityReport } from '../api'
import ReactMarkdown from 'react-markdown'

export default function Explainability() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set())

  useEffect(() => {
    const id = localStorage.getItem('sessionId')
    if (id) setSessionId(id)
  }, [])

  const { data: report, isLoading, error } = useQuery({
    queryKey: ['explainability', sessionId],
    queryFn: () => getExplainabilityReport(sessionId!),
    enabled: !!sessionId
  })

  const toggleExpand = (idx: number) => {
    const newSet = new Set(expandedItems)
    if (newSet.has(idx)) {
      newSet.delete(idx)
    } else {
      newSet.add(idx)
    }
    setExpandedItems(newSet)
  }

  if (!sessionId) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <AlertCircle className="w-16 h-16 text-dark-600 mb-4" />
        <h2 className="text-xl font-semibold text-dark-400">No Session Found</h2>
        <p className="text-dark-500 mt-2">Upload and analyze data first</p>
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
        <h2 className="text-xl font-semibold text-dark-400">Explainability Report Not Available</h2>
        <p className="text-dark-500 mt-2">Run analysis first to generate explanations</p>
      </div>
    )
  }

  const exportReport = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `explainability_report_${sessionId}.json`
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
          <h1 className="text-3xl font-bold">Explainability Report</h1>
          <p className="text-dark-400 mt-1">
            Clear explanations for non-technical stakeholders
          </p>
        </div>
        <button onClick={exportReport} className="btn-secondary flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export
        </button>
      </div>

      {/* Summary Card */}
      <div className="glass-card p-6 bg-gradient-to-r from-primary-500/10 to-purple-500/10">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-primary-500/20">
            <FileText className="w-8 h-8 text-primary-400" />
          </div>
          <div className="flex-1 prose prose-invert max-w-none">
            <div className="text-dark-200 whitespace-pre-line">
              {report.summary}
            </div>
          </div>
        </div>
      </div>

      {/* Core Explainability Questions */}
      <div className="glass-card p-6">
        <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
          <Brain className="w-6 h-6 text-purple-400" />
          Why Was This Column Mapped?
        </h2>
        
        <div className="space-y-3">
          {report.column_mappings.map((mapping, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.03 }}
              className="rounded-xl bg-dark-800/50 overflow-hidden"
            >
              <button
                onClick={() => toggleExpand(idx)}
                className="w-full flex items-center justify-between p-4 hover:bg-dark-800 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <HelpCircle className="w-5 h-5 text-primary-400 flex-shrink-0" />
                  <span className="text-dark-200">{mapping.question}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-sm px-3 py-1 rounded-full ${
                    mapping.confidence.includes('very') || mapping.confidence.includes('95') ? 'bg-emerald-500/20 text-emerald-400' :
                    mapping.confidence.includes('80') || mapping.confidence.includes('85') ? 'bg-amber-500/20 text-amber-400' :
                    'bg-dark-700 text-dark-300'
                  }`}>
                    {mapping.confidence}
                  </span>
                  {expandedItems.has(idx) ? (
                    <ChevronUp className="w-5 h-5 text-dark-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-dark-400" />
                  )}
                </div>
              </button>
              
              {expandedItems.has(idx) && (
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: 'auto' }}
                  className="px-4 pb-4"
                >
                  <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 mb-4">
                    <p className="text-emerald-200">
                      <CheckCircle className="w-4 h-4 inline mr-2" />
                      {mapping.answer}
                    </p>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-3">
                    {Object.entries(mapping.details).map(([key, value]) => (
                      <div key={key} className="p-3 rounded-lg bg-dark-900">
                        <p className="text-xs text-dark-400 mb-1">{key}</p>
                        <p className="text-sm text-dark-200">{value}</p>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Why Was Another Column Ignored? */}
      {report.ignored_columns.length > 0 && (
        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <XCircle className="w-6 h-6 text-amber-400" />
            Why Were These Columns Ignored?
          </h2>
          
          <div className="space-y-3">
            {report.ignored_columns.map((col, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30"
              >
                <div className="flex items-start gap-3">
                  <HelpCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-dark-200">{col.question}</p>
                    <p className="text-sm text-dark-400 mt-2">{col.answer}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* What Transformation Was Applied? */}
      {report.transformations.length > 0 && (
        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <RefreshCw className="w-6 h-6 text-blue-400" />
            What Transformations Were Applied?
          </h2>
          
          <div className="space-y-3">
            {report.transformations.map((trans, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30"
              >
                <div className="flex items-center gap-3 mb-3">
                  <HelpCircle className="w-5 h-5 text-blue-400" />
                  <span className="font-medium text-dark-200">{trans.question}</span>
                </div>
                <div className="flex items-center gap-4 ml-8">
                  <div className="px-3 py-2 rounded bg-dark-800">
                    <p className="text-xs text-dark-400">Source Type</p>
                    <code className="text-blue-400">{trans.source_type}</code>
                  </div>
                  <ArrowRight className="w-5 h-5 text-dark-500" />
                  <div className="px-3 py-2 rounded bg-dark-800">
                    <p className="text-xs text-dark-400">Target Type</p>
                    <code className="text-purple-400">{trans.target_type}</code>
                  </div>
                </div>
                <p className="mt-3 ml-8 text-sm text-dark-300">{trans.answer}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* What Data Failed and Why? */}
      {report.failed_data.length > 0 && (
        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-red-400">
            <XCircle className="w-6 h-6" />
            What Data Failed and Why?
          </h2>
          
          <div className="space-y-4">
            {report.failed_data.map((failure, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="p-4 rounded-xl bg-red-500/10 border border-red-500/30"
              >
                <div className="flex items-center gap-3 mb-3">
                  <HelpCircle className="w-5 h-5 text-red-400" />
                  <span className="font-medium text-dark-200">{failure.question}</span>
                </div>
                
                <div className="ml-8 space-y-3">
                  <div className="p-3 rounded bg-dark-900">
                    <p className="text-xs text-dark-400 mb-2">Failed Record Data</p>
                    <pre className="text-xs text-dark-300 overflow-x-auto">
                      {JSON.stringify(failure.record, null, 2)}
                    </pre>
                  </div>
                  
                  <div className="p-3 rounded bg-red-900/30">
                    <p className="text-sm text-red-300">
                      <strong>Error:</strong> {failure.error}
                    </p>
                    <p className="text-xs text-red-400 mt-1">{failure.reason}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Key Insights */}
      <div className="glass-card p-6 bg-gradient-to-br from-purple-500/10 to-blue-500/10">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-purple-400" />
          Understanding This Report
        </h2>
        
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-dark-800/50">
            <h4 className="font-semibold text-emerald-400 mb-2">High Confidence Mappings</h4>
            <p className="text-sm text-dark-300">
              These mappings have 85%+ confidence. The AI is very sure about these 
              connections based on column names, data types, and database conventions.
            </p>
          </div>
          
          <div className="p-4 rounded-xl bg-dark-800/50">
            <h4 className="font-semibold text-amber-400 mb-2">Medium Confidence Mappings</h4>
            <p className="text-sm text-dark-300">
              These mappings (65-85%) are likely correct but should be reviewed. 
              The column names are similar but not identical.
            </p>
          </div>
          
          <div className="p-4 rounded-xl bg-dark-800/50">
            <h4 className="font-semibold text-red-400 mb-2">Low Confidence Mappings</h4>
            <p className="text-sm text-dark-300">
              These mappings are uncertain and require manual review. 
              The AI found some similarity but isn't confident.
            </p>
          </div>
          
          <div className="p-4 rounded-xl bg-dark-800/50">
            <h4 className="font-semibold text-dark-400 mb-2">Unmapped Columns</h4>
            <p className="text-sm text-dark-300">
              These columns couldn't be matched. They may be deprecated, 
              renamed significantly, or new in the target schema.
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

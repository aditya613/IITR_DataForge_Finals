import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle,
  Database,
  Copy,
  AlertCircle,
  Download,
  BarChart3,
  Hash,
  FileX
} from 'lucide-react'
import { getValidationReport, ValidationReport } from '../api'

export default function ValidationReportPage() {
  const [sessionId, setSessionId] = useState<string | null>(null)

  useEffect(() => {
    const id = localStorage.getItem('sessionId')
    if (id) setSessionId(id)
  }, [])

  const { data: report, isLoading, error } = useQuery({
    queryKey: ['validation-report', sessionId],
    queryFn: () => getValidationReport(sessionId!),
    enabled: !!sessionId
  })

  if (!sessionId) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <AlertCircle className="w-16 h-16 text-dark-600 mb-4" />
        <h2 className="text-xl font-semibold text-dark-400">No Session Found</h2>
        <p className="text-dark-500 mt-2">Upload and migrate data first</p>
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
        <h2 className="text-xl font-semibold text-dark-400">Validation Report Not Available</h2>
        <p className="text-dark-500 mt-2">Execute migration first to generate the validation report</p>
      </div>
    )
  }

  const exportReport = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `validation_report_${sessionId}.json`
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
          <h1 className="text-3xl font-bold">Validation Report</h1>
          <p className="text-dark-400 mt-1">Data integrity checks and migration validation</p>
        </div>
        <button onClick={exportReport} className="btn-secondary flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export JSON
        </button>
      </div>

      {/* Summary Card */}
      <div className={`glass-card p-6 border-2 ${report.is_valid ? 'border-emerald-500/50' : 'border-amber-500/50'}`}>
        <div className="flex items-start gap-4">
          {report.is_valid ? (
            <CheckCircle2 className="w-12 h-12 text-emerald-400 flex-shrink-0" />
          ) : (
            <AlertTriangle className="w-12 h-12 text-amber-400 flex-shrink-0" />
          )}
          <div>
            <h2 className={`text-2xl font-bold ${report.is_valid ? 'text-emerald-400' : 'text-amber-400'}`}>
              {report.is_valid ? 'All Validation Checks Passed' : 'Validation Issues Found'}
            </h2>
            <p className="text-dark-300 mt-2">{report.summary}</p>
          </div>
        </div>
      </div>

      {/* Migration Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card p-6 text-center">
          <Database className="w-8 h-8 text-primary-400 mx-auto mb-2" />
          <p className="text-3xl font-bold text-primary-400">{report.migration_stats.rows_migrated}</p>
          <p className="text-sm text-dark-400">Rows Migrated</p>
        </div>
        <div className="glass-card p-6 text-center">
          <XCircle className="w-8 h-8 text-red-400 mx-auto mb-2" />
          <p className="text-3xl font-bold text-red-400">{report.migration_stats.rows_failed}</p>
          <p className="text-sm text-dark-400">Rows Failed</p>
        </div>
        <div className="glass-card p-6 text-center">
          <Hash className="w-8 h-8 text-amber-400 mx-auto mb-2" />
          <p className="text-3xl font-bold text-amber-400">
            {Object.values(report.duplicate_checks).filter((d: any) => d.has_duplicates).length}
          </p>
          <p className="text-sm text-dark-400">Duplicate Issues</p>
        </div>
        <div className="glass-card p-6 text-center">
          <FileX className="w-8 h-8 text-orange-400 mx-auto mb-2" />
          <p className="text-3xl font-bold text-orange-400">
            {Object.values(report.null_checks).filter((n: any) => !n.match).length}
          </p>
          <p className="text-sm text-dark-400">Null Mismatches</p>
        </div>
      </div>

      {/* Row Count Comparison */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-primary-400" />
          Row Count Comparison
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-dark-700">
                <th className="px-4 py-3 text-left text-sm font-semibold text-dark-300">Table Mapping</th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-dark-300">Source Count</th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-dark-300">Target Count</th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-dark-300">Difference</th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-dark-300">Status</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(report.row_comparison).map(([key, value]: [string, any]) => (
                <tr key={key} className="border-b border-dark-800 hover:bg-dark-800/50">
                  <td className="px-4 py-3">
                    <code className="text-sm text-primary-400">{key}</code>
                  </td>
                  <td className="px-4 py-3 text-center font-semibold">{value.source}</td>
                  <td className="px-4 py-3 text-center font-semibold">{value.target}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={value.difference === 0 ? 'text-emerald-400' : 'text-amber-400'}>
                      {value.difference >= 0 ? '+' : ''}{value.difference}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {value.match ? (
                      <span className="badge-high">Match</span>
                    ) : (
                      <span className="badge-medium">Mismatch</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Null Checks */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-orange-400" />
          Null Value Checks
        </h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(report.null_checks).map(([key, value]: [string, any]) => (
            <div 
              key={key} 
              className={`p-4 rounded-xl ${value.match ? 'bg-emerald-500/10' : 'bg-amber-500/10'}`}
            >
              <code className="text-sm text-primary-400">{key}</code>
              <div className="flex items-center justify-between mt-2">
                <div>
                  <p className="text-xs text-dark-400">Source</p>
                  <p className="font-semibold">{value.source_nulls} nulls</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-dark-400">Target</p>
                  <p className="font-semibold">{value.target_nulls} nulls</p>
                </div>
              </div>
              <div className="mt-2 text-center">
                {value.match ? (
                  <span className="text-emerald-400 text-sm">✓ Consistent</span>
                ) : (
                  <span className="text-amber-400 text-sm">⚠ Mismatch</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Duplicate Checks */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Copy className="w-5 h-5 text-amber-400" />
          Duplicate Checks
        </h3>
        {Object.keys(report.duplicate_checks).length === 0 ? (
          <p className="text-dark-400">No identifier columns checked for duplicates</p>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(report.duplicate_checks).map(([column, value]: [string, any]) => (
              <div 
                key={column}
                className={`p-4 rounded-xl ${!value.has_duplicates ? 'bg-emerald-500/10' : 'bg-red-500/10'}`}
              >
                <code className="text-sm text-primary-400">{column}</code>
                <div className="mt-2">
                  {!value.has_duplicates ? (
                    <span className="text-emerald-400 flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4" />
                      No duplicates found
                    </span>
                  ) : (
                    <span className="text-red-400 flex items-center gap-1">
                      <XCircle className="w-4 h-4" />
                      {value.duplicate_count} duplicate values
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Failed Records */}
      {report.failed_records.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-red-400">
            <XCircle className="w-5 h-5" />
            Failed Records ({report.failed_records.length})
          </h3>
          <p className="text-dark-400 mb-4">
            These records failed to migrate. Review the errors below.
          </p>
          <div className="space-y-4">
            {report.failed_records.map((record, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="p-4 rounded-xl bg-red-500/10 border border-red-500/30"
              >
                <div className="flex items-start justify-between mb-2">
                  <code className="text-sm text-red-400">
                    {record.source_table} → {record.target_table}
                  </code>
                  <span className="badge-low">Failed</span>
                </div>
                <div className="mt-2">
                  <p className="text-sm font-semibold text-dark-300">Data:</p>
                  <pre className="text-xs text-dark-400 bg-dark-900 p-2 rounded mt-1 overflow-x-auto">
                    {JSON.stringify(record.data, null, 2)}
                  </pre>
                </div>
                <div className="mt-3 p-3 rounded bg-dark-900">
                  <p className="text-sm font-semibold text-red-400">Error:</p>
                  <p className="text-sm text-dark-300">{record.error}</p>
                  <p className="text-xs text-dark-500 mt-1">{record.reason}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}

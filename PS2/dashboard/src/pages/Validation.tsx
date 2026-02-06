import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  ShieldCheck,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Loader2,
  FileWarning,
  Database
} from 'lucide-react'
import toast from 'react-hot-toast'
import { runValidation, ValidationResult } from '../api'

export default function Validation() {
  const [sourcePath, setSourcePath] = useState<string>('')
  const [targetPath, setTargetPath] = useState<string>('')
  const [validating, setValidating] = useState(false)
  const [result, setResult] = useState<ValidationResult | null>(null)

  useEffect(() => {
    const storedSource = localStorage.getItem('sourcePath')
    const storedTarget = localStorage.getItem('targetPath')
    if (storedSource) setSourcePath(storedSource)
    if (storedTarget) setTargetPath(storedTarget)
  }, [])

  const handleValidate = async () => {
    if (!sourcePath || !targetPath) {
      toast.error('Please run analysis first to set database paths')
      return
    }

    setValidating(true)
    try {
      const validationResult = await runValidation(sourcePath, targetPath)
      setResult(validationResult)
      toast.success('Validation complete!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Validation failed')
    }
    setValidating(false)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed': return <CheckCircle className="w-5 h-5 text-emerald-400" />
      case 'failed': return <XCircle className="w-5 h-5 text-red-400" />
      case 'warning': return <AlertTriangle className="w-5 h-5 text-amber-400" />
      default: return <FileWarning className="w-5 h-5 text-dark-400" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-500/20 border-red-500/30'
      case 'high': return 'text-orange-400 bg-orange-500/20 border-orange-500/30'
      case 'medium': return 'text-amber-400 bg-amber-500/20 border-amber-500/30'
      case 'low': return 'text-blue-400 bg-blue-500/20 border-blue-500/30'
      default: return 'text-dark-400 bg-dark-700 border-dark-600'
    }
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
          <h1 className="text-3xl font-bold">Data Validation</h1>
          <p className="text-dark-400 mt-2">
            Pre-migration data quality checks and integrity validation
          </p>
        </div>

        <button
          onClick={handleValidate}
          disabled={validating}
          className="btn-primary flex items-center gap-2"
        >
          {validating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Validating...
            </>
          ) : (
            <>
              <RefreshCw className="w-5 h-5" />
              Run Validation
            </>
          )}
        </button>
      </div>

      {/* Database Paths */}
      <div className="glass-card p-6">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <Database className="w-5 h-5 text-primary-400" />
          Database Paths
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-dark-400 mb-2">Source Database</label>
            <code className="text-sm text-blue-400 bg-dark-800 px-3 py-2 rounded-lg block">
              {sourcePath || 'Not set'}
            </code>
          </div>
          <div>
            <label className="block text-sm text-dark-400 mb-2">Target Database</label>
            <code className="text-sm text-purple-400 bg-dark-800 px-3 py-2 rounded-lg block">
              {targetPath || 'Not set'}
            </code>
          </div>
        </div>
      </div>

      {/* Results */}
      {result && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="stat-card"
            >
              <p className="text-dark-400 text-sm">Total Checks</p>
              <p className="text-3xl font-bold mt-2">{result.summary.total}</p>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="stat-card border-l-4 border-emerald-500"
            >
              <p className="text-dark-400 text-sm">Passed</p>
              <p className="text-3xl font-bold mt-2 text-emerald-400">{result.summary.passed}</p>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="stat-card border-l-4 border-amber-500"
            >
              <p className="text-dark-400 text-sm">Warnings</p>
              <p className="text-3xl font-bold mt-2 text-amber-400">{result.summary.warnings}</p>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="stat-card border-l-4 border-red-500"
            >
              <p className="text-dark-400 text-sm">Failed</p>
              <p className="text-3xl font-bold mt-2 text-red-400">{result.summary.failed}</p>
            </motion.div>
          </div>

          {/* Progress Bar */}
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold">Validation Health</span>
              <span className="text-emerald-400 font-semibold">
                {((result.summary.passed / result.summary.total) * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-4 bg-dark-700 rounded-full overflow-hidden flex">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(result.summary.passed / result.summary.total) * 100}%` }}
                transition={{ duration: 1 }}
                className="h-full bg-emerald-500"
              />
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(result.summary.warnings / result.summary.total) * 100}%` }}
                transition={{ duration: 1, delay: 0.2 }}
                className="h-full bg-amber-500"
              />
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(result.summary.failed / result.summary.total) * 100}%` }}
                transition={{ duration: 1, delay: 0.4 }}
                className="h-full bg-red-500"
              />
            </div>
          </div>

          {/* Results List */}
          <div className="glass-card overflow-hidden">
            <div className="p-4 border-b border-dark-700">
              <h3 className="font-semibold flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-primary-400" />
                Validation Results
              </h3>
            </div>

            <div className="divide-y divide-dark-700/50">
              {result.results.map((check, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="p-4 hover:bg-dark-700/30 transition-colors"
                >
                  <div className="flex items-start gap-4">
                    {getStatusIcon(check.status)}
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <h4 className="font-semibold">{check.check_name}</h4>
                        <span className={`text-xs px-2 py-0.5 rounded border ${getSeverityColor(check.severity)}`}>
                          {check.severity}
                        </span>
                      </div>
                      <p className="text-dark-400 text-sm">{check.message}</p>
                      
                      {check.recommendations && check.recommendations.length > 0 && (
                        <div className="mt-3 pl-4 border-l-2 border-primary-500/30">
                          <p className="text-xs text-dark-500 mb-1">Recommendations:</p>
                          <ul className="text-sm text-dark-300 space-y-1">
                            {check.recommendations.map((rec, i) => (
                              <li key={i}>• {rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </>
      )}

      {!result && !validating && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center justify-center h-64 glass-card"
        >
          <ShieldCheck className="w-16 h-16 text-dark-600 mb-4" />
          <h2 className="text-xl font-semibold text-dark-400">No Validation Results</h2>
          <p className="text-dark-500 mt-2">Click "Run Validation" to check data quality</p>
        </motion.div>
      )}
    </motion.div>
  )
}

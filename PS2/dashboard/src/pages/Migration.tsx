import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Rocket,
  Play,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
  Database,
  ArrowRight
} from 'lucide-react'
import toast from 'react-hot-toast'
import { executeMigration, MigrationResult, ColumnMapping } from '../api'

export default function Migration() {
  const [sourcePath, setSourcePath] = useState<string>('')
  const [targetPath, setTargetPath] = useState<string>('')
  const [mappings, setMappings] = useState<ColumnMapping[]>([])
  const [batchSize, setBatchSize] = useState(100)
  const [migrating, setMigrating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<MigrationResult | null>(null)

  useEffect(() => {
    const storedSource = localStorage.getItem('sourcePath')
    const storedTarget = localStorage.getItem('targetPath')
    const storedResult = localStorage.getItem('analysisResult')
    
    if (storedSource) setSourcePath(storedSource)
    if (storedTarget) setTargetPath(storedTarget)
    if (storedResult) {
      const parsed = JSON.parse(storedResult)
      setMappings(parsed.all_mappings || [])
    }
  }, [])

  const handleMigrate = async () => {
    if (!sourcePath || !targetPath || mappings.length === 0) {
      toast.error('Please run analysis first to set up migration')
      return
    }

    setMigrating(true)
    setProgress(0)
    
    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress(p => Math.min(p + 10, 90))
    }, 500)

    try {
      const migrationResult = await executeMigration(sourcePath, targetPath, mappings, batchSize)
      setResult(migrationResult)
      setProgress(100)
      
      if (migrationResult.status === 'success') {
        toast.success('Migration completed successfully!')
      } else {
        toast.error('Migration completed with errors')
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Migration failed')
    }
    
    clearInterval(progressInterval)
    setMigrating(false)
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Execute Migration</h1>
        <p className="text-dark-400 mt-2">
          Safely migrate data with batch processing and transaction support
        </p>
      </div>

      {/* Warning */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex items-start gap-3"
      >
        <AlertTriangle className="w-6 h-6 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-semibold text-amber-400">Caution</h3>
          <p className="text-amber-300/80 text-sm mt-1">
            This will modify the target database. Make sure you have a backup before proceeding.
            The migration uses transactions for safety and can be rolled back if errors occur.
          </p>
        </div>
      </motion.div>

      {/* Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card p-6"
        >
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-400" />
            Source Database
          </h3>
          <code className="text-sm text-blue-400 bg-dark-800 px-3 py-2 rounded-lg block">
            {sourcePath || 'Not set - Run analysis first'}
          </code>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card p-6"
        >
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-purple-400" />
            Target Database
          </h3>
          <code className="text-sm text-purple-400 bg-dark-800 px-3 py-2 rounded-lg block">
            {targetPath || 'Not set - Run analysis first'}
          </code>
        </motion.div>
      </div>

      {/* Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6"
      >
        <h3 className="font-semibold mb-4">Migration Settings</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm text-dark-400 mb-2">Batch Size</label>
            <input
              type="number"
              value={batchSize}
              onChange={(e) => setBatchSize(parseInt(e.target.value))}
              min="1"
              max="10000"
              className="input-field"
            />
            <p className="text-xs text-dark-500 mt-1">Records per batch</p>
          </div>
          
          <div>
            <label className="block text-sm text-dark-400 mb-2">Mappings to Migrate</label>
            <div className="input-field bg-dark-800 flex items-center">
              <span className="text-2xl font-bold gradient-text">{mappings.length}</span>
              <span className="text-dark-400 ml-2">columns</span>
            </div>
          </div>
          
          <div>
            <label className="block text-sm text-dark-400 mb-2">Transaction Mode</label>
            <div className="input-field bg-dark-800 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              <span>Enabled (Safe)</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Execute Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-center"
      >
        <button
          onClick={handleMigrate}
          disabled={migrating || mappings.length === 0}
          className="btn-primary flex items-center gap-3 text-lg px-8 py-4"
        >
          {migrating ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              Migrating...
            </>
          ) : (
            <>
              <Rocket className="w-6 h-6" />
              Execute Migration
              <ArrowRight className="w-6 h-6" />
            </>
          )}
        </button>
      </motion.div>

      {/* Progress */}
      {migrating && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold">Migration Progress</span>
            <span className="text-primary-400 font-semibold">{progress}%</span>
          </div>
          <div className="h-4 bg-dark-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              className="h-full bg-gradient-to-r from-primary-500 to-secondary-500"
            />
          </div>
        </motion.div>
      )}

      {/* Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="stat-card border-l-4 border-emerald-500">
              <p className="text-dark-400 text-sm">Records Migrated</p>
              <p className="text-3xl font-bold mt-2 text-emerald-400">
                {result.summary.total_migrated.toLocaleString()}
              </p>
            </div>
            
            <div className="stat-card border-l-4 border-red-500">
              <p className="text-dark-400 text-sm">Records Failed</p>
              <p className="text-3xl font-bold mt-2 text-red-400">
                {result.summary.total_failed.toLocaleString()}
              </p>
            </div>
            
            <div className="stat-card border-l-4 border-primary-500">
              <p className="text-dark-400 text-sm">Success Rate</p>
              <p className="text-3xl font-bold mt-2 gradient-text">
                {result.summary.success_rate}%
              </p>
            </div>
          </div>

          {/* Table Results */}
          <div className="glass-card overflow-hidden">
            <div className="p-4 border-b border-dark-700">
              <h3 className="font-semibold">Table Results</h3>
            </div>
            <div className="divide-y divide-dark-700/50">
              {result.table_results.map((table, idx) => (
                <div key={idx} className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-blue-400 font-mono">{table.source_table}</span>
                    <ArrowRight className="w-4 h-4 text-dark-500" />
                    <span className="text-purple-400 font-mono">{table.target_table}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-emerald-400">
                      <CheckCircle className="w-4 h-4 inline mr-1" />
                      {table.records_migrated}
                    </span>
                    {table.records_failed > 0 && (
                      <span className="text-red-400">
                        <XCircle className="w-4 h-4 inline mr-1" />
                        {table.records_failed}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Failed Records */}
          {result.failed_records.length > 0 && (
            <div className="glass-card overflow-hidden">
              <div className="p-4 border-b border-dark-700">
                <h3 className="font-semibold text-red-400 flex items-center gap-2">
                  <XCircle className="w-5 h-5" />
                  Failed Records ({result.failed_records.length})
                </h3>
              </div>
              <div className="max-h-64 overflow-y-auto divide-y divide-dark-700/50">
                {result.failed_records.slice(0, 10).map((record, idx) => (
                  <div key={idx} className="p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-dark-400">ID:</span>
                      <code className="text-red-400">{record.record_id}</code>
                    </div>
                    <p className="text-sm text-dark-300">{record.error_message}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  )
}

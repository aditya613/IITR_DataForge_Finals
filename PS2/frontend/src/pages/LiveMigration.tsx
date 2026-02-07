import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useSearchParams } from 'react-router-dom'
import {
  Play,
  CheckCircle,
  XCircle,
  Database,
  ArrowRight,
  Loader2,
  Zap,
  Table,
  Clock,
  TrendingUp,
  Activity,
  Server,
  HardDrive,
  RefreshCw
} from 'lucide-react'
import { executeLiveMigration, createMigrationWebSocket, LiveMigrationUpdate } from '../api'

interface TableProgress {
  source: string
  target: string
  status: 'pending' | 'migrating' | 'completed' | 'error'
  rows: number
  migrated: number
  failed: number
  progress: number
}

export default function LiveMigration() {
  const [searchParams] = useSearchParams()
  const sessionId = searchParams.get('session') || ''
  
  const [migrationState, setMigrationState] = useState<'idle' | 'connecting' | 'running' | 'completed' | 'error'>('idle')
  const [phase, setPhase] = useState<string>('Ready to migrate')
  const [totalTables, setTotalTables] = useState(0)
  const [migratedTables, setMigratedTables] = useState(0)
  const [totalRows, setTotalRows] = useState(0)
  const [migratedRows, setMigratedRows] = useState(0)
  const [failedRows, setFailedRows] = useState(0)
  const [currentTable, setCurrentTable] = useState('')
  const [tableProgress, setTableProgress] = useState<TableProgress[]>([])
  const [logs, setLogs] = useState<Array<{ time: string; message: string; type: 'info' | 'success' | 'error' | 'warning' }>>([])
  const [startTime, setStartTime] = useState<Date | null>(null)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [validationResult, setValidationResult] = useState<Record<string, unknown> | null>(null)
  
  const wsRef = useRef<WebSocket | null>(null)
  const logContainerRef = useRef<HTMLDivElement>(null)

  // Add log entry
  const addLog = useCallback((message: string, type: 'info' | 'success' | 'error' | 'warning' = 'info') => {
    const time = new Date().toLocaleTimeString()
    setLogs(prev => [...prev.slice(-100), { time, message, type }])
  }, [])

  // Start migration
  const startMigration = async () => {
    if (!sessionId) {
      addLog('No session ID provided', 'error')
      return
    }

    setMigrationState('connecting')
    setPhase('Connecting to server...')
    addLog('Initiating WebSocket connection...', 'info')
    
    // Connect WebSocket
    const ws = createMigrationWebSocket(sessionId)
    wsRef.current = ws
    
    ws.onopen = async () => {
      addLog('WebSocket connected', 'success')
      setPhase('Starting migration...')
      setStartTime(new Date())
      setMigrationState('running')
      
      try {
        await executeLiveMigration(sessionId)
      } catch (err) {
        addLog(`Migration failed: ${err}`, 'error')
        setMigrationState('error')
      }
    }
    
    ws.onmessage = (event) => {
      try {
        const update: LiveMigrationUpdate = JSON.parse(event.data)
        handleMigrationUpdate(update)
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err)
      }
    }
    
    ws.onerror = () => {
      addLog('WebSocket error', 'error')
      setMigrationState('error')
    }
    
    ws.onclose = () => {
      addLog('WebSocket connection closed', 'info')
    }
  }

  // Handle migration updates
  const handleMigrationUpdate = (update: LiveMigrationUpdate) => {
    const { type, data } = update
    
    switch (type) {
      case 'migration_start':
        addLog('Migration started', 'success')
        setPhase('Initializing...')
        break
        
      case 'migration_progress':
        setTotalTables(data.total_tables as number)
        setTotalRows(data.total_rows as number)
        setPhase(`Found ${data.total_rows} rows across ${data.total_tables} tables`)
        addLog(`Discovered ${data.total_rows} rows in ${data.total_tables} tables`, 'info')
        break
        
      case 'table_start': {
        setCurrentTable(`${data.source_table} → ${data.target_table}`)
        setPhase(`Migrating: ${data.source_table}`)
        addLog(`Starting table: ${data.source_table} → ${data.target_table} (${data.total_rows} rows)`, 'info')
        
        setTableProgress(prev => {
          const existing = prev.findIndex(t => t.source === data.source_table)
          if (existing >= 0) {
            const updated = [...prev]
            updated[existing] = { ...updated[existing], status: 'migrating' }
            return updated
          }
          return [...prev, {
            source: data.source_table as string,
            target: data.target_table as string,
            status: 'migrating',
            rows: data.total_rows as number,
            migrated: 0,
            failed: 0,
            progress: 0
          }]
        })
        break
      }
        
      case 'row_progress':
        setMigratedRows(data.overall_migrated as number)
        setFailedRows(data.overall_failed as number)
        setTableProgress(prev => {
          const updated = [...prev]
          const idx = updated.findIndex(t => t.source === data.table)
          if (idx >= 0) {
            updated[idx] = {
              ...updated[idx],
              migrated: data.migrated as number,
              failed: data.failed as number,
              progress: data.progress_percent as number
            }
          }
          return updated
        })
        break
        
      case 'table_complete':
        setMigratedTables(data.table_index as number)
        addLog(`✓ Completed: ${data.source_table} → ${data.target_table} (${data.migrated} migrated, ${data.failed} failed)`, 
               data.failed === 0 ? 'success' : 'warning')
        
        setTableProgress(prev => {
          const updated = [...prev]
          const idx = updated.findIndex(t => t.source === data.source_table)
          if (idx >= 0) {
            updated[idx] = {
              ...updated[idx],
              status: data.failed === 0 ? 'completed' : 'error',
              migrated: data.migrated as number,
              failed: data.failed as number,
              progress: 100
            }
          }
          return updated
        })
        break
        
      case 'phase_change':
        setPhase(data.message as string)
        addLog(data.message as string, 'info')
        break
        
      case 'migration_complete':
        setMigrationState('completed')
        setPhase('Migration completed!')
        setValidationResult(data.validation_summary as Record<string, unknown>)
        addLog(`🎉 Migration complete! ${data.total_migrated} rows migrated, ${data.total_failed} failed`, 
               data.total_failed === 0 ? 'success' : 'warning')
        wsRef.current?.close()
        break
        
      case 'migration_error':
        setMigrationState('error')
        setPhase('Migration failed')
        addLog(`❌ Error: ${data.error}`, 'error')
        break
        
      case 'table_error':
        addLog(`❌ Table error (${data.table}): ${data.error}`, 'error')
        break
    }
  }

  // Update elapsed time
  useEffect(() => {
    if (migrationState === 'running' && startTime) {
      const interval = setInterval(() => {
        setElapsedTime(Math.floor((new Date().getTime() - startTime.getTime()) / 1000))
      }, 1000)
      return () => clearInterval(interval)
    }
  }, [migrationState, startTime])

  // Auto-scroll logs
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs])

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      wsRef.current?.close()
    }
  }, [])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const overallProgress = totalRows > 0 ? Math.round((migratedRows / totalRows) * 100) : 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg shadow-purple-500/25">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Live Migration</h1>
                <p className="text-sm text-gray-400">Real-time data migration with progress tracking</p>
              </div>
            </div>
            
            {migrationState === 'idle' && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={startMigration}
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold shadow-lg shadow-green-500/25 hover:shadow-green-500/40 transition-shadow"
              >
                <Play className="w-5 h-5" />
                Start Migration
              </motion.button>
            )}
            
            {migrationState === 'running' && (
              <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-blue-500/20 border border-blue-500/30">
                <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                <span className="text-blue-300 font-medium">Migrating...</span>
              </div>
            )}
            
            {migrationState === 'completed' && (
              <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-green-500/20 border border-green-500/30">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-green-300 font-medium">Complete!</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatsCard 
            icon={<Table className="w-5 h-5" />}
            label="Tables"
            value={`${migratedTables}/${totalTables}`}
            progress={(migratedTables / Math.max(totalTables, 1)) * 100}
            color="purple"
          />
          <StatsCard 
            icon={<Database className="w-5 h-5" />}
            label="Rows Migrated"
            value={migratedRows.toLocaleString()}
            progress={overallProgress}
            color="blue"
          />
          <StatsCard 
            icon={<XCircle className="w-5 h-5" />}
            label="Failed"
            value={failedRows.toLocaleString()}
            color="red"
          />
          <StatsCard 
            icon={<Clock className="w-5 h-5" />}
            label="Elapsed Time"
            value={formatTime(elapsedTime)}
            color="amber"
          />
        </div>

        {/* Main Progress Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Overall Progress */}
          <div className="lg:col-span-2">
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-purple-400" />
                  Migration Progress
                </h2>
                <span className="text-3xl font-bold text-white">{overallProgress}%</span>
              </div>
              
              {/* Progress Bar */}
              <div className="relative h-4 bg-slate-800 rounded-full overflow-hidden mb-4">
                <motion.div
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${overallProgress}%` }}
                  transition={{ duration: 0.5 }}
                >
                  <div className="absolute inset-0 bg-[linear-gradient(90deg,transparent,rgba(255,255,255,0.3),transparent)] animate-shimmer" />
                </motion.div>
              </div>
              
              <div className="flex items-center justify-between text-sm text-gray-400">
                <span>Current: {currentTable || 'Waiting...'}</span>
                <span>{phase}</span>
              </div>
            </div>
          </div>

          {/* Status Panel */}
          <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Server className="w-5 h-5 text-blue-400" />
              Status
            </h2>
            
            <div className="space-y-4">
              <StatusItem 
                label="Connection" 
                status={migrationState !== 'idle' ? 'active' : 'inactive'} 
              />
              <StatusItem 
                label="Source DB" 
                status={migrationState === 'running' ? 'reading' : 'ready'} 
              />
              <StatusItem 
                label="Target DB" 
                status={migrationState === 'running' ? 'writing' : 'ready'} 
              />
              <StatusItem 
                label="Validation" 
                status={phase.includes('Validat') ? 'active' : 'pending'} 
              />
            </div>
          </div>
        </div>

        {/* Table Progress */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Tables List */}
          <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <HardDrive className="w-5 h-5 text-green-400" />
              Table Migration Status
            </h2>
            
            <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-white/20">
              <AnimatePresence mode="popLayout">
                {tableProgress.map((table, idx) => (
                  <TableProgressCard key={table.source} table={table} index={idx} />
                ))}
                
                {tableProgress.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Database className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>Tables will appear here during migration</p>
                  </div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Live Log */}
          <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-amber-400" />
              Migration Log
            </h2>
            
            <div 
              ref={logContainerRef}
              className="h-[400px] overflow-y-auto font-mono text-sm space-y-1 pr-2 scrollbar-thin scrollbar-thumb-white/20"
            >
              {logs.map((log, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`flex items-start gap-2 ${
                    log.type === 'error' ? 'text-red-400' :
                    log.type === 'success' ? 'text-green-400' :
                    log.type === 'warning' ? 'text-amber-400' :
                    'text-gray-400'
                  }`}
                >
                  <span className="text-gray-600 shrink-0">[{log.time}]</span>
                  <span>{log.message}</span>
                </motion.div>
              ))}
              
              {logs.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <p>Logs will appear here</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Validation Results (shown after completion) */}
        <AnimatePresence>
          {migrationState === 'completed' && validationResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 backdrop-blur-xl rounded-2xl border border-green-500/30 p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-lg bg-green-500/20">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-white">Migration Complete!</h2>
                  <p className="text-sm text-green-400">All data has been successfully migrated</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-black/20 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Total Rows</p>
                  <p className="text-2xl font-bold text-white">{migratedRows.toLocaleString()}</p>
                </div>
                <div className="bg-black/20 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Tables Migrated</p>
                  <p className="text-2xl font-bold text-white">{migratedTables}</p>
                </div>
                <div className="bg-black/20 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Failed Rows</p>
                  <p className="text-2xl font-bold text-red-400">{failedRows}</p>
                </div>
                <div className="bg-black/20 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Duration</p>
                  <p className="text-2xl font-bold text-white">{formatTime(elapsedTime)}</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Animated background elements */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        {migrationState === 'running' && (
          <>
            <motion.div
              className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl"
              animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
              transition={{ duration: 4, repeat: Infinity }}
            />
            <motion.div
              className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-pink-500/10 rounded-full blur-3xl"
              animate={{ scale: [1.2, 1, 1.2], opacity: [0.5, 0.3, 0.5] }}
              transition={{ duration: 4, repeat: Infinity }}
            />
          </>
        )}
      </div>

      {/* CSS for shimmer animation */}
      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
      `}</style>
    </div>
  )
}

// Stats Card Component
function StatsCard({ icon, label, value, progress, color }: { 
  icon: React.ReactNode
  label: string
  value: string
  progress?: number
  color: 'purple' | 'blue' | 'red' | 'amber' | 'green'
}) {
  const colors = {
    purple: 'from-purple-500 to-pink-500',
    blue: 'from-blue-500 to-cyan-500',
    red: 'from-red-500 to-orange-500',
    amber: 'from-amber-500 to-yellow-500',
    green: 'from-green-500 to-emerald-500'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/5 backdrop-blur-xl rounded-xl border border-white/10 p-4"
    >
      <div className="flex items-center gap-3 mb-2">
        <div className={`p-2 rounded-lg bg-gradient-to-br ${colors[color]} bg-opacity-20`}>
          {icon}
        </div>
        <span className="text-sm text-gray-400">{label}</span>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      {progress !== undefined && (
        <div className="mt-2 h-1 bg-slate-800 rounded-full overflow-hidden">
          <motion.div
            className={`h-full bg-gradient-to-r ${colors[color]}`}
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      )}
    </motion.div>
  )
}

// Status Item Component
function StatusItem({ label, status }: { label: string; status: 'active' | 'inactive' | 'reading' | 'writing' | 'ready' | 'pending' }) {
  const statusConfig = {
    active: { color: 'bg-green-500', text: 'Active', animate: true },
    inactive: { color: 'bg-gray-500', text: 'Inactive', animate: false },
    reading: { color: 'bg-blue-500', text: 'Reading', animate: true },
    writing: { color: 'bg-purple-500', text: 'Writing', animate: true },
    ready: { color: 'bg-emerald-500', text: 'Ready', animate: false },
    pending: { color: 'bg-gray-500', text: 'Pending', animate: false }
  }

  const config = statusConfig[status]

  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-400">{label}</span>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${config.color} ${config.animate ? 'animate-pulse' : ''}`} />
        <span className="text-sm text-gray-300">{config.text}</span>
      </div>
    </div>
  )
}

// Table Progress Card
function TableProgressCard({ table, index }: { table: TableProgress; index: number }) {
  const statusIcons = {
    pending: <Clock className="w-4 h-4 text-gray-400" />,
    migrating: <RefreshCw className="w-4 h-4 text-blue-400 animate-spin" />,
    completed: <CheckCircle className="w-4 h-4 text-green-400" />,
    error: <XCircle className="w-4 h-4 text-red-400" />
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`p-3 rounded-lg border ${
        table.status === 'completed' ? 'bg-green-500/10 border-green-500/30' :
        table.status === 'migrating' ? 'bg-blue-500/10 border-blue-500/30' :
        table.status === 'error' ? 'bg-red-500/10 border-red-500/30' :
        'bg-white/5 border-white/10'
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {statusIcons[table.status]}
          <span className="text-sm text-white font-medium">{table.source}</span>
          <ArrowRight className="w-3 h-3 text-gray-500" />
          <span className="text-sm text-gray-400">{table.target}</span>
        </div>
        <span className="text-xs text-gray-500">{table.rows} rows</span>
      </div>
      
      <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${
            table.status === 'completed' ? 'bg-green-500' :
            table.status === 'error' ? 'bg-red-500' :
            'bg-blue-500'
          }`}
          initial={{ width: 0 }}
          animate={{ width: `${table.progress}%` }}
        />
      </div>
      
      {table.status !== 'pending' && (
        <div className="flex justify-between mt-1 text-xs">
          <span className="text-green-400">{table.migrated} migrated</span>
          {table.failed > 0 && <span className="text-red-400">{table.failed} failed</span>}
        </div>
      )}
    </motion.div>
  )
}

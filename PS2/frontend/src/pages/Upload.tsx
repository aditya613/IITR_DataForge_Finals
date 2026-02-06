import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { useMutation } from '@tanstack/react-query'
import { 
  Upload as UploadIcon, 
  Database, 
  ArrowRight, 
  Play, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  FileUp,
  Sparkles,
  Brain,
  Cpu,
  Layers
} from 'lucide-react'
import toast from 'react-hot-toast'
import { uploadDatabases, analyzeSchemas, executeMigration, createSampleData, UploadResponse, AnalysisResponse } from '../api'

export default function Upload() {
  const [sourceFile, setSourceFile] = useState<File | null>(null)
  const [targetFile, setTargetFile] = useState<File | null>(null)
  const [threshold, setThreshold] = useState(0.65)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null)
  const [migrationResult, setMigrationResult] = useState<any>(null)
  const [usingSampleData, setUsingSampleData] = useState(false)
  const [sampleDataPaths, setSampleDataPaths] = useState<{ source: string; target: string } | null>(null)

  // Sample data mutation
  const sampleDataMutation = useMutation({
    mutationFn: () => createSampleData(),
    onSuccess: async (data) => {
      setSampleDataPaths({ source: data.source_path, target: data.target_path })
      setUsingSampleData(true)
      
      // Fetch the sample files and set them
      const sourceRes = await fetch(`/api/sample-file/source`)
      const targetRes = await fetch(`/api/sample-file/target`)
      
      if (sourceRes.ok && targetRes.ok) {
        const sourceBlob = await sourceRes.blob()
        const targetBlob = await targetRes.blob()
        setSourceFile(new File([sourceBlob], 'legacy_crm.db', { type: 'application/x-sqlite3' }))
        setTargetFile(new File([targetBlob], 'modern_crm.db', { type: 'application/x-sqlite3' }))
        toast.success('Sample databases loaded! Click Upload to continue.')
      } else {
        toast.success('Sample data created on server. Paths shown below.')
      }
    },
    onError: () => toast.error('Failed to create sample data')
  })

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: () => uploadDatabases(sourceFile!, targetFile!),
    onSuccess: (data) => {
      setSessionId(data.session_id)
      setUploadResult(data)
      localStorage.setItem('sessionId', data.session_id)
      toast.success('Databases uploaded successfully!')
    },
    onError: () => toast.error('Failed to upload databases')
  })

  // Analysis mutation
  const analysisMutation = useMutation({
    mutationFn: () => analyzeSchemas(sessionId!, threshold),
    onSuccess: (data) => {
      setAnalysisResult(data)
      localStorage.setItem('analysisComplete', 'true')
      toast.success(`Analysis complete! Found ${data.total_mappings} column mappings`)
    },
    onError: () => toast.error('Analysis failed')
  })

  // Migration mutation
  const migrationMutation = useMutation({
    mutationFn: () => executeMigration(sessionId!),
    onSuccess: (data) => {
      setMigrationResult(data)
      localStorage.setItem('migrationComplete', 'true')
      if (data.success) {
        toast.success(`Migration complete! ${data.rows_migrated} rows migrated`)
      } else {
        toast.error(`Migration had ${data.rows_failed} failures`)
      }
    },
    onError: () => toast.error('Migration failed')
  })

  const handleDrop = useCallback((e: React.DragEvent, type: 'source' | 'target') => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.name.endsWith('.db')) {
      if (type === 'source') setSourceFile(file)
      else setTargetFile(file)
    } else {
      toast.error('Please drop a SQLite (.db) file')
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>, type: 'source' | 'target') => {
    const file = e.target.files?.[0]
    if (file) {
      if (type === 'source') setSourceFile(file)
      else setTargetFile(file)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="space-y-8"
    >
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold">
          <span className="gradient-text">AI-Powered</span> Data Migration
        </h1>
        <p className="text-dark-400 mt-3 max-w-2xl mx-auto">
          Upload your source and target databases. Our hybrid AI system will analyze schemas,
          map columns intelligently, and provide explainable results.
        </p>
      </div>

      {/* AI Models Info */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { name: 'BERT', icon: Brain, weight: '35%', desc: 'Semantic Understanding', color: 'blue' },
          { name: 'Gemini', icon: Sparkles, weight: '30%', desc: 'LLM Reasoning', color: 'purple' },
          { name: 'TF-IDF', icon: Layers, weight: '15%', desc: 'Pattern Matching', color: 'orange' },
          { name: 'Domain', icon: Cpu, weight: '20%', desc: 'DB Conventions', color: 'emerald' },
        ].map((model) => (
          <div key={model.name} className={`glass-card p-4 text-center border-${model.color}-500/30`}>
            <model.icon className={`w-8 h-8 text-${model.color}-400 mx-auto mb-2`} />
            <h3 className="font-semibold">{model.name}</h3>
            <p className="text-xs text-dark-400">{model.desc}</p>
            <span className={`text-sm font-bold text-${model.color}-400`}>{model.weight}</span>
          </div>
        ))}
      </div>

      {/* Upload Section */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Source DB */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => handleDrop(e, 'source')}
          className={`glass-card p-8 border-2 border-dashed transition-all cursor-pointer
            ${sourceFile ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-dark-600 hover:border-primary-500/50'}`}
        >
          <input
            type="file"
            accept=".db,.sqlite,.sqlite3"
            onChange={(e) => handleFileSelect(e, 'source')}
            className="hidden"
            id="source-upload"
          />
          <label htmlFor="source-upload" className="block text-center cursor-pointer">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-blue-500/20 flex items-center justify-center">
              {sourceFile ? (
                <CheckCircle className="w-8 h-8 text-emerald-400" />
              ) : (
                <Database className="w-8 h-8 text-blue-400" />
              )}
            </div>
            <h3 className="text-lg font-semibold mb-2">Source Database</h3>
            {sourceFile ? (
              <p className="text-emerald-400 font-medium">{sourceFile.name}</p>
            ) : (
              <p className="text-dark-400">Drag & drop or click to upload</p>
            )}
          </label>
        </div>

        {/* Target DB */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => handleDrop(e, 'target')}
          className={`glass-card p-8 border-2 border-dashed transition-all cursor-pointer
            ${targetFile ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-dark-600 hover:border-primary-500/50'}`}
        >
          <input
            type="file"
            accept=".db,.sqlite,.sqlite3"
            onChange={(e) => handleFileSelect(e, 'target')}
            className="hidden"
            id="target-upload"
          />
          <label htmlFor="target-upload" className="block text-center cursor-pointer">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-purple-500/20 flex items-center justify-center">
              {targetFile ? (
                <CheckCircle className="w-8 h-8 text-emerald-400" />
              ) : (
                <Database className="w-8 h-8 text-purple-400" />
              )}
            </div>
            <h3 className="text-lg font-semibold mb-2">Target Database</h3>
            {targetFile ? (
              <p className="text-emerald-400 font-medium">{targetFile.name}</p>
            ) : (
              <p className="text-dark-400">Drag & drop or click to upload</p>
            )}
          </label>
        </div>
      </div>

      {/* Threshold Slider */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold">Confidence Threshold</h3>
            <p className="text-sm text-dark-400">Minimum score to accept a column mapping</p>
          </div>
          <span className="text-2xl font-bold text-primary-400">{(threshold * 100).toFixed(0)}%</span>
        </div>
        <input
          type="range"
          min="0.5"
          max="0.95"
          step="0.05"
          value={threshold}
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
          className="w-full accent-primary-500"
        />
        <div className="flex justify-between text-xs text-dark-500 mt-2">
          <span>More Mappings</span>
          <span>Higher Accuracy</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-4 justify-center">
        {/* Use Sample Data Button */}
        <button
          onClick={() => sampleDataMutation.mutate()}
          disabled={sampleDataMutation.isPending}
          className="btn-secondary flex items-center gap-2"
        >
          {sampleDataMutation.isPending ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Database className="w-5 h-5" />
          )}
          {sampleDataMutation.isPending ? 'Creating...' : 'Use Sample Data'}
        </button>

        {/* Upload Button */}
        <button
          onClick={() => uploadMutation.mutate()}
          disabled={!sourceFile || !targetFile || uploadMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          {uploadMutation.isPending ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <FileUp className="w-5 h-5" />
          )}
          {uploadMutation.isPending ? 'Uploading...' : 'Upload Databases'}
        </button>

        {/* Analyze Button */}
        <button
          onClick={() => analysisMutation.mutate()}
          disabled={!sessionId || analysisMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          {analysisMutation.isPending ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Brain className="w-5 h-5" />
          )}
          {analysisMutation.isPending ? 'Analyzing...' : 'Run AI Analysis'}
        </button>

        {/* Migrate Button */}
        <button
          onClick={() => migrationMutation.mutate()}
          disabled={!analysisResult || migrationMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          {migrationMutation.isPending ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Play className="w-5 h-5" />
          )}
          {migrationMutation.isPending ? 'Migrating...' : 'Execute Migration'}
        </button>
      </div>

      {/* Results Section */}
      {uploadResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6"
        >
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            Schema Extracted
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm text-dark-400 mb-2">Source Database</h4>
              <p className="text-lg font-semibold">{uploadResult.source_tables.length} Tables</p>
              <p className="text-dark-400">{uploadResult.source_columns} Columns</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {uploadResult.source_tables.map((t) => (
                  <span key={t} className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-sm">{t}</span>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-sm text-dark-400 mb-2">Target Database</h4>
              <p className="text-lg font-semibold">{uploadResult.target_tables.length} Tables</p>
              <p className="text-dark-400">{uploadResult.target_columns} Columns</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {uploadResult.target_tables.map((t) => (
                  <span key={t} className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-sm">{t}</span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {analysisResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6"
        >
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-400" />
            Analysis Results
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 rounded-xl bg-dark-800">
              <p className="text-3xl font-bold text-primary-400">{analysisResult.total_mappings}</p>
              <p className="text-sm text-dark-400">Total Mappings</p>
            </div>
            <div className="text-center p-4 rounded-xl bg-dark-800">
              <p className="text-3xl font-bold text-emerald-400">{analysisResult.statistics.high_confidence}</p>
              <p className="text-sm text-dark-400">High Confidence</p>
            </div>
            <div className="text-center p-4 rounded-xl bg-dark-800">
              <p className="text-3xl font-bold text-amber-400">{analysisResult.statistics.medium_confidence}</p>
              <p className="text-sm text-dark-400">Medium Confidence</p>
            </div>
            <div className="text-center p-4 rounded-xl bg-dark-800">
              <p className="text-3xl font-bold text-red-400">{analysisResult.statistics.low_confidence}</p>
              <p className="text-sm text-dark-400">Low Confidence</p>
            </div>
          </div>
          <div className="mt-4 flex items-center gap-4 text-sm">
            <span className={`flex items-center gap-1 ${analysisResult.gemini_used ? 'text-emerald-400' : 'text-dark-500'}`}>
              <Sparkles className="w-4 h-4" />
              Gemini {analysisResult.gemini_used ? 'Enabled' : 'Disabled'}
            </span>
            <span className={`flex items-center gap-1 ${analysisResult.statistics.bert_enabled ? 'text-emerald-400' : 'text-dark-500'}`}>
              <Brain className="w-4 h-4" />
              BERT {analysisResult.statistics.bert_enabled ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </motion.div>
      )}

      {migrationResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`glass-card p-6 border ${migrationResult.success ? 'border-emerald-500/50' : 'border-amber-500/50'}`}
        >
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            {migrationResult.success ? (
              <CheckCircle className="w-5 h-5 text-emerald-400" />
            ) : (
              <AlertCircle className="w-5 h-5 text-amber-400" />
            )}
            Migration Complete
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 rounded-xl bg-emerald-500/10">
              <p className="text-3xl font-bold text-emerald-400">{migrationResult.rows_migrated}</p>
              <p className="text-sm text-dark-400">Rows Migrated</p>
            </div>
            <div className="text-center p-4 rounded-xl bg-red-500/10">
              <p className="text-3xl font-bold text-red-400">{migrationResult.rows_failed}</p>
              <p className="text-sm text-dark-400">Rows Failed</p>
            </div>
          </div>
          <p className="mt-4 text-center text-dark-400">
            View detailed reports in the other tabs
          </p>
        </motion.div>
      )}
    </motion.div>
  )
}

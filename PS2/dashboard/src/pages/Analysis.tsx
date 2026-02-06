import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import {
  Upload,
  Database,
  ArrowRight,
  Play,
  Settings,
  Sparkles,
  Brain,
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react'
import toast from 'react-hot-toast'
import { runAnalysis, AnalysisResult, LLMConfig } from '../api'

export default function Analysis() {
  const [sourceDb, setSourceDb] = useState<string>('data/source_legacy_crm.db')
  const [targetDb, setTargetDb] = useState<string>('data/target_modern_crm.db')
  const [threshold, setThreshold] = useState(0.4)
  const [showLlmConfig, setShowLlmConfig] = useState(false)
  const [llmConfig, setLlmConfig] = useState<LLMConfig>({
    provider: 'none',
    api_key: '',
    model: 'gpt-4o-mini',
    base_url: ''
  })
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)

  const handleAnalyze = async () => {
    if (!sourceDb || !targetDb) {
      toast.error('Please specify both database paths')
      return
    }

    setAnalyzing(true)
    try {
      const analysisResult = await runAnalysis({
        source_db_path: sourceDb,
        target_db_path: targetDb,
        threshold,
        llm_config: llmConfig.provider !== 'none' ? llmConfig : undefined
      })
      setResult(analysisResult)
      
      // Store in localStorage for other pages
      localStorage.setItem('analysisResult', JSON.stringify(analysisResult))
      localStorage.setItem('sourcePath', sourceDb)
      localStorage.setItem('targetPath', targetDb)
      
      toast.success(`Analysis complete! Found ${analysisResult.total_mappings} mappings`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Analysis failed')
    }
    setAnalyzing(false)
  }

  const onDropSource = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      toast.success(`Source: ${acceptedFiles[0].name}`)
    }
  }, [])

  const onDropTarget = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      toast.success(`Target: ${acceptedFiles[0].name}`)
    }
  }, [])

  const { getRootProps: getSourceRootProps, getInputProps: getSourceInputProps, isDragActive: isSourceDrag } = useDropzone({
    onDrop: onDropSource,
    accept: { 'application/x-sqlite3': ['.db', '.sqlite'] }
  })

  const { getRootProps: getTargetRootProps, getInputProps: getTargetInputProps, isDragActive: isTargetDrag } = useDropzone({
    onDrop: onDropTarget,
    accept: { 'application/x-sqlite3': ['.db', '.sqlite'] }
  })

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Schema Analysis</h1>
        <p className="text-dark-400 mt-2">
          Use hybrid AI to analyze and match database schemas
        </p>
      </div>

      {/* Database Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Source Database */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card p-6"
        >
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-400" />
            Source Database
          </h3>
          
          <input
            type="text"
            value={sourceDb}
            onChange={(e) => setSourceDb(e.target.value)}
            placeholder="Path to source database"
            className="input-field mb-4"
          />
          
          <div
            {...getSourceRootProps()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
                      transition-all duration-300 ${isSourceDrag 
                        ? 'border-primary-500 bg-primary-500/10' 
                        : 'border-dark-600 hover:border-primary-500/50'}`}
          >
            <input {...getSourceInputProps()} />
            <Upload className="w-8 h-8 text-dark-400 mx-auto mb-2" />
            <p className="text-dark-400 text-sm">
              Drag & drop or click to upload
            </p>
          </div>
        </motion.div>

        {/* Target Database */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card p-6"
        >
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-purple-400" />
            Target Database
          </h3>
          
          <input
            type="text"
            value={targetDb}
            onChange={(e) => setTargetDb(e.target.value)}
            placeholder="Path to target database"
            className="input-field mb-4"
          />
          
          <div
            {...getTargetRootProps()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
                      transition-all duration-300 ${isTargetDrag 
                        ? 'border-secondary-500 bg-secondary-500/10' 
                        : 'border-dark-600 hover:border-secondary-500/50'}`}
          >
            <input {...getTargetInputProps()} />
            <Upload className="w-8 h-8 text-dark-400 mx-auto mb-2" />
            <p className="text-dark-400 text-sm">
              Drag & drop or click to upload
            </p>
          </div>
        </motion.div>
      </div>

      {/* Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="font-semibold flex items-center gap-2">
            <Settings className="w-5 h-5 text-amber-400" />
            Analysis Settings
          </h3>
          
          <button
            onClick={() => setShowLlmConfig(!showLlmConfig)}
            className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1"
          >
            <Sparkles className="w-4 h-4" />
            {showLlmConfig ? 'Hide' : 'Configure'} LLM API
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Threshold Slider */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Matching Threshold: {threshold.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full h-2 bg-dark-700 rounded-full appearance-none cursor-pointer
                       [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 
                       [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full
                       [&::-webkit-slider-thumb]:bg-gradient-to-r [&::-webkit-slider-thumb]:from-primary-500 
                       [&::-webkit-slider-thumb]:to-secondary-500 [&::-webkit-slider-thumb]:cursor-pointer"
            />
            <div className="flex justify-between text-xs text-dark-500 mt-1">
              <span>More matches</span>
              <span>Higher confidence</span>
            </div>
          </div>

          {/* LLM Provider */}
          {showLlmConfig && (
            <>
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  LLM Provider
                </label>
                <select
                  value={llmConfig.provider}
                  onChange={(e) => setLlmConfig({ ...llmConfig, provider: e.target.value })}
                  className="input-field"
                >
                  <option value="none">None (Local Only)</option>
                  <option value="openai">OpenAI</option>
                  <option value="azure_openai">Azure OpenAI</option>
                  <option value="ollama">Ollama (Local)</option>
                  <option value="groq">Groq</option>
                </select>
              </div>

              {llmConfig.provider !== 'none' && llmConfig.provider !== 'ollama' && (
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    API Key
                  </label>
                  <input
                    type="password"
                    value={llmConfig.api_key}
                    onChange={(e) => setLlmConfig({ ...llmConfig, api_key: e.target.value })}
                    placeholder="Enter API key"
                    className="input-field"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  Model
                </label>
                <input
                  type="text"
                  value={llmConfig.model}
                  onChange={(e) => setLlmConfig({ ...llmConfig, model: e.target.value })}
                  placeholder="gpt-4o-mini"
                  className="input-field"
                />
              </div>
            </>
          )}
        </div>
      </motion.div>

      {/* Analyze Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-center"
      >
        <button
          onClick={handleAnalyze}
          disabled={analyzing}
          className="btn-primary flex items-center gap-3 text-lg px-8 py-4"
        >
          {analyzing ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Brain className="w-5 h-5" />
              Run Hybrid AI Analysis
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </motion.div>

      {/* Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="stat-card">
              <p className="text-dark-400 text-sm">Total Mappings</p>
              <p className="text-3xl font-bold gradient-text">{result.total_mappings}</p>
            </div>
            <div className="stat-card">
              <p className="text-dark-400 text-sm">High Confidence</p>
              <p className="text-3xl font-bold text-emerald-400">{result.statistics.high_confidence}</p>
            </div>
            <div className="stat-card">
              <p className="text-dark-400 text-sm">Medium Confidence</p>
              <p className="text-3xl font-bold text-amber-400">{result.statistics.medium_confidence}</p>
            </div>
            <div className="stat-card">
              <p className="text-dark-400 text-sm">Low Confidence</p>
              <p className="text-3xl font-bold text-red-400">{result.statistics.low_confidence}</p>
            </div>
          </div>

          {/* Model Scores */}
          <div className="glass-card p-6">
            <h3 className="font-semibold mb-4">Average Model Scores</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(result.statistics.average_scores).map(([model, score]) => (
                <div key={model} className="text-center">
                  <div className="w-full h-2 bg-dark-700 rounded-full overflow-hidden mb-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${score * 100}%` }}
                      transition={{ duration: 1, delay: 0.5 }}
                      className="h-full bg-gradient-to-r from-primary-500 to-secondary-500"
                    />
                  </div>
                  <p className="text-sm">
                    <span className="text-dark-400 capitalize">{model}</span>
                    <span className="text-white font-semibold ml-2">{(score * 100).toFixed(1)}%</span>
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* LLM Status */}
          <div className="flex items-center gap-2">
            {result.llm_enabled ? (
              <>
                <CheckCircle className="w-5 h-5 text-emerald-400" />
                <span className="text-emerald-400">LLM API enabled for contextual reasoning</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-5 h-5 text-amber-400" />
                <span className="text-amber-400">Running with local models only (no LLM API)</span>
              </>
            )}
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

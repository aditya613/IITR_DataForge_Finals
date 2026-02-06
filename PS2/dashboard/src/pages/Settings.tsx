import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Settings as SettingsIcon,
  Key,
  Cloud,
  Server,
  Cpu,
  Save,
  Check,
  RefreshCw,
  Trash2,
  Download,
  Upload,
  Moon,
  Sun,
  Palette,
  Shield,
  Database
} from 'lucide-react'
import { toast } from 'react-hot-toast'

interface LLMSettings {
  provider: 'openai' | 'azure' | 'ollama' | 'groq' | 'none'
  apiKey: string
  model: string
  endpoint?: string
}

interface AppSettings {
  llm: LLMSettings
  defaultThreshold: number
  autoSave: boolean
  showAdvanced: boolean
}

const defaultSettings: AppSettings = {
  llm: {
    provider: 'none',
    apiKey: '',
    model: ''
  },
  defaultThreshold: 0.75,
  autoSave: true,
  showAdvanced: false
}

const providers = [
  { id: 'none', name: 'None (Local Only)', icon: Cpu, description: 'Use only local models (BERT, TF-IDF, Domain)' },
  { id: 'openai', name: 'OpenAI', icon: Cloud, description: 'GPT-4, GPT-3.5-turbo' },
  { id: 'azure', name: 'Azure OpenAI', icon: Server, description: 'Azure-hosted OpenAI models' },
  { id: 'ollama', name: 'Ollama', icon: Database, description: 'Local LLM (llama2, mistral, etc.)' },
  { id: 'groq', name: 'Groq', icon: Cpu, description: 'Fast inference (llama-70b, mixtral)' },
]

const modelsByProvider: Record<string, string[]> = {
  none: [],
  openai: ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
  azure: ['gpt-4', 'gpt-35-turbo'],
  ollama: ['llama2', 'mistral', 'codellama', 'mixtral'],
  groq: ['llama-3.1-70b-versatile', 'mixtral-8x7b-32768', 'llama-3.1-8b-instant'],
}

export default function Settings() {
  const [settings, setSettings] = useState<AppSettings>(defaultSettings)
  const [isSaving, setIsSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('appSettings')
    if (stored) {
      setSettings(JSON.parse(stored))
    }
  }, [])

  const handleSave = async () => {
    setIsSaving(true)
    await new Promise(resolve => setTimeout(resolve, 500))
    localStorage.setItem('appSettings', JSON.stringify(settings))
    setIsSaving(false)
    setHasChanges(false)
    toast.success('Settings saved successfully!')
  }

  const handleReset = () => {
    setSettings(defaultSettings)
    setHasChanges(true)
    toast.success('Settings reset to defaults')
  }

  const handleExport = () => {
    const data = {
      settings,
      exportedAt: new Date().toISOString()
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'dataforge-settings.json'
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Settings exported!')
  }

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string)
          if (data.settings) {
            setSettings(data.settings)
            setHasChanges(true)
            toast.success('Settings imported!')
          }
        } catch (err) {
          toast.error('Invalid settings file')
        }
      }
      reader.readAsText(file)
    }
  }

  const updateSettings = (updates: Partial<AppSettings>) => {
    setSettings(prev => ({ ...prev, ...updates }))
    setHasChanges(true)
  }

  const updateLLM = (updates: Partial<LLMSettings>) => {
    setSettings(prev => ({
      ...prev,
      llm: { ...prev.llm, ...updates }
    }))
    setHasChanges(true)
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
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-dark-400 mt-2">
            Configure LLM providers and application preferences
          </p>
        </div>
        <div className="flex items-center gap-3">
          {hasChanges && (
            <motion.span
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-amber-400 text-sm"
            >
              Unsaved changes
            </motion.span>
          )}
          <button
            onClick={handleSave}
            disabled={isSaving || !hasChanges}
            className="btn-primary flex items-center gap-2"
          >
            {isSaving ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            Save Settings
          </button>
        </div>
      </div>

      {/* LLM Provider Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-xl bg-purple-500/20">
            <Cloud className="w-5 h-5 text-purple-400" />
          </div>
          <h2 className="text-xl font-semibold">LLM Provider</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {providers.map((provider) => (
            <motion.button
              key={provider.id}
              onClick={() => updateLLM({ 
                provider: provider.id as any,
                model: modelsByProvider[provider.id][0] || ''
              })}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`p-4 rounded-xl text-left transition-all duration-300
                ${settings.llm.provider === provider.id
                  ? 'bg-gradient-to-br from-primary-500/20 to-secondary-500/20 border-2 border-primary-500'
                  : 'bg-dark-800 border border-dark-700 hover:border-dark-600'
                }`}
            >
              <div className="flex items-start justify-between">
                <provider.icon className={`w-6 h-6 ${
                  settings.llm.provider === provider.id ? 'text-primary-400' : 'text-dark-400'
                }`} />
                {settings.llm.provider === provider.id && (
                  <Check className="w-5 h-5 text-primary-400" />
                )}
              </div>
              <h3 className="font-semibold mt-3">{provider.name}</h3>
              <p className="text-sm text-dark-400 mt-1">{provider.description}</p>
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* LLM Configuration */}
      {settings.llm.provider !== 'none' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-blue-500/20">
              <Key className="w-5 h-5 text-blue-400" />
            </div>
            <h2 className="text-xl font-semibold">API Configuration</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {settings.llm.provider !== 'ollama' && (
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  API Key
                </label>
                <div className="relative">
                  <input
                    type="password"
                    value={settings.llm.apiKey}
                    onChange={(e) => updateLLM({ apiKey: e.target.value })}
                    placeholder={`Enter your ${settings.llm.provider} API key`}
                    className="w-full px-4 py-3 rounded-xl bg-dark-800 border border-dark-600 
                             focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                             text-white placeholder-dark-500 transition-all"
                  />
                  <Shield className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
                </div>
                <p className="text-xs text-dark-500 mt-2">
                  Keys are stored locally and never sent to our servers
                </p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Model
              </label>
              <select
                value={settings.llm.model}
                onChange={(e) => updateLLM({ model: e.target.value })}
                className="w-full px-4 py-3 rounded-xl bg-dark-800 border border-dark-600 
                         focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                         text-white transition-all"
              >
                {modelsByProvider[settings.llm.provider].map((model) => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
            </div>

            {(settings.llm.provider === 'azure' || settings.llm.provider === 'ollama') && (
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  Endpoint URL
                </label>
                <input
                  type="url"
                  value={settings.llm.endpoint || ''}
                  onChange={(e) => updateLLM({ endpoint: e.target.value })}
                  placeholder={settings.llm.provider === 'ollama' 
                    ? 'http://localhost:11434'
                    : 'https://your-resource.openai.azure.com/'
                  }
                  className="w-full px-4 py-3 rounded-xl bg-dark-800 border border-dark-600 
                           focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                           text-white placeholder-dark-500 transition-all"
                />
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* General Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-6"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-xl bg-emerald-500/20">
            <SettingsIcon className="w-5 h-5 text-emerald-400" />
          </div>
          <h2 className="text-xl font-semibold">General Settings</h2>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Default Confidence Threshold
            </label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0.5"
                max="0.95"
                step="0.05"
                value={settings.defaultThreshold}
                onChange={(e) => updateSettings({ defaultThreshold: parseFloat(e.target.value) })}
                className="flex-1 accent-primary-500"
              />
              <span className="text-lg font-semibold w-16 text-center text-primary-400">
                {(settings.defaultThreshold * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between py-3 border-b border-dark-700">
            <div>
              <h3 className="font-medium">Auto-save Results</h3>
              <p className="text-sm text-dark-400">Automatically save analysis results to local storage</p>
            </div>
            <button
              onClick={() => updateSettings({ autoSave: !settings.autoSave })}
              className={`relative w-12 h-6 rounded-full transition-colors ${
                settings.autoSave ? 'bg-primary-500' : 'bg-dark-600'
              }`}
            >
              <motion.div
                animate={{ x: settings.autoSave ? 24 : 4 }}
                className="absolute top-1 w-4 h-4 bg-white rounded-full shadow"
              />
            </button>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <h3 className="font-medium">Show Advanced Options</h3>
              <p className="text-sm text-dark-400">Display advanced configuration options in analysis</p>
            </div>
            <button
              onClick={() => updateSettings({ showAdvanced: !settings.showAdvanced })}
              className={`relative w-12 h-6 rounded-full transition-colors ${
                settings.showAdvanced ? 'bg-primary-500' : 'bg-dark-600'
              }`}
            >
              <motion.div
                animate={{ x: settings.showAdvanced ? 24 : 4 }}
                className="absolute top-1 w-4 h-4 bg-white rounded-full shadow"
              />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Data Management */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card p-6"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-xl bg-amber-500/20">
            <Database className="w-5 h-5 text-amber-400" />
          </div>
          <h2 className="text-xl font-semibold">Data Management</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={handleExport}
            className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl
                     bg-dark-800 border border-dark-600 hover:border-primary-500/50
                     transition-all duration-300"
          >
            <Download className="w-5 h-5 text-blue-400" />
            <span>Export Settings</span>
          </button>

          <label className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl
                          bg-dark-800 border border-dark-600 hover:border-primary-500/50
                          transition-all duration-300 cursor-pointer">
            <Upload className="w-5 h-5 text-emerald-400" />
            <span>Import Settings</span>
            <input
              type="file"
              accept=".json"
              onChange={handleImport}
              className="hidden"
            />
          </label>

          <button
            onClick={handleReset}
            className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl
                     bg-dark-800 border border-dark-600 hover:border-red-500/50
                     transition-all duration-300 text-red-400"
          >
            <Trash2 className="w-5 h-5" />
            <span>Reset to Defaults</span>
          </button>
        </div>

        <div className="mt-6 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
          <p className="text-sm text-amber-200">
            <strong>Note:</strong> Clearing browser data will remove all saved settings and analysis results.
            Consider exporting your settings before clearing browser data.
          </p>
        </div>
      </motion.div>

      {/* Model Weights Info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass-card p-6"
      >
        <h2 className="text-xl font-semibold mb-4">Model Weights</h2>
        <p className="text-dark-400 mb-6">
          The hybrid AI engine uses ensemble scoring with the following default weights:
        </p>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { name: 'BERT', weight: 35, color: 'blue', desc: 'Semantic embeddings' },
            { name: 'LLM', weight: 30, color: 'purple', desc: 'Contextual understanding' },
            { name: 'TF-IDF', weight: 15, color: 'orange', desc: 'Term frequency' },
            { name: 'Domain', weight: 20, color: 'emerald', desc: 'Abbreviation mapping' },
          ].map((model) => (
            <div
              key={model.name}
              className={`p-4 rounded-xl bg-${model.color}-500/10 border border-${model.color}-500/30`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`font-semibold text-${model.color}-400`}>{model.name}</span>
                <span className="text-lg font-bold">{model.weight}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-dark-700">
                <div
                  className={`h-full rounded-full bg-${model.color}-500`}
                  style={{ width: `${model.weight}%` }}
                />
              </div>
              <p className="text-xs text-dark-500 mt-2">{model.desc}</p>
            </div>
          ))}
        </div>

        <p className="text-sm text-dark-500 mt-4">
          When LLM is disabled, weights are redistributed: BERT (50%), TF-IDF (21%), Domain (29%)
        </p>
      </motion.div>
    </motion.div>
  )
}

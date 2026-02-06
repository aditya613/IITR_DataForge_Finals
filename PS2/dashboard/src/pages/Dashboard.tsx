import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  Database,
  GitBranch,
  ShieldCheck,
  Rocket,
  ArrowRight,
  Sparkles,
  Cpu,
  Brain,
  Layers,
  Zap
} from 'lucide-react'
import { checkHealth, checkSampleData, createSampleData } from '../api'
import toast from 'react-hot-toast'

interface StatCardProps {
  icon: any
  title: string
  value: string | number
  subtitle: string
  color: string
  delay?: number
}

function StatCard({ icon: Icon, title, value, subtitle, color, delay = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay * 0.1, duration: 0.5 }}
      className="stat-card group"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-dark-400 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold mt-2 gradient-text">{value}</p>
          <p className="text-dark-500 text-sm mt-1">{subtitle}</p>
        </div>
        <div className={`p-3 rounded-xl ${color} group-hover:scale-110 transition-transform`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </motion.div>
  )
}

function FeatureCard({ icon: Icon, title, description, onClick }: any) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="glass-card p-6 text-left w-full card-hover group"
    >
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-xl bg-gradient-to-br from-primary-500/20 to-secondary-500/20
                      group-hover:from-primary-500/30 group-hover:to-secondary-500/30 transition-all">
          <Icon className="w-6 h-6 text-primary-400" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-lg">{title}</h3>
          <p className="text-dark-400 text-sm mt-1">{description}</p>
        </div>
        <ArrowRight className="w-5 h-5 text-dark-500 group-hover:text-primary-400 
                              group-hover:translate-x-1 transition-all" />
      </div>
    </motion.button>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [sampleDataReady, setSampleDataReady] = useState(false)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    checkApiStatus()
    checkSampleDataStatus()
  }, [])

  const checkApiStatus = async () => {
    try {
      await checkHealth()
      setApiStatus('online')
    } catch {
      setApiStatus('offline')
    }
  }

  const checkSampleDataStatus = async () => {
    try {
      const result = await checkSampleData()
      setSampleDataReady(result.ready)
    } catch {
      setSampleDataReady(false)
    }
  }

  const handleCreateSampleData = async () => {
    setCreating(true)
    try {
      await createSampleData()
      setSampleDataReady(true)
      toast.success('Sample databases created successfully!')
    } catch (error) {
      toast.error('Failed to create sample data')
    }
    setCreating(false)
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 mb-4">
          <Sparkles className="w-4 h-4 text-primary-400" />
          <span className="text-sm font-medium text-primary-400">Hybrid AI Engine v2.0</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold">
          <span className="gradient-text">AI-Powered</span> Data Migration
        </h1>
        <p className="text-dark-400 mt-4 max-w-2xl mx-auto text-lg">
          Intelligently map database schemas using BERT embeddings, LLM reasoning, 
          and domain-aware matching for seamless data migration.
        </p>
      </motion.div>

      {/* API Status */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex justify-center"
      >
        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full 
          ${apiStatus === 'online' ? 'bg-emerald-500/10 border-emerald-500/30' : 
            apiStatus === 'offline' ? 'bg-red-500/10 border-red-500/30' : 
            'bg-amber-500/10 border-amber-500/30'} border`}>
          <div className={`w-2 h-2 rounded-full animate-pulse
            ${apiStatus === 'online' ? 'bg-emerald-400' : 
              apiStatus === 'offline' ? 'bg-red-400' : 'bg-amber-400'}`} />
          <span className={`text-sm font-medium
            ${apiStatus === 'online' ? 'text-emerald-400' : 
              apiStatus === 'offline' ? 'text-red-400' : 'text-amber-400'}`}>
            API {apiStatus === 'online' ? 'Online' : apiStatus === 'offline' ? 'Offline' : 'Checking...'}
          </span>
        </div>
      </motion.div>

      {/* Model Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          icon={Brain}
          title="BERT Model"
          value="MiniLM"
          subtitle="Semantic Embeddings"
          color="bg-gradient-to-br from-blue-500 to-cyan-500"
          delay={0}
        />
        <StatCard
          icon={Sparkles}
          title="LLM API"
          value="GPT-4"
          subtitle="Contextual Reasoning"
          color="bg-gradient-to-br from-purple-500 to-pink-500"
          delay={1}
        />
        <StatCard
          icon={Layers}
          title="TF-IDF"
          value="N-gram"
          subtitle="Statistical Analysis"
          color="bg-gradient-to-br from-orange-500 to-amber-500"
          delay={2}
        />
        <StatCard
          icon={Cpu}
          title="Domain"
          value="50+"
          subtitle="Abbreviation Mappings"
          color="bg-gradient-to-br from-emerald-500 to-teal-500"
          delay={3}
        />
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card p-8"
      >
        <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-400" />
          Quick Actions
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FeatureCard
            icon={Database}
            title="Start New Analysis"
            description="Upload source and target databases to begin AI-powered schema matching"
            onClick={() => navigate('/analysis')}
          />
          <FeatureCard
            icon={GitBranch}
            title="View Mappings"
            description="Explore detected column mappings with confidence scores and explanations"
            onClick={() => navigate('/mappings')}
          />
          <FeatureCard
            icon={ShieldCheck}
            title="Run Validation"
            description="Perform pre-migration data quality checks and integrity validation"
            onClick={() => navigate('/validation')}
          />
          <FeatureCard
            icon={Rocket}
            title="Execute Migration"
            description="Safely migrate data with batch processing and rollback support"
            onClick={() => navigate('/migration')}
          />
        </div>
      </motion.div>

      {/* Sample Data */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-card p-8"
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Sample Databases</h2>
            <p className="text-dark-400 mt-1">
              {sampleDataReady 
                ? 'Sample CRM databases are ready for testing'
                : 'Create sample databases to test the migration platform'}
            </p>
          </div>
          
          {sampleDataReady ? (
            <div className="badge-success">
              <ShieldCheck className="w-4 h-4 mr-2" />
              Ready
            </div>
          ) : (
            <button
              onClick={handleCreateSampleData}
              disabled={creating}
              className="btn-primary flex items-center gap-2"
            >
              {creating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Database className="w-4 h-4" />
                  Create Sample Data
                </>
              )}
            </button>
          )}
        </div>
      </motion.div>

      {/* Architecture Diagram */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="glass-card p-8"
      >
        <h2 className="text-xl font-semibold mb-6">Hybrid AI Architecture</h2>
        
        <div className="flex flex-wrap items-center justify-center gap-4 text-sm">
          <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-blue-500/10 border border-blue-500/30">
            <Brain className="w-5 h-5 text-blue-400" />
            <span>BERT (35%)</span>
          </div>
          <div className="text-dark-500">+</div>
          <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-purple-500/10 border border-purple-500/30">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <span>LLM (30%)</span>
          </div>
          <div className="text-dark-500">+</div>
          <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-orange-500/10 border border-orange-500/30">
            <Layers className="w-5 h-5 text-orange-400" />
            <span>TF-IDF (15%)</span>
          </div>
          <div className="text-dark-500">+</div>
          <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
            <Cpu className="w-5 h-5 text-emerald-400" />
            <span>Domain (20%)</span>
          </div>
          <div className="text-dark-500">=</div>
          <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-primary-500/20 to-secondary-500/20 border border-primary-500/30">
            <Zap className="w-5 h-5 text-primary-400" />
            <span className="font-semibold gradient-text">Ensemble Score</span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart3,
  PieChart,
  TrendingUp,
  ArrowRight,
  Brain,
  Sparkles,
  Layers,
  Cpu
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RePieChart,
  Pie,
  Cell,
  Sankey,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  AreaChart,
  Area
} from 'recharts'
import { ColumnMapping } from '../api'

const COLORS = {
  high: '#10b981',
  medium: '#f59e0b',
  low: '#ef4444',
  bert: '#3b82f6',
  llm: '#a855f7',
  tfidf: '#f97316',
  domain: '#10b981'
}

export default function Visualizations() {
  const [result, setResult] = useState<any>(null)
  const [activeChart, setActiveChart] = useState<'confidence' | 'models' | 'flow' | 'radar'>('confidence')

  useEffect(() => {
    const stored = localStorage.getItem('analysisResult')
    if (stored) {
      setResult(JSON.parse(stored))
    }
  }, [])

  if (!result) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center justify-center h-96"
      >
        <BarChart3 className="w-16 h-16 text-dark-600 mb-4" />
        <h2 className="text-xl font-semibold text-dark-400">No Data Available</h2>
        <p className="text-dark-500 mt-2">Run an analysis first to see visualizations</p>
      </motion.div>
    )
  }

  const mappings: ColumnMapping[] = result.all_mappings || []

  // Confidence Distribution Data
  const confidenceData = [
    { name: 'High', value: result.statistics.high_confidence, color: COLORS.high },
    { name: 'Medium', value: result.statistics.medium_confidence, color: COLORS.medium },
    { name: 'Low', value: result.statistics.low_confidence, color: COLORS.low },
  ]

  // Model Scores Data
  const modelScoresData = [
    { name: 'BERT', score: result.statistics.average_scores.bert * 100, fill: COLORS.bert },
    { name: 'LLM', score: result.statistics.average_scores.llm * 100, fill: COLORS.llm },
    { name: 'TF-IDF', score: result.statistics.average_scores.tfidf * 100, fill: COLORS.tfidf },
    { name: 'Domain', score: result.statistics.average_scores.domain * 100, fill: COLORS.domain },
  ]

  // Score Distribution (histogram-like)
  const scoreRanges = [
    { range: '0-20%', count: 0 },
    { range: '20-40%', count: 0 },
    { range: '40-60%', count: 0 },
    { range: '60-80%', count: 0 },
    { range: '80-100%', count: 0 },
  ]

  mappings.forEach((m: ColumnMapping) => {
    const score = m.ensemble_score * 100
    if (score < 20) scoreRanges[0].count++
    else if (score < 40) scoreRanges[1].count++
    else if (score < 60) scoreRanges[2].count++
    else if (score < 80) scoreRanges[3].count++
    else scoreRanges[4].count++
  })

  // Radar data for model comparison
  const radarData = mappings.slice(0, 5).map((m: ColumnMapping) => ({
    name: `${m.source_column.slice(0, 8)}→${m.target_column.slice(0, 8)}`,
    bert: m.bert_score * 100,
    llm: m.llm_score * 100,
    tfidf: m.tfidf_score * 100,
    domain: m.domain_score * 100,
  }))

  const chartButtons = [
    { id: 'confidence', label: 'Confidence', icon: PieChart },
    { id: 'models', label: 'Model Scores', icon: BarChart3 },
    { id: 'flow', label: 'Score Distribution', icon: TrendingUp },
    { id: 'radar', label: 'Model Comparison', icon: Brain },
  ]

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Visualizations</h1>
        <p className="text-dark-400 mt-2">
          Interactive charts showing migration analysis results
        </p>
      </div>

      {/* Chart Selector */}
      <div className="flex flex-wrap gap-3">
        {chartButtons.map((btn) => (
          <button
            key={btn.id}
            onClick={() => setActiveChart(btn.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-300
              ${activeChart === btn.id
                ? 'bg-gradient-to-r from-primary-500/20 to-secondary-500/20 border border-primary-500/50 text-white'
                : 'bg-dark-800 border border-dark-700 text-dark-400 hover:text-white hover:border-dark-600'
              }`}
          >
            <btn.icon className="w-4 h-4" />
            {btn.label}
          </button>
        ))}
      </div>

      {/* Charts */}
      <motion.div
        key={activeChart}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6"
      >
        {activeChart === 'confidence' && (
          <div>
            <h3 className="text-xl font-semibold mb-6">Confidence Distribution</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <RePieChart>
                  <Pie
                    data={confidenceData}
                    cx="50%"
                    cy="50%"
                    innerRadius={80}
                    outerRadius={120}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                  >
                    {confidenceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '8px'
                    }}
                  />
                </RePieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-6 mt-4">
              {confidenceData.map((item) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-sm text-dark-300">{item.name}: {item.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeChart === 'models' && (
          <div>
            <h3 className="text-xl font-semibold mb-6">Average Model Scores</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={modelScoresData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis type="number" domain={[0, 100]} stroke="#64748b" />
                  <YAxis type="category" dataKey="name" stroke="#64748b" width={80} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '8px'
                    }}
                    formatter={(value: number) => `${value.toFixed(1)}%`}
                  />
                  <Bar dataKey="score" radius={[0, 8, 8, 0]}>
                    {modelScoresData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-4 gap-4 mt-6">
              {[
                { name: 'BERT', icon: Brain, color: 'blue', weight: '35%' },
                { name: 'LLM', icon: Sparkles, color: 'purple', weight: '30%' },
                { name: 'TF-IDF', icon: Layers, color: 'orange', weight: '15%' },
                { name: 'Domain', icon: Cpu, color: 'emerald', weight: '20%' },
              ].map((model) => (
                <div key={model.name} className={`text-center p-3 rounded-xl bg-${model.color}-500/10 border border-${model.color}-500/30`}>
                  <model.icon className={`w-6 h-6 text-${model.color}-400 mx-auto mb-2`} />
                  <p className="font-semibold">{model.name}</p>
                  <p className="text-xs text-dark-400">Weight: {model.weight}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeChart === 'flow' && (
          <div>
            <h3 className="text-xl font-semibold mb-6">Score Distribution</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={scoreRanges}>
                  <defs>
                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#764ba2" stopOpacity={0.2}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="range" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '8px'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke="#667eea"
                    fillOpacity={1}
                    fill="url(#colorCount)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeChart === 'radar' && (
          <div>
            <h3 className="text-xl font-semibold mb-6">Model Score Comparison (Top 5 Mappings)</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#334155" />
                  <PolarAngleAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 10 }} />
                  <Radar name="BERT" dataKey="bert" stroke={COLORS.bert} fill={COLORS.bert} fillOpacity={0.3} />
                  <Radar name="LLM" dataKey="llm" stroke={COLORS.llm} fill={COLORS.llm} fillOpacity={0.3} />
                  <Radar name="TF-IDF" dataKey="tfidf" stroke={COLORS.tfidf} fill={COLORS.tfidf} fillOpacity={0.3} />
                  <Radar name="Domain" dataKey="domain" stroke={COLORS.domain} fill={COLORS.domain} fillOpacity={0.3} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '8px'
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-6 mt-4">
              {[
                { name: 'BERT', color: COLORS.bert },
                { name: 'LLM', color: COLORS.llm },
                { name: 'TF-IDF', color: COLORS.tfidf },
                { name: 'Domain', color: COLORS.domain },
              ].map((item) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-sm text-dark-300">{item.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.div>

      {/* Mapping Flow */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6"
      >
        <h3 className="text-xl font-semibold mb-6">Column Mapping Flow</h3>
        <div className="space-y-2">
          {mappings.slice(0, 10).map((m: ColumnMapping, idx: number) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="flex items-center gap-4 p-3 rounded-xl bg-dark-800/50 hover:bg-dark-700/50 transition-colors"
            >
              <div className="flex-1 flex items-center gap-3">
                <code className="text-blue-400 font-mono text-sm px-2 py-1 bg-blue-500/10 rounded">
                  {m.source_column}
                </code>
                <ArrowRight className="w-4 h-4 text-dark-500" />
                <code className="text-purple-400 font-mono text-sm px-2 py-1 bg-purple-500/10 rounded">
                  {m.target_column}
                </code>
              </div>
              
              <div className="flex items-center gap-2">
                <div className={`w-24 h-2 rounded-full overflow-hidden bg-dark-700`}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${m.ensemble_score * 100}%` }}
                    transition={{ duration: 0.5, delay: idx * 0.1 }}
                    className={`h-full ${
                      m.confidence_level === 'high' ? 'bg-emerald-500' :
                      m.confidence_level === 'medium' ? 'bg-amber-500' : 'bg-red-500'
                    }`}
                  />
                </div>
                <span className={`text-sm font-medium w-12 text-right ${
                  m.confidence_level === 'high' ? 'text-emerald-400' :
                  m.confidence_level === 'medium' ? 'text-amber-400' : 'text-red-400'
                }`}>
                  {(m.ensemble_score * 100).toFixed(0)}%
                </span>
              </div>
            </motion.div>
          ))}
        </div>
        {mappings.length > 10 && (
          <p className="text-center text-dark-500 mt-4">
            Showing 10 of {mappings.length} mappings
          </p>
        )}
      </motion.div>
    </motion.div>
  )
}

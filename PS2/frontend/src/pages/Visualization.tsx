import { useState, useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { 
  BarChart3, 
  GitBranch, 
  AlertCircle,
  ArrowRight,
  Table,
  Link2,
  Unlink,
  CheckCircle,
  XCircle
} from 'lucide-react'
import {
  Sankey,
  Tooltip,
  ResponsiveContainer,
  Rectangle,
  Layer
} from 'recharts'
import { getVisualizationData, VisualizationData } from '../api'

// Custom Sankey Node
const CustomNode = ({ x, y, width, height, index, payload }: any) => {
  const isSource = payload.type === 'source' || payload.type === 'source_unmapped'
  const isUnmapped = payload.type === 'source_unmapped' || payload.type === 'target_unmapped'
  
  let fill = isSource ? '#3b82f6' : '#a855f7'
  if (isUnmapped) fill = '#6b7280'
  
  return (
    <Rectangle
      x={x}
      y={y}
      width={width}
      height={height}
      fill={fill}
      fillOpacity={isUnmapped ? 0.5 : 0.9}
      rx={4}
      ry={4}
    />
  )
}

// Custom Sankey Link
const CustomLink = ({ sourceX, targetX, sourceY, targetY, sourceControlX, targetControlX, linkWidth, index, payload }: any) => {
  const colors: Record<string, string> = {
    high: '#10b981',
    medium: '#f59e0b',
    low: '#ef4444'
  }
  const color = colors[payload.confidence] || '#6b7280'
  
  return (
    <path
      d={`M${sourceX},${sourceY}
          C${sourceControlX},${sourceY} ${targetControlX},${targetY} ${targetX},${targetY}`}
      fill="none"
      stroke={color}
      strokeWidth={Math.max(linkWidth, 2)}
      strokeOpacity={0.6}
    />
  )
}

export default function Visualization() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'sankey' | 'table' | 'flow'>('table')

  useEffect(() => {
    const id = localStorage.getItem('sessionId')
    if (id) setSessionId(id)
  }, [])

  const { data, isLoading, error } = useQuery({
    queryKey: ['visualization', sessionId],
    queryFn: () => getVisualizationData(sessionId!),
    enabled: !!sessionId
  })

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

  if (error || !data) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <AlertCircle className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-xl font-semibold text-dark-400">Visualization Not Available</h2>
        <p className="text-dark-500 mt-2">Run analysis first to generate visualizations</p>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Table Mapping Visualization</h1>
        <p className="text-dark-400 mt-1">
          Visual representation of source and target table relationships
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div className="glass-card p-4 text-center">
          <Link2 className="w-6 h-6 text-primary-400 mx-auto mb-1" />
          <p className="text-2xl font-bold">{data.summary.total_mappings}</p>
          <p className="text-xs text-dark-400">Mappings</p>
        </div>
        <div className="glass-card p-4 text-center">
          <CheckCircle className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
          <p className="text-2xl font-bold text-emerald-400">{data.summary.high_confidence}</p>
          <p className="text-xs text-dark-400">High Conf.</p>
        </div>
        <div className="glass-card p-4 text-center">
          <CheckCircle className="w-6 h-6 text-amber-400 mx-auto mb-1" />
          <p className="text-2xl font-bold text-amber-400">{data.summary.medium_confidence}</p>
          <p className="text-xs text-dark-400">Medium Conf.</p>
        </div>
        <div className="glass-card p-4 text-center">
          <CheckCircle className="w-6 h-6 text-red-400 mx-auto mb-1" />
          <p className="text-2xl font-bold text-red-400">{data.summary.low_confidence}</p>
          <p className="text-xs text-dark-400">Low Conf.</p>
        </div>
        <div className="glass-card p-4 text-center">
          <Unlink className="w-6 h-6 text-dark-500 mx-auto mb-1" />
          <p className="text-2xl font-bold text-dark-400">{data.summary.unmapped_source}</p>
          <p className="text-xs text-dark-400">Unmapped Src</p>
        </div>
        <div className="glass-card p-4 text-center">
          <Unlink className="w-6 h-6 text-dark-500 mx-auto mb-1" />
          <p className="text-2xl font-bold text-dark-400">{data.summary.unmapped_target}</p>
          <p className="text-xs text-dark-400">Unmapped Tgt</p>
        </div>
      </div>

      {/* View Mode Tabs */}
      <div className="flex gap-2">
        {[
          { id: 'table', label: 'Table View', icon: Table },
          { id: 'flow', label: 'Flow Diagram', icon: GitBranch },
        ].map((view) => (
          <button
            key={view.id}
            onClick={() => setViewMode(view.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all
              ${viewMode === view.id ? 'tab-active' : 'tab-inactive'}`}
          >
            <view.icon className="w-4 h-4" />
            {view.label}
          </button>
        ))}
      </div>

      {/* Table View */}
      {viewMode === 'table' && (
        <div className="space-y-6">
          {data.table_mappings.map((tableMap, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="glass-card p-6"
            >
              <div className="flex items-center gap-4 mb-6">
                <div className="flex-1 text-center p-3 rounded-lg bg-blue-500/20 border border-blue-500/30">
                  <p className="text-sm text-dark-400">Source Table</p>
                  <h3 className="text-xl font-bold text-blue-400">{tableMap.source_table}</h3>
                </div>
                <ArrowRight className="w-8 h-8 text-dark-500 flex-shrink-0" />
                <div className="flex-1 text-center p-3 rounded-lg bg-purple-500/20 border border-purple-500/30">
                  <p className="text-sm text-dark-400">Target Table</p>
                  <h3 className="text-xl font-bold text-purple-400">{tableMap.target_table}</h3>
                </div>
              </div>

              <div className="grid gap-2">
                {tableMap.columns.map((col, colIdx) => (
                  <div 
                    key={colIdx}
                    className="flex items-center gap-4 p-3 rounded-lg bg-dark-800/50 hover:bg-dark-800 transition-colors"
                  >
                    <code className="flex-1 text-blue-400 font-mono text-sm">{col.source}</code>
                    
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 rounded-full bg-dark-700 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${col.score * 100}%` }}
                          transition={{ duration: 0.5, delay: colIdx * 0.05 }}
                          className={`h-full ${
                            col.confidence === 'high' ? 'bg-emerald-500' :
                            col.confidence === 'medium' ? 'bg-amber-500' : 'bg-red-500'
                          }`}
                        />
                      </div>
                      <span className="text-xs text-dark-400 w-12 text-right">
                        {(col.score * 100).toFixed(0)}%
                      </span>
                    </div>
                    
                    <ArrowRight className="w-4 h-4 text-dark-500" />
                    
                    <code className="flex-1 text-purple-400 font-mono text-sm text-right">{col.target}</code>
                    
                    <span className={`badge-${col.confidence} text-xs`}>
                      {col.confidence}
                    </span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Flow Diagram */}
      {viewMode === 'flow' && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Column Mapping Flow</h3>
          <div className="space-y-2">
            {data.sankey.links.map((link, idx) => {
              const sourceNode = data.sankey.nodes[link.source]
              const targetNode = data.sankey.nodes[link.target]
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.03 }}
                  className="flex items-center gap-4 p-3 rounded-lg bg-dark-800/50 hover:bg-dark-800 transition-colors"
                >
                  {/* Source */}
                  <div className="flex-1 flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${
                      sourceNode.type === 'source_unmapped' ? 'bg-dark-500' : 'bg-blue-500'
                    }`} />
                    <code className="text-sm text-blue-400 font-mono truncate">{sourceNode.name}</code>
                  </div>

                  {/* Connection */}
                  <div className="flex items-center gap-2">
                    <div className={`w-16 h-1 rounded-full ${
                      link.confidence === 'high' ? 'bg-emerald-500' :
                      link.confidence === 'medium' ? 'bg-amber-500' : 'bg-red-500'
                    }`} />
                    <ArrowRight className={`w-4 h-4 ${
                      link.confidence === 'high' ? 'text-emerald-500' :
                      link.confidence === 'medium' ? 'text-amber-500' : 'text-red-500'
                    }`} />
                  </div>

                  {/* Target */}
                  <div className="flex-1 flex items-center gap-2 justify-end">
                    <code className="text-sm text-purple-400 font-mono truncate text-right">{targetNode.name}</code>
                    <div className={`w-3 h-3 rounded-full ${
                      targetNode.type === 'target_unmapped' ? 'bg-dark-500' : 'bg-purple-500'
                    }`} />
                  </div>

                  {/* Score */}
                  <span className={`w-16 text-right font-bold ${
                    link.confidence === 'high' ? 'text-emerald-400' :
                    link.confidence === 'medium' ? 'text-amber-400' : 'text-red-400'
                  }`}>
                    {(link.value * 100).toFixed(0)}%
                  </span>
                </motion.div>
              )
            })}
          </div>

          {/* Unmapped Nodes */}
          {data.sankey.nodes.filter(n => n.type.includes('unmapped')).length > 0 && (
            <div className="mt-6 pt-6 border-t border-dark-700">
              <h4 className="text-sm font-semibold text-dark-400 mb-3">Unmapped Fields</h4>
              <div className="grid md:grid-cols-2 gap-4">
                {data.sankey.nodes.filter(n => n.type === 'source_unmapped').length > 0 && (
                  <div>
                    <p className="text-xs text-dark-500 mb-2">Source (not mapped)</p>
                    <div className="space-y-1">
                      {data.sankey.nodes.filter(n => n.type === 'source_unmapped').map((node, idx) => (
                        <div key={idx} className="flex items-center gap-2 p-2 rounded bg-dark-800/50">
                          <Unlink className="w-4 h-4 text-dark-500" />
                          <code className="text-xs text-dark-400">{node.name}</code>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {data.sankey.nodes.filter(n => n.type === 'target_unmapped').length > 0 && (
                  <div>
                    <p className="text-xs text-dark-500 mb-2">Target (no source)</p>
                    <div className="space-y-1">
                      {data.sankey.nodes.filter(n => n.type === 'target_unmapped').map((node, idx) => (
                        <div key={idx} className="flex items-center gap-2 p-2 rounded bg-dark-800/50">
                          <Unlink className="w-4 h-4 text-dark-500" />
                          <code className="text-xs text-dark-400">{node.name}</code>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="glass-card p-4">
        <h4 className="text-sm font-semibold text-dark-300 mb-3">Legend</h4>
        <div className="flex flex-wrap gap-6">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-blue-500" />
            <span className="text-sm text-dark-400">Source Column</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-purple-500" />
            <span className="text-sm text-dark-400">Target Column</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-2 rounded bg-emerald-500" />
            <span className="text-sm text-dark-400">High Confidence</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-2 rounded bg-amber-500" />
            <span className="text-sm text-dark-400">Medium Confidence</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-2 rounded bg-red-500" />
            <span className="text-sm text-dark-400">Low Confidence</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-dark-500" />
            <span className="text-sm text-dark-400">Unmapped</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

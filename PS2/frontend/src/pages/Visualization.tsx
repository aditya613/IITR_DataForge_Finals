import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
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
  ZoomIn,
  ZoomOut,
  Maximize2,
  Info
} from 'lucide-react'
import { getVisualizationData, VisualizationData } from '../api'

/* ─────────────────────────────────────────────────────
   Interactive SVG Schema Graph (node-based)
   ───────────────────────────────────────────────────── */

interface GraphNode {
  id: string
  label: string
  table: string
  type: 'source' | 'target' | 'source_unmapped' | 'target_unmapped'
  x: number
  y: number
  reason?: string
}

interface GraphEdge {
  sourceId: string
  targetId: string
  confidence: string
  score: number
  explanation: string
  mappingType: string
}

function InteractiveSchemaGraph({ data }: { data: VisualizationData }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [tooltip, setTooltip] = useState<{
    x: number; y: number; text: string; subtext: string; confidence: string
  } | null>(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isPanning, setIsPanning] = useState(false)
  const [panStart, setPanStart] = useState({ x: 0, y: 0 })
  const [hoveredEdge, setHoveredEdge] = useState<number | null>(null)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  // Build graph model from API data
  const { nodes, edges } = useMemo(() => {
    const nodeMap = new Map<string, GraphNode>()
    const edgeList: GraphEdge[] = []

    const sourceNodes: typeof data.sankey.nodes = []
    const targetNodes: typeof data.sankey.nodes = []

    data.sankey.nodes.forEach((n) => {
      if (n.type === 'source' || n.type === 'source_unmapped') sourceNodes.push(n)
      else targetNodes.push(n)
    })

    const ROW_H = 52
    const PAD_TOP = 40
    const LEFT_X = 60
    const RIGHT_X = 600

    sourceNodes.forEach((n, i) => {
      nodeMap.set(n.id, {
        id: n.id, label: n.name, table: n.table,
        type: n.type as GraphNode['type'],
        x: LEFT_X, y: PAD_TOP + i * ROW_H, reason: n.reason,
      })
    })
    targetNodes.forEach((n, i) => {
      nodeMap.set(n.id, {
        id: n.id, label: n.name, table: n.table,
        type: n.type as GraphNode['type'],
        x: RIGHT_X, y: PAD_TOP + i * ROW_H, reason: n.reason,
      })
    })

    data.sankey.links.forEach((link) => {
      const src = data.sankey.nodes[link.source]
      const tgt = data.sankey.nodes[link.target]
      if (src && tgt) {
        edgeList.push({
          sourceId: src.id, targetId: tgt.id,
          confidence: link.confidence, score: link.value,
          explanation: link.explanation, mappingType: link.mapping_type,
        })
      }
    })

    return { nodes: Array.from(nodeMap.values()), edges: edgeList }
  }, [data])

  const svgHeight = Math.max(
    nodes.filter(n => n.type === 'source' || n.type === 'source_unmapped').length * 52 + 80,
    nodes.filter(n => n.type === 'target' || n.type === 'target_unmapped').length * 52 + 80,
    400
  )

  const edgeColor = (c: string) =>
    c === 'high' ? '#10b981' : c === 'medium' ? '#f59e0b' : c === 'low' ? '#ef4444' : '#6b7280'

  // Pan handlers
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 0 && (e.target as SVGElement).tagName === 'svg') {
      setIsPanning(true)
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
    }
  }, [pan])
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isPanning) setPan({ x: e.clientX - panStart.x, y: e.clientY - panStart.y })
  }, [isPanning, panStart])
  const handleMouseUp = useCallback(() => setIsPanning(false), [])
  const resetView = () => { setZoom(1); setPan({ x: 0, y: 0 }) }

  // Edge hover tooltip
  const showEdgeTooltip = (e: React.MouseEvent, edge: GraphEdge, idx: number) => {
    const rect = containerRef.current?.getBoundingClientRect()
    if (!rect) return
    setHoveredEdge(idx)
    const srcLabel = edge.sourceId.includes('.') ? edge.sourceId.split('.').pop() : edge.sourceId
    const tgtLabel = edge.targetId.includes('.') ? edge.targetId.split('.').pop() : edge.targetId
    setTooltip({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top - 12,
      text: `Mapped '${srcLabel}' → '${tgtLabel}'`,
      subtext: edge.explanation || `${edge.mappingType} match · ${(edge.score * 100).toFixed(0)}%`,
      confidence: edge.confidence,
    })
  }
  const hideEdgeTooltip = () => { setHoveredEdge(null); setTooltip(null) }

  // Highlight helpers
  const connectedEdgeSet = useMemo(() => {
    if (!selectedNode) return new Set<number>()
    const s = new Set<number>()
    edges.forEach((e, i) => {
      if (e.sourceId === selectedNode || e.targetId === selectedNode) s.add(i)
    })
    return s
  }, [selectedNode, edges])

  const isNodeDimmed = (nodeId: string) => {
    if (!selectedNode) return false
    if (nodeId === selectedNode) return false
    return !edges.some(e =>
      (e.sourceId === selectedNode && e.targetId === nodeId) ||
      (e.targetId === selectedNode && e.sourceId === nodeId)
    )
  }

  return (
    <div className="glass-card p-6 relative" ref={containerRef}>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <GitBranch className="w-5 h-5 text-primary-400" />
          Interactive Schema Graph
        </h3>
        <div className="flex items-center gap-2">
          <button onClick={() => setZoom(z => Math.min(z + 0.2, 2.5))}
            className="p-2 rounded-lg bg-dark-800 hover:bg-dark-700 transition-colors"><ZoomIn className="w-4 h-4" /></button>
          <button onClick={() => setZoom(z => Math.max(z - 0.2, 0.4))}
            className="p-2 rounded-lg bg-dark-800 hover:bg-dark-700 transition-colors"><ZoomOut className="w-4 h-4" /></button>
          <button onClick={resetView}
            className="p-2 rounded-lg bg-dark-800 hover:bg-dark-700 transition-colors"><Maximize2 className="w-4 h-4" /></button>
          {selectedNode && (
            <button onClick={() => setSelectedNode(null)}
              className="px-3 py-1.5 text-xs rounded-lg bg-primary-500/20 text-primary-400 border border-primary-500/30">
              Clear Selection
            </button>
          )}
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="overflow-hidden rounded-xl bg-dark-950/80 border border-dark-700/50"
        style={{ height: Math.min(svgHeight * zoom + 60, 700), cursor: isPanning ? 'grabbing' : 'grab' }}>
        <svg
          width="100%" height="100%"
          viewBox={`${-pan.x / zoom} ${-pan.y / zoom} ${880 / zoom} ${svgHeight / zoom}`}
          onMouseDown={handleMouseDown} onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp}
        >
          <defs>
            <filter id="glow-g"><feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="#10b981" floodOpacity="0.6" /></filter>
            <filter id="glow-y"><feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="#f59e0b" floodOpacity="0.6" /></filter>
            <filter id="glow-r"><feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="#ef4444" floodOpacity="0.6" /></filter>
            <filter id="glow-b"><feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#3b82f6" floodOpacity="0.4" /></filter>
            <filter id="glow-p"><feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#a855f7" floodOpacity="0.4" /></filter>
          </defs>

          {/* ── Bezier Edges ── */}
          {edges.map((edge, idx) => {
            const src = nodes.find(n => n.id === edge.sourceId)
            const tgt = nodes.find(n => n.id === edge.targetId)
            if (!src || !tgt) return null

            const x1 = src.x + 220, y1 = src.y + 20
            const x2 = tgt.x, y2 = tgt.y + 20
            const cx1 = x1 + 120, cx2 = x2 - 120
            const color = edgeColor(edge.confidence)
            const isHl = hoveredEdge === idx || connectedEdgeSet.has(idx)
            const isDim = (hoveredEdge !== null && hoveredEdge !== idx && !connectedEdgeSet.has(idx)) ||
              (selectedNode !== null && !connectedEdgeSet.has(idx))
            const dashed = edge.confidence === 'low'
            const glowId = edge.confidence === 'high' ? 'glow-g' : edge.confidence === 'medium' ? 'glow-y' : 'glow-r'

            return (
              <g key={`e-${idx}`}>
                {/* Wide invisible hit area */}
                <path d={`M${x1},${y1} C${cx1},${y1} ${cx2},${y2} ${x2},${y2}`}
                  fill="none" stroke="transparent" strokeWidth={16}
                  onMouseMove={(ev) => showEdgeTooltip(ev, edge, idx)}
                  onMouseLeave={hideEdgeTooltip} style={{ cursor: 'pointer' }} />
                {/* Visible bezier */}
                <path d={`M${x1},${y1} C${cx1},${y1} ${cx2},${y2} ${x2},${y2}`}
                  fill="none" stroke={color}
                  strokeWidth={isHl ? 3 : 1.5}
                  strokeOpacity={isDim ? 0.1 : isHl ? 1 : 0.5}
                  strokeDasharray={dashed ? '6 4' : undefined}
                  filter={isHl ? `url(#${glowId})` : undefined}
                  style={{ transition: 'all .2s' }} pointerEvents="none" />
                {/* Animated dot when highlighted */}
                {isHl && (
                  <circle r="4" fill={color}>
                    <animateMotion dur="1.5s" repeatCount="indefinite"
                      path={`M${x1},${y1} C${cx1},${y1} ${cx2},${y2} ${x2},${y2}`} />
                  </circle>
                )}
              </g>
            )
          })}

          {/* ── Source Nodes (left) ── */}
          {nodes.filter(n => n.type === 'source' || n.type === 'source_unmapped').map((node) => {
            const unm = node.type === 'source_unmapped'
            const sel = selectedNode === node.id
            const dim = isNodeDimmed(node.id)
            return (
              <g key={node.id} onClick={() => setSelectedNode(sel ? null : node.id)} style={{ cursor: 'pointer' }}>
                <rect x={node.x} y={node.y} width={220} height={40} rx={8}
                  fill={unm ? '#1e293b' : '#1e3a5f'}
                  stroke={sel ? '#3b82f6' : unm ? '#475569' : '#3b82f6'}
                  strokeWidth={sel ? 2 : 1} opacity={dim ? 0.25 : 1}
                  filter={sel ? 'url(#glow-b)' : undefined}
                  style={{ transition: 'all .2s' }} />
                <text x={node.x + 12} y={node.y + 16} fontSize="10" fill="#94a3b8" opacity={dim ? 0.25 : 0.7}>{node.table}</text>
                <text x={node.x + 12} y={node.y + 31} fontSize="12" fontFamily="monospace"
                  fill={unm ? '#64748b' : '#60a5fa'} fontWeight={sel ? 700 : 500} opacity={dim ? 0.25 : 1}>
                  {node.label.length > 22 ? node.label.slice(0, 22) + '…' : node.label}
                </text>
                {unm && <text x={node.x + 205} y={node.y + 26} fontSize="10" fill="#ef4444" textAnchor="end">✗</text>}
              </g>
            )
          })}

          {/* ── Target Nodes (right) ── */}
          {nodes.filter(n => n.type === 'target' || n.type === 'target_unmapped').map((node) => {
            const unm = node.type === 'target_unmapped'
            const sel = selectedNode === node.id
            const dim = isNodeDimmed(node.id)
            return (
              <g key={node.id} onClick={() => setSelectedNode(sel ? null : node.id)} style={{ cursor: 'pointer' }}>
                <rect x={node.x} y={node.y} width={220} height={40} rx={8}
                  fill={unm ? '#1e293b' : '#2d1f5e'}
                  stroke={sel ? '#a855f7' : unm ? '#475569' : '#a855f7'}
                  strokeWidth={sel ? 2 : 1} opacity={dim ? 0.25 : 1}
                  filter={sel ? 'url(#glow-p)' : undefined}
                  style={{ transition: 'all .2s' }} />
                <text x={node.x + 12} y={node.y + 16} fontSize="10" fill="#94a3b8" opacity={dim ? 0.25 : 0.7}>{node.table}</text>
                <text x={node.x + 12} y={node.y + 31} fontSize="12" fontFamily="monospace"
                  fill={unm ? '#64748b' : '#c084fc'} fontWeight={sel ? 700 : 500} opacity={dim ? 0.25 : 1}>
                  {node.label.length > 22 ? node.label.slice(0, 22) + '…' : node.label}
                </text>
                {unm && <text x={node.x + 205} y={node.y + 26} fontSize="10" fill="#ef4444" textAnchor="end">✗</text>}
              </g>
            )
          })}
        </svg>
      </div>

      {/* Floating Tooltip */}
      <AnimatePresence>
        {tooltip && (
          <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="absolute pointer-events-none z-50"
            style={{ left: tooltip.x, top: tooltip.y, transform: 'translate(-50%,-100%)' }}>
            <div className={`px-4 py-3 rounded-xl shadow-2xl border backdrop-blur-xl max-w-xs
              ${tooltip.confidence === 'high' ? 'bg-emerald-950/90 border-emerald-500/40' :
                tooltip.confidence === 'medium' ? 'bg-amber-950/90 border-amber-500/40' :
                  'bg-red-950/90 border-red-500/40'}`}>
              <p className="text-sm font-medium text-white">{tooltip.text}</p>
              <p className="text-xs text-dark-300 mt-1">{tooltip.subtext}</p>
              <span className={`mt-2 inline-block text-xs px-2 py-0.5 rounded-full
                ${tooltip.confidence === 'high' ? 'bg-emerald-500/20 text-emerald-400' :
                  tooltip.confidence === 'medium' ? 'bg-amber-500/20 text-amber-400' :
                    'bg-red-500/20 text-red-400'}`}>
                {tooltip.confidence} confidence
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <p className="text-xs text-dark-500 mt-3 flex items-center gap-1">
        <Info className="w-3 h-3" />
        Click a node to highlight its connections · Hover edges for AI reasoning · Drag to pan · Use zoom controls
      </p>
    </div>
  )
}

/* ─────────────────────────────────────────────────────
   Main Visualization Page
   ───────────────────────────────────────────────────── */

export default function Visualization() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'graph' | 'table' | 'flow'>('graph')

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
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Table Mapping Visualization</h1>
        <p className="text-dark-400 mt-1">Interactive graph of source-to-target schema relationships</p>
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

      {/* View Tabs */}
      <div className="flex gap-2">
        {([
          { id: 'graph' as const, label: 'Schema Graph', icon: GitBranch },
          { id: 'table' as const, label: 'Table View', icon: Table },
          { id: 'flow' as const, label: 'Flow List', icon: BarChart3 },
        ]).map((v) => (
          <button key={v.id} onClick={() => setViewMode(v.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${viewMode === v.id ? 'tab-active' : 'tab-inactive'}`}>
            <v.icon className="w-4 h-4" />{v.label}
          </button>
        ))}
      </div>

      {/* ── GRAPH VIEW ── */}
      {viewMode === 'graph' && <InteractiveSchemaGraph data={data} />}

      {/* ── TABLE VIEW ── */}
      {viewMode === 'table' && (
        <div className="space-y-6">
          {data.table_mappings.map((tm, idx) => (
            <motion.div key={idx} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }} className="glass-card p-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="flex-1 text-center p-3 rounded-lg bg-blue-500/20 border border-blue-500/30">
                  <p className="text-sm text-dark-400">Source Table</p>
                  <h3 className="text-xl font-bold text-blue-400">{tm.source_table}</h3>
                </div>
                <ArrowRight className="w-8 h-8 text-dark-500 flex-shrink-0" />
                <div className="flex-1 text-center p-3 rounded-lg bg-purple-500/20 border border-purple-500/30">
                  <p className="text-sm text-dark-400">Target Table</p>
                  <h3 className="text-xl font-bold text-purple-400">{tm.target_table}</h3>
                </div>
              </div>
              <div className="grid gap-2">
                {tm.columns.map((col, ci) => (
                  <div key={ci} className="flex items-center gap-4 p-3 rounded-lg bg-dark-800/50 hover:bg-dark-800 transition-colors">
                    <code className="flex-1 text-blue-400 font-mono text-sm">{col.source}</code>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 rounded-full bg-dark-700 overflow-hidden">
                        <motion.div initial={{ width: 0 }} animate={{ width: `${col.score * 100}%` }}
                          transition={{ duration: 0.5, delay: ci * 0.05 }}
                          className={`h-full ${col.confidence === 'high' ? 'bg-emerald-500' : col.confidence === 'medium' ? 'bg-amber-500' : 'bg-red-500'}`} />
                      </div>
                      <span className="text-xs text-dark-400 w-12 text-right">{(col.score * 100).toFixed(0)}%</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-dark-500" />
                    <code className="flex-1 text-purple-400 font-mono text-sm text-right">{col.target}</code>
                    <span className={`badge-${col.confidence} text-xs`}>{col.confidence}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* ── FLOW LIST VIEW ── */}
      {viewMode === 'flow' && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Column Mapping Flow</h3>
          <div className="space-y-2">
            {data.sankey.links.map((link, idx) => {
              const sn = data.sankey.nodes[link.source]
              const tn = data.sankey.nodes[link.target]
              return (
                <motion.div key={idx} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.03 }}
                  className="flex items-center gap-4 p-3 rounded-lg bg-dark-800/50 hover:bg-dark-800 transition-colors">
                  <div className="flex-1 flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${sn.type === 'source_unmapped' ? 'bg-dark-500' : 'bg-blue-500'}`} />
                    <code className="text-sm text-blue-400 font-mono truncate">{sn.name}</code>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-16 h-1 rounded-full ${link.confidence === 'high' ? 'bg-emerald-500' : link.confidence === 'medium' ? 'bg-amber-500' : 'bg-red-500'}`} />
                    <ArrowRight className={`w-4 h-4 ${link.confidence === 'high' ? 'text-emerald-500' : link.confidence === 'medium' ? 'text-amber-500' : 'text-red-500'}`} />
                  </div>
                  <div className="flex-1 flex items-center gap-2 justify-end">
                    <code className="text-sm text-purple-400 font-mono truncate text-right">{tn.name}</code>
                    <div className={`w-3 h-3 rounded-full ${tn.type === 'target_unmapped' ? 'bg-dark-500' : 'bg-purple-500'}`} />
                  </div>
                  <span className={`w-16 text-right font-bold ${link.confidence === 'high' ? 'text-emerald-400' : link.confidence === 'medium' ? 'text-amber-400' : 'text-red-400'}`}>
                    {(link.value * 100).toFixed(0)}%
                  </span>
                </motion.div>
              )
            })}
          </div>

          {data.sankey.nodes.filter(n => n.type.includes('unmapped')).length > 0 && (
            <div className="mt-6 pt-6 border-t border-dark-700">
              <h4 className="text-sm font-semibold text-dark-400 mb-3">Unmapped Fields</h4>
              <div className="grid md:grid-cols-2 gap-4">
                {data.sankey.nodes.filter(n => n.type === 'source_unmapped').length > 0 && (
                  <div>
                    <p className="text-xs text-dark-500 mb-2">Source (not mapped)</p>
                    <div className="space-y-1">
                      {data.sankey.nodes.filter(n => n.type === 'source_unmapped').map((node, i) => (
                        <div key={i} className="flex items-center gap-2 p-2 rounded bg-dark-800/50">
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
                      {data.sankey.nodes.filter(n => n.type === 'target_unmapped').map((node, i) => (
                        <div key={i} className="flex items-center gap-2 p-2 rounded bg-dark-800/50">
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
          <div className="flex items-center gap-2"><div className="w-4 h-4 rounded bg-blue-500" /><span className="text-sm text-dark-400">Source Column</span></div>
          <div className="flex items-center gap-2"><div className="w-4 h-4 rounded bg-purple-500" /><span className="text-sm text-dark-400">Target Column</span></div>
          <div className="flex items-center gap-2"><div className="w-8 h-1 rounded bg-emerald-500" /><span className="text-sm text-dark-400">High Confidence</span></div>
          <div className="flex items-center gap-2"><div className="w-8 h-1 rounded bg-amber-500" /><span className="text-sm text-dark-400">Medium Confidence</span></div>
          <div className="flex items-center gap-2"><div className="w-8 h-1 rounded bg-red-500 border-dashed border border-red-500" /><span className="text-sm text-dark-400">Low (dashed)</span></div>
          <div className="flex items-center gap-2"><div className="w-4 h-4 rounded bg-dark-600" /><span className="text-sm text-dark-400">Unmapped</span></div>
        </div>
      </div>
    </motion.div>
  )
}

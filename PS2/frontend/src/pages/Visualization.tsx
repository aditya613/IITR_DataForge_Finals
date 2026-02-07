import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart3,
  GitBranch,
  AlertCircle,
  ArrowRight,
  ArrowRightLeft,
  Table,
  Link2,
  Unlink,
  CheckCircle,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Info,
  Database
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

    const ROW_H = 58
    const PAD_TOP = 60
    const LEFT_X = 80
    const RIGHT_X = 620

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
    nodes.filter(n => n.type === 'source' || n.type === 'source_unmapped').length * 58 + 120,
    nodes.filter(n => n.type === 'target' || n.type === 'target_unmapped').length * 58 + 120,
    450
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
      text: `${srcLabel} → ${tgtLabel}`,
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

  // Stats
  const highConfCount = edges.filter(e => e.confidence === 'high').length
  const medConfCount = edges.filter(e => e.confidence === 'medium').length
  const lowConfCount = edges.filter(e => e.confidence === 'low').length
  const sourceCount = nodes.filter(n => n.type === 'source' || n.type === 'source_unmapped').length
  const targetCount = nodes.filter(n => n.type === 'target' || n.type === 'target_unmapped').length

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 border border-white/10" ref={containerRef}>
      {/* Animated Background Pattern */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, rgba(148, 163, 184, 0.15) 1px, transparent 0)`,
          backgroundSize: '24px 24px'
        }} />
      </div>
      
      {/* Gradient Orbs */}
      <div className="absolute top-20 left-20 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-20 right-20 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl" />

      {/* Header */}
      <div className="relative z-10 p-6 border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 shadow-lg shadow-blue-500/25">
              <GitBranch className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Interactive Schema Graph</h3>
              <p className="text-sm text-gray-400">AI-powered column mapping visualization</p>
            </div>
          </div>
          
          {/* Stats Pills */}
          <div className="hidden md:flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/30">
              <Database className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-medium text-blue-300">{sourceCount} source</span>
            </div>
            <ArrowRightLeft className="w-4 h-4 text-gray-500" />
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/30">
              <Database className="w-4 h-4 text-purple-400" />
              <span className="text-sm font-medium text-purple-300">{targetCount} target</span>
            </div>
          </div>
          
          {/* Controls */}
          <div className="flex items-center gap-2">
            <button onClick={() => setZoom(z => Math.min(z + 0.2, 2.5))}
              className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all hover:scale-105">
              <ZoomIn className="w-4 h-4 text-gray-300" />
            </button>
            <button onClick={() => setZoom(z => Math.max(z - 0.2, 0.4))}
              className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all hover:scale-105">
              <ZoomOut className="w-4 h-4 text-gray-300" />
            </button>
            <button onClick={resetView}
              className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all hover:scale-105">
              <Maximize2 className="w-4 h-4 text-gray-300" />
            </button>
            {selectedNode && (
              <button onClick={() => setSelectedNode(null)}
                className="px-4 py-2 text-sm rounded-xl bg-blue-500/20 text-blue-300 border border-blue-500/30 hover:bg-blue-500/30 transition-all">
                Clear Selection
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Confidence Legend */}
      <div className="relative z-10 px-6 py-3 border-b border-white/5 bg-black/10 flex items-center gap-6">
        <span className="text-xs text-gray-500 uppercase tracking-wider">Confidence:</span>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50" />
            <span className="text-xs text-gray-400">High ({highConfCount})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-amber-500 shadow-sm shadow-amber-500/50" />
            <span className="text-xs text-gray-400">Medium ({medConfCount})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500 shadow-sm shadow-red-500/50" />
            <span className="text-xs text-gray-400">Low ({lowConfCount})</span>
          </div>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-gradient-to-r from-emerald-500 to-emerald-500" />
            <span className="text-xs text-gray-500">Solid = High/Med</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 border-t-2 border-dashed border-red-500" />
            <span className="text-xs text-gray-500">Dashed = Low</span>
          </div>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="relative overflow-hidden"
        style={{ height: Math.min(svgHeight * zoom + 60, 700), cursor: isPanning ? 'grabbing' : 'grab' }}>
        <svg
          width="100%" height="100%"
          viewBox={`${-pan.x / zoom} ${-pan.y / zoom} ${920 / zoom} ${svgHeight / zoom}`}
          onMouseDown={handleMouseDown} onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp}
          className="select-none"
        >
          <defs>
            {/* Glows */}
            <filter id="glow-g"><feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#10b981" floodOpacity="0.7" /></filter>
            <filter id="glow-y"><feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#f59e0b" floodOpacity="0.7" /></filter>
            <filter id="glow-r"><feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#ef4444" floodOpacity="0.7" /></filter>
            <filter id="glow-b"><feDropShadow dx="0" dy="0" stdDeviation="5" floodColor="#3b82f6" floodOpacity="0.5" /></filter>
            <filter id="glow-p"><feDropShadow dx="0" dy="0" stdDeviation="5" floodColor="#a855f7" floodOpacity="0.5" /></filter>
            <filter id="glow-c"><feDropShadow dx="0" dy="0" stdDeviation="6" floodColor="#06b6d4" floodOpacity="0.4" /></filter>
            
            {/* Gradient fills for nodes */}
            <linearGradient id="sourceGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#1e40af" />
              <stop offset="100%" stopColor="#0e7490" />
            </linearGradient>
            <linearGradient id="targetGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#5b21b6" />
              <stop offset="100%" stopColor="#7c3aed" />
            </linearGradient>
            <linearGradient id="unmappedGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#1e293b" />
              <stop offset="100%" stopColor="#334155" />
            </linearGradient>
            
            {/* Edge gradients */}
            <linearGradient id="edgeGradHigh" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" />
              <stop offset="100%" stopColor="#34d399" />
            </linearGradient>
            <linearGradient id="edgeGradMed" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#fbbf24" />
            </linearGradient>
            <linearGradient id="edgeGradLow" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#ef4444" />
              <stop offset="100%" stopColor="#f87171" />
            </linearGradient>
          </defs>

          {/* ── Column Headers ── */}
          <text x={80 + 110} y={30} fontSize="11" fill="#64748b" textAnchor="middle" fontWeight="600" letterSpacing="0.1em">SOURCE SCHEMA</text>
          <text x={620 + 110} y={30} fontSize="11" fill="#64748b" textAnchor="middle" fontWeight="600" letterSpacing="0.1em">TARGET SCHEMA</text>

          {/* ── Bezier Edges ── */}
          {edges.map((edge, idx) => {
            const src = nodes.find(n => n.id === edge.sourceId)
            const tgt = nodes.find(n => n.id === edge.targetId)
            if (!src || !tgt) return null

            const x1 = src.x + 220, y1 = src.y + 22
            const x2 = tgt.x, y2 = tgt.y + 22
            const cx1 = x1 + 140, cx2 = x2 - 140
            const color = edgeColor(edge.confidence)
            const isHl = hoveredEdge === idx || connectedEdgeSet.has(idx)
            const isDim = (hoveredEdge !== null && hoveredEdge !== idx && !connectedEdgeSet.has(idx)) ||
              (selectedNode !== null && !connectedEdgeSet.has(idx))
            const dashed = edge.confidence === 'low'
            const glowId = edge.confidence === 'high' ? 'glow-g' : edge.confidence === 'medium' ? 'glow-y' : 'glow-r'
            const gradId = edge.confidence === 'high' ? 'url(#edgeGradHigh)' : edge.confidence === 'medium' ? 'url(#edgeGradMed)' : 'url(#edgeGradLow)'

            return (
              <g key={`e-${idx}`}>
                {/* Wide invisible hit area */}
                <path d={`M${x1},${y1} C${cx1},${y1} ${cx2},${y2} ${x2},${y2}`}
                  fill="none" stroke="transparent" strokeWidth={18}
                  onMouseMove={(ev) => showEdgeTooltip(ev, edge, idx)}
                  onMouseLeave={hideEdgeTooltip} style={{ cursor: 'pointer' }} />
                {/* Visible bezier */}
                <path d={`M${x1},${y1} C${cx1},${y1} ${cx2},${y2} ${x2},${y2}`}
                  fill="none" stroke={isHl ? gradId : color}
                  strokeWidth={isHl ? 3.5 : 2}
                  strokeOpacity={isDim ? 0.08 : isHl ? 1 : 0.4}
                  strokeDasharray={dashed ? '8 5' : undefined}
                  filter={isHl ? `url(#${glowId})` : undefined}
                  strokeLinecap="round"
                  style={{ transition: 'all .25s ease-out' }} pointerEvents="none" />
                {/* Animated dot when highlighted */}
                {isHl && (
                  <>
                    <circle r="5" fill={color} filter={`url(#${glowId})`}>
                      <animateMotion dur="2s" repeatCount="indefinite"
                        path={`M${x1},${y1} C${cx1},${y1} ${cx2},${y2} ${x2},${y2}`} />
                    </circle>
                    <circle r="3" fill="white" opacity="0.8">
                      <animateMotion dur="2s" repeatCount="indefinite"
                        path={`M${x1},${y1} C${cx1},${y1} ${cx2},${y2} ${x2},${y2}`} />
                    </circle>
                  </>
                )}
                {/* Connection indicator circles */}
                {isHl && (
                  <>
                    <circle cx={x1} cy={y1} r="4" fill={color} filter={`url(#${glowId})`}>
                      <animate attributeName="r" values="4;6;4" dur="1s" repeatCount="indefinite" />
                    </circle>
                    <circle cx={x2} cy={y2} r="4" fill={color} filter={`url(#${glowId})`}>
                      <animate attributeName="r" values="4;6;4" dur="1s" repeatCount="indefinite" />
                    </circle>
                  </>
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
                {/* Shadow */}
                <rect x={node.x + 3} y={node.y + 3} width={220} height={44} rx={10}
                  fill="rgba(0,0,0,0.3)" opacity={dim ? 0.1 : 0.5} />
                {/* Main rect */}
                <rect x={node.x} y={node.y} width={220} height={44} rx={10}
                  fill={unm ? 'url(#unmappedGrad)' : 'url(#sourceGrad)'}
                  stroke={sel ? '#06b6d4' : unm ? '#475569' : '#0ea5e9'}
                  strokeWidth={sel ? 2.5 : 1.5} opacity={dim ? 0.2 : 1}
                  filter={sel ? 'url(#glow-c)' : undefined}
                  style={{ transition: 'all .25s ease-out' }} />
                {/* Icon area */}
                <rect x={node.x + 8} y={node.y + 8} width={28} height={28} rx={6}
                  fill="rgba(255,255,255,0.1)" opacity={dim ? 0.2 : 1} />
                <text x={node.x + 22} y={node.y + 27} fontSize="14" fill="#60a5fa" textAnchor="middle" opacity={dim ? 0.2 : 1}>📊</text>
                {/* Table name */}
                <text x={node.x + 44} y={node.y + 16} fontSize="9" fill="#94a3b8" opacity={dim ? 0.2 : 0.7} fontWeight="500">{node.table}</text>
                {/* Column name */}
                <text x={node.x + 44} y={node.y + 32} fontSize="12" fontFamily="'SF Mono', monospace"
                  fill={unm ? '#94a3b8' : '#7dd3fc'} fontWeight={sel ? 700 : 500} opacity={dim ? 0.2 : 1}>
                  {node.label.length > 18 ? node.label.slice(0, 18) + '…' : node.label}
                </text>
                {unm && <text x={node.x + 205} y={node.y + 27} fontSize="12" fill="#f87171" textAnchor="end" opacity={dim ? 0.2 : 1}>✗</text>}
                {sel && !unm && <text x={node.x + 205} y={node.y + 27} fontSize="12" fill="#06b6d4" textAnchor="end">●</text>}
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
                {/* Shadow */}
                <rect x={node.x + 3} y={node.y + 3} width={220} height={44} rx={10}
                  fill="rgba(0,0,0,0.3)" opacity={dim ? 0.1 : 0.5} />
                {/* Main rect */}
                <rect x={node.x} y={node.y} width={220} height={44} rx={10}
                  fill={unm ? 'url(#unmappedGrad)' : 'url(#targetGrad)'}
                  stroke={sel ? '#c084fc' : unm ? '#475569' : '#a855f7'}
                  strokeWidth={sel ? 2.5 : 1.5} opacity={dim ? 0.2 : 1}
                  filter={sel ? 'url(#glow-p)' : undefined}
                  style={{ transition: 'all .25s ease-out' }} />
                {/* Icon area */}
                <rect x={node.x + 8} y={node.y + 8} width={28} height={28} rx={6}
                  fill="rgba(255,255,255,0.1)" opacity={dim ? 0.2 : 1} />
                <text x={node.x + 22} y={node.y + 27} fontSize="14" fill="#c084fc" textAnchor="middle" opacity={dim ? 0.2 : 1}>🎯</text>
                {/* Table name */}
                <text x={node.x + 44} y={node.y + 16} fontSize="9" fill="#94a3b8" opacity={dim ? 0.2 : 0.7} fontWeight="500">{node.table}</text>
                {/* Column name */}
                <text x={node.x + 44} y={node.y + 32} fontSize="12" fontFamily="'SF Mono', monospace"
                  fill={unm ? '#94a3b8' : '#d8b4fe'} fontWeight={sel ? 700 : 500} opacity={dim ? 0.2 : 1}>
                  {node.label.length > 18 ? node.label.slice(0, 18) + '…' : node.label}
                </text>
                {unm && <text x={node.x + 205} y={node.y + 27} fontSize="12" fill="#f87171" textAnchor="end" opacity={dim ? 0.2 : 1}>✗</text>}
                {sel && !unm && <text x={node.x + 205} y={node.y + 27} fontSize="12" fill="#c084fc" textAnchor="end">●</text>}
              </g>
            )
          })}
        </svg>
      </div>

      {/* Floating Tooltip */}
      <AnimatePresence>
        {tooltip && (
          <motion.div initial={{ opacity: 0, y: 8, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 8, scale: 0.95 }}
            className="absolute pointer-events-none z-50"
            style={{ left: tooltip.x, top: tooltip.y, transform: 'translate(-50%,-100%)' }}>
            <div className={`px-5 py-4 rounded-2xl shadow-2xl border backdrop-blur-xl max-w-sm
              ${tooltip.confidence === 'high' ? 'bg-emerald-950/95 border-emerald-400/40 shadow-emerald-500/20' :
                tooltip.confidence === 'medium' ? 'bg-amber-950/95 border-amber-400/40 shadow-amber-500/20' :
                  'bg-red-950/95 border-red-400/40 shadow-red-500/20'}`}>
              <div className="flex items-center gap-2 mb-2">
                <ArrowRight className={`w-4 h-4 ${tooltip.confidence === 'high' ? 'text-emerald-400' : tooltip.confidence === 'medium' ? 'text-amber-400' : 'text-red-400'}`} />
                <p className="text-sm font-semibold text-white">{tooltip.text}</p>
              </div>
              <p className="text-xs text-gray-300">{tooltip.subtext}</p>
              <div className="flex items-center gap-2 mt-3">
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium
                  ${tooltip.confidence === 'high' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                    tooltip.confidence === 'medium' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                      'bg-red-500/20 text-red-300 border border-red-500/30'}`}>
                  {tooltip.confidence.toUpperCase()} CONFIDENCE
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer */}
      <div className="relative z-10 px-6 py-3 border-t border-white/5 bg-black/20 flex items-center justify-between">
        <p className="text-xs text-gray-500 flex items-center gap-2">
          <Info className="w-3.5 h-3.5" />
          Click nodes to highlight connections • Hover edges for AI reasoning • Drag to pan • Scroll to zoom
        </p>
        <div className="text-xs text-gray-500">
          {edges.length} mappings • {nodes.length} columns
        </div>
      </div>
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

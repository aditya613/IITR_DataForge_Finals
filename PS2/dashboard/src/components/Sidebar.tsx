import { NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  Search,
  GitBranch,
  ShieldCheck,
  Rocket,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Database,
  Sparkles
} from 'lucide-react'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
  { icon: Search, label: 'Analysis', path: '/analysis' },
  { icon: GitBranch, label: 'Mappings', path: '/mappings' },
  { icon: ShieldCheck, label: 'Validation', path: '/validation' },
  { icon: Rocket, label: 'Migration', path: '/migration' },
  { icon: BarChart3, label: 'Visualizations', path: '/visualizations' },
  { icon: Settings, label: 'Settings', path: '/settings' },
]

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const location = useLocation()

  return (
    <motion.aside
      className="fixed left-0 top-0 h-screen bg-dark-900/80 backdrop-blur-xl border-r border-dark-700/50 z-50"
      animate={{ width: isOpen ? 256 : 80 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
    >
      {/* Logo */}
      <div className="flex items-center h-20 px-6 border-b border-dark-700/50">
        <motion.div
          className="flex items-center gap-3"
          animate={{ justifyContent: isOpen ? 'flex-start' : 'center' }}
        >
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center shadow-lg shadow-primary-500/30">
              <Database className="w-5 h-5 text-white" />
            </div>
            <Sparkles className="w-4 h-4 text-amber-400 absolute -top-1 -right-1 animate-pulse" />
          </div>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
            >
              <h1 className="font-bold text-lg gradient-text">DataForge</h1>
              <p className="text-xs text-dark-400">AI Migration</p>
            </motion.div>
          )}
        </motion.div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-2 p-4 mt-4">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`group relative flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300
                ${isActive 
                  ? 'bg-gradient-to-r from-primary-500/20 to-secondary-500/20 text-white' 
                  : 'text-dark-400 hover:text-white hover:bg-dark-800'
                }`}
            >
              {/* Active indicator */}
              {isActive && (
                <motion.div
                  layoutId="activeIndicator"
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-primary-500 to-secondary-500 rounded-r-full"
                />
              )}
              
              <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-primary-400' : ''}`} />
              
              {isOpen && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="font-medium whitespace-nowrap"
                >
                  {item.label}
                </motion.span>
              )}

              {/* Tooltip when collapsed */}
              {!isOpen && (
                <div className="absolute left-full ml-2 px-3 py-2 bg-dark-800 rounded-lg text-sm font-medium
                              opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity
                              whitespace-nowrap shadow-xl border border-dark-700">
                  {item.label}
                </div>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-24 w-6 h-6 bg-dark-800 border border-dark-700 rounded-full
                   flex items-center justify-center text-dark-400 hover:text-white hover:bg-dark-700
                   transition-all duration-300 shadow-lg"
      >
        {isOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-dark-700/50">
        {isOpen ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center"
          >
            <p className="text-xs text-dark-500">Powered by</p>
            <p className="text-sm font-semibold gradient-text">Hybrid AI Engine</p>
            <p className="text-xs text-dark-500 mt-1">BERT + LLM + TF-IDF</p>
          </motion.div>
        ) : (
          <div className="flex justify-center">
            <Sparkles className="w-5 h-5 text-primary-400" />
          </div>
        )}
      </div>
    </motion.aside>
  )
}

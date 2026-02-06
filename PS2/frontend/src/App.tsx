import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Database, 
  GitBranch, 
  CheckCircle2, 
  BarChart3, 
  MessageCircle,
  Sparkles
} from 'lucide-react'

// Pages
import Upload from './pages/Upload'
import MappingReport from './pages/MappingReport'
import ValidationReport from './pages/ValidationReport'
import Visualization from './pages/Visualization'
import Explainability from './pages/Explainability'

const navItems = [
  { path: '/', label: 'Upload & Analyze', icon: Database },
  { path: '/mapping', label: 'Mapping Report', icon: GitBranch },
  { path: '/validation', label: 'Validation Report', icon: CheckCircle2 },
  { path: '/visualization', label: 'Visualization', icon: BarChart3 },
  { path: '/explainability', label: 'Explainability', icon: MessageCircle },
]

function Navigation() {
  const location = useLocation()
  
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-950/90 backdrop-blur-xl border-b border-dark-800">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-primary-500 to-cyan-500">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">DataForge</span>
          </div>
          
          {/* Nav Links */}
          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
                    ${isActive 
                      ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' 
                      : 'text-dark-400 hover:text-white hover:bg-dark-800'
                    }`}
                >
                  <item.icon className="w-4 h-4" />
                  <span className="hidden md:inline">{item.label}</span>
                </NavLink>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}

function AppContent() {
  return (
    <div className="min-h-screen bg-dark-950 pt-20 pb-8 px-4">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
      </div>
      
      <Navigation />
      
      <main className="relative max-w-7xl mx-auto">
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<Upload />} />
            <Route path="/mapping" element={<MappingReport />} />
            <Route path="/validation" element={<ValidationReport />} />
            <Route path="/visualization" element={<Visualization />} />
            <Route path="/explainability" element={<Explainability />} />
          </Routes>
        </AnimatePresence>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

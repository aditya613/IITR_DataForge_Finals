import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Analysis from './pages/Analysis'
import Mappings from './pages/Mappings'
import Validation from './pages/Validation'
import Migration from './pages/Migration'
import Visualizations from './pages/Visualizations'
import Settings from './pages/Settings'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <Router>
      <div className="flex min-h-screen bg-dark-950">
        {/* Background Effects */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary-500/10 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-primary-500/5 to-transparent rounded-full" />
        </div>

        {/* Sidebar */}
        <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

        {/* Main Content */}
        <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
          <div className="p-8">
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/analysis" element={<Analysis />} />
                <Route path="/mappings" element={<Mappings />} />
                <Route path="/validation" element={<Validation />} />
                <Route path="/migration" element={<Migration />} />
                <Route path="/visualizations" element={<Visualizations />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </AnimatePresence>
          </div>
        </main>
      </div>
    </Router>
  )
}

export default App

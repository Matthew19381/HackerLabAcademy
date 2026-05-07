import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Map, FlaskConical, CreditCard, Bot, AlertTriangle, BarChart2, Brain, BookMarked, Flag, Terminal as TerminalIcon, Shield, Skull, Network, Award, Newspaper, Plus, X, Loader } from 'lucide-react'
import { getStats, getUserId, quickCreateFlashcard } from '../api/client'
import StudyTimer from './StudyTimer'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/topics', label: 'Tematy', icon: Map },
  { path: '/mindmap', label: 'Mindmap', icon: Network },
  { path: '/lab', label: 'Lab', icon: FlaskConical },
  { path: '/flashcards', label: 'Fiszki', icon: CreditCard },
  { path: '/errors', label: 'Błędy', icon: AlertTriangle },
  { path: '/mentor', label: 'AI Mentor', icon: Bot },
  { path: '/ctf', label: 'CTF', icon: Flag },
  { path: '/defense', label: 'Defense', icon: Shield },
  { path: '/attack', label: 'Attack', icon: Skull },
  { path: '/terminal', label: 'Terminal', icon: TerminalIcon },
  { path: '/articles', label: 'Artykuły', icon: Newspaper },
  { path: '/stats', label: 'Statystyki', icon: BarChart2 },
  { path: '/certificates', label: 'Certyfikaty', icon: Award },
  { path: '/brain', label: 'Brain', icon: Brain },
  { path: '/vocabulary', label: 'Słownik', icon: BookMarked },
]

export default function Layout({ children }) {
  const location = useLocation()
  const [toasts, setToasts] = useState([])
  const [stats, setStats] = useState(null)
  const [showQuickCard, setShowQuickCard] = useState(false)
  const [quickTerm, setQuickTerm] = useState('')
  const [quickSaving, setQuickSaving] = useState(false)

  useEffect(() => {
    const userId = getUserId()
    if (!userId) return
    getStats(userId).then(data => {
      setStats(data)
      if (data.new_achievements?.length > 0) {
        setToasts(data.new_achievements)
        setTimeout(() => setToasts([]), 5000)
      }
    }).catch(() => {})
  }, [location.pathname])

  const handleQuickCard = async () => {
    if (!quickTerm.trim()) return
    const userId = getUserId()
    if (!userId) return
    setQuickSaving(true)
    try {
      await quickCreateFlashcard(userId, quickTerm.trim())
      setShowQuickCard(false)
      setQuickTerm('')
    } catch {
      alert('Błąd tworzenia fiszki')
    } finally {
      setQuickSaving(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-[#0d1117]">
      {/* Sidebar */}
      <aside className="w-56 bg-[#161b22] border-r border-[#30363d] flex flex-col">
        <div className="p-4 border-b border-[#30363d]">
          <h1 className="text-[#39d353] font-bold text-lg font-mono">HackerLabAcademy</h1>
          <p className="text-[#8b949e] text-xs mt-1">Web Security Training</p>
        </div>

        {stats && (
          <div className="px-4 py-3 border-b border-[#30363d]">
            <div className="text-xs text-[#8b949e] mb-1">
              Level {stats.level_info.level} · {stats.level_info.level_name}
            </div>
            <div className="w-full bg-[#30363d] rounded-full h-1.5">
              <div
                className="bg-[#39d353] h-1.5 rounded-full transition-all"
                style={{ width: `${stats.level_info.progress_percent}%` }}
              />
            </div>
            <div className="text-xs text-[#8b949e] mt-1">{stats.level_info.xp} XP</div>
          </div>
        )}

        <nav className="flex-1 p-2 space-y-1">
          {navItems.map(({ path, label, icon: Icon }) => {
            const active = location.pathname === path
            return (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                  active
                    ? 'bg-[#1f6feb]/20 text-[#58a6ff] border border-[#1f6feb]/40'
                    : 'text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d]'
                }`}
              >
                <Icon size={16} />
                {label}
                {path === '/errors' && stats?.progress?.errors_pending > 0 && (
                  <span className="ml-auto bg-[#f85149] text-white text-xs px-1.5 rounded-full">
                    {stats.progress.errors_pending}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>

        {stats && (
          <div className="p-4 border-t border-[#30363d] text-xs text-[#8b949e]">
            🔥 {stats.user.streak_days} dni z rzędu
          </div>
        )}
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>

      {/* Global Study Timer */}
      <StudyTimer />

      {/* Global Quick Flashcard Button */}
      <button
        onClick={() => setShowQuickCard(true)}
        className="fixed bottom-6 left-6 z-50 flex items-center gap-2 bg-[#bc8cff] hover:bg-[#a371f7] text-white px-4 py-2.5 rounded-full shadow-lg text-sm font-medium transition-colors"
        title="Szybka fiszka"
      >
        <Plus size={16} />
        Fiszka
      </button>

      {/* Quick Flashcard Modal */}
      {showQuickCard && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[#f0f6fc] font-bold">Szybka fiszka</h3>
              <button onClick={() => { setShowQuickCard(false); setQuickTerm('') }} className="text-[#8b949e] hover:text-[#c9d1d9]">
                <X size={18} />
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-[#8b949e] text-sm mb-1 block">Termin</label>
                <input
                  type="text"
                  value={quickTerm}
                  onChange={e => setQuickTerm(e.target.value)}
                  placeholder="Np. SQL Injection"
                  className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-[#f0f6fc] text-sm focus:outline-none focus:border-[#58a6ff]"
                  onKeyDown={e => e.key === 'Enter' && handleQuickCard()}
                />
              </div>
              <button
                onClick={handleQuickCard}
                disabled={quickSaving || !quickTerm.trim()}
                className="w-full bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-2"
              >
                {quickSaving ? <Loader size={14} className="animate-spin" /> : <Plus size={14} />}
                Dodaj fiszkę (AI uzupełni)
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Achievement toasts */}
      <div className="fixed bottom-4 right-4 space-y-2 z-50">
        {toasts.map((a, i) => (
          <div key={i} className="bg-[#161b22] border border-[#39d353]/50 rounded-lg p-3 flex items-center gap-3 shadow-lg">
            <span className="text-2xl">{a.icon}</span>
            <div>
              <div className="text-[#39d353] font-medium text-sm">{a.title}</div>
              <div className="text-[#8b949e] text-xs">{a.description}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

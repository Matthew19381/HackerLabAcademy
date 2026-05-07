import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getStats, getDueFlashcards, getDueErrors, getUser, getUserId } from '../api/client'
import { BookOpen, FlaskConical, CreditCard, AlertTriangle, TrendingUp, Lightbulb } from 'lucide-react'
import { getTipOfTheDay } from '../data/security_tips'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [dueCards, setDueCards] = useState(0)
  const [dueErrors, setDueErrors] = useState(0)
  const [user, setUser] = useState(null)
  const [dailyTip, setDailyTip] = useState('')
  const [dailyStatus, setDailyStatus] = useState(null)
  const userId = getUserId()

  useEffect(() => {
    if (!userId) return
    getStats(userId).then(setStats).catch(() => {})
    getDueFlashcards(userId).then(cards => setDueCards(cards.length)).catch(() => {})
    getDueErrors(userId).then(errors => setDueErrors(errors.length)).catch(() => {})
    getUser(userId).then(setUser).catch(() => {})
    getDailyStatus(userId).then(setDailyStatus).catch(() => {})
    setDailyTip(getTipOfTheDay())
  }, [userId])

  if (!stats) return (
    <div className="p-8 text-[#8b949e] text-center">
      <div className="animate-pulse">Ładowanie...</div>
    </div>
  )

  const { level_info, progress } = stats
  const completionPct = progress.topics_total
    ? Math.round((progress.theory_completed / progress.topics_total) * 100)
    : 0

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-[#f0f6fc]">
          Cześć, {user?.name || 'Hacker'} 👋
        </h2>
        <p className="text-[#8b949e] mt-1">Oto Twój dzisiejszy przegląd</p>
      </div>

      {/* Daily Security Tip */}
      {dailyTip && (
        <div className="bg-[#0d1117] border border-[#e3b341]/30 rounded-xl p-5 mb-6">
          <div className="flex items-center gap-2 mb-2">
            <Lightbulb size={18} className="text-[#e3b341]" />
            <h3 className="text-[#e3b341] font-medium">Wskazówka bezpieczeństwa dnia</h3>
          </div>
          <p className="text-[#c9d1d9] text-sm">{dailyTip}</p>
        </div>
      )}

      {/* Daily Completion Bar */}
      {dailyStatus && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5 mb-6">
          <h3 className="text-[#f0f6fc] font-medium mb-3 flex items-center gap-2">
            <span>📅 Dzienny postęp</span>
          </h3>
          <div className="w-full bg-[#30363d] rounded-full h-2 mb-2">
            <div
              className="bg-[#58a6ff] h-2 rounded-full transition-all"
              style={{ width: `${dailyStatus.completion_percent}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-[#8b949e]">
            <span>{dailyStatus.completed_tasks}/{dailyStatus.total_tasks} zadań</span>
            <span>{dailyStatus.completion_percent}%</span>
          </div>
          <div className="text-xs text-[#8b949e] mt-1 flex gap-3 flex-wrap">
            <span>Lab: {dailyStatus.lab_done ? '✅' : '❌'}</span>
            <span>Quiz: {dailyStatus.quiz_done ? '✅' : '❌'}</span>
            <span>Fiszki: {dailyStatus.flashcard_done ? '✅' : '❌'}</span>
            <span>Artykuł: {dailyStatus.article_done ? '✅' : '❌'}</span>
          </div>
        </div>
      )}

      {/* XP / Level card */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6 mb-6">
        <div className="flex items-center justify-between mb-3">
          <div>
            <span className="text-[#39d353] font-bold text-lg">Level {level_info.level}</span>
            <span className="text-[#8b949e] ml-2 text-sm">{level_info.level_name}</span>
          </div>
          <span className="text-[#8b949e] text-sm">{level_info.xp} XP</span>
        </div>
        <div className="w-full bg-[#30363d] rounded-full h-2">
          <div
            className="bg-[#39d353] h-2 rounded-full transition-all"
            style={{ width: `${level_info.progress_percent}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-[#484f58] mt-1">
          <span>{level_info.current_level_xp} XP</span>
          <span>{level_info.next_level_xp} XP</span>
        </div>
      </div>

      {/* Action cards */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <ActionCard
          to="/topics"
          icon={<BookOpen size={24} className="text-[#58a6ff]" />}
          title="Kontynuuj naukę"
          subtitle={`${progress.theory_completed}/${progress.topics_total} tematów · ${completionPct}%`}
          color="blue"
        />
        <ActionCard
          to="/lab"
          icon={<FlaskConical size={24} className="text-[#bc8cff]" />}
          title="Docker Lab"
          subtitle={`${progress.labs_completed} labów ukończonych`}
          color="purple"
        />
        <ActionCard
          to="/flashcards"
          icon={<CreditCard size={24} className="text-[#e3b341]" />}
          title="Fiszki do powtórki"
          subtitle={dueCards > 0 ? `${dueCards} kart czeka` : 'Brak kart na dziś'}
          color="yellow"
          badge={dueCards}
        />
        <ActionCard
          to="/errors"
          icon={<AlertTriangle size={24} className="text-[#f85149]" />}
          title="Błędy do naprawy"
          subtitle={dueErrors > 0 ? `${dueErrors} błędów do przejrzenia` : 'Brak błędów — super!'}
          color="red"
          badge={dueErrors}
        />
      </div>

      {/* Progress overview */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6">
        <h3 className="text-[#f0f6fc] font-medium mb-4 flex items-center gap-2">
          <TrendingUp size={18} className="text-[#39d353]" />
          Postęp ogólny
        </h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          <Stat value={progress.theory_completed} label="Lekcji teorii" />
          <Stat value={progress.labs_completed} label="Labów" />
          <Stat value={stats.user.streak_days} label="Dni streak" suffix="🔥" />
        </div>
      </div>
    </div>
  )
}

function ActionCard({ to, icon, title, subtitle, color, badge }) {
  const borders = {
    blue: 'border-[#1f6feb]/30 hover:border-[#58a6ff]/50',
    purple: 'border-[#6e40c9]/30 hover:border-[#bc8cff]/50',
    yellow: 'border-[#9e6a03]/30 hover:border-[#e3b341]/50',
    red: 'border-[#da3633]/30 hover:border-[#f85149]/50',
  }
  return (
    <Link
      to={to}
      className={`bg-[#161b22] border ${borders[color]} rounded-xl p-5 flex items-start gap-4 hover:bg-[#1c2128] transition-colors group`}
    >
      <div className="mt-0.5">{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="text-[#f0f6fc] font-medium text-sm flex items-center gap-2">
          {title}
          {badge > 0 && (
            <span className="bg-[#f85149] text-white text-xs px-1.5 py-0.5 rounded-full">{badge}</span>
          )}
        </div>
        <div className="text-[#8b949e] text-xs mt-1">{subtitle}</div>
      </div>
    </Link>
  )
}

function Stat({ value, label, suffix }) {
  return (
    <div>
      <div className="text-2xl font-bold text-[#f0f6fc]">
        {value}{suffix}
      </div>
      <div className="text-[#8b949e] text-xs mt-1">{label}</div>
    </div>
  )
}

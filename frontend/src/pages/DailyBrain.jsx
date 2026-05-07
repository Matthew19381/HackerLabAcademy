import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDailyAgenda, getUserId } from '../api/client'
import { Brain, ChevronRight, Flame, Star } from 'lucide-react'

const PRIORITY_COLORS = {
  1: 'border-[#f85149]/40 bg-[#f85149]/5',
  2: 'border-[#e3b341]/40 bg-[#e3b341]/5',
  3: 'border-[#39d353]/40 bg-[#39d353]/5',
  4: 'border-[#bc8cff]/40 bg-[#bc8cff]/5',
  5: 'border-[#58a6ff]/40 bg-[#58a6ff]/5',
}

export default function DailyBrain() {
  const userId = getUserId()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDailyAgenda(userId).then(d => { setData(d); setLoading(false) })
  }, [userId])

  if (loading) return (
    <div className="p-8 text-[#8b949e] text-center animate-pulse flex items-center justify-center gap-2">
      <Brain size={18} /> Analizuję Twój postęp...
    </div>
  )

  const { agenda, summary, stats, level_info } = data

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="flex items-center gap-3 mb-2">
        <Brain size={24} className="text-[#bc8cff]" />
        <h2 className="text-2xl font-bold text-[#f0f6fc]">Learning Brain</h2>
      </div>
      <p className="text-[#8b949e] mb-6">{summary}</p>

      {/* Stats bar */}
      <div className="grid grid-cols-4 gap-3 mb-8">
        {[
          { value: stats.streak, label: 'Streak', icon: '🔥', color: 'text-[#e3b341]' },
          { value: stats.errors_pending, label: 'Błędy', icon: '🐛', color: 'text-[#f85149]' },
          { value: stats.flashcards_due, label: 'Fiszki', icon: '🃏', color: 'text-[#e3b341]' },
          { value: stats.labs_done, label: 'Laby', icon: '🧪', color: 'text-[#bc8cff]' },
        ].map(s => (
          <div key={s.label} className="bg-[#161b22] border border-[#30363d] rounded-xl p-3 text-center">
            <div className={`text-xl font-bold ${s.color}`}>{s.icon} {s.value}</div>
            <div className="text-[#8b949e] text-xs mt-0.5">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Agenda */}
      {agenda.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-3">🎉</div>
          <h3 className="text-[#f0f6fc] font-bold text-lg">Wszystko na dziś zrobione!</h3>
          <p className="text-[#8b949e] mt-1">Wróć jutro. Brain sprawdzi co masz do powtórki.</p>
        </div>
      ) : (
        <div className="space-y-3">
          <h3 className="text-[#8b949e] text-xs font-mono uppercase tracking-widest mb-4">
            Plan na dziś — {agenda.length} zadań
          </h3>
          {agenda.map((item, i) => (
            <Link
              key={i}
              to={item.action_url}
              className={`flex items-center gap-4 p-4 rounded-xl border transition-colors hover:brightness-110 ${PRIORITY_COLORS[item.priority] || 'border-[#30363d]'}`}
            >
              <span className="text-2xl w-8 text-center flex-shrink-0">{item.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="text-[#f0f6fc] font-medium text-sm">{item.title}</div>
                <div className="text-[#8b949e] text-xs mt-0.5 truncate">{item.description}</div>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                <span className="text-xs text-[#39d353]">+{item.xp_potential} XP</span>
                <div className={`text-xs px-2 py-0.5 rounded-full font-mono ${
                  item.priority === 1 ? 'bg-[#f85149]/20 text-[#f85149]' :
                  item.priority === 2 ? 'bg-[#e3b341]/20 text-[#e3b341]' :
                  'bg-[#30363d] text-[#8b949e]'
                }`}>
                  #{item.priority}
                </div>
                <ChevronRight size={16} className="text-[#484f58]" />
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Level progress */}
      <div className="mt-8 bg-[#161b22] border border-[#30363d] rounded-xl p-4">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-[#39d353] font-medium">Level {level_info.level} — {level_info.level_name}</span>
          <span className="text-[#8b949e]">{level_info.xp} XP</span>
        </div>
        <div className="w-full bg-[#30363d] rounded-full h-1.5">
          <div className="bg-[#39d353] h-1.5 rounded-full" style={{ width: `${level_info.progress_percent}%` }} />
        </div>
        <div className="text-xs text-[#484f58] mt-1 text-right">
          Do następnego: {level_info.next_level_xp - level_info.xp} XP
        </div>
      </div>
    </div>
  )
}

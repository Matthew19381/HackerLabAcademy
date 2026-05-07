import { useEffect, useState } from 'react'
import { getStats, getAchievements, getAnalytics, getUserId } from '../api/client'
import { BarChart2, Trophy, ShieldCheck, AlertTriangle, BookOpen } from 'lucide-react'

export default function Stats() {
  const userId = getUserId()
  const [stats, setStats] = useState(null)
  const [achievements, setAchievements] = useState(null)
  const [analytics, setAnalytics] = useState(null)

  useEffect(() => {
    if (!userId) return
    getStats(userId).then(setStats)
    getAchievements(userId).then(setAchievements)
    getAnalytics(userId).then(setAnalytics).catch(() => {})
  }, [userId])

  if (!stats || !achievements) return (
    <div className="p-8 text-[#8b949e] text-center animate-pulse">Ładowanie...</div>
  )

  const { level_info, progress } = stats

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold text-[#f0f6fc] mb-6 flex items-center gap-2">
        <BarChart2 size={24} className="text-[#39d353]" />
        Statystyki
      </h2>

      {/* Level */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6 mb-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-16 h-16 rounded-full bg-[#39d353]/10 border-2 border-[#39d353]/40 flex items-center justify-center">
            <span className="text-[#39d353] font-bold text-xl">{level_info.level}</span>
          </div>
          <div>
            <div className="text-[#f0f6fc] font-bold text-lg">{level_info.level_name}</div>
            <div className="text-[#8b949e] text-sm">{level_info.xp} XP zdobyte</div>
          </div>
        </div>
        <div className="w-full bg-[#30363d] rounded-full h-2 mb-1">
          <div
            className="bg-[#39d353] h-2 rounded-full"
            style={{ width: `${level_info.progress_percent}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-[#484f58]">
          <span>Poziom {level_info.level}: {level_info.current_level_xp} XP</span>
          <span>Poziom {level_info.level + 1}: {level_info.next_level_xp} XP</span>
        </div>
      </div>

      {/* Progress stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { value: progress.theory_completed, label: 'Lekcji teorii', color: 'text-[#58a6ff]' },
          { value: progress.labs_completed, label: 'Labów', color: 'text-[#bc8cff]' },
          { value: `${progress.topics_total - progress.theory_completed}`, label: 'Pozostałych tematów', color: 'text-[#e3b341]' },
          { value: stats.user.streak_days, label: 'Dni streak 🔥', color: 'text-[#39d353]' },
        ].map(s => (
          <div key={s.label} className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
            <div className="text-[#8b949e] text-xs mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Achievements */}
      <div>
        <h3 className="text-[#f0f6fc] font-semibold mb-4 flex items-center gap-2">
          <Trophy size={18} className="text-[#e3b341]" />
          Osiągnięcia — {achievements.earned}/{achievements.total}
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {achievements.achievements.map(a => (
            <div
              key={a.type}
              className={`flex items-center gap-3 p-3 rounded-xl border transition-colors ${
                a.earned
                  ? 'bg-[#161b22] border-[#e3b341]/30'
                  : 'bg-[#0d1117] border-[#30363d] opacity-40'
              }`}
            >
              <span className="text-2xl">{a.icon}</span>
              <div>
                <div className={`text-sm font-medium ${a.earned ? 'text-[#f0f6fc]' : 'text-[#484f58]'}`}>
                  {a.title}
                </div>
                <div className="text-xs text-[#8b949e]">{a.description}</div>
                {a.earned && a.unlocked_at && (
                  <div className="text-xs text-[#484f58]">
                    {new Date(a.unlocked_at).toLocaleDateString('pl')}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Learning Analytics */}
      {analytics && (
        <div className="space-y-6">
          <h3 className="text-[#f0f6fc] font-semibold mb-4 flex items-center gap-2">
            <BarChart2 size={18} className="text-[#58a6ff]" />
            Analiza nauki
          </h3>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
              <h4 className="text-[#f0f6fc] font-medium mb-3 flex items-center gap-2">
                <AlertTriangle size={16} className="text-[#f85149]" />
                Tematy wymagające uwagi
              </h4>
              {analytics.weakest_topics.length === 0 ? (
                <p className="text-[#8b949e] text-sm">Brak błędów — świetnie!</p>
              ) : (
                <ul className="space-y-2">
                  {analytics.weakest_topics.map(t => (
                    <li key={t.topic_slug} className="flex justify-between text-sm">
                      <span className="text-[#c9d1d9]">#{t.topic_slug}</span>
                      <span className="text-[#f85149]">{t.unresolved_errors} błędów</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
              <h4 className="text-[#f0f6fc] font-medium mb-3 flex items-center gap-2">
                <BookOpen size={16} className="text-[#e3b341]" />
                W toku nauki
              </h4>
              {analytics.in_progress_topics.length === 0 ? (
                <p className="text-[#8b949e] text-sm">Rozpocznij pierwszy temat!</p>
              ) : (
                <ul className="space-y-2">
                  {analytics.in_progress_topics.map(t => (
                    <li key={t.slug} className="text-sm text-[#c9d1d9]">
                      #{t.slug} <span className="text-[#8b949e]">({t.category})</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
            <h4 className="text-[#f0f6fc] font-medium mb-3">Ogólna skuteczność</h4>
            <div className="flex items-center gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-[#39d353]">{analytics.overall_accuracy}%</div>
                <div className="text-xs text-[#8b949e]">Poprawnych odpowiedzi</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-[#58a6ff]">{analytics.total_exercises}</div>
                <div className="text-xs text-[#8b949e]">Rozwiązanych ćwiczeń</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-[#e3b341]">{analytics.correct_exercises}</div>
                <div className="text-xs text-[#8b949e]">Poprawnie</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

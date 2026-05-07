import { useEffect, useState } from 'react'
import { getDueErrors, reviewError, getErrorStats, getUserId } from '../api/client'
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

export default function Errors() {
  const userId = getUserId()
  const [errors, setErrors] = useState([])
  const [stats, setStats] = useState(null)
  const [index, setIndex] = useState(0)
  const [answered, setAnswered] = useState(null) // null | 'correct' | 'wrong'
  const [done, setDone] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getDueErrors(userId), getErrorStats(userId)]).then(([errs, s]) => {
      setErrors(errs)
      setStats(s)
      setLoading(false)
    })
  }, [userId])

  const current = errors[index]

  const handleAnswer = async (correct) => {
    setAnswered(correct ? 'correct' : 'wrong')
    await reviewError(current.id, correct)
    setTimeout(() => {
      const next = index + 1
      if (next >= errors.length) {
        setDone(true)
      } else {
        setIndex(next)
        setAnswered(null)
      }
    }, 1500)
  }

  if (loading) return <div className="p-8 text-[#8b949e] text-center animate-pulse">Ładowanie błędów...</div>

  const ERROR_TYPE_LABELS = {
    no_knowledge: { label: 'Brak wiedzy', color: 'text-[#f85149]' },
    misunderstanding: { label: 'Złe rozumienie', color: 'text-[#e3b341]' },
    guessing: { label: 'Zgadywanie', color: 'text-[#bc8cff]' },
    unknown: { label: 'Błąd', color: 'text-[#8b949e]' },
  }

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-[#f0f6fc] flex items-center gap-2">
          <AlertTriangle size={20} className="text-[#f85149]" />
          Fix My Mistakes
        </h2>
        {stats && (
          <div className="text-[#8b949e] text-sm">
            {stats.resolved}/{stats.total} naprawionych
          </div>
        )}
      </div>

      {errors.length === 0 && (
        <div className="text-center py-12">
          <CheckCircle size={48} className="text-[#39d353] mx-auto mb-4" />
          <h3 className="text-[#f0f6fc] font-bold text-lg mb-2">Brak błędów do przejrzenia!</h3>
          <p className="text-[#8b949e]">Świetna robota. Wróć jutro lub rozwiąż więcej quizów.</p>
        </div>
      )}

      {errors.length > 0 && !done && current && (
        <div>
          <div className="text-[#8b949e] text-sm mb-4">{index + 1} / {errors.length}</div>

          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6 mb-4">
            <div className="flex items-center gap-2 mb-3">
              {current.topic_slug && (
                <span className="text-xs font-mono text-[#58a6ff] bg-[#1f6feb]/10 px-2 py-0.5 rounded">
                  {current.topic_slug}
                </span>
              )}
              {current.error_type && (
                <span className={`text-xs ${ERROR_TYPE_LABELS[current.error_type]?.color}`}>
                  {ERROR_TYPE_LABELS[current.error_type]?.label}
                </span>
              )}
              <span className="text-xs text-[#484f58] ml-auto">
                Streak: {current.correct_streak}/3
              </span>
            </div>

            <p className="text-[#f0f6fc] text-lg mb-4">{current.question}</p>

            {current.explanation && (
              <div className="text-[#8b949e] text-sm border-t border-[#30363d] pt-3">
                <span className="text-[#e3b341]">Poprzednia odpowiedź:</span> {current.user_answer}
                <br />
                <span className="text-[#39d353]">Poprawna:</span> {current.correct_answer}
              </div>
            )}

            {current.explanation && (
              <div className="mt-2 text-[#8b949e] text-sm italic">{current.explanation}</div>
            )}
          </div>

          {answered === null ? (
            <div className="flex gap-3">
              <button
                onClick={() => handleAnswer(false)}
                className="flex-1 flex items-center justify-center gap-2 bg-[#f85149]/10 border border-[#f85149]/30 text-[#f85149] py-3 rounded-lg hover:bg-[#f85149]/20"
              >
                <XCircle size={18} /> Nie pamiętam
              </button>
              <button
                onClick={() => handleAnswer(true)}
                className="flex-1 flex items-center justify-center gap-2 bg-[#39d353]/10 border border-[#39d353]/30 text-[#39d353] py-3 rounded-lg hover:bg-[#39d353]/20"
              >
                <CheckCircle size={18} /> Wiedziałem!
              </button>
            </div>
          ) : (
            <div className={`text-center py-4 rounded-xl ${answered === 'correct' ? 'bg-[#39d353]/10 text-[#39d353]' : 'bg-[#f85149]/10 text-[#f85149]'}`}>
              {answered === 'correct' ? '✅ Dobrze! Tak trzymaj.' : '❌ Wróci za 24 godziny.'}
            </div>
          )}
        </div>
      )}

      {done && (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🎯</div>
          <h3 className="text-[#f0f6fc] font-bold text-lg mb-2">Sesja zakończona!</h3>
          <p className="text-[#8b949e]">Przejrzyłeś {errors.length} błędów. Wróć jutro po następne.</p>
        </div>
      )}
    </div>
  )
}

import { useEffect, useState } from 'react'
import { getAttackScenarios, startAttackScenario, getCurrentStep, submitAttackAnswer } from '../api/client'
import { Skull, Play, ChevronRight, CheckCircle, XCircle, Flag } from 'lucide-react'

export default function AttackScenario() {
  const [scenarios, setScenarios] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [current, setCurrent] = useState(null) // { step, question, total_steps, points_available, completed? }
  const [answer, setAnswer] = useState('')
  const [feedback, setFeedback] = useState(null) // { correct, message, points_earned, completed }
  const [loading, setLoading] = useState(false)

  const userId = localStorage.getItem('hackerlabacademy_user_id') ? parseInt(localStorage.getItem('hackerlabacademy_user_id')) : null

  useEffect(() => {
    loadScenarios()
  }, [])

  const loadScenarios = async () => {
    try {
      const data = await getAttackScenarios()
      setScenarios(data)
      if (data.length > 0 && !selectedId) {
        setSelectedId(data[0].id)
      }
    } catch (e) {
      console.error(e)
    }
  }

  const selectScenario = async (id) => {
    setSelectedId(id)
    setFeedback(null)
    setAnswer('')
    // Start
    setLoading(true)
    try {
      const startRes = await startAttackScenario(id, userId)
      if (startRes.completed) {
        setCurrent({ completed: true, total_points: startRes.total_points })
      } else {
        setCurrent({
          step: startRes.current_step,
          total_steps: startRes.total_steps,
          question: startRes.question,
          points_available: startRes.points_available,
          completed: false
        })
      }
    } catch (e) {
      console.error(e)
      setCurrent(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedId) {
      selectScenario(selectedId)
    }
  }, [selectedId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!answer.trim() || !selectedId) return
    setLoading(true)
    setFeedback(null)
    try {
      const res = await submitAttackAnswer(selectedId, userId, answer.trim())
      setFeedback({
        correct: res.correct,
        message: res.feedback,
        points: res.points_earned,
        completed: res.completed,
        total_points: res.total_points
      })
      if (res.completed) {
        setCurrent(prev => ({ ...prev, completed: true, total_points: res.total_points }))
      } else {
        // Advance to next step
        setCurrent(prev => ({
          ...prev,
          step: res.step_completed + 1,
          // question will be fetched? We could auto-fetch or require manual refresh. Simpler: show message to continue.
        }))
        // Optionally fetch next step immediately; but we need a GET current step endpoint. For now, user clicks "Next" to load next.
      }
    } catch (e) {
      setFeedback({ correct: false, message: e.response?.data?.detail || 'Błąd' })
    } finally {
      setLoading(false)
    }
  }

  const loadNextStep = async () => {
    setLoading(true)
    setFeedback(null)
    try {
      const res = await getCurrentStep(selectedId, userId)
      if (res.completed) {
        setCurrent({ completed: true, total_points: res.total_points })
      } else {
        setCurrent({
          step: res.current_step,
          total_steps: res.total_steps,
          question: res.question,
          points_available: res.points_available,
          completed: false
        })
        setAnswer('')
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-[#f0f6fc] mb-2 flex items-center gap-2">
        <Skull size={24} className="text-[#f85149]" />
        Attack Scenario
      </h1>
      <p className="text-[#8b949e] mb-6">Przepełnij pełny kill chain krok po kroku. Rozwiązuj zadania, zdobywaj punkty.</p>

      <div className="flex gap-2 mb-6">
        <select
          value={selectedId || ''}
          onChange={e => selectScenario(parseInt(e.target.value, 10))}
          className="bg-[#0d1117] border border-[#30363d] rounded px-3 py-2 text-sm text-[#c9d1d9]"
        >
          {scenarios.map(s => (
            <option key={s.id} value={s.id}>{s.title}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="text-center py-8 text-[#8b949e]">Ładowanie...</div>
      ) : current ? (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-bold text-[#f0f6fc]">{scenarios.find(s => s.id === selectedId)?.title}</h2>
              <p className="text-[#8b949e] text-sm">Krok {current.step} z {current.total_steps} • Łącznie punktów: {current.total_points || 0}</p>
            </div>
            {current.completed && (
              <div className="text-[#39d353] font-bold">✅ Ukończono!</div>
            )}
          </div>

          {current.completed ? (
            <div className="text-center py-8">
              <Flag size={48} className="text-[#e3b341] mx-auto mb-4" />
              <p className="text-[#c9d1d9]">Scenariusz ukończony! Zdobyto {current.total_points} punktów.</p>
              <button
                onClick={() => { selectScenario(selectedId) }}
                className="mt-4 px-4 py-2 bg-[#238636] hover:bg-[#2ea043] text-white rounded"
              >
                Rozpocznij ponownie
              </button>
            </div>
          ) : (
            <>
              <p className="text-[#f0f6fc] mb-4">{current.question}</p>

              {feedback ? (
                <div className={`p-4 rounded-lg border ${feedback.correct ? 'bg-[#39d353]/10 border-[#39d353]/30' : 'bg-[#f85149]/10 border-[#f85149]/30'}`}>
                  <div className={`font-bold mb-1 ${feedback.correct ? 'text-[#39d353]' : 'text-[#f85149]'}`}>
                    {feedback.correct ? <><CheckCircle className="inline mr-1" size={18} /> Poprawnie! </> : <><XCircle className="inline mr-1" size={18} /> Niepoprawnie</>}
                  </div>
                  <p className="text-sm text-[#c9d1d9]">{feedback.message}</p>
                  {feedback.points && feedback.points > 0 && (
                    <p className="text-[#e3b341] text-sm mt-1">+{feedback.points} XP</p>
                  )}
                  {feedback.correct && !current.completed && (
                    <button
                      onClick={loadNextStep}
                      disabled={loading}
                      className="mt-4 px-4 py-2 bg-[#58a6ff] hover:bg-[#79c0ff] text-white rounded text-sm"
                    >
                      Następny krok <ChevronRight size={14} className="inline ml-1" />
                    </button>
                  )}
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <textarea
                    value={answer}
                    onChange={e => setAnswer(e.target.value)}
                    placeholder="Wpisz odpowiedź..."
                    className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg p-3 text-[#c9d1d9] focus:outline-none focus:border-[#58a6ff]"
                    rows={4}
                  />
                  <button
                    type="submit"
                    disabled={!answer.trim() || loading}
                    className="px-4 py-2 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white rounded font-medium"
                  >
                    {loading ? 'Sprawdzanie...' : 'Wyślij'}
                  </button>
                </form>
              )}
            </div>
          </>
        )}
        </div>
      ) : (
        <div className="text-[#8b949e]">Wybierz scenariusz ataku</div>
      )}
    </div>
  )
}

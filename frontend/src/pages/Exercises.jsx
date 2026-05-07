import { useEffect, useState } from 'react'
import { getExercises, submitExercise, generateExercises, getUserId } from '../api/client'
import { Loader, CheckCircle, XCircle, ChevronRight, Trophy } from 'lucide-react'

export default function Exercises({ topicId }) {
  const [exercises, setExercises] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentIdx, setCurrentIdx] = useState(0)
  const [userAnswer, setUserAnswer] = useState('')
  const [result, setResult] = useState(null) // {correct, xp_awarded, explanation}
  const [submitting, setSubmitting] = useState(false)
  const [finished, setFinished] = useState(false)
  const [totalXp, setTotalXp] = useState(0)

  useEffect(() => {
    const load = async () => {
      try {
        let data = await getExercises(topicId)
        if (data.length === 0) {
          // Auto-generate exercises if none exist
          try {
            await generateExercises(topicId, 10)
            data = await getExercises(topicId)
          } catch (genErr) {
            console.error('Generate failed', genErr)
          }
        }
        setExercises(data)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [topicId])

  const currentEx = exercises[currentIdx]

  const handleSubmit = async () => {
    if (!userAnswer.trim()) return
    setSubmitting(true)
    try {
      const userId = getUserId()
      const res = await submitExercise(currentEx.id, userId, userAnswer)
      setResult(res)
      setTotalXp(prev => prev + res.xp_awarded)
    } catch (e) {
      alert('Błąd wysyłania odpowiedzi')
    } finally {
      setSubmitting(false)
    }
  }

  const handleNext = () => {
    if (currentIdx + 1 < exercises.length) {
      setCurrentIdx(currentIdx + 1)
      setUserAnswer('')
      setResult(null)
    } else {
      setFinished(true)
    }
  }

  if (loading) return (
    <div className="p-8 flex items-center justify-center text-[#8b949e]">
      <Loader size={20} className="animate-spin mr-2" />
      Ładowanie ćwiczeń...
    </div>
  )

  if (exercises.length === 0) {
    return (
      <div className="p-8 text-center text-[#8b949e]">
        <p>Brak ćwiczeń dla tego tematu.</p>
        <p className="text-sm mt-2">Ćwiczenia są generowane przez AI — spróbuj odświeżyć stronę.</p>
      </div>
    )
  }

  if (finished) {
    return (
      <div className="p-8 text-center">
        <Trophy className="mx-auto mb-4 text-[#e3b341]" size={48} />
        <h2 className="text-2xl font-bold text-[#f0f6fc] mb-2">🎉 Wszystkie ćwiczenia ukończone!</h2>
        <p className="text-[#8b949e] mb-4">Zdobyłeś łącznie <span className="text-[#e3b341] font-bold">+{totalXp} XP</span></p>
        <button
          onClick={() => { setCurrentIdx(0); setUserAnswer(''); setResult(null); setFinished(false); setTotalXp(0); }}
          className="bg-[#238636] hover:bg-[#2ea043] text-white px-6 py-2 rounded-lg"
        >
          Powtórz ćwiczenia
        </button>
      </div>
    )
  }

  const renderQuestion = () => {
    const { exercise_type, question, options, code_snippet } = currentEx
    const optionsList = options ? JSON.parse(options) : []

    return (
      <div className="space-y-6">
        <div>
          <span className="text-xs uppercase text-[#8b949e] font-mono">{exercise_type.replace('_', ' ')}</span>
          <h3 className="text-xl font-semibold text-[#f0f6fc] mt-1">{question}</h3>
        </div>

        {code_snippet && (
          <pre className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4 text-[#39d353] text-sm overflow-x-auto font-mono">
            {code_snippet}
          </pre>
        )}

        {exercise_type === 'quiz_mc' && (
          <div className="space-y-2">
            {optionsList.map((opt, i) => {
              const letter = opt.charAt(0)
              const selected = userAnswer === letter
              return (
                <button
                  key={i}
                  onClick={() => !result && setUserAnswer(letter)}
                  className={`w-full text-left px-4 py-3 rounded-lg text-sm border transition-colors ${
                    selected
                      ? 'border-[#58a6ff] bg-[#1f6feb]/20 text-[#58a6ff]'
                      : 'border-[#30363d] text-[#c9d1d9] hover:bg-[#21262d]'
                  } ${result ? 'cursor-default opacity-70' : ''}`}
                >
                  {opt}
                </button>
              )
            })}
          </div>
        )}

        {(exercise_type === 'fill_blank') && (
          <textarea
            value={userAnswer}
            onChange={e => !result && setUserAnswer(e.target.value)}
            placeholder="Wpisz odpowiedź..."
            className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg p-3 text-[#c9d1d9] text-sm focus:outline-none focus:border-[#58a6ff]"
            rows={3}
            disabled={!!result}
          />
        )}

        {exercise_type === 'code_review' && (
          <div>
            <p className="text-[#8b949e] text-sm mb-2">Która linia zawiera podatność? (np. "3" lub "line:3")</p>
            <input
              type="text"
              value={userAnswer}
              onChange={e => !result && setUserAnswer(e.target.value)}
              placeholder="Np. 3 lub line:3"
              className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg p-3 text-[#c9d1d9] text-sm focus:outline-none focus:border-[#58a6ff]"
              disabled={!!result}
            />
          </div>
        )}

        {exercise_type === 'defense_write' && (
          <div>
            <p className="text-[#8b949e] text-sm mb-2">Napraw ten kod dając bezpieczną wersję poniżej:</p>
            <textarea
              value={userAnswer}
              onChange={e => !result && setUserAnswer(e.target.value)}
              placeholder="Wklej poprawiony kod..."
              className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg p-3 text-[#c9d1d9] text-sm focus:outline-none focus:border-[#58a6ff] font-mono"
              rows={6}
              disabled={!!result}
            />
          </div>
        )}
      </div>
    )
  }

  const renderFeedback = () => {
    if (!result) return null
    const { correct, explanation } = result
    return (
      <div className={`mt-4 p-4 rounded-lg border ${correct ? 'bg-[#39d353]/10 border-[#39d353]/30' : 'bg-[#f85149]/10 border-[#f85149]/30'}`}>
        <div className={`text-lg font-bold mb-2 ${correct ? 'text-[#39d353]' : 'text-[#f85149]'}`}>
          {correct ? <><CheckCircle className="inline mr-2" size={20} />Poprawnie!</> : <><XCircle className="inline mr-2" size={20} />Niepoprawnie</>}
        </div>
        {explanation && <p className="text-[#c9d1d9] text-sm">{explanation}</p>}
        {result.xp_awarded > 0 && (
          <div className="mt-2 text-[#e3b341] text-sm">+{result.xp_awarded} XP</div>
        )}
      </div>
    )
  }

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <div className="mb-4 text-sm text-[#8b949e]">
        Ćwiczenie {currentIdx + 1} z {exercises.length}
      </div>

      {renderQuestion()}

      {!result ? (
        <button
          onClick={handleSubmit}
          disabled={submitting || !userAnswer.trim()}
          className="mt-6 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          {submitting ? 'Sprawdzanie...' : 'Sprawdź odpowiedź'}
        </button>
      ) : (
        <div className="mt-6">
          {renderFeedback()}
          <button
            onClick={handleNext}
            className="mt-4 bg-[#58a6ff] hover:bg-[#79c0ff] text-white px-6 py-2 rounded-lg flex items-center gap-2 ml-auto"
          >
            {currentIdx + 1 < exercises.length ? 'Następne' : 'Zakończ'} <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  )
}

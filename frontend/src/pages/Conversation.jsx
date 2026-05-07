import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { startConversationSession, getNextQuestion, submitAnswer, endConversationSession, listConversationSessions } from '../api/client'
import { getUserId } from '../api/client'
import { Bot, Send, Loader, ChevronRight, Trophy, RotateCcw, CheckCircle, XCircle } from 'lucide-react'

export default function Conversation({ topicSlug: initialTopicSlug }) {
  const { slug: paramSlug } = useParams()
  const navigate = useNavigate()
  const userId = getUserId()
  const topicSlug = initialTopicSlug || paramSlug

  const [sessionId, setSessionId] = useState(null)
  const [question, setQuestion] = useState(null)
  const [userAnswer, setUserAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [feedback, setFeedback] = useState(null) // {correct, message, xp}
  const [sessionState, setSessionState] = useState('init') // init, active, ended
  const [turns, setTurns] = useState([])
  const [totalXp, setTotalXp] = useState(0)
  const [history, setHistory] = useState([])

  // Load history on mount
  useEffect(() => {
    if (userId) {
      listConversationSessions(userId).then(data => setHistory(data))
    }
  }, [userId])

  const startSession = async () => {
    setLoading(true)
    try {
      const res = await startConversationSession(userId, topicSlug)
      setSessionId(res.session_id)
      setSessionState('active')
      setTurns([])
      setTotalXp(0)
      // Get first question
      await fetchQuestion()
    } catch (e) {
      alert('Błąd rozpoczęcia sesji')
    } finally {
      setLoading(false)
    }
  }

  const fetchQuestion = async () => {
    try {
      const q = await getNextQuestion(sessionId)
      setQuestion(q)
      setUserAnswer('')
      setFeedback(null)
    } catch (e) {
      if (e.response?.status === 400) {
        // Max turns reached
        endSession()
      } else {
        alert('Błąd pobierania pytania')
      }
    }
  }

  const handleSubmit = async () => {
    if (!userAnswer.trim()) return
    setLoading(true)
    try {
      const res = await submitAnswer(sessionId, userAnswer)
      setFeedback({
        correct: res.correct,
        message: res.feedback,
        xp: res.xp_awarded,
      })
      if (res.xp_awarded > 0) {
        setTotalXp(prev => prev + res.xp_awarded)
      }
      // Record turn
      setTurns(prev => [...prev, { answer: userAnswer, correct: res.correct }])
    } catch (e) {
      alert('Błąd wysyłania odpowiedzi')
    } finally {
      setLoading(false)
    }
  }

  const nextQuestion = () => {
    fetchQuestion()
  }

  const endSession = async () => {
    try {
      const res = await endConversationSession(sessionId)
      setSessionState('ended')
      setFeedback(null)
      // Refresh history
      listConversationSessions(userId).then(data => setHistory(data))
    } catch (e) {
      alert('Błąd kończenia sesji')
    }
  }

  if (!userId) {
    return <div className="p-8 text-center text-[#8b949e]">Zaloguj się najpierw.</div>
  }

  if (sessionState === 'init') {
    return (
      <div className="p-8 max-w-2xl mx-auto text-center">
        <Bot size={48} className="text-[#58a6ff] mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-[#f0f6fc] mb-2">Ćwiczenia Konwersacyjne</h1>
        <p className="text-[#8b949e] mb-6">
          Rozmowa z AI Mentorem — strukturyzowane sesje Q&A. AI zadaje pytania, ty odpowiadasz, otrzymujesz natychmiastowy feedback i XP.
        </p>
        <button
          onClick={startSession}
          disabled={loading}
          className="bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white px-6 py-3 rounded-lg font-medium"
        >
          {loading ? 'Rozpoczynanie...' : 'Rozpocznij sesję'}
        </button>

        <div className="mt-8 text-left">
          <h2 className="text-[#f0f6fc] font-semibold mb-3">Historia sesji</h2>
          {history.length === 0 ? (
            <p className="text-[#8b949e] text-sm">Brak historii.</p>
          ) : (
            <div className="space-y-2">
              {history.map(s => (
                <div key={s.id} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-[#f0f6fc]">{s.started_at?.split('T')[0]}</span>
                    <span className="text-[#8b949e]">{s.turns_completed} pytań, {s.correct_answers} poprawnych</span>
                    <span className="text-[#e3b341]">+{s.xp_awarded} XP</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  if (sessionState === 'active') {
    return (
      <div className="p-8 max-w-2xl mx-auto">
        <div className="mb-4 flex items-center justify-between">
          <div className="text-sm text-[#8b949e]">
            Sesja aktywna • Tura {turns.length + 1}/5 • Łącznie XP: +{totalXp}
          </div>
          <button onClick={endSession} className="text-xs text-[#f85149] hover:underline">
            Zakończ sesję
          </button>
        </div>

        {question && (
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6 mb-6">
            <div className="flex items-center gap-2 mb-3">
              <Bot size={18} className="text-[#58a6ff]" />
              <span className="text-[#58a6ff] font-medium text-sm">Mentor</span>
              <span className="text-[#8b949e] text-xs">({question.type})</span>
            </div>
            <h2 className="text-xl font-semibold text-[#f0f6fc] mb-4">{question.question}</h2>

            {question.type === 'multiple_choice' && question.options && (
              <div className="space-y-2">
                {question.options.map((opt, i) => {
                  const letter = opt.charAt(0)
                  const selected = userAnswer === letter
                  return (
                    <button
                      key={i}
                      onClick={() => !feedback && setUserAnswer(letter)}
                      className={`w-full text-left px-4 py-3 rounded-lg text-sm border transition-colors ${
                        selected
                          ? 'border-[#58a6ff] bg-[#1f6feb]/20 text-[#58a6ff]'
                          : 'border-[#30363d] text-[#c9d1d9] hover:bg-[#21262d]'
                      } ${feedback ? 'cursor-default opacity-70' : ''}`}
                    >
                      {opt}
                    </button>
                  )
                })}
              </div>
            )}

            {(question.type === 'open_ended' || question.type === 'scenario') && (
              <textarea
                value={userAnswer}
                onChange={e => !feedback && setUserAnswer(e.target.value)}
                placeholder="Wpisz swoją odpowiedź..."
                className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg p-3 text-[#c9d1d9] focus:outline-none focus:border-[#58a6ff]"
                rows={4}
                disabled={!!feedback}
              />
            )}
          </div>
        )}

        {feedback ? (
          <div className="mb-6">
            <div className={`rounded-xl p-4 border ${feedback.correct ? 'bg-[#39d353]/10 border-[#39d353]/30' : 'bg-[#f85149]/10 border-[#f85149]/30'}`}>
              <div className={`font-bold mb-2 ${feedback.correct ? 'text-[#39d353]' : 'text-[#f85149]'}`}>
                {feedback.correct ? <><CheckCircle className="inline mr-2" size={18} />Poprawnie!</> : <><XCircle className="inline mr-2" size={18} />Niepoprawnie</>}
              </div>
              <p className="text-[#c9d1d9] text-sm">{feedback.message}</p>
              {feedback.xp > 0 && (
                <div className="mt-2 text-[#e3b341] text-sm">+{feedback.xp} XP</div>
              )}
            </div>
            <button
              onClick={nextQuestion}
              className="mt-4 bg-[#58a6ff] hover:bg-[#79c0ff] text-white px-6 py-2 rounded-lg flex items-center gap-2 ml-auto"
            >
              Następne pytanie <ChevronRight size={16} />
            </button>
          </div>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={loading || !userAnswer.trim()}
            className="bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white px-6 py-3 rounded-lg font-medium w-full"
          >
            {loading ? 'Sprawdzanie...' : 'Wyślij odpowiedź'}
          </button>
        )}
      </div>
    )
  }

  if (sessionState === 'ended') {
    return (
      <div className="p-8 max-w-2xl mx-auto text-center">
        <Trophy className="mx-auto mb-4 text-[#e3b341]" size={64} />
        <h1 className="text-2xl font-bold text-[#f0f6fc] mb-2">Sesja zakończona!</h1>
        <p className="text-[#8b949e] mb-4">
          Ukończyłeś {turns.length} pytań, poprawnie: {turns.filter(t => t.correct).length}
        </p>
        <p className="text-[#e3b341] text-lg font-bold mb-6">Zdobyte XP: +{totalXp}</p>
        <button
          onClick={startSession}
          className="bg-[#238636] hover:bg-[#2ea043] text-white px-6 py-3 rounded-lg font-medium"
        >
          Rozpocznij nową sesję
        </button>

        <div className="mt-8 text-left">
          <h2 className="text-[#f0f6fc] font-semibold mb-3">Historia sesji</h2>
          {/* render history */}
          {history.slice(0, 5).map(s => (
            <div key={s.id} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 text-sm mb-2">
              <div className="flex justify-between">
                <span className="text-[#f0f6fc]">{s.started_at?.split('T')[0]}</span>
                <span className="text-[#8b949e]">{s.turns_completed} pytań, {s.correct_answers} poprawnych</span>
                <span className="text-[#e3b341]">+{s.xp_awarded} XP</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }
}

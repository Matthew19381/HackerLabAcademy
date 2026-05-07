import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getTheory, submitQuiz, getUserId, downloadLessonPDF, downloadLessonAudio, downloadLessonBundle, triggerDownload } from '../api/client'
import { CheckCircle, XCircle, ChevronRight, Loader, FileText, Volume2, Package } from 'lucide-react'
import Exercises from './Exercises'
import Conversation from './Conversation'

export default function TheoryLesson() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const userId = getUserId()

  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState('theory') // 'theory' | 'quiz' | 'exercises' | 'conversation' | 'result'
  const [answers, setAnswers] = useState({})
  const [questionStartTimes, setQuestionStartTimes] = useState({})
  const [responseTimes, setResponseTimes] = useState({})
  const [result, setResult] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [dlPdf, setDlPdf] = useState(false)
  const [dlAudio, setDlAudio] = useState(false)
  const [dlBundle, setDlBundle] = useState(false)

  useEffect(() => {
    getTheory(slug, userId)
      .then(d => { setData(d); setLoading(false) })
      .catch(e => {
        alert(e.response?.data?.detail || 'Błąd ładowania lekcji')
        navigate('/topics')
      })
  }, [slug, userId])

  // Start timing when quiz tab is opened
  useEffect(() => {
    if (view === 'quiz') {
      const now = Date.now()
      const initial = {}
      const quiz = data?.content?.quiz || []
      quiz.forEach((_, idx) => { initial[String(idx)] = now })
      setQuestionStartTimes(initial)
    }
  }, [view])

  const handleAnswer = (idx, letter) => {
    const elapsed = Date.now() - (questionStartTimes[String(idx)] || Date.now())
    setResponseTimes(prev => ({ ...prev, [String(idx)]: elapsed }))
    setAnswers(prev => ({ ...prev, [String(idx)]: letter }))
  }

  const handleQuizSubmit = async () => {
    setSubmitting(true)
    try {
      const res = await submitQuiz(slug, userId, answers, responseTimes)
      setResult(res)
      setView('result')
    } catch (e) {
      alert('Błąd wysyłania quizu')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDownloadPDF = async () => {
    setDlPdf(true)
    try {
      const res = await downloadLessonPDF(slug)
      triggerDownload(res.data, `${slug}.pdf`)
    } catch {
      alert('Błąd pobierania PDF')
    } finally {
      setDlPdf(false)
    }
  }

  const handleDownloadAudio = async () => {
    setDlAudio(true)
    try {
      const res = await downloadLessonAudio(slug)
      triggerDownload(res.data, `${slug}.mp3`)
    } catch {
      alert('Błąd pobierania audio')
    } finally {
      setDlAudio(false)
    }
  }

  const handleDownloadBundle = async () => {
    setDlBundle(true)
    try {
      const res = await downloadLessonBundle(slug)
      triggerDownload(res.data, `${slug}_lesson.zip`)
    } catch {
      alert('Błąd pobierania pakietu')
    } finally {
      setDlBundle(false)
    }
  }

  if (loading) return (
    <div className="p-8 flex items-center justify-center text-[#8b949e]">
      <Loader size={20} className="animate-spin mr-2" />
      Generowanie lekcji AI...
    </div>
  )

  const { content, topic } = data
  const quiz = content.quiz || []

  return (
    <div className="p-8 max-w-3xl mx-auto">
      {/* Tab bar + download buttons */}
      <div className="flex items-center gap-3 mb-6 flex-wrap">
        <div className="flex gap-1 bg-[#161b22] border border-[#30363d] rounded-lg p-1">
          {['theory', 'quiz', 'exercises', 'conversation'].map(tab => (
            <button
              key={tab}
              onClick={() => setView(tab)}
              className={`px-4 py-1.5 rounded text-sm transition-colors ${
                view === tab
                  ? 'bg-[#21262d] text-[#f0f6fc]'
                  : 'text-[#8b949e] hover:text-[#c9d1d9]'
              }`}
            >
              {tab === 'theory' ? '📖 Teoria' : tab === 'quiz' ? '❓ Quiz' : tab === 'exercises' ? '💪 Ćwiczenia' : '💬 Konwersacja'}
            </button>
          ))}
        </div>

        <button
          onClick={handleDownloadPDF}
          disabled={dlPdf}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm bg-[#161b22] border border-[#30363d] text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d] transition-colors disabled:opacity-50"
        >
          {dlPdf ? <Loader size={14} className="animate-spin" /> : <FileText size={14} />}
          PDF
        </button>

        <button
          onClick={handleDownloadAudio}
          disabled={dlAudio}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm bg-[#161b22] border border-[#30363d] text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d] transition-colors disabled:opacity-50"
        >
          {dlAudio ? <Loader size={14} className="animate-spin" /> : <Volume2 size={14} />}
          Audio
        </button>

        <button
          onClick={handleDownloadBundle}
          disabled={dlBundle}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm bg-[#161b22] border border-[#30363d] text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d] transition-colors disabled:opacity-50"
        >
          {dlBundle ? <Loader size={14} className="animate-spin" /> : <Package size={14} />}
          PDF+Audio
        </button>
      </div>

      {view === 'theory' && (
        <div>
          <h1 className="text-2xl font-bold text-[#f0f6fc] mb-2">{content.title}</h1>
          <p className="text-[#8b949e] mb-6">{content.intro}</p>

          {(content.sections || []).map((s, i) => (
            <div key={i} className="mb-6">
              <h3 className="text-[#f0f6fc] font-semibold text-lg mb-2">{s.heading}</h3>
              <p className="text-[#c9d1d9] leading-relaxed">{s.content}</p>
              {s.code_example && (
                <pre className="mt-3 bg-[#0d1117] border border-[#30363d] rounded-lg p-4 text-[#39d353] text-sm overflow-x-auto font-mono">
                  {s.code_example}
                </pre>
              )}
            </div>
          ))}

          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5 mb-6">
            <h3 className="text-[#f0f6fc] font-semibold mb-3">🛡️ Jak się bronić</h3>
            <p className="text-[#c9d1d9] leading-relaxed">{content.how_to_defend}</p>
          </div>

          <div className="bg-[#161b22] border border-[#e3b341]/30 rounded-xl p-5 mb-6">
            <h3 className="text-[#e3b341] font-semibold mb-2">🌍 Przykład z życia</h3>
            <p className="text-[#c9d1d9]">{content.real_world_example}</p>
          </div>

          {/* Key concepts */}
          <div className="mb-6">
            <h3 className="text-[#f0f6fc] font-semibold mb-3">📌 Kluczowe pojęcia</h3>
            <div className="space-y-2">
              {(content.key_concepts || []).map((kc, i) => (
                <div key={i} className="flex gap-3 bg-[#161b22] border border-[#30363d] rounded-lg p-3">
                  <span className="text-[#58a6ff] font-mono text-sm font-medium w-40 flex-shrink-0">{kc.term}</span>
                  <span className="text-[#8b949e] text-sm">{kc.definition}</span>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => setView('quiz')}
            className="bg-[#238636] hover:bg-[#2ea043] text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            Przejdź do quizu <ChevronRight size={18} />
          </button>
        </div>
      )}

      {view === 'exercises' && (
        <div>
          <Exercises topicId={data.topic.id} />
        </div>
      )}

      {view === 'conversation' && (
        <div>
          <Conversation topicSlug={data.topic.slug} />
        </div>
      )}

      {view === 'quiz' && (
        <div>
          <h2 className="text-xl font-bold text-[#f0f6fc] mb-6">Quiz — {content.title}</h2>
          <div className="space-y-6">
            {quiz.map((q, idx) => (
              <div key={idx} className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
                <p className="text-[#f0f6fc] font-medium mb-3">
                  {idx + 1}. {q.question}
                </p>
                <div className="space-y-2">
                  {(q.options || []).map((opt, oi) => {
                    const letter = opt.charAt(0)
                    const selected = answers[String(idx)] === letter
                    return (
                      <button
                        key={oi}
                        onClick={() => handleAnswer(idx, letter)}
                        className={`w-full text-left px-4 py-2.5 rounded-lg text-sm border transition-colors ${
                          selected
                            ? 'border-[#58a6ff] bg-[#1f6feb]/20 text-[#58a6ff]'
                            : 'border-[#30363d] text-[#c9d1d9] hover:bg-[#21262d]'
                        }`}
                      >
                        {opt}
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={handleQuizSubmit}
            disabled={submitting || Object.keys(answers).length < quiz.length}
            className="mt-6 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            {submitting ? 'Sprawdzanie...' : 'Wyślij odpowiedzi'}
          </button>
        </div>
      )}

      {view === 'result' && result && (
        <div>
          <div className={`rounded-xl p-6 mb-6 ${result.score >= 70 ? 'bg-[#39d353]/10 border border-[#39d353]/30' : 'bg-[#f85149]/10 border border-[#f85149]/30'}`}>
            <div className="text-4xl font-bold mb-1" style={{ color: result.score >= 70 ? '#39d353' : '#f85149' }}>
              {result.score?.toFixed(0)}%
            </div>
            <div className="text-[#8b949e]">
              {result.score >= 70 ? '✅ Temat zaliczony!' : '❌ Potrzebujesz więcej powtórek'}
            </div>
            {result.xp_awarded > 0 && (
              <div className="mt-2 text-[#e3b341] text-sm">+{result.xp_awarded} XP zdobyte</div>
            )}
          </div>

          {result.analysis?.errors?.length > 0 && (
            <div className="mb-6">
              <h3 className="text-[#f0f6fc] font-semibold mb-3">🐛 Błędy do naprawy</h3>
              <div className="space-y-3">
                {result.analysis.errors.map((e, i) => (
                  <div key={i} className="bg-[#161b22] border border-[#f85149]/30 rounded-lg p-4">
                    <div className="text-sm text-[#c9d1d9] mb-1">{e.question}</div>
                    <div className="flex gap-4 text-xs">
                      <span className="text-[#f85149]">Twoja: {e.user_answer}</span>
                      <span className="text-[#39d353]">Poprawna: {e.correct_answer}</span>
                      <span className="text-[#8b949e] capitalize">[{e.error_type?.replace('_', ' ')}]</span>
                    </div>
                    {e.explanation && (
                      <div className="text-xs text-[#8b949e] mt-2 border-t border-[#30363d] pt-2">{e.explanation}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.new_achievements?.length > 0 && (
            <div className="mb-6 bg-[#e3b341]/10 border border-[#e3b341]/30 rounded-xl p-4">
              <h3 className="text-[#e3b341] font-semibold mb-2">🏆 Nowe osiągnięcia!</h3>
              {result.new_achievements.map((a, i) => (
                <div key={i} className="text-sm text-[#c9d1d9]">{a.icon} {a.title} — {a.description}</div>
              ))}
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={() => navigate('/topics')}
              className="bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] px-4 py-2 rounded-lg text-sm"
            >
              ← Wróć do tematów
            </button>
            {topic.lab_type && (
              <button
                onClick={() => navigate('/lab')}
                className="bg-[#238636] hover:bg-[#2ea043] text-white px-4 py-2 rounded-lg text-sm"
              >
                Przejdź do labu →
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

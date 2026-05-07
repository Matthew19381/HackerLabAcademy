import { useEffect, useState } from 'react'
import { getArticles, getArticle, markArticleRead, submitArticleQuiz, getUserId } from '../api/client'
import { BookOpen, Clock, CheckCircle, Award } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

export default function Articles() {
  const userId = getUserId()
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedArticle, setSelectedArticle] = useState(null)
  const [readTimeStart, setReadTimeStart] = useState(null)

  useEffect(() => {
    getArticles().then(data => {
      setArticles(data)
      setLoading(false)
    }).catch(() => {})
  }, [])

  const handleSelectArticle = async (slug) => {
    try {
      const data = await getArticle(slug)
      setSelectedArticle(data)
      setReadTimeStart(Date.now())
    } catch (e) {
      alert('Błąd ładowania artykułu')
    }
  }

  const handleMarkRead = async () => {
    if (!selectedArticle || !readTimeStart) return
    const readTimeSec = Math.round((Date.now() - readTimeStart) / 1000)
    try {
      await markArticleRead(selectedArticle.slug, userId, readTimeSec)
      alert('Artykuł oznaczony jako przeczytany!')
    } catch (e) {
      alert('Błąd zapisu: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleQuizSubmit = async (answers) => {
    try {
      const res = await submitArticleQuiz(selectedArticle.slug, userId, answers)
      alert(`Quiz zakończony!\nWynik: ${res.correct}/${res.total} (${res.score_percent}%)\nXP: ${res.xp_awarded}`)
      // Optionally mark article read if not already
      if (!readTimeStart) {
        await markArticleRead(selectedArticle.slug, userId, 0)
      }
    } catch (e) {
      alert('Błąd quizu: ' + (e.response?.data?.detail || e.message))
    }
  }

  if (loading) return <div className="p-8 text-[#8b949e] animate-pulse">Ładowanie artykułów...</div>

  if (selectedArticle) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <button
          onClick={() => setSelectedArticle(null)}
          className="mb-4 text-[#58a6ff] hover:underline text-sm"
        >
          ← Powrót do listy
        </button>

        <h1 className="text-2xl font-bold text-[#f0f6fc] mb-2">{selectedArticle.title}</h1>
        <div className="flex gap-4 text-sm text-[#8b949e] mb-4">
          <span className="flex items-center gap-1"><Clock size={14} /> {selectedArticle.read_time_minutes} min</span>
          <span className="flex items-center gap-1">📚 Poziom {selectedArticle.difficulty}</span>
          {selectedArticle.topic_slug && (
            <span className="text-[#58a6ff]">#{selectedArticle.topic_slug}</span>
          )}
        </div>

        {/* Read time timer */}
        {readTimeStart && (
          <div className="mb-4 text-sm text-[#8b949e]">
            Czas czytania: {Math.round((Date.now() - readTimeStart) / 1000)} s
          </div>
        )}

        {/* Mark as read button */}
        <div className="mb-6">
          <button
            onClick={handleMarkRead}
            className="flex items-center gap-2 bg-[#238636] hover:bg-[#2ea043] text-white px-4 py-2 rounded-lg text-sm"
          >
            <CheckCircle size={16} /> Oznacz jako przeczytany
          </button>
        </div>

        {/* Article content (Markdown) */}
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6 mb-8 prose prose-invert max-w-none">
          <ReactMarkdown>{selectedArticle.content_md}</ReactMarkdown>
        </div>

        {/* Quiz */}
        {selectedArticle.quiz_questions && selectedArticle.quiz_questions.length > 0 && (
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6">
            <h2 className="text-xl font-bold text-[#f0f6fc] mb-4 flex items-center gap-2">
              <Award size={20} className="text-[#e3b341]" /> Quiz after reading
            </h2>
            <ArticleQuiz
              questions={selectedArticle.quiz_questions}
              onSubmit={handleQuizSubmit}
            />
          </div>
        )}
      </div>
    )
  }

  // List view
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-[#f0f6fc] mb-6 flex items-center gap-2">
        <BookOpen size={24} className="text-[#58a6ff]" /> Artykuły
      </h2>

      {articles.length === 0 ? (
        <p className="text-[#8b949e]">Brak artykułów. Zostań w kontakcie — wkrótce więcej!</p>
      ) : (
        <div className="grid gap-4">
          {articles.map(art => (
            <div
              key={art.id}
              className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 hover:border-[#58a6ff]/50 transition-colors cursor-pointer"
              onClick={() => handleSelectArticle(art.slug)}
            >
              <h3 className="text-[#f0f6fc] font-medium mb-2">{art.title}</h3>
              <div className="flex gap-4 text-sm text-[#8b949e]">
                <span>⏱ {art.read_time_minutes} min</span>
                <span>📚 Poziom {art.difficulty}</span>
                {art.topic_slug && <span className="text-[#58a6ff]">#{art.topic_slug}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function ArticleQuiz({ questions, onSubmit }) {
  const [answers, setAnswers] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const handleAnswer = (qid, idx) => {
    setAnswers(prev => ({ ...prev, [qid]: idx }))
  }

  const handleSubmit = async () => {
    // Check all answered
    if (Object.keys(answers).length < questions.length) {
      alert('Odpowiedz na wszystkie pytania!')
      return
    }
    setSubmitting(true)
    try {
      await onSubmit(answers)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      {questions.map((q, idx) => (
        <div key={q.id} className="border-b border-[#30363d] pb-4 last:border-0">
          <p className="text-[#f0f6fc] font-medium mb-2">
            {idx + 1}. {q.question}
          </p>
          <div className="grid grid-cols-1 gap-2 ml-4">
            {q.options.map((opt, optIdx) => (
              <label
                key={optIdx}
                className={`flex items-center gap-2 p-2 rounded cursor-pointer ${
                  answers[q.id] === optIdx ? 'bg-[#1f6feb]/20 border border-[#1f6feb]/40' : 'bg-[#0d1117] border border-transparent hover:border-[#30363d]'
                }`}
              >
                <input
                  type="radio"
                  name={`q-${q.id}`}
                  checked={answers[q.id] === optIdx}
                  onChange={() => handleAnswer(q.id, optIdx)}
                  className="accent-[#58a6ff]"
                />
                <span className="text-[#c9d1d9] text-sm">{opt}</span>
              </label>
            ))}
          </div>
        </div>
      ))}

      <button
        onClick={handleSubmit}
        disabled={submitting || Object.keys(answers).length < questions.length}
        className="bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white px-6 py-2 rounded-lg text-sm"
      >
        {submitting ? 'Sprawdzanie...' : 'Zakończ quiz'}
      </button>
    </div>
  )
}

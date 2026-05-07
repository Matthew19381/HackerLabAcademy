import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getTopics, getUserId } from '../api/client'
import { Lock, CheckCircle, FlaskConical, BookOpen, ChevronRight } from 'lucide-react'

const CATEGORY_ORDER = ['Fundamentals', 'OWASP Top 10', 'Advanced']
const DIFFICULTY_LABELS = ['', 'Łatwy', 'Podstawowy', 'Średni', 'Trudny', 'Ekspert']
const DIFFICULTY_COLORS = ['', 'text-[#39d353]', 'text-[#58a6ff]', 'text-[#e3b341]', 'text-[#f85149]', 'text-[#bc8cff]']

export default function Topics() {
  const [topics, setTopics] = useState([])
  const [loading, setLoading] = useState(true)
  const userId = getUserId()

  useEffect(() => {
    getTopics(userId).then(data => {
      setTopics(data)
      setLoading(false)
    })
  }, [userId])

  if (loading) return <div className="p-8 text-[#8b949e] text-center animate-pulse">Ładowanie tematów...</div>

  const grouped = CATEGORY_ORDER.reduce((acc, cat) => {
    acc[cat] = topics.filter(t => t.category === cat)
    return acc
  }, {})

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-[#f0f6fc] mb-2">Mapa tematów</h2>
      <p className="text-[#8b949e] mb-8">Odblokuj tematy wykonując poprzednie. Każdy temat: Teoria → Quiz → Lab.</p>

      {CATEGORY_ORDER.map(cat => {
        const catTopics = grouped[cat] || []
        if (!catTopics.length) return null
        return (
          <div key={cat} className="mb-8">
            <h3 className="text-[#8b949e] text-xs font-mono uppercase tracking-widest mb-3">{cat}</h3>
            <div className="space-y-2">
              {catTopics.map(topic => (
                <TopicRow key={topic.slug} topic={topic} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function TopicRow({ topic }) {
  const locked = !topic.unlocked
  const done = topic.theory_completed && topic.lab_completed
  const partialDone = topic.theory_completed && !topic.lab_completed

  return (
    <div className={`bg-[#161b22] border rounded-lg p-4 flex items-center gap-4 transition-colors ${
      locked
        ? 'border-[#30363d] opacity-50 cursor-not-allowed'
        : done
          ? 'border-[#39d353]/40 hover:border-[#39d353]/60'
          : 'border-[#30363d] hover:border-[#58a6ff]/40 cursor-pointer'
    }`}>
      <div className="w-8 flex-shrink-0 text-center">
        {locked ? (
          <Lock size={18} className="text-[#484f58] mx-auto" />
        ) : done ? (
          <CheckCircle size={18} className="text-[#39d353] mx-auto" />
        ) : (
          <div className={`w-4 h-4 rounded-full border-2 mx-auto ${partialDone ? 'border-[#e3b341] bg-[#e3b341]/20' : 'border-[#30363d]'}`} />
        )}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={`font-medium text-sm ${locked ? 'text-[#484f58]' : 'text-[#f0f6fc]'}`}>
            {topic.name}
          </span>
          <span className={`text-xs ${DIFFICULTY_COLORS[topic.difficulty]}`}>
            {DIFFICULTY_LABELS[topic.difficulty]}
          </span>
        </div>
        <p className="text-[#8b949e] text-xs mt-0.5 truncate">{topic.description}</p>
      </div>

      <div className="flex items-center gap-3 flex-shrink-0">
        {topic.theory_completed && (
          <span className="flex items-center gap-1 text-xs text-[#39d353]">
            <BookOpen size={12} /> Teoria
          </span>
        )}
        {topic.lab_completed && (
          <span className="flex items-center gap-1 text-xs text-[#39d353]">
            <FlaskConical size={12} /> Lab
          </span>
        )}
        {topic.quiz_score !== null && (
          <span className="text-xs text-[#8b949e]">{topic.quiz_score?.toFixed(0)}%</span>
        )}
        {!locked && (
          <Link
            to={`/topics/${topic.slug}`}
            className="flex items-center gap-1 text-xs text-[#58a6ff] hover:text-[#79c0ff] px-3 py-1.5 bg-[#1f6feb]/10 rounded-md hover:bg-[#1f6feb]/20 transition-colors"
          >
            {topic.theory_completed ? 'Kontynuuj' : 'Zacznij'}
            <ChevronRight size={12} />
          </Link>
        )}
        {locked && topic.prerequisites.length > 0 && (
          <span className="text-xs text-[#484f58]">Wymaga: {topic.prerequisites.join(', ')}</span>
        )}
      </div>
    </div>
  )
}

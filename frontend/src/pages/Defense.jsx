import { useEffect, useState, useRef } from 'react'
import { getDefenseChallenges, getDefenseChallenge, submitDefenseFix, getUserId } from '../api/client'
import { Shield, Code2, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

const DIFFICULTY_LABELS = ['', 'Easy', 'Medium', 'Hard', 'Expert', 'Insane']

export default function Defense() {
  const userId = getUserId()
  const [challenges, setChallenges] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [selectedChallenge, setSelectedChallenge] = useState(null)
  const [userCode, setUserCode] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null) // {correct, points, feedback, message}
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadChallenges()
  }, [])

  const loadChallenges = async () => {
    try {
      const data = await getDefenseChallenges()
      setChallenges(data)
      if (data.length > 0 && !selectedId) {
        setSelectedId(data[0].id)
        loadChallengeDetail(data[0].id)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const loadChallengeDetail = async (challengeId) => {
    try {
      const data = await getDefenseChallenge(challengeId)
      setSelectedChallenge(data)
      setUserCode('') // reset editor
      setResult(null)
    } catch (e) {
      console.error(e)
    }
  }

  const handleSelect = (e) => {
    const id = parseInt(e.target.value)
    setSelectedId(id)
    loadChallengeDetail(id)
  }

  const handleSubmit = async () => {
    if (!userCode.trim()) return
    setSubmitting(true)
    setResult(null)
    try {
      const res = await submitDefenseFix(selectedId, userId, userCode)
      setResult(res)
    } catch (e) {
      setResult({
        correct: false,
        points: 0,
        message: e.response?.data?.detail || 'Błąd wysyłania rozwiązania',
        feedback: null,
      })
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return (
    <div className="p-8 text-[#8b949e] text-center animate-pulse">
      Ładowanie zadań...
    </div>
  )

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-[#f0f6fc] mb-2 flex items-center gap-2">
        <Shield size={24} className="text-[#39d353]" />
        Defense Mode
      </h1>
      <p className="text-[#8b949e] mb-6">Napraw podatny kod. Twoja poprawka zostanie automatycznie oceniona przez AI.</p>

      <div className="grid grid-cols-3 gap-6">
        {/* Challenge list */}
        <div className="col-span-1 space-y-3">
          <select
            value={selectedId || ''}
            onChange={handleSelect}
            className="w-full bg-[#161b22] border border-[#30363d] rounded px-3 py-2 text-sm text-[#c9d1d9] mb-4"
          >
            {challenges.map(c => (
              <option key={c.id} value={c.id}>{c.title}</option>
            ))}
          </select>

          {challenges.map(c => (
            <div
              key={c.id}
              onClick={() => loadChallengeDetail(c.id)}
              className={`p-3 rounded-lg cursor-pointer border transition-colors ${
                selectedId === c.id
                  ? 'border-[#58a6ff] bg-[#1f6feb]/10'
                  : 'border-[#30363d] bg-[#161b22] hover:border-[#58a6ff]/50'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-sm text-[#f0f6fc]">{c.title}</span>
                <span className={`text-xs px-2 py-0.5 rounded ${c.difficulty <= 2 ? 'bg-[#39d353]/20 text-[#39d353]' : c.difficulty <= 3 ? 'bg-[#e3b341]/20 text-[#e3b341]' : 'bg-[#f85149]/20 text-[#f85149]'}`}>
                  {DIFFICULTY_LABELS[c.difficulty]}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs text-[#8b949e]">
                <Code2 size={12} /> {c.topic_slug} • {c.points} pts
              </div>
            </div>
          ))}
        </div>

        {/* Challenge detail + editor */}
        <div className="col-span-2">
          {selectedChallenge ? (
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6">
              <h2 className="text-xl font-bold text-[#f0f6fc] mb-2">{selectedChallenge.title}</h2>
              <div className="flex items-center gap-3 mb-4">
                <span className={`text-xs px-2 py-1 rounded border ${selectedChallenge.difficulty <= 2 ? 'border-[#39d353]/30 text-[#39d353]' : selectedChallenge.difficulty <= 3 ? 'border-[#e3b341]/30 text-[#e3b341]' : 'border-[#f85149]/30 text-[#f85149]'}`}>
                  {DIFFICULTY_LABELS[selectedChallenge.difficulty]}
                </span>
                <span className="text-xs text-[#8b949e]">Topic: {selectedChallenge.topic_slug}</span>
                <span className="text-xs text-[#e3b341]">{selectedChallenge.points} points</span>
              </div>

              <p className="text-[#c9d1d9] mb-4">{selectedChallenge.description}</p>

              <div className="mb-4">
                <label className="block text-sm font-medium text-[#8b949e] mb-2">Vulnerable Code (do not edit):</label>
                <pre className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4 text-sm text-[#f85149] overflow-x-auto font-mono">
                  {selectedChallenge.vulnerable_code}
                </pre>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-[#8b949e] mb-2">Your Fixed Code:</label>
                <textarea
                  value={userCode}
                  onChange={(e) => setUserCode(e.target.value)}
                  placeholder="// Write your fixed code here..."
                  className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg p-4 text-sm text-[#c9d1d9] font-mono min-h-[200px] focus:outline-none focus:border-[#58a6ff]"
                  disabled={submitting}
                />
              </div>

              <button
                onClick={handleSubmit}
                disabled={submitting || !userCode.trim()}
                className="px-6 py-2.5 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white rounded-lg font-medium"
              >
                {submitting ? 'Evaluating...' : 'Submit Fix'}
              </button>

              {result && (
                <div className={`mt-4 p-4 rounded-lg border ${result.correct ? 'bg-[#39d353]/10 border-[#39d353]/30' : 'bg-[#f85149]/10 border-[#f85149]/30'}`}>
                  <div className={`font-bold mb-1 flex items-center gap-2 ${result.correct ? 'text-[#39d353]' : 'text-[#f85149]'}`}>
                    {result.correct ? <><CheckCircle size={18} /> Poprawnie! 🎉</> : <><XCircle size={18} /> Nie całkowo poprawnie</>}
                  </div>
                  <div className="text-sm text-[#c9d1d9] mb-1">{result.message}</div>
                  {result.feedback && (
                    <div className="text-xs text-[#8b949e] mt-2">
                      <AlertCircle size={12} className="inline mr-1" />
                      {result.feedback}
                    </div>
                  )}
                  {result.points && result.points > 0 && (
                    <div className="mt-1 text-[#e3b341] font-mono">+{result.points} XP</div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-8 text-center text-[#8b949e]">
              Wybierz zadanie z listy
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

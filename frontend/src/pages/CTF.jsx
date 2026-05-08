import { useEffect, useState } from 'react'
import { getCtfChallenges, submitFlag, getLeaderboard, getUserId } from '../api/client'
import { Flag, Trophy, AlertCircle, CheckCircle, XCircle, Code2, Loader } from 'lucide-react'

const CATEGORIES = ['web', 'forensics', 'crypto', 'pwn', 'reversing']
const DIFFICULTY_LABELS = ['', 'Easy', 'Medium', 'Hard', 'Expert', 'Insane']

export default function CTF() {
  const userId = getUserId()
  const [challenges, setChallenges] = useState([])
  const [selected, setSelected] = useState(null)
  const [flagInput, setFlagInput] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [leaderboard, setLeaderboard] = useState([])
  const [activeTab, setActiveTab] = useState('challenges')

  useEffect(() => {
    loadChallenges()
    loadLeaderboard()
  }, [])

  const loadChallenges = async () => {
    try {
      const data = await getCtfChallenges()
      setChallenges(data)
      if (data.length > 0 && !selected) {
        setSelected(data[0].id)
      }
    } catch (e) {
      console.error(e)
    }
  }

  const loadLeaderboard = async () => {
    try {
      const data = await getLeaderboard()
      setLeaderboard(data)
    } catch (e) {
      console.error(e)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!flagInput.trim() || !selected) return

    setSubmitting(true)
    try {
      const res = await submitFlag(selected, flagInput.trim())
      setResult(res)
    } catch (e) {
      console.error(e)
    } finally {
      setSubmitting(false)
    }
  }

  const currentChallenge = challenges.find(c => c.id === selected)

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#c9d1d9] p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-[#f0f6fc] mb-6 flex items-center gap-2">
          <Flag /> CTF Challenges
        </h1>

        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab('challenges')}
            className={`px-4 py-2 rounded-lg ${activeTab === 'challenges' ? 'bg-[#238636] text-white' : 'bg-[#21262d] text-[#8b949e] hover:text-[#c9d1d9]'}`}
          >
            Challenges
          </button>
          <button
            onClick={() => setActiveTab('leaderboard')}
            className={`px-4 py-2 rounded-lg ${activeTab === 'leaderboard' ? 'bg-[#238636] text-white' : 'bg-[#21262d] text-[#8b949e] hover:text-[#c9d1d9]'}`}
          >
            <Trophy className="inline mr-1" size={16} /> Leaderboard
          </button>
        </div>

        {activeTab === 'challenges' ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1">
              <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
                <h3 className="text-[#f0f6fc] font-bold mb-3">Challenges</h3>
                <div className="space-y-2">
                  {challenges.map(c => (
                    <button
                      key={c.id}
                      onClick={() => { setSelected(c.id); setResult(null) }}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm ${selected === c.id ? 'bg-[#1f6feb]/20 border border-[#58a6ff]' : 'bg-[#21262d] hover:bg-[#30363d] border border-transparent'}`}
                    >
                      <div className="font-medium text-[#f0f6fc]">{c.title}</div>
                      <div className="text-xs text-[#8b949e]">{DIFFICULTY_LABELS[c.difficulty]} • {c.points} pts</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="md:col-span-2">
              {currentChallenge ? (
                <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6">
                  <h2 className="text-xl font-bold text-[#f0f6fc] mb-2">{currentChallenge.title}</h2>
                  <div className="flex gap-2 mb-4">
                    <span className="px-2 py-1 bg-[#21262d] rounded text-xs text-[#8b949e]">{DIFFICULTY_LABELS[currentChallenge.difficulty]}</span>
                    <span className="px-2 py-1 bg-[#21262d] rounded text-xs text-[#8b949e]">{currentChallenge.points} pts</span>
                    <span className="px-2 py-1 bg-[#21262d] rounded text-xs text-[#8b949e]">{currentChallenge.category}</span>
                  </div>

                  <div className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4 mb-4">
                    <p className="text-[#c9d1d9] whitespace-pre-wrap">{currentChallenge.description}</p>
                  </div>

                  {currentChallenge.hint && (
                    <details className="mb-4">
                      <summary className="cursor-pointer text-[#8b949e] hover:text-[#c9d1d9] text-sm">Need a hint?</summary>
                      <div className="mt-2 p-3 bg-[#0d1117] border border-[#30363d] rounded text-sm text-[#c9d1d9]">
                        {currentChallenge.hint}
                      </div>
                    </details>
                  )}

                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <label className="block text-sm text-[#8b949e] mb-1">Enter flag (format: FLAG[...])</label>
                      <input
                        type="text"
                        value={flagInput}
                        onChange={e => setFlagInput(e.target.value)}
                        placeholder="FLAG[...]"
                        className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-[#f0f6fc] focus:outline-none focus:border-[#58a6ff]"
                        disabled={submitting}
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={submitting || !flagInput.trim()}
                      className="px-6 py-2.5 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white rounded-lg font-medium"
                    >
                      {submitting ? 'Checking...' : 'Submit Flag'}
                    </button>
                  </form>

                  {result && (
                    <div className={`mt-4 p-4 rounded-lg border ${result.success ? 'bg-[#39d353]/10 border-[#39d353]/30' : 'bg-[#f85149]/10 border-[#f85149]/30'}`}>
                      <div className={`font-bold mb-1 ${result.success ? 'text-[#39d353]' : 'text-[#f85149]'}`}>
                        {result.success ? <><CheckCircle className="inline mr-1" size={18} /> Correct!</> : <><XCircle className="inline mr-1" size={18} /> Wrong!</>}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-[#8b949e]">Select a challenge</div>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6">
            <h2 className="text-xl font-bold text-[#f0f6fc] mb-4">Leaderboard</h2>
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#30363d]">
                  <th className="text-left py-2">Rank</th>
                  <th className="text-left py-2">User</th>
                  <th className="text-right py-2">Points</th>
                  <th className="text-right py-2">Solved</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((row, idx) => (
                  <tr key={row.user_id} className="border-b border-[#21262d] last:border-0">
                    <td className="py-2 text-[#f0f6fc]">{idx + 1}</td>
                    <td className="py-2 text-[#f0f6fc]">{row.name}</td>
                    <td className="py-2 text-right text-[#e3b341] font-mono">{row.ctf_points}</td>
                    <td className="py-2 text-right text-[#8b949e]">{row.challenges_solved}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

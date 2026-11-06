import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { CheckCircle, Flag, Lightbulb, Loader, XCircle } from 'lucide-react'
import { getCtfChallenges, getUserId, submitCtfFlag, takeCtfHint } from '../api/client'

// CTF restored 2026-11-03 (decision of 2026-08-09: puzzles stay, no leaderboard). Every flag follows
// from the challenge text; a hint halves the points - the page says so before you take it.
const DIFFICULTY = ['', 'łatwe', 'średnie', 'trudne', 'bardzo trudne', 'ekspert']

export default function CTF() {
  const userId = getUserId()
  const [challenges, setChallenges] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [flag, setFlag] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const load = () =>
    getCtfChallenges(userId)
      .then(data => {
        setChallenges(data)
        setSelectedId(current => current ?? data.find(c => !c.solved)?.id ?? data[0]?.id ?? null)
      })
      .catch(() => setError('Nie udało się wczytać zadań.'))

  useEffect(() => {
    load()
  // eslint-disable-next-line react-hooks/exhaustive-deps -- load once per user
  }, [userId])

  const current = challenges.find(c => c.id === selectedId)
  const solvedCount = challenges.filter(c => c.solved).length
  const myPoints = challenges.reduce((sum, c) => sum + (c.points_earned || 0), 0)

  const select = (id) => {
    setSelectedId(id)
    setFlag('')
    setResult(null)
  }

  const submit = async (e) => {
    e.preventDefault()
    if (!flag.trim() || !current) return
    setBusy(true)
    try {
      setResult(await submitCtfFlag(current.id, userId, flag.trim()))
      load()
    } catch {
      setResult({ correct: false, message: 'Nie udało się wysłać flagi.' })
    } finally {
      setBusy(false)
    }
  }

  const hint = async () => {
    await takeCtfHint(current.id, userId)
    load()
  }

  return (
    <div className="p-4 sm:p-8 max-w-5xl mx-auto">
      <h2 className="text-2xl font-bold text-[#f0f6fc] mb-1 flex items-center gap-2">
        <Flag size={24} className="text-[#f85149]" /> CTF
      </h2>
      <p className="text-[#8b949e] text-sm mb-6">
        Znajdź flagę w treści zadania (format <code>FLAG{'{...}'}</code>). Rozwiązane: {solvedCount}/{challenges.length} · Twoje punkty: {myPoints}
      </p>
      {error && <p className="text-[#f85149] text-sm mb-4">{error}</p>}

      <div className="grid grid-cols-1 md:grid-cols-[260px_1fr] gap-4">
        <ul className="space-y-2">
          {challenges.map(c => (
            <li key={c.id}>
              <button
                onClick={() => select(c.id)}
                className={`w-full text-left rounded-lg border px-3 py-2 text-sm ${c.id === selectedId
                  ? 'border-[#58a6ff] bg-[#1f6feb]/10' : 'border-[#30363d] bg-[#161b22] hover:bg-[#21262d]'}`}
              >
                <div className="flex items-center gap-2 text-[#c9d1d9]">
                  {c.solved ? <CheckCircle size={14} className="text-[#39d353]" /> : <Flag size={14} className="text-[#8b949e]" />}
                  {c.title}
                </div>
                <div className="text-xs text-[#8b949e] mt-0.5">{c.category} · {DIFFICULTY[c.difficulty]} · {c.points} pkt</div>
              </button>
            </li>
          ))}
        </ul>

        {current && (
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
            <h3 className="text-lg font-semibold text-[#f0f6fc] mb-3">{current.title}</h3>
            <div className="prose prose-invert prose-sm max-w-none text-[#c9d1d9] mb-4 break-words">
              <ReactMarkdown>{current.description}</ReactMarkdown>
            </div>

            {current.hint ? (
              <p className="text-sm text-[#e3b341] bg-[#e3b341]/10 border border-[#e3b341]/30 rounded-lg p-3 mb-4">
                <Lightbulb size={14} className="inline mr-1" /> {current.hint}
              </p>
            ) : current.has_hint && !current.solved && (
              <button onClick={hint} className="text-sm text-[#e3b341] mb-4 flex items-center gap-1">
                <Lightbulb size={14} /> Pokaż podpowiedź (za rozwiązanie dostaniesz połowę punktów)
              </button>
            )}

            {current.solved ? (
              <div className="text-sm bg-[#39d353]/10 border border-[#39d353]/30 rounded-lg p-3 text-[#c9d1d9]">
                <p className="text-[#39d353] font-medium mb-1">Rozwiązane (+{current.points_earned} pkt)</p>
                {current.solution}
              </div>
            ) : (
              <form onSubmit={submit} className="flex gap-2">
                <input
                  value={flag}
                  onChange={e => setFlag(e.target.value)}
                  placeholder="FLAG{...}"
                  aria-label="Flaga"
                  className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-[#c9d1d9] font-mono"
                />
                <button type="submit" disabled={busy} className="bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white rounded-lg px-4 py-2 text-sm">
                  {busy ? <Loader size={14} className="animate-spin" /> : 'Sprawdź'}
                </button>
              </form>
            )}
            {result && !current.solved && !result.correct && (
              <p className="mt-3 text-sm text-[#f85149] flex items-center gap-1"><XCircle size={14} /> {result.message}</p>
            )}
            {result?.correct && <p className="mt-3 text-sm text-[#39d353]">{result.message}</p>}
          </div>
        )}
      </div>
    </div>
  )
}

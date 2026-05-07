import { useEffect, useState } from 'react'
import { getDueFlashcards, reviewFlashcard, getUserId, downloadAnki, triggerDownload, quickCreateFlashcard } from '../api/client'
import { CreditCard, Eye, EyeOff, Download, Volume2 } from 'lucide-react'

export default function Flashcards() {
  const userId = getUserId()
  const [cards, setCards] = useState([])
  const [index, setIndex] = useState(0)
  const [revealed, setRevealed] = useState(false)
  const [done, setDone] = useState(false)
  const [loading, setLoading] = useState(true)
  const [sessionStats, setSessionStats] = useState({ easy: 0, good: 0, hard: 0, again: 0 })
  const [downloading, setDownloading] = useState(false)
  // Quick add state
  const [quickTerm, setQuickTerm] = useState('')
  const [quickLoading, setQuickLoading] = useState(false)

  useEffect(() => {
    getDueFlashcards(userId).then(data => {
      setCards(data)
      setLoading(false)
    })
  }, [userId])

  const current = cards[index]

  const handleRate = async (rating) => {
    const labels = { 4: 'easy', 3: 'good', 2: 'hard', 1: 'again' }
    setSessionStats(s => ({ ...s, [labels[rating]]: s[labels[rating]] + 1 }))
    await reviewFlashcard(current.id, rating)
    const next = index + 1
    if (next >= cards.length) {
      setDone(true)
    } else {
      setIndex(next)
      setRevealed(false)
    }
  }

  const handleQuickAdd = async () => {
    if (!quickTerm.trim()) return
    setQuickLoading(true)
    try {
      await quickCreateFlashcard(userId, quickTerm.trim())
      alert('Fiszka dodana!')
      setQuickTerm('')
      // Optionally refresh due cards count?
      // Could re-fetch due cards to update count, but not critical
    } catch (e) {
      alert('Błąd dodawania fiszki: ' + (e.response?.data?.detail || e.message))
    } finally {
      setQuickLoading(false)
    }
  }

  const handleDownloadAnki = async () => {
    setDownloading(true)
    try {
      const res = await downloadAnki(userId)
      triggerDownload(res.data, 'hackerlabacademy_flashcards.apkg')
    } catch (e) {
      alert(e.response?.data?.detail || 'Błąd eksportu Anki')
    } finally {
      setDownloading(false)
    }
  }

  if (loading) return <div className="p-8 text-[#8b949e] text-center animate-pulse">Ładowanie fiszek...</div>

  if (cards.length === 0) return (
    <div className="p-8 max-w-2xl mx-auto text-center">
      <CreditCard size={48} className="text-[#8b949e] mx-auto mb-4" />
      <h2 className="text-xl font-bold text-[#f0f6fc] mb-2">Brak fiszek do powtórki</h2>
      <p className="text-[#8b949e]">Ukończ quiz po lekcji, żeby automatycznie dodać fiszki.</p>
    </div>
  )

  if (done) return (
    <div className="p-8 max-w-2xl mx-auto text-center">
      <div className="text-5xl mb-4">🎉</div>
      <h2 className="text-xl font-bold text-[#f0f6fc] mb-2">Sesja ukończona!</h2>
      <p className="text-[#8b949e] mb-6">Powtórzyłeś {cards.length} fiszek</p>
      <div className="grid grid-cols-4 gap-3 mb-6">
        {[
          { label: 'Łatwe', count: sessionStats.easy, color: 'text-[#39d353]' },
          { label: 'Dobre', count: sessionStats.good, color: 'text-[#58a6ff]' },
          { label: 'Trudne', count: sessionStats.hard, color: 'text-[#e3b341]' },
          { label: 'Znowu', count: sessionStats.again, color: 'text-[#f85149]' },
        ].map(s => (
          <div key={s.label} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 text-center">
            <div className={`text-2xl font-bold ${s.color}`}>{s.count}</div>
            <div className="text-[#8b949e] text-xs">{s.label}</div>
          </div>
        ))}
      </div>
      <button
        onClick={() => { setDone(false); setIndex(0); setRevealed(false) }}
        className="bg-[#238636] hover:bg-[#2ea043] text-white px-6 py-2 rounded-lg text-sm"
      >
        Zacznij od nowa
      </button>
    </div>
  )

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-[#f0f6fc] flex items-center gap-2">
          <CreditCard size={20} className="text-[#e3b341]" />
          Fiszki
        </h2>
        <div className="flex items-center gap-3">
          <button
            onClick={handleDownloadAnki}
            disabled={downloading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs bg-[#161b22] border border-[#30363d] text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d] transition-colors disabled:opacity-50"
          >
            {downloading ? 'Eksport...' : <><Download size={12} /> Anki</>}
          </button>
          <span className="text-[#8b949e] text-sm">{index + 1} / {cards.length}</span>
        </div>
      </div>

      {/* Quick Add Flashcard */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={quickTerm}
            onChange={e => setQuickTerm(e.target.value)}
            placeholder="Dodaj nowy termin..."
            className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-[#c9d1d9] focus:outline-none focus:border-[#58a6ff]"
            onKeyDown={e => e.key === 'Enter' && !quickLoading && handleQuickAdd()}
          />
          <button
            onClick={handleQuickAdd}
            disabled={!quickTerm.trim() || quickLoading}
            className="px-4 py-2 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white rounded-lg text-sm"
          >
            {quickLoading ? 'Dodaj...' : 'Dodaj fiszkę'}
          </button>
        </div>
        <p className="text-[#8b949e] text-xs mt-2">AI automatycznie wygeneruje definicję i przykład.</p>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-[#30363d] rounded-full h-1 mb-6">
        <div
          className="bg-[#e3b341] h-1 rounded-full transition-all"
          style={{ width: `${(index / cards.length) * 100}%` }}
        />
      </div>

      {/* Card */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-8 mb-4 min-h-[200px] flex flex-col justify-center">
        {current.topic_slug && (
          <div className="text-xs text-[#58a6ff] font-mono mb-4 uppercase tracking-wide">{current.topic_slug}</div>
        )}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-[#f0f6fc] text-lg font-medium flex-1">{current.front}</span>
          <button
            onClick={() => {
              const audio = new Audio(`/api/download/flashcard/${current.id}/audio`);
              audio.play().catch(e => console.error('Audio play failed:', e));
            }}
            className="p-1.5 rounded-lg bg-[#161b22] border border-[#30363d] text-[#58a6ff] hover:bg-[#21262d] transition-colors"
            title="Odtwórz wymowę"
          >
            <Volume2 size={16} />
          </button>
        </div>

        {!revealed ? (
          <button
            onClick={() => setRevealed(true)}
            className="flex items-center gap-2 text-[#58a6ff] text-sm hover:text-[#79c0ff] mx-auto"
          >
            <Eye size={16} /> Pokaż odpowiedź
          </button>
        ) : (
          <div>
            <div className="border-t border-[#30363d] pt-4">
              <div className="text-[#39d353] text-base">{current.back}</div>
              {current.example && (
                <pre className="mt-3 bg-[#0d1117] border border-[#30363d] rounded p-3 text-[#e3b341] text-sm font-mono overflow-x-auto">
                  {current.example}
                </pre>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Rating buttons */}
      {revealed && (
        <div className="grid grid-cols-4 gap-2">
          {[
            { rating: 1, label: '1\nZnowu', color: 'border-[#f85149]/50 text-[#f85149] hover:bg-[#f85149]/10' },
            { rating: 2, label: '2\nTrudne', color: 'border-[#e3b341]/50 text-[#e3b341] hover:bg-[#e3b341]/10' },
            { rating: 3, label: '3\nDobre', color: 'border-[#58a6ff]/50 text-[#58a6ff] hover:bg-[#58a6ff]/10' },
            { rating: 4, label: '4\nŁatwe', color: 'border-[#39d353]/50 text-[#39d353] hover:bg-[#39d353]/10' },
          ].map(({ rating, label, color }) => (
            <button
              key={rating}
              onClick={() => handleRate(rating)}
              className={`border rounded-lg py-3 text-sm font-medium whitespace-pre-line transition-colors ${color}`}
            >
              {label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

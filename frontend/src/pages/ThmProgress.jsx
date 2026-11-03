import { useEffect, useState } from 'react'
import { CheckCircle, Circle, ExternalLink, Loader, Plus, Sparkles, Trash2, Target } from 'lucide-react'
import {
  getUserId, getThmEntries, createThmEntry, updateThmEntry, deleteThmEntry, flashcardsFromNotes,
} from '../api/client'

// Plan C4 (2026-11-03): TryHackMe has no public progress API - rooms and paths are entered by hand.
// Done / not done only, no XP and no ranking (decision 2 of 2026-08-09).
const EMPTY = { name: '', kind: 'room', category: '', url: '' }
const MIN_NOTES = 20

const cardsWord = (n) => {
  if (n === 1) return 'fiszkę'
  const last = n % 10, lastTwo = n % 100
  return last >= 2 && last <= 4 && (lastTwo < 12 || lastTwo > 14) ? 'fiszki' : 'fiszek'
}

function EntryCard({ entry, onChange, onDelete }) {
  const [notes, setNotes] = useState(entry.notes || '')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState(null)

  const saveNotes = () => {
    if ((entry.notes || '') !== notes) onChange(entry.id, { notes })
  }

  const makeCards = async () => {
    setBusy(true)
    setMessage(null)
    try {
      if ((entry.notes || '') !== notes) await onChange(entry.id, { notes })
      const res = await flashcardsFromNotes(getUserId(), entry.name, notes)
      setMessage(`Dodano ${res.created} ${cardsWord(res.created)} do powtórek.`)
    } catch {
      setMessage('Nie udało się zrobić fiszek — spróbuj ponownie za chwilę.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
      <div className="flex items-start gap-3">
        <button
          onClick={() => onChange(entry.id, { done: !entry.done })}
          aria-label={entry.done ? 'Oznacz jako niezrobione' : 'Oznacz jako zrobione'}
          className={entry.done ? 'text-[#39d353]' : 'text-[#8b949e] hover:text-[#c9d1d9]'}
        >
          {entry.done ? <CheckCircle size={20} /> : <Circle size={20} />}
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`font-medium ${entry.done ? 'text-[#8b949e]' : 'text-[#f0f6fc]'}`}>{entry.name}</span>
            <span className="text-xs px-2 py-0.5 rounded bg-[#21262d] text-[#8b949e]">
              {entry.kind === 'path' ? 'ścieżka' : 'pokój'}
            </span>
            {entry.category && <span className="text-xs text-[#8b949e]">{entry.category}</span>}
            {entry.url && (
              <a href={entry.url} target="_blank" rel="noopener noreferrer" className="text-[#58a6ff]" aria-label="Otwórz na TryHackMe">
                <ExternalLink size={14} />
              </a>
            )}
          </div>
          {entry.completed_at && (
            <div className="text-xs text-[#8b949e] mt-0.5">
              ukończone {new Date(entry.completed_at).toLocaleDateString('pl-PL')}
            </div>
          )}
          <textarea
            value={notes}
            onChange={e => setNotes(e.target.value)}
            onBlur={saveNotes}
            placeholder="Notatki: komendy, flagi, co zadziałało, co było nowe…"
            rows={3}
            className="mt-3 w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-[#c9d1d9] placeholder-[#484f58] text-sm focus:outline-none focus:border-[#58a6ff] resize-y"
          />
          <div className="flex items-center gap-3 mt-2">
            <button
              onClick={makeCards}
              disabled={busy || notes.trim().length < MIN_NOTES}
              className="flex items-center gap-1.5 text-sm text-[#bc8cff] disabled:opacity-40"
              title={notes.trim().length < MIN_NOTES ? 'Najpierw zapisz notatki (min. 20 znaków)' : ''}
            >
              {busy ? <Loader size={14} className="animate-spin" /> : <Sparkles size={14} />}
              Zrób fiszki z notatek
            </button>
            {message && <span className="text-xs text-[#8b949e]">{message}</span>}
          </div>
        </div>
        <button onClick={() => onDelete(entry.id)} aria-label="Usuń wpis" className="text-[#8b949e] hover:text-[#f85149]">
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  )
}

export default function ThmProgress() {
  const userId = getUserId()
  const [entries, setEntries] = useState([])
  const [counts, setCounts] = useState({ done: 0, todo: 0 })
  const [form, setForm] = useState(EMPTY)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = () =>
    getThmEntries(userId)
      .then(data => { setEntries(data.entries); setCounts(data.counts) })
      .catch(() => setError('Nie udało się wczytać listy.'))
      .finally(() => setLoading(false))

  useEffect(() => {
    load()
  // eslint-disable-next-line react-hooks/exhaustive-deps -- load once per user
  }, [userId])

  const add = async (e) => {
    e.preventDefault()
    if (!form.name.trim()) return
    await createThmEntry({
      user_id: userId,
      kind: form.kind,
      name: form.name.trim(),
      category: form.category.trim() || null,
      url: form.url.trim() || null,
    })
    setForm(EMPTY)
    load()
  }

  const change = async (id, data) => {
    await updateThmEntry(id, data)
    load()
  }

  const remove = async (id) => {
    await deleteThmEntry(id)
    load()
  }

  if (loading) return <div className="p-8 text-[#8b949e] text-center animate-pulse">Ładowanie…</div>

  return (
    <div className="p-4 sm:p-8 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold text-[#f0f6fc] mb-1 flex items-center gap-2">
        <Target size={24} className="text-[#39d353]" /> TryHackMe
      </h2>
      <p className="text-[#8b949e] mb-6 text-sm">
        Pokoje i ścieżki, które robisz. Zapisz notatki po pokoju — z nich zrobisz fiszki do powtórek.
        Zrobione: {counts.done} · do zrobienia: {counts.todo}
      </p>

      {error && <p className="text-[#f85149] text-sm mb-4">{error}</p>}

      <form onSubmit={add} className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 mb-6 grid grid-cols-1 sm:grid-cols-6 gap-2">
        <input
          value={form.name}
          onChange={e => setForm({ ...form, name: e.target.value })}
          placeholder="Nazwa pokoju lub ścieżki"
          aria-label="Nazwa"
          className="sm:col-span-3 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-[#c9d1d9]"
        />
        <select
          value={form.kind}
          onChange={e => setForm({ ...form, kind: e.target.value })}
          aria-label="Rodzaj"
          className="bg-[#0d1117] border border-[#30363d] rounded-lg px-2 py-2 text-sm text-[#c9d1d9]"
        >
          <option value="room">pokój</option>
          <option value="path">ścieżka</option>
        </select>
        <input
          value={form.category}
          onChange={e => setForm({ ...form, category: e.target.value })}
          placeholder="Kategoria"
          aria-label="Kategoria"
          className="sm:col-span-2 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-[#c9d1d9]"
        />
        <input
          value={form.url}
          onChange={e => setForm({ ...form, url: e.target.value })}
          placeholder="Link (opcjonalnie)"
          aria-label="Link"
          className="sm:col-span-5 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-[#c9d1d9]"
        />
        <button type="submit" className="flex items-center justify-center gap-1 bg-[#238636] hover:bg-[#2ea043] text-white rounded-lg px-3 py-2 text-sm">
          <Plus size={14} /> Dodaj
        </button>
      </form>

      {entries.length === 0 ? (
        <p className="text-[#8b949e] text-sm">Nie masz jeszcze wpisów. Dodaj pokój, który właśnie robisz.</p>
      ) : (
        <div className="space-y-3">
          {entries.map(entry => (
            <EntryCard key={`${entry.id}-${entry.done}`} entry={entry} onChange={change} onDelete={remove} />
          ))}
        </div>
      )}
    </div>
  )
}

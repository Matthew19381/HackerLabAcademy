import { useEffect, useState } from 'react'
import { getCtfChallenges, submitFlag, getLeaderboard, getUserId, getWriteupTemplates, generateWriteup, downloadWriteupPdf } from '../api/client'
import { Flag, Trophy, AlertCircle, CheckCircle, XCircle, Code2, FileText, Download, Loader } from 'lucide-react'

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
  const [activeTab, setActiveTab] = useState('challenges') // 'challenges' | 'leaderboard'
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [templates, setTemplates] = useState([])
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [templateVars, setTemplateVars] = useState({})
  const [generatingWriteup, setGeneratingWriteup] = useState(false)
  const [generatedWriteupId, setGeneratedWriteupId] = useState(null)

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

  useEffect(() => {
    if (showTemplateModal) {
      getWriteupTemplates('ctf').then(data => {
        setTemplates(data)
        if (data.length > 0) {
          setSelectedTemplate(data[0])
          const initialVars = {}
          data[0].variables?.forEach(v => { initialVars[v.name] = '' })
          setTemplateVars(initialVars)
        }
      }).catch(() => {})
    }
  }, [showTemplateModal])

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template)
    const initialVars = {}
    template.variables?.forEach(v => { initialVars[v.name] = '' })
    setTemplateVars(initialVars)
  }

  const handleGenerateWriteup = async () => {
    if (!selectedTemplate || !currentChallenge) return
    setGeneratingWriteup(true)
    try {
      const vars = { ...templateVars, challenge: currentChallenge.title, category: currentChallenge.category }
      const res = await generateWriteup(userId, selectedTemplate.id, vars, `CTF: ${currentChallenge.title}`)
      setGeneratedWriteupId(res.id)
    } catch {
      alert('Błąd generowania raportu')
    } finally {
      setGeneratingWriteup(false)
    }
  }

  const handleDownloadWriteup = async () => {
    if (!generatedWriteupId) return
    try {
      const blob = await downloadWriteupPdf(generatedWriteupId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `writeup_${generatedWriteupId}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch {
      alert('Błąd pobierania PDF')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!flagInput.trim()) return
    setSubmitting(true)
    setResult(null)
    try {
      const res = await submitFlag(selected, userId, flagInput.trim())
      setResult({ success: true, message: res.message, points: res.points_earned })
      loadLeaderboard() // refresh scores
    } catch (e) {
      setResult({ success: false, message: e.response?.data?.detail || 'Błąd wysłania flagi' })
    } finally {
      setSubmitting(false)
    }
  }

  const currentChallenge = challenges.find(c => c.id === selected)

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-[#f0f6fc] mb-2 flex items-center gap-2">
        <Flag size={24} className="text-[#e3b341]" />
        CTF Challenge Mode
      </h1>
      <p className="text-[#8b949e] mb-6">Rozwiąż zadania, znajdź flagi, zdobądź punkty i wejdź na ranking!</p>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-[#30363d]">
        <button
          onClick={() => setActiveTab('challenges')}
          className={`px-4 py-2 text-sm ${activeTab === 'challenges' ? 'border-b-2 border-[#58a6ff] text-[#f0f6fc]' : 'text-[#8b949e]'}`}
        >
          Zadania ({challenges.length})
        </button>
        <button
          onClick={() => setActiveTab('leaderboard')}
          className={`px-4 py-2 text-sm ${activeTab === 'leaderboard' ? 'border-b-2 border-[#e3b341] text-[#f0f6fc]' : 'text-[#8b949e]'}`}
        >
          <Trophy size={14} className="inline mr-1" /> Ranking
        </button>
      </div>

      {activeTab === 'challenges' && (
        <div className="grid grid-cols-3 gap-6">
          {/* Challenge list */}
          <div className="col-span-1 space-y-3">
            {challenges.map(c => (
              <div
                key={c.id}
                onClick={() => { setSelected(c.id); setResult(null); setFlagInput('') }}
                className={`p-3 rounded-lg cursor-pointer border transition-colors ${
                  selected === c.id
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
                  <Code2 size={12} /> {c.category} • {c.points} pts
                </div>
              </div>
            ))}
          </div>

          {/* Challenge detail + submission */}
          <div className="col-span-2">
            {currentChallenge ? (
              <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6">
                <h2 className="text-xl font-bold text-[#f0f6fc] mb-2">{currentChallenge.title}</h2>
                <div className="flex items-center gap-3 mb-4">
                  <span className={`text-xs px-2 py-1 rounded border ${currentChallenge.difficulty <= 2 ? 'border-[#39d353]/30 text-[#39d353]' : currentChallenge.difficulty <= 3 ? 'border-[#e3b341]/30 text-[#e3b341]' : 'border-[#f85149]/30 text-[#f85149]'}`}>
                    {DIFFICULTY_LABELS[currentChallenge.difficulty]}
                  </span>
                  <span className="text-xs text-[#8b949e]">Kategoria: {currentChallenge.category}</span>
                  <span className="text-xs text-[#e3b341]">{currentChallenge.points} punktów</span>
                </div>

                <div className="prose prose-invert max-w-none mb-6">
                  <p className="text-[#c9d1d9] whitespace-pre-line">{currentChallenge.description}</p>
                </div>

                {currentChallenge.has_hint && (
                  <details className="mb-4">
                    <summary className="cursor-pointer text-[#8b949e] hover:text-[#c9d1d9] text-sm">Potrzebujesz podpowiedzi?</summary>
                    <div className="mt-2 p-3 bg-[#0d1117] border border-[#30363d] rounded text-sm text-[#c9d1d9]">
                      {currentChallenge.hint}
                      <span className="block text-xs text-[#f85149] mt-1">Uwaga: podpowiedź może zmniejszyć pulę punktów o 50%!</span>
                    </div>
                  </details>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm text-[#8b949e] mb-1">Wprowadź flagę (format: FLAG{...})</label>
                    <input
                      type="text"
                      value={flagInput}
                      onChange={e => setFlagInput(e.target.value)}
                      placeholder="FLAG{...}"
                      className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-[#f0f6fc] focus:outline-none focus:border-[#58a6ff]"
                      disabled={submitting}
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={submitting || !flagInput.trim()}
                    className="px-6 py-2.5 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white rounded-lg font-medium"
                  >
                    {submitting ? 'Sprawdzam...' : 'Prześlij flagę'}
                  </button>
                </form>

                {result && (
                  <div className={`mt-4 p-4 rounded-lg border ${result.success ? 'bg-[#39d353]/10 border-[#39d353]/30' : 'bg-[#f85149]/10 border-[#f85149]/30'}`}>
                    <div className={`font-bold mb-1 ${result.success ? 'text-[#39d353]' : 'text-[#f85149]'}`}>
                      {result.success ? <><CheckCircle size={18} className="inline mr-1" /> Poprawnie! </> : <><XCircle size={18} className="inline mr-1" /> Błędna flaga</>}
                    </div>
                    <div className="text-sm text-[#c9d1d9]">{result.message}</div>
                    {result.points && result.points > 0 && (
                      <div className="mt-1 text-[#e3b341] text-sm">+{result.points} XP</div>
                    )}
                  </div>
                )}

                {/* Write-up Template Button */}
                <div className="mt-4">
                  <button
                    onClick={() => setShowTemplateModal(true)}
                    className="flex items-center gap-2 bg-[#1f6feb]/20 hover:bg-[#1f6feb]/30 text-[#58a6ff] border border-[#1f6feb]/40 px-4 py-2 rounded-lg text-sm"
                  >
                    <FileText size={14} />
                    Generuj Write-up z szablonu
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-8 text-center text-[#8b949e]">
                Wybierz zadanie z listy
              </div>
            )}
          </div>
        </div>

        {/* Template Modal */}
        {showTemplateModal && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[#f0f6fc] font-bold">Szablony Write-up</h3>
                <button onClick={() => { setShowTemplateModal(false); setGeneratedWriteupId(null) }} className="text-[#8b949e] hover:text-[#c9d1d9]">
                  <span className="text-xl">×</span>
                </button>
              </div>

              {/* Template selector */}
              <div className="flex gap-2 mb-4 flex-wrap">
                {templates.map(t => (
                  <button
                    key={t.id}
                    onClick={() => handleTemplateSelect(t)}
                    className={`px-3 py-1.5 rounded-lg text-xs border transition-colors ${
                      selectedTemplate?.id === t.id
                        ? 'border-[#58a6ff] bg-[#1f6feb]/20 text-[#58a6ff]'
                        : 'border-[#30363d] text-[#8b949e] hover:text-[#c9d1d9]'
                    }`}
                  >
                    {t.name}
                  </button>
                ))}
              </div>

              {/* Variable inputs */}
              {selectedTemplate && (
                <div className="space-y-3 mb-4">
                  {selectedTemplate.variables?.map(v => (
                    <div key={v.name}>
                      <label className="text-[#c9d1d9] text-sm font-medium mb-1 block">{v.label}</label>
                      <textarea
                        value={templateVars[v.name] || ''}
                        onChange={e => setTemplateVars(prev => ({ ...prev, [v.name]: e.target.value }))}
                        placeholder={`Wpisz ${v.label.toLowerCase()}...`}
                        rows={2}
                        className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-[#c9d1d9] placeholder-[#484f58] text-sm focus:outline-none focus:border-[#58a6ff] resize-none"
                      />
                    </div>
                  ))}
                </div>
              )}

              {/* Generate button */}
              <div className="flex gap-2">
                <button
                  onClick={handleGenerateWriteup}
                  disabled={generatingWriteup || !selectedTemplate}
                  className="flex-1 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                >
                  {generatingWriteup ? <Loader size={14} className="animate-spin" /> : <FileText size={14} />}
                  Generuj raport
                </button>
                {generatedWriteupId && (
                  <button
                    onClick={handleDownloadWriteup}
                    className="flex items-center gap-2 bg-[#1f6feb]/20 hover:bg-[#1f6feb]/30 text-[#58a6ff] border border-[#1f6feb]/40 px-4 py-2 rounded-lg text-sm"
                  >
                    <Download size={14} /> PDF
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      )}

      {activeTab === 'leaderboard' && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6">
          <h2 className="text-xl font-bold text-[#f0f6fc] mb-4 flex items-center gap-2">
            <Trophy size={20} className="text-[#e3b341]" />
            Ranking CTF
          </h2>
          {leaderboard.length === 0 ? (
            <p className="text-[#8b949e]">Brak rozwiązań. Bądź pierwszy!</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-[#8b949e] border-b border-[#30363d]">
                  <th className="text-left py-2">#</th>
                  <th className="text-left py-2">Użytkownik</th>
                  <th className="text-right py-2">Punkty</th>
                  <th className="text-right py-2">Rozwiązane</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((row, idx) => (
                  <tr key={row.user_id} className="border-b border-[#21262d] last:border-0">
                    <td className="py-2 text-[#f0f6fc]">{row.rank}</td>
                    <td className="py-2 text-[#f0f6fc]">{row.name}</td>
                    <td className="py-2 text-right text-[#e3b341] font-mono">{row.ctf_points}</td>
                    <td className="py-2 text-right text-[#8b949e]">{row.challenges_solved}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}

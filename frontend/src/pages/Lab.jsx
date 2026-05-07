import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getLabStatus, startLab, stopLab, resetLab, getTopics, completeLab, getUserId, getWriteupTemplates, generateWriteup, downloadWriteupPdf } from '../api/client'
import { FlaskConical, Play, Square, RefreshCw, ExternalLink, CheckCircle, Loader, FileText, Download } from 'lucide-react'

export default function Lab() {
  const userId = getUserId()
  const navigate = useNavigate()
  const [labStatus, setLabStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [topics, setTopics] = useState([])
  const [selectedTopic, setSelectedTopic] = useState(null)
  const [writeup, setWriteup] = useState({ reconnaissance: '', exploitation: '', result: '', lesson: '' })
  const [completing, setCompleting] = useState(false)
  const [completed, setCompleted] = useState(null)
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [templates, setTemplates] = useState([])
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [templateVars, setTemplateVars] = useState({})
  const [generatingWriteup, setGeneratingWriteup] = useState(false)
  const [generatedWriteupId, setGeneratedWriteupId] = useState(null)

  useEffect(() => {
    getLabStatus().then(setLabStatus)
    getTopics(userId).then(ts => {
      const withLabs = ts.filter(t => t.lab_type && t.unlocked && t.theory_completed)
      setTopics(withLabs)
      if (withLabs.length > 0) setSelectedTopic(withLabs[0])
    })
  }, [userId])

  useEffect(() => {
    if (showTemplateModal) {
      getWriteupTemplates('lab').then(data => {
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

  const handleStart = async () => {
    setLoading(true)
    try {
      const res = await startLab()
      setLabStatus({ running: res.success, url: res.url })
    } catch {
      alert('Błąd uruchamiania Dockera')
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    setLoading(true)
    await stopLab()
    setLabStatus({ running: false })
    setLoading(false)
  }

  const handleComplete = async () => {
    if (!selectedTopic || !writeup.exploitation.trim()) {
      alert('Wypełnij przynajmniej pole "Eksploitacja"')
      return
    }
    setCompleting(true)
    try {
      const res = await completeLab(selectedTopic.slug, userId, writeup)
      setCompleted(res)
    } catch {
      alert('Błąd zapisywania writeupa')
    } finally {
      setCompleting(false)
    }
  }

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template)
    const initialVars = {}
    template.variables?.forEach(v => { initialVars[v.name] = '' })
    setTemplateVars(initialVars)
  }

  const handleGenerateWriteup = async () => {
    if (!selectedTemplate) return
    setGeneratingWriteup(true)
    try {
      const res = await generateWriteup(userId, selectedTemplate.id, templateVars, `Lab: ${selectedTopic?.name || 'DVWA'}`)
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

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-[#f0f6fc] mb-2 flex items-center gap-2">
        <FlaskConical size={24} className="text-[#bc8cff]" />
        Docker Labs
      </h2>
      <p className="text-[#8b949e] mb-6">Praktyczne ćwiczenia na DVWA (Damn Vulnerable Web Application)</p>

      {/* Lab control panel */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`w-2.5 h-2.5 rounded-full ${labStatus?.running ? 'bg-[#39d353]' : 'bg-[#f85149]'}`} />
            <span className="text-[#c9d1d9] font-medium">
              {labStatus?.running ? 'Lab działa' : 'Lab zatrzymany'}
            </span>
            {labStatus?.running && labStatus.url && (
              <a
                href={labStatus.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-[#58a6ff] text-sm hover:underline"
              >
                {labStatus.url} <ExternalLink size={12} />
              </a>
            )}
          </div>

          <div className="flex gap-2">
            {!labStatus?.running ? (
              <button
                onClick={handleStart}
                disabled={loading}
                className="flex items-center gap-2 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm"
              >
                {loading ? <Loader size={14} className="animate-spin" /> : <Play size={14} />}
                Uruchom
              </button>
            ) : (
              <>
                <button
                  onClick={() => resetLab().then(() => getLabStatus().then(setLabStatus))}
                  className="flex items-center gap-2 bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] px-3 py-2 rounded-lg text-sm"
                >
                  <RefreshCw size={14} /> Reset
                </button>
                <button
                  onClick={handleStop}
                  className="flex items-center gap-2 bg-[#da3633]/20 hover:bg-[#da3633]/30 text-[#f85149] border border-[#f85149]/30 px-3 py-2 rounded-lg text-sm"
                >
                  <Square size={14} /> Stop
                </button>
              </>
            )}
          </div>
        </div>

        {!labStatus?.running && (
          <div className="text-[#8b949e] text-sm bg-[#0d1117] rounded-lg p-3">
            💡 Wymagany Docker Desktop. Po kliknięciu "Uruchom" pobierze się obraz DVWA (~500MB, tylko pierwszy raz).
          </div>
        )}
      </div>

      {/* Topic selector */}
      {topics.length > 0 && (
        <div className="mb-6">
          <h3 className="text-[#f0f6fc] font-medium mb-3">Wybierz temat:</h3>
          <div className="flex flex-wrap gap-2">
            {topics.map(t => (
              <button
                key={t.slug}
                onClick={() => setSelectedTopic(t)}
                className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
                  selectedTopic?.slug === t.slug
                    ? 'border-[#58a6ff] bg-[#1f6feb]/20 text-[#58a6ff]'
                    : 'border-[#30363d] text-[#8b949e] hover:text-[#c9d1d9]'
                }`}
              >
                {t.lab_completed ? '✅ ' : ''}{t.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {topics.length === 0 && (
        <div className="bg-[#161b22] border border-[#e3b341]/30 rounded-xl p-5 mb-6 text-[#e3b341] text-sm">
          ⚠️ Brak odblokowanych labów. Ukończ teorię dla tematów z labem (np. SQL Injection).
        </div>
      )}

      {/* Writeup form */}
      {selectedTopic && !completed && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
          <h3 className="text-[#f0f6fc] font-semibold mb-1">
            Lab: {selectedTopic.name}
          </h3>
          <p className="text-[#8b949e] text-sm mb-4">
            Otwórz DVWA, wykonaj atak, a potem wypełnij writeup poniżej.
          </p>

          {labStatus?.running && selectedTopic.lab_type && (
            <a
              href={`http://localhost:8080`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-[#bc8cff] text-sm mb-4 hover:underline"
            >
              Otwórz DVWA w przeglądarce <ExternalLink size={14} />
            </a>
          )}

          <div className="space-y-4">
            {[
              { key: 'reconnaissance', label: 'Rekonesans', placeholder: 'Co sprawdziłeś przed atakiem? (np. znalazłem pole input, sprawdziłem nagłówki)' },
              { key: 'exploitation', label: 'Eksploitacja ⭐', placeholder: 'Jaki payload/technikę użyłeś? Co dokładnie wpisałeś?' },
              { key: 'result', label: 'Wynik', placeholder: 'Co udało Ci się osiągnąć? (np. wyświetliłem dane z bazy)' },
              { key: 'lesson', label: 'Lekcja', placeholder: 'Czego się nauczyłeś? Jak można to naprawić w prawdziwej aplikacji?' },
            ].map(({ key, label, placeholder }) => (
              <div key={key}>
                <label className="text-[#c9d1d9] text-sm font-medium mb-1 block">{label}</label>
                <textarea
                  value={writeup[key]}
                  onChange={e => setWriteup(prev => ({ ...prev, [key]: e.target.value }))}
                  placeholder={placeholder}
                  rows={3}
                  className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-3 text-[#c9d1d9] placeholder-[#484f58] text-sm focus:outline-none focus:border-[#58a6ff] resize-none"
                />
              </div>
            ))}
          </div>

          <button
            onClick={handleComplete}
            disabled={completing}
            className="mt-4 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white px-6 py-2.5 rounded-lg text-sm font-medium flex items-center gap-2"
          >
            {completing ? <Loader size={14} className="animate-spin" /> : <CheckCircle size={14} />}
            Ukończ lab i wygeneruj writeup
          </button>
        </div>
      )}

      {/* Writeup result */}
      {completed && (
        <div className="bg-[#161b22] border border-[#39d353]/30 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle size={20} className="text-[#39d353]" />
            <h3 className="text-[#39d353] font-bold">Lab ukończony! +{completed.xp_awarded} XP</h3>
          </div>

          <div className="bg-[#0d1117] rounded-lg p-4 mb-4 font-mono text-sm">
            <h4 className="text-[#58a6ff] font-bold mb-2"># {completed.writeup?.title}</h4>
            <p className="text-[#8b949e] mb-3">{completed.writeup?.summary}</p>

            <h5 className="text-[#e3b341] mb-1">## Przebieg ataku</h5>
            <p className="text-[#c9d1d9] mb-3">{completed.writeup?.attack_narrative}</p>

            <h5 className="text-[#f85149] mb-1">## Ochrona</h5>
            <p className="text-[#c9d1d9] mb-3">{completed.writeup?.defense_notes}</p>

            <h5 className="text-[#39d353] mb-1">## Kluczowe lekcje</h5>
            <ul className="text-[#c9d1d9] space-y-1">
              {completed.writeup?.key_lessons?.map((l, i) => (
                <li key={i}>• {l}</li>
              ))}
            </ul>
          </div>

          {completed.new_achievements?.length > 0 && (
            <div className="bg-[#e3b341]/10 border border-[#e3b341]/30 rounded-lg p-3 mb-4">
              {completed.new_achievements.map((a, i) => (
                <div key={i} className="text-sm">{a.icon} <span className="text-[#e3b341]">{a.title}</span> — {a.description}</div>
              ))}
            </div>
          )}

          <button
            onClick={() => { setCompleted(null); setWriteup({ reconnaissance: '', exploitation: '', result: '', lesson: '' }) }}
            className="bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] px-4 py-2 rounded-lg text-sm"
          >
            Następny lab
          </button>
        </div>
      )}

      {/* Template Write-up Button */}
      {selectedTopic && (
        <div className="mt-6">
          <button
            onClick={() => setShowTemplateModal(true)}
            className="flex items-center gap-2 bg-[#1f6feb]/20 hover:bg-[#1f6feb]/30 text-[#58a6ff] border border-[#1f6feb]/40 px-4 py-2.5 rounded-lg text-sm"
          >
            <FileText size={14} />
            Generuj raport z szablonu
          </button>
        </div>
      )}

      {/* Template Modal */}
      {showTemplateModal && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[#f0f6fc] font-bold">Szablony raportów</h3>
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
    </div>
  )
}

import { useEffect, useState } from 'react'
import { getCves, createFlashcardFromCve, getUserId } from '../api/client'
import { Shield, AlertTriangle, AlertCircle, Zap, Clock, ExternalLink, Plus } from 'lucide-react'

const SEVERITY_COLORS = {
  CRITICAL: 'text-[#f85149] border-[#f85149]/30 bg-[#f85149]/10',
  HIGH: 'text-[#e3b341] border-[#e3b341]/30 bg-[#e3b341]/10',
  MEDIUM: 'text-[#58a6ff] border-[#58a6ff]/30 bg-[#58a6ff]/10',
  LOW: 'text-[#39d353] border-[#39d353]/30 bg-[#39d353]/10',
}

const SEVERITY_ICONS = {
  CRITICAL: AlertTriangle,
  HIGH: Zap,
  MEDIUM: AlertCircle,
  LOW: Shield,
}

export default function Cves() {
  const userId = getUserId()
  const [cves, setCves] = useState([])
  const [loading, setLoading] = useState(true)
  const [filterTopic, setFilterTopic] = useState('')
  const [filterSeverity, setFilterSeverity] = useState('')

  useEffect(() => {
    loadCves()
  }, [])

  const loadCves = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterTopic) params.topic_slug = filterTopic
      if (filterSeverity) params.severity = filterSeverity
      const data = await getCves(params)
      setCves(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleAddToFlashcards = async (cve) => {
    try {
      await createFlashcardFromCve(cve.cve_id, { user_id: userId })
      alert(`Dodano fiszkę: ${cve.cve_id}`)
    } catch (e) {
      alert('Błąd dodawania fiszki: ' + (e.response?.data?.detail || e.message))
    }
  }

  if (loading) return (
    <div className="p-8 text-[#8b949e] text-center animate-pulse">
      Ładowanie CVE...
    </div>
  )

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-[#f0f6fc] flex items-center gap-2">
          <Shield size={24} className="text-[#58a6ff]" />
          CVE Explorer
        </h1>
        <button
          onClick={loadCves}
          className="text-sm text-[#58a6ff] hover:text-[#79c0ff]"
        >
          Odśwież
        </button>
      </div>

      <p className="text-[#8b949e] mb-6">
        Przeglądaj znane podatności (CVE). Kliknij "Dodaj do fiszek", aby utrwalić wiedzę.
      </p>

      {/* Filters */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 mb-6 flex gap-4">
        <div>
          <label className="block text-xs text-[#8b949e] mb-1">Temat (topic_slug)</label>
          <input
            type="text"
            value={filterTopic}
            onChange={e => setFilterTopic(e.target.value)}
            placeholder="np. sql-injection, xss"
            className="bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-sm text-[#c9d1d9] w-48"
          />
        </div>
        <div>
          <label className="block text-xs text-[#8b949e] mb-1">Waga (severity)</label>
          <select
            value={filterSeverity}
            onChange={e => setFilterSeverity(e.target.value)}
            className="bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-sm text-[#c9d1d9] w-32"
          >
            <option value="">Wszystkie</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>
        <div className="flex items-end">
          <button
            onClick={loadCves}
            className="px-4 py-1.5 bg-[#238636] hover:bg-[#2ea043] text-white rounded text-sm"
          >
            Filtruj
          </button>
        </div>
      </div>

      {/* CVE list */}
      <div className="space-y-4">
        {cves.length === 0 ? (
          <div className="text-center py-8 text-[#8b949e]">Brak CVEs spełniających kryteria</div>
        ) : (
          cves.map(cve => {
            const IconComp = SEVERITY_ICONS[cve.severity] || Shield
            const style = SEVERITY_COLORS[cve.severity] || ''
            const date = new Date(cve.published_date).toLocaleDateString('pl-PL')
            return (
              <div key={cve.id} className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <code className="text-[#e3b341] font-mono text-sm bg-[#0d1117] px-2 py-0.5 rounded">
                        {cve.cve_id}
                      </code>
                      <span className={`text-xs px-2 py-0.5 rounded-full border ${style}`}>
                        {cve.severity}
                      </span>
                      {cve.topic_slug && (
                        <span className="text-[#8b949e] text-xs bg-[#21262d] px-2 py-0.5 rounded">
                          {cve.topic_slug}
                        </span>
                      )}
                    </div>
                    <h3 className="text-[#f0f6fc] font-semibold mb-2">{cve.title}</h3>
                    <p className="text-[#8b949e] text-sm mb-3">{cve.description}</p>
                    <div className="flex items-center gap-4 text-xs text-[#484f58]">
                      <span className="flex items-center gap-1">
                        <Clock size={12} /> {date}
                      </span>
                      {cve.affected_products && cve.affected_products.length > 0 && (
                        <span className="truncate max-w-md">
                          🎯 {cve.affected_products.join(', ')}
                        </span>
                      )}
                    </div>
                    {cve.references && cve.references.length > 0 && (
                      <div className="mt-2">
                        {cve.references.map((ref, i) => (
                          <a
                            key={i}
                            href={ref}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-[#58a6ff] hover:underline mr-3"
                          >
                            <ExternalLink size={10} /> Link {i + 1}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => handleAddToFlashcards(cve)}
                      className="flex items-center gap-1.5 px-3 py-2 bg-[#238636] hover:bg-[#2ea043] text-white text-sm rounded-lg"
                      title="Dodaj tę CVE jako fiszkę"
                    >
                      <Plus size={14} />
                      Dodaj do fiszek
                    </button>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

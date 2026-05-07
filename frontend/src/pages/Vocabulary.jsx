import { useEffect, useState } from 'react'
import { getTopics, getTopicVocabulary, getTopicResources, getUserId } from '../api/client'
import { BookMarked, ExternalLink, Youtube, Globe, Wrench, Loader } from 'lucide-react'

export default function Vocabulary() {
  const userId = getUserId()
  const [topics, setTopics] = useState([])
  const [selectedSlug, setSelectedSlug] = useState(null)
  const [vocab, setVocab] = useState(null)
  const [resources, setResources] = useState(null)
  const [tab, setTab] = useState('vocab')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getTopics(userId).then(ts => {
      const done = ts.filter(t => t.theory_completed)
      setTopics(done)
      if (done.length > 0) selectTopic(done[0].slug)
    })
  }, [userId])

  const selectTopic = async (slug) => {
    setSelectedSlug(slug)
    setVocab(null)
    setResources(null)
    setLoading(true)
    try {
      const [v, r] = await Promise.all([getTopicVocabulary(slug), getTopicResources(slug)])
      setVocab(v)
      setResources(r)
    } catch {}
    setLoading(false)
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <BookMarked size={22} className="text-[#58a6ff]" />
        <h2 className="text-2xl font-bold text-[#f0f6fc]">Słownik & Zasoby</h2>
      </div>

      {topics.length === 0 && (
        <div className="text-[#8b949e] text-center py-12">
          Ukończ przynajmniej jeden temat, żeby zobaczyć słownik.
        </div>
      )}

      {topics.length > 0 && (
        <div className="flex gap-6">
          {/* Topic list */}
          <div className="w-48 flex-shrink-0">
            <div className="text-xs text-[#8b949e] font-mono uppercase mb-2">Tematy</div>
            <div className="space-y-1">
              {topics.map(t => (
                <button
                  key={t.slug}
                  onClick={() => selectTopic(t.slug)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    selectedSlug === t.slug
                      ? 'bg-[#1f6feb]/20 text-[#58a6ff] border border-[#1f6feb]/40'
                      : 'text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d]'
                  }`}
                >
                  {t.name}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex gap-1 mb-4 bg-[#161b22] border border-[#30363d] rounded-lg p-1 w-fit">
              {[
                { id: 'vocab', label: '📚 Słownik' },
                { id: 'resources', label: '🔗 Zasoby' },
              ].map(t => (
                <button
                  key={t.id}
                  onClick={() => setTab(t.id)}
                  className={`px-4 py-1.5 rounded text-sm transition-colors ${
                    tab === t.id ? 'bg-[#21262d] text-[#f0f6fc]' : 'text-[#8b949e] hover:text-[#c9d1d9]'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {loading && (
              <div className="flex items-center gap-2 text-[#8b949e] py-8">
                <Loader size={16} className="animate-spin" /> Ładowanie...
              </div>
            )}

            {!loading && tab === 'vocab' && vocab && (
              <div className="space-y-2">
                {vocab.vocabulary.map((v, i) => (
                  <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3">
                    <div className="flex items-start gap-3">
                      <span className="text-[#58a6ff] font-mono text-sm font-medium w-48 flex-shrink-0 pt-0.5">
                        {v.term_en}
                      </span>
                      <div className="flex-1">
                        <div className="text-[#c9d1d9] text-sm">{v.definition}</div>
                        {v.example && (
                          <pre className="mt-2 text-[#e3b341] text-xs font-mono bg-[#0d1117] rounded p-2 overflow-x-auto">
                            {v.example}
                          </pre>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!loading && tab === 'resources' && resources && (
              <div className="space-y-6">
                {/* Tip */}
                {resources.resources.tip && (
                  <div className="bg-[#39d353]/10 border border-[#39d353]/30 rounded-xl p-4 text-[#c9d1d9] text-sm">
                    💡 {resources.resources.tip}
                  </div>
                )}

                <ResourceSection
                  icon={<Youtube size={16} className="text-[#f85149]" />}
                  title="YouTube"
                  items={resources.resources.youtube_channels || []}
                  keyField="name"
                  descField="why"
                  hintField="url_hint"
                />
                <ResourceSection
                  icon={<Globe size={16} className="text-[#58a6ff]" />}
                  title="Strony / Dokumentacja"
                  items={resources.resources.websites || []}
                  keyField="name"
                  descField="why"
                  hintField="url_hint"
                />
                <ResourceSection
                  icon={<Wrench size={16} className="text-[#bc8cff]" />}
                  title="Narzędzia"
                  items={resources.resources.tools || []}
                  keyField="name"
                  descField="description"
                  hintField={null}
                />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function ResourceSection({ icon, title, items, keyField, descField, hintField }) {
  if (!items.length) return null
  return (
    <div>
      <h3 className="text-[#f0f6fc] font-medium mb-2 flex items-center gap-2">
        {icon} {title}
      </h3>
      <div className="space-y-2">
        {items.map((item, i) => (
          <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 flex items-start gap-3">
            <div className="flex-1">
              <div className="text-[#c9d1d9] text-sm font-medium">{item[keyField]}</div>
              <div className="text-[#8b949e] text-xs mt-0.5">{item[descField]}</div>
              {hintField && item[hintField] && (
                <div className="text-[#484f58] text-xs mt-1 font-mono">{item[hintField]}</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

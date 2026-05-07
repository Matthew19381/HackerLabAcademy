import { useEffect, useState } from 'react'
import { listCertificates, generateCertificate, downloadCertificate, getUserId } from '../api/client'
import { Award, Download, CheckCircle, AlertCircle } from 'lucide-react'

const CATEGORIES = ["Fundamentals", "OWASP Top 10", "Advanced"]

export default function Certificates() {
  const userId = getUserId()
  const [certificates, setCertificates] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState({})
  const [message, setMessage] = useState(null)

  useEffect(() => {
    load()
  }, [])

  const load = async () => {
    try {
      const data = await listCertificates(userId)
      setCertificates(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async (category) => {
    setGenerating(cat => ({ ...cat, [category]: true }))
    setMessage(null)
    try {
      const res = await generateCertificate(category, userId)
      setMessage({ type: 'success', text: `Certyfikat wygenerowany! Kod: ${res.certificate_code}` })
      load() // refresh list
    } catch (e) {
      setMessage({ type: 'error', text: e.response?.data?.detail || 'Nie udało się wygenerować certyfikatu' })
    } finally {
      setGenerating(cat => ({ ...cat, [category]: false }))
    }
  }

  const handleDownload = async (certCode) => {
    try {
      const res = await downloadCertificate(certCode)
      const blob = new Blob([res.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${certCode}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      alert('Błąd pobierania: ' + (e.response?.data?.detail || e.message))
    }
  }

  // Check which categories are already earned
  const earnedCategories = new Set(certificates.map(c => c.category))

  if (loading) return (
    <div className="p-8 text-[#8b949e] text-center animate-pulse">
      Ładowanie certyfikatów...
    </div>
  )

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-[#f0f6fc] mb-2 flex items-center gap-2">
        <Award size={24} className="text-[#e3b341]" />
        Certyfikaty
      </h1>
      <p className="text-[#8b949e] mb-6">Po ukończeniu wszystkich tematów w kategorii otrzymasz certyfikat PDF.</p>

      {message && (
        <div className={`p-3 rounded-lg mb-4 ${message.type === 'success' ? 'bg-[#39d353]/10 border border-[#39d353]/30 text-[#39d353]' : 'bg-[#f85149]/10 border border-[#f85149]/30 text-[#f85149]'}`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {CATEGORIES.map(cat => {
          const earned = earnedCategories.has(cat)
          return (
            <div key={cat} className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
              <h3 className="text-[#f0f6fc] font-medium mb-2">{cat}</h3>
              {earned ? (
                <div className="flex flex-col gap-2">
                  <div className="flex items-center gap-2 text-[#39d353] text-sm">
                    <CheckCircle size={16} /> Ukończono
                  </div>
                  {certificates
                    .filter(c => c.category === cat)
                    .map(c => (
                      <button
                        key={c.certificate_code}
                        onClick={() => handleDownload(c.certificate_code)}
                        className="flex items-center gap-2 px-3 py-2 bg-[#238636] hover:bg-[#2ea043] text-white rounded text-sm"
                      >
                        <Download size={14} /> Pobierz PDF
                      </button>
                    ))
                  }
                </div>
              ) : (
                <div className="text-sm text-[#8b949e] mb-3">
                  Ukończ wszystkie tematy w tej kategorii, aby odblokować.
                </div>
              )}
              <button
                onClick={() => handleGenerate(cat)}
                disabled={earned || generating[cat]}
                className="w-full px-4 py-2 mt-2 border border-[#30363d] rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#21262d] text-[#c9d1d9]"
              >
                {generating[cat] ? 'Generowanie...' : earned ? 'Już wygenerowano' : 'Sprawdź status / Wygeneruj'}
              </button>
            </div>
          )
        })}
      </div>

      {/* Certificates list */}
      {certificates.length > 0 && (
        <div className="mt-8 bg-[#161b22] border border-[#30363d] rounded-xl p-6">
          <h2 className="text-xl font-bold text-[#f0f6fc] mb-4">Twoje certyfikaty</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[#8b949e] border-b border-[#30363d]">
                <th className="text-left py-2">Kategoria</th>
                <th className="text-left py-2">Kod</th>
                <th className="text-left py-2">Data</th>
                <th className="text-right py-2">Pobierz</th>
              </tr>
            </thead>
            <tbody>
              {certificates.map(c => (
                <tr key={c.id} className="border-b border-[#21262d]">
                  <td className="py-2 text-[#c9d1d9]">{c.category}</td>
                  <td className="py-2 text-[#58a6ff] font-mono text-xs">{c.certificate_code}</td>
                  <td className="py-2 text-[#8b949e]">{new Date(c.issued_at).toLocaleDateString('pl-PL')}</td>
                  <td className="py-2 text-right">
                    <button
                      onClick={() => handleDownload(c.certificate_code)}
                      className="text-[#58a6ff] hover:underline text-xs flex items-center gap-1 ml-auto"
                    >
                      <Download size={12} /> PDF
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

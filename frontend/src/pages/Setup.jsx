import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createUser, setUserId } from '../api/client'
import { ShieldCheck } from 'lucide-react'

export default function Setup() {
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleStart = async () => {
    if (!name.trim()) return
    setLoading(true)
    try {
      const data = await createUser(name.trim())
      setUserId(data.user_id)
      navigate('/')
    } catch (e) {
      alert('Błąd podczas tworzenia konta. Sprawdź czy backend działa.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0d1117] flex items-center justify-center">
      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-10 w-full max-w-md text-center">
        <ShieldCheck size={48} className="text-[#39d353] mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-[#f0f6fc] mb-2">HackerLabAcademy</h1>
        <p className="text-[#8b949e] mb-8">
          Naucz się web security od podstaw.<br />
          Teoria → Quiz → Docker Lab → Writeup.
        </p>

        <input
          type="text"
          value={name}
          onChange={e => setName(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleStart()}
          placeholder="Twoje imię lub nick"
          className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-3 text-[#c9d1d9] placeholder-[#484f58] focus:outline-none focus:border-[#58a6ff] mb-4"
        />

        <button
          onClick={handleStart}
          disabled={loading || !name.trim()}
          className="w-full bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white font-medium py-3 rounded-lg transition-colors"
        >
          {loading ? 'Tworzenie...' : 'Zacznij naukę →'}
        </button>

        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          {[
            { icon: '📖', label: '13 tematów' },
            { icon: '🧪', label: 'Docker Labs' },
            { icon: '🃏', label: 'SM-2 Fiszki' },
          ].map(({ icon, label }) => (
            <div key={label} className="text-[#8b949e] text-sm">
              <div className="text-2xl mb-1">{icon}</div>
              {label}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

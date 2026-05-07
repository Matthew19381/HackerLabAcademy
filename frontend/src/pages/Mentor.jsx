import { useState, useRef, useEffect } from 'react'
import { mentorChat, getUserId } from '../api/client'
import { Bot, Send, Loader, Trash2 } from 'lucide-react'

const SESSION_ID = `mentor_${Date.now()}`

export default function Mentor() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Cześć! Jestem Twoim AI Mentorem cyberbezpieczeństwa. Pytaj o cokolwiek — ataki, obrony, pojęcia. Wyjaśnię prosto i po polsku. 🛡️'
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    if (!input.trim() || loading) return
    const msg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: msg }])
    setLoading(true)
    try {
      const res = await mentorChat(SESSION_ID, msg)
      setMessages(prev => [...prev, { role: 'assistant', content: res.response }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Błąd połączenia. Spróbuj ponownie.' }])
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([{
      role: 'assistant',
      content: 'Rozmowa wyczyszczona. O co chcesz zapytać? 🛡️'
    }])
  }

  return (
    <div className="flex flex-col h-screen max-h-screen">
      {/* Header */}
      <div className="p-4 border-b border-[#30363d] flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <Bot size={20} className="text-[#58a6ff]" />
          <span className="text-[#f0f6fc] font-medium">AI Mentor</span>
          <span className="text-xs text-[#8b949e]">Cybersecurity Assistant</span>
        </div>
        <button onClick={clearChat} className="text-[#8b949e] hover:text-[#c9d1d9] flex items-center gap-1 text-sm">
          <Trash2 size={14} /> Wyczyść
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
              m.role === 'user'
                ? 'bg-[#1f6feb] text-white rounded-br-sm'
                : 'bg-[#161b22] border border-[#30363d] text-[#c9d1d9] rounded-bl-sm'
            }`}>
              {m.role === 'assistant' && (
                <div className="flex items-center gap-1 mb-1 text-[#58a6ff] text-xs font-medium">
                  <Bot size={12} /> Mentor
                </div>
              )}
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-[#161b22] border border-[#30363d] rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-2 text-[#8b949e] text-sm">
              <Loader size={14} className="animate-spin" /> Myślę...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggested prompts */}
      {messages.length === 1 && (
        <div className="px-6 pb-3 flex flex-wrap gap-2">
          {[
            'Co to jest SQL Injection?',
            'Jak działa XSS?',
            'Czym różni się CSRF od XSS?',
            'Jak sprawdzić czy aplikacja jest podatna na SQLi?',
          ].map(p => (
            <button
              key={p}
              onClick={() => { setInput(p); }}
              className="text-xs text-[#58a6ff] bg-[#1f6feb]/10 border border-[#1f6feb]/30 px-3 py-1.5 rounded-full hover:bg-[#1f6feb]/20"
            >
              {p}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-[#30363d] flex gap-3 flex-shrink-0">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder="Pytaj o cybersecurity..."
          className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-xl px-4 py-3 text-[#c9d1d9] placeholder-[#484f58] focus:outline-none focus:border-[#58a6ff] text-sm"
        />
        <button
          onClick={send}
          disabled={loading || !input.trim()}
          className="bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white p-3 rounded-xl"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}

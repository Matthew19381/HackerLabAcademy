import { useEffect, useState, useRef } from 'react'
import { getScenario, listScenarios } from '../data/terminal_scenarios'
import { Terminal as TerminalIcon, ChevronRight } from 'lucide-react'

export default function Terminal() {
  const [scenarios, setScenarios] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [stepIndex, setStepIndex] = useState(0)
  const [history, setHistory] = useState([])
  const [command, setCommand] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    setScenarios(listScenarios())
    if (listScenarios().length > 0) {
      setSelectedId(listScenarios()[0].id)
    }
  }, [])

  const scenario = selectedId ? getScenario(selectedId) : null

  const resetScenario = () => {
    setStepIndex(0)
    setHistory([])
  }

  useEffect(() => {
    if (scenario) {
      resetScenario()
    }
  }, [selectedId])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!command.trim() || !scenario) return
    const step = scenario.steps[stepIndex]
    const normalizedCmd = command.trim().toLowerCase()
    const expected = step.prompt.toLowerCase()
    // Exact match or simplified match: ignore extra spaces
    if (normalizedCmd.replace(/\s+/g, ' ') === expected.replace(/\s+/g, ' ')) {
      // Correct
      setHistory(prev => [...prev, { cmd: command, output: step.output, correct: true }])
      if (stepIndex + 1 < scenario.steps.length) {
        setStepIndex(prev => prev + 1)
      } else {
        // Scenario complete
        setCommand('')
        return
      }
    } else {
      // Wrong
      setHistory(prev => [...prev, { cmd: command, output: `Błąd: nieznana komenda lub niewłaściwe użycie. Spróbuj ponownie.\n(Wskazówka: ${scenario.hints[stepIndex]})`, correct: false }])
    }
    setCommand('')
  }

  if (!scenario) {
    return (
      <div className="p-8 text-[#8b949e] text-center">
        Ładowanie scenariuszy...
      </div>
    )
  }

  const isComplete = stepIndex >= scenario.steps.length

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-[#f0f6fc] flex items-center gap-2">
          <TerminalIcon size={24} className="text-[#39d353]" />
          Terminal Simulator
        </h1>
        <select
          value={selectedId}
          onChange={e => setSelectedId(e.target.value)}
          className="bg-[#161b22] border border-[#30363d] rounded px-3 py-1.5 text-sm text-[#c9d1d9]"
        >
          {scenarios.map(s => (
            <option key={s.id} value={s.id}>{s.title}</option>
          ))}
        </select>
      </div>

      <div className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4 mb-4 font-mono text-sm">
        <div className="text-[#c9d1d9] mb-2">{scenario.description}</div>
        <div className="flex items-center gap-2 mb-3">
          <ChevronRight size={16} className="text-[#39d353]" />
          <span className={isComplete ? "text-[#39d353]" : "text-[#e3b341]"}>
            {isComplete ? '✅ Scenariusz ukończony!' : `Krok ${stepIndex + 1}/${scenario.steps.length}`}
          </span>
        </div>
      </div>

      {/* Terminal window */}
      <div className="bg-[#0d1117] border border-[#30363d] rounded-lg font-mono text-sm overflow-hidden">
        <div className="bg-[#161b22] px-4 py-2 border-b border-[#30363d] text-[#8b949e] flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#f85149]"></div>
          <div className="w-3 h-3 rounded-full bg-[#e3b341]"></div>
          <div className="w-3 h-3 rounded-full bg-[#39d353]"></div>
          <span className="ml-2">user@hackerlab:~</span>
        </div>
        <div className="p-4 min-h-[300px] max-h-[500px] overflow-y-auto" onClick={() => inputRef.current?.focus()}>
          {history.length === 0 && (
            <div className="text-[#8b949e] mb-2">Napisz komendę zgodnie z zadaniem. Naciśnij Enter.</div>
          )}
          {history.map((h, i) => (
            <div key={i} className="mb-3">
              <div className="flex">
                <span className="text-[#58a6ff] mr-2">$</span>
                <span className="text-[#f0f6fc]">{h.cmd}</span>
              </div>
              <pre className="text-[#8b949e] mt-1 whitespace-pre-wrap">{h.output}</pre>
              {!h.correct && (
                <div className="text-[#f85149] text-xs mt-1">✗ Niepoprawnie. Spróbuj ponownie.</div>
              )}
            </div>
          ))}
          {isComplete && (
            <div className="text-[#39d353] mt-2 font-bold">Scenariusz zakończony! Brawo!</div>
          )}
          <form onSubmit={handleSubmit} className="flex mt-2">
            <span className="text-[#58a6ff] mr-2">$</span>
            <input
              ref={inputRef}
              type="text"
              value={command}
              onChange={e => setCommand(e.target.value)}
              disabled={isComplete}
              autoFocus
              className="flex-1 bg-transparent border-none outline-none text-[#f0f6fc]"
              placeholder={isComplete ? '' : 'Wpisz komendę...'}
            />
          </form>
        </div>
      </div>

      {/* Hints */}
      <div className="mt-4 text-xs text-[#8b949e]">
        <p>💡 Wskazówki:</p>
        <ul className="list-disc ml-5 mt-1">
          {scenario.hints.slice(0, stepIndex + 1).map((hint, i) => (
            <li key={i} className="mb-1">{hint}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}

import { useEffect, useState, useRef, useCallback } from 'react'
import { Clock, Play, Pause, RotateCcw } from 'lucide-react'

const DURATIONS = [15, 30, 60] // minutes

export default function StudyTimer() {
  const [durationMin, setDurationMin] = useState(() => {
    const saved = localStorage.getItem('studyTimerDuration')
    return saved ? parseInt(saved, 10) : 25
  })
  const [timeLeft, setTimeLeft] = useState(() => {
    const saved = localStorage.getItem('studyTimerRemaining')
    return saved ? parseInt(saved, 10) : durationMin * 60
  })
  const [isRunning, setIsRunning] = useState(() => {
    return localStorage.getItem('studyTimerRunning') === 'true'
  })

  const intervalRef = useRef(null)

  // Persist state
  useEffect(() => {
    localStorage.setItem('studyTimerDuration', durationMin)
  }, [durationMin])
  useEffect(() => {
    localStorage.setItem('studyTimerRemaining', timeLeft)
  }, [timeLeft])
  useEffect(() => {
    localStorage.setItem('studyTimerRunning', isRunning)
  }, [isRunning])

  // Tick
  useEffect(() => {
    if (isRunning && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft(prev => prev - 1)
      }, 1000)
    } else if (timeLeft === 0) {
      if (isRunning) {
        setIsRunning(false)
        // Notify
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification('Sesja zakończona!', { body: 'Czas na przerwę.' })
        }
      }
    }
    return () => clearInterval(intervalRef.current)
  }, [isRunning, timeLeft])

  const toggle = useCallback(() => setIsRunning(r => !r), [])
  const reset = useCallback(() => {
    setIsRunning(false)
    setTimeLeft(durationMin * 60)
  }, [durationMin])

  const format = (s) => {
    const m = Math.floor(s / 60)
    const sec = s % 60
    return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
  }

  const critical = timeLeft <= 5 && timeLeft > 0
  const finished = timeLeft === 0

  return (
    <div className={`fixed top-4 right-4 bg-[#161b22] border rounded-xl p-3 flex items-center gap-3 z-50 shadow-lg transition-all ${
      finished ? 'border-[#f85149] animate-pulse' : 'border-[#30363d]'
    }`}>
      {/* Duration selector */}
      <select
        value={durationMin}
        onChange={e => {
          const newDur = parseInt(e.target.value, 10)
          setDurationMin(newDur)
          setTimeLeft(newDur * 60)
        }}
        disabled={isRunning}
        className="bg-[#0d1117] border border-[#30363d] rounded px-2 py-1 text-xs text-[#c9d1d9]"
        title="Ustaw czas sesji"
      >
        {DURATIONS.map(d => (
          <option key={d} value={d}>{d} min</option>
        ))}
      </select>

      {/* Timer display */}
      <div className={`font-mono text-lg font-bold ${critical ? 'text-[#f85149] animate-pulse' : finished ? 'text-[#f85149]' : 'text-[#f0f6fc]'}`}>
        {format(timeLeft)}
      </div>

      {/* Controls */}
      <button
        onClick={toggle}
        className={`p-1.5 rounded ${isRunning ? 'text-[#e3b341] hover:bg-[#e3b341]/20' : 'text-[#39d353] hover:bg-[#39d353]/20'}`}
        title={isRunning ? 'Pauza' : 'Start'}
      >
        {isRunning ? <Pause size={18} /> : <Play size={18} />}
      </button>
      <button
        onClick={reset}
        className="p-1.5 rounded text-[#8b949e] hover:bg-[#30363d]"
        title="Reset"
      >
        <RotateCcw size={16} />
      </button>

      {/* Icon */}
      <Clock size={14} className="text-[#58a6ff]" />
    </div>
  )
}

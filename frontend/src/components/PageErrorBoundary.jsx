import { Component } from 'react'
import { useLocation } from 'react-router-dom'

// One broken page must not blank the whole app (Mindmap's missing d3 import did, 2026-09-27).
class Boundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  render() {
    if (this.state.error) {
      return (
        <div className="m-6 p-4 rounded-lg border border-red-700 bg-red-950 text-red-200">
          <p className="font-semibold">Ta strona napotkała błąd.</p>
          <p className="text-sm mt-1 opacity-80">{String(this.state.error.message || this.state.error)}</p>
          <p className="text-sm mt-2">Wybierz inną sekcję z menu.</p>
        </div>
      )
    }
    return this.props.children
  }
}

// keyed by path: navigating away resets the error
export default function PageErrorBoundary({ children }) {
  const { pathname } = useLocation()
  return <Boundary key={pathname}>{children}</Boundary>
}

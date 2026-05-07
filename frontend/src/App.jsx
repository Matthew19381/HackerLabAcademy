import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { getUserId } from './api/client'
import Layout from './components/Layout'
import Setup from './pages/Setup'
import Dashboard from './pages/Dashboard'
import Topics from './pages/Topics'
import TheoryLesson from './pages/TheoryLesson'
import Lab from './pages/Lab'
import Flashcards from './pages/Flashcards'
import Errors from './pages/Errors'
import Mentor from './pages/Mentor'
import Stats from './pages/Stats'
import DailyBrain from './pages/DailyBrain'
import Vocabulary from './pages/Vocabulary'
import Conversation from './pages/Conversation'
import Cves from './pages/Cves'
import Videos from './pages/Videos'
import CTF from './pages/CTF'
import Defense from './pages/Defense'
import Mindmap from './pages/Mindmap'
import Terminal from './pages/Terminal'
import AttackScenario from './pages/AttackScenario'
import Certificates from './pages/Certificates'
import Articles from './pages/Articles'

function RequireAuth({ children }) {
  const userId = getUserId()
  if (!userId) return <Navigate to="/setup" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/setup" element={<Setup />} />
        <Route
          path="/*"
          element={
            <RequireAuth>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/topics" element={<Topics />} />
                  <Route path="/mindmap" element={<Mindmap />} />
                  <Route path="/topics/:slug" element={<TheoryLesson />} />
                  <Route path="/lab" element={<Lab />} />
                  <Route path="/flashcards" element={<Flashcards />} />
                  <Route path="/errors" element={<Errors />} />
                  <Route path="/mentor" element={<Mentor />} />
                  <Route path="/stats" element={<Stats />} />
                  <Route path="/certificates" element={<Certificates />} />
                  <Route path="/brain" element={<DailyBrain />} />
                  <Route path="/vocabulary" element={<Vocabulary />} />
                  <Route path="/conversation/:slug?" element={<Conversation />} />
                  <Route path="/cves" element={<Cves />} />
                  <Route path="/videos" element={<Videos />} />
                  <Route path="/ctf" element={<CTF />} />
                  <Route path="/defense" element={<Defense />} />
                  <Route path="/terminal" element={<Terminal />} />
                  <Route path="/attack" element={<AttackScenario />} />
                  <Route path="/articles" element={<Articles />} />
                </Routes>
              </Layout>
            </RequireAuth>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

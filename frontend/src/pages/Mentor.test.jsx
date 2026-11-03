import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Mentor from './Mentor'

const api = vi.hoisted(() => ({
  mentorChat: vi.fn(),
  getMentorSession: vi.fn(),
  clearMentorSession: vi.fn(),
}))
vi.mock('../api/client', () => api)

beforeEach(() => {
  vi.clearAllMocks()
  localStorage.clear()
  Element.prototype.scrollIntoView = vi.fn()
})

describe('Mentor', () => {
  it('sends the chosen help mode and shows the usage notice without blocking', async () => {
    api.getMentorSession.mockResolvedValue({ messages: [] })
    api.mentorChat.mockResolvedValue({ response: 'Co zwraca serwer przy pojedynczym apostrofie?', usage: { today: 101, threshold: 100, over: true } })
    render(<Mentor />)
    fireEvent.click(screen.getByRole('radio', { name: 'Naprowadź' }))
    fireEvent.change(screen.getByPlaceholderText('Pytaj o cybersecurity...'), { target: { value: 'Jak znaleźć SQLi?' } })
    fireEvent.keyDown(screen.getByPlaceholderText('Pytaj o cybersecurity...'), { key: 'Enter' })
    expect(await screen.findByText('Co zwraca serwer przy pojedynczym apostrofie?')).toBeInTheDocument()
    expect(api.mentorChat).toHaveBeenCalledWith(expect.any(String), 'Jak znaleźć SQLi?', null, 'guide')
    expect(screen.getByText(/próg 100/)).toBeInTheDocument()
  })

  it('restores the stored conversation after a reload', async () => {
    localStorage.setItem('hackerlabacademy_mentor_session', 'mentor_1')
    api.getMentorSession.mockResolvedValue({ messages: [
      { role: 'user', content: 'Co to XSS?' },
      { role: 'assistant', content: 'Wstrzyknięcie skryptu.' },
    ] })
    render(<Mentor />)
    expect(await screen.findByText('Wstrzyknięcie skryptu.')).toBeInTheDocument()
    expect(api.getMentorSession).toHaveBeenCalledWith('mentor_1')
  })

  it('clearing deletes the server-side conversation and starts a new session', async () => {
    localStorage.setItem('hackerlabacademy_mentor_session', 'mentor_1')
    api.getMentorSession.mockResolvedValue({ messages: [] })
    api.clearMentorSession.mockResolvedValue({ success: true })
    render(<Mentor />)
    fireEvent.click(screen.getByText(/Wyczyść/))
    await waitFor(() => expect(api.clearMentorSession).toHaveBeenCalledWith('mentor_1'))
    await waitFor(() => expect(localStorage.getItem('hackerlabacademy_mentor_session')).not.toBe('mentor_1'))
  })
})

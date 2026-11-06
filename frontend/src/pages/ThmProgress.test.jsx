import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ThmProgress from './ThmProgress'

const api = vi.hoisted(() => ({
  getUserId: vi.fn(() => 1),
  getThmEntries: vi.fn(),
  createThmEntry: vi.fn(),
  updateThmEntry: vi.fn(),
  deleteThmEntry: vi.fn(),
  flashcardsFromNotes: vi.fn(),
}))
vi.mock('../api/client', () => api)

const entry = { id: 7, kind: 'room', name: 'Nmap', category: 'Network', url: null, done: false,
  completed_at: null, notes: 'nmap -sV pokazuje wersje usług na portach' }

beforeEach(() => {
  vi.clearAllMocks()
  api.getThmEntries.mockResolvedValue({ entries: [entry], counts: { done: 0, todo: 1 } })
  api.updateThmEntry.mockResolvedValue({})
  api.createThmEntry.mockResolvedValue({})
})

describe('ThmProgress', () => {
  it('lists entries and adds a room', async () => {
    render(<ThmProgress />)
    expect(await screen.findByText('Nmap')).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Nazwa'), { target: { value: 'Burp Suite: The Basics' } })
    fireEvent.click(screen.getByText('Dodaj'))
    await waitFor(() => expect(api.createThmEntry).toHaveBeenCalledWith(
      expect.objectContaining({ user_id: 1, name: 'Burp Suite: The Basics', kind: 'room' })))
  })

  it('marks a room done without any points', async () => {
    render(<ThmProgress />)
    fireEvent.click(await screen.findByLabelText('Oznacz jako zrobione'))
    await waitFor(() => expect(api.updateThmEntry).toHaveBeenCalledWith(7, { done: true }))
    expect(screen.queryByText(/XP/)).not.toBeInTheDocument()
  })

  it('turns the notes into flashcards', async () => {
    api.flashcardsFromNotes.mockResolvedValue({ created: 3 })
    render(<ThmProgress />)
    fireEvent.click(await screen.findByText('Zrób fiszki z notatek'))
    expect(await screen.findByText('Dodano 3 fiszki do powtórek.')).toBeInTheDocument()
    expect(api.flashcardsFromNotes).toHaveBeenCalledWith(1, 'Nmap', entry.notes)
  })
})

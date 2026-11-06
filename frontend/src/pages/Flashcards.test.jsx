import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Flashcards from './Flashcards'

const api = vi.hoisted(() => ({
  getUserId: vi.fn(() => 1),
  getDueFlashcards: vi.fn(),
  reviewFlashcard: vi.fn(),
  downloadAnki: vi.fn(),
  triggerDownload: vi.fn(),
  quickCreateFlashcard: vi.fn(),
  addToolDeck: vi.fn(),
}))
vi.mock('../api/client', () => api)

const card = { id: 3, front: 'nmap: która flaga wykrywa wersje usług?', back: '-sV', example: 'nmap -sV 10.10.10.10' }

beforeEach(() => vi.clearAllMocks())

describe('Flashcards', () => {
  it('reveals the answer and sends an FSRS rating', async () => {
    api.getDueFlashcards.mockResolvedValue([card])
    api.reviewFlashcard.mockResolvedValue({})
    render(<Flashcards />)
    expect(await screen.findByText(card.front)).toBeInTheDocument()
    fireEvent.click(screen.getByText(/Pokaż odpowiedź/))
    fireEvent.click(screen.getByText(/Dobre/))
    await waitFor(() => expect(api.reviewFlashcard).toHaveBeenCalledWith(3, 3))
    expect(await screen.findByText('Sesja ukończona!')).toBeInTheDocument()
  })

  it('adds the tool syntax deck from the empty screen', async () => {
    api.getDueFlashcards.mockResolvedValueOnce([]).mockResolvedValueOnce([card])
    api.addToolDeck.mockResolvedValue({ added: 24, deck_size: 24 })
    render(<Flashcards />)
    fireEvent.click(await screen.findByText('Talia narzędzi'))
    expect(await screen.findByText(card.front)).toBeInTheDocument()
    expect(api.addToolDeck).toHaveBeenCalledWith(1)
  })
})

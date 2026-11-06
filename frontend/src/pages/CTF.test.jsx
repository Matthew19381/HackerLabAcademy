import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import CTF from './CTF'

const api = vi.hoisted(() => ({
  getUserId: vi.fn(() => 1),
  getCtfChallenges: vi.fn(),
  takeCtfHint: vi.fn(),
  submitCtfFlag: vi.fn(),
}))
vi.mock('../api/client', () => api)

const challenge = { id: 3, title: 'Ciasteczko w Base64', description: 'debug=RkxB', category: 'web', difficulty: 1,
  points: 50, has_hint: true, solved: false, points_earned: 0, hint: null, solution: null }

beforeEach(() => {
  vi.clearAllMocks()
  api.getCtfChallenges.mockResolvedValue([challenge])
})

describe('CTF', () => {
  it('submits the flag for the current user and has no leaderboard', async () => {
    api.submitCtfFlag.mockResolvedValue({ correct: true, points_earned: 50, message: 'Flaga przyjęta! +50 XP' })
    render(<CTF />)
    fireEvent.change(await screen.findByLabelText('Flaga'), { target: { value: 'FLAG{CIASTECZKO_ODKODOWANE}' } })
    fireEvent.click(screen.getByText('Sprawdź'))
    await waitFor(() => expect(api.submitCtfFlag).toHaveBeenCalledWith(3, 1, 'FLAG{CIASTECZKO_ODKODOWANE}'))
    expect(screen.queryByText(/Leaderboard|Ranking/i)).not.toBeInTheDocument()
  })

  it('warns that a hint halves the points before taking it', async () => {
    api.takeCtfHint.mockResolvedValue({ hint: 'base64 -d', points_if_solved: 25 })
    render(<CTF />)
    const button = await screen.findByText(/połowę punktów/)
    fireEvent.click(button)
    await waitFor(() => expect(api.takeCtfHint).toHaveBeenCalledWith(3, 1))
  })
})

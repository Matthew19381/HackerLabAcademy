import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Practice from './Practice'

const api = vi.hoisted(() => ({
  getUserId: vi.fn(() => 1),
  getTopics: vi.fn(),
  completeLab: vi.fn(),
  getWriteupTemplates: vi.fn(() => Promise.resolve([])),
  generateWriteup: vi.fn(),
  downloadWriteupPdf: vi.fn(),
}))
vi.mock('../api/client', () => api)

beforeEach(() => vi.clearAllMocks())

describe('Practice', () => {
  it('links to TryHackMe and saves the write-up - no Docker controls', async () => {
    api.getTopics.mockResolvedValue([
      { slug: 'sql-injection', name: 'SQL Injection', practice_hint: 'SQL Injection', unlocked: true, theory_completed: true },
      { slug: 'http-basics', name: 'HTTP', practice_hint: null, unlocked: true, theory_completed: true },
    ])
    api.completeLab.mockResolvedValue({ xp_awarded: 50, writeup: { title: 'SQLi', key_lessons: [] }, new_achievements: [] })
    render(<Practice />)

    const link = await screen.findByText(/Szukaj pokoi na TryHackMe/)
    expect(link.closest('a').getAttribute('href')).toContain('searchText=SQL%20Injection')
    expect(screen.queryByText('HTTP')).not.toBeInTheDocument()
    expect(screen.queryByText(/Uruchom|DVWA|Docker/)).not.toBeInTheDocument()

    fireEvent.change(screen.getByPlaceholderText(/Jaki payload/), { target: { value: "' OR 1=1 --" } })
    fireEvent.click(screen.getByText(/Zapisz praktykę/))
    await waitFor(() => expect(api.completeLab).toHaveBeenCalledWith('sql-injection', 1, expect.objectContaining({ exploitation: "' OR 1=1 --" })))
  })
})

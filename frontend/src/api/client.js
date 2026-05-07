import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error)
)

// --- User ---
export const createUser = (name) => api.post('/placement/user', { name })
export const getUser = (userId) => api.get(`/placement/user/${userId}`)

// --- Stats ---
export const getStats = (userId) => api.get(`/stats/${userId}`)
export const getAchievements = (userId) => api.get(`/stats/${userId}/achievements`)
export const getAnalytics = (userId) => api.get(`/stats/${userId}/analytics`)

// --- Topics ---
export const getTopics = (userId) => api.get(`/topics/?user_id=${userId}`)
export const getTheory = (slug, userId) => api.get(`/topics/${slug}/theory?user_id=${userId}`)
export const submitQuiz = (slug, userId, answers, responseTimes = {}) =>
  api.post(`/topics/${slug}/quiz`, { user_id: userId, answers, response_times: responseTimes })
export const completeLab = (slug, userId, writeupSteps) =>
  api.post(`/topics/${slug}/lab/complete`, { user_id: userId, writeup_steps: writeupSteps })

// --- Labs ---
export const getLabStatus = () => api.get('/labs/status')
export const startLab = () => api.post('/labs/start')
export const stopLab = () => api.post('/labs/stop')
export const resetLab = () => api.post('/labs/reset')
export const getLabUrl = (labType) => api.get(`/labs/url/${labType}`)

// --- Flashcards ---
export const getDueFlashcards = (userId) => api.get(`/flashcards/due/${userId}`)
export const getAllFlashcards = (userId) => api.get(`/flashcards/all/${userId}`)
export const reviewFlashcard = (cardId, rating) => api.post(`/flashcards/${cardId}/review`, { rating })
export const deleteFlashcard = (cardId) => api.delete(`/flashcards/${cardId}`)
export const quickCreateFlashcard = (userId, term) => api.post('/flashcards/quick-create', { user_id: userId, term })
export const createFlashcardFromCve = (cveId, data) => api.post(`/cves/${cveId}/flashcard`, data)

// --- CVE Explorer ---
export const getCves = (params = {}) => {
  const search = new URLSearchParams()
  if (params.topic_slug) search.append('topic_slug', params.topic_slug)
  if (params.severity) search.append('severity', params.severity)
  if (params.limit) search.append('limit', params.limit)
  return api.get(`/cves/?${search.toString()}`)
}

// --- YouTube Videos ---
export const getVideos = (params = {}) => {
  const search = new URLSearchParams()
  if (params.topic_slug) search.append('topic_slug', params.topic_slug)
  if (params.category) search.append('category', params.category)
  if (params.limit) search.append('limit', params.limit)
  return api.get(`/videos/?${search.toString()}`)
}
export const getVideosByTopic = () => api.get('/videos/topics')

// --- CTF Challenges ---
export const getCtfChallenges = (params = {}) => {
  const search = new URLSearchParams()
  if (params.category) search.append('category', params.category)
  if (params.difficulty) search.append('difficulty', params.difficulty)
  if (params.limit) search.append('limit', params.limit)
  return api.get(`/ctf/challenges/?${search.toString()}`)
}
export const submitFlag = (challengeId, userId, flag) => api.post(`/ctf/challenges/${challengeId}/submit`, { user_id: userId, flag })
export const getLeaderboard = (limit = 20) => api.get(`/ctf/leaderboard?limit=${limit}`)

// --- Defense Mode ---
export const getDefenseChallenges = (params = {}) => {
  const search = new URLSearchParams()
  if (params.topic_slug) search.append('topic_slug', params.topic_slug)
  if (params.difficulty) search.append('difficulty', params.difficulty)
  if (params.limit) search.append('limit', params.limit)
  return api.get(`/defense/challenges/?${search.toString()}`)
}
export const getDefenseChallenge = (challengeId) => api.get(`/defense/challenges/${challengeId}`)
export const submitDefenseFix = (challengeId, userId, submittedCode) =>
  api.post(`/defense/submit`, { challenge_id: challengeId, user_id: userId, submitted_code: submittedCode })

// --- Certificates ---
export const listCertificates = (userId) => api.get(`/certificates/list?user_id=${userId}`)
export const generateCertificate = (category, userId) =>
  api.get(`/certificates/generate?category=${encodeURIComponent(category)}&user_id=${userId}`)
export const downloadCertificate = (certificateCode) =>
  axios.get(`/certificates/download/${certificateCode}`, { responseType: 'blob' })

// --- Attack Scenarios ---
export const getAttackScenarios = () => api.get('/attack/scenarios')
export const getCurrentStep = (scenarioId, userId) => api.get(`/attack/scenarios/${scenarioId}/current?user_id=${userId}`)
export const startAttackScenario = (scenarioId, userId) => api.post(`/attack/scenarios/${scenarioId}/start`, { user_id: userId })
export const submitAttackAnswer = (scenarioId, userId, answer) => api.post(`/attack/scenarios/${scenarioId}/submit`, { user_id: userId, answer })

// --- Exercises ---
export const getExercises = (topicId) => api.get(`/exercises/topics/${topicId}`)
export const submitExercise = (exerciseId, userId, userAnswer) =>
  api.post('/exercises/submit', { exercise_id: exerciseId, user_id: userId, user_answer: userAnswer })
export const generateExercises = (topicId, count = 5) =>
  api.post(`/exercises/topics/${topicId}/generate`, { count })

// --- Conversation Practice ---
export const startConversationSession = (userId, topicSlug = null) =>
  api.post('/conversation/sessions/start', { user_id: userId, topic_slug: topicSlug })
export const getNextQuestion = (sessionId) =>
  api.post(`/conversation/sessions/${sessionId}/question`)
export const submitAnswer = (sessionId, userAnswer) =>
  api.post(`/conversation/sessions/${sessionId}/answer`, { user_answer: userAnswer })
export const endConversationSession = (sessionId) =>
  api.post(`/conversation/sessions/${sessionId}/end`)
export const listConversationSessions = (userId) =>
  api.get(`/conversation/sessions/user/${userId}`)

// --- Mentor ---
export const mentorChat = (sessionId, message, topicContext = null) =>
  api.post('/mentor/chat', { session_id: sessionId, message, topic_context: topicContext })
export const clearMentorSession = (sessionId) => api.delete(`/mentor/session/${sessionId}`)

// --- Error Loop ---
export const getDueErrors = (userId) => api.get(`/errors/due/${userId}`)
export const getErrorStats = (userId) => api.get(`/errors/stats/${userId}`)
export const reviewError = (errorId, correct) => api.post(`/errors/${errorId}/review`, { correct })

// --- Learning Brain ---
export const getDailyAgenda = (userId) => api.get(`/brain/today/${userId}`)

// --- Vocabulary & Resources ---
export const getTopicVocabulary = (slug) => api.get(`/vocabulary/topic/${slug}`)
export const getTopicResources = (slug) => api.get(`/vocabulary/topic/${slug}/resources`)

// --- Daily Status ---
export const getDailyStatus = (userId) => api.get('/daily/status', { params: { user_id: userId } })

// --- Articles ---
export const getArticles = (params = {}) => {
  const search = new URLSearchParams()
  if (params.topic_slug) search.append('topic_slug', params.topic_slug)
  if (params.difficulty) search.append('difficulty', params.difficulty)
  if (params.limit) search.append('limit', params.limit)
  return api.get(`/articles/?${search.toString()}`)
}
export const getArticle = (slug) => api.get(`/articles/${slug}`)
export const markArticleRead = (slug, userId, readTimeSec = null) =>
  api.post(`/articles/${slug}/read`, { user_id: userId, read_time_seconds: readTimeSec })
export const submitArticleQuiz = (slug, userId, answers) =>
  api.post(`/articles/${slug}/quiz/submit`, { user_id: userId, answers })

// --- Write-up Templates ---
export const getWriteupTemplates = (category = null) => {
  const search = new URLSearchParams()
  if (category) search.append('category', category)
  return api.get(`/writeups/templates?${search.toString()}`)
}
export const generateWriteup = (userId, templateId, variables, title = null) =>
  api.post('/writeups/generate', { user_id: userId, template_id: templateId, variables, title })
export const getWriteupHistory = (userId) => api.get(`/writeups/history/${userId}`)
export const downloadWriteupPdf = (writeupId) =>
  axios.get(`/api/writeups/download/${writeupId}`, { responseType: 'blob', timeout: 30000 })

// --- Downloads (raw axios for file blobs) ---
export const downloadLessonPDF = (slug) =>
  axios.get(`/api/download/lesson/${slug}/pdf`, { responseType: 'blob', timeout: 60000 })
export const downloadLessonAudio = (slug) =>
  axios.get(`/api/download/lesson/${slug}/audio`, { responseType: 'blob', timeout: 120000 })
export const downloadLessonBundle = (slug) =>
  axios.get(`/api/download/lesson/${slug}/bundle`, { responseType: 'blob', timeout: 180000 })
export const downloadAnki = (userId) =>
  axios.get(`/api/download/flashcards/${userId}/anki`, { responseType: 'blob', timeout: 30000 })

// --- Local storage helpers ---
export const getUserId = () => {
  const id = localStorage.getItem('hackerlabacademy_user_id')
  return id ? parseInt(id) : null
}
export const setUserId = (id) => localStorage.setItem('hackerlabacademy_user_id', String(id))
export const clearUser = () => localStorage.removeItem('hackerlabacademy_user_id')

// --- Blob download helper ---
export const triggerDownload = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
}

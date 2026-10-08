const TOKEN_KEY = 'pasteur_token'

export const tokenStore = {
  get: () => {
    try { return localStorage.getItem(TOKEN_KEY) } catch { return null }
  },
  set: (t) => {
    try { t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY) } catch { /* sin almacenamiento */ }
  },
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = tokenStore.get()
  if (token) headers.Authorization = `Bearer ${token}`
  let res
  try {
    res = await fetch(`/api${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined })
  } catch {
    throw new ApiError('No se pudo conectar con el servidor. ¿Está encendido el backend?', 0)
  }
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    if (res.status === 401) window.dispatchEvent(new Event('pasteur:unauthorized'))
    const detail = Array.isArray(data.detail) ? 'Revisa los datos ingresados' : data.detail
    throw new ApiError(detail || 'Ocurrió un error, inténtalo otra vez', res.status)
  }
  return data
}

export const api = {
  login: (identifier, password) => request('/auth/login', { method: 'POST', body: { identifier, password } }),
  register: (payload) => request('/auth/register', { method: 'POST', body: payload }),
  forgot: () => request('/auth/forgot', { method: 'POST' }),
  me: () => request('/auth/me'),

  dashboard: () => request('/dashboard'),
  answerChallenge: (id, option) => request(`/challenge/${id}/answer`, { method: 'POST', body: { option } }),

  routes: (course) => request(`/routes${course ? `?course=${course}` : ''}`),
  route: (id) => request(`/routes/${id}`),
  answerActivity: (id, option) => request(`/activities/${id}/answer`, { method: 'POST', body: { option } }),

  assessments: () => request('/assessments'),
  assessment: (id) => request(`/assessments/${id}`),
  checkQuestion: (id, option, confidence) =>
    request(`/assessments/questions/${id}/check`, { method: 'POST', body: { option, confidence } }),

  tutorSession: (course) => request(`/tutor/session?course=${course}`),
  tutorReset: (course) => request('/tutor/reset', { method: 'POST', body: { course } }),
  tutorMessage: (course, message, session_id) =>
    request('/tutor/message', { method: 'POST', body: { course, message, session_id } }),

  metrics: () => request('/metrics'),
}

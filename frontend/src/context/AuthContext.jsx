import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { api, tokenStore } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(tokenStore.get()))

  const logout = useCallback(() => {
    tokenStore.set(null)
    setUser(null)
  }, [])

  useEffect(() => {
    if (!tokenStore.get()) return
    api.me().then(setUser).catch(logout).finally(() => setLoading(false))
  }, [logout])

  useEffect(() => {
    window.addEventListener('pasteur:unauthorized', logout)
    return () => window.removeEventListener('pasteur:unauthorized', logout)
  }, [logout])

  const startSession = (data) => {
    tokenStore.set(data.token)
    setUser(data.user)
    return data
  }

  const login = async (identifier, password) => startSession(await api.login(identifier, password))
  const register = async (payload) => startSession(await api.register(payload))

  // Actualiza puntos/racha en la barra superior tras ganar puntos
  const setPoints = (points) => setUser((u) => (u ? { ...u, points } : u))
  const refresh = () => api.me().then(setUser).catch(() => {})

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, setPoints, refresh }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)

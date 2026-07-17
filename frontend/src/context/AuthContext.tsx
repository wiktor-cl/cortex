import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api, setAuthToken } from '../api/client'
import type { AuthResponse, Role } from '../api/types'

interface Session {
  token: string
  userId: string
  email: string
  role: Role
}

interface AuthContextValue {
  session: Session | null
  isAdmin: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
}

const STORAGE_KEY = 'cortex.session'

const AuthContext = createContext<AuthContextValue | null>(null)

function readStoredSession(): Session | null {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as Session
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(() => readStoredSession())

  useEffect(() => {
    setAuthToken(session?.token ?? null)
  }, [session])

  const applyAuthResponse = (response: AuthResponse) => {
    const next: Session = {
      token: response.token,
      userId: response.userId,
      email: response.email,
      role: response.role,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
    setSession(next)
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      isAdmin: session?.role === 'ADMIN',
      login: async (email, password) => {
        const response = await api.post<AuthResponse>('/auth/login', { email, password })
        applyAuthResponse(response)
      },
      register: async (email, password) => {
        const response = await api.post<AuthResponse>('/auth/register', { email, password })
        applyAuthResponse(response)
      },
      logout: () => {
        localStorage.removeItem(STORAGE_KEY)
        setSession(null)
      },
    }),
    [session],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}

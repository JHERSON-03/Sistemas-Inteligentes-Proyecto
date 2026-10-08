import { createContext, useCallback, useContext, useState } from 'react'

const ToastContext = createContext(null)

const TONES = {
  success: 'border-success/40 bg-[#123326] text-success',
  info: 'border-primary/40 bg-[#16224a] text-[#b5c4ff]',
  warn: 'border-streak/40 bg-[#3a2410] text-streak',
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const toast = useCallback((message, tone = 'success') => {
    const id = Date.now() + Math.random()
    setToasts((t) => [...t, { id, message, tone }])
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3200)
  }, [])

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div className="fixed bottom-6 left-1/2 z-50 flex -translate-x-1/2 flex-col items-center gap-2" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={`animate-pop rounded-2xl border px-5 py-3 font-bold shadow-soft ${TONES[t.tone]}`}>
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export const useToast = () => useContext(ToastContext)

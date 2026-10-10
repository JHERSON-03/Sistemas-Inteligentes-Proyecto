import { useEffect, useRef, useState } from 'react'
import { Info, RotateCcw, Send, Star } from 'lucide-react'
import { api } from '../api/client'
import { COURSES, ErrorBox, Loading } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

// Ritmo del tutor: pausa mínima "pensando" y velocidad de escritura (ms por carácter)
const THINK_MIN_MS = 1500
const THINK_EXTRA_MS = 1000
const TYPE_MS_PER_CHAR = 30

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

/** Muestra el texto poco a poco, como si el tutor lo estuviera escribiendo. */
function TypewriterText({ text, onTick, onDone }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (count >= text.length) {
      onDone?.()
      return
    }
    // Pausa un poco más tras signos de puntuación para que se lea natural
    const prev = text[count - 1]
    const delay = '.?!'.includes(prev) ? TYPE_MS_PER_CHAR * 10 : ',;:'.includes(prev) ? TYPE_MS_PER_CHAR * 4 : TYPE_MS_PER_CHAR
    const id = setTimeout(() => { setCount((c) => c + 1); onTick?.() }, delay)
    return () => clearTimeout(id)
  }, [count, text]) // eslint-disable-line react-hooks/exhaustive-deps

  return <>{text.slice(0, count)}<span className="ml-0.5 inline-block h-4 w-1.5 animate-pulse bg-tutor align-middle" /></>
}

function Bubble({ role, children }) {
  const mine = role === 'user'
  return (
    <div className={`flex items-end gap-2 ${mine ? 'justify-end' : ''}`}>
      {!mine && <img src="/img/robot-tutor.jpg" alt="" className="h-8 w-8 shrink-0 rounded-full object-cover" />}
      <div className={`animate-pop max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-3 leading-relaxed ${
        mine ? 'rounded-br-sm bg-navy text-white' : 'rounded-bl-sm border border-line bg-card text-ink'}`}>
        {children}
      </div>
    </div>
  )
}

export default function Tutor() {
  const { setPoints } = useAuth()
  const toast = useToast()
  const [course, setCourse] = useState('matematica')
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [thinking, setThinking] = useState(false)
  const [typing, setTyping] = useState(false)
  const [error, setError] = useState('')
  const endRef = useRef(null)

  const load = (c) => {
    setSession(null)
    setError('')
    setTyping(false)
    api.tutorSession(c).then((s) => { setSession(s); setMessages(s.messages) }).catch((e) => setError(e.message))
  }
  useEffect(() => { load(course) }, [course])
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }) }, [messages, thinking])

  const send = async (content) => {
    const msg = content.trim()
    if (!msg || thinking || typing) return
    setText('')
    setMessages((m) => [...m, { role: 'user', content: msg }])
    setThinking(true)
    const started = Date.now()
    try {
      const res = await api.tutorMessage(course, msg, session.session_id)
      // El tutor "piensa" al menos un momento aunque la IA responda al instante
      const pause = THINK_MIN_MS + Math.random() * THINK_EXTRA_MS - (Date.now() - started)
      if (pause > 0) await sleep(pause)
      setThinking(false)
      setTyping(true)
      setMessages((m) => [...m, { role: 'assistant', content: res.reply, animate: true }])
      setSession((s) => ({ ...s, session_id: res.session_id }))
      if (res.points_earned) {
        setPoints(res.total_points)
        toast(`+${res.points_earned} pts por tu sesión con el tutor ⭐`)
      }
    } catch (e) {
      setThinking(false)
      setMessages((m) => [...m, { role: 'assistant', content: `⚠️ ${e.message}` }])
    }
  }

  const finishTyping = (index) => {
    setTyping(false)
    setMessages((m) => m.map((x, i) => (i === index ? { ...x, animate: false } : x)))
  }
  const scrollToEnd = () => endRef.current?.scrollIntoView({ block: 'end' })
  const busy = thinking || typing

  const reset = async () => {
    const s = await api.tutorReset(course)
    setSession((prev) => ({ ...prev, ...s }))
    setMessages([])
    setTyping(false)
  }

  if (error) return <ErrorBox message={error} onRetry={() => load(course)} />

  return (
    <div className="card flex h-[calc(100vh-11rem)] min-h-[560px] flex-col overflow-hidden">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line bg-card p-4">
        <div className="flex items-center gap-3">
          <img src="/img/robot-tutor.jpg" alt="" className="h-12 w-12 rounded-xl border border-line object-cover" />
          <div>
            <h1 className="text-lg font-extrabold leading-tight">Tutor IA Socrático</h1>
            <span className="mt-0.5 inline-flex items-center gap-1.5 text-xs font-bold text-success">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-60" />
                <span className="relative h-2 w-2 rounded-full bg-success" />
              </span> En línea
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <select className="input w-auto py-2" value={course} onChange={(e) => setCourse(e.target.value)} aria-label="Curso">
            {COURSES.map((c) => <option key={c.slug} value={c.slug}>{c.name}</option>)}
          </select>
          <button className="btn-outline py-2" onClick={reset}><RotateCcw size={16} /> <span className="hidden sm:inline">Reiniciar diálogo</span></button>
        </div>
      </header>

      <div className="flex gap-3 border-b border-line bg-navy/[0.04] px-4 py-3 text-sm text-primary-soft">
        <Info size={18} className="shrink-0" />
        <p><b>Método socrático:</b> el tutor no te da la respuesta directa; te guía con preguntas y pistas para que la descubras tú.</p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto bg-bg/60 p-4 md:px-6">
        {!session ? <Loading label="Conectando con tu tutor…" /> : (
          <>
            <Bubble role="assistant">{session.greeting}</Bubble>
            {messages.map((m, i) => (
              <Bubble key={i} role={m.role}>
                {m.animate
                  ? <TypewriterText text={m.content} onTick={scrollToEnd} onDone={() => finishTyping(i)} />
                  : m.content}
              </Bubble>
            ))}
            {thinking && (
              <Bubble role="assistant">
                <span className="typing text-xl leading-none"><span>•</span><span>•</span><span>•</span></span>
              </Bubble>
            )}
          </>
        )}
        <div ref={endRef} />
      </div>

      <footer className="space-y-3 border-t border-line bg-card p-4">
        {session && messages.length === 0 && (
          <div className="flex flex-wrap gap-2">
            {session.suggestions.map((s) => (
              <button key={s} onClick={() => send(s)} disabled={busy} className="chip border border-line bg-card font-semibold text-ink/80 transition hover:border-navy/40 hover:text-navy active:scale-[.97] disabled:opacity-50">{s}</button>
            ))}
          </div>
        )}
        <form onSubmit={(e) => { e.preventDefault(); send(text) }} className="flex gap-2">
          <input className="input" placeholder="Escribe tu pregunta o cuéntame qué intentaste…" value={text}
            onChange={(e) => setText(e.target.value)} disabled={!session} />
          <button className="btn-primary" disabled={!text.trim() || busy || !session}>
            <Send size={16} /> <span className="hidden sm:inline">Preguntar</span>
          </button>
        </form>
        <p className="flex items-center gap-1 text-xs text-muted">
          <Star size={12} className="text-gold" /> +{session?.points_per_session ?? 5} pts por cada sesión con el tutor
        </p>
      </footer>
    </div>
  )
}

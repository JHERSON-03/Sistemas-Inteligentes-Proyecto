import { useEffect, useRef, useState } from 'react'
import { CheckCircle2, Gamepad2, RotateCcw, Timer, Trophy, XCircle } from 'lucide-react'
import { api } from '../api/client'
import { ErrorBox, Loading, ProgressBar } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useApi } from '../hooks/useApi'

const HIT = 10
const MISS = -5

// Globos con los colores del escudo: azul marino y dorado
const SCHOOL_TONES = [
  { body: 'bg-navy text-white', shard: 'bg-navy' },
  { body: 'bg-accent text-navy', shard: 'bg-accent' },
]

// Pedazos del globo al reventar: salen en círculo con distancia y giro algo distintos
const SHARDS = Array.from({ length: 9 }, (_, k) => {
  const angle = (k / 9) * 2 * Math.PI + 0.3
  const dist = 3 + (k % 3) * 0.8
  return {
    dx: `${(Math.cos(angle) * dist).toFixed(2)}rem`,
    dy: `${(Math.sin(angle) * dist).toFixed(2)}rem`,
    rot: `${(k % 2 ? 1 : -1) * (120 + k * 25)}deg`,
    size: ['h-2.5 w-3.5', 'h-2 w-2.5', 'h-3 w-2'][k % 3],
  }
})

const FALL_MIN = 4.5
const FALL_MAX = 6.5
const FIRST_DELAY = 1.2
const DELAY_JITTER = 0.5

const RULES = [
  { Icon: CheckCircle2, color: 'text-success', text: `Revienta un globo correcto: +${HIT} puntos.` },
  { Icon: XCircle, color: 'text-red-600', text: `Revienta uno incorrecto: ${MISS} puntos.` },
  { Icon: Timer, color: 'text-navy', text: 'Si dejas caer una correcta no pierdes nada.' },
]

/** Reparte los globos a lo largo de la ronda con posición y velocidad al azar. */
function makeBubbles(items, seconds) {
  // El último globo debe terminar de caer antes de que se acabe el tiempo
  const spread = seconds - FIRST_DELAY - DELAY_JITTER - FALL_MAX - 0.3
  return items.map((text, i) => ({
    i,
    text,
    tone: SCHOOL_TONES[i % SCHOOL_TONES.length],
    left: 18 + Math.random() * 64,
    duration: FALL_MIN + Math.random() * (FALL_MAX - FALL_MIN),
    delay: FIRST_DELAY + (i / Math.max(1, items.length - 1)) * spread + Math.random() * DELAY_JITTER,
    state: 'falling', // falling | checking | good | bad | gone
  }))
}

function PlaysLeft({ left, max }) {
  return (
    <span className={`chip num border ${left ? 'border-navy/20 text-navy' : 'border-red-600/30 bg-red-600/[0.08] text-red-600'}`}>
      <Gamepad2 size={16} /> {left ? `Te ${left === 1 ? 'queda' : 'quedan'} ${left} de ${max} partidas hoy` : 'Ya usaste tus partidas de hoy'}
    </span>
  )
}

function Ranking({ ranking }) {
  return (
    <div className="card p-5">
      <h2 className="mb-3 flex items-center gap-2 font-extrabold"><Trophy size={18} className="text-gold" /> Mejores puntajes</h2>
      {ranking.error && <p className="text-sm text-muted">{ranking.error}</p>}
      {ranking.data?.top.length === 0 && <p className="text-sm text-muted">Nadie ha jugado todavía. ¡Sé el primero! 🚀</p>}
      <ol className="divide-y divide-line text-sm">
        {ranking.data?.top.map((r) => (
          <li key={r.position} className={`-mx-2 flex items-center justify-between px-2 py-2 ${r.me ? 'rounded-md bg-navy/[0.06] font-bold' : ''}`}>
            <span><b className="num mr-2 inline-block w-6">{['🥇', '🥈', '🥉'][r.position - 1] || `${r.position}.`}</b>{r.name}</span>
            <span className="num font-bold text-gold">{r.score}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}

/** Pita del globo: una línea ondulada que cuelga del nudo. */
function BalloonString({ className = '' }) {
  return (
    <svg width="14" height="34" viewBox="0 0 14 34" aria-hidden="true" className={`mx-auto text-navy/45 ${className}`}>
      <path d="M7 0 C 1 7, 13 13, 7 20 S 3 30, 7 34" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
    </svg>
  )
}

function Bubble({ bubble, onCatch, onGone }) {
  const { state, text, tone } = bubble
  const popped = state !== 'falling'
  const result = state === 'good' || state === 'bad'
  const size = text.length <= 3 ? 'text-2xl' : 'px-2 text-[13px] leading-tight sm:text-sm'
  return (
    <div className="animate-fall absolute"
      style={{
        left: `${bubble.left}%`, transform: 'translateX(-50%)',
        '--fall-duration': `${bubble.duration}s`, '--fall-delay': `${bubble.delay}s`,
        animationPlayState: popped ? 'paused' : 'running',
      }}
      // Desaparece al salir por abajo o cuando termina de subir el "+10 / -5"
      onAnimationEnd={(e) => (e.animationName === 'fall' || e.animationName === 'float-up') && onGone(bubble.i)}>
      {!popped ? (
        <>
          <button type="button" tabIndex={-1}
            // pointerdown revienta al primer toque, aunque el globo se mueva antes de soltar el dedo
            onPointerDown={() => onCatch(bubble.i)}
            className={`balloon num touch-manipulation select-none text-center font-extrabold transition hover:brightness-110 ${tone.body} ${size}`}>
            <span className="relative [overflow-wrap:anywhere]">{text}</span>
          </button>
          <BalloonString />
        </>
      ) : (
        // Al reventar: el globo se infla un instante y desaparece, los pedazos salen volando y la pita cae
        <div className="pointer-events-none relative">
          <div className={`balloon animate-balloon-pop ${tone.body}`} />
          <BalloonString className="animate-string-fall" />
          {SHARDS.map((s, k) => (
            <span key={k} className={`animate-shard absolute left-1/2 top-[42%] rounded-[3px] ${s.size} ${tone.shard}`}
              style={{ '--dx': s.dx, '--dy': s.dy, '--rot': s.rot }} />
          ))}
          {result && (
            <>
              <span className={`animate-flash absolute left-1/2 top-[42%] h-24 w-24 rounded-full border-4 ${state === 'good' ? 'border-success bg-success/20' : 'border-red-600 bg-red-600/20'}`} />
              <span className={`animate-float-up absolute left-1/2 top-[30%] text-2xl font-extrabold drop-shadow-sm ${state === 'good' ? 'text-success' : 'text-red-600'}`}>
                {state === 'good' ? `+${HIT}` : MISS}
              </span>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default function AtrapaRespuesta() {
  const { setPoints } = useAuth()
  const toast = useToast()
  const ranking = useApi(() => api.atrapaRanking(), [])
  const [phase, setPhase] = useState('intro') // intro | loading | playing | sending | done
  const [round, setRound] = useState(null)
  const [bubbles, setBubbles] = useState([])
  const [timeLeft, setTimeLeft] = useState(0)
  const [live, setLive] = useState({ score: 0, hits: 0, misses: 0 })
  const [result, setResult] = useState(null)
  const caught = useRef(new Set())
  const roundRef = useRef(null)

  const setBubbleState = (i, state) => setBubbles((bs) => bs.map((b) => (b.i === i ? { ...b, state } : b)))

  const start = async () => {
    setPhase('loading')
    try {
      const r = await api.atrapaRonda()
      roundRef.current = r
      caught.current = new Set()
      setRound({ ...r, startedAt: Date.now() })
      setBubbles(makeBubbles(r.elementos, r.duracion))
      setLive({ score: 0, hits: 0, misses: 0 })
      setTimeLeft(r.duracion)
      setResult(null)
      setPhase('playing')
    } catch (e) {
      toast(e.message, 'warn')
      setPhase(result ? 'done' : 'intro')
    }
  }

  const finish = async () => {
    setPhase('sending')
    try {
      const res = await api.atrapaResultado(roundRef.current.ronda_id, [...caught.current])
      setResult(res)
      setPoints(res.total_points)
      if (res.points_earned > 0) toast(`+${res.points_earned} pts 🎉`)
      ranking.reload()
    } catch (e) {
      setResult({ error: e.message })
    }
    setPhase('done')
  }
  const finishRef = useRef(finish)
  finishRef.current = finish

  // Temporizador: se calcula con la hora real para no desfasarse si la pestaña se queda en segundo plano
  useEffect(() => {
    if (phase !== 'playing') return undefined
    const id = setInterval(() => {
      const left = Math.max(0, round.duracion - (Date.now() - round.startedAt) / 1000)
      setTimeLeft(left)
      if (left <= 0) { clearInterval(id); finishRef.current() }
    }, 200)
    return () => clearInterval(id)
  }, [phase, round])

  const onCatch = (i) => {
    if (phase !== 'playing' || caught.current.has(i)) return
    caught.current.add(i)
    setBubbleState(i, 'checking')
    api.atrapaVerificar(round.ronda_id, i)
      .then(({ correct }) => {
        setBubbleState(i, correct ? 'good' : 'bad')
        setLive((l) => correct
          ? { ...l, score: l.score + HIT, hits: l.hits + 1 }
          : { ...l, score: l.score + MISS, misses: l.misses + 1 })
      })
      .catch(() => setBubbleState(i, 'gone'))
  }

  // Tras una partida, el resultado trae las partidas restantes antes de que el ranking termine de recargarse
  const playsLeft = result && !result.error ? result.plays_left : ranking.data?.plays_left
  const maxPlays = ranking.data?.max_plays ?? 3

  const onGone = (i) => setBubbles((bs) => bs.map((b) => (b.i === i && b.state !== 'checking' ? { ...b, state: 'gone' } : b)))

  const header = (
    <div>
      <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-gold">Minijuego</p>
      <h1 className="mt-1.5 flex items-center gap-2 text-[1.75rem] font-extrabold leading-tight">
        <Gamepad2 className="text-navy" size={28} /> Atrapa la respuesta
      </h1>
    </div>
  )

  if (phase === 'intro' || (phase === 'loading' && !result)) {
    return (
      <div className="mx-auto grid max-w-4xl gap-5 md:grid-cols-[1fr_18rem]">
        <div className="space-y-5">
          {header}
          <div className="card overflow-hidden">
            <div className="h-1 bg-accent" />
            <div className="p-6">
              <p className="text-muted">
                Aparecerá una consigna, por ejemplo <b className="text-ink">“Atrapa los números pares”</b>. Durante 30 segundos caerán
                globos con números o palabras: revienta solo los que cumplen la consigna.
              </p>
              <ul className="mt-4 space-y-2.5">
                {RULES.map(({ Icon, color, text }) => (
                  <li key={text} className="flex items-center gap-3 font-semibold"><Icon size={20} className={`shrink-0 ${color}`} /> {text}</li>
                ))}
              </ul>
              <div className="mt-6 flex flex-wrap items-center gap-3">
                <button className="btn-gold w-full sm:w-auto sm:px-10" disabled={phase === 'loading' || playsLeft === 0} onClick={start}>
                  <Gamepad2 size={18} /> {phase === 'loading' ? 'Preparando…' : playsLeft === 0 ? 'Vuelve mañana' : '¡Jugar!'}
                </button>
                {playsLeft !== undefined && <PlaysLeft left={playsLeft} max={maxPlays} />}
              </div>
            </div>
          </div>
        </div>
        <Ranking ranking={ranking} />
      </div>
    )
  }

  if (phase === 'done' || phase === 'loading') {
    if (result?.error) return <ErrorBox message={result.error} onRetry={start} />
    return (
      <div className="mx-auto grid max-w-4xl gap-5 md:grid-cols-[1fr_18rem]">
        <div className="card animate-pop overflow-hidden text-center">
          <div className="h-1 bg-accent" />
          <div className="p-8">
            <span className="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-full border-2 border-gold/30 bg-gold/[0.08]">
              <Trophy className="text-gold" size={32} />
            </span>
            <h1 className="text-[1.75rem] font-extrabold">¡Se acabó el tiempo!</h1>
            <p className="mt-1 text-sm text-muted">{round.consigna}</p>
            <p className="num mt-5 text-5xl font-extrabold text-navy">{result.score}<span className="ml-1 text-lg text-muted">pts</span></p>
            <div className="mx-auto mt-5 grid max-w-xs grid-cols-2 gap-px overflow-hidden rounded-xl border border-line/80 bg-line/80">
              <div className="bg-card p-3">
                <p className="num text-2xl font-extrabold text-success">{result.hits}</p>
                <p className="text-xs font-bold uppercase tracking-wide text-muted">Aciertos</p>
              </div>
              <div className="bg-card p-3">
                <p className="num text-2xl font-extrabold text-red-600">{result.misses}</p>
                <p className="text-xs font-bold uppercase tracking-wide text-muted">Errores</p>
              </div>
            </div>
            <p className="mt-4 text-sm text-muted">
              {result.points_earned > 0
                ? <>Sumaste <b className="text-gold">{result.points_earned} pts</b> a tu total.</>
                : 'Esta vez no sumaste puntos, ¡la próxima sí! 💪'}
            </p>
            <div className="mt-6 flex flex-col items-center gap-3">
              {playsLeft > 0 ? (
                <button className="btn-primary" disabled={phase === 'loading'} onClick={start}>
                  <RotateCcw size={16} /> {phase === 'loading' ? 'Preparando…' : 'Jugar otra vez'}
                </button>
              ) : <p className="font-bold text-navy">¡Buen trabajo hoy! Mañana tendrás {maxPlays} partidas nuevas. 🌟</p>}
              <PlaysLeft left={playsLeft} max={maxPlays} />
            </div>
          </div>
        </div>
        <Ranking ranking={ranking} />
      </div>
    )
  }

  if (phase === 'sending') return <Loading label="Calculando tu puntaje…" />

  return (
    <div className="mx-auto max-w-3xl space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="animate-pop text-xl font-extrabold leading-tight text-navy sm:text-2xl">{round.consigna}</h1>
        <div className="flex gap-2">
          <span className={`chip num border ${timeLeft <= 10 ? 'border-red-600/30 bg-red-600/[0.08] text-red-600' : 'border-navy/20 text-navy'}`}>
            <Timer size={16} /> {Math.ceil(timeLeft)} s
          </span>
          <span className="chip num border border-gold/25 bg-gold/[0.08] text-gold">{live.score} pts</span>
        </div>
      </div>
      <ProgressBar value={(timeLeft / round.duracion) * 100} color={timeLeft <= 10 ? '#DC2626' : '#A8A028'} height="h-1.5" />

      <div className="relative h-[62vh] min-h-[380px] max-h-[640px] select-none overflow-hidden rounded-xl border border-line border-b-4 border-b-accent bg-card-2
        bg-[radial-gradient(circle_at_20%_10%,rgb(40_64_120/0.08),transparent_45%),radial-gradient(circle_at_85%_70%,rgb(168_160_40/0.16),transparent_50%)]">
        {bubbles.filter((b) => b.state !== 'gone').map((b) => (
          <Bubble key={b.i} bubble={b} onCatch={onCatch} onGone={onGone} />
        ))}
      </div>

      <p className="num flex justify-center gap-5 text-sm font-bold">
        <span className="flex items-center gap-1.5 text-success"><CheckCircle2 size={16} /> {live.hits} aciertos</span>
        <span className="flex items-center gap-1.5 text-red-600"><XCircle size={16} /> {live.misses} errores</span>
      </p>
    </div>
  )
}

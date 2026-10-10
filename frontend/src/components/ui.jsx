import { BookOpen, Calculator, FlaskConical, Landmark, Loader2 } from 'lucide-react'

export const COURSES = [
  { slug: 'historia', name: 'Historia', color: '#D97706', Icon: Landmark },
  { slug: 'ciencia', name: 'Ciencia y Tecnología', color: '#16A34A', Icon: FlaskConical },
  { slug: 'matematica', name: 'Matemática', color: '#2563EB', Icon: Calculator },
  { slug: 'comunicacion', name: 'Comunicación', color: '#DB2777', Icon: BookOpen },
]

export const courseBySlug = (slug) => COURSES.find((c) => c.slug === slug) || COURSES[0]

/** Escudo del I.E.P. Louis Pasteur. lg: portada de login/registro · md: icono junto al nombre en la barra superior */
export function Logo({ size = 'md' }) {
  const box = size === 'lg' ? 'h-28 w-28 sm:h-32 sm:w-32' : 'h-12 w-12'
  return (
    <img src="/img/logo-pasteur.png" alt="Escudo del I.E.P. Louis Pasteur de Laredo"
      className={`${box} shrink-0 object-contain drop-shadow-sm`} />
  )
}

export function ProgressBar({ value, color = '#A8A028', height = 'h-2' }) {
  const pct = Math.max(0, Math.min(100, value))
  return (
    <div className={`${height} w-full overflow-hidden rounded-full bg-navy/10`} role="progressbar" aria-valuenow={pct}
      aria-valuemin={0} aria-valuemax={100}>
      <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, background: color }} />
    </div>
  )
}

export function CourseTag({ course }) {
  const c = courseBySlug(course.slug)
  return (
    <span className="chip text-xs" style={{ background: `${c.color}22`, color: c.color }}>
      <c.Icon size={14} /> {c.name}
    </span>
  )
}

export function Ring({ value, color, size = 64, stroke = 7, children }) {
  const r = (size - stroke) / 2
  const circ = 2 * Math.PI * r
  return (
    <div className="relative grid place-items-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} stroke="rgba(40,64,120,.12)" strokeWidth={stroke} fill="none" />
        <circle cx={size / 2} cy={size / 2} r={r} stroke={color} strokeWidth={stroke} fill="none" strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={circ * (1 - value / 100)} className="transition-all duration-700" />
      </svg>
      <div className="num absolute text-sm font-extrabold">{children ?? `${value}%`}</div>
    </div>
  )
}

export function Loading({ label = 'Cargando…' }) {
  return (
    <div className="grid min-h-[40vh] place-items-center text-muted">
      <div className="flex items-center gap-3 text-sm font-semibold"><Loader2 className="animate-spin text-navy" size={20} /> {label}</div>
    </div>
  )
}

export function ErrorBox({ message, onRetry }) {
  return (
    <div className="card mx-auto max-w-md border-l-4 border-l-streak p-6">
      <p className="mb-4 text-ink/80">{message}</p>
      {onRetry && <button className="btn-primary" onClick={onRetry}>Reintentar</button>}
    </div>
  )
}

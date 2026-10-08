import { BookOpen, Calculator, FlaskConical, GraduationCap, Landmark, Loader2 } from 'lucide-react'

export const COURSES = [
  { slug: 'historia', name: 'Historia', color: '#F59E0B', Icon: Landmark },
  { slug: 'ciencia', name: 'Ciencia y Tecnología', color: '#22C55E', Icon: FlaskConical },
  { slug: 'matematica', name: 'Matemática', color: '#4F7CFF', Icon: Calculator },
  { slug: 'comunicacion', name: 'Comunicación', color: '#EC4899', Icon: BookOpen },
]

export const courseBySlug = (slug) => COURSES.find((c) => c.slug === slug) || COURSES[0]

export function Logo({ size = 'md' }) {
  const box = size === 'lg' ? 'h-14 w-14' : 'h-10 w-10'
  const icon = size === 'lg' ? 30 : 22
  return (
    <div className={`${box} grid place-items-center rounded-2xl bg-gradient-to-br from-primary to-tutor text-white shadow-soft`}>
      <GraduationCap size={icon} />
    </div>
  )
}

export function ProgressBar({ value, color = '#4F7CFF', height = 'h-2' }) {
  const pct = Math.max(0, Math.min(100, value))
  return (
    <div className={`${height} w-full overflow-hidden rounded-full bg-white/10`} role="progressbar" aria-valuenow={pct}
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
        <circle cx={size / 2} cy={size / 2} r={r} stroke="rgba(255,255,255,.1)" strokeWidth={stroke} fill="none" />
        <circle cx={size / 2} cy={size / 2} r={r} stroke={color} strokeWidth={stroke} fill="none" strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={circ * (1 - value / 100)} className="transition-all duration-700" />
      </svg>
      <div className="absolute text-sm font-extrabold">{children ?? `${value}%`}</div>
    </div>
  )
}

export function Loading({ label = 'Cargando…' }) {
  return (
    <div className="grid min-h-[40vh] place-items-center text-muted">
      <div className="flex items-center gap-3"><Loader2 className="animate-spin" /> {label}</div>
    </div>
  )
}

export function ErrorBox({ message, onRetry }) {
  return (
    <div className="card mx-auto max-w-md p-6 text-center">
      <p className="mb-4 text-muted">{message}</p>
      {onRetry && <button className="btn-primary" onClick={onRetry}>Reintentar</button>}
    </div>
  )
}

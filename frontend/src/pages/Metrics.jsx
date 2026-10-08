import { Bot, Flame, Gauge, Star } from 'lucide-react'
import { api } from '../api/client'
import { courseBySlug, ErrorBox, Loading, ProgressBar, Ring } from '../components/ui'
import { useApi } from '../hooks/useApi'

const WEEKDAYS = ['L', 'M', 'M', 'J', 'V', 'S', 'D']

function Calendar({ cal }) {
  const cells = [...Array(cal.first_weekday).fill(null), ...Array.from({ length: cal.days }, (_, i) => i + 1)]
  const studied = new Set(cal.studied)
  return (
    <div className="card p-5">
      <h2 className="mb-4 font-extrabold">Calendario de {cal.month}</h2>
      <div className="grid grid-cols-7 gap-1.5 text-center text-sm">
        {WEEKDAYS.map((d, i) => <span key={i} className="pb-1 text-xs font-bold text-muted">{d}</span>)}
        {cells.map((day, i) => (
          <span key={i} className={`grid aspect-square place-items-center rounded-lg ${
            !day ? '' : day === cal.today ? 'bg-primary font-extrabold text-white'
              : studied.has(day) ? 'bg-streak/15' : 'text-muted'}`}>
            {day && (studied.has(day) && day !== cal.today ? '🔥' : day)}
          </span>
        ))}
      </div>
      <p className="mt-3 text-xs text-muted">🔥 Días en los que estudiaste este mes: {cal.studied.length}</p>
    </div>
  )
}

export default function Metrics() {
  const { data, error, loading, reload } = useApi(() => api.metrics(), [])
  if (loading) return <Loading />
  if (error) return <ErrorBox message={error} onRetry={reload} />

  const totalHours = data.time.reduce((s, t) => s + t.hours, 0) || 1

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-extrabold">Mi progreso {data.year}</h1>
        <span className="chip bg-success/15 text-success">{data.status}</span>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="card p-5">
          <h2 className="mb-4 font-extrabold">Avance por curso</h2>
          <div className="space-y-4">
            {data.courses.map((c) => {
              const { Icon } = courseBySlug(c.slug)
              return (
                <div key={c.slug}>
                  <div className="mb-1.5 flex items-center justify-between text-sm font-bold">
                    <span className="flex items-center gap-2"><Icon size={16} style={{ color: c.color }} /> {c.name}</span>
                    <span style={{ color: c.color }}>{c.percent}%</span>
                  </div>
                  <ProgressBar value={c.percent} color={c.color} height="h-3" />
                </div>
              )
            })}
          </div>
        </section>

        <section className="card p-5">
          <h2 className="mb-4 font-extrabold">¿Cómo uso mi tiempo esta semana?</h2>
          <div className="mb-5 flex h-4 overflow-hidden rounded-full">
            {data.time.map((t) => <div key={t.kind} style={{ width: `${(t.hours / totalHours) * 100}%`, background: t.color }} />)}
          </div>
          <ul className="space-y-3">
            {data.time.map((t) => (
              <li key={t.kind} className="flex items-center justify-between rounded-xl bg-white/5 px-4 py-3">
                <span className="flex items-center gap-3 font-semibold"><span className="h-3 w-3 rounded-full" style={{ background: t.color }} /> {t.label}</span>
                <span className="font-extrabold">{t.hours} h</span>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="card flex items-center gap-4 p-5">
          <span className="grid h-12 w-12 place-items-center rounded-xl bg-streak/15 text-streak"><Flame /></span>
          <div><p className="text-sm text-muted">Racha actual</p><p className="text-2xl font-extrabold">{data.streak} días</p></div>
        </div>
        <div className="card flex items-center gap-4 p-5">
          <span className="grid h-12 w-12 place-items-center rounded-xl bg-gold/15 text-gold"><Star /></span>
          <div><p className="text-sm text-muted">Puntos totales</p><p className="text-2xl font-extrabold">{data.points}</p></div>
        </div>
        <div className="card flex items-center gap-4 p-5">
          <Ring value={(data.autonomy.level / data.autonomy.max) * 100} color="#34D399" size={56} stroke={6}>
            <Gauge size={18} />
          </Ring>
          <div><p className="text-sm text-muted">Nivel de autonomía</p><p className="text-2xl font-extrabold">Nivel {data.autonomy.level} de {data.autonomy.max}</p></div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
        <section className="flex h-fit gap-4 rounded-card border border-primary/30 bg-primary/10 p-5">
          <img src="/img/robot-tutor.jpg" alt="" className="h-14 w-14 shrink-0 rounded-2xl object-cover" />
          <div>
            <h2 className="mb-1 flex items-center gap-2 font-extrabold text-[#b5c4ff]"><Bot size={18} /> Comentario de la IA</h2>
            <p className="leading-relaxed">{data.ai_comment}</p>
            <p className="mt-2 text-sm text-muted">Precisión general: {data.accuracy}% · Récord de racha: {data.best_streak} días</p>
          </div>
        </section>
        <Calendar cal={data.calendar} />
      </div>
    </div>
  )
}

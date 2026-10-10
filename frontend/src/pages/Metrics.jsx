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
      <h2 className="section-title mb-4">Calendario de {cal.month}</h2>
      <div className="num grid grid-cols-7 gap-1 text-center text-sm">
        {WEEKDAYS.map((d, i) => <span key={i} className="pb-1 text-[11px] font-bold uppercase text-muted">{d}</span>)}
        {cells.map((day, i) => (
          <span key={i} className={`grid aspect-square place-items-center rounded-md ${
            !day ? '' : day === cal.today ? 'bg-navy font-extrabold text-white ring-2 ring-accent ring-offset-1'
              : studied.has(day) ? 'border border-streak/25 bg-streak/[0.08]' : 'text-muted'}`}>
            {day && (studied.has(day) && day !== cal.today ? '🔥' : day)}
          </span>
        ))}
      </div>
      <p className="num mt-4 border-t border-dashed border-line pt-3 text-xs text-muted">🔥 Días en los que estudiaste este mes: {cal.studied.length}</p>
    </div>
  )
}

export default function Metrics() {
  const { data, error, loading, reload } = useApi(() => api.metrics(), [])
  if (loading) return <Loading />
  if (error) return <ErrorBox message={error} onRetry={reload} />

  const totalHours = data.time.reduce((s, t) => s + t.hours, 0) || 1

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end gap-3 border-b border-line pb-5">
        <h1 className="text-[1.75rem] font-extrabold leading-tight">Mi progreso <span className="num text-gold">{data.year}</span></h1>
        <span className="chip mb-1 border border-success/30 text-success">{data.status}</span>
      </div>

      {/* Indicadores en una franja dividida, como el resumen del inicio */}
      <div className="grid gap-px overflow-hidden rounded-xl border border-line/80 bg-line/80 sm:grid-cols-3">
        <div className="flex items-center gap-4 bg-card p-5">
          <span className="grid h-11 w-11 place-items-center rounded-lg border border-streak/25 bg-streak/[0.08] text-streak"><Flame size={20} /></span>
          <div><p className="text-xs font-bold uppercase tracking-wider text-muted">Racha actual</p><p className="num font-['Bricolage_Grotesque'] text-2xl font-extrabold">{data.streak} días</p></div>
        </div>
        <div className="flex items-center gap-4 bg-card p-5">
          <span className="grid h-11 w-11 place-items-center rounded-lg border border-gold/25 bg-gold/[0.08] text-gold"><Star size={20} /></span>
          <div><p className="text-xs font-bold uppercase tracking-wider text-muted">Puntos totales</p><p className="num font-['Bricolage_Grotesque'] text-2xl font-extrabold">{data.points}</p></div>
        </div>
        <div className="flex items-center gap-4 bg-card p-5">
          <Ring value={(data.autonomy.level / data.autonomy.max) * 100} color="#0F9F6E" size={52} stroke={5}>
            <Gauge size={18} />
          </Ring>
          <div><p className="text-xs font-bold uppercase tracking-wider text-muted">Nivel de autonomía</p><p className="num font-['Bricolage_Grotesque'] text-2xl font-extrabold">Nivel {data.autonomy.level} de {data.autonomy.max}</p></div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,7fr)_minmax(0,5fr)]">
        <section className="card p-5 md:p-6">
          <h2 className="section-title mb-5">Avance por curso</h2>
          <div className="space-y-5">
            {data.courses.map((c) => {
              const { Icon } = courseBySlug(c.slug)
              return (
                <div key={c.slug}>
                  <div className="mb-2 flex items-center justify-between text-sm font-bold">
                    <span className="flex items-center gap-2"><Icon size={16} style={{ color: c.color }} /> {c.name}</span>
                    <span className="num font-['Bricolage_Grotesque'] text-base" style={{ color: c.color }}>{c.percent}%</span>
                  </div>
                  <ProgressBar value={c.percent} color={c.color} height="h-2" />
                </div>
              )
            })}
          </div>
        </section>

        <section className="card p-5 md:p-6">
          <h2 className="section-title mb-5">¿Cómo uso mi tiempo esta semana?</h2>
          <div className="mb-5 flex h-3 gap-0.5 overflow-hidden rounded-full">
            {data.time.map((t) => <div key={t.kind} style={{ width: `${(t.hours / totalHours) * 100}%`, background: t.color }} />)}
          </div>
          <ul className="divide-y divide-line">
            {data.time.map((t) => (
              <li key={t.kind} className="flex items-center justify-between py-3">
                <span className="flex items-center gap-3 font-semibold"><span className="h-2.5 w-2.5 rounded-sm" style={{ background: t.color }} /> {t.label}</span>
                <span className="num font-extrabold">{t.hours} h</span>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
        <section className="card flex h-fit gap-4 border-l-4 border-l-accent p-5 md:p-6">
          <img src="/img/robot-tutor.jpg" alt="" className="h-14 w-14 shrink-0 rounded-xl border border-line object-cover" />
          <div>
            <h2 className="mb-2 flex items-center gap-2 font-extrabold text-primary-soft"><Bot size={18} /> Comentario de la IA</h2>
            <p className="text-[1.05rem] leading-relaxed">{data.ai_comment}</p>
            <p className="num mt-3 border-t border-dashed border-line pt-3 text-sm text-muted">Precisión general: {data.accuracy}% · Récord de racha: {data.best_streak} días</p>
          </div>
        </section>
        <Calendar cal={data.calendar} />
      </div>
    </div>
  )
}

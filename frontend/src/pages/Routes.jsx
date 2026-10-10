import { useSearchParams, Link } from 'react-router-dom'
import { CheckCircle2, Clock, Lock, Play, Sparkles, Star } from 'lucide-react'
import { api } from '../api/client'
import { COURSES, CourseTag, ErrorBox, Loading, ProgressBar } from '../components/ui'
import { useApi } from '../hooks/useApi'

const LEVEL_STYLE = {
  'básico': 'border-line text-muted',
  intermedio: 'border-primary/30 text-primary-soft',
  avanzado: 'border-success/40 text-success',
}

function RouteCard({ r }) {
  const action = r.status === 'completada' ? { label: 'Ver actividad', cls: 'btn-outline', Icon: CheckCircle2 }
    : r.status === 'pendiente' ? { label: 'Iniciar', cls: 'btn-outline', Icon: Play }
      : { label: 'Continuar', cls: 'btn-primary', Icon: Play }
  const statusText = r.status === 'completada' ? 'Completada' : r.status === 'pendiente' ? 'Sin iniciar'
    : r.percent >= 50 ? `${r.percent}% completado` : `En progreso ${r.percent}%`

  return (
    <article className={`card group relative flex flex-col overflow-hidden p-5 pl-6 transition hover:border-navy/30 ${
      r.recommended ? 'ring-1 ring-tutor/30' : ''}`}>
      {/* Lomo de color del curso, como el canto de un cuaderno */}
      <span className="absolute inset-y-0 left-0 w-1.5 transition-all group-hover:w-2" style={{ background: r.course.color }} />
      <div className="mb-3 flex items-center justify-between gap-2">
        <CourseTag course={r.course} />
        <span className={`chip border bg-card text-xs capitalize ${LEVEL_STYLE[r.level]}`}>Nivel: {r.level}</span>
      </div>
      <h3 className="text-lg font-extrabold leading-snug">{r.title}</h3>
      <p className="mt-1.5 flex-1 text-sm leading-relaxed text-muted">{r.description}</p>

      {r.recommended && (
        <div className="mt-3 flex items-center gap-2 rounded-md border border-dashed border-tutor/40 bg-tutor/[0.06] px-3 py-2 text-xs font-bold text-tutor-soft">
          <Lock size={14} /> <Sparkles size={14} /> Recomendada por la IA
        </div>
      )}

      <div className="mt-4 space-y-2">
        <div className="num flex justify-between text-xs font-bold text-muted">
          <span>{statusText}</span><span>{r.done}/{r.total} actividades</span>
        </div>
        <ProgressBar value={r.percent} color={r.course.color} height="h-1.5" />
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-dashed border-line pt-3 text-sm text-muted">
        <span className="num flex items-center gap-1"><Clock size={14} /> {r.minutes} min</span>
        <span className="num flex items-center gap-1 font-bold text-gold"><Star size={14} /> +{r.points} pts</span>
      </div>
      <Link to={`/rutas/${r.id}`} className={`${action.cls} mt-4 w-full`}><action.Icon size={16} /> {action.label}</Link>
    </article>
  )
}

export default function RoutesPage() {
  const [params, setParams] = useSearchParams()
  const filter = params.get('curso') || ''
  const { data, error, loading, reload } = useApi(() => api.routes(), [])

  if (loading) return <Loading />
  if (error) return <ErrorBox message={error} onRetry={reload} />

  const routes = filter ? data.filter((r) => r.course.slug === filter) : data
  const filters = [{ slug: '', name: 'Todos' }, ...COURSES]

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-5">
        <div>
          <h1 className="text-[1.75rem] font-extrabold leading-tight">Mis rutas de aprendizaje · 1ro de Secundaria</h1>
          <p className="mt-1 text-muted">Los módulos se ajustan a tu ritmo</p>
        </div>
        {/* Filtro como control segmentado */}
        <div className="flex max-w-full gap-1 overflow-x-auto rounded-lg border border-line bg-card p-1">
          {filters.map((f) => {
            const color = COURSES.find((c) => c.slug === f.slug)?.color
            return (
              <button key={f.slug} onClick={() => setParams(f.slug ? { curso: f.slug } : {})}
                className={`flex shrink-0 items-center gap-2 rounded-md px-3 py-1.5 text-sm font-bold transition active:scale-[.97]
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
                  filter === f.slug ? 'bg-navy text-white' : 'text-muted hover:bg-navy/5 hover:text-ink'}`}>
                {color && <span className="h-2 w-2 rounded-full" style={{ background: color }} />}
                {f.name}
              </button>
            )
          })}
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {routes.map((r) => <RouteCard key={r.id} r={r} />)}
      </div>
    </div>
  )
}

import { useSearchParams, Link } from 'react-router-dom'
import { CheckCircle2, Clock, Lock, Play, Sparkles, Star } from 'lucide-react'
import { api } from '../api/client'
import { COURSES, CourseTag, ErrorBox, Loading, ProgressBar } from '../components/ui'
import { useApi } from '../hooks/useApi'

const LEVEL_STYLE = {
  'básico': 'bg-white/10 text-muted',
  intermedio: 'bg-primary/15 text-[#b5c4ff]',
  avanzado: 'bg-success/15 text-success',
}

function RouteCard({ r }) {
  const action = r.status === 'completada' ? { label: 'Ver actividad', cls: 'btn-outline', Icon: CheckCircle2 }
    : r.status === 'pendiente' ? { label: 'Iniciar', cls: 'btn-outline', Icon: Play }
      : { label: 'Continuar', cls: 'btn-primary', Icon: Play }
  const statusText = r.status === 'completada' ? 'Completada' : r.status === 'pendiente' ? 'Sin iniciar'
    : r.percent >= 50 ? `${r.percent}% completado` : `En progreso ${r.percent}%`

  return (
    <article className="card flex flex-col p-5 transition hover:-translate-y-0.5">
      <div className="mb-3 flex items-center justify-between gap-2">
        <CourseTag course={r.course} />
        <span className={`chip text-xs capitalize ${LEVEL_STYLE[r.level]}`}>Nivel: {r.level}</span>
      </div>
      <h3 className="text-lg font-extrabold">{r.title}</h3>
      <p className="mt-1 flex-1 text-sm text-muted">{r.description}</p>

      {r.recommended && (
        <div className="mt-3 flex items-center gap-2 rounded-lg bg-tutor/15 px-3 py-2 text-xs font-bold text-[#c7bfff]">
          <Lock size={14} /> <Sparkles size={14} /> Recomendada por la IA
        </div>
      )}

      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-xs font-bold text-muted">
          <span>{statusText}</span><span>{r.done}/{r.total} actividades</span>
        </div>
        <ProgressBar value={r.percent} color={r.course.color} />
      </div>

      <div className="mt-4 flex items-center justify-between text-sm text-muted">
        <span className="flex items-center gap-1"><Clock size={14} /> {r.minutes} min</span>
        <span className="flex items-center gap-1 font-bold text-gold"><Star size={14} /> +{r.points} pts</span>
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
      <div>
        <h1 className="text-2xl font-extrabold">Mis rutas de aprendizaje · 5to de Secundaria</h1>
        <p className="text-muted">Los módulos se ajustan a tu ritmo</p>
      </div>
      <div className="flex flex-wrap gap-2">
        {filters.map((f) => (
          <button key={f.slug} onClick={() => setParams(f.slug ? { curso: f.slug } : {})}
            className={`chip border px-4 py-2 ${filter === f.slug ? 'border-primary bg-primary text-white' : 'border-line text-muted hover:text-ink'}`}>
            {f.name}
          </button>
        ))}
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {routes.map((r) => <RouteCard key={r.id} r={r} />)}
      </div>
    </div>
  )
}

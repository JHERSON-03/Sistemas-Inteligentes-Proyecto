import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Award, Bot, CheckCircle2, Clock, Flame, Medal, Route, Sparkles, Star, Trophy, Zap } from 'lucide-react'
import { api } from '../api/client'
import { courseBySlug, ErrorBox, Loading, ProgressBar } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useApi } from '../hooks/useApi'

const BADGE_ICONS = { route: Route, flame: Flame, star: Star, bot: Bot }

/** Una celda de la franja de estadísticas (las celdas se separan con líneas finas, no con tarjetas sueltas) */
function StatCard({ Icon, color, title, value, sub, progress }) {
  return (
    <div className="flex flex-col bg-card p-4 sm:p-5">
      <div className="mb-3 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-muted">
        <Icon size={15} style={{ color }} />
        {title}
      </div>
      <div className="num font-['Bricolage_Grotesque'] text-2xl font-extrabold tracking-tight sm:text-[1.7rem]">{value}</div>
      <div className="mb-4 mt-0.5 text-xs text-muted">{sub}</div>
      <div className="mt-auto"><ProgressBar value={progress} color={color} height="h-1.5" /></div>
    </div>
  )
}

function DailyChallenge({ challenge, onSolved }) {
  const toast = useToast()
  const [selected, setSelected] = useState(null)
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  const submit = async () => {
    setBusy(true)
    try {
      const res = await api.answerChallenge(challenge.id, selected)
      setResult(res)
      onSolved(res)
      toast(res.correct ? `¡Bien hecho! +${res.points_earned} pts 🎉` : 'Casi, ¡mañana hay otro reto! 💪', res.correct ? 'success' : 'warn')
    } catch (e) {
      toast(e.message, 'warn')
    } finally {
      setBusy(false)
    }
  }

  if (challenge.answered && !result) {
    return (
      <div className="flex items-start gap-3 rounded-lg border border-line bg-bg p-3 text-sm">
        <CheckCircle2 className={`shrink-0 ${challenge.was_correct ? 'text-success' : 'text-streak'}`} size={20} />
        <div><b>Reto resuelto hoy.</b> <span className="text-muted">{challenge.explanation}</span></div>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <p className="font-semibold leading-snug">{challenge.question}</p>
      <div className="grid grid-cols-2 gap-2">
        {challenge.options.map((opt, i) => {
          const isAnswer = result && i === result.answer
          const isWrong = result && i === selected && !result.correct
          return (
            <button key={i} disabled={!!result} onClick={() => setSelected(i)}
              className={`rounded-lg border px-3 py-2.5 text-left text-sm font-semibold transition active:scale-[.98]
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
                isAnswer ? 'border-success bg-success/10 text-success' : isWrong ? 'border-streak bg-streak/10 text-streak'
                  : selected === i ? 'border-navy bg-navy text-white' : 'border-line hover:border-navy/40 hover:bg-navy/[0.03]'}`}>
              {opt}
            </button>
          )
        })}
      </div>
      {result ? (
        <p className="border-l-2 border-line pl-3 text-sm text-muted">{result.explanation}</p>
      ) : (
        <button className="btn-gold w-full" disabled={selected === null || busy} onClick={submit}>
          <Zap size={16} /> Resolver (+{challenge.points} pts)
        </button>
      )}
    </div>
  )
}

export default function Dashboard() {
  const { user, setPoints } = useAuth()
  const navigate = useNavigate()
  const { data, error, loading, reload } = useApi(() => api.dashboard(), [])

  if (loading && !data) return <Loading />
  if (error) return <ErrorBox message={error} onRetry={reload} />

  const { stats, week, courses, next_step: next, challenge, achievements, ranking } = data

  return (
    <div className="space-y-6">
      {/* 1. Banner de bienvenida: azul liso, foto que se funde a la derecha y filete dorado abajo */}
      <section className="relative overflow-hidden rounded-xl bg-navy text-white">
        <img src="/img/banner-1ro.jpg" alt="" className="absolute inset-y-0 right-0 hidden h-full w-[55%] object-cover opacity-50 [mask-image:linear-gradient(to_left,black_40%,transparent)] md:block" />
        <div className="relative max-w-xl px-6 py-7 md:px-8 md:py-9">
          <h1 className="text-[1.65rem] font-extrabold leading-[1.15] md:text-[2.1rem]">¡Hola, {user.first_name}! Sigue con tu aprendizaje hoy 👋</h1>
          <p className="mt-3 max-w-md text-white/75">
            Llevas {stats.streak} {stats.streak === 1 ? 'día' : 'días'} seguidos estudiando. ¡No rompas tu racha!
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to="/tutor" className="btn-gold focus-visible:ring-offset-navy"><Bot size={18} /> Hablar con el Tutor IA</Link>
            <button onClick={() => navigate(next ? `/rutas/${next.route_id}` : '/rutas')}
              className="btn border border-white/30 text-white hover:border-white/60 hover:bg-white/10 focus-visible:ring-offset-navy">
              <Route size={18} /> Continuar mi ruta
            </button>
          </div>
        </div>
        <div className="h-1 bg-accent" />
      </section>

      {/* 2. Estadísticas en una sola franja dividida */}
      <section className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-line/80 bg-line/80 lg:grid-cols-4">
        <StatCard Icon={Flame} color="#E8590C" title="Racha" value={`${stats.streak} días seguidos`}
          sub={`Tu récord: ${stats.best_streak} días`} progress={(stats.streak / Math.max(stats.best_streak, 1)) * 100} />
        <StatCard Icon={Star} color="#A8A028" title="Puntos" value={`${stats.points} pts`}
          sub={`+${stats.weekly_points} pts esta semana`} progress={(stats.points % 1000) / 10} />
        <StatCard Icon={Clock} color="#3B5BA5" title="Estudio de la semana" value={`${stats.week_hours} h`}
          sub={`Meta: ${stats.goal_hours} h`} progress={(stats.week_hours / stats.goal_hours) * 100} />
        <StatCard Icon={CheckCircle2} color="#0F9F6E" title="Temas dominados" value={`${stats.topics_done} / ${stats.topics_total}`}
          sub="Actividades completadas" progress={(stats.topics_done / stats.topics_total) * 100} />
      </section>

      <section className="grid gap-4 lg:grid-cols-[minmax(0,5fr)_minmax(0,8fr)]">
        {/* 3. Racha semanal */}
        <div className="card p-5">
          <h2 className="section-title mb-5">Racha semanal</h2>
          <div className="flex justify-between gap-1">
            {week.map((d) => (
              <div key={d.date} className="flex flex-col items-center gap-1.5">
                <div className={`grid h-10 w-10 place-items-center rounded-full border-2 text-lg transition ${
                  d.state === 'today' ? 'border-streak bg-streak/15 ring-4 ring-streak/15'
                    : d.studied ? 'border-streak/50 bg-streak/10' : d.state === 'missed' ? 'border-line bg-bg' : 'border-dashed border-line'}`}>
                  {d.studied ? '🔥' : ''}
                </div>
                <span className={`text-xs font-bold ${d.state === 'today' ? 'text-streak' : 'text-muted'}`}>{d.label}</span>
              </div>
            ))}
          </div>
          <p className="mt-5 border-t border-dashed border-line pt-3 text-sm text-muted">Entra todos los días para mantener tu racha 🔥</p>
        </div>

        {/* 4. Tus cursos */}
        <div className="card p-5">
          <h2 className="section-title mb-4">Tus cursos</h2>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {courses.map((c) => {
              const { Icon } = courseBySlug(c.slug)
              return (
                <Link key={c.slug} to={`/rutas?curso=${c.slug}`}
                  className="group rounded-lg border border-line bg-card p-3 transition hover:-translate-y-0.5 hover:border-[var(--c)] active:translate-y-0
                    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
                  style={{ '--c': c.color, borderTop: `3px solid ${c.color}` }}>
                  <span className="mb-3 grid h-9 w-9 place-items-center rounded-md transition group-hover:scale-105" style={{ background: `${c.color}18`, color: c.color }}>
                    <Icon size={18} />
                  </span>
                  <div className="mb-2 min-h-[2.5rem] text-sm font-bold leading-tight">{c.name}</div>
                  <div className="num mb-1.5 font-['Bricolage_Grotesque'] text-xl font-extrabold" style={{ color: c.color }}>{c.percent}%</div>
                  <ProgressBar value={c.percent} color={c.color} height="h-1.5" />
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      {/* Fila asimétrica: siguiente paso y reto del día al frente; ranking y logros apilados a la derecha */}
      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-12">
        {/* 5. Siguiente paso recomendado */}
        <div className="card flex flex-col border-l-4 border-l-accent p-5 lg:col-span-4">
          <h2 className="mb-3 flex items-start gap-2 font-extrabold leading-snug"><Sparkles size={18} className="mt-0.5 shrink-0 text-tutor" /> Siguiente paso recomendado por la IA</h2>
          {next ? (
            <>
              <p className="flex-1 text-muted"><b className="text-ink">{next.title}:</b> te {next.remaining === 1 ? 'falta 1 actividad' : `faltan ${next.remaining} actividades`}</p>
              <button className="btn-primary mt-5 self-start" onClick={() => navigate(`/rutas/${next.route_id}`)}>Continuar</button>
            </>
          ) : <p className="text-muted">¡Completaste todas tus rutas! 🎉</p>}
        </div>

        {/* 6. Reto del día */}
        <div className="card p-5 lg:col-span-5">
          <h2 className="mb-3 flex items-center gap-2 font-extrabold"><Zap size={18} className="text-gold" /> Reto del día</h2>
          <DailyChallenge challenge={challenge} onSolved={(r) => setPoints(r.total_points)} />
        </div>

        <div className="flex flex-col gap-4 md:col-span-2 lg:col-span-3">
          {/* 8. Mini ranking */}
          <div className="card p-5">
            <h2 className="mb-3 flex items-center gap-2 font-extrabold"><Trophy size={18} className="text-gold" /> Ranking del salón</h2>
            <ul className="divide-y divide-line text-sm">
              {ranking.top.map((r) => (
                <li key={r.position} className={`-mx-2 flex items-center justify-between px-2 py-2 ${r.me ? 'rounded-md bg-navy/[0.06] font-bold' : ''}`}>
                  <span><b className="mr-2">{['🥇', '🥈', '🥉'][r.position - 1]}</b>{r.name}</span>
                  <span className="num font-bold text-gold">{r.points}</span>
                </li>
              ))}
            </ul>
            {!ranking.top.some((r) => r.me) && (
              <p className="mt-3 rounded-md border border-dashed border-navy/25 px-3 py-2 text-sm">
                Vas <b>{ranking.me.position}.º</b> de tu salón con {ranking.me.points} pts. ¡Tú puedes! 💪
              </p>
            )}
          </div>

          {/* 7. Logros recientes */}
          <div className="card p-5">
            <h2 className="mb-4 flex items-center gap-2 font-extrabold"><Award size={18} className="text-success" /> Logros recientes</h2>
            <div className="flex justify-around gap-2">
              {achievements.map((b) => {
                const Icon = BADGE_ICONS[b.icon] || Medal
                return (
                  <div key={b.id} className={`group flex w-20 flex-col items-center text-center ${b.unlocked ? '' : 'opacity-40 grayscale'}`}>
                    <div className="mb-2 grid h-12 w-12 place-items-center rounded-full border-2 border-success/40 bg-success/10 text-success transition group-hover:-rotate-6">
                      <Icon size={20} />
                    </div>
                    <span className="text-xs font-bold leading-tight">{b.name}</span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

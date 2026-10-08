import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Award, Bot, CheckCircle2, Clock, Flame, Medal, Route, Sparkles, Star, Trophy, Zap } from 'lucide-react'
import { api } from '../api/client'
import { courseBySlug, ErrorBox, Loading, ProgressBar } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useApi } from '../hooks/useApi'

const BADGE_ICONS = { route: Route, flame: Flame, star: Star, bot: Bot }

function StatCard({ Icon, color, title, value, sub, progress }) {
  return (
    <div className="card p-4">
      <div className="mb-2 flex items-center gap-2 text-sm font-bold text-muted">
        <span className="grid h-8 w-8 place-items-center rounded-lg" style={{ background: `${color}22`, color }}><Icon size={16} /></span>
        {title}
      </div>
      <div className="text-2xl font-extrabold">{value}</div>
      <div className="mb-3 text-xs text-muted">{sub}</div>
      <ProgressBar value={progress} color={color} />
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
      <div className="flex items-start gap-3 rounded-xl bg-white/5 p-3 text-sm">
        <CheckCircle2 className={challenge.was_correct ? 'text-success' : 'text-streak'} size={20} />
        <div><b>Reto resuelto hoy.</b> <span className="text-muted">{challenge.explanation}</span></div>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <p className="font-semibold">{challenge.question}</p>
      <div className="grid grid-cols-2 gap-2">
        {challenge.options.map((opt, i) => {
          const isAnswer = result && i === result.answer
          const isWrong = result && i === selected && !result.correct
          return (
            <button key={i} disabled={!!result} onClick={() => setSelected(i)}
              className={`rounded-xl border px-3 py-2 text-left text-sm font-semibold transition ${
                isAnswer ? 'border-success bg-success/15' : isWrong ? 'border-streak bg-streak/15'
                  : selected === i ? 'border-primary bg-primary/15' : 'border-line hover:bg-white/5'}`}>
              {opt}
            </button>
          )
        })}
      </div>
      {result ? (
        <p className="text-sm text-muted">{result.explanation}</p>
      ) : (
        <button className="btn-primary w-full" disabled={selected === null || busy} onClick={submit}>
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
    <div className="space-y-5">
      {/* 1. Banner de bienvenida */}
      <section className="relative overflow-hidden rounded-card bg-gradient-to-r from-[#1b2a6b] via-[#2a2580] to-[#5b3fd1] p-6 shadow-soft md:p-8">
        <img src="/img/banner-estudiante.jpg" alt="" className="absolute inset-y-0 right-0 hidden h-full w-1/2 object-cover opacity-40 [mask-image:linear-gradient(to_left,black,transparent)] md:block" />
        <div className="relative max-w-xl">
          <h1 className="text-2xl font-extrabold md:text-3xl">¡Hola, {user.first_name}! Sigue con tu aprendizaje hoy 👋</h1>
          <p className="mt-2 text-[#d6dbff]">
            Llevas {stats.streak} {stats.streak === 1 ? 'día' : 'días'} seguidos estudiando. ¡No rompas tu racha!
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link to="/tutor" className="btn-primary"><Bot size={18} /> Hablar con el Tutor IA</Link>
            <button onClick={() => navigate(next ? `/rutas/${next.route_id}` : '/rutas')} className="btn-outline border-white/40">
              <Route size={18} /> Continuar mi ruta
            </button>
          </div>
        </div>
      </section>

      {/* 2. Tarjetas de estadísticas */}
      <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard Icon={Flame} color="#FB923C" title="Racha" value={`${stats.streak} días seguidos`}
          sub={`Tu récord: ${stats.best_streak} días`} progress={(stats.streak / Math.max(stats.best_streak, 1)) * 100} />
        <StatCard Icon={Star} color="#FBBF24" title="Puntos" value={`${stats.points} pts`}
          sub={`+${stats.weekly_points} pts esta semana`} progress={(stats.points % 1000) / 10} />
        <StatCard Icon={Clock} color="#8B7BFF" title="Estudio de la semana" value={`${stats.week_hours} h`}
          sub={`Meta: ${stats.goal_hours} h`} progress={(stats.week_hours / stats.goal_hours) * 100} />
        <StatCard Icon={CheckCircle2} color="#34D399" title="Temas dominados" value={`${stats.topics_done} / ${stats.topics_total}`}
          sub="Actividades completadas" progress={(stats.topics_done / stats.topics_total) * 100} />
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        {/* 3. Racha semanal */}
        <div className="card p-5">
          <h2 className="mb-4 font-extrabold">Racha semanal</h2>
          <div className="flex justify-between gap-1">
            {week.map((d) => (
              <div key={d.date} className="flex flex-col items-center gap-1.5">
                <div className={`grid h-10 w-10 place-items-center rounded-full border-2 text-lg ${
                  d.state === 'today' ? 'border-streak bg-streak/20 ring-4 ring-streak/20'
                    : d.studied ? 'border-streak/60 bg-streak/15' : d.state === 'missed' ? 'border-line bg-white/5' : 'border-dashed border-line'}`}>
                  {d.studied ? '🔥' : ''}
                </div>
                <span className={`text-xs font-bold ${d.state === 'today' ? 'text-streak' : 'text-muted'}`}>{d.label}</span>
              </div>
            ))}
          </div>
          <p className="mt-4 text-sm text-muted">Entra todos los días para mantener tu racha 🔥</p>
        </div>

        {/* 4. Tus cursos */}
        <div className="card p-5 lg:col-span-2">
          <h2 className="mb-4 font-extrabold">Tus cursos</h2>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {courses.map((c) => {
              const { Icon } = courseBySlug(c.slug)
              return (
                <Link key={c.slug} to={`/rutas?curso=${c.slug}`}
                  className="rounded-xl border border-line p-3 transition hover:-translate-y-0.5 hover:bg-white/5"
                  style={{ borderTopColor: c.color, borderTopWidth: 3 }}>
                  <span className="mb-2 grid h-9 w-9 place-items-center rounded-lg" style={{ background: `${c.color}22`, color: c.color }}>
                    <Icon size={18} />
                  </span>
                  <div className="mb-2 min-h-[2.5rem] text-sm font-bold leading-tight">{c.name}</div>
                  <div className="mb-1 text-lg font-extrabold" style={{ color: c.color }}>{c.percent}%</div>
                  <ProgressBar value={c.percent} color={c.color} />
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* 5. Siguiente paso recomendado */}
        <div className="card flex flex-col p-5">
          <h2 className="mb-3 flex items-center gap-2 font-extrabold"><Sparkles size={18} className="text-tutor" /> Siguiente paso recomendado por la IA</h2>
          {next ? (
            <>
              <p className="flex-1 text-muted"><b className="text-ink">{next.title}:</b> te {next.remaining === 1 ? 'falta 1 actividad' : `faltan ${next.remaining} actividades`}</p>
              <button className="btn-primary mt-4" onClick={() => navigate(`/rutas/${next.route_id}`)}>Continuar</button>
            </>
          ) : <p className="text-muted">¡Completaste todas tus rutas! 🎉</p>}
        </div>

        {/* 6. Reto del día */}
        <div className="card p-5">
          <h2 className="mb-3 flex items-center gap-2 font-extrabold"><Zap size={18} className="text-gold" /> Reto del día</h2>
          <DailyChallenge challenge={challenge} onSolved={(r) => setPoints(r.total_points)} />
        </div>

        {/* 7. Logros recientes */}
        <div className="card p-5">
          <h2 className="mb-4 flex items-center gap-2 font-extrabold"><Award size={18} className="text-success" /> Logros recientes</h2>
          <div className="flex justify-around gap-2">
            {achievements.map((b) => {
              const Icon = BADGE_ICONS[b.icon] || Medal
              return (
                <div key={b.id} className={`flex w-20 flex-col items-center text-center ${b.unlocked ? '' : 'opacity-40'}`}>
                  <div className="mb-2 grid h-14 w-14 place-items-center rounded-full bg-gradient-to-br from-success/40 to-primary/40 ring-2 ring-success/40">
                    <Icon size={22} />
                  </div>
                  <span className="text-xs font-bold leading-tight">{b.name}</span>
                </div>
              )
            })}
          </div>
        </div>

        {/* 8. Mini ranking */}
        <div className="card p-5">
          <h2 className="mb-3 flex items-center gap-2 font-extrabold"><Trophy size={18} className="text-gold" /> Ranking del salón</h2>
          <ul className="space-y-2 text-sm">
            {ranking.top.map((r) => (
              <li key={r.position} className={`flex items-center justify-between rounded-lg px-3 py-1.5 ${r.me ? 'bg-primary/15' : ''}`}>
                <span><b className="mr-2">{['🥇', '🥈', '🥉'][r.position - 1]}</b>{r.name}</span>
                <span className="font-bold text-gold">{r.points}</span>
              </li>
            ))}
          </ul>
          {!ranking.top.some((r) => r.me) && (
            <p className="mt-3 rounded-lg bg-primary/15 px-3 py-2 text-sm">
              Vas <b>{ranking.me.position}.º</b> de tu salón con {ranking.me.points} pts. ¡Tú puedes! 💪
            </p>
          )}
        </div>
      </section>
    </div>
  )
}

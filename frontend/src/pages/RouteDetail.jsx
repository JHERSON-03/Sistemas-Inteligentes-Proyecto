import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, Circle, Lightbulb, PartyPopper } from 'lucide-react'
import { api } from '../api/client'
import { CourseTag, ErrorBox, Loading, ProgressBar } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useApi } from '../hooks/useApi'

export default function RouteDetail() {
  const { id } = useParams()
  const { setPoints } = useAuth()
  const toast = useToast()
  const { data, setData, error, loading, reload } = useApi(() => api.route(id), [id])
  const [currentId, setCurrentId] = useState(null)
  const [selected, setSelected] = useState(null)
  const [feedback, setFeedback] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (data && currentId === null) setCurrentId(data.next_activity_id ?? data.activities[0]?.id)
  }, [data, currentId])

  if (loading && !data) return <Loading />
  if (error) return <ErrorBox message={error} onRetry={reload} />

  const activity = data.activities.find((a) => a.id === currentId) || data.activities[0]
  const select = (a) => { setCurrentId(a.id); setSelected(null); setFeedback(null) }

  const check = async () => {
    setBusy(true)
    try {
      const res = await api.answerActivity(activity.id, selected)
      setFeedback(res)
      if (res.correct) {
        setPoints(res.total_points)
        toast(res.route_completed ? `¡Ruta completada! +${res.points_earned} pts 🏆` : `¡Bien hecho! +${res.points_earned} pts 🎉`)
        setData((d) => ({
          ...d, ...res.route,
          activities: d.activities.map((a) => (a.id === activity.id ? { ...a, completed: true } : a)),
        }))
      }
    } catch (e) {
      toast(e.message, 'warn')
    } finally {
      setBusy(false)
    }
  }

  const goNext = () => {
    const next = data.activities.find((a) => !a.completed)
    if (next) select(next)
  }

  return (
    <div className="space-y-5">
      <Link to="/rutas" className="btn-ghost -ml-3 w-fit"><ArrowLeft size={16} /> Mis rutas</Link>
      <div className="card relative overflow-hidden p-5 pl-7">
        <span className="absolute inset-y-0 left-0 w-1.5" style={{ background: data.course.color }} />
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <CourseTag course={data.course} />
          <span className="chip border border-line text-xs capitalize text-muted">Nivel: {data.level}</span>
        </div>
        <h1 className="text-[1.75rem] font-extrabold leading-tight">{data.title}</h1>
        <p className="mt-1 max-w-2xl text-muted">{data.description}</p>
        <div className="mt-5 flex items-center gap-3">
          <ProgressBar value={data.percent} color={data.course.color} height="h-2.5" />
          <span className="num shrink-0 text-sm font-bold">{data.done}/{data.total}</span>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
        {/* Lista de actividades como línea de tiempo */}
        <ol className="card relative h-fit p-3 before:absolute before:bottom-6 before:left-[33px] before:top-6 before:w-px before:bg-line">
          {data.activities.map((a) => (
            <li key={a.id} className="relative">
              <button onClick={() => select(a)}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-semibold transition
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
                  a.id === activity.id ? 'bg-navy/[0.07] text-ink' : 'text-muted hover:bg-navy/[0.04] hover:text-ink'}`}>
                <span className="relative z-10 rounded-full bg-card">
                  {a.completed ? <CheckCircle2 size={18} className="shrink-0 text-success" />
                    : <Circle size={18} className={`shrink-0 ${a.id === activity.id ? 'text-navy' : ''}`} />}
                </span>
                {a.order}. {a.title}
              </button>
            </li>
          ))}
        </ol>

        <section className="card p-6 md:p-7">
          <p className="num mb-2 text-xs font-extrabold uppercase tracking-[0.14em] text-gold">Actividad {activity.order} de {data.total}</p>
          <h2 className="mb-5 text-xl font-extrabold leading-snug md:text-[1.4rem]">{activity.question}</h2>

          {activity.completed && !feedback ? (
            <div className="flex items-center gap-3 rounded-lg border border-success/30 bg-success/[0.07] p-4 text-success">
              <CheckCircle2 /> Ya completaste esta actividad.
              {data.next_activity_id && <button className="btn-primary ml-auto" onClick={goNext}>Siguiente</button>}
            </div>
          ) : (
            <>
              <div className="grid gap-3 sm:grid-cols-2">
                {activity.options.map((opt, i) => {
                  const ok = feedback?.correct && i === selected
                  const bad = feedback && !feedback.correct && i === selected
                  return (
                    <button key={i} disabled={feedback?.correct} onClick={() => { setSelected(i); if (feedback && !feedback.correct) setFeedback(null) }}
                      className={`group flex items-center gap-3 rounded-lg border-2 p-4 text-left font-semibold transition active:scale-[.99]
                        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 ${
                        ok ? 'border-success bg-success/[0.07]' : bad ? 'border-streak bg-streak/[0.07]'
                          : selected === i ? 'border-navy bg-navy/[0.05]' : 'border-line hover:border-navy/40'}`}>
                      <span className={`grid h-7 w-7 shrink-0 place-items-center rounded-md border text-sm font-extrabold transition ${
                        ok ? 'border-success bg-success text-white' : bad ? 'border-streak bg-streak text-white'
                          : selected === i ? 'border-navy bg-navy text-white' : 'border-line text-muted group-hover:border-navy/40 group-hover:text-navy'}`}>
                        {String.fromCharCode(65 + i)}
                      </span>
                      {opt}
                    </button>
                  )
                })}
              </div>

              {feedback && !feedback.correct && (
                <div className="animate-pop mt-4 flex gap-3 rounded-lg border-l-4 border-streak bg-streak/[0.07] p-4 text-sm">
                  <Lightbulb className="shrink-0 text-streak" size={18} />
                  <p><b>Pista:</b> {feedback.hint} Inténtalo de nuevo.</p>
                </div>
              )}
              {feedback?.correct && (
                <div className="animate-pop mt-4 rounded-lg border-l-4 border-success bg-success/[0.07] p-4 text-sm">
                  <p className="mb-1 flex items-center gap-2 font-extrabold text-success">
                    {feedback.route_completed ? <PartyPopper size={18} /> : <CheckCircle2 size={18} />}
                    {feedback.route_completed ? `¡Ruta completada! +${feedback.points_earned} pts` : `¡Bien hecho! +${feedback.points_earned} pts 🎉`}
                  </p>
                  <p className="text-muted">{feedback.explanation}</p>
                </div>
              )}

              <div className="mt-6 flex justify-end gap-3 border-t border-line pt-5">
                {feedback?.correct
                  ? data.next_activity_id && <button className="btn-primary" onClick={goNext}>Siguiente actividad</button>
                  : <button className="btn-primary px-7" disabled={selected === null || busy} onClick={check}>Comprobar</button>}
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  )
}

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
      <div className="card p-5">
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <CourseTag course={data.course} />
          <span className="chip bg-navy/10 text-xs capitalize text-muted">Nivel: {data.level}</span>
        </div>
        <h1 className="text-2xl font-extrabold">{data.title}</h1>
        <p className="text-muted">{data.description}</p>
        <div className="mt-4 flex items-center gap-3">
          <ProgressBar value={data.percent} color={data.course.color} height="h-3" />
          <span className="shrink-0 text-sm font-bold">{data.done}/{data.total}</span>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
        <ol className="card h-fit space-y-1 p-3">
          {data.activities.map((a) => (
            <li key={a.id}>
              <button onClick={() => select(a)}
                className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-semibold ${
                  a.id === activity.id ? 'bg-primary/15 text-ink' : 'text-muted hover:bg-navy/5'}`}>
                {a.completed ? <CheckCircle2 size={18} className="shrink-0 text-success" /> : <Circle size={18} className="shrink-0" />}
                {a.order}. {a.title}
              </button>
            </li>
          ))}
        </ol>

        <section className="card p-6">
          <p className="mb-1 text-xs font-extrabold uppercase tracking-wider text-muted">Actividad {activity.order} de {data.total}</p>
          <h2 className="mb-4 text-xl font-extrabold">{activity.question}</h2>

          {activity.completed && !feedback ? (
            <div className="flex items-center gap-3 rounded-xl bg-success/10 p-4 text-success">
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
                      className={`flex items-center gap-3 rounded-xl border-2 p-4 text-left font-semibold transition ${
                        ok ? 'border-success bg-success/10' : bad ? 'border-streak bg-streak/10'
                          : selected === i ? 'border-primary bg-primary/10' : 'border-line hover:bg-navy/5'}`}>
                      <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full border border-current text-sm">{String.fromCharCode(65 + i)}</span>
                      {opt}
                    </button>
                  )
                })}
              </div>

              {feedback && !feedback.correct && (
                <div className="mt-4 flex gap-3 rounded-xl border border-streak/40 bg-streak/10 p-4 text-sm">
                  <Lightbulb className="shrink-0 text-streak" size={18} />
                  <p><b>Pista:</b> {feedback.hint} Inténtalo de nuevo.</p>
                </div>
              )}
              {feedback?.correct && (
                <div className="mt-4 rounded-xl border border-success/40 bg-success/10 p-4 text-sm">
                  <p className="mb-1 flex items-center gap-2 font-extrabold text-success">
                    {feedback.route_completed ? <PartyPopper size={18} /> : <CheckCircle2 size={18} />}
                    {feedback.route_completed ? `¡Ruta completada! +${feedback.points_earned} pts` : `¡Bien hecho! +${feedback.points_earned} pts 🎉`}
                  </p>
                  <p className="text-muted">{feedback.explanation}</p>
                </div>
              )}

              <div className="mt-5 flex justify-end gap-3">
                {feedback?.correct
                  ? data.next_activity_id && <button className="btn-primary" onClick={goNext}>Siguiente actividad</button>
                  : <button className="btn-primary" disabled={selected === null || busy} onClick={check}>Comprobar</button>}
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  )
}

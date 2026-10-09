import { useState } from 'react'
import { CheckCircle2, Lightbulb, RotateCcw, Trophy } from 'lucide-react'
import { api } from '../api/client'
import { ErrorBox, Loading, ProgressBar } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useApi } from '../hooks/useApi'

const CONFIDENCE = [
  { value: 'baja', label: 'Nada seguro' },
  { value: 'media', label: 'Más o menos' },
  { value: 'alta', label: 'Muy seguro' },
]

// Ilustraciones de Stitch según el tema de la pregunta
function questionImage(text) {
  const t = text.toLowerCase()
  if (t.includes('mototaxi') || t.includes('bicicleta') || t.includes('plaza de laredo')) {
    return { src: '/img/rapidez-laredo.jpg', alt: 'Bicicleta y skate en la Plaza de Laredo: distancia y rapidez' }
  }
  return null
}

export default function Assessment() {
  const { setPoints } = useAuth()
  const toast = useToast()
  const list = useApi(() => api.assessments(), [])
  const [currentId, setCurrentId] = useState(null)
  const activeId = currentId ?? list.data?.[0]?.id ?? null
  const { data, error, loading, reload } = useApi(
    () => (activeId ? api.assessment(activeId) : Promise.resolve(null)), [activeId])
  const [index, setIndex] = useState(0)
  const [selected, setSelected] = useState(null)
  const [confidence, setConfidence] = useState(null)
  const [result, setResult] = useState(null)
  const [score, setScore] = useState({ correct: 0, points: 0 })
  const [busy, setBusy] = useState(false)

  if (list.error) return <ErrorBox message={list.error} onRetry={list.reload} />
  if (list.loading || loading || !data) {
    return list.data?.length === 0 ? <ErrorBox message="Aún no hay autoevaluaciones disponibles." /> : <Loading />
  }
  if (error) return <ErrorBox message={error} onRetry={reload} />

  const total = data.questions.length
  const finished = index >= total
  const q = data.questions[Math.min(index, total - 1)]

  const check = async () => {
    setBusy(true)
    try {
      const res = await api.checkQuestion(q.id, selected, confidence)
      setResult(res)
      setScore((s) => ({ correct: s.correct + (res.correct ? 1 : 0), points: s.points + res.points_earned }))
      if (res.correct) { setPoints(res.total_points); toast(`+${res.points_earned} pts 🎉`) }
    } catch (e) {
      toast(e.message, 'warn')
    } finally {
      setBusy(false)
    }
  }

  const next = () => { setIndex((i) => i + 1); setSelected(null); setConfidence(null); setResult(null) }
  const restart = () => { setIndex(0); setScore({ correct: 0, points: 0 }); setSelected(null); setConfidence(null); setResult(null) }
  const choose = (id) => { if (id !== activeId) { setCurrentId(id); restart() } }

  const picker = list.data.length > 1 && (
    <div className="mx-auto flex max-w-3xl flex-wrap gap-2">
      {list.data.map((a) => (
        <button key={a.id} onClick={() => choose(a.id)}
          className={`chip border px-4 py-2 ${a.id === activeId ? 'border-primary bg-primary text-primary-ink' : 'border-line text-muted hover:text-ink'}`}>
          {a.title} · {a.questions} {a.questions === 1 ? 'pregunta' : 'preguntas'}
        </button>
      ))}
    </div>
  )

  if (finished) {
    return (
      <div className="space-y-5">
      {picker}
      <div className="card mx-auto max-w-lg animate-pop p-8 text-center">
        <Trophy className="mx-auto mb-3 text-gold" size={48} />
        <h1 className="text-2xl font-extrabold">¡Terminaste el desafío!</h1>
        <p className="mt-2 text-muted">Acertaste {score.correct} de {total} preguntas y ganaste <b className="text-gold">{score.points} pts</b>.</p>
        <p className="mt-2 text-sm text-muted">Recuerda: esto no es una nota, es una forma de ver cómo razonas.</p>
        <button className="btn-primary mt-6" onClick={restart}><RotateCcw size={16} /> Volver a intentarlo</button>
      </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      {picker}
      <div>
        <p className="text-xs font-extrabold uppercase tracking-widest text-tutor">Evaluación autónoma formativa</p>
        <div className="mt-1 flex flex-wrap items-center justify-between gap-2">
          <h1 className="text-2xl font-extrabold">{data.title}</h1>
          <span className="chip bg-primary/15 text-primary-soft">Pregunta {index + 1} de {total}</span>
        </div>
        <p className="mt-1 text-sm text-muted">Esta prueba no es una nota; sirve para ver cómo razonas.</p>
        <div className="mt-3"><ProgressBar value={((index + (result ? 1 : 0)) / total) * 100} color="#3B5BA5" height="h-2.5" /></div>
      </div>

      <div className="card overflow-hidden">
        {questionImage(q.situation) && (
          <img src={questionImage(q.situation).src} alt={questionImage(q.situation).alt} className="h-44 w-full object-cover" />
        )}
        <p className="p-5 text-lg font-semibold leading-relaxed">{q.situation}</p>
      </div>

      <div className="space-y-3">
        {q.options.map((opt, i) => {
          const isRight = result && i === result.answer
          const isWrong = result && i === selected && !result.correct
          return (
            <button key={i} disabled={!!result} onClick={() => setSelected(i)}
              className={`card flex w-full items-center gap-4 p-4 text-left transition ${
                isRight ? '!border-success bg-success/10' : isWrong ? '!border-streak bg-streak/10'
                  : selected === i ? '!border-primary bg-primary/10' : 'hover:bg-navy/5'}`}>
              <span className={`grid h-6 w-6 shrink-0 place-items-center rounded-full border-2 ${selected === i ? 'border-primary' : 'border-line'}`}>
                {selected === i && <span className="h-3 w-3 rounded-full bg-primary" />}
              </span>
              <span><b>{String.fromCharCode(65 + i)}) {opt.text}</b> <span className="text-muted">({opt.reason})</span></span>
            </button>
          )
        })}
      </div>

      <div className="card p-5">
        <p className="mb-3 font-bold">¿Qué tan seguro estás de tu respuesta?</p>
        <div className="grid grid-cols-3 gap-2">
          {CONFIDENCE.map((c) => (
            <button key={c.value} disabled={!!result} onClick={() => setConfidence(c.value)}
              className={`rounded-xl border px-3 py-2.5 text-sm font-bold transition ${
                confidence === c.value ? 'border-tutor bg-tutor/20 text-tutor-soft' : 'border-line text-muted hover:bg-navy/5'}`}>
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {result && (
        <div className={`animate-pop rounded-card border p-5 ${result.correct ? 'border-success/40 bg-success/10' : 'border-streak/40 bg-streak/10'}`}>
          <p className={`flex items-center gap-2 font-extrabold ${result.correct ? 'text-success' : 'text-streak'}`}>
            {result.correct ? <CheckCircle2 size={20} /> : <Lightbulb size={20} />}
            {result.correct ? `¡Correcto! +${result.points_earned} pts` : 'Sigue intentándolo, vas por buen camino'}
          </p>
          <p className="mt-2">{result.feedback}</p>
          {result.confidence_tip && <p className="mt-2 text-sm text-muted">💡 {result.confidence_tip}</p>}
        </div>
      )}

      <div className="flex justify-end">
        {result
          ? <button className="btn-primary" onClick={next}>{index + 1 < total ? 'Siguiente pregunta' : 'Ver resultado'}</button>
          : <button className="btn-primary px-8" disabled={selected === null || !confidence || busy} onClick={check}>Comprobar</button>}
      </div>
    </div>
  )
}

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Info, Loader2, Lock, User } from 'lucide-react'
import { api } from '../api/client'
import { Logo } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

export default function Login() {
  const { login } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [form, setForm] = useState({ identifier: '', password: '' })
  const [show, setShow] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [forgotMsg, setForgotMsg] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    if (!form.identifier.trim() || !form.password) {
      setError('Completa tu usuario o DNI y tu contraseña')
      return
    }
    setBusy(true)
    setError('')
    try {
      const data = await login(form.identifier, form.password)
      if (data.streak_message) toast(data.streak_message, 'info')
      else toast(`🔥 ¡Racha de ${data.user.streak} ${data.user.streak === 1 ? 'día' : 'días'}! Sigue así`, 'warn')
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const forgot = async () => {
    const res = await api.forgot().catch(() => ({ message: 'Pídele ayuda a tu tutor o docente.' }))
    setForgotMsg(res.message)
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <section className="relative hidden overflow-hidden lg:block">
        <img src="/img/banner-1ro.jpg" alt="Estudiante aprendiendo con un robot tutor amigable"
          className="absolute inset-0 h-full w-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-bg via-bg/30 to-transparent" />
        <div className="absolute bottom-10 left-10 right-10">
          <p className="text-3xl font-extrabold leading-tight">Aprende a tu ritmo,<br />con un tutor que te guía.</p>
          <p className="mt-2 text-muted">Colegio Louis Pasteur · Laredo, La Libertad</p>
        </div>
      </section>

      <section className="flex items-center justify-center px-4 py-10">
        <form onSubmit={submit} className="card animate-pop w-full max-w-md space-y-5 p-8" noValidate>
          <div className="flex flex-col items-center text-center">
            <Logo size="lg" />
            <h1 className="mt-4 text-2xl font-extrabold">Bienvenido a Pasteur Learn</h1>
            <p className="mt-1 text-muted">Solo para estudiantes de 1ro de secundaria</p>
          </div>

          <img src="/img/robot-tutor.jpg" alt="" className="mx-auto h-28 w-28 rounded-full object-cover lg:hidden" />

          <label className="block space-y-2">
            <span className="label">Usuario o DNI</span>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={18} />
              <input className="input pl-10" autoComplete="username" placeholder="Ej. joaquin o 70000001"
                value={form.identifier} onChange={(e) => setForm({ ...form, identifier: e.target.value })} />
            </div>
          </label>

          <label className="block space-y-2">
            <span className="label">Contraseña</span>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={18} />
              <input className="input px-10" type={show ? 'text' : 'password'} autoComplete="current-password"
                placeholder="••••••••" value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })} />
              <button type="button" onClick={() => setShow((s) => !s)} aria-label={show ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink">
                {show ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </label>

          {error && <p className="rounded-xl bg-red-500/10 px-4 py-2 text-sm font-semibold text-red-300">{error}</p>}

          <button className="btn-primary w-full py-3.5 text-lg" disabled={busy}>
            {busy && <Loader2 className="animate-spin" size={18} />} Ingresar
          </button>

          <div className="text-center">
            <button type="button" onClick={forgot} className="text-sm font-semibold text-primary hover:underline">
              ¿Olvidaste tu contraseña?
            </button>
            {forgotMsg && <p className="mt-2 text-sm text-muted">{forgotMsg}</p>}
          </div>

          <div className="flex gap-3 rounded-xl border border-primary/30 bg-primary/10 p-3 text-sm text-primary-soft">
            <Info size={18} className="shrink-0" />
            <p>Si no tienes cuenta, pídela a tu tutor o docente. ¿Ya tienes tu código? <Link to="/registro" className="font-bold underline">Actívala aquí</Link>.</p>
          </div>
        </form>
      </section>
    </div>
  )
}

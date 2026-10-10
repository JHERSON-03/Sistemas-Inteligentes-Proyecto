import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { Logo } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

const EMPTY = { full_name: '', dni: '', username: '', password: '', confirm: '', section: 'B' }

function validate(f) {
  if (f.full_name.trim().split(/\s+/).length < 2) return 'Escribe tu nombre y apellido'
  if (!/^\d{8}$/.test(f.dni)) return 'El DNI debe tener 8 dígitos'
  if (!/^[a-zA-Z0-9_.]{3,}$/.test(f.username)) return 'El usuario debe tener al menos 3 letras o números, sin espacios'
  if (f.password.length < 6) return 'La contraseña debe tener al menos 6 caracteres'
  if (f.password !== f.confirm) return 'Las contraseñas no coinciden'
  return ''
}

export default function Register() {
  const { register } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    const msg = validate(form)
    if (msg) return setError(msg)
    setBusy(true)
    setError('')
    try {
      const { confirm, ...payload } = form
      await register(payload)
      toast('¡Cuenta creada! Empieza tu primera ruta 🎉')
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <form onSubmit={submit} className="card animate-pop w-full max-w-lg space-y-4 border-t-4 border-t-navy p-8" noValidate>
        <Link to="/login" className="btn-ghost -ml-3 w-fit"><ArrowLeft size={16} /> Volver</Link>
        <div className="flex items-center gap-4 border-b border-line pb-5">
          <Logo size="lg" />
          <div>
            <span className="mb-2 block h-1 w-10 rounded-full bg-accent" />
            <h1 className="text-[1.75rem] font-extrabold leading-tight">Activa tu cuenta</h1>
            <p className="text-sm text-muted">Louis Pasteur · 1ro de secundaria</p>
          </div>
        </div>

        <label className="block space-y-2">
          <span className="label">Nombre completo</span>
          <input className="input" placeholder="Nombre y apellido" value={form.full_name} onChange={set('full_name')} />
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block space-y-2">
            <span className="label">DNI</span>
            <input className="input" inputMode="numeric" maxLength={8} placeholder="8 dígitos" value={form.dni}
              onChange={(e) => setForm({ ...form, dni: e.target.value.replace(/\D/g, '') })} />
          </label>
          <label className="block space-y-2">
            <span className="label">Sección</span>
            <select className="input" value={form.section} onChange={set('section')}>
              {['A', 'B', 'C', 'D', 'E'].map((s) => <option key={s} value={s}>1ro {s}</option>)}
            </select>
          </label>
        </div>
        <label className="block space-y-2">
          <span className="label">Usuario</span>
          <input className="input" autoComplete="username" placeholder="Ej. joaquin.p" value={form.username} onChange={set('username')} />
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block space-y-2">
            <span className="label">Contraseña</span>
            <input className="input" type="password" autoComplete="new-password" value={form.password} onChange={set('password')} />
          </label>
          <label className="block space-y-2">
            <span className="label">Repite la contraseña</span>
            <input className="input" type="password" autoComplete="new-password" value={form.confirm} onChange={set('confirm')} />
          </label>
        </div>

        {error && <p role="alert" className="animate-pop rounded-lg border-l-4 border-red-600 bg-red-500/[0.07] px-4 py-2.5 text-sm font-semibold text-red-700">{error}</p>}

        <button className="btn-primary w-full py-3.5 text-lg" disabled={busy}>
          {busy && <Loader2 className="animate-spin" size={18} />} Crear cuenta
        </button>
        <p className="text-center text-sm text-muted">¿Ya tienes cuenta? <Link to="/login" className="font-bold text-primary underline-offset-4 hover:underline">Ingresa</Link></p>
      </form>
    </div>
  )
}

import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { BarChart3, Bot, ClipboardCheck, Flame, Home, LogOut, Route, Star } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { Logo } from './ui'

const TABS = [
  { to: '/', label: 'Inicio', Icon: Home, end: true },
  { to: '/tutor', label: 'Tutor IA', Icon: Bot },
  { to: '/rutas', label: 'Rutas Adaptativas', Icon: Route },
  { to: '/autoevaluacion', label: 'Autoevaluación', Icon: ClipboardCheck },
  { to: '/metricas', label: 'Mis Métricas', Icon: BarChart3 },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [menu, setMenu] = useState(false)
  const initials = user.full_name.split(' ').map((p) => p[0]).slice(0, 2).join('')

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-40 border-b border-line bg-bg/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3">
          <button onClick={() => navigate('/')} className="flex items-center gap-3">
            <Logo />
            <div className="text-left leading-tight">
              <div className="whitespace-nowrap text-lg font-extrabold">Pasteur Learn</div>
              <span className="text-xs font-bold text-muted">Laredo 2026</span>
            </div>
          </button>

          <div className="flex items-center gap-2">
            <span className="chip bg-streak/15 text-streak" title="Racha de días seguidos">
              <Flame size={16} /> <span className="hidden sm:inline">Racha</span> {user.streak}
              <span className="hidden sm:inline">{user.streak === 1 ? 'día' : 'días'}</span>
            </span>
            <span className="chip bg-gold/15 text-gold" title="Puntos acumulados">
              <Star size={16} /> {user.points} <span className="hidden sm:inline">pts</span>
            </span>
            <div className="relative">
              <button onClick={() => setMenu((m) => !m)} className="flex items-center gap-2 rounded-full p-1 pr-3 hover:bg-white/5">
                <span className="grid h-9 w-9 place-items-center rounded-full bg-tutor/30 text-sm font-extrabold text-[#c7bfff]">
                  {initials}
                </span>
                <span className="hidden text-sm font-bold md:inline">
                  {user.full_name} · {user.grade} {user.section}
                </span>
              </button>
              {menu && (
                <div className="card animate-pop absolute right-0 mt-2 w-56 p-2">
                  <div className="px-3 py-2 text-sm text-muted md:hidden">{user.full_name} · {user.grade} {user.section}</div>
                  <button onClick={logout} className="btn-ghost w-full justify-start">
                    <LogOut size={16} /> Cerrar sesión
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        <nav className="mx-auto flex max-w-6xl gap-1 overflow-x-auto px-4 pb-2" aria-label="Secciones">
          {TABS.map(({ to, label, Icon, end }) => (
            <NavLink key={to} to={to} end={end}
              className={({ isActive }) =>
                `flex shrink-0 items-center gap-2 rounded-xl px-4 py-2 text-sm font-bold transition ${
                  isActive ? 'bg-primary text-white' : 'text-muted hover:bg-white/5 hover:text-ink'}`}>
              <Icon size={16} /> {label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}

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
      <header className="sticky top-0 z-40 border-b-[3px] border-navy bg-card/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 pb-2 pt-3">
          <button onClick={() => navigate('/')}
            className="flex items-center gap-3 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent">
            <Logo />
            <div className="border-l border-line pl-3 text-left leading-tight">
              <div className="whitespace-nowrap font-['Bricolage_Grotesque'] text-lg font-extrabold tracking-tight text-navy">Louis Pasteur</div>
              <span className="text-[11px] font-bold uppercase tracking-[0.14em] text-gold">Laredo 2026</span>
            </div>
          </button>

          <div className="flex items-center gap-1.5 sm:gap-2">
            <span className="chip num border border-streak/25 bg-streak/[0.08] text-streak" title="Racha de días seguidos">
              <Flame size={16} /> <span className="hidden sm:inline">Racha</span> {user.streak}
              <span className="hidden sm:inline">{user.streak === 1 ? 'día' : 'días'}</span>
            </span>
            <span className="chip num border border-gold/25 bg-gold/[0.08] text-gold" title="Puntos acumulados">
              <Star size={16} /> {user.points} <span className="hidden sm:inline">pts</span>
            </span>
            <div className="relative">
              <button onClick={() => setMenu((m) => !m)} aria-expanded={menu}
                className={`flex items-center gap-2 rounded-full p-1 pr-1 transition hover:bg-navy/5 md:pr-3 ${menu ? 'bg-navy/5' : ''}`}>
                <span className="grid h-9 w-9 place-items-center rounded-full bg-navy text-sm font-extrabold text-white ring-2 ring-accent ring-offset-2 ring-offset-card">
                  {initials}
                </span>
                <span className="hidden text-sm font-bold md:inline">
                  {user.full_name} · {user.grade} {user.section}
                </span>
              </button>
              {menu && (
                <div className="card animate-pop absolute right-0 mt-2 w-56 p-1.5 shadow-lg shadow-ink/10">
                  <div className="border-b border-line px-3 py-2 text-sm text-muted md:hidden">{user.full_name} · {user.grade} {user.section}</div>
                  <button onClick={logout} className="btn-ghost w-full justify-start hover:bg-streak/10 hover:text-streak">
                    <LogOut size={16} /> Cerrar sesión
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Pestañas tipo carpeta: la activa se apoya sobre la línea azul del encabezado */}
        <nav className="mx-auto -mb-[3px] flex max-w-6xl gap-0.5 overflow-x-auto px-4 pt-1" aria-label="Secciones">
          {TABS.map(({ to, label, Icon, end }) => (
            <NavLink key={to} to={to} end={end}
              className={({ isActive }) =>
                `group relative flex shrink-0 items-center gap-2 rounded-t-lg px-4 pb-2.5 pt-2 text-sm font-bold transition
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent ${
                  isActive ? 'bg-navy text-white' : 'text-muted hover:bg-navy/5 hover:text-ink'}`}>
              {({ isActive }) => (
                <>
                  <Icon size={16} className={isActive ? 'text-accent' : 'transition group-hover:text-navy'} /> {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-7">
        <Outlet />
      </main>
    </div>
  )
}

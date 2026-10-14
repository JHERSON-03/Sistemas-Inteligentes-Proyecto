import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { Loading } from './components/ui'
import { useAuth } from './context/AuthContext'
import Assessment from './pages/Assessment'
import AtrapaRespuesta from './pages/AtrapaRespuesta'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Metrics from './pages/Metrics'
import Register from './pages/Register'
import RouteDetail from './pages/RouteDetail'
import RoutesPage from './pages/Routes'
import Tutor from './pages/Tutor'

function Private({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <Loading />
  return user ? children : <Navigate to="/login" replace />
}

function PublicOnly({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <Loading />
  return user ? <Navigate to="/" replace /> : children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />
      <Route path="/registro" element={<PublicOnly><Register /></PublicOnly>} />
      <Route element={<Private><Layout /></Private>}>
        <Route index element={<Dashboard />} />
        <Route path="tutor" element={<Tutor />} />
        <Route path="rutas" element={<RoutesPage />} />
        <Route path="rutas/:id" element={<RouteDetail />} />
        <Route path="autoevaluacion" element={<Assessment />} />
        <Route path="metricas" element={<Metrics />} />
        <Route path="juegos" element={<AtrapaRespuesta />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

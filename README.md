# Pasteur Learn · Laredo 2026

Plataforma de aprendizaje autónomo con Tutor IA para alumnos de 5to de secundaria del Colegio Louis Pasteur (Laredo, Perú).
Las pantallas provienen del proyecto de Google Stitch **"Dark Theme Interactive WebApp"** y del prompt en [docs/prompt-stitch-pasteur.md](docs/prompt-stitch-pasteur.md).

## Stack

| Capa | Tecnología | Por qué |
|---|---|---|
| Frontend | React 18 + Vite + TailwindCSS + React Router + lucide-react | Stitch genera Tailwind; la paleta del design system "Nocturnal Scholar" se pasó a `tailwind.config.js` |
| Backend | Python + FastAPI + SQLAlchemy + SQLite + JWT | Python facilita la parte de sistemas inteligentes (tutor IA, adaptatividad, métricas) |
| IA | Groq (gratis) o xAI Grok vía API compatible con OpenAI + motor socrático local | Sin API key el tutor funciona igual con reglas |

## Estructura

```
backend/
  app/
    main.py            # App FastAPI, CORS, creación de tablas y datos iniciales
    config.py          # Variables de entorno y reglas de puntos
    models.py          # Tablas: usuarios, rutas, actividades, evaluaciones, retos, tutor, tiempo de estudio
    security.py        # Contraseñas (PBKDF2) y JWT
    seed.py            # Cursos, 8 rutas con 37 actividades, autoevaluación, retos y alumnos de 5to B
    routers/           # auth, dashboard, routes, assessment, tutor, metrics
    services/
      gamification.py  # Racha, puntos, tiempo semanal, logros
      adaptive.py      # Nivel por desempeño, recomendación de rutas, nivel de autonomía
      tutor_ai.py      # Tutor socrático (Groq/Grok o motor local)
frontend/
  src/
    api/client.js      # Cliente HTTP con token
    context/           # Sesión (AuthContext) y avisos emergentes (ToastContext)
    components/        # Layout (barra superior + pestañas) y componentes de UI
    pages/             # Login, Register, Dashboard, Tutor, Routes, RouteDetail, Assessment, Metrics
  public/img/          # Ilustraciones generadas en Stitch
docs/                  # Prompt original de Stitch
```

## Cómo ejecutar

**Backend** (puerto 8000):

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows (en Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # opcional: agrega LLM_API_KEY (Groq o Grok) para el tutor IA
uvicorn app.main:app --reload --port 8000
```

La base `pasteur.db` se crea sola con datos de ejemplo. Documentación de la API: http://localhost:8000/docs

**Frontend** (puerto 5173, redirige `/api` al backend):

```bash
cd frontend
npm install
npm run dev
```

Abre http://localhost:5173

### Usuario de prueba

| Usuario | DNI | Contraseña |
|---|---|---|
| `joaquin` (Joaquín Paredes · 5to Sec. B) | `70000001` | `pasteur2026` |

Compañeros de salón para el ranking: `valeria`, `diego`, `camila`, `mateo`, `lucia` (misma contraseña).
Para volver a los datos iniciales borra `backend/pasteur.db`.

## Pantallas y lógica

| Pantalla | Ruta | Lógica |
|---|---|---|
| Inicio de sesión | `/login` | Login con usuario o DNI, mostrar/ocultar contraseña, registro de la racha del día |
| Registro de cuenta | `/registro` | Validación de DNI (8 dígitos), usuario y contraseña |
| Inicio / Dashboard | `/` | Racha, puntos, horas de la semana vs. meta, temas dominados, racha semanal L–D, avance por curso, siguiente paso de la IA, reto del día (+10 pts, uno por día), logros, ranking del salón |
| Tutor IA Socrático | `/tutor` | Chat por curso con historial guardado, sugerencias, reiniciar diálogo, +5 pts por sesión. Nunca da la respuesta directa |
| Rutas Adaptativas | `/rutas`, `/rutas/:id` | Filtros por curso, progreso, nivel básico/intermedio/avanzado según aciertos al primer intento, ruta recomendada por la IA, actividades con pista al fallar, +10 pts por actividad y bonus al terminar la ruta |
| Autoevaluación | `/autoevaluacion` | 5 preguntas de cinemática, nivel de confianza, retroalimentación verde/naranja, +10 pts por acierto, resumen final |
| Mis Métricas | `/metricas` | Avance por curso, uso del tiempo, racha, puntos, nivel de autonomía (1–4), comentario de la IA y calendario del mes |

### Reglas de racha y puntos

- La racha suma 1 cuando el alumno ingresa un día después del último ingreso; si falta un día vuelve a empezar (con mensaje animador).
- Puntos: +10 por actividad, bonus de la ruta al completarla (+40 a +60), +10 por acierto en la autoevaluación, +10 por el reto del día, +5 por sesión con el tutor.

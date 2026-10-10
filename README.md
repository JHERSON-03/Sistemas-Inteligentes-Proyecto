# Louis Pasteur · Laredo 2026

> Sistemas-Inteligentes-Proyecto: un proyecto de la universidad para desarrollar grupalmente.

Plataforma de aprendizaje autónomo con Tutor IA para alumnos de 1ro de secundaria del Colegio Louis Pasteur (Laredo, Perú).
Las pantallas provienen del proyecto de Google Stitch **"Dark Theme Interactive WebApp"** y del prompt en [docs/prompt-stitch-pasteur.md](docs/prompt-stitch-pasteur.md).

## Stack

| Capa | Tecnología | Por qué |
|---|---|---|
| Frontend | React 18 + Vite + TailwindCSS + React Router + lucide-react | Stitch genera Tailwind; la paleta del design system "Nocturnal Scholar" se pasó a `tailwind.config.js` |
| Backend | Python + FastAPI + SQLAlchemy + PostgreSQL (Supabase) + JWT | Python facilita la parte de sistemas inteligentes (tutor IA, adaptatividad, métricas) |
| IA | Groq (gratis) o xAI Grok vía API compatible con OpenAI + motor socrático local | Sin API key el tutor funciona igual con reglas |

## Estructura (MVC)

El backend sigue el patrón **Modelo–Vista–Controlador**:

- **Modelo** (`models/` + `services/`): las entidades de la base de datos y las reglas del negocio.
- **Vista** (`views/` en el backend, que arma las respuestas JSON, y el frontend React, que las muestra).
- **Controlador** (`controllers/`): recibe cada petición HTTP, usa los modelos y servicios y responde con una vista.

```
backend/
  app/
    main.py            # App FastAPI, CORS, registro de controladores, creación de tablas y datos iniciales
    core/
      config.py        # Variables de entorno y reglas de puntos
      database.py      # Conexión a Supabase (PostgreSQL) o SQLite local
      security.py      # Contraseñas (bcrypt, compatible con pgcrypto) y JWT
    models/            # MODELO: mapeo a las tablas en español (usuarios, rutas, actividades, evaluaciones, retos...)
    services/          # MODELO (lógica de negocio)
      gamification.py  # Racha, puntos, tiempo semanal, logros
      adaptive.py      # Nivel por desempeño, recomendación de rutas, nivel de autonomía
      tutor_ai.py      # Tutor socrático (Groq/Grok o motor local)
    views/             # VISTA: arma las respuestas JSON de cada sección
    controllers/       # CONTROLADOR: endpoints de auth, dashboard, routes, assessment, tutor, metrics
    schemas.py         # Validación de los datos que llegan en cada petición
    seed.py            # Contenido académico y datos de ejemplo para una base vacía
    cargar_contenido.py # Agrega a la base el contenido que falte, sin tocar usuarios ni progreso
frontend/             # VISTA: interfaz en React
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
copy .env.example .env          # completa DATABASE_URL (Supabase) y LLM_API_KEY (Groq o Grok)
uvicorn app.main:app --reload --port 8000
```

### Base de datos (Supabase)

En `backend/.env` coloca la URL de Supabase (**Connect → Direct → Session pooler**, puerto 5432) con la contraseña real:

```
DATABASE_URL=postgresql://postgres.xxxxxxxx:CONTRASEÑA@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

Para cargar en la base el contenido académico que falte (rutas, actividades, autoevaluación y retos):

```bash
.venv\Scripts\python -m app.cargar_contenido            # simulación: muestra lo que agregaría
.venv\Scripts\python -m app.cargar_contenido --aplicar  # lo guarda
```

Sin `DATABASE_URL` de Supabase se usa SQLite local (`pasteur.db`), que se crea sola con datos de ejemplo.
Documentación de la API: http://localhost:8000/docs

**Frontend** (puerto 5173, redirige `/api` al backend):

```bash
cd frontend
npm install
npm run dev
```

Abre http://localhost:5173

### Usuarios

- **Supabase:** se ingresa con los usuarios registrados en la tabla `usuarios` (contraseñas en bcrypt).
- **SQLite local (modo demo):** usuario `joaquin` / DNI `70000001`, contraseña `pasteur2026`. Compañeros: `valeria`, `diego`, `camila`, `mateo`, `lucia` (misma contraseña). Para reiniciar los datos borra `backend/pasteur.db`.

## Publicar en Vercel (frontend + backend 24/7)

El proyecto se publica como **un solo proyecto de Vercel** usando *Services* (configurado en `vercel.json`):
el frontend (Vite) atiende todas las páginas y las peticiones a `/api/...` van al backend FastAPI.

1. En https://vercel.com inicia sesión con GitHub y elige **Add New → Project**.
2. Importa el repositorio `Sistemas-Inteligentes-Proyecto`. Deja la carpeta raíz (*Root Directory*) en `./`.
3. En **Environment Variables** agrega:

   | Variable | Valor |
   |---|---|
   | `DATABASE_URL` | URL de Supabase en modo **Transaction pooler** (puerto **6543**), con la contraseña real |
   | `LLM_API_KEY` | API key de Groq |
   | `SECRET_KEY` | Texto largo y aleatorio (mínimo 32 caracteres) para firmar las sesiones |
   | `LLM_PROVIDER` | `groq` (opcional) |

4. Presiona **Deploy**. Cada `git push` a `main` vuelve a publicar automáticamente.

> En Vercel el backend no crea tablas al arrancar (la base de Supabase ya está lista). Para cargar o reemplazar
> contenido usa `cargar_contenido` desde tu PC.

## Pantallas y lógica

| Pantalla | Ruta | Lógica |
|---|---|---|
| Inicio de sesión | `/login` | Login con usuario o DNI, mostrar/ocultar contraseña, registro de la racha del día |
| Registro de cuenta | `/registro` | Validación de DNI (8 dígitos), usuario y contraseña |
| Inicio / Dashboard | `/` | Racha, puntos, horas de la semana vs. meta, temas dominados, racha semanal L–D, avance por curso, siguiente paso de la IA, reto del día (+10 pts, uno por día), logros, ranking del salón |
| Tutor IA Socrático | `/tutor` | Chat por curso con historial guardado, sugerencias, reiniciar diálogo, +5 pts por sesión. Nunca da la respuesta directa |
| Rutas Adaptativas | `/rutas`, `/rutas/:id` | Filtros por curso, progreso, nivel básico/intermedio/avanzado según aciertos al primer intento, ruta recomendada por la IA, actividades con pista al fallar, +10 pts por actividad y bonus al terminar la ruta |
| Autoevaluación | `/autoevaluacion` | Selector de evaluaciones (p. ej. "Rapidez y movimiento", 5 preguntas), nivel de confianza, retroalimentación verde/naranja, +10 pts por acierto, resumen final |
| Mis Métricas | `/metricas` | Avance por curso, uso del tiempo, racha, puntos, nivel de autonomía (1–4), comentario de la IA y calendario del mes |

### Reglas de racha y puntos

- La racha suma 1 cuando el alumno ingresa un día después del último ingreso; si falta un día vuelve a empezar (con mensaje animador).
- Puntos: +10 por actividad, bonus de la ruta al completarla (+40 a +60), +10 por acierto en la autoevaluación, +10 por el reto del día, +5 por sesión con el tutor.

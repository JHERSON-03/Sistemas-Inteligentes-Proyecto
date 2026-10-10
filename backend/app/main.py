from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import FRONTEND_ORIGIN, INIT_DB
from .core.database import Base, SessionLocal, engine
from .controllers import assessment, auth, dashboard, metrics, routes, tutor
from .seed import seed


@asynccontextmanager
async def lifespan(_: FastAPI):
    if INIT_DB:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            seed(db)
    yield


app = FastAPI(title="Louis Pasteur API", version="1.0.0", lifespan=lifespan,
              description="Backend de la plataforma de aprendizaje autónomo del Colegio Louis Pasteur de Laredo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


for r in (auth.router, dashboard.router, routes.router, assessment.router, tutor.router, metrics.router):
    app.include_router(r)

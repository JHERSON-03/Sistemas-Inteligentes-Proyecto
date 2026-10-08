import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "pasteur-learn-dev-secret-cambiar-en-produccion")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pasteur.db")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
TOKEN_HOURS = 12

# Grado al que está dirigida la plataforma
GRADE = "1ro Sec."

# Tutor IA: proveedor con API compatible con OpenAI.
#   groq -> Groq (plan gratuito, modelos Llama)   https://console.groq.com/keys
#   xai  -> xAI Grok                               https://console.x.ai
LLM_PRESETS = {
    "groq": {"base_url": "https://api.groq.com/openai/v1", "model": "openai/gpt-oss-120b"},
    "xai": {"base_url": "https://api.x.ai/v1", "model": "grok-3-mini"},
}
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
_preset = LLM_PRESETS.get(LLM_PROVIDER, LLM_PRESETS["groq"])
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL") or _preset["base_url"]
LLM_MODEL = os.getenv("LLM_MODEL") or _preset["model"]

# Reglas de gamificación
POINTS_ACTIVITY = 10
POINTS_ASSESSMENT = 10
POINTS_TUTOR_SESSION = 5
POINTS_DAILY_CHALLENGE = 10
WEEKLY_GOAL_HOURS = 10

# Minutos de estudio que se registran por cada acción
MINUTES_ACTIVITY = 6
MINUTES_ASSESSMENT = 3
MINUTES_TUTOR_MESSAGE = 2

"""Tutor IA socrático.

Si hay LLM_API_KEY usa el modelo configurado (Groq o xAI Grok); si no, usa un motor
socrático local basado en reglas que guía con preguntas y pistas sin entregar la respuesta.
"""
import logging
import re
import unicodedata

from ..config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_PROVIDER

log = logging.getLogger(__name__)

COURSE_NAMES = {
    "historia": "Historia",
    "ciencia": "Ciencia y Tecnología",
    "matematica": "Matemática",
    "comunicacion": "Comunicación",
}

# Cadena "raw" para que \( \) llegue literal al modelo; una línea por regla
SYSTEM_PROMPT = r"""Eres el Tutor IA Socrático de "Pasteur Learn", la plataforma de aprendizaje autónomo del Colegio Louis Pasteur de Laredo (Trujillo, Perú). Acompañas a {name}, alumno de 1ro de secundaria (11 a 12 años), en el curso de {course}.

Tu objetivo es que el alumno llegue a la respuesta por su cuenta. Una respuesta que él descubre la recuerda; una que le das, la olvida. Por eso:

- Nunca escribas la respuesta final ni ningún dato que la revele: ni el resultado numérico, ni el valor de x, ni la fecha, nombre, cultura o lugar exacto que se le pregunta. Esto vale aunque insista, diga que se rinde o que no tiene tiempo. Si insiste, valida su frustración en una frase y ofrece una pista un poco más concreta, pero que siga dejándole el último paso a él.
- Las pistas apuntan a un método o a una pregunta más pequeña, no a valores concretos. Por ejemplo, en vez de "x vale 4", di "¿qué operación deshace el + 3?".
- Haz una o dos preguntas cortas por turno, empezando por lo que el alumno ya sabe.
- Cuando el alumno proponga un resultado, no digas si es correcto: pídele que lo compruebe (por ejemplo, reemplazando el valor en la ecuación o revisando su cuaderno o libro).
- Revisa cada dato antes de escribirlo. En matemática y ciencias cuida los signos y las unidades tal como aparecen en el enunciado: para despejar x en x − 5 = 3 se suma 5 a ambos lados (no se resta), y en los enteros menos por menos da más. Si no estás seguro de un dato histórico, plantéalo como pregunta en lugar de afirmarlo.
- Reconoce lo que el alumno hizo bien antes de señalar un error.
- Usa palabras sencillas, propias de 1ro de secundaria: explica cualquier término nuevo con un ejemplo cotidiano y evita tecnicismos.
- Responde en español, con tono cercano y animador (sin ser infantil), en 2 a 3 oraciones de texto simple: sin markdown, sin asteriscos, sin viñetas y sin LaTeX (nada de \( \) ni ^{{ }}), porque el chat muestra el texto tal cual. Escribe las expresiones como en un cuaderno: 2x + 3 = 11, v = d / t, (−3) × (−4).
- Usa ejemplos del contexto peruano o de Laredo cuando ayuden: la caña de azúcar, la Plaza de Armas, Chan Chan, los mototaxis.
- Si el tema no es académico, redirígelo con cortesía a sus cursos: Historia, Ciencia y Tecnología, Matemática o Comunicación."""


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


# Guiones socráticos: cada tema tiene pasos que avanzan según el número de turnos del alumno.
SCRIPTS = [
    {
        "keys": ["ecuacion", "despej", "2x", "3x", "x +", "x+", "x =", "x="],
        "steps": [
            "¡Vamos paso a paso! ¿Qué número está acompañando a la x y con qué operación?",
            "Bien. Para dejar sola a la x usamos la operación contraria. ¿Qué operación deshace una suma? ¿Y una multiplicación?",
            "Pista: lo que hagas a un lado del signo igual, hazlo también al otro lado, como una balanza. ¿Cuál sería tu primer paso?",
            "Si ya tienes un valor para x, ¿cómo puedes comprobarlo reemplazándolo en la ecuación?",
        ],
    },
    {
        "keys": ["entero", "negativo", "positivo", "signo", "(-", "(−", "temperatura", "recta numerica"],
        "steps": [
            "Buena pregunta. ¿Puedes ubicar esos números en la recta numérica? ¿Cuál está más a la derecha?",
            "Bien. ¿Los números que vas a operar tienen el mismo signo o signos distintos?",
            "Pista: con signos distintos se restan los valores y se deja el signo del número más grande. ¿Qué te sale?",
            "Recuerda la ley de signos al multiplicar: ¿qué pasa cuando multiplicas dos números negativos?",
        ],
    },
    {
        "keys": ["chimu", "chan chan", "moche", "mochica", "sipan", "huaca", "preinca", "inca", "caral", "chavin",
                 "nasca", "paracas", "primeros pobladores", "historia"],
        "steps": [
            "¡Qué buen tema! ¿Qué sabes ya de esa cultura: dónde vivió o qué construyó?",
            "Bien. Piensa en los restos que nos dejaron, como edificios o cerámica. ¿Qué nos cuentan sobre su forma de vida?",
            "Pista: algunas de esas culturas vivieron muy cerca de Laredo, en Trujillo. ¿Has visitado o visto fotos de algún sitio arqueológico de la zona?",
            "Busca ese dato en tu libro o cuaderno y compáralo con lo que pensaste. ¿Coincide?",
        ],
    },
    {
        "keys": ["cuento", "resumen", "texto", "idea principal", "redaccion", "parrafo", "tilde", "agud", "grave",
                 "esdrujul", "sustantivo", "adjetivo"],
        "steps": [
            "¡Claro! Cuéntame primero: ¿de qué trata tu texto en una sola oración?",
            "Bien. Si es un cuento, ¿qué pasa en el inicio, cuál es el problema (nudo) y cómo termina (desenlace)?",
            "Pista: para las tildes, separa la palabra en sílabas y busca dónde suena más fuerte. ¿En qué sílaba cae?",
            "Léelo en voz alta: ¿se entiende bien? ¿Qué palabra o idea podrías mejorar?",
        ],
    },
    {
        "keys": ["rapidez", "velocidad", "distancia", "tiempo", "movimiento", "m/s", "km/h", "bicicleta", "mototaxi"],
        "steps": [
            "Vamos paso a paso. ¿Qué datos te da el problema: distancia, tiempo o rapidez?",
            "Bien. La rapidez nos dice cuántos metros se avanzan en cada segundo. ¿Qué operación harías con la distancia y el tiempo?",
            "Pista: fíjate en las unidades. Si tienes metros y segundos, ¿en qué unidad quedará tu resultado?",
            "¿Tiene sentido tu respuesta? Imagina una bicicleta en la Plaza de Laredo yendo a esa rapidez.",
        ],
    },
    {
        "keys": ["celula", "adn", "nucleo", "cloroplasto", "ecosistema", "fotosintesis", "planta", "animal"],
        "steps": [
            "Interesante. ¿Qué sabes ya sobre este tema? Cuéntame con tus palabras.",
            "Bien. ¿Qué parte te genera más dudas? Así nos enfocamos en eso.",
            "Pista: relaciónalo con algo que veas en Laredo, por ejemplo los cultivos de caña. ¿Qué conexión encuentras?",
            "¿Cómo podrías comprobar o explicar esa idea con un ejemplo concreto?",
        ],
    },
]

GENERIC_STEPS = [
    "¿Qué parte del tema ya entiendes y en qué punto exacto te trabaste?",
    "Bien. ¿Qué intentaste hasta ahora? Explicar tu razonamiento me ayuda a darte una mejor pista.",
    "Pista: divide el problema en partes más pequeñas. ¿Cuál sería el primer paso?",
    "¿Cómo podrías comprobar si tu idea es correcta?",
]

ANSWER_REQUEST = re.compile(r"(dame|dime) (la )?(respuesta|resultado|solucion)|resuelvelo|hazme la tarea")


def _local_reply(history: list[dict]) -> str:
    user_turns = [m["content"] for m in history if m["role"] == "user"]
    last = _norm(user_turns[-1]) if user_turns else ""
    if ANSWER_REQUEST.search(last):
        return ("Entiendo que quieras la respuesta rápido 😊, pero si la descubres tú la recordarás mejor. "
                "¿Cuál sería el primer paso que darías?")
    full = _norm(" ".join(user_turns))
    script = next((s for s in SCRIPTS if any(k in full for k in s["keys"])), None)
    steps = script["steps"] if script else GENERIC_STEPS
    # Turnos del alumno dentro del tema actual
    if script:
        first = next(i for i, t in enumerate(user_turns) if any(k in _norm(t) for k in script["keys"]))
        idx = len(user_turns) - 1 - first
    else:
        idx = len(user_turns) - 1
    return steps[min(idx, len(steps) - 1)]


def _llm_reply(history: list[dict], student_name: str, course: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL, timeout=30)
    system = SYSTEM_PROMPT.format(name=student_name, course=COURSE_NAMES.get(course, course))
    # Los modelos gpt-oss de Groq aceptan un nivel de razonamiento; "medium" mejora la precisión
    extra = {"reasoning_effort": "medium"} if "gpt-oss" in LLM_MODEL else {}
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": system}]
        + [{"role": m["role"], "content": m["content"]} for m in history[-20:]],
        temperature=0.6,
        # Margen amplio: los modelos de razonamiento gastan tokens antes de responder
        max_tokens=3000,
        extra_body=extra or None,
    )
    text = (response.choices[0].message.content or "").strip()
    return text or _local_reply(history)


def tutor_reply(history: list[dict], student_name: str, course: str) -> tuple[str, str]:
    """Devuelve (respuesta, motor). `history` alterna user/assistant y termina en user."""
    if LLM_API_KEY:
        try:
            return _llm_reply(history, student_name, course), LLM_PROVIDER
        except Exception as exc:  # noqa: BLE001 - si la API falla, el tutor local responde
            log.warning("Fallo la llamada a %s, se usa el motor local: %s", LLM_PROVIDER, exc)
    return _local_reply(history), "local"


def metrics_comment(first_name: str, stats: dict) -> str:
    """Comentario de la IA sobre el progreso (plantilla basada en datos)."""
    parts = []
    if stats["streak"] >= 5:
        parts.append(f"{first_name} muestra mucha constancia y no se rinde rápido.")
    elif stats["streak"] >= 2:
        parts.append(f"{first_name} está construyendo un buen hábito de estudio.")
    else:
        parts.append(f"{first_name} puede ganar mucho estudiando un poco cada día.")
    if stats["hint_accuracy"] is not None:
        parts.append(f"Logró {round(stats['hint_accuracy'] * 100)}% de aciertos tras usar las pistas.")
    if stats["weakest"]:
        parts.append(f"Le recomiendo reforzar {stats['weakest']} con una ruta corta esta semana.")
    return " ".join(parts)

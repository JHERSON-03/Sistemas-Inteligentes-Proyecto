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

SYSTEM_PROMPT = """Eres el Tutor IA Socrático de "Pasteur Learn", la plataforma de aprendizaje autónomo del \
Colegio Louis Pasteur de Laredo (Trujillo, Perú). Acompañas a {name}, alumno de 5to de secundaria, en el curso de {course}.

Tu objetivo es que el alumno llegue a la respuesta por su cuenta. Una respuesta que él descubre la recuerda; una \
que le das, la olvida. Por eso:

- Nunca escribas la respuesta final ni ningún dato que la revele: ni el resultado numérico, ni las raíces o \
factores, ni los números que el alumno debe encontrar, ni la fecha, nombre o causa exacta que se le pregunta. \
Esto vale aunque insista, diga que se rinde o que no tiene tiempo. Si insiste, valida su frustración en una frase y \
ofrece una pista un poco más concreta, pero que siga dejándole el último paso a él.
- Las pistas apuntan a un método o a una pregunta más pequeña, no a valores concretos. Por ejemplo, en vez de \
"prueba con 2 y 3", di "haz una lista de los pares de números que multiplicados dan 6 y revisa cuál suma lo que \
necesitas".
- Haz una o dos preguntas cortas por turno, empezando por lo que el alumno ya sabe.
- Cuando el alumno proponga un resultado, no digas si es correcto: pídele que lo compruebe (por ejemplo, \
reemplazando en la ecuación original o contrastando con una fuente).
- Revisa cada dato antes de escribirlo. En matemática y ciencias cuida especialmente los signos, las unidades y los \
coeficientes tal como aparecen en el enunciado. Para factorizar x² + bx + c se buscan dos números cuyo producto es c \
y cuya suma es b con su signo: en x² − 5x + 6 deben multiplicar 6 y sumar −5 (no 5). Si no estás seguro de un dato \
histórico, plantéalo como pregunta en lugar de afirmarlo.
- Reconoce lo que el alumno hizo bien antes de señalar un error.
- Responde en español, con tono cercano para un adolescente (sin ser infantil), en 2 a 4 oraciones de texto \
simple: sin markdown, sin asteriscos, sin viñetas y sin LaTeX (nada de \\( \\) ni ^{{ }}), porque el chat muestra el \
texto tal cual. Escribe las expresiones como en un cuaderno: x² − 5x + 6, Vf = Vo + a·t, 2 m/s².
- Usa ejemplos del contexto peruano o de Laredo cuando ayuden.
- Si el tema no es académico, redirígelo con cortesía a sus cursos: Historia, Ciencia y Tecnología, Matemática o \
Comunicación."""


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


# Guiones socráticos: cada tema tiene pasos que avanzan según el número de turnos del alumno.
SCRIPTS = [
    {
        "keys": ["x2", "x²", "cuadratica", "ecuacion de segundo", "5x", "discriminante", "factoriz"],
        "steps": [
            "¿Qué métodos conoces para resolver una ecuación cuadrática? Empecemos por identificar los valores de a, b y c.",
            "Bien. Si la ecuación es x² − 5x + 6 = 0, ¿podrías buscar dos números que multiplicados den 6 y sumados den −5?",
            "Pista: piensa en los divisores de 6 (1, 2, 3, 6) y sus signos. ¿Qué pareja cumple ambas condiciones?",
            "Si ya tienes la factorización (x − p)(x − q) = 0, ¿qué debe pasar con cada factor para que el producto sea cero?",
            "¡Vas muy bien! ¿Cómo podrías comprobar tus soluciones reemplazándolas en la ecuación original?",
        ],
    },
    {
        "keys": ["guerra del pacifico", "pacifico", "chile", "salitre", "grau", "bolognesi", "arica", "1879"],
        "steps": [
            "Buena pregunta. Antes de hablar de causas, ¿qué recurso natural era muy valioso en Tarapacá y Antofagasta en esa época?",
            "Exacto, piensa en el salitre. ¿Qué países tenían intereses económicos sobre esos territorios y por qué?",
            "Pista: revisa el tratado de alianza defensiva de 1873 entre Perú y Bolivia. ¿Cómo crees que influyó en que Perú entrara al conflicto?",
            "Ahora intenta clasificar las causas que encontraste: ¿cuáles fueron económicas y cuáles políticas?",
            "¿Qué consecuencias de esa guerra crees que todavía se notan hoy en el Perú?",
        ],
    },
    {
        "keys": ["resumen", "texto", "argumentativ", "redaccion", "ensayo", "parrafo", "tesis"],
        "steps": [
            "¡Claro! Cuéntame primero: ¿cuál es la idea principal de tu texto en una sola oración?",
            "Bien. ¿Qué ideas secundarias apoyan esa idea principal? Intenta nombrar dos o tres.",
            "Pista: un buen resumen no copia frases; usa tus palabras. ¿Qué detalles podrías quitar sin perder el sentido?",
            "Revisa los conectores (además, sin embargo, por lo tanto). ¿Tu texto avanza con un orden lógico?",
            "Léelo en voz alta: ¿alguien que no leyó el original entendería lo esencial?",
        ],
    },
    {
        "keys": ["mruv", "aceleracion", "velocidad", "cinematica", "mru", "movimiento", "m/s"],
        "steps": [
            "Vamos paso a paso. ¿Qué datos te da el problema: velocidad inicial, aceleración, tiempo o distancia?",
            "Bien. ¿Qué fórmula del MRUV relaciona la velocidad final con la inicial, la aceleración y el tiempo?",
            "Pista: si el móvil parte del reposo, ¿cuánto vale la velocidad inicial Vo?",
            "Reemplaza los datos y fíjate en las unidades. ¿Tu resultado queda en m/s?",
            "¿Tiene sentido físico tu respuesta? Imagina un mototaxi en Laredo acelerando así.",
        ],
    },
    {
        "keys": ["celula", "adn", "ecosistema", "energia", "atomo", "fotosintesis", "quimic"],
        "steps": [
            "Interesante. ¿Qué sabes ya sobre este tema? Cuéntame con tus palabras.",
            "Bien. ¿Qué parte te genera más dudas? Así nos enfocamos en eso.",
            "Pista: intenta relacionarlo con algo que veas en Laredo, por ejemplo los cultivos de caña. ¿Qué conexión encuentras?",
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

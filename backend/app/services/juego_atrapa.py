"""Minijuego "Atrapa la respuesta": consignas, armado de rondas y cálculo del puntaje.

La ronda viaja al alumno como un token firmado (ronda_id) que guarda la consigna y los elementos.
Así el backend puede recalcular el puntaje sin guardar la ronda en la base de datos (funciona en Vercel).
"""
import random
import time
from datetime import datetime, timedelta, timezone

import jwt

from ..core.config import SECRET_KEY

JUEGO = "atrapa_respuesta"
DURACION_SEGUNDOS = 30
ELEMENTOS_POR_RONDA = 20
# Partidas que cada alumno puede registrar por día, a la hora que quiera
PARTIDAS_POR_DIA = 3
# Perú está en UTC-5 todo el año: el día del alumno empieza a las 00:00 de Lima
ZONA_PERU = timezone(timedelta(hours=-5))
PUNTOS_ACIERTO = 10
PUNTOS_ERROR = -5
# Cada 10 puntos del juego suman 1 punto de la plataforma (una ronda perfecta ≈ una actividad)
PUNTOS_JUEGO_POR_PUNTO = 10
# Tolerancia para la latencia de red entre el fin del juego y el envío del resultado
MARGEN_SEGUNDOS = 5
VIGENCIA_SEGUNDOS = 10 * 60

# Clave propia: un ronda_id nunca sirve como token de sesión
_CLAVE = f"{SECRET_KEY}:juego-atrapa"


def _numeros(condicion) -> tuple[list[str], list[str]]:
    correctos = [str(n) for n in range(1, 100) if condicion(n)]
    incorrectos = [str(n) for n in range(1, 100) if not condicion(n)]
    return correctos, incorrectos


def _es_primo(n: int) -> bool:
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


CONSIGNAS = [
    {"id": "pares", "texto": "Atrapa los números pares", "elementos": _numeros(lambda n: n % 2 == 0)},
    {"id": "impares", "texto": "Atrapa los números impares", "elementos": _numeros(lambda n: n % 2 == 1)},
    {"id": "multiplos-3", "texto": "Atrapa los múltiplos de 3", "elementos": _numeros(lambda n: n % 3 == 0)},
    {"id": "mayores-50", "texto": "Atrapa los números mayores que 50", "elementos": _numeros(lambda n: n > 50)},
    {"id": "primos", "texto": "Atrapa los números primos", "elementos": _numeros(_es_primo)},
    {"id": "verbos", "texto": "Atrapa los verbos", "elementos": (
        ["correr", "estudiar", "cantar", "escribir", "saltar", "leer", "jugar", "dormir", "pensar", "nadar",
         "aprender", "dibujar"],
        ["mesa", "árbol", "rápido", "feliz", "cuaderno", "azul", "montaña", "alto", "perro", "ventana",
         "hermoso", "lápiz", "río", "suave"],
    )},
    {"id": "sustantivos", "texto": "Atrapa los sustantivos", "elementos": (
        ["casa", "libro", "perro", "Laredo", "escuela", "amistad", "montaña", "lápiz", "ciudad", "flor",
         "maestro", "río"],
        ["correr", "bonito", "rápidamente", "saltar", "grande", "comer", "feliz", "lentamente", "verde",
         "escribir", "alto", "cantar", "suave"],
    )},
    {"id": "adjetivos", "texto": "Atrapa los adjetivos", "elementos": (
        ["alto", "feliz", "rojo", "inteligente", "pequeño", "valiente", "suave", "hermoso", "rápido", "amable",
         "frío", "brillante"],
        ["correr", "mesa", "ayer", "perro", "cantar", "ciudad", "libro", "saltar", "nunca", "escuela", "comer",
         "árbol", "aquí"],
    )},
    {"id": "capitales", "texto": "Atrapa las capitales de Sudamérica", "elementos": (
        ["Lima", "Bogotá", "Quito", "Santiago", "Buenos Aires", "Caracas", "Asunción", "Montevideo", "Brasilia",
         "La Paz", "Sucre", "Georgetown", "Paramaribo"],
        ["Trujillo", "Cusco", "Arequipa", "Madrid", "Medellín", "Guayaquil", "Río de Janeiro", "São Paulo",
         "Córdoba", "Valparaíso", "México", "Panamá", "Roma", "Santa Cruz"],
    )},
    {"id": "vertebrados", "texto": "Atrapa los animales vertebrados", "elementos": (
        ["perro", "águila", "tiburón", "rana", "serpiente", "vicuña", "cóndor", "delfín", "tortuga", "gato",
         "caballo", "lagartija"],
        ["araña", "pulpo", "mariposa", "lombriz", "medusa", "caracol", "hormiga", "cangrejo", "estrella de mar",
         "abeja", "mosquito", "langosta", "esponja"],
    )},
    {"id": "planetas", "texto": "Atrapa los planetas del sistema solar", "elementos": (
        ["Mercurio", "Venus", "Tierra", "Marte", "Júpiter", "Saturno", "Urano", "Neptuno"],
        ["Sol", "Luna", "Plutón", "Ceres", "Titán", "Europa", "Ganímedes", "Fobos", "Halley", "Orión",
         "Andrómeda", "Vía Láctea", "Sirio"],
    )},
]

_POR_ID = {c["id"]: c for c in CONSIGNAS}


def inicio_del_dia() -> datetime:
    """Medianoche de hoy en Lima, en UTC y sin zona (así se guarda partida_fecha)."""
    hoy = datetime.now(ZONA_PERU).replace(hour=0, minute=0, second=0, microsecond=0)
    return hoy.astimezone(timezone.utc).replace(tzinfo=None)


class RondaInvalida(Exception):
    pass


def nueva_ronda(user_id: int) -> dict:
    consigna = random.choice(CONSIGNAS)
    correctos, incorrectos = consigna["elementos"]
    n_correctos = min(random.randint(8, 10), len(correctos))
    elementos = random.sample(correctos, n_correctos) + random.sample(incorrectos, ELEMENTOS_POR_RONDA - n_correctos)
    random.shuffle(elementos)
    # "t" guarda el inicio exacto (con decimales) para no confundir una ronda nueva con la anterior
    ahora = time.time()
    ronda_id = jwt.encode({"u": user_id, "c": consigna["id"], "e": elementos, "t": ahora,
                           "exp": int(ahora) + VIGENCIA_SEGUNDOS}, _CLAVE, algorithm="HS256")
    return {"ronda_id": ronda_id, "consigna": consigna["texto"], "elementos": elementos,
            "duracion": DURACION_SEGUNDOS}


def abrir_ronda(ronda_id: str, user_id: int, terminada: bool = True) -> dict:
    """Valida el token de la ronda y devuelve sus datos (consigna, elementos, inicio).

    terminada=True exige que hayan pasado los 45 s (para guardar el resultado).
    """
    try:
        data = jwt.decode(ronda_id, _CLAVE, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise RondaInvalida("La ronda expiró, juega una nueva")
    except jwt.PyJWTError:
        raise RondaInvalida("Ronda no válida")
    consigna = _POR_ID.get(data.get("c"))
    if data.get("u") != user_id or consigna is None or not isinstance(data.get("t"), (int, float)):
        raise RondaInvalida("Ronda no válida")
    if terminada and time.time() - data["t"] < DURACION_SEGUNDOS - MARGEN_SEGUNDOS:
        raise RondaInvalida("La ronda todavía no termina")
    return {"consigna": consigna, "elementos": data["e"], "inicio": data["t"]}


def es_correcto(ronda: dict, indice: int) -> bool:
    elementos = ronda["elementos"]
    return 0 <= indice < len(elementos) and elementos[indice] in ronda["consigna"]["elementos"][0]


def calificar(ronda: dict, clicados: list[int]) -> dict:
    """Recalcula aciertos, errores y puntaje a partir de los índices que el alumno atrapó."""
    elementos = ronda["elementos"]
    validos = {i for i in clicados if 0 <= i < len(elementos)}
    aciertos = sum(1 for i in validos if es_correcto(ronda, i))
    errores = len(validos) - aciertos
    correctas = [i for i in range(len(elementos)) if es_correcto(ronda, i)]
    return {"aciertos": aciertos, "errores": errores, "correctas": correctas,
            "puntaje": aciertos * PUNTOS_ACIERTO + errores * PUNTOS_ERROR}


def puntos_plataforma(puntaje: int) -> int:
    return max(0, puntaje) // PUNTOS_JUEGO_POR_PUNTO

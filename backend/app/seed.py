"""Datos iniciales: cursos, rutas con actividades, autoevaluación, retos y alumnos de 1ro B.

Contenido alineado al Currículo Nacional (CNEB) para 1ro de secundaria.
"""
from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .config import GRADE
from .security import hash_password

DEMO_PASSWORD = "pasteur2026"


COURSES = [
    ("historia", "Historia", "#F59E0B", "landmark"),
    ("ciencia", "Ciencia y Tecnología", "#22C55E", "flask"),
    ("matematica", "Matemática", "#4F7CFF", "calculator"),
    ("comunicacion", "Comunicación", "#EC4899", "book"),
]

# (curso, título, descripción, minutos, bonus, actividades[(título, pregunta, opciones, respuesta, pista, explicación)])
ROUTES = [
    ("matematica", "Números enteros",
     "Ordena, suma, resta y multiplica números positivos y negativos.", 35, 50, [
         ("Comparar enteros", "¿Cuál número es mayor: −3 o −8?",
          ["−8", "−3", "Son iguales", "No se puede saber"], 1,
          "Ubica ambos números en la recta numérica: el mayor está más a la derecha.",
          "−3 está más cerca del cero que −8, por eso es mayor."),
         ("Suma de enteros", "¿Cuánto es (−5) + 8?",
          ["−13", "3", "−3", "13"], 1,
          "Con signos distintos, resta los valores y deja el signo del número más grande.",
          "8 − 5 = 3, y el signo es positivo porque 8 es mayor que 5."),
         ("Resta de enteros", "¿Cuánto es 4 − (−6)?",
          ["−2", "10", "2", "−10"], 1,
          "Restar un número negativo es lo mismo que sumar su opuesto.",
          "4 − (−6) = 4 + 6 = 10."),
         ("Multiplicación de enteros", "¿Cuánto es (−3) × (−4)?",
          ["−12", "12", "−7", "7"], 1,
          "Recuerda la ley de signos: menos por menos da…",
          "Menos por menos da más: (−3) × (−4) = 12."),
         ("Temperaturas", "En la sierra de La Libertad, la temperatura en la madrugada fue −2 °C y al mediodía subió "
          "15 °C. ¿Qué temperatura hubo al mediodía?",
          ["17 °C", "13 °C", "−17 °C", "15 °C"], 1,
          "Parte de −2 y avanza 15 lugares a la derecha en la recta numérica.",
          "−2 + 15 = 13 °C."),
     ]),
    ("ciencia", "Rapidez y movimiento",
     "Calcula distancias, tiempos y rapidez con ejemplos de la Plaza de Laredo.", 35, 50, [
         ("¿Qué es la rapidez?", "La rapidez se calcula dividiendo…",
          ["el tiempo entre la distancia", "la distancia entre el tiempo", "la distancia por el tiempo",
           "la masa entre el tiempo"], 1,
          "Piensa en cuántos metros avanzas en cada segundo.",
          "Rapidez = distancia ÷ tiempo (v = d / t)."),
         ("Calcula la rapidez", "Un ciclista recorre 100 m en 20 s por la Plaza de Laredo. ¿Cuál es su rapidez?",
          ["5 m/s", "2000 m/s", "80 m/s", "120 m/s"], 0,
          "Usa v = d / t con d = 100 m y t = 20 s.",
          "v = 100 m ÷ 20 s = 5 m/s."),
         ("Unidades", "¿Cuál es la unidad de rapidez en el Sistema Internacional?",
          ["km", "m/s", "s", "kg"], 1,
          "La rapidez combina una unidad de longitud con una de tiempo.",
          "Se mide en metros por segundo (m/s)."),
         ("Calcula la distancia", "Una chica en skate va a 3 m/s durante 10 s. ¿Qué distancia recorre?",
          ["13 m", "30 m", "0,3 m", "7 m"], 1,
          "Despeja la distancia: d = v × t.",
          "d = 3 m/s × 10 s = 30 m."),
         ("Reposo", "Si un objeto está en reposo, su rapidez es…",
          ["0 m/s", "1 m/s", "depende del tiempo", "muy grande"], 0,
          "En reposo el objeto no cambia de posición.",
          "Si no se mueve, no recorre distancia: su rapidez es 0 m/s."),
     ]),
    ("historia", "Culturas preincas del norte",
     "Conoce a los moches y chimúes, que vivieron muy cerca de Laredo.", 35, 50, [
         ("Chan Chan", "¿Qué cultura construyó Chan Chan, la ciudad de barro más grande de América, en Trujillo?",
          ["Moche", "Chimú", "Nasca", "Paracas"], 1,
          "Fue la capital de un reino que luego fue conquistado por los incas.",
          "Chan Chan fue la capital del reino Chimú."),
         ("Huacas del Sol y de la Luna", "Las Huacas del Sol y de la Luna, cerca de Trujillo, pertenecen a la "
          "cultura…",
          ["Chimú", "Moche", "Chavín", "Inca"], 1,
          "Es la misma cultura del Señor de Sipán y de los famosos huacos retrato.",
          "Son templos de la cultura Moche (o Mochica)."),
         ("Señor de Sipán", "El Señor de Sipán fue un gobernante de la cultura…",
          ["Moche", "Wari", "Nasca", "Tiahuanaco"], 0,
          "Su tumba se halló en Lambayeque, en la costa norte.",
          "Fue un gobernante moche; su tumba se descubrió en 1987."),
         ("Cerámica moche", "Los moches son famosos por su cerámica llamada…",
          ["sin decoración", "huacos retrato", "de vidrio", "de metal"], 1,
          "Representaban rostros humanos con mucho detalle.",
          "Los huacos retrato muestran rostros y expresiones de personas."),
         ("Materiales", "¿Qué material usaron principalmente los chimúes para construir Chan Chan?",
          ["Piedra tallada", "Adobe (barro)", "Madera", "Cemento"], 1,
          "Por eso se la conoce como 'la ciudad de barro'.",
          "Chan Chan se construyó con adobe y barro."),
     ]),
    ("comunicacion", "La tildación",
     "Aprende a reconocer palabras agudas, graves y esdrújulas y cuándo llevan tilde.", 30, 40, [
         ("Palabras agudas", "Las palabras agudas llevan tilde cuando terminan en…",
          ["consonante que no sea n ni s", "n, s o vocal", "cualquier letra", "solo en r"], 1,
          "Piensa en 'camión', 'compás' y 'café'.",
          "Las agudas se tildan si terminan en n, s o vocal."),
         ("Palabras graves", "¿Cuál de estas palabras es grave (llana)?",
          ["canción", "árbol", "brújula", "reloj"], 1,
          "En las graves, la sílaba más fuerte es la penúltima.",
          "ÁR-bol: la fuerza de voz está en la penúltima sílaba."),
         ("Palabras esdrújulas", "¿Cuál de estas palabras es esdrújula?",
          ["camión", "lápiz", "música", "papel"], 2,
          "Busca la palabra con la fuerza de voz en la antepenúltima sílaba.",
          "MÚ-si-ca es esdrújula."),
         ("Escritura correcta", "¿Cuál palabra está bien escrita?",
          ["arbol", "lapiz", "camión", "jovén"], 2,
          "Separa en sílabas y aplica las reglas de agudas y graves.",
          "'Camión' es aguda y termina en n, por eso lleva tilde."),
         ("Regla de las esdrújulas", "Las palabras esdrújulas…",
          ["nunca llevan tilde", "siempre llevan tilde", "llevan tilde si terminan en n", "solo a veces"], 1,
          "Piensa en 'brújula', 'música' y 'pájaro'.",
          "Todas las esdrújulas llevan tilde."),
     ]),
    ("matematica", "Ecuaciones de primer grado",
     "Encuentra el valor de x con operaciones inversas.", 30, 40, [
         ("Suma y resta", "Si x + 7 = 15, ¿cuánto vale x?", ["8", "22", "7", "15"], 0,
          "¿Qué operación deshace el + 7?", "Restamos 7 a ambos lados: x = 15 − 7 = 8."),
         ("Multiplicación", "Si 3x = 18, ¿cuánto vale x?", ["15", "6", "21", "54"], 1,
          "¿Qué operación deshace el 'multiplicar por 3'?", "Dividimos entre 3: x = 18 ÷ 3 = 6."),
         ("Dos pasos", "Si 2x + 3 = 11, ¿cuánto vale x?", ["4", "7", "5", "8"], 0,
          "Primero quita el + 3 y luego el 'por 2'.", "2x = 11 − 3 = 8, entonces x = 8 ÷ 2 = 4."),
         ("Problema", "Ana compró 3 cuadernos iguales y un lapicero de S/ 2. En total pagó S/ 17. "
          "¿Cuánto costó cada cuaderno?",
          ["S/ 5", "S/ 6", "S/ 15", "S/ 19"], 0,
          "Plantea 3x + 2 = 17, donde x es el precio de un cuaderno.",
          "3x = 15, entonces x = 5: cada cuaderno costó S/ 5."),
     ]),
    ("comunicacion", "El cuento y la comprensión lectora",
     "Identifica las partes de un cuento y la idea principal de un texto.", 30, 40, [
         ("Partes del cuento", "¿Cuáles son las partes de un cuento?",
          ["inicio, nudo y desenlace", "título, índice y anexo", "tesis y argumentos", "pregunta y respuesta"], 0,
          "Piensa en cómo empieza, qué problema aparece y cómo termina.",
          "Un cuento tiene inicio, nudo y desenlace."),
         ("El nudo", "En el nudo de un cuento…",
          ["se presentan los personajes", "aparece el problema o conflicto", "termina la historia",
           "se escribe el título"], 1,
          "Es la parte más emocionante de la historia.",
          "En el nudo surge el conflicto que deben resolver los personajes."),
         ("Idea principal", "La idea principal de un párrafo es…",
          ["el detalle más curioso", "lo que resume el sentido global", "la primera palabra", "un ejemplo"], 1,
          "Pregúntate: ¿de qué trata todo el párrafo?",
          "Es la idea que resume y engloba a las demás."),
         ("Tipo de texto", "Una noticia sobre la cosecha de caña en Laredo es un texto…",
          ["informativo", "poético", "dramático", "instructivo"], 0,
          "Su objetivo es dar a conocer hechos reales.",
          "Las noticias son textos informativos."),
     ]),
    ("ciencia", "La célula",
     "Descubre la unidad básica de los seres vivos y sus partes.", 35, 40, [
         ("Unidad de la vida", "La unidad básica de todos los seres vivos es…",
          ["el átomo", "la célula", "el órgano", "el tejido"], 1,
          "Todos los seres vivos, desde una bacteria hasta tú, están formados por ella.",
          "La célula es la unidad básica de la vida."),
         ("El núcleo", "¿Qué parte de la célula guarda el material genético (ADN) en las células eucariotas?",
          ["membrana", "núcleo", "citoplasma", "pared celular"], 1,
          "Es como el 'centro de control' de la célula.",
          "El núcleo contiene el ADN y dirige las funciones de la célula."),
         ("Cloroplastos", "¿Qué organelo realiza la fotosíntesis en las células vegetales, como las de la caña "
          "de azúcar?",
          ["mitocondria", "cloroplasto", "ribosoma", "vacuola"], 1,
          "Es de color verde porque tiene clorofila.",
          "Los cloroplastos captan la luz del sol para fabricar alimento."),
         ("Célula vegetal", "¿Qué estructura tienen las células vegetales pero NO las animales?",
          ["membrana celular", "pared celular", "núcleo", "citoplasma"], 1,
          "Le da rigidez y forma a la planta.",
          "La pared celular solo está en células vegetales (y en hongos y bacterias)."),
     ]),
    ("historia", "Primeros pobladores y Caral",
     "Viaja a los orígenes del Perú: cazadores, recolectores y la ciudad más antigua de América.", 30, 40, [
         ("Primeros pobladores", "Los primeros pobladores del Perú eran cazadores y…",
          ["agricultores industriales", "recolectores", "comerciantes de barcos", "mineros"], 1,
          "Obtenían su alimento de lo que encontraban en la naturaleza.",
          "Eran nómadas que cazaban animales y recolectaban frutos."),
         ("Arte rupestre", "Las pinturas rupestres de Toquepala (Tacna) muestran principalmente escenas de…",
          ["batallas navales", "caza", "ciudades", "mercados"], 1,
          "Piensa en la actividad principal de los primeros pobladores.",
          "Muestran escenas de caza de camélidos."),
         ("Agricultura", "La domesticación de plantas y animales dio origen a…",
          ["la agricultura y la ganadería", "la imprenta", "la industria", "el comercio marítimo"], 0,
          "Al cultivar y criar animales, los pueblos pudieron quedarse en un lugar.",
          "Así nacieron la agricultura y la ganadería, y los pueblos se volvieron sedentarios."),
         ("Caral", "Caral, ubicada en Supe (Lima), es considerada…",
          ["la ciudad más antigua de América", "la capital de los incas", "una ciudad colonial", "una ciudad moderna"],
          0,
          "Tiene alrededor de 5000 años de antigüedad.",
          "Caral es la ciudad más antigua de América."),
     ]),
]

ASSESSMENT = ("ciencia", "Desafío: Rapidez y movimiento", [
    ("Un mototaxi recorre 120 m por una calle de Laredo en 20 s con rapidez constante. ¿Cuál es su rapidez?",
     [("2400 m/s", "multiplicando 120 por 20"), ("6 m/s", "dividiendo 120 entre 20"),
      ("100 m/s", "restando 120 − 20"), ("140 m/s", "sumando 120 + 20")], 1,
     "¡Bien hecho! Usaste v = d / t: 120 m ÷ 20 s = 6 m/s.",
     "Casi. La rapidez indica cuántos metros avanza en cada segundo: divide la distancia entre el tiempo."),
    ("Un estudiante va en bicicleta al colegio a 4 m/s y tarda 50 s. ¿Qué distancia recorre?",
     [("200 m", "multiplicando 4 por 50"), ("54 m", "sumando 4 + 50"),
      ("12,5 m", "dividiendo 50 entre 4"), ("46 m", "restando 50 − 4")], 0,
     "¡Correcto! d = v × t = 4 m/s × 50 s = 200 m.",
     "Revisa: si avanza 4 metros cada segundo, ¿cuántos metros avanza en 50 segundos?"),
    ("Un bus de Trujillo a Laredo recorre 10 km en 15 minutos. Otro bus recorre 10 km en 20 minutos. "
     "¿Cuál es más rápido?",
     [("El de 20 minutos", "porque tarda más"), ("Los dos igual", "porque recorren la misma distancia"),
      ("El de 15 minutos", "porque recorre lo mismo en menos tiempo"), ("No se puede saber", "faltan datos")], 2,
     "¡Exacto! En la misma distancia, es más rápido el que tarda menos tiempo.",
     "Piensa: si los dos recorren 10 km, ¿quién llega primero?"),
    ("¿Cuánto tiempo tarda una persona que camina a 2 m/s en recorrer 30 m?",
     [("60 s", "multiplicando 30 por 2"), ("28 s", "restando 30 − 2"),
      ("32 s", "sumando 30 + 2"), ("15 s", "dividiendo 30 entre 2")], 3,
     "¡Muy bien! t = d / v = 30 m ÷ 2 m/s = 15 s.",
     "Pista: despeja el tiempo de v = d / t, es decir, t = d / v."),
    ("En la Plaza de Laredo, un perro duerme bajo una banca durante 10 minutos sin moverse. ¿Cuál es su rapidez?",
     [("10 m/s", "por los 10 minutos"), ("0 m/s", "no cambia de posición"),
      ("1 m/s", "porque respira"), ("No se puede saber", "falta la distancia")], 1,
     "¡Exacto! Si no cambia de posición, no recorre distancia: su rapidez es 0 m/s.",
     "Fíjate: ¿cuántos metros recorre el perro mientras duerme?"),
])

CHALLENGES = [
    ("matematica", "¿Cuánto es (−4) + 9?", ["−13", "5", "−5", "13"], 1,
     "Con signos distintos se restan: 9 − 4 = 5, y queda positivo."),
    ("historia", "¿Qué cultura preinca construyó Chan Chan, cerca de Laredo?", ["Moche", "Chimú", "Nasca", "Paracas"],
     1, "Chan Chan fue la capital del reino Chimú."),
    ("ciencia", "¿Qué gas absorben las plantas de caña de azúcar durante la fotosíntesis?",
     ["Oxígeno", "Dióxido de carbono", "Nitrógeno", "Hidrógeno"], 1, "Las plantas absorben CO₂ y liberan oxígeno."),
    ("comunicacion", "¿Cuál de estas palabras es esdrújula?", ["canción", "árbol", "brújula", "reloj"], 2,
     "Brú-ju-la lleva el acento en la antepenúltima sílaba."),
    ("matematica", "Si 3x = 21, ¿cuánto vale x?", ["6", "7", "8", "18"], 1, "x = 21 ÷ 3 = 7."),
    ("ciencia", "¿Cuál es la unidad básica de los seres vivos?", ["El átomo", "La célula", "El tejido", "El órgano"],
     1, "Todos los seres vivos están formados por células."),
    ("historia", "¿Dónde se encuentra Caral, la ciudad más antigua de América?",
     ["Cusco", "Supe (Lima)", "Trujillo", "Puno"], 1, "Caral está en el valle de Supe, en Lima."),
]

STUDENTS = [
    # (usuario, dni, nombre, puntos, racha, récord)
    ("joaquin", "70000001", "Joaquín Paredes", 740, 4, 12),
    ("valeria", "70000002", "Valeria Rojas", 980, 9, 15),
    ("diego", "70000003", "Diego Castillo", 865, 6, 10),
    ("camila", "70000004", "Camila Vásquez", 790, 3, 8),
    ("mateo", "70000005", "Mateo Ruiz", 610, 2, 7),
    ("lucia", "70000006", "Lucía Cárdenas", 540, 1, 5),
]

# Progreso inicial de Joaquín: título de ruta -> lista de intentos por actividad completada
JOAQUIN_PROGRESS = {
    "Números enteros": [1, 1, 1, 2],
    "Rapidez y movimiento": [1, 2, 3],
    "La tildación": [1],
    "Ecuaciones de primer grado": [1, 1, 2, 1],
    "El cuento y la comprensión lectora": [1, 1, 1, 2],
    "La célula": [1, 1],
    "Primeros pobladores y Caral": [1, 2],
}


def seed(db: Session) -> None:
    if db.scalar(select(models.Course)):
        return
    today = date.today()
    courses = {}
    for slug, name, color, icon in COURSES:
        c = models.Course(slug=slug, name=name, color=color, icon=icon)
        db.add(c)
        courses[slug] = c
    db.flush()

    routes = {}
    for slug, title, desc, minutes, bonus, acts in ROUTES:
        r = models.LearningRoute(course_id=courses[slug].id, title=title, description=desc, minutes=minutes,
                                 bonus_points=bonus)
        db.add(r)
        db.flush()
        routes[title] = r
        for i, (atitle, q, opts, ans, hint, expl) in enumerate(acts, start=1):
            db.add(models.Activity(route_id=r.id, order=i, title=atitle, question=q, options=opts, answer=ans,
                                   hint=hint, explanation=expl))

    slug, title, questions = ASSESSMENT
    a = models.Assessment(course_id=courses[slug].id, title=title)
    db.add(a)
    db.flush()
    for i, (situation, opts, ans, ok, ko) in enumerate(questions, start=1):
        db.add(models.AssessmentQuestion(assessment_id=a.id, order=i, situation=situation,
                                         options=[{"texto": t, "razon": r} for t, r in opts], answer=ans,
                                         feedback_ok=ok, feedback_ko=ko))

    for slug, q, opts, ans, expl in CHALLENGES:
        db.add(models.DailyChallenge(course_id=courses[slug].id, question=q, options=opts, answer=ans,
                                     explanation=expl))

    users = {}
    for username, dni, name, points, streak, best in STUDENTS:
        u = models.User(username=username, dni=dni, full_name=name, password_hash=hash_password(DEMO_PASSWORD),
                        grade=GRADE, section="B", points=points, streak=streak, best_streak=best,
                        last_login=today - timedelta(days=1))
        db.add(u)
        users[username] = u
    db.flush()

    joaquin = users["joaquin"]
    # Días estudiados: racha actual (ayer y 3 días antes) + algunos días previos del mes
    for d in [1, 2, 3, 4, 6, 7, 9, 11, 12, 13, 15, 18, 19, 20]:
        db.add(models.LoginDay(user_id=joaquin.id, day=today - timedelta(days=d)))

    db.flush()
    offset = 0
    for title, entries in JOAQUIN_PROGRESS.items():
        for act, attempts in zip(routes[title].activities, entries):
            offset += 1
            db.add(models.ActivityProgress(
                user_id=joaquin.id, activity_id=act.id, attempts=attempts, correct_first_try=attempts == 1,
                completed=True, completed_at=datetime.combine(today - timedelta(days=offset % 9), time(17, 0)),
            ))

    # Tiempo de estudio de la semana: rutas 4.5 h, tutor 2.2 h, autoevaluación 1.8 h
    monday = today - timedelta(days=today.weekday())
    week_days = [monday + timedelta(days=i) for i in range((today - monday).days + 1)]
    for kind, minutes in (("ruta", 270), ("tutor", 132), ("autoevaluacion", 108)):
        per_day = minutes / len(week_days)
        for d in week_days:
            db.add(models.StudyLog(user_id=joaquin.id, kind=kind, minutes=per_day, day=d))
    db.commit()

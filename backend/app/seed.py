"""Datos iniciales: cursos, rutas con actividades, autoevaluación, retos y alumnos de 5to B."""
from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
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
    ("matematica", "Ecuaciones cuadráticas",
     "Aprende a resolver ecuaciones de segundo grado por factorización y fórmula general.", 45, 50, [
         ("Identifica a, b y c", "En la ecuación 2x² − 3x + 5 = 0, ¿cuáles son los valores de a, b y c?",
          ["a = 2, b = 3, c = 5", "a = 2, b = −3, c = 5", "a = −3, b = 2, c = 5", "a = 5, b = −3, c = 2"], 1,
          "Fíjate en el signo que acompaña a cada término.",
          "a es el coeficiente de x², b el de x (con su signo) y c el término independiente."),
         ("Factorización", "¿Cuál es la factorización de x² − 5x + 6?",
          ["(x − 2)(x − 3)", "(x + 2)(x + 3)", "(x − 1)(x − 6)", "(x + 1)(x − 6)"], 0,
          "Busca dos números que multiplicados den 6 y sumados den −5.",
          "−2 y −3 multiplicados dan 6 y sumados dan −5."),
         ("Raíces", "¿Cuáles son las soluciones de x² − 9 = 0?",
          ["x = 9", "x = 3", "x = 3 y x = −3", "No tiene solución"], 2,
          "Despeja x² y recuerda que un número positivo tiene dos raíces cuadradas.",
          "x² = 9, entonces x = 3 o x = −3."),
         ("Discriminante", "Si el discriminante b² − 4ac es negativo, la ecuación…",
          ["tiene dos soluciones reales", "tiene una solución real", "no tiene soluciones reales", "tiene infinitas soluciones"], 2,
          "El discriminante está dentro de una raíz cuadrada en la fórmula general.",
          "No existe la raíz cuadrada real de un número negativo, por eso no hay soluciones reales."),
         ("Problema aplicado", "Un terreno rectangular en Laredo tiene largo x + 2 y ancho x. Si su área es 48 m², ¿cuánto mide el ancho?",
          ["4 m", "6 m", "8 m", "12 m"], 1,
          "Plantea x(x + 2) = 48 y pasa todo a un solo lado.",
          "x² + 2x − 48 = 0 → (x + 8)(x − 6) = 0 → x = 6 (una medida no puede ser negativa)."),
     ]),
    ("ciencia", "Movimiento rectilíneo (MRUV)",
     "Analiza el movimiento con aceleración constante usando ejemplos de tu ciudad.", 50, 60, [
         ("Concepto de aceleración", "La aceleración mide…",
          ["la distancia recorrida", "el cambio de velocidad en el tiempo", "el tiempo total del viaje", "la masa del móvil"], 1,
          "Piensa en qué pasa cuando un mototaxi acelera.",
          "La aceleración es el cambio de velocidad por unidad de tiempo (m/s²)."),
         ("Velocidad final", "Un ciclista parte del reposo con a = 1 m/s². ¿Qué velocidad tiene a los 5 s?",
          ["1 m/s", "5 m/s", "6 m/s", "25 m/s"], 1,
          "Usa Vf = Vo + a·t con Vo = 0.", "Vf = 0 + 1·5 = 5 m/s."),
         ("Unidades", "¿Cuál es la unidad de la aceleración en el SI?",
          ["m/s", "m·s", "m/s²", "km/h"], 2,
          "La aceleración es velocidad dividida entre tiempo.", "(m/s)/s = m/s²."),
         ("Distancia recorrida", "Un auto parte del reposo con a = 2 m/s². ¿Qué distancia recorre en 4 s?",
          ["8 m", "16 m", "32 m", "4 m"], 1,
          "Usa d = Vo·t + ½·a·t².", "d = 0 + ½·2·4² = 16 m."),
         ("Frenado", "Un bus va a 20 m/s y frena con a = −4 m/s². ¿En cuánto tiempo se detiene?",
          ["4 s", "5 s", "16 s", "80 s"], 1,
          "Al detenerse la velocidad final es 0.", "0 = 20 − 4·t → t = 5 s."),
         ("Gráficas", "En una gráfica velocidad-tiempo del MRUV, la pendiente representa…",
          ["la distancia", "la aceleración", "la masa", "el tiempo"], 1,
          "Pendiente = cambio en y / cambio en x.", "Δv/Δt es precisamente la aceleración."),
     ]),
    ("historia", "Perú en la Guerra del Pacífico",
     "Comprende las causas, batallas y consecuencias de la guerra de 1879-1883.", 40, 50, [
         ("Causa económica", "¿Qué recurso natural fue clave en el origen de la Guerra del Pacífico?",
          ["El oro", "El salitre", "El petróleo", "La plata"], 1,
          "Era un fertilizante muy cotizado en Europa.", "El salitre de Tarapacá y Antofagasta era muy valioso."),
         ("Tratado de 1873", "El tratado secreto de 1873 fue una alianza defensiva entre…",
          ["Perú y Chile", "Perú y Bolivia", "Chile y Bolivia", "Perú y Ecuador"], 1,
          "Chile declaró la guerra a dos países.", "Perú y Bolivia firmaron una alianza defensiva en 1873."),
         ("Combate de Angamos", "¿Qué héroe peruano murió en el combate de Angamos (1879)?",
          ["Francisco Bolognesi", "Miguel Grau", "Andrés A. Cáceres", "Alfonso Ugarte"], 1,
          "Comandaba el monitor Huáscar.", "Miguel Grau murió al mando del Huáscar."),
         ("Batalla de Arica", "¿Quién dijo 'Tengo deberes sagrados que cumplir y los cumpliré hasta quemar el último cartucho'?",
          ["Miguel Grau", "Francisco Bolognesi", "Ramón Castilla", "Nicolás de Piérola"], 1,
          "Defendió el morro de Arica.", "Francisco Bolognesi, en la defensa de Arica (1880)."),
         ("Consecuencias", "¿Qué tratado puso fin a la guerra entre Perú y Chile en 1883?",
          ["Tratado de Ancón", "Tratado de Lima", "Tratado de Versalles", "Tratado de Tordesillas"], 0,
          "Lleva el nombre de un balneario de Lima.", "El Tratado de Ancón (1883) terminó la guerra."),
     ]),
    ("comunicacion", "Texto argumentativo",
     "Aprende a plantear una tesis y defenderla con argumentos sólidos.", 35, 40, [
         ("La tesis", "En un texto argumentativo, la tesis es…",
          ["un dato estadístico", "la postura principal del autor", "la conclusión del lector", "un ejemplo"], 1,
          "Es lo que el autor quiere demostrar.", "La tesis es la opinión o postura que el autor defiende."),
         ("Tipos de argumento", "'Según la OMS, dormir 8 horas mejora el rendimiento' es un argumento de…",
          ["autoridad", "ejemplificación", "analogía", "experiencia personal"], 0,
          "Se apoya en una institución reconocida.", "Citar a un experto o institución es un argumento de autoridad."),
         ("Conectores", "¿Qué conector sirve para introducir una idea opuesta?",
          ["además", "por lo tanto", "sin embargo", "por ejemplo"], 2,
          "Busca el conector de contraste.", "'Sin embargo' introduce una idea contraria."),
         ("Estructura", "¿Cuál es el orden habitual de un texto argumentativo?",
          ["Conclusión, tesis, argumentos", "Tesis, argumentos, conclusión", "Argumentos, conclusión, tesis", "Ejemplos, tesis, título"], 1,
          "Primero se plantea la postura.", "Introducción con tesis, cuerpo con argumentos y conclusión."),
         ("Contraargumento", "¿Para qué sirve incluir un contraargumento?",
          ["Para cambiar de tesis", "Para responder a posibles objeciones y fortalecer la postura", "Para alargar el texto", "Para confundir al lector"], 1,
          "Piensa en cómo anticiparte a quien no está de acuerdo.", "Refutar objeciones fortalece tu postura."),
     ]),
    ("matematica", "Funciones lineales",
     "Interpreta pendientes e interceptos en situaciones reales.", 30, 40, [
         ("Pendiente", "En f(x) = 3x + 2, la pendiente es…", ["2", "3", "5", "x"], 1,
          "Es el número que multiplica a x.", "En f(x) = mx + b, m es la pendiente: 3."),
         ("Intercepto", "En f(x) = 3x + 2, ¿dónde corta al eje y?", ["(0, 2)", "(2, 0)", "(0, 3)", "(3, 0)"], 0,
          "Evalúa f(0).", "f(0) = 2, entonces corta en (0, 2)."),
         ("Evaluación", "Si f(x) = 2x − 1, ¿cuánto es f(4)?", ["6", "7", "8", "9"], 1,
          "Reemplaza x por 4.", "2·4 − 1 = 7."),
         ("Aplicación", "Un taxi cobra S/ 4 de base más S/ 1.5 por km. ¿Cuánto cuesta un viaje de 6 km?",
          ["S/ 9", "S/ 13", "S/ 10", "S/ 24"], 1, "Costo = 4 + 1.5·km.", "4 + 1.5·6 = 13 soles."),
     ]),
    ("comunicacion", "Comprensión lectora",
     "Identifica ideas principales, inferencias y propósito del autor.", 30, 40, [
         ("Idea principal", "La idea principal de un párrafo es…",
          ["el detalle más curioso", "lo que resume el sentido global", "la primera palabra", "un ejemplo"], 1,
          "Pregúntate: ¿de qué trata todo el párrafo?", "Es la idea que resume y engloba a las demás."),
         ("Inferencia", "Inferir significa…",
          ["copiar textualmente", "deducir información no explícita", "resumir el título", "buscar sinónimos"], 1,
          "Es leer 'entre líneas'.", "Inferir es deducir lo que el texto sugiere sin decirlo."),
         ("Propósito", "Un afiche que invita a vacunarse tiene un propósito…",
          ["narrativo", "persuasivo", "descriptivo", "poético"], 1,
          "Busca convencer al lector.", "Busca convencer: su propósito es persuasivo."),
         ("Tipo de texto", "Una noticia sobre la cosecha de caña en Laredo es un texto…",
          ["informativo", "lírico", "dramático", "instructivo"], 0,
          "Su objetivo es dar a conocer hechos.", "Las noticias son textos informativos."),
     ]),
    ("ciencia", "Leyes de Newton",
     "Relaciona fuerzas, masa y aceleración en situaciones cotidianas.", 35, 40, [
         ("Inercia", "La primera ley de Newton también se llama ley de…",
          ["acción y reacción", "inercia", "gravitación", "conservación"], 1,
          "Los cuerpos tienden a mantener su estado.", "Es la ley de la inercia."),
         ("F = m·a", "¿Qué fuerza se necesita para acelerar 2 m/s² una masa de 10 kg?",
          ["5 N", "12 N", "20 N", "8 N"], 2, "Usa F = m·a.", "F = 10·2 = 20 N."),
         ("Acción y reacción", "Al remar en un bote, el bote avanza porque…",
          ["el agua empuja el remo hacia adelante", "el remo empuja el agua hacia atrás y el agua empuja al bote hacia adelante",
           "el viento lo empuja", "la gravedad lo mueve"], 1,
          "Piensa en pares de fuerzas.", "Tercera ley: a toda acción corresponde una reacción igual y opuesta."),
         ("Peso", "¿Cuál es el peso aproximado de una persona de 50 kg (g = 10 m/s²)?",
          ["50 N", "500 N", "5 N", "5000 N"], 1, "Peso = m·g.", "50·10 = 500 N."),
     ]),
    ("historia", "Independencia del Perú",
     "Conoce a los precursores, próceres y el proceso de independencia.", 35, 40, [
         ("Proclamación", "¿En qué año se proclamó la independencia del Perú?", ["1810", "1821", "1824", "1879"], 1,
          "Fue proclamada por San Martín.", "San Martín la proclamó el 28 de julio de 1821."),
         ("Batalla de Ayacucho", "La batalla de Ayacucho (1824) consolidó la independencia. ¿Quién dirigió al ejército patriota?",
          ["José de San Martín", "Antonio José de Sucre", "Túpac Amaru II", "Ramón Castilla"], 1,
          "Fue un general venezolano, lugarteniente de Bolívar.", "Antonio José de Sucre dirigió a los patriotas."),
         ("Precursores", "¿Quién encabezó la gran rebelión de 1780?",
          ["Túpac Amaru II", "Mateo Pumacahua", "José Olaya", "Micaela Bastidas"], 0,
          "Fue un curaca de Tinta.", "José Gabriel Condorcanqui, Túpac Amaru II."),
         ("Trujillo", "Trujillo proclamó su independencia en 1820 gracias a…",
          ["el marqués de Torre Tagle", "Simón Bolívar", "Miguel Grau", "Ramón Castilla"], 0,
          "Era el intendente de Trujillo.", "José Bernardo de Tagle proclamó la independencia de Trujillo el 29 de diciembre de 1820."),
     ]),
]

ASSESSMENT = ("ciencia", "Desafío: Cinemática y aceleración", [
    ("Un mototaxi parte del reposo en la Plaza de Armas de Laredo con una aceleración constante de 2 m/s² en línea recta. "
     "¿Cuál será su velocidad después de 6 segundos?",
     [("8 m/s", "sumando 2 + 6"), ("12 m/s", "aplicando Vf = Vo + a·t, con Vo = 0"),
      ("3 m/s", "dividiendo 6 entre 2"), ("36 m/s", "elevando 6 al cuadrado")], 1,
     "¡Bien hecho! Aplicaste Vf = Vo + a·t: 0 + 2·6 = 12 m/s.",
     "Casi. Recuerda que la velocidad crece 2 m/s cada segundo. Usa Vf = Vo + a·t con Vo = 0."),
    ("Una combi que va a 15 m/s frena uniformemente y se detiene en 5 s. ¿Cuál fue su aceleración?",
     [("3 m/s²", "dividiendo 15 entre 5"), ("−3 m/s²", "usando a = (Vf − Vo)/t"),
      ("75 m/s²", "multiplicando 15 por 5"), ("−75 m/s²", "multiplicando con signo")], 1,
     "¡Excelente! Al frenar, la aceleración es negativa: (0 − 15)/5 = −3 m/s².",
     "Revisa el signo: si la velocidad disminuye, la aceleración es negativa. a = (Vf − Vo)/t."),
    ("Un ciclista recorre la avenida principal de Laredo a velocidad constante de 5 m/s. ¿Cuánto recorre en 1 minuto?",
     [("5 m", "la velocidad por 1"), ("300 m", "5 m/s · 60 s"), ("12 m", "60 entre 5"), ("65 m", "sumando 5 + 60")], 1,
     "¡Correcto! Convertiste 1 minuto a 60 s: d = v·t = 5·60 = 300 m.",
     "Ojo con las unidades: 1 minuto son 60 segundos. Luego usa d = v·t."),
    ("Un carro parte del reposo con aceleración de 3 m/s². ¿Qué distancia recorre en 4 s?",
     [("12 m", "3 · 4"), ("24 m", "½ · 3 · 4²"), ("48 m", "3 · 4²"), ("7 m", "3 + 4")], 1,
     "¡Muy bien! d = ½·a·t² = ½·3·16 = 24 m.",
     "Pista: en el MRUV la distancia depende del tiempo al cuadrado: d = Vo·t + ½·a·t²."),
    ("En una gráfica velocidad-tiempo, una línea recta horizontal indica que el móvil…",
     [("está detenido siempre", "porque la línea no sube"), ("tiene velocidad constante", "la velocidad no cambia"),
      ("acelera", "porque avanza en el tiempo"), ("retrocede", "porque es horizontal")], 1,
     "¡Exacto! Si la velocidad no cambia, la aceleración es cero: es un MRU.",
     "Fíjate en el eje vertical: es la velocidad. Si la línea es horizontal, ¿la velocidad cambia?"),
])

CHALLENGES = [
    ("matematica", "¿Cuánto es el 15% de 200?", ["15", "30", "20", "35"], 1, "200 × 0.15 = 30."),
    ("historia", "¿En qué año llegaron los españoles a Cajamarca y capturaron a Atahualpa?",
     ["1492", "1532", "1572", "1821"], 1, "Pizarro capturó a Atahualpa en Cajamarca en 1532."),
    ("ciencia", "¿Qué gas absorben las plantas de caña de azúcar durante la fotosíntesis?",
     ["Oxígeno", "Dióxido de carbono", "Nitrógeno", "Hidrógeno"], 1, "Las plantas absorben CO₂ y liberan oxígeno."),
    ("comunicacion", "¿Cuál de estas palabras es esdrújula?", ["canción", "árbol", "brújula", "reloj"], 2,
     "Brú-ju-la lleva el acento en la antepenúltima sílaba."),
    ("matematica", "Si 3x = 21, ¿cuánto vale x?", ["6", "7", "8", "18"], 1, "x = 21 ÷ 3 = 7."),
    ("ciencia", "¿Cuál es la unidad de fuerza en el SI?", ["Joule", "Watt", "Newton", "Pascal"], 2,
     "La fuerza se mide en newtons (N)."),
    ("historia", "¿Qué cultura preinca construyó Chan Chan, cerca de Laredo?", ["Moche", "Chimú", "Nasca", "Paracas"], 1,
     "Chan Chan fue la capital del reino Chimú."),
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

# Progreso inicial de Joaquín: título de ruta -> lista de (completada, intentos)
JOAQUIN_PROGRESS = {
    "Ecuaciones cuadráticas": [1, 1, 1, 2],
    "Movimiento rectilíneo (MRUV)": [1, 2, 3],
    "Texto argumentativo": [1],
    "Funciones lineales": [1, 1, 2, 1],
    "Comprensión lectora": [1, 1, 1, 2],
    "Leyes de Newton": [1, 1],
    "Independencia del Perú": [1, 2],
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
                                         options=[{"text": t, "reason": r} for t, r in opts], answer=ans,
                                         feedback_ok=ok, feedback_ko=ko))

    for slug, q, opts, ans, expl in CHALLENGES:
        db.add(models.DailyChallenge(course_id=courses[slug].id, question=q, options=opts, answer=ans,
                                     explanation=expl))

    users = {}
    for username, dni, name, points, streak, best in STUDENTS:
        u = models.User(username=username, dni=dni, full_name=name, password_hash=hash_password(DEMO_PASSWORD),
                        grade="5to Sec.", section="B", points=points, streak=streak, best_streak=best,
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
    for kind, minutes in (("rutas", 270), ("tutor", 132), ("autoevaluacion", 108)):
        per_day = minutes / len(week_days)
        for d in week_days:
            db.add(models.StudyLog(user_id=joaquin.id, kind=kind, minutes=per_day, day=d))
    db.commit()

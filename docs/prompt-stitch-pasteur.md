# Prompt para Google Stitch: Plataforma de Aprendizaje Autónomo "Pasteur"

Diseña un prototipo web (versión escritorio, que también se vea bien en celular) de una plataforma educativa sencilla llamada **"Pasteur Learn"**, del Colegio Louis Pasteur de Laredo, Perú. La plataforma tiene un tutor con inteligencia artificial y ayuda a los alumnos a estudiar por su cuenta fuera del colegio.

Todo el texto de la interfaz debe estar **en español**. Quiero un diseño **simple, limpio y amigable**, nada corporativo ni recargado. Que parezca una app para estudiantes, no un sistema empresarial.

---

## 1. Público y alcance

- Solo para **alumnos de 5to año de secundaria**.
- Cuatro cursos de estudio (no más):
  1. **Historia**
  2. **Ciencia y Tecnología**
  3. **Matemática**
  4. **Comunicación**

- El alumno de ejemplo se llama **Joaquín Paredes, 5to Secundaria B**.

## 2. Estilo visual

- **Tema oscuro** en toda la página (fondo azul noche casi negro).
- Paleta:
  - Fondo general: `#0F1220`
  - Tarjetas: `#1A1F36` con borde suave `#2A3050`
  - Texto principal: `#F1F3FA`, texto secundario: `#9AA3C0`
  - Azul principal (botones y pestaña activa): `#4F7CFF`
  - Violeta (tutor IA): `#8B7BFF`
  - Verde (progreso, logros): `#34D399`
  - Naranja (racha): `#FB923C`
  - Amarillo (puntos): `#FBBF24`
  - Colores por curso: Historia `#F59E0B`, Ciencia y Tecnología `#22C55E`, Matemática `#4F7CFF`, Comunicación `#EC4899`
- Esquinas redondeadas (16 px), sombras suaves, mucho espacio entre elementos.
- Tipografía redonda y legible (por ejemplo Inter o Nunito). Íconos simples de línea.
- Nada de gráficos complicados: barras de progreso, círculos de porcentaje y tarjetas.

## 3. Estructura general

Barra superior fija con:
- A la izquierda: logo (birrete) + "Pasteur Learn" + etiqueta "Laredo 2026".
- A la derecha: chip de **🔥 Racha** (ej. "5 días"), chip de **⭐ Puntos** (ej. "740 pts"), y avatar con nombre "Joaquín Paredes · 5to Sec. B".

Debajo, menú de pestañas:
**Inicio · Tutor IA · Rutas Adaptativas · Autoevaluación · Mis Métricas**

---

## 4. Pantallas a diseñar

### Pantalla 1: Inicio de sesión (primera pantalla al abrir el link)
Sin iniciar sesión no se ve nada del contenido.
- Pantalla centrada, fondo oscuro, una tarjeta con logo, título **"Bienvenido a Pasteur Learn"** y subtítulo "Solo para estudiantes de 5to de secundaria".
- Campos: **Usuario o DNI** y **Contraseña** (con ojito para mostrarla).
- Botón grande azul **"Ingresar"**.
- Enlace pequeño "¿Olvidaste tu contraseña?".
- Mensaje de ayuda: "Si no tienes cuenta, pídela a tu tutor o docente."
- Ilustración sencilla de un estudiante con un robot amigable (estilo plano, sin detalles).

### Pantalla 2: Inicio / Dashboard (pequeño y claro, al entrar después del login)
De arriba hacia abajo:

1. **Banner de bienvenida** (degradado azul oscuro a violeta):
   "¡Hola, Joaquín! Sigue con tu aprendizaje hoy 👋"
   Texto: "Llevas 5 días seguidos estudiando. ¡No rompas tu racha!"
   Dos botones: **"Hablar con el Tutor IA"** (azul) y **"Continuar mi ruta"** (borde claro).

2. **Fila de 4 tarjetas pequeñas** con barra de progreso:
   - 🔥 **Racha**: "5 días seguidos" · "Tu récord: 12 días"
   - ⭐ **Puntos**: "740 pts" · "+60 pts esta semana"
   - ⏱️ **Estudio de la semana**: "8.5 h" · "Meta: 10 h"
   - ✅ **Temas dominados**: "14 / 18"

3. **Tarjeta de Racha semanal**: siete círculos L M M J V S D; los días cumplidos con fueguito naranja, el de hoy resaltado, los futuros vacíos. Texto: "Entra todos los días para mantener tu racha 🔥".

4. **Tarjeta "Tus cursos"**: 4 mini tarjetas (Historia, Ciencia y Tecnología, Matemática, Comunicación), cada una con su color, ícono y porcentaje de avance (ej. 40%, 55%, 80%, 65%).

5. **Tarjeta "Siguiente paso recomendado por la IA"**: "Cinemática: te faltan 3 actividades" con botón **"Continuar"**.

6. **Tarjeta "Reto del día"**: una pregunta rápida con botón "Resolver (+10 pts)".

7. **Tarjeta "Logros recientes"**: 3 insignias circulares (ej. "Primera ruta completada", "Racha de 5 días", "100 puntos").

8. **Mini ranking del salón** (solo los 3 primeros y la posición de Joaquín, ej. "Vas 4.º de tu salón"), tono amistoso, sin presión.

> El dashboard debe verse pequeño y ordenado: máximo dos filas de tarjetas visibles sin hacer mucho scroll.

### Pantalla 3: Tutor IA Socrático
- Ventana de chat grande. Encabezado con ícono de robot, título **"Tutor IA Socrático"**, etiqueta verde "En línea" y botón "Reiniciar diálogo".
- Aviso azul claro bajo el encabezado: "**Método socrático:** el tutor no te da la respuesta directa; te guía con preguntas y pistas para que la descubras tú."
- Selector arriba para elegir el curso (Historia, Ciencia y Tecnología, Matemática, Comunicación).
- Primer mensaje del tutor (burbuja gris oscuro): "¡Hola, Joaquín! Soy tu tutor de aprendizaje autónomo. Estoy aquí para acompañarte sin hacer el trabajo por ti. ¿Sobre qué tema quieres reflexionar hoy?"
- Ejemplo de mensaje del alumno (burbuja azul): "No entiendo cómo resolver x² − 5x + 6 = 0".
- Respuesta de ejemplo del tutor: "¿Qué métodos conoces para resolver una ecuación cuadrática? Empecemos por identificar los valores de a, b y c."
- Sugerencias rápidas (chips clicables): "¿Cómo resuelvo x² − 5x + 6 = 0?", "¿Qué causó la Guerra del Pacífico?", "Ayúdame a mejorar mi resumen".
- Caja de texto abajo "Escribe tu pregunta o cuéntame qué intentaste…" y botón azul **"Preguntar"**.
- Ganar puntos: aviso discreto "+5 pts por cada sesión con el tutor".

### Pantalla 4: Rutas Adaptativas
- Título: "Mis rutas de aprendizaje · 5to de Secundaria". Subtítulo: "Los módulos se ajustan a tu ritmo".
- Filtros tipo botón: **Todos · Historia · Ciencia y Tecnología · Matemática · Comunicación**.
- Tarjetas de ruta en cuadrícula de 3 columnas, cada una con etiqueta del curso, título, descripción corta, barra de progreso, tiempo estimado, **puntos que se ganan** y un botón:
  - **Matemática**: "Ecuaciones cuadráticas" · 80% completado · 4/5 actividades · +50 pts · botón "Ver actividad".
  - **Ciencia y Tecnología**: "Movimiento rectilíneo (MRUV)" · En progreso 55% · 3/6 actividades · +60 pts · botón azul "Continuar".
  - **Historia**: "Perú en la Guerra del Pacífico" · 0/5 actividades · "Recomendada por la IA" con candadito · +50 pts · botón "Iniciar".
  - **Comunicación**: "Texto argumentativo" · 20% · 1/5 actividades · +40 pts · botón "Continuar".
- Cada tarjeta muestra una insignia pequeña "Nivel: básico / intermedio / avanzado" que cambia según el desempeño.
- Al completar una actividad se muestra un aviso emergente: "¡Bien hecho! +10 pts 🎉".

### Pantalla 5: Autoevaluación
- Encabezado pequeño "EVALUACIÓN AUTÓNOMA FORMATIVA", título "Desafío: Cinemática y aceleración", etiqueta "Pregunta 1 de 5". Nota: "Esta prueba no es una nota; sirve para ver cómo razonas."
- Barra de avance de la prueba arriba.
- Recuadro con la situación: "Un mototaxi parte del reposo en la Plaza de Armas de Laredo con una aceleración constante de 2 m/s² en línea recta. ¿Cuál será su velocidad después de 6 segundos?"
- 4 opciones tipo tarjeta con botón circular:
  - A) 8 m/s (sumando 2 + 6)
  - B) 12 m/s (aplicando Vf = Vo + a·t, con Vo = 0)
  - C) 3 m/s (dividiendo 6 entre 2)
  - D) 36 m/s (elevando 6 al cuadrado)
- Debajo, la pregunta de reflexión: "¿Qué tan seguro estás de tu respuesta?" con 3 botones: **Nada seguro · Más o menos · Muy seguro**.
- Botón **"Comprobar"**; luego mostrar retroalimentación amable (verde si acierta, naranja si no) y "+10 pts".

### Pantalla 6: Mis Métricas de Aprendizaje
- Título "Mi progreso 2026" y etiqueta verde "Vas muy bien".
- Columna izquierda, **"Avance por curso"**: cuatro barras (Matemática 82%, Ciencia y Tecnología 76%, Historia 64%, Comunicación 71%) con el color de cada curso.
- Columna derecha, **"¿Cómo uso mi tiempo esta semana?"**: lista con punto de color: Rutas adaptativas 4.5 h · Tutor IA 2.2 h · Autoevaluación 1.8 h.
- Fila de 3 tarjetas: **Racha actual** (5 días), **Puntos totales** (740), **Nivel de autonomía** (Nivel 3 de 4).
- Cuadro azul claro "Comentario de la IA": "Joaquín muestra mucha constancia y no se rinde rápido. Logró 85% de aciertos tras la segunda pista del tutor."
- Pequeño calendario del mes con los días estudiados marcados con 🔥.

---

## 5. Detalles de la racha y los puntos

**Racha 🔥**
- Se suma un día cada vez que el alumno ingresa a la plataforma en ese día.
- Si falta un día, la racha vuelve a 0 (mostrar mensaje animador, no castigo).
- Se muestra siempre en la barra superior y en el Inicio.

**Puntos ⭐**
- Se ganan al avanzar en las rutas adaptativas (+10 por actividad, bonus al terminar la ruta).
- Pequeños extras por la autoevaluación y por conversar con el tutor.
- El total se ve siempre en la barra superior.

## 6. Reglas de diseño importantes

- Sencillo y limpio, sin exceso de elementos ni lenguaje técnico.
- Textos cortos, tono cercano para un adolescente (sin ser infantil).
- Botones grandes y fáciles de tocar.
- Todo en modo oscuro, buen contraste para leer.
- Usar exactamente los 4 cursos indicados, y mantener sus colores en todas las pantallas.

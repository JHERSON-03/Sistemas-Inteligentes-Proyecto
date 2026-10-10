-- Renombra las columnas al patrón <entidad>_<campo> (ej. cursos.curso_nombre).
-- Las claves foráneas, índices y restricciones siguen funcionando: Postgres los actualiza solo.
BEGIN;

-- usuarios
ALTER TABLE public.usuarios RENAME COLUMN id TO usuario_id;
ALTER TABLE public.usuarios RENAME COLUMN usuario TO usuario_usuario;
ALTER TABLE public.usuarios RENAME COLUMN dni TO usuario_dni;
ALTER TABLE public.usuarios RENAME COLUMN clave_hash TO usuario_clave_hash;
ALTER TABLE public.usuarios RENAME COLUMN nombre_completo TO usuario_nombre_completo;
ALTER TABLE public.usuarios RENAME COLUMN grado TO usuario_grado;
ALTER TABLE public.usuarios RENAME COLUMN seccion TO usuario_seccion;
ALTER TABLE public.usuarios RENAME COLUMN puntos TO usuario_puntos;
ALTER TABLE public.usuarios RENAME COLUMN racha TO usuario_racha;
ALTER TABLE public.usuarios RENAME COLUMN mejor_racha TO usuario_mejor_racha;
ALTER TABLE public.usuarios RENAME COLUMN ultimo_ingreso TO usuario_ultimo_ingreso;
ALTER TABLE public.usuarios RENAME COLUMN creado_en TO usuario_creado_en;

-- dias_ingreso
ALTER TABLE public.dias_ingreso RENAME COLUMN id TO ingreso_id;
ALTER TABLE public.dias_ingreso RENAME COLUMN usuario_id TO ingreso_usuario_id;
ALTER TABLE public.dias_ingreso RENAME COLUMN dia TO ingreso_dia;

-- cursos
ALTER TABLE public.cursos RENAME COLUMN id TO curso_id;
ALTER TABLE public.cursos RENAME COLUMN codigo TO curso_codigo;
ALTER TABLE public.cursos RENAME COLUMN nombre TO curso_nombre;
ALTER TABLE public.cursos RENAME COLUMN color TO curso_color;
ALTER TABLE public.cursos RENAME COLUMN icono TO curso_icono;

-- rutas
ALTER TABLE public.rutas RENAME COLUMN id TO ruta_id;
ALTER TABLE public.rutas RENAME COLUMN curso_id TO ruta_curso_id;
ALTER TABLE public.rutas RENAME COLUMN titulo TO ruta_titulo;
ALTER TABLE public.rutas RENAME COLUMN descripcion TO ruta_descripcion;
ALTER TABLE public.rutas RENAME COLUMN minutos TO ruta_minutos;
ALTER TABLE public.rutas RENAME COLUMN puntos_bonus TO ruta_puntos_bonus;

-- actividades
ALTER TABLE public.actividades RENAME COLUMN id TO actividad_id;
ALTER TABLE public.actividades RENAME COLUMN ruta_id TO actividad_ruta_id;
ALTER TABLE public.actividades RENAME COLUMN orden TO actividad_orden;
ALTER TABLE public.actividades RENAME COLUMN titulo TO actividad_titulo;
ALTER TABLE public.actividades RENAME COLUMN pregunta TO actividad_pregunta;
ALTER TABLE public.actividades RENAME COLUMN opciones TO actividad_opciones;
ALTER TABLE public.actividades RENAME COLUMN respuesta TO actividad_respuesta;
ALTER TABLE public.actividades RENAME COLUMN pista TO actividad_pista;
ALTER TABLE public.actividades RENAME COLUMN explicacion TO actividad_explicacion;

-- progreso_actividad
ALTER TABLE public.progreso_actividad RENAME COLUMN id TO progreso_id;
ALTER TABLE public.progreso_actividad RENAME COLUMN usuario_id TO progreso_usuario_id;
ALTER TABLE public.progreso_actividad RENAME COLUMN actividad_id TO progreso_actividad_id;
ALTER TABLE public.progreso_actividad RENAME COLUMN intentos TO progreso_intentos;
ALTER TABLE public.progreso_actividad RENAME COLUMN acerto_primer_intento TO progreso_acerto_primer_intento;
ALTER TABLE public.progreso_actividad RENAME COLUMN completada TO progreso_completada;
ALTER TABLE public.progreso_actividad RENAME COLUMN completada_en TO progreso_completada_en;

-- evaluaciones
ALTER TABLE public.evaluaciones RENAME COLUMN id TO evaluacion_id;
ALTER TABLE public.evaluaciones RENAME COLUMN curso_id TO evaluacion_curso_id;
ALTER TABLE public.evaluaciones RENAME COLUMN titulo TO evaluacion_titulo;

-- preguntas_evaluacion
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN id TO pregunta_id;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN evaluacion_id TO pregunta_evaluacion_id;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN orden TO pregunta_orden;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN situacion TO pregunta_situacion;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN opciones TO pregunta_opciones;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN respuesta TO pregunta_respuesta;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN comentario_ok TO pregunta_comentario_ok;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN comentario_mal TO pregunta_comentario_mal;

-- respuestas_evaluacion
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN id TO respuesta_eval_id;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN usuario_id TO respuesta_eval_usuario_id;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN pregunta_id TO respuesta_eval_pregunta_id;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN seleccion TO respuesta_eval_seleccion;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN confianza TO respuesta_eval_confianza;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN correcta TO respuesta_eval_correcta;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN creado_en TO respuesta_eval_creado_en;

-- retos_diarios
ALTER TABLE public.retos_diarios RENAME COLUMN id TO reto_id;
ALTER TABLE public.retos_diarios RENAME COLUMN curso_id TO reto_curso_id;
ALTER TABLE public.retos_diarios RENAME COLUMN pregunta TO reto_pregunta;
ALTER TABLE public.retos_diarios RENAME COLUMN opciones TO reto_opciones;
ALTER TABLE public.retos_diarios RENAME COLUMN respuesta TO reto_respuesta;
ALTER TABLE public.retos_diarios RENAME COLUMN explicacion TO reto_explicacion;

-- respuestas_reto
ALTER TABLE public.respuestas_reto RENAME COLUMN id TO respuesta_reto_id;
ALTER TABLE public.respuestas_reto RENAME COLUMN usuario_id TO respuesta_reto_usuario_id;
ALTER TABLE public.respuestas_reto RENAME COLUMN reto_id TO respuesta_reto_reto_id;
ALTER TABLE public.respuestas_reto RENAME COLUMN dia TO respuesta_reto_dia;
ALTER TABLE public.respuestas_reto RENAME COLUMN correcta TO respuesta_reto_correcta;

-- registro_estudio
ALTER TABLE public.registro_estudio RENAME COLUMN id TO estudio_id;
ALTER TABLE public.registro_estudio RENAME COLUMN usuario_id TO estudio_usuario_id;
ALTER TABLE public.registro_estudio RENAME COLUMN tipo TO estudio_tipo;
ALTER TABLE public.registro_estudio RENAME COLUMN minutos TO estudio_minutos;
ALTER TABLE public.registro_estudio RENAME COLUMN dia TO estudio_dia;

-- mensajes_tutor
ALTER TABLE public.mensajes_tutor RENAME COLUMN id TO mensaje_id;
ALTER TABLE public.mensajes_tutor RENAME COLUMN usuario_id TO mensaje_usuario_id;
ALTER TABLE public.mensajes_tutor RENAME COLUMN sesion_id TO mensaje_sesion_id;
ALTER TABLE public.mensajes_tutor RENAME COLUMN curso TO mensaje_curso;
ALTER TABLE public.mensajes_tutor RENAME COLUMN emisor TO mensaje_emisor;
ALTER TABLE public.mensajes_tutor RENAME COLUMN contenido TO mensaje_contenido;
ALTER TABLE public.mensajes_tutor RENAME COLUMN creado_en TO mensaje_creado_en;
ALTER TABLE public.mensajes_tutor RENAME COLUMN archivado TO mensaje_archivado;

COMMIT;

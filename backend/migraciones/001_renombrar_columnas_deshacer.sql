-- Deshace 001_renombrar_columnas.sql (vuelve a los nombres anteriores).
BEGIN;

-- usuarios
ALTER TABLE public.usuarios RENAME COLUMN usuario_id TO id;
ALTER TABLE public.usuarios RENAME COLUMN usuario_usuario TO usuario;
ALTER TABLE public.usuarios RENAME COLUMN usuario_dni TO dni;
ALTER TABLE public.usuarios RENAME COLUMN usuario_clave_hash TO clave_hash;
ALTER TABLE public.usuarios RENAME COLUMN usuario_nombre_completo TO nombre_completo;
ALTER TABLE public.usuarios RENAME COLUMN usuario_grado TO grado;
ALTER TABLE public.usuarios RENAME COLUMN usuario_seccion TO seccion;
ALTER TABLE public.usuarios RENAME COLUMN usuario_puntos TO puntos;
ALTER TABLE public.usuarios RENAME COLUMN usuario_racha TO racha;
ALTER TABLE public.usuarios RENAME COLUMN usuario_mejor_racha TO mejor_racha;
ALTER TABLE public.usuarios RENAME COLUMN usuario_ultimo_ingreso TO ultimo_ingreso;
ALTER TABLE public.usuarios RENAME COLUMN usuario_creado_en TO creado_en;

-- dias_ingreso
ALTER TABLE public.dias_ingreso RENAME COLUMN ingreso_id TO id;
ALTER TABLE public.dias_ingreso RENAME COLUMN ingreso_usuario_id TO usuario_id;
ALTER TABLE public.dias_ingreso RENAME COLUMN ingreso_dia TO dia;

-- cursos
ALTER TABLE public.cursos RENAME COLUMN curso_id TO id;
ALTER TABLE public.cursos RENAME COLUMN curso_codigo TO codigo;
ALTER TABLE public.cursos RENAME COLUMN curso_nombre TO nombre;
ALTER TABLE public.cursos RENAME COLUMN curso_color TO color;
ALTER TABLE public.cursos RENAME COLUMN curso_icono TO icono;

-- rutas
ALTER TABLE public.rutas RENAME COLUMN ruta_id TO id;
ALTER TABLE public.rutas RENAME COLUMN ruta_curso_id TO curso_id;
ALTER TABLE public.rutas RENAME COLUMN ruta_titulo TO titulo;
ALTER TABLE public.rutas RENAME COLUMN ruta_descripcion TO descripcion;
ALTER TABLE public.rutas RENAME COLUMN ruta_minutos TO minutos;
ALTER TABLE public.rutas RENAME COLUMN ruta_puntos_bonus TO puntos_bonus;

-- actividades
ALTER TABLE public.actividades RENAME COLUMN actividad_id TO id;
ALTER TABLE public.actividades RENAME COLUMN actividad_ruta_id TO ruta_id;
ALTER TABLE public.actividades RENAME COLUMN actividad_orden TO orden;
ALTER TABLE public.actividades RENAME COLUMN actividad_titulo TO titulo;
ALTER TABLE public.actividades RENAME COLUMN actividad_pregunta TO pregunta;
ALTER TABLE public.actividades RENAME COLUMN actividad_opciones TO opciones;
ALTER TABLE public.actividades RENAME COLUMN actividad_respuesta TO respuesta;
ALTER TABLE public.actividades RENAME COLUMN actividad_pista TO pista;
ALTER TABLE public.actividades RENAME COLUMN actividad_explicacion TO explicacion;

-- progreso_actividad
ALTER TABLE public.progreso_actividad RENAME COLUMN progreso_id TO id;
ALTER TABLE public.progreso_actividad RENAME COLUMN progreso_usuario_id TO usuario_id;
ALTER TABLE public.progreso_actividad RENAME COLUMN progreso_actividad_id TO actividad_id;
ALTER TABLE public.progreso_actividad RENAME COLUMN progreso_intentos TO intentos;
ALTER TABLE public.progreso_actividad RENAME COLUMN progreso_acerto_primer_intento TO acerto_primer_intento;
ALTER TABLE public.progreso_actividad RENAME COLUMN progreso_completada TO completada;
ALTER TABLE public.progreso_actividad RENAME COLUMN progreso_completada_en TO completada_en;

-- evaluaciones
ALTER TABLE public.evaluaciones RENAME COLUMN evaluacion_id TO id;
ALTER TABLE public.evaluaciones RENAME COLUMN evaluacion_curso_id TO curso_id;
ALTER TABLE public.evaluaciones RENAME COLUMN evaluacion_titulo TO titulo;

-- preguntas_evaluacion
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN pregunta_id TO id;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN pregunta_evaluacion_id TO evaluacion_id;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN pregunta_orden TO orden;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN pregunta_situacion TO situacion;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN pregunta_opciones TO opciones;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN pregunta_respuesta TO respuesta;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN pregunta_comentario_ok TO comentario_ok;
ALTER TABLE public.preguntas_evaluacion RENAME COLUMN pregunta_comentario_mal TO comentario_mal;

-- respuestas_evaluacion
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN respuesta_eval_id TO id;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN respuesta_eval_usuario_id TO usuario_id;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN respuesta_eval_pregunta_id TO pregunta_id;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN respuesta_eval_seleccion TO seleccion;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN respuesta_eval_confianza TO confianza;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN respuesta_eval_correcta TO correcta;
ALTER TABLE public.respuestas_evaluacion RENAME COLUMN respuesta_eval_creado_en TO creado_en;

-- retos_diarios
ALTER TABLE public.retos_diarios RENAME COLUMN reto_id TO id;
ALTER TABLE public.retos_diarios RENAME COLUMN reto_curso_id TO curso_id;
ALTER TABLE public.retos_diarios RENAME COLUMN reto_pregunta TO pregunta;
ALTER TABLE public.retos_diarios RENAME COLUMN reto_opciones TO opciones;
ALTER TABLE public.retos_diarios RENAME COLUMN reto_respuesta TO respuesta;
ALTER TABLE public.retos_diarios RENAME COLUMN reto_explicacion TO explicacion;

-- respuestas_reto
ALTER TABLE public.respuestas_reto RENAME COLUMN respuesta_reto_id TO id;
ALTER TABLE public.respuestas_reto RENAME COLUMN respuesta_reto_usuario_id TO usuario_id;
ALTER TABLE public.respuestas_reto RENAME COLUMN respuesta_reto_reto_id TO reto_id;
ALTER TABLE public.respuestas_reto RENAME COLUMN respuesta_reto_dia TO dia;
ALTER TABLE public.respuestas_reto RENAME COLUMN respuesta_reto_correcta TO correcta;

-- registro_estudio
ALTER TABLE public.registro_estudio RENAME COLUMN estudio_id TO id;
ALTER TABLE public.registro_estudio RENAME COLUMN estudio_usuario_id TO usuario_id;
ALTER TABLE public.registro_estudio RENAME COLUMN estudio_tipo TO tipo;
ALTER TABLE public.registro_estudio RENAME COLUMN estudio_minutos TO minutos;
ALTER TABLE public.registro_estudio RENAME COLUMN estudio_dia TO dia;

-- mensajes_tutor
ALTER TABLE public.mensajes_tutor RENAME COLUMN mensaje_id TO id;
ALTER TABLE public.mensajes_tutor RENAME COLUMN mensaje_usuario_id TO usuario_id;
ALTER TABLE public.mensajes_tutor RENAME COLUMN mensaje_sesion_id TO sesion_id;
ALTER TABLE public.mensajes_tutor RENAME COLUMN mensaje_curso TO curso;
ALTER TABLE public.mensajes_tutor RENAME COLUMN mensaje_emisor TO emisor;
ALTER TABLE public.mensajes_tutor RENAME COLUMN mensaje_contenido TO contenido;
ALTER TABLE public.mensajes_tutor RENAME COLUMN mensaje_creado_en TO creado_en;
ALTER TABLE public.mensajes_tutor RENAME COLUMN mensaje_archivado TO archivado;

COMMIT;

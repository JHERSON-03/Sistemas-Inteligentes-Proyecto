-- Contadores del límite de peticiones (rate limit) del backend: login, registro y tutor IA.
-- Cada fila es una clave (ej. "tutor_minuto:usuario:7") con el inicio de su ventana y cuántas peticiones lleva.
-- Sigue el patrón <entidad>_<campo> del resto del esquema (ver backend/migraciones/001_renombrar_columnas.sql).
-- Ejecutar una sola vez en el SQL Editor de Supabase.
BEGIN;

CREATE TABLE IF NOT EXISTS public.limites_peticion (
    limite_clave   varchar(150) PRIMARY KEY,
    limite_inicio  timestamp    NOT NULL,
    limite_conteo  integer      NOT NULL CHECK (limite_conteo >= 0)
);

-- Solo el backend (que se conecta como dueño de la tabla) lee y escribe; la API pública de Supabase queda bloqueada.
ALTER TABLE public.limites_peticion ENABLE ROW LEVEL SECURITY;

COMMIT;

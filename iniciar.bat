@echo off
title Pasteur Learn
cd /d "%~dp0"

echo Iniciando el backend (puerto 8000)...
start "Pasteur Learn - BACKEND (no cerrar)" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\python -m uvicorn app.main:app --reload --port 8000"

echo Iniciando el frontend (puerto 5173)...
start "Pasteur Learn - FRONTEND (no cerrar)" cmd /k "cd /d "%~dp0frontend" && npm.cmd run dev"

echo Esperando a que todo cargue...
timeout /t 8 /nobreak >nul
start "" http://localhost:5173

echo.
echo Listo. Usuario: joaquin   Contrasena: pasteur2026
echo Para apagar el proyecto cierra las dos ventanas negras.
timeout /t 10 >nul

@echo off
REM Launcher para Karaoke App
echo Iniciando Karaoke...
python karaoke.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Ocurrio un error al iniciar la aplicacion.
    echo Asegurate de tener Python instalado y accesible.
    pause
)

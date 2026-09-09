@echo off
TITLE Duotech Telemetria - Control Flota Bomberos
echo ===================================================
echo   Iniciando Servidor Duotech Telemetria (FastAPI)
echo ===================================================
cd /d C:\Duotech_Proyecto
python -m pip install fastapi uvicorn sqlite3 >nul 2>&1
echo [OK] Entorno y dependencias verificadas.
echo [OK] Abriendo interfaz en http://127.0.0.1:8080/dashboard/index.html
start http://127.0.0.1:8080/dashboard/index.html
python main.py
pause
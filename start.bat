@echo off
echo Starting HackerLabAcademy...

if not exist backend\.env (
    echo ERROR: backend\.env not found!
    echo Copy backend\.env.example to backend\.env and set GEMINI_API_KEY
    pause
    exit /b 1
)

start "HackerLabAcademy Backend" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --reload --port 8001"
timeout /t 3 >nul
start "HackerLabAcademy Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
timeout /t 5 >nul
start "" "http://localhost:5174"

echo.
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:5174
echo.

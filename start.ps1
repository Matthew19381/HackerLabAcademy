Write-Host "Starting HackerLabAcademy..." -ForegroundColor Green

if (-not (Test-Path "backend\.env")) {
    Write-Host "ERROR: backend\.env not found!" -ForegroundColor Red
    Write-Host "Copy backend\.env.example to backend\.env and set GEMINI_API_KEY"
    Read-Host "Press Enter to exit"
    exit 1
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD'; python -m uvicorn backend.main:app --reload --port 8001"
Start-Sleep 3
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD\frontend'; npm run dev"
Start-Sleep 5
Start-Process "http://localhost:5174"

Write-Host ""
Write-Host "Backend:  http://localhost:8001" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5174" -ForegroundColor Cyan

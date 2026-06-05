@echo off
echo Starting AI Compiler...
echo.

echo [1/2] Starting Backend...
start "Backend" cmd /k "cd backend && uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo Both servers starting...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs

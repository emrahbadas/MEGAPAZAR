@echo off
cd /d "%~dp0"
echo Starting Megapazar Agent API...
echo.
echo API will run at: http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.
python main.py
pause

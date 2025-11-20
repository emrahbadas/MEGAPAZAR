# Manuel test için server başlatma
Write-Host "🚀 Starting server..." -ForegroundColor Green
cd "c:\Users\emrah badas\OneDrive\Desktop\pazarglobal"
Remove-Item -Path "sessions\*.pkl" -Force -ErrorAction SilentlyContinue
python -m uvicorn main:app --host 0.0.0.0 --port 8000

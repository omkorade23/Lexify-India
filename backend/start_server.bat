@echo off
set PYTHONUTF8=1
cd /d "C:\Users\Om Korade\Lexify-India\backend"
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000

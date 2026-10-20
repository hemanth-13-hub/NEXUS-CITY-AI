@echo off
cd /d "%~dp0backend"
if not exist .venv\Scripts\python.exe py -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if not exist .env copy .env.example .env
python -m app.seed
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause

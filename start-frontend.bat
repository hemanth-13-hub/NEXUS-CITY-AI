@echo off
cd /d "%~dp0frontend"
if not exist node_modules call npm install
if not exist .env copy .env.example .env
npm run dev -- --host 127.0.0.1
pause

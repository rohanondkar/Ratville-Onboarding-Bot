@echo off
cd /d "%~dp0"

if not exist ".env" (
  echo Missing .env file. Copy .env.example to .env and add your bot token.
  copy .env.example .env
  notepad .env
  pause
  exit /b 1
)

echo Installing dependencies...
python -m pip install -r requirements.txt -q

echo.
echo Starting Ratville onboarding bot...
echo Keep this window OPEN while you want auto Player roles.
echo Press Ctrl+C to stop.
echo.

python onboarding_bot.py
pause

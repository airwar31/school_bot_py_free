@echo off
chcp 65001 > nul
echo =====================================================================
echo  🎓 School LMS Telegram Bot (LMS_BOT) - Startup
echo =====================================================================
echo.

if not exist ".env" (
    echo [WARNING] .env file not found! Copying from .env.example...
    copy .env.example .env
    echo [ACTION] Please edit .env and configure your BOT_TOKEN before running!
    echo.
)

echo [INFO] Starting Telegram Bot...
python main.py

pause

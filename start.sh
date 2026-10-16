#!/usr/bin/env bash
# ==============================================================================
# School LMS Telegram Bot - Unix Startup Script
# ==============================================================================

echo "====================================================================="
echo "  🎓 School LMS Telegram Bot (LMS_BOT) - Startup"
echo "====================================================================="

if [ ! -f ".env" ]; then
    echo "[WARNING] .env not found. Copying from .env.example..."
    cp .env.example .env
    echo "[ACTION] Please configure BOT_TOKEN in .env!"
fi

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python3 main.py

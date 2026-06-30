@echo off
title Autopilot Digital Product System Launcher
echo ==========================================================
echo       AUTOPILOT DIGITAL PRODUCT SYSTEM & SWARM
echo ==========================================================
echo.

:: Verify virtual environment exists
if not exist "venv\Scripts\activate" (
    echo Error: Virtual environment (venv) not found.
    echo Please install dependencies first.
    pause
    exit /b
)

echo [1/2] Starting Webhook Server (FastAPI) in a separate window...
start "Autopilot Sales Webhook Server" cmd /k "call venv\Scripts\activate && python src/orchestrator.py --webhook-server"

echo [2/2] Starting Scheduler Loop (Content Generation & Queue)...
echo.
echo Press Ctrl+C in this window to stop the scheduler.
echo ==========================================================
call venv\Scripts\activate
python src/orchestrator.py --scheduler

pause

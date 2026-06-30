@echo off
title Autopilot Digital Product System Installer
echo ==========================================================
echo         AUTOPILOT SYSTEM: ONE-CLICK INSTALLER
echo ==========================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed on your system!
    echo.
    echo Please download and install Python from:
    echo https://www.python.org/downloads/
    echo (Make sure to check the box that says "Add Python to PATH" during installation)
    echo.
    pause
    exit /b
)

echo [1/3] Python found. Setting up virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b
)

echo [2/3] Installing all required software packages (this can take 30-60 seconds)...
call venv\Scripts\activate
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install package dependencies.
    pause
    exit /b
)

echo [3/3] Creating a template config file (.env)...
if not exist ".env" (
    (
    echo GEMINI_API_KEY=your_gemini_api_key_here
    echo.
    echo # (Optional) Social media and Email keys
    echo TWITTER_CONSUMER_KEY=
    echo TWITTER_CONSUMER_SECRET=
    echo TWITTER_ACCESS_TOKEN=
    echo TWITTER_ACCESS_TOKEN_SECRET=
    echo BEEHIIV_API_KEY=
    echo BEEHIIV_PUBLICATION_ID=
    echo DISCORD_WEBHOOK_URL=
    ) > .env
    echo Created .env file. Open it with Notepad to add your keys.
) else (
    echo .env file already exists. Skipping creation.
)

echo.
echo ==========================================================
echo INSTALLATION SUCCESSFUL!
echo.
echo Next Steps:
echo 1. Open the ".env" file in Notepad and paste your Gemini API Key.
echo 2. Double-click "start.bat" to launch the system on autopilot!
echo ==========================================================
pause

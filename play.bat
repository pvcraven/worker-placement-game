@echo off
setlocal

REM --- Worker Placement Game Launcher ---
REM First run: clones/installs everything.
REM Subsequent runs: pulls latest code and launches.

set REPO_URL=https://github.com/pvcraven/Worker-Placement-Game.git
set SERVER_PORT=8765

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python not found. Install Python 3.12+ from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM If we're already inside the repo, just update. Otherwise, clone first.
if exist "pyproject.toml" (
    echo Updating to latest version...
    git pull --ff-only
    if errorlevel 1 (
        echo.
        echo WARNING: Could not auto-update. You may have local changes.
        echo Continuing with current version...
    )
) else (
    echo First-time setup: cloning repository...
    git clone %REPO_URL% game
    cd game
)

REM Install/update dependencies
echo Installing dependencies...
pip install -e ".[dev]" --quiet 2>nul
if errorlevel 1 (
    echo Retrying dependency install...
    pip install -e . --quiet
)

REM Kill any existing server on our port
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%SERVER_PORT% " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM Start server in background
echo Starting server...
start /b "GameServer" python -m server.main --port %SERVER_PORT% >nul 2>&1

REM Give server a moment to start
timeout /t 2 /nobreak >nul

REM Launch client
echo Launching game...
python -m client.main --server ws://localhost:%SERVER_PORT%

REM When client closes, stop the server
echo Shutting down server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%SERVER_PORT% " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo Done.

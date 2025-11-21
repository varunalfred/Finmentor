@echo off
echo ========================================
echo  FinMentor AI - Frontend Setup
echo ========================================
echo.

echo [1/3] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo Node.js: OK
node --version

echo.
echo [2/3] Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo [3/3] Setup complete!
echo.
echo ========================================
echo  Ready to start development server
echo ========================================
echo.
echo To start the app, run:
echo   npm run dev
echo.
echo Then open http://localhost:3000 in your browser
echo.
pause

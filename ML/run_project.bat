@echo off
echo ===================================================
echo Starting Student Performance Analysis System...
echo ===================================================

echo [1/3] Starting Python Analysis Server (Port 8001)...
start "Python Server" cmd /k "python main.py"

echo [2/3] Starting R Automation Server...
start "R Server" cmd /k "Rscript plumber.R"

echo [3/3] Opening Dashboard...
timeout /t 3 >nul
start index.html

echo.
echo ===================================================
echo System Started! 
echo Keep the terminal windows open.
echo ===================================================
pause

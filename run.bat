@echo off
cd /d "%~dp0"
echo ======================================================================
echo   Starting Legal Metrology Compliance System (SIH 2026 PS-26034)
echo   Department of Consumer Affairs (DoCA) - Govt of India
echo ======================================================================
echo.

where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py
)

echo Opening local browser at http://127.0.0.1:5001 ...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5001
%PYTHON_CMD% app.py
pause

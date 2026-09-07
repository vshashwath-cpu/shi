@echo off
title Legal Metrology Compliance System - Global Server
echo =========================================================================
echo    LEGAL METROLOGY (PACKAGED COMMODITIES) RULES, 2011 COMPLIANCE SYSTEM
echo       Department of Consumer Affairs (DoCA) ^| SIH 2026 PS-26034
echo                  Global Internet Deployment (Cloudflare Tunnel)
echo =========================================================================
echo.

:: Ensure we run from this script's directory
cd /d "%~dp0"

REM Start the local Python server in a minimized window
echo [1/2] Starting local LMPC Compliance server on port 5001...
start /min "LMPC Compliance Server" python app.py

REM Wait 3 seconds for server to initialize
timeout /t 3 /nobreak > nul

REM Start Cloudflare Tunnel to expose the server globally with free HTTPS
echo [2/2] Launching Cloudflare Global Tunnel...
echo.
echo =========================================================================
echo  Your global HTTPS link will appear below in a few seconds.
echo  Share that link with anyone in the world to access your workstation!
echo =========================================================================
echo.
if exist "%~dp0cloudflared.exe" (
    "%~dp0cloudflared.exe" tunnel --url http://127.0.0.1:5001
) else (
    "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:5001
)
pause

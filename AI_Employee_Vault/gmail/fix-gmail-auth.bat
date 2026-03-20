@echo off
REM Gmail Re-Authentication Fix Script
REM Use this when orchestrator shows "No new emails" but emails exist

echo.
echo ============================================================
echo   GMAIL RE-AUTHENTICATION FIX
echo ============================================================
echo.
echo This will:
echo   1. Delete old OAuth token (wrong permissions)
echo   2. Delete Gmail cache (force fresh check)
echo   3. Re-authenticate with correct permissions
echo   4. Restart Auto Orchestrator
echo.
echo Press any key to continue...
pause >nul

cd /d "%~dp0AI_Employee_Vault"

echo.
echo [1/4] Stopping any running orchestrator...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/4] Deleting old OAuth token...
del scripts\token.json 2>nul
if exist scripts\token.json (
    echo ERROR: Could not delete token.json
) else (
    echo OK: Token deleted
)

echo.
echo [3/4] Deleting Gmail cache...
del .cache\GmailWatcher_processed.txt 2>nul
echo OK: Cache cleared

echo.
echo [4/4] Re-authenticating Gmail...
echo.
echo *** BROWSER WILL OPEN ***
echo *** SIGN IN TO GOOGLE AND GRANT PERMISSIONS ***
echo.
python scripts/gmail_watcher.py . 10

echo.
echo ============================================================
echo   RE-AUTHENTICATION COMPLETE!
echo ============================================================
echo.
echo Starting Auto Orchestrator...
echo.
python scripts/auto_orchestrator.py

pause

@echo off
REM Quick Gmail Fix - Run in NEW terminal (doesn't stop orchestrator)
REM Use when orchestrator shows "No new emails" but emails exist

echo.
echo ============================================================
echo   GMAIL QUICK FIX
echo ============================================================
echo.
echo This will:
echo   1. Delete old OAuth token (wrong permissions)
echo   2. Delete Gmail cache (force fresh check)
echo   3. Re-authenticate with correct permissions
echo.
echo   Your orchestrator will continue running in other window!
echo.
echo Press any key to continue...
pause >nul

cd /d "%~dp0AI_Employee_Vault"

echo.
echo [1/3] Deleting old OAuth token...
del scripts\token.json 2>nul
if exist scripts\token.json (
    echo ERROR: Could not delete token.json
) else (
    echo OK: Token deleted
)

echo.
echo [2/3] Deleting Gmail cache...
del .cache\GmailWatcher_processed.txt 2>nul
echo OK: Cache cleared

echo.
echo [3/3] Re-authenticating Gmail...
echo.
echo *** BROWSER WILL OPEN ***
echo *** SIGN IN TO GOOGLE AND GRANT PERMISSIONS ***
echo.
python scripts/gmail_watcher.py . 10

echo.
echo ============================================================
echo   GMAIL RE-AUTHENTICATION COMPLETE!
echo ============================================================
echo.
echo Your orchestrator should now detect emails within 120 seconds.
echo Check the orchestrator terminal for:
echo   "Found X new email(s) to process"
echo.
pause

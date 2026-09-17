@echo off
chcp 65001 >nul
echo ============================================
echo   HG Tech Improvement Cases - AI Table Sync
echo ============================================
echo.
"C:\Users\22104\.real\.bin\python-3.12-windows-x64\python.exe" "%~dp0sync_from_aitable.py"
echo.
pause

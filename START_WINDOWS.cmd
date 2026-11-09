@echo off
cd /d "%~dp0"
echo Ionian Sanctuary - Research Assessment
where py >nul 2>nul
if %errorlevel%==0 (py -3 verify_package.py) else (python verify_package.py)
start "" "%~dp0FRONTIER_REAL_TEST.html"
echo.
echo Browser worksheet opened. Wikimedia automatic downloads are optional.
echo If the photos are missing, download them in Chrome and run IMPORT_PHOTOS_WINDOWS.cmd.
pause

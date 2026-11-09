@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (py -3 import_photos.py --check) else (python import_photos.py --check)
pause

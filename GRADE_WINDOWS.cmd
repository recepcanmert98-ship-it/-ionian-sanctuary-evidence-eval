@echo off
cd /d "%~dp0"
if "%~1"=="" (echo Drag your exported trials JSON onto this file.&pause&exit /b 1)
where py >nul 2>nul
if %errorlevel%==0 (py -3 grade_responses.py --grade "%~1") else (python grade_responses.py --grade "%~1")
pause

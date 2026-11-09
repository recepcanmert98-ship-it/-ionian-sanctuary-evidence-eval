@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 goto usepy
where python >nul 2>&1
if not errorlevel 1 goto usepython
echo Python 3.9 or newer is required. No third-party packages or API keys.
pause
exit /b 1
:usepy
py -3 reproduce.py
set ERROR_CODE=%ERRORLEVEL%
pause
exit /b %ERROR_CODE%
:usepython
python reproduce.py
set ERROR_CODE=%ERRORLEVEL%
pause
exit /b %ERROR_CODE%

@echo off
cd /d "%~dp0"
echo IONIAN SANCTUARY - MANUAL PHOTO IMPORT
 echo Select the FOUR JPEGs downloaded in your web browser. No HTTP requests will be made.
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 import_photos.py --interactive --open-sources
) else (
  python import_photos.py --interactive --open-sources
)
echo.
if errorlevel 1 (
  echo Some JPEGs are still missing. Check the four links in PHOTO_RECOVERY.md.
) else (
  echo ALL PHOTOS IMPORTED. Run BUILD_OFFLINE_WINDOWS.cmd next.
)
pause

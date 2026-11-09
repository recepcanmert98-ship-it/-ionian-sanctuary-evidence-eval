@echo off
cd /d "%~dp0"
echo Downloading licensed photographs (smaller Wikimedia thumbnails where available)...
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 fetch_photos.py
) else (
  python fetch_photos.py
)
echo.
if errorlevel 1 (
  echo PHOTO DOWNLOAD INCOMPLETE.
  echo HTTP 429 or a blocked photo source? Stop retries.
  echo Open PHOTO_RECOVERY.md then run IMPORT_PHOTOS_WINDOWS.cmd.
) else (
  echo Photos ready. Run BUILD_OFFLINE_WINDOWS.cmd to create the offline ZIP.
)
pause

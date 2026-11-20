@echo off
title Kavinan Design Studio - website preview
cd /d "%~dp0"
echo Building the website and starting a local preview...
echo Your browser will open at http://localhost:8000
echo Keep this window open while you browse. Close it to stop the preview.
echo.
start "" cmd /c "timeout /t 3 >nul & start http://localhost:8000"
python build.py --serve
if errorlevel 1 (
  echo.
  echo Python was not found or the build failed.
  echo Install Python 3.12 from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^),
  echo or simply open offline\index.html by double-clicking it.
  pause
)

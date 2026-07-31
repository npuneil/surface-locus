@echo off
REM Quickstart - Surface Locus Device-Tracking Prototype
setlocal
cd /d %~dp0
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
REM pip install -r locus_requirements.txt   (first run only)
python locus_app.py
endlocal

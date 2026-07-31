# Quickstart — Surface Locus Device-Tracking Prototype
Set-Location -Path $PSScriptRoot
if (Test-Path .\.venv\Scripts\Activate.ps1) { . .\.venv\Scripts\Activate.ps1 }
# pip install -r locus_requirements.txt   # first run only
python locus_app.py

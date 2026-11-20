@echo off
rem Double-click to open Canary Lab with live runs. Close this window to stop it.
cd /d "%~dp0"
python pipeline-app\serve.py
pause

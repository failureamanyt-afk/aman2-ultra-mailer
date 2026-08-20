@echo off
title BM2 Ultra
cd /d "%~dp0"
start "" python web_server.py
timeout /t 2 >nul
start "" http://localhost:5000/

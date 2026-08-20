@echo off
title AMAN2 - Generate Public Universal Link for Friends
cd /d "%~dp0"
echo ========================================================
echo   Generating Universal Link for Other PCs / Friends...
echo ========================================================
python generate_public_link.py
pause

@echo off
setlocal
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
  echo The Tactile Dice designer needs uv. Install uv, then run .\dice again.
  exit /b 1
)

uv run python tools\tactile_dice.py %*
exit /b %errorlevel%

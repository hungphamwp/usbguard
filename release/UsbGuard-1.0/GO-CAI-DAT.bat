@echo off
chcp 65001 >nul
title Go cai dat UsbGuard
net session >nul 2>&1
if errorlevel 1 (
  echo Can chay voi quyen Administrator.
  echo Bam chuot phai vao GO-CAI-DAT.bat ^> Run as administrator.
  pause
  exit /b 5
)
cd /d "%~dp0"
echo === GO CAI DAT USBGUARD ===
UsbGuard.exe uninstall
pause

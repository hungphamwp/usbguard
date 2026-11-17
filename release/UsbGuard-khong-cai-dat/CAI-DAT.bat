@echo off
title Cai dat UsbGuard
net session >nul 2>&1
if errorlevel 1 (
  echo Can chay voi quyen Administrator.
  echo Bam chuot phai vao CAI-DAT.bat ^> Run as administrator.
  pause
  exit /b 5
)
cd /d "%~dp0"
echo === CAI DAT USBGUARD ===
echo Dat mat khau quan tri (it nhat 8 ky tu). GHI LAI mat khau nay, quen se khong go duoc.
echo.
UsbGuard.exe install
echo.
UsbGuard.exe status
pause

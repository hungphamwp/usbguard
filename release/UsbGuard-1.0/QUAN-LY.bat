@echo off
chcp 65001 >nul
title Quan ly UsbGuard
net session >nul 2>&1
if errorlevel 1 (
  echo Can chay voi quyen Administrator.
  echo Bam chuot phai vao QUAN-LY.bat ^> Run as administrator.
  pause
  exit /b 5
)
cd /d "%~dp0"
:menu
cls
echo ===== QUAN LY USBGUARD =====
echo  1. Xem trang thai
echo  2. Tam dung chan USB (nhap so phut)
echo  3. Bat lai chan USB ngay
echo  4. Xem USB dang cam (lay ID de cho phep)
echo  5. Cho phep 1 USB (them vao danh sach)
echo  6. Bo cho phep 1 USB
echo  7. Xem danh sach USB duoc phep
echo  8. Doi mat khau quan tri
echo  0. Thoat (hoac bam Enter)
echo.
set "c="
set /p c=Chon so: 
if "%c%"=="" exit /b 0
if "%c%"=="1" UsbGuard.exe status
if "%c%"=="2" (set /p m=So phut tam dung [1-1440]: & call UsbGuard.exe pause %%m%%)
if "%c%"=="3" UsbGuard.exe resume
if "%c%"=="4" UsbGuard.exe devices
if "%c%"=="5" (set /p id=Dan ID thiet bi: & call UsbGuard.exe whitelist add "%%id%%")
if "%c%"=="6" (set /p id=Dan ID thiet bi: & call UsbGuard.exe whitelist remove "%%id%%")
if "%c%"=="7" UsbGuard.exe whitelist list
if "%c%"=="8" UsbGuard.exe passwd
if "%c%"=="0" exit /b 0
echo.
pause
goto menu

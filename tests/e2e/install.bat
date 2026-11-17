@echo off
rem Chạy tự động sau khi Windows cài xong (dockur): khởi động kịch bản kiểm thử cắm USB.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\OEM\e2e-usb.ps1" > "C:\OEM\e2e-console.txt" 2>&1

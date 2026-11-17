# Kết quả kiểm thử UsbGuard 1.1

| Bộ kiểm thử | Môi trường | Kết quả | Lần chạy |
|---|---|---|---|
| Unit test (xUnit) | Windows Server 2022, 2025 | 12/12 mỗi bản | https://github.com/hungphamwp/usbguard/actions/runs/44128607095 |
| Tích hợp: cài dịch vụ thật, 3 tầng chặn, chống tắt, người dùng thường, gỡ (`tests/integration.ps1`) | Windows Server 2022, 2025 | 34/34 mỗi bản | https://github.com/hungphamwp/usbguard/actions/runs/44128607095 |
| Cắm USB thật: cài bằng setup.exe, cắm/rút ổ USB, bàn phím USB, whitelist, file đang mở, gỡ bằng trình gỡ (`tests/e2e/`) | Windows 10 Pro, Windows 11 Pro (QEMU, cổng xHCI) | 17/17 mỗi bản | https://github.com/hungphamwp/usbguard/actions/runs/44128607063 |

Ổ USB trong kiểm thử cắm USB thật là ổ QEMU usb-storage cắm nóng vào cổng USB 3 (xHCI) của máy ảo. Windows nhận đúng như USB flash disk thật: bus USB, driver USBSTOR, có ký tự ổ, ghi được file (ca E01).

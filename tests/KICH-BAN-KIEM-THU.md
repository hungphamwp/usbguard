# Kịch bản kiểm thử thủ công (chạy trên Windows 10/11 thật)

Chuẩn bị: build `dotnet build -c Release`, copy toàn bộ `bin/Release/net48/` sang máy Windows
thật (hoặc máy ảo), chuẩn bị 1 USB flash disk thường + 1 tài khoản Windows không phải Administrator.

| # | Bước thực hiện | Kết quả mong đợi |
|---|---|---|
| 1 | Admin: `UsbGuard.exe install MatKhau123`, khởi động lại máy | Dịch vụ `UsbGuard` ở trạng thái Running, Start type Automatic (`sc qc UsbGuard`) |
| 2 | Cắm USB flash disk thường vào | Ổ đĩa bị gỡ an toàn (eject) trong vòng 2 giây, không hiện trong "This PC"; `usbguard.log` ghi lại tên + ID thiết bị |
| 3 | Admin: `UsbGuard.exe whitelist add "<ID lấy từ log bước 2>" MatKhau123`, cắm lại đúng USB đó | Không bị eject, dùng được bình thường |
| 4 | Đăng nhập bằng tài khoản thường (không phải Administrator), mở Command Prompt, chạy `sc stop UsbGuard` | Bị từ chối "Access is denied" — xác nhận người dùng thường không tắt được dịch vụ |
| 5 | Admin: `UsbGuard.exe uninstall sai-mat-khau` | Bị từ chối, dịch vụ vẫn chạy, không có gì thay đổi |
| 6 | Admin: `UsbGuard.exe uninstall MatKhau123` | Dịch vụ dừng + xoá sạch, `USBSTOR` Start trở lại 3 (mặc định Windows), cắm USB bất kỳ hoạt động lại bình thường |
| 7 | Cắm chuột/bàn phím/USB không phải ổ đĩa (thiết bị HID) trong lúc dịch vụ đang chạy (trước bước 6) | Không bị ảnh hưởng — `Enforcer` chỉ nhắm driver lưu trữ (`USBSTOR`/`UASPStor`), `UsbDisks` chỉ liệt kê `GUID_DEVINTERFACE_DISK` |

## Ghi lại kết quả

Điền vào bảng này sau khi chạy thật trên Windows (đính kèm ảnh chụp màn hình vào báo cáo):

| # | Đạt / Không đạt | Ghi chú |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |

# Kế hoạch & Tài liệu kiểm thử UsbGuard

Hệ thống kiểm thử của UsbGuard được thiết kế theo 3 tầng chiến lược chặt chẽ:

## 1. Unit Test tự động (`tests/UsbGuard.Tests.csproj`)
- Chạy trên nền tảng .NET đa nền tảng (Windows, macOS, Linux).
- Kiểm thử các mô-đun nghiệp vụ thuần túy không phụ thuộc Win32 P/Invoke:
  - `src/Auth.cs`: Cơ chế băm mật khẩu PBKDF2-SHA1 với 100000 vòng lặp, tạo muối 16 byte ngẫu nhiên, so sánh thời gian hằng để chống tấn công kênh kề (timing attack), kiểm tra độ dài và loại trừ các chuỗi băm sai định dạng hoặc số vòng lặp dưới 1000.
  - `src/Whitelist.cs`: So khớp chuỗi ID thiết bị không phân biệt chữ hoa chữ thường, kiểm tra độ dài tối thiểu của mục nhập (tối thiểu 4 ký tự), xử lý danh sách rỗng.
- Kết quả kiểm chuẩn: **12/12 ca kiểm thử đạt**.

Chạy kiểm thử:
```bash
dotnet test tests/UsbGuard.Tests.csproj
```

## 2. Kiểm thử tích hợp tự động trên Windows (`tests/integration.ps1`)
- Kịch bản PowerShell thực hiện kiểm thử tự động toàn diện **30 ca kiểm thử** trên môi trường Windows Server thật thông qua GitHub Actions CI (`.github/workflows/windows.yml` trên 2 hệ điều hành Windows Server 2022 và Windows Server 2025).
- Nội dung kiểm thử bao gồm:
  - Quá trình cài đặt dịch vụ, thiết lập quyền LocalSystem và cơ chế tự phục hồi sau sự cố (`sc failure`).
  - Kiểm tra việc vô hiệu hóa driver lưu trữ USBSTOR (`Start = 4`) và chính sách `Deny_All = 1`.
  - Kiểm tra tính năng tự phục hồi cấu hình Registry khi bị sửa đổi thủ công trái phép.
  - Kiểm tra cơ chế "không tắt được": Administrator thực hiện `sc stop` bị từ chối với mã lỗi 1052 (`CanStop = false`); khi tiến trình bị cưỡng chế kết thúc (`taskkill /F`), Windows tự động khởi chạy lại sau 5 giây.
  - Kiểm tra phân quyền an toàn: Tài khoản người dùng thông thường bị từ chối quyền dừng dịch vụ (lỗi 5), không đọc được khóa cấu hình chứa mã băm mật khẩu trong HKLM (lỗi 5 / ACL), không gỡ cài đặt được.
  - Chuyển đổi linh hoạt giữa 3 chế độ: CHẶN TẤT CẢ, DANH SÁCH CHO PHÉP và TẠM DỪNG.
  - Gọi API SetupAPI và IOCTL truy vấn thiết bị thật (`UsbGuard.exe devices --all`).
  - Quy trình gỡ cài đặt sạch: kiểm tra mật khẩu, dừng dịch vụ và hoàn trả toàn bộ cấu hình Registry về mặc định của Windows.

Chạy kiểm thử tích hợp trên máy Windows (với quyền Administrator):
```powershell
powershell -ExecutionPolicy Bypass -File tests\integration.ps1 -Exe bin\Release\net48\UsbGuard.exe
```

## 3. Kịch bản kiểm thử thủ công với USB vật lý (`tests/KICH-BAN-KIEM-THU.md`)
- 7 kịch bản kiểm tra tương tác với thiết bị USB flash disk vật lý cắm vào cổng USB trên máy tính thật.
- Bổ sung quy trình lấy ID thiết bị bằng lệnh `UsbGuard.exe devices` khi đang ở chế độ tạm dừng, kiểm tra thông báo cảnh báo `WTSSendMessage` gửi tới người dùng màn hình console, và cột ghi nhận ảnh chụp màn hình minh chứng.

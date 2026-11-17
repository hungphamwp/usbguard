# UsbGuard — Ứng dụng ngăn cắm USB Flash Disk trên Windows

Đề tài: *"Xây dựng ứng dụng ngăn người dùng cắm USB flash disk vào máy hệ điều hành Windows, ứng dụng được chạy như dịch vụ không tắt được."*

## 1. Tóm tắt giải pháp

UsbGuard là 1 **Windows Service** viết bằng C# (.NET Framework 4.8), hoạt động với 2 lớp bảo vệ và 3 chế độ vận hành:

1. **2 lớp chặn:**
   - **Lớp 1 (Chính sách & Driver):** Tắt driver lưu trữ `USBSTOR`, `UASPStor` qua Registry (`Start = 4`) và kích hoạt chính sách `RemovableStorageDevices\Deny_All` tương đương Group Policy doanh nghiệp.
   - **Lớp 2 (Quét & Eject chủ động):** Sử dụng SetupAPI và `IOCTL_STORAGE_QUERY_PROPERTY` để phát hiện các ổ đĩa có `BusType = 7` (USB) và gỡ an toàn bằng `CM_Request_Device_Eject`. Đi tối đa 2 cấp đến nút USB cha (không gỡ hub để tránh ảnh hưởng chuột, bàn phím). Dự phòng bằng `pnputil /disable-device` khi có tiến trình khóa file.
2. **3 chế độ hoạt động:**
   - **CHẶN TẤT CẢ (mặc định khi whitelist rỗng):** Khóa toàn bộ driver lưu trữ và chính sách, gỡ bỏ ngay lập tức mọi ổ đĩa USB được cắm vào.
   - **DANH SÁCH CHO PHÉP (khi whitelist có mục):** Mở driver lưu trữ để USB hợp lệ hoạt động, quét và gỡ bỏ ngay các ổ đĩa USB không khớp ID trong danh sách cho phép.
   - **TẠM DỪNG (có thời hạn, yêu cầu mật khẩu quản trị):** Mở lại toàn bộ quyền truy cập USB và khôi phục các thiết bị từng bị vô hiệu hóa trong khoảng thời gian chỉ định.
3. **Phản ứng tức thì:** Lắng nghe sự kiện WMI `__InstanceCreationEvent` của `Win32_DiskDrive` để xử lý ngay khi thiết bị vừa gắn vào, kết hợp vòng lặp kiểm tra định kỳ 2 giây để tự động khôi phục Registry nếu bị can thiệp trái phép.
4. **Cơ chế "Không tắt được":**
   - Dịch vụ thiết lập thuộc tính `CanStop = false`, khiến Service Control Manager (SCM) của Windows từ chối mọi lệnh dừng (`sc stop`, `Stop-Service`, giao diện `services.msc`), trả về lỗi 1052 kể cả khi người thực hiện là Administrator.
   - Người dùng thông thường không có quyền gửi lệnh điều khiển tới dịch vụ (trả về lỗi 5 Access Denied).
   - Nếu tiến trình dịch vụ bị cưỡng chế kết thúc (`taskkill /F`), cơ chế phục hồi dịch vụ của Windows (`sc failure`) tự động khởi chạy lại dịch vụ sau 5 giây.
   - Dịch vụ chỉ dừng an toàn khi người quản trị thực hiện lệnh `UsbGuard.exe uninstall` với đúng mật khẩu quản trị đã thiết lập (bật cờ `Uninstalling` trong Registry để dịch vụ chủ động dừng).

## 2. Kiến trúc & mã nguồn

```
UsbGuard/
├── UsbGuard.csproj
├── src/
│   ├── Program.cs      Điểm khởi nhập CLI (install/uninstall/status/pause/resume/whitelist/devices/passwd)
│   ├── Worker.cs        Lớp ServiceBase — vòng lặp định kỳ 2 giây kết hợp bộ theo dõi sự kiện WMI
│   ├── Enforcer.cs      Quản lý khóa Registry cho driver (USBSTOR/UASPStor) và chính sách lưu trữ di động
│   ├── UsbDisks.cs      Quét danh sách ổ đĩa (SetupAPI), kiểm tra BusType và gỡ thiết bị (CfgMgr32)
│   ├── Native.cs        Khai báo P/Invoke Win32 API (kernel32, setupapi, cfgmgr32, advapi32, wtsapi32)
│   ├── Whitelist.cs     Thuật toán so khớp ID thiết bị với danh sách cho phép
│   ├── Settings.cs      Quản lý đọc/ghi cấu hình tại HKLM\SOFTWARE\UsbGuard với phân quyền ACL bảo mật
│   ├── Auth.cs          Băm và xác thực mật khẩu quản trị qua chuẩn PBKDF2-SHA1 với muối 16 byte
│   ├── Password.cs      Hỗ trợ nhập mật khẩu ẩn từ bàn phím hoặc đọc từ tham số dòng lệnh
│   ├── Installer.cs     Cài đặt, cấu hình phục hồi, thiết lập phân quyền và gỡ bỏ dịch vụ bằng sc.exe
│   ├── Cli.cs           Xử lý các lệnh quản trị dòng lệnh
│   ├── Log.cs           Ghi nhật ký hệ thống ra tập tin và Windows Event Log
│   ├── Reg.cs           Tiện ích thao tác Registry và thiết lập bảo mật DACL
│   ├── Sys.cs           Tiện ích thực thi tiến trình hệ thống an toàn
│   └── Constants.cs     Định nghĩa hằng số tên dịch vụ và thông tin hiển thị
├── tests/               Kiểm thử tự động và kịch bản thực nghiệm
└── reference/           Mã nguồn tham khảo trong quá trình nghiên cứu thiết kế
```

### 2 lớp bảo vệ (Defense in Depth)

| Lớp | Cơ chế kỹ thuật | Mục đích thiết kế |
|---|---|---|
| 1. Chính sách & Driver | `USBSTOR`/`UASPStor` `Start = 4` + `RemovableStorageDevices\Deny_All = 1` | Chặn tận gốc ở mức hệ điều hành, ngăn nạp driver lưu trữ USB, tương tự Group Policy doanh nghiệp. |
| 2. Quét & Gỡ chủ động | SetupAPI liệt kê `GUID_DEVINTERFACE_DISK`, `IOCTL_STORAGE_QUERY_PROPERTY`, `CM_Request_Device_Eject` | Gỡ bỏ ngay các thiết bị đã cắm trước khi dịch vụ chạy hoặc khi driver đã nạp sẵn; cô lập nút thiết bị, bảo toàn hub. |

## 3. Cài đặt & sử dụng trên Windows

Mở Command Prompt hoặc PowerShell với quyền quản trị (**Run as administrator**):

```bat
:: Biên dịch bản Release (.NET Framework 4.8)
dotnet build -c Release

:: Cài đặt dịch vụ (có thể nhập trực tiếp mật khẩu hoặc bỏ trống để nhập ẩn)
UsbGuard.exe install MatKhauQuanTri123

:: Xem trạng thái hoạt động của dịch vụ và cấu hình whitelist
UsbGuard.exe status

:: Liệt kê các ổ đĩa USB đang kết nối (kèm bus type) để lấy ID cấu hình
UsbGuard.exe devices

:: Liệt kê toàn bộ các ổ đĩa trên máy (bao gồm ổ đĩa trong)
UsbGuard.exe devices --all

:: Tạm dừng chặn trong 15 phút (cần mật khẩu quản trị)
UsbGuard.exe pause 15 MatKhauQuanTri123

:: Kích hoạt lại trạng thái chặn ngay lập tức
UsbGuard.exe resume MatKhauQuanTri123

:: Thêm thiết bị vào danh sách cho phép (ID lấy từ lệnh devices hoặc nhật ký)
UsbGuard.exe whitelist add "VID_0951&PID_1666" MatKhauQuanTri123

:: Xem danh sách thiết bị được phép
UsbGuard.exe whitelist list

:: Gỡ thiết bị khỏi danh sách cho phép
UsbGuard.exe whitelist remove "VID_0951&PID_1666" MatKhauQuanTri123

:: Thay đổi mật khẩu quản trị
UsbGuard.exe passwd MatKhauCu123 MatKhauMoi456

:: Gỡ cài đặt dịch vụ và khôi phục cài đặt mặc định của Windows
UsbGuard.exe uninstall MatKhauQuanTri123
```

Khi không truyền tham số mật khẩu trên dòng lệnh, chương trình tự động hiển thị lời nhắc và ẩn ký tự khi nhập để chống lộ mật khẩu trong lịch sử dòng lệnh hoặc danh sách tiến trình.

Chạy thử nghiệm trực tiếp trên màn hình console (không qua dịch vụ SCM):
```bat
UsbGuard.exe --console
```

## 4. Kế hoạch & kết quả kiểm thử

Hệ thống được kiểm thử toàn diện qua 3 cấp độ:

1. **Unit Test tự động (`tests/AuthTests.cs`):**
   - 12/12 ca kiểm thử đạt trên nền tảng .NET đa nền tảng.
   - Kiểm tra thuật toán băm PBKDF2 (muối ngẫu nhiên, độ dài, thời gian hằng, từ chối hash giả mạo) và thuật toán so khớp whitelist.
2. **Kiểm thử tích hợp tự động (`tests/integration.ps1`):**
   - 30 ca kiểm thử tích hợp tự động trên môi trường Windows Server 2022 và Windows Server 2025 qua GitHub Actions CI (`.github/workflows/windows.yml`).
   - Kiểm tra cài đặt, tự khởi động lại sau sự cố, từ chối lệnh `sc stop` từ Administrator (lỗi 1052), chặn toàn diện người dùng thường (lỗi 5), tự sửa Registry khi bị can thiệp, chuyển đổi 3 chế độ hoạt động và gỡ sạch.
3. **Kịch bản kiểm thử thủ công với USB vật lý (`tests/KICH-BAN-KIEM-THU.md`):**
   - 7 kịch bản kiểm thử thực tế trên máy có cổng USB vật lý (cắm USB flash disk thật, kiểm tra gỡ bỏ, xác thực whitelist, kiểm tra tính độc lập của chuột/bàn phím HID).

## 5. Tài liệu tham khảo

- Chuẩn lưu trữ USB Mass Storage Class (BOT và UAS Specification).
- Tài liệu Microsoft Learn về Windows Services Architecture, Service Control Manager, và Service Recovery Options (`sc.exe failure`).
- Tài liệu Microsoft Win32 API: SetupAPI (`SetupDiGetClassDevs`), CfgMgr32 (`CM_Request_Device_Eject`), Storage IOCTL (`IOCTL_STORAGE_QUERY_PROPERTY`), Removable Storage Policies.
- RFC 8018: Password-Based Cryptography Specification (PBKDF2).
- Các dự án mã nguồn mở tham khảo cấu trúc và giải pháp:
  - [JBalanza/USBBlocker](https://github.com/JBalanza/USBBlocker)
  - [sidd607/usbAlert](https://github.com/sidd607/usbAlert)
  - [amir13872/usb-control-application](https://github.com/amir13872/usb-control-application)
  - [Den-Sec/USBBlocker](https://gitblind.noratr.app/Den-Sec/USBBlocker)

## 6. Giới hạn đã biết

- Nhận diện thiết bị theo cặp VID/PID: Nếu 2 thiết bị USB cùng hãng, cùng chủng loại và không có số serial phân biệt từ nhà sản xuất, chính sách whitelist theo VID/PID sẽ áp dụng cho cả 2. Giải pháp khuyến nghị là ưu tiên cấu hình theo số serial phần cứng hoặc sử dụng chế độ `pause` có thời hạn.
- Giới hạn quyền Administrator cấp cao nhất: Administrator có quyền khởi động máy vào chế độ Safe Mode hoặc can thiệp trực tiếp vào ổ cứng ngoại tuyến (offline registry editing) vẫn có thể vô hiệu hóa dịch vụ. Đây là giới hạn tự nhiên của mô hình phân quyền hệ điều hành Windows khi không sử dụng giải pháp bảo mật phần cứng chuyên dụng.
- Phạm vi thiết bị: Phiên bản hiện tại tập trung kiểm soát các thiết bị lưu trữ dạng khối (USB Mass Storage và UAS). Thiết bị truyền thông đa phương tiện MTP/PTP (như điện thoại thông minh) hoặc thiết bị quang (CD/DVD) nằm ngoài phạm vi xử lý của phiên bản này.

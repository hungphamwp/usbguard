# UsbGuard — Ứng dụng ngăn cắm USB Flash Disk trên Windows

Đề bài: *"Xây dựng ứng dụng ngăn người dùng cắm USB flash disk vào máy hệ điều hành Windows,
ứng dụng được chạy như dịch vụ không tắt được."*

## 1. Tóm tắt giải pháp

UsbGuard là một **Windows Service** viết bằng C# (.NET Framework 4.8), khi bật sẽ:

1. **Chặn driver lưu trữ USB** (`USBSTOR`, `UASPStor`) bằng registry — cùng cơ chế mà
   Group Policy "Removable Storage Access" dùng trên Windows thật.
2. **Quét mọi ổ đĩa đang cắm qua cổng USB** (SetupAPI + IOCTL_STORAGE_QUERY_PROPERTY) và
   **gỡ an toàn (eject)** ổ nào không nằm trong whitelist.
3. Lặp lại kiểm tra mỗi 2 giây để tự sửa nếu registry bị chỉnh tay.

**"Không tắt được" nghĩa là gì trong bản này:** dịch vụ Windows theo mặc định chỉ
Administrator mới Start/Stop/Delete được qua `sc.exe` / `services.msc` — người dùng
thường không có quyền đó. Đây là hành vi chuẩn của Windows Service, **không phải**
cơ chế ẩn mình/chống gỡ bởi chính admin. UsbGuard có lệnh `uninstall` công khai,
yêu cầu đúng mật khẩu quản trị do chính người cài đặt. Quyết định thiết kế này áp dụng
đúng mô hình các phần mềm device-control/DLP thương mại thật (xem mục 5).

## 2. Kiến trúc & mã nguồn

```
UsbGuard/
├── UsbGuard.csproj
├── src/
│   ├── Program.cs      CLI entry point (install/uninstall/status/pause/whitelist/passwd)
│   ├── Worker.cs        ServiceBase — vòng lặp chính (2s/lần)
│   ├── Enforcer.cs      Chặn ở mức registry (driver + policy, kiểu Group Policy)
│   ├── UsbDisks.cs      Liệt kê ổ USB (SetupAPI) + eject an toàn (CM_Request_Device_Eject)
│   ├── Native.cs        P/Invoke: kernel32, setupapi, cfgmgr32, advapi32
│   ├── Whitelist.cs     So khớp ID thiết bị với danh sách cho phép
│   ├── Settings.cs      Lưu trạng thái tại HKLM\SOFTWARE\UsbGuard
│   ├── Auth.cs          Băm/so mật khẩu quản trị (PBKDF2-SHA1, muối ngẫu nhiên)
│   ├── Installer.cs     sc.exe create/delete, copy vào Program Files
│   ├── Cli.cs           Lệnh pause/resume/whitelist/passwd (yêu cầu mật khẩu)
│   ├── Log.cs           Ghi log file + Event Log
│   ├── Reg.cs / Sys.cs  Tiện ích registry / chạy tiến trình con
│   └── Constants.cs     Tên/mô tả dịch vụ
├── tests/               (xem mục 4 — kế hoạch kiểm thử)
└── reference/           Mã nguồn mở tham khảo khi thiết kế (xem mục 5)
```

### Hai lớp chặn (defense in depth)

| Lớp | Cơ chế | Vì sao cần |
|---|---|---|
| 1. Chính sách/driver | `USBSTOR`/`UASPStor` Start=4 + `RemovableStorageDevices\Deny_All` | Chặn tận gốc — Windows không gắn driver cho ổ đĩa nữa, giống Group Policy doanh nghiệp |
| 2. Quét & eject chủ động | SetupAPI liệt kê ổ USB đang cắm, `CM_Request_Device_Eject` | Dự phòng cho thiết bị đã cắm trước khi service khởi động, hoặc driver đã nạp sẵn |

### Whitelist

- Quản trị viên thêm ID thiết bị (VD `VID_0951&PID_1666` hoặc số serial) bằng:
  `UsbGuard.exe whitelist add "VID_0951&PID_1666" <mật_khẩu>`
- Thiết bị khớp whitelist sẽ không bị eject (nhưng registry vẫn chặn driver —
  nếu cần dùng USB thường xuyên, nên `pause` tạm thời thay vì whitelist VID/PID
  vì nhiều USB flash disk dùng chung VID/PID giá rẻ, không phân biệt được theo serial giả).

## 3. Cài đặt & sử dụng (trên máy Windows thật)

```bat
:: Build (trên Windows, Visual Studio hoặc dotnet build với Developer Command Prompt)
dotnet build -c Release

:: Cài đặt (PHẢI chạy Command Prompt "Run as administrator")
UsbGuard.exe install MatKhauManhCuaBan123

:: Xem trạng thái
UsbGuard.exe status

:: Tạm dừng chặn 15 phút (vd. cần chép dữ liệu hợp lệ)
UsbGuard.exe pause 15 MatKhauManhCuaBan123

:: Thêm thiết bị vào whitelist
UsbGuard.exe whitelist add "VID_0951&PID_1666" MatKhauManhCuaBan123

:: Gỡ cài đặt (khôi phục mặc định Windows)
UsbGuard.exe uninstall MatKhauManhCuaBan123
```

Chạy thử không cần cài dịch vụ (debug nhanh trong console):
```bat
UsbGuard.exe --console
```

## 4. Kế hoạch kiểm thử (đặt mã thật vào `tests/`)

1. **Cắm USB flash disk thường** → phải bị eject trong ≤2s, log ghi lại tên + ID thiết bị.
2. **Thêm whitelist rồi cắm lại cùng thiết bị** → không bị eject.
3. **Người dùng thường (không phải admin) chạy `sc stop UsbGuard`** → bị từ chối quyền (Access denied) — xác nhận tính "không tắt được".
4. **Admin chạy `UsbGuard.exe uninstall` sai mật khẩu** → từ chối, dịch vụ vẫn chạy.
5. **Admin chạy đúng mật khẩu** → gỡ sạch, `USBSTOR` Start trở lại 3 (mặc định Windows), cắm USB lại hoạt động bình thường.
6. **Khởi động lại máy** → dịch vụ tự chạy lại (Start Automatic), vẫn chặn.
7. **Chuột/bàn phím/USB không phải ổ đĩa** (HID) → không bị ảnh hưởng (Enforcer chỉ nhắm driver lưu trữ, UsbDisks chỉ liệt kê `GUID_DEVINTERFACE_DISK`).

## 5. Mã nguồn tham khảo (không dùng trực tiếp, chỉ đối chiếu thiết kế)

Đã khảo sát các dự án mã nguồn mở cùng chủ đề trước khi tự viết lại UsbGuard theo
kiến trúc riêng (đăng ký WM_DEVICECHANGE / SetupAPI, chặn registry kiểu GPO):

- [JBalanza/USBBlocker](https://github.com/JBalanza/USBBlocker) — Windows Service C#, cơ chế whitelist qua "training mode", khoá màn hình khi phát hiện USB lạ.
- [sidd607/usbAlert](https://github.com/sidd607/usbAlert) — Windows Service C#, dùng `RegisterDeviceNotification`/`WM_DEVICECHANGE` + SetupAPI để liệt kê thiết bị USB (tham khảo `UsbApi.cs`, `helper.cs`).
- [amir13872/usb-control-application](https://github.com/amir13872/usb-control-application) — whitelist + xác thực mật khẩu cho thiết bị lạ (tham khảo mô hình Config/Whitelist/Log).
- [Den-Sec/USBBlocker](https://gitblind.noratr.app/Den-Sec/USBBlocker) — script PowerShell bật/tắt driver USBSTOR qua registry (xác nhận đây là cơ chế chặn gốc rễ đúng chuẩn Windows).

UsbGuard **không** sao chép nguyên văn code từ các repo trên; các file trong
`reference/` được giữ lại chỉ để đối chiếu khi viết báo cáo và trích dẫn nguồn,
không build vào sản phẩm (`UsbGuard.csproj` chỉ compile `src/**/*.cs`).

## 6. Giới hạn đã biết (ghi trong báo cáo cho trung thực)

- Chưa chặn USB qua Windows To Go / RAW disk truy cập bằng driver tự ký của kẻ tấn công có quyền SYSTEM — nằm ngoài phạm vi đồ án.
- Whitelist theo VID/PID không phân biệt được 2 USB cùng model, cùng hãng không có serial — nên ưu tiên whitelist theo serial hoặc dùng `pause` thời hạn.
- Build & test được thực hiện biên dịch trên macOS (dùng `Microsoft.NETFramework.ReferenceAssemblies`); **chạy thực tế bắt buộc trên Windows** vì dùng P/Invoke `setupapi.dll`/`cfgmgr32.dll`.

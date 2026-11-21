# Kết quả kiểm thử tích hợp UsbGuard — Microsoft Windows Server 2022 Datacenter (10.0.20348)

Thời điểm: 2026-11-21 08:30:47 · Kết quả: **37/37 ca đạt**

| Mã | Ca kiểm thử | Kết quả | Chi tiết |
|---|---|---|---|
| TC01 | Cài đặt, dịch vụ chạy | Đạt | mã thoát 0, trạng thái Running |
| TC02 | Khởi động tự động cùng Windows | Đạt | StartType = Automatic |
| TC03 | Cấu hình tự khởi động lại khi bị kill | Đạt | sc qfailure có RESTART |
| TC04 | Chạy dưới tài khoản LocalSystem | Đạt | SERVICE_START_NAME = LocalSystem |
| TC05 | USBSTOR bị tắt (Start = 4) | Đạt | Start = 4, sau 2 ms |
| TC06 | Chính sách Removable Storage Deny_All = 1 | Đạt | Deny_All = 1 |
| TC07 | Tự sửa khi registry bị đổi tay | Đạt | khôi phục Start = 4 sau 1311 ms |
| TC31 | Tầng 3: cấm cài thiết bị lớp USB Mass Storage, giữ nguyên mục của công ty | Đạt | DenyDeviceIDs = 1, mục UsbGuard: USB\Class_08&SubClass_06&Prot_50, USB\Class_08&SubClass_06&Prot_62, USB\Class_08; mục công ty còn: USB\VID_DEAD&PID_BEEF |
| TC32 | Tầng 3 tự sửa khi bị xoá tay | Đạt | khôi phục sau 1989 ms |
| TC08 | Admin "sc stop" bị từ chối | Đạt | mã 1052 (1052 = dịch vụ không nhận lệnh Stop), trạng thái Running |
| TC09 | Admin Stop-Service (PowerShell) bị từ chối | Đạt | trạng thái Running |
| TC10 | Bị kill tiến trình thì Windows tự chạy lại | Đạt | PID 1040 -> 2648, chạy lại sau 5398 ms |
| TC11 | User thường "sc stop" bị từ chối quyền | Đạt | mã 5 (5 = Access is denied) |
| TC12 | User thường không đổi được kiểu khởi động | Đạt | mã 5 |
| TC13 | User thường không xoá được dịch vụ | Đạt | mã 5 |
| TC14 | User thường không đọc được cấu hình/mã băm mật khẩu | Đạt | mã 1 |
| TC15 | User thường gỡ cài đặt bị từ chối (kể cả biết mật khẩu) | Đạt | mã 5 |
| TC16 | User thường không mở lại được driver USB | Đạt | mã 1 |
| TC17 | Tạm dừng với sai mật khẩu bị từ chối | Đạt | mã 3 |
| TC18 | Tạm dừng đúng mật khẩu: mở lại USB | Đạt | USBSTOR Start = 3, sau 1203 ms |
| TC19 | Bật lại chặn | Đạt | USBSTOR Start = 4, sau 1858 ms |
| TC20 | Có whitelist: chuyển sang chế độ danh sách cho phép | Đạt | driver mở để USB được phép chạy, sau 1974 ms |
| TC21 | Xem whitelist | Đạt | có VID_0951&PID_1666 |
| TC22 | Xoá whitelist: quay lại chặn tất cả | Đạt | sau 1966 ms |
| TC23 | Đổi mật khẩu quản trị | Đạt | đổi sang mật khẩu mới rồi đổi lại |
| TC24 | Liệt kê ổ đĩa qua SetupAPI + IOCTL (gọi API Windows thật) | Đạt | đọc được loại bus của từng ổ |
| TC25 | Không nhận nhầm ổ cứng trong máy là USB | Đạt | máy không cắm USB, kết quả 0 ổ USB |
| TC26 | Xem trạng thái | Đạt | RUNNING, chế độ CHẶN TẤT CẢ |
| TC33 | Trạng thái hiện đủ 3 tầng chặn | Đạt | Tầng 1 driver USBSTOR: TẮT (chặn) | Tầng 2 Deny_All: BẬT | Tầng 3 cấm cài USB lưu trữ: BẬT |
| TC27 | Ghi nhật ký hoạt động | Đạt | C:\ProgramData\UsbGuard\usbguard.log |
| TC35 | Mật khẩu lưu bằng PBKDF2-SHA256 600.000 vòng, có muối | Đạt | pbkdf2-sha256 600000 |
| TC36 | Sai 5 lần liên tiếp: bị khoá, nhập đúng mật khẩu cũng bị từ chối tới khi hết khoá | Đạt | lần sai thứ 5: Sai mật khẩu quản trị. Đã sai 5 lần liên tiếp, thử lại sau 30 giây. | nhập đúng khi đang khoá: mã 3 |
| TC37 | Hết 30 giây khoá: đúng mật khẩu dùng lại được, bộ đếm sai về 0 | Đạt | mã 0, số lần sai còn lại 0 |
| TC28 | Gỡ với sai mật khẩu bị từ chối | Đạt | mã 3, trạng thái Running |
| TC29 | Gỡ đúng mật khẩu: dịch vụ tự dừng và bị xoá | Đạt | mất 3695 ms, sc query trả 1060 (không còn dịch vụ) |
| TC30 | Trả lại mặc định Windows sau khi gỡ | Đạt |  |
| TC34 | Gỡ cài đặt chỉ xoá mục của UsbGuard, giữ chính sách có sẵn của công ty | Đạt | còn mục UsbGuard: 0, DenyDeviceIDs = 1, mục công ty: USB\VID_DEAD&PID_BEEF |

## Nhật ký chạy
```
=== KIỂM THỬ TÍCH HỢP USBGUARD ===
Máy: runnervmhh3zg | Microsoft Windows Server 2022 Datacenter 10.0.20348 | 2026-11-21 08:27:59
Chạy bằng: runnervmhh3zg\runneradmin
USBSTOR trước khi cài: Start = 3
Chính sách có sẵn của 'công ty': DenyDeviceIDs\1 = USB\VID_DEAD&PID_BEEF

--- TC01 Cài đặt dịch vụ ---
> UsbGuard.exe install ********   (mã thoát 0)
  Đã cài đặt và khởi động dịch vụ UsbGuard.
  Kiểm tra: UsbGuard.exe status
[ĐẠT] TC01 Cài đặt, dịch vụ chạy — mã thoát 0, trạng thái Running
[ĐẠT] TC02 Khởi động tự động cùng Windows — StartType = Automatic
> sc.exe qfailure UsbGuard   (mã thoát 0)
  [SC] QueryServiceConfig2 SUCCESS
  SERVICE_NAME: UsbGuard
  RESET_PERIOD (in seconds)    : 86400
  REBOOT_MESSAGE               :
  COMMAND_LINE                 :
  FAILURE_ACTIONS              : RESTART -- Delay = 5000 milliseconds.
  RESTART -- Delay = 30000 milliseconds.
[ĐẠT] TC03 Cấu hình tự khởi động lại khi bị kill — sc qfailure có RESTART
> sc.exe qc UsbGuard   (mã thoát 0)
  [SC] QueryServiceConfig SUCCESS
  SERVICE_NAME: UsbGuard
  TYPE               : 10  WIN32_OWN_PROCESS
  START_TYPE         : 2   AUTO_START
  ERROR_CONTROL      : 1   NORMAL
  BINARY_PATH_NAME   : C:\Program Files\UsbGuard\UsbGuard.exe
  LOAD_ORDER_GROUP   :
  TAG                : 0
  DISPLAY_NAME       : UsbGuard - Chan USB Flash Disk
  DEPENDENCIES       :
  SERVICE_START_NAME : LocalSystem
[ĐẠT] TC04 Chạy dưới tài khoản LocalSystem — SERVICE_START_NAME = LocalSystem

--- TC05 Chặn driver lưu trữ USB ---
[ĐẠT] TC05 USBSTOR bị tắt (Start = 4) — Start = 4, sau 2 ms
[ĐẠT] TC06 Chính sách Removable Storage Deny_All = 1 — Deny_All = 1
--- TC07 Sửa tay registry, dịch vụ phải tự khoá lại ---
  Đã đặt tay USBSTOR Start = 3
[ĐẠT] TC07 Tự sửa khi registry bị đổi tay — khôi phục Start = 4 sau 1311 ms

--- TC31 Tầng 3: Device Installation Restrictions ---
[ĐẠT] TC31 Tầng 3: cấm cài thiết bị lớp USB Mass Storage, giữ nguyên mục của công ty — DenyDeviceIDs = 1, mục UsbGuard: USB\Class_08&SubClass_06&Prot_50, USB\Class_08&SubClass_06&Prot_62, USB\Class_08; mục công ty còn: USB\VID_DEAD&PID_BEEF
  Đã xoá tay mục UsbGuard3 (USB\Class_08)
[ĐẠT] TC32 Tầng 3 tự sửa khi bị xoá tay — khôi phục sau 1989 ms

--- TC08 Administrator thử dừng dịch vụ ---
> sc.exe stop UsbGuard   (mã thoát 1052)
  [SC] ControlService FAILED 1052:
  The requested control is not valid for this service.
[ĐẠT] TC08 Admin "sc stop" bị từ chối — mã 1052 (1052 = dịch vụ không nhận lệnh Stop), trạng thái Running
> Stop-Service UsbGuard  =>  Service 'UsbGuard - Chan USB Flash Disk (UsbGuard)' cannot be stopped due to the following error: Cannot stop 'UsbGuard' service on computer '.'.
[ĐẠT] TC09 Admin Stop-Service (PowerShell) bị từ chối — trạng thái Running
> taskkill.exe /F /PID 1040   (mã thoát 0)
  SUCCESS: The process with PID 1040 has been terminated.
[ĐẠT] TC10 Bị kill tiến trình thì Windows tự chạy lại — PID 1040 -> 2648, chạy lại sau 5398 ms

--- TC11 Người dùng thường (không phải Administrator) ---
  Đã tạo tài khoản thường 'ugthuong' (nhóm Users).
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] sc.exe stop UsbGuard   (mã thoát 5)
  runnervmhh3zg\ugthuong
  [SC] OpenService FAILED 5:
  Access is denied.
[ĐẠT] TC11 User thường "sc stop" bị từ chối quyền — mã 5 (5 = Access is denied)
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] sc.exe config UsbGuard start= disabled   (mã thoát 5)
  runnervmhh3zg\ugthuong
  [SC] OpenService FAILED 5:
  Access is denied.
[ĐẠT] TC12 User thường không đổi được kiểu khởi động — mã 5
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] sc.exe delete UsbGuard   (mã thoát 5)
  runnervmhh3zg\ugthuong
  [SC] OpenService FAILED 5:
  Access is denied.
[ĐẠT] TC13 User thường không xoá được dịch vụ — mã 5
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] reg.exe query HKLM\SOFTWARE\UsbGuard   (mã thoát 1)
  runnervmhh3zg\ugthuong
  ERROR: Access is denied.
[ĐẠT] TC14 User thường không đọc được cấu hình/mã băm mật khẩu — mã 1
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] UsbGuard.exe uninstall ********   (mã thoát 5)
  runnervmhh3zg\ugthuong
  Cần chạy với quyền Administrator.
[ĐẠT] TC15 User thường gỡ cài đặt bị từ chối (kể cả biết mật khẩu) — mã 5
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] reg.exe add HKLM\SYSTEM\CurrentControlSet\Services\USBSTOR /v Start /t REG_DWORD /d 3 /f   (mã thoát 1)
  runnervmhh3zg\ugthuong
  ERROR: Access is denied.
[ĐẠT] TC16 User thường không mở lại được driver USB — mã 1

--- TC17 Chức năng quản trị (Administrator) ---
> UsbGuard.exe pause 1 sai-mat-khau-123   (mã thoát 3)
  Sai mật khẩu quản trị.
[ĐẠT] TC17 Tạm dừng với sai mật khẩu bị từ chối — mã 3
> UsbGuard.exe pause 1 ********   (mã thoát 0)
  Đã tạm dừng chặn USB trong 1 phút.
[ĐẠT] TC18 Tạm dừng đúng mật khẩu: mở lại USB — USBSTOR Start = 3, sau 1203 ms
> UsbGuard.exe resume ********   (mã thoát 0)
  Đã bật lại chặn USB.
[ĐẠT] TC19 Bật lại chặn — USBSTOR Start = 4, sau 1858 ms
> UsbGuard.exe whitelist add VID_0951&PID_1666 ********   (mã thoát 0)
  OK.
[ĐẠT] TC20 Có whitelist: chuyển sang chế độ danh sách cho phép — driver mở để USB được phép chạy, sau 1974 ms
> UsbGuard.exe whitelist list   (mã thoát 0)
  1 thiết bị trong whitelist:
    - VID_0951&PID_1666
[ĐẠT] TC21 Xem whitelist — có VID_0951&PID_1666
> UsbGuard.exe whitelist remove VID_0951&PID_1666 ********   (mã thoát 0)
  OK.
[ĐẠT] TC22 Xoá whitelist: quay lại chặn tất cả — sau 1966 ms
> UsbGuard.exe passwd ******** MatKhauMoi@2026   (mã thoát 0)
  Đã đổi mật khẩu.
> UsbGuard.exe passwd MatKhauMoi@2026 ********   (mã thoát 0)
  Đã đổi mật khẩu.
[ĐẠT] TC23 Đổi mật khẩu quản trị — đổi sang mật khẩu mới rồi đổi lại
> UsbGuard.exe devices --all   (mã thoát 0)
  Ổ đĩa đang có mặt: 2
  - Msft Virtual Disk  [bus SAS]
      SCSI\DISK&VEN_MSFT&PROD_VIRTUAL_DISK\5&394B69D0&0&000001
      VMBUS\{BA6163D9-04A1-4D29-B605-72E2FFB1DC7F}\{F8B3781A-1E82-4818-A1C3-63D806EC15BB}
  - Msft Virtual Disk  [bus SAS]
      SCSI\DISK&VEN_MSFT&PROD_VIRTUAL_DISK\5&394B69D0&0&000000
      VMBUS\{BA6163D9-04A1-4D29-B605-72E2FFB1DC7F}\{F8B3781A-1E82-4818-A1C3-63D806EC15BB}
[ĐẠT] TC24 Liệt kê ổ đĩa qua SetupAPI + IOCTL (gọi API Windows thật) — đọc được loại bus của từng ổ
> UsbGuard.exe devices   (mã thoát 0)
  Ổ USB đang cắm: 0
  Thiết bị USB lưu trữ đang cắm (kể cả đang bị chặn): 0
[ĐẠT] TC25 Không nhận nhầm ổ cứng trong máy là USB — máy không cắm USB, kết quả 0 ổ USB
> UsbGuard.exe status   (mã thoát 0)
  SERVICE_NAME: UsbGuard 
          TYPE               : 10  WIN32_OWN_PROCESS  
          STATE              : 4  RUNNING 
                                  (NOT_STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
          WIN32_EXIT_CODE    : 0  (0x0)
          SERVICE_EXIT_CODE  : 0  (0x0)
          CHECKPOINT         : 0x0
          WAIT_HINT          : 0x0
  Trạng thái chặn: ĐANG BẬT, chế độ CHẶN TẤT CẢ
  Whitelist (0 mục):
  Tầng 1 driver USBSTOR: TẮT (chặn) | Tầng 2 Deny_All: BẬT | Tầng 3 cấm cài USB lưu trữ: BẬT
[ĐẠT] TC26 Xem trạng thái — RUNNING, chế độ CHẶN TẤT CẢ
[ĐẠT] TC33 Trạng thái hiện đủ 3 tầng chặn — Tầng 1 driver USBSTOR: TẮT (chặn) | Tầng 2 Deny_All: BẬT | Tầng 3 cấm cài USB lưu trữ: BẬT
[ĐẠT] TC27 Ghi nhật ký hoạt động — C:\ProgramData\UsbGuard\usbguard.log

--- TC35 Chống dò mật khẩu ---
[ĐẠT] TC35 Mật khẩu lưu bằng PBKDF2-SHA256 600.000 vòng, có muối — pbkdf2-sha256 600000
> UsbGuard.exe pause 1 sai-mat-khau-1   (mã thoát 3)
  Sai mật khẩu quản trị.
> UsbGuard.exe pause 1 sai-mat-khau-2   (mã thoát 3)
  Sai mật khẩu quản trị.
> UsbGuard.exe pause 1 sai-mat-khau-3   (mã thoát 3)
  Sai mật khẩu quản trị.
> UsbGuard.exe pause 1 sai-mat-khau-4   (mã thoát 3)
  Sai mật khẩu quản trị.
> UsbGuard.exe pause 1 sai-mat-khau-5   (mã thoát 3)
  Sai mật khẩu quản trị. Đã sai 5 lần liên tiếp, thử lại sau 30 giây.
> UsbGuard.exe pause 1 ********   (mã thoát 3)
  Nhập sai mật khẩu quá nhiều lần. Thử lại sau 30 giây.
[ĐẠT] TC36 Sai 5 lần liên tiếp: bị khoá, nhập đúng mật khẩu cũng bị từ chối tới khi hết khoá — lần sai thứ 5: Sai mật khẩu quản trị. Đã sai 5 lần liên tiếp, thử lại sau 30 giây. | nhập đúng khi đang khoá: mã 3
> UsbGuard.exe resume ********   (mã thoát 0)
  Đã bật lại chặn USB.
[ĐẠT] TC37 Hết 30 giây khoá: đúng mật khẩu dùng lại được, bộ đếm sai về 0 — mã 0, số lần sai còn lại 0

--- Đo tài nguyên dịch vụ trong 60 giây ---
  RAM (working set): trung bình 23.3 MB, cao nhất 23.6 MB; CPU trung bình 0 % (trên 4 lõi)

--- TC28 Gỡ cài đặt ---
> UsbGuard.exe uninstall sai-mat-khau-123   (mã thoát 3)
  Sai mật khẩu quản trị.
[ĐẠT] TC28 Gỡ với sai mật khẩu bị từ chối — mã 3, trạng thái Running
> UsbGuard.exe uninstall ********   (mã thoát 0)
  Đã gỡ cài đặt UsbGuard và khôi phục cấu hình USB mặc định của Windows.
> sc.exe query UsbGuard   (mã thoát 1060)
  [SC] EnumQueryServicesStatus:OpenService FAILED 1060:
  The specified service does not exist as an installed service.
[ĐẠT] TC29 Gỡ đúng mật khẩu: dịch vụ tự dừng và bị xoá — mất 3695 ms, sc query trả 1060 (không còn dịch vụ)
[ĐẠT] TC30 Trả lại mặc định Windows sau khi gỡ — 
[ĐẠT] TC34 Gỡ cài đặt chỉ xoá mục của UsbGuard, giữ chính sách có sẵn của công ty — còn mục UsbGuard: 0, DenyDeviceIDs = 1, mục công ty: USB\VID_DEAD&PID_BEEF

=== KẾT QUẢ: 37/37 ca ĐẠT ===
```

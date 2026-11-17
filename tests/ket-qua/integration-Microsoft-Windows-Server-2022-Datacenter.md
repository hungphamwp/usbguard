# Kết quả kiểm thử tích hợp UsbGuard — Microsoft Windows Server 2022 Datacenter (10.0.20348)

Thời điểm: 2026-11-17 10:05:38 · Kết quả: **30/30 ca đạt**

| Mã | Ca kiểm thử | Kết quả | Chi tiết |
|---|---|---|---|
| TC01 | Cài đặt, dịch vụ chạy | Đạt | mã thoát 0, trạng thái Running |
| TC02 | Khởi động tự động cùng Windows | Đạt | StartType = Automatic |
| TC03 | Cấu hình tự khởi động lại khi bị kill | Đạt | sc qfailure có RESTART |
| TC04 | Chạy dưới tài khoản LocalSystem | Đạt | SERVICE_START_NAME = LocalSystem |
| TC05 | USBSTOR bị tắt (Start = 4) | Đạt | Start = 4, sau 1 ms |
| TC06 | Chính sách Removable Storage Deny_All = 1 | Đạt | Deny_All = 1 |
| TC07 | Tự sửa khi registry bị đổi tay | Đạt | khôi phục Start = 4 sau 1089 ms |
| TC08 | Admin "sc stop" bị từ chối | Đạt | mã 1052 (1052 = dịch vụ không nhận lệnh Stop), trạng thái Running |
| TC09 | Admin Stop-Service (PowerShell) bị từ chối | Đạt | trạng thái Running |
| TC10 | Bị kill tiến trình thì Windows tự chạy lại | Đạt | PID 5320 -> 744, chạy lại sau 5320 ms |
| TC11 | User thường "sc stop" bị từ chối quyền | Đạt | mã 5 (5 = Access is denied) |
| TC12 | User thường không đổi được kiểu khởi động | Đạt | mã 5 |
| TC13 | User thường không xoá được dịch vụ | Đạt | mã 5 |
| TC14 | User thường không đọc được cấu hình/mã băm mật khẩu | Đạt | mã 1 |
| TC15 | User thường gỡ cài đặt bị từ chối (kể cả biết mật khẩu) | Đạt | mã 5 |
| TC16 | User thường không mở lại được driver USB | Đạt | mã 1 |
| TC17 | Tạm dừng với sai mật khẩu bị từ chối | Đạt | mã 3 |
| TC18 | Tạm dừng đúng mật khẩu: mở lại USB | Đạt | USBSTOR Start = 3, sau 879 ms |
| TC19 | Bật lại chặn | Đạt | USBSTOR Start = 4, sau 1417 ms |
| TC20 | Có whitelist: chuyển sang chế độ danh sách cho phép | Đạt | driver mở để USB được phép chạy, sau 1414 ms |
| TC21 | Xem whitelist | Đạt | có VID_0951&PID_1666 |
| TC22 | Xoá whitelist: quay lại chặn tất cả | Đạt | sau 1306 ms |
| TC23 | Đổi mật khẩu quản trị | Đạt | đổi sang mật khẩu mới rồi đổi lại |
| TC24 | Liệt kê ổ đĩa qua SetupAPI + IOCTL (gọi API Windows thật) | Đạt | đọc được loại bus của từng ổ |
| TC25 | Không nhận nhầm ổ cứng trong máy là USB | Đạt | máy không cắm USB, kết quả 0 ổ USB |
| TC26 | Xem trạng thái | Đạt | RUNNING, chế độ CHẶN TẤT CẢ |
| TC27 | Ghi nhật ký hoạt động | Đạt | C:\ProgramData\UsbGuard\usbguard.log |
| TC28 | Gỡ với sai mật khẩu bị từ chối | Đạt | mã 3, trạng thái Running |
| TC29 | Gỡ đúng mật khẩu: dịch vụ tự dừng và bị xoá | Đạt | mất 2801 ms, sc query trả 1060 (không còn dịch vụ) |
| TC30 | Trả lại mặc định Windows sau khi gỡ | Đạt | USBSTOR Start = 3, Deny_All = , không còn khoá cấu hình và thư mục cài |

## Nhật ký chạy
```
=== KIỂM THỬ TÍCH HỢP USBGUARD ===
Máy: runnervm9zap3 | Microsoft Windows Server 2022 Datacenter 10.0.20348 | 2026-11-17 10:03:50
Chạy bằng: runnervm9zap3\runneradmin
USBSTOR trước khi cài: Start = 3

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
[ĐẠT] TC05 USBSTOR bị tắt (Start = 4) — Start = 4, sau 1 ms
[ĐẠT] TC06 Chính sách Removable Storage Deny_All = 1 — Deny_All = 1
--- TC07 Sửa tay registry, dịch vụ phải tự khoá lại ---
  Đã đặt tay USBSTOR Start = 3
[ĐẠT] TC07 Tự sửa khi registry bị đổi tay — khôi phục Start = 4 sau 1089 ms

--- TC08 Administrator thử dừng dịch vụ ---
> sc.exe stop UsbGuard   (mã thoát 1052)
  [SC] ControlService FAILED 1052:
  The requested control is not valid for this service.
[ĐẠT] TC08 Admin "sc stop" bị từ chối — mã 1052 (1052 = dịch vụ không nhận lệnh Stop), trạng thái Running
> Stop-Service UsbGuard  =>  Service 'UsbGuard - Chan USB Flash Disk (UsbGuard)' cannot be stopped due to the following error: Cannot stop 'UsbGuard' service on computer '.'.
[ĐẠT] TC09 Admin Stop-Service (PowerShell) bị từ chối — trạng thái Running
> taskkill.exe /F /PID 5320   (mã thoát 0)
  SUCCESS: The process with PID 5320 has been terminated.
[ĐẠT] TC10 Bị kill tiến trình thì Windows tự chạy lại — PID 5320 -> 744, chạy lại sau 5320 ms

--- TC11 Người dùng thường (không phải Administrator) ---
  Đã tạo tài khoản thường 'ugthuong' (nhóm Users).
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] sc.exe stop UsbGuard   (mã thoát 5)
  runnervm9zap3\ugthuong
  [SC] OpenService FAILED 5:
  Access is denied.
[ĐẠT] TC11 User thường "sc stop" bị từ chối quyền — mã 5 (5 = Access is denied)
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] sc.exe config UsbGuard start= disabled   (mã thoát 5)
  runnervm9zap3\ugthuong
  [SC] OpenService FAILED 5:
  Access is denied.
[ĐẠT] TC12 User thường không đổi được kiểu khởi động — mã 5
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] sc.exe delete UsbGuard   (mã thoát 5)
  runnervm9zap3\ugthuong
  [SC] OpenService FAILED 5:
  Access is denied.
[ĐẠT] TC13 User thường không xoá được dịch vụ — mã 5
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] reg.exe query HKLM\SOFTWARE\UsbGuard   (mã thoát 1)
  runnervm9zap3\ugthuong
  ERROR: Access is denied.
[ĐẠT] TC14 User thường không đọc được cấu hình/mã băm mật khẩu — mã 1
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] UsbGuard.exe uninstall ********   (mã thoát 5)
  runnervm9zap3\ugthuong
  Cần chạy với quyền Administrator.
[ĐẠT] TC15 User thường gỡ cài đặt bị từ chối (kể cả biết mật khẩu) — mã 5
  (tiến trình user thường kết thúc, mã 0)
> [ugthuong] reg.exe add HKLM\SYSTEM\CurrentControlSet\Services\USBSTOR /v Start /t REG_DWORD /d 3 /f   (mã thoát 1)
  runnervm9zap3\ugthuong
  ERROR: Access is denied.
[ĐẠT] TC16 User thường không mở lại được driver USB — mã 1

--- TC17 Chức năng quản trị (Administrator) ---
> UsbGuard.exe pause 1 sai-mat-khau-123   (mã thoát 3)
  Sai mật khẩu quản trị.
[ĐẠT] TC17 Tạm dừng với sai mật khẩu bị từ chối — mã 3
> UsbGuard.exe pause 1 ********   (mã thoát 0)
  Đã tạm dừng chặn USB trong 1 phút.
[ĐẠT] TC18 Tạm dừng đúng mật khẩu: mở lại USB — USBSTOR Start = 3, sau 879 ms
> UsbGuard.exe resume ********   (mã thoát 0)
  Đã bật lại chặn USB.
[ĐẠT] TC19 Bật lại chặn — USBSTOR Start = 4, sau 1417 ms
> UsbGuard.exe whitelist add VID_0951&PID_1666 ********   (mã thoát 0)
  OK.
[ĐẠT] TC20 Có whitelist: chuyển sang chế độ danh sách cho phép — driver mở để USB được phép chạy, sau 1414 ms
> UsbGuard.exe whitelist list   (mã thoát 0)
  1 thiết bị trong whitelist:
    - VID_0951&PID_1666
[ĐẠT] TC21 Xem whitelist — có VID_0951&PID_1666
> UsbGuard.exe whitelist remove VID_0951&PID_1666 ********   (mã thoát 0)
  OK.
[ĐẠT] TC22 Xoá whitelist: quay lại chặn tất cả — sau 1306 ms
> UsbGuard.exe passwd ******** MatKhauMoi@2026   (mã thoát 0)
  Đã đổi mật khẩu.
> UsbGuard.exe passwd MatKhauMoi@2026 ********   (mã thoát 0)
  Đã đổi mật khẩu.
[ĐẠT] TC23 Đổi mật khẩu quản trị — đổi sang mật khẩu mới rồi đổi lại
> UsbGuard.exe devices --all   (mã thoát 0)
  Ổ đĩa đang có mặt: 2
  - Virtual_Disk NVME Premium  [bus NVMe]
      SCSI\DISK&VEN_NVME&PROD_MSFT_NVME_ACCELE\6&CA10229&0&000000
      PCI\VEN_1414&DEV_00A9&SUBSYS_00001414&REV_00\5&2B9FD912&0&0
      62AA_8BCF_A568_4137_9D36_69C0_2A40_2701.
  - Microsoft NVMe Direct Disk v2  [bus NVMe]
      SCSI\DISK&VEN_NVME&PROD_MICROSOFT_NVME_D\6&23CBF041&0&000000
      PCI\VEN_1414&DEV_B111&SUBSYS_FFFF1414&REV_01\5&1538631A&0&0
      B08F_06C1_A9F0_5958_86CD_CB8F_D501_2578.
[ĐẠT] TC24 Liệt kê ổ đĩa qua SetupAPI + IOCTL (gọi API Windows thật) — đọc được loại bus của từng ổ
> UsbGuard.exe devices   (mã thoát 0)
  Ổ USB đang cắm: 0
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
[ĐẠT] TC26 Xem trạng thái — RUNNING, chế độ CHẶN TẤT CẢ
[ĐẠT] TC27 Ghi nhật ký hoạt động — C:\ProgramData\UsbGuard\usbguard.log

--- Đo tài nguyên dịch vụ trong 60 giây ---
  RAM (working set): trung bình 21.9 MB, cao nhất 22.1 MB; CPU trung bình 0 % (trên 4 lõi)

--- TC28 Gỡ cài đặt ---
> UsbGuard.exe uninstall sai-mat-khau-123   (mã thoát 3)
  Sai mật khẩu quản trị.
[ĐẠT] TC28 Gỡ với sai mật khẩu bị từ chối — mã 3, trạng thái Running
> UsbGuard.exe uninstall ********   (mã thoát 0)
  Đã gỡ cài đặt UsbGuard và khôi phục cấu hình USB mặc định của Windows.
> sc.exe query UsbGuard   (mã thoát 1060)
  [SC] EnumQueryServicesStatus:OpenService FAILED 1060:
  The specified service does not exist as an installed service.
[ĐẠT] TC29 Gỡ đúng mật khẩu: dịch vụ tự dừng và bị xoá — mất 2801 ms, sc query trả 1060 (không còn dịch vụ)
[ĐẠT] TC30 Trả lại mặc định Windows sau khi gỡ — USBSTOR Start = 3, Deny_All = , không còn khoá cấu hình và thư mục cài

=== KẾT QUẢ: 30/30 ca ĐẠT ===
```

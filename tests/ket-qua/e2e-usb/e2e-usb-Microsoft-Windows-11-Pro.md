# Kiểm thử cắm USB thật: Microsoft Windows 11 Pro

Phiên bản Windows: 10.0.26200 · Thời điểm: 2026-11-21 00:48:45 · Kết quả: **20/20 ca đạt**

USB: ổ QEMU usb-storage cắm nóng vào cổng xHCI (Windows nhận là USB flash disk thật: bus USB, driver USBSTOR).

| Mã | Ca kiểm thử | Kết quả | Chi tiết |
|---|---|---|---|
| E01 | Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file | Đạt | bus=USB, có ký tự ổ sau 3 ms, ghi file sau 3 ms |
| E02 | Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu | Đạt | mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True |
| E03 | Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) | Đạt | thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE |
| E04 | Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng | Đạt | 2026-11-21 00:43:29 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device / ID: USB\VID_46F4&PID_0001\UGBLOCK0001 |
| E05 | Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận | Đạt | trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK |
| E06 | Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra | Đạt | ghi được sau 146 ms kể từ lệnh tạm dừng |
| E07 | Bật lại chặn khi USB đang mở file: USB vẫn bị chặn | Đạt | còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá:  |
| E08 | Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial | Đạt |  |
| E09 | Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) | Đạt | ghi được sau 297 ms |
| E10 | Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây | Đạt | ổ xuất hiện không lần nào, ghi được: False |
| E11 | Danh sách cho phép: USB được phép vẫn dùng bình thường | Đạt |  |
| E12 | Rút USB được phép ra cắm lại vẫn dùng được | Đạt | ghi được sau 0 ms |
| E13 | Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay | Đạt | còn ổ: False |
| E18 | USB bị chặn khi đang cắm (Windows đã tháo) vẫn hiện trong danh sách thiết bị | Đạt |  |
| E19 | Cho phép lại USB đang bị tháo: tự hiện lại trong This PC, không cần rút ra cắm lại | Đạt | ghi được sau 1591 ms; nhật ký: 2026-11-21 00:46:42 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device / USB\VID_46F4&PID_0001\UGALLOW0002 / cổng 3 |
| E20 | Tạm dừng khi USB đang bị tháo: tự dùng được, không cần rút ra cắm lại | Đạt | ghi được sau 1834 ms |
| E14 | Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được | Đạt | dịch vụ: Running |
| E15 | Trình gỡ của bộ cài, sai mật khẩu: không gỡ được | Đạt |  |
| E16 | Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB | Đạt | USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False |
| E17 | Sau khi gỡ: cắm USB dùng lại bình thường | Đạt | ghi được sau 0 ms |

## Nhật ký chạy
```
00:42:28.407 === KIỂM THỬ CẮM USB THẬT (QEMU usb-storage) ===
00:42:28.555 Máy: WIN-L7J5UNLU7SN | Microsoft Windows 11 Pro 10.0.26200 | quyền Administrator: True
00:42:54.487   [host] plug A
00:42:55.288   theo dõi USB A {"disk_dau":3,"disk_cuoi":3,"vol_dau":3,"vol_cuoi":3,"ghi_duoc":true,"ghi_ms":3,"con_disk":true,"con_vol":true}
00:43:02.097 [ĐẠT] E01 Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file — bus=USB, có ký tự ổ sau 3 ms, ghi file sau 3 ms
00:43:08.122   [host] shot e01-truoc-khi-cai
00:43:13.313   [host] unplug A
00:43:27.689 [ĐẠT] E02 Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu — mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True
00:43:33.928   [host] plug A
00:43:49.003   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:43:55.156   [host] shot e03-thong-bao-chan-usb
00:43:55.249 [ĐẠT] E03 Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) — thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE
00:43:55.313 [ĐẠT] E04 Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng — 2026-11-21 00:43:29 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device | ID: USB\VID_46F4&PID_0001\UGBLOCK0001
00:44:00.673   [host] plug K
00:44:12.902 [ĐẠT] E05 Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận — trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK
00:44:18.081   [host] unplug K
00:44:22.066   > UsbGuard.exe pause 10 MatKhauE2E@2026 (mã 0)
00:44:22.345   theo dõi USB A {"disk_dau":146,"disk_cuoi":146,"vol_dau":146,"vol_cuoi":146,"ghi_duoc":true,"ghi_ms":146,"con_disk":true,"con_vol":true}
00:44:22.373 [ĐẠT] E06 Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra — ghi được sau 146 ms kể từ lệnh tạm dừng
00:44:24.965   > UsbGuard.exe resume MatKhauE2E@2026 (mã 0)
00:44:26.632   theo dõi USB A {"disk_dau":0,"disk_cuoi":1476,"vol_dau":0,"vol_cuoi":1476,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:44:26.670   nhật ký UsbGuard: 2026-11-21 00:43:21 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\1-0000:00:02.0-2&0 ; USB\VID_46F4&PID_0001\1-0000:00:02.0-2 ; 1-0000:00:02.0-2 2026-11-21 00:44:26 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\1-0000:00:02.0-2&0 ; USB\VID_46F4&PID_0001\1-0000:00:02.0-2 ; 1-0000:00:02.0-2
00:44:26.702 [ĐẠT] E07 Bật lại chặn khi USB đang mở file: USB vẫn bị chặn — còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá: 
00:44:31.887   [host] unplug A
00:44:39.043   [host] plug B
00:44:45.272   > UsbGuard.exe devices (mã 0)
00:44:45.304 ß╗ö USB ─æang cß║»m: 0
Thiß║┐t bß╗ï USB l╞░u trß╗» ─æang cß║»m (kß╗â cß║ú ─æang bß╗ï chß║╖n): 2
- QEMU USB HARDDRIVE  [bß╗ï chß║╖n (m├ú 1)]
    ID: USB\VID_46F4&PID_0001\UGALLOW0002
    Gß╗úi ├╜ th├¬m whitelist: UGALLOW0002
    Cß╗òng: 4 tr├¬n hub USB\ROOT_HUB30\4&1D3628F5&0&0
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 47)]
    ID: USB\VID_46F4&PID_0001\1-0000:00:02.0-2
    Gß╗úi ├╜ th├¬m whitelist: 1-0000:00:02.0-2
    Cß╗òng: 2 tr├¬n hub USB\ROOT_HUB30\4&10DC1CB6&0&0
00:44:45.383 [ĐẠT] E08 Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial — 
00:44:48.106   > UsbGuard.exe whitelist add UGALLOW0002 MatKhauE2E@2026 (mã 0)
00:44:48.494   theo dõi USB B {"disk_dau":297,"disk_cuoi":297,"vol_dau":297,"vol_cuoi":297,"ghi_duoc":true,"ghi_ms":297,"con_disk":true,"con_vol":true}
00:44:48.525 [ĐẠT] E09 Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) — ghi được sau 297 ms
00:44:54.450   [host] plug A
00:45:34.556   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:45:34.626   nhật ký UsbGuard: 2026-11-21 00:44:50 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGBLOCK0001&0 ; USB\VID_46F4&PID_0001\UGBLOCK0001 ; UGBLOCK0001
00:45:40.666   [host] shot e10-whitelist-chan-usb-la
00:45:40.697 [ĐẠT] E10 Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây — ổ xuất hiện không lần nào, ghi được: False
00:45:40.756 [ĐẠT] E11 Danh sách cho phép: USB được phép vẫn dùng bình thường — 
00:45:55.504   [host] shot gui-quan-ly
00:46:00.699   [host] unplug A
00:46:07.869   [host] unplug B
00:46:15.054   [host] plug B
00:46:31.505   theo dõi USB B {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
00:46:31.543 [ĐẠT] E12 Rút USB được phép ra cắm lại vẫn dùng được — ghi được sau 0 ms
00:46:33.452   > UsbGuard.exe whitelist remove UGALLOW0002 MatKhauE2E@2026 (mã 0)
00:46:34.754   theo dõi USB B {"disk_dau":0,"disk_cuoi":947,"vol_dau":0,"vol_cuoi":1089,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:46:34.801 [ĐẠT] E13 Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay — còn ổ: False
00:46:38.997   > UsbGuard.exe devices (mã 0)
00:46:39.019 ß╗ö USB ─æang cß║»m: 0
Thiß║┐t bß╗ï USB l╞░u trß╗» ─æang cß║»m (kß╗â cß║ú ─æang bß╗ï chß║╖n): 2
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 47)]
    ID: USB\VID_46F4&PID_0001\UGALLOW0002
    Gß╗úi ├╜ th├¬m whitelist: UGALLOW0002
    Cß╗òng: 3 tr├¬n hub USB\ROOT_HUB30\4&1D3628F5&0&0
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 47)]
    ID: USB\VID_46F4&PID_0001\1-0000:00:02.0-2
    Gß╗úi ├╜ th├¬m whitelist: 1-0000:00:02.0-2
    Cß╗òng: 2 tr├¬n hub USB\ROOT_HUB30\4&10DC1CB6&0&0
00:46:39.059 [ĐẠT] E18 USB bị chặn khi đang cắm (Windows đã tháo) vẫn hiện trong danh sách thiết bị — 
00:46:41.127   > UsbGuard.exe whitelist add UGALLOW0002 MatKhauE2E@2026 (mã 0)
00:46:42.833   theo dõi USB B {"disk_dau":1591,"disk_cuoi":1591,"vol_dau":1591,"vol_cuoi":1591,"ghi_duoc":true,"ghi_ms":1591,"con_disk":true,"con_vol":true}
00:46:42.864   nhật ký dịch vụ: 2026-11-21 00:44:36 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 1): QEMU USB HARDDRIVE | ID: USB\VID_46F4&PID_0001\UGALLOW0002 || 2026-11-21 00:44:48 [INFO] Thêm whitelist: UGALLOW0002 (qua CLI). || 2026-11-21 00:44:48 [INFO] Chế độ: DANH SÁCH CHO PHÉP (1 mục) || 2026-11-21 00:44:48 [INFO] Cho Windows cài lại USB từng bị cấm cài (đang cắm): USB\VID_46F4&PID_0001\UGALLOW0002 (mã 0) || 2026-11-21 00:44:50 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGBLOCK0001&0 ; USB\VID_46F4&PID_0001\UGBLOCK0001 ; UGBLOCK0001 || 2026-11-21 00:46:33 [INFO] Xoá whitelist: UGALLOW0002 (qua CLI). || 2026-11-21 00:46:34 [INFO] Chế độ: CHẶN TẤT CẢ || 2026-11-21 00:46:34 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGALLOW0002&0 ; USB\VID_46F4&PID_0001\UGALLOW0002 ; UGALLOW0002 || 2026-11-21 00:46:41 [INFO] Thêm whitelist: UGALLOW0002 (qua CLI). || 2026-11-21 00:46:42 [INFO] Chế độ: DANH SÁCH CHO PHÉP (1 mục) || 2026-11-21 00:46:42 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\UGALLOW0002 | cổng 3 || 
00:46:43.460   > UsbGuard.exe devices (mã 0)
00:46:43.482 ß╗ö USB ─æang cß║»m: 1
- QEMU QEMU HARDDISK  [bus USB]
    USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGALLOW0002&0
    USB\VID_46F4&PID_0001\UGALLOW0002
    UGALLOW0002
Thiß║┐t bß╗ï USB l╞░u trß╗» ─æang cß║»m (kß╗â cß║ú ─æang bß╗ï chß║╖n): 2
- USB Mass Storage Device  [─æ╞░ß╗úc ph├⌐p]
    ID: USB\VID_46F4&PID_0001\UGALLOW0002
    Gß╗úi ├╜ th├¬m whitelist: UGALLOW0002
    Cß╗òng: 3 tr├¬n hub USB\ROOT_HUB30\4&1D3628F5&0&0
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 47)]
    ID: USB\VID_46F4&PID_0001\1-0000:00:02.0-2
    Gß╗úi ├╜ th├¬m whitelist: 1-0000:00:02.0-2
    Cß╗òng: 2 tr├¬n hub USB\ROOT_HUB30\4&10DC1CB6&0&0
00:46:43.512 [ĐẠT] E19 Cho phép lại USB đang bị tháo: tự hiện lại trong This PC, không cần rút ra cắm lại — ghi được sau 1591 ms; nhật ký: 2026-11-21 00:46:42 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\UGALLOW0002 | cổng 3
00:46:45.393   > UsbGuard.exe whitelist remove UGALLOW0002 MatKhauE2E@2026 (mã 0)
00:46:46.677   theo dõi USB B {"disk_dau":0,"disk_cuoi":1074,"vol_dau":0,"vol_cuoi":1074,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:46:48.958   > UsbGuard.exe pause 5 MatKhauE2E@2026 (mã 0)
00:46:51.778   theo dõi USB B {"disk_dau":1834,"disk_cuoi":1834,"vol_dau":1834,"vol_cuoi":1834,"ghi_duoc":true,"ghi_ms":1834,"con_disk":true,"con_vol":true}
00:46:51.802   nhật ký dịch vụ: 2026-11-21 00:46:42 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\UGALLOW0002 | cổng 3 || 2026-11-21 00:46:45 [INFO] Xoá whitelist: UGALLOW0002 (qua CLI). || 2026-11-21 00:46:46 [INFO] Chế độ: CHẶN TẤT CẢ || 2026-11-21 00:46:48 [INFO] Tạm dừng chặn USB trong 5 phút (qua CLI). || 2026-11-21 00:46:50 [INFO] Chế độ: TẠM DỪNG || 2026-11-21 00:46:50 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\UGALLOW0002 | cổng 3 || 2026-11-21 00:46:50 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\1-0000:00:02.0-2 | cổng 2 || 
00:46:51.820 [ĐẠT] E20 Tạm dừng khi USB đang bị tháo: tự dùng được, không cần rút ra cắm lại — ghi được sau 1834 ms
00:46:53.650   > UsbGuard.exe resume MatKhauE2E@2026 (mã 0)
00:47:13.143   theo dõi USB B {"disk_dau":0,"disk_cuoi":19264,"vol_dau":0,"vol_cuoi":19264,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:47:18.349   [host] unplug B
00:47:25.565   [host] plug A
00:47:38.622 [ĐẠT] E14 Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được — dịch vụ: Running
00:47:43.800   [host] unplug A
00:48:11.482 [ĐẠT] E15 Trình gỡ của bộ cài, sai mật khẩu: không gỡ được — 
00:48:21.628 [ĐẠT] E16 Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB — USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False
00:48:26.797   [host] plug A
00:48:26.866   theo dõi USB A {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
00:48:26.884 [ĐẠT] E17 Sau khi gỡ: cắm USB dùng lại bình thường — ghi được sau 0 ms
00:48:32.056   [host] unplug A
00:48:44.812   [host] shot setup-1-dieu-khoan
00:48:44.967   đã chụp giao diện bộ cài
00:48:45.092 === KẾT QUẢ: 20/20 ca ĐẠT ===
```

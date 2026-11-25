# Kiểm thử cắm USB thật: Microsoft Windows 11 Pro

Phiên bản Windows: 10.0.26200 · Thời điểm: 2026-11-25 04:22:35 · Kết quả: **21/21 ca đạt**

USB: ổ QEMU usb-storage cắm nóng vào cổng xHCI (Windows nhận là USB flash disk thật: bus USB, driver USBSTOR).

| Mã | Ca kiểm thử | Kết quả | Chi tiết |
|---|---|---|---|
| E01 | Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file | Đạt | bus=USB, có ký tự ổ sau 4 ms, ghi file sau 4 ms |
| E02 | Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu | Đạt | mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True |
| E03 | Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) | Đạt | thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE |
| E04 | Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng | Đạt | 2026-11-25 04:17:24 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device / ID: USB\VID_46F4&PID_0001\UGBLOCK0001 |
| E05 | Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận | Đạt | trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK |
| E06 | Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra | Đạt | ghi được sau 1577 ms kể từ lệnh tạm dừng |
| E07 | Bật lại chặn khi USB đang mở file: USB vẫn bị chặn | Đạt | còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá:  |
| E08 | Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial | Đạt |  |
| E09 | Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) | Đạt | ghi được sau 1443 ms |
| E10 | Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây | Đạt | ổ xuất hiện không lần nào, ghi được: False |
| E11 | Danh sách cho phép: USB được phép vẫn dùng bình thường | Đạt |  |
| E12 | Rút USB được phép ra cắm lại vẫn dùng được | Đạt | ghi được sau 0 ms |
| E13 | Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay | Đạt | còn ổ: False |
| E18 | USB bị chặn khi đang cắm (Windows đã tháo) vẫn hiện trong danh sách thiết bị | Đạt |  |
| E19 | Cho phép lại USB đang bị tháo: tự hiện lại trong This PC, không cần rút ra cắm lại | Đạt | ghi được sau 201 ms; nhật ký: 2026-11-25 04:20:27 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device / USB\VID_46F4&PID_0001\UGALLOW0002 / cổng 3 |
| E20 | Tạm dừng khi USB đang bị tháo: tự dùng được, không cần rút ra cắm lại | Đạt | ghi được sau 1161 ms |
| E14 | Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được | Đạt | dịch vụ: Running |
| E15 | Trình gỡ của bộ cài, sai mật khẩu: không gỡ được | Đạt |  |
| E16 | Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB | Đạt | USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False |
| E21 | Gỡ cài đặt khi USB đang cắm và bị chặn: USB tự dùng được, không cần rút ra cắm lại | Đạt | ghi được sau 0 ms |
| E17 | Sau khi gỡ: cắm USB dùng lại bình thường | Đạt | ghi được sau 0 ms |

## Nhật ký chạy
```
04:16:13.827 === KIỂM THỬ CẮM USB THẬT (QEMU usb-storage) ===
04:16:14.047 Máy: WIN-QIRESS7DQNQ | Microsoft Windows 11 Pro 10.0.26200 | quyền Administrator: True
04:16:40.062   [host] plug A
04:16:41.140   theo dõi USB A {"disk_dau":4,"disk_cuoi":4,"vol_dau":4,"vol_cuoi":4,"ghi_duoc":true,"ghi_ms":4,"con_disk":true,"con_vol":true}
04:16:50.335 [ĐẠT] E01 Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file — bus=USB, có ký tự ổ sau 4 ms, ghi file sau 4 ms
04:16:56.421   [host] shot e01-truoc-khi-cai
04:17:01.659   [host] unplug A
04:17:21.848 [ĐẠT] E02 Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu — mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True
04:17:28.327   [host] plug A
04:17:43.365   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
04:17:49.485   [host] shot e03-thong-bao-chan-usb
04:17:49.593 [ĐẠT] E03 Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) — thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE
04:17:49.677 [ĐẠT] E04 Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng — 2026-11-25 04:17:24 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device | ID: USB\VID_46F4&PID_0001\UGBLOCK0001
04:17:54.879   [host] plug K
04:18:07.267 [ĐẠT] E05 Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận — trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK
04:18:12.520   [host] unplug K
04:18:17.303   > UsbGuard.exe pause 10 MatKhauE2E@2026 (mã 0)
04:18:19.086   theo dõi USB A {"disk_dau":1577,"disk_cuoi":1577,"vol_dau":1577,"vol_cuoi":1577,"ghi_duoc":true,"ghi_ms":1577,"con_disk":true,"con_vol":true}
04:18:19.132 [ĐẠT] E06 Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra — ghi được sau 1577 ms kể từ lệnh tạm dừng
04:18:22.242   > UsbGuard.exe resume MatKhauE2E@2026 (mã 0)
04:18:23.319   theo dõi USB A {"disk_dau":0,"disk_cuoi":854,"vol_dau":0,"vol_cuoi":854,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
04:18:23.383   nhật ký UsbGuard: 2026-11-25 04:17:14 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\1-0000:00:02.0-2&0 ; USB\VID_46F4&PID_0001\1-0000:00:02.0-2 ; 1-0000:00:02.0-2 2026-11-25 04:18:22 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\1-0000:00:02.0-2&0 ; USB\VID_46F4&PID_0001\1-0000:00:02.0-2 ; 1-0000:00:02.0-2
04:18:23.439 [ĐẠT] E07 Bật lại chặn khi USB đang mở file: USB vẫn bị chặn — còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá: 
04:18:28.692   [host] unplug A
04:18:35.962   [host] plug B
04:18:42.274   > UsbGuard.exe devices (mã 0)
04:18:42.326 ß╗ö USB ─æang cß║»m: 0
Thiß║┐t bß╗ï USB l╞░u trß╗» ─æang cß║»m (kß╗â cß║ú ─æang bß╗ï chß║╖n): 2
- QEMU USB HARDDRIVE  [bß╗ï chß║╖n (m├ú 1)]
    ID: USB\VID_46F4&PID_0001\UGALLOW0002
    Gß╗úi ├╜ th├¬m whitelist: UGALLOW0002
    Cß╗òng: 4 tr├¬n hub USB\ROOT_HUB30\4&1D3628F5&0&0
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 47)]
    ID: USB\VID_46F4&PID_0001\1-0000:00:02.0-2
    Gß╗úi ├╜ th├¬m whitelist: 1-0000:00:02.0-2
    Cß╗òng: 2 tr├¬n hub USB\ROOT_HUB30\4&10DC1CB6&0&0
04:18:42.392 [ĐẠT] E08 Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial — 
04:18:45.669   > UsbGuard.exe whitelist add UGALLOW0002 MatKhauE2E@2026 (mã 0)
04:18:47.323   theo dõi USB B {"disk_dau":1443,"disk_cuoi":1443,"vol_dau":1443,"vol_cuoi":1443,"ghi_duoc":true,"ghi_ms":1443,"con_disk":true,"con_vol":true}
04:18:47.395 [ĐẠT] E09 Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) — ghi được sau 1443 ms
04:18:53.193   [host] plug A
04:19:33.372   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
04:19:33.454   nhật ký UsbGuard: 2026-11-25 04:18:50 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGBLOCK0001&0 ; USB\VID_46F4&PID_0001\UGBLOCK0001 ; UGBLOCK0001
04:19:39.531   [host] shot e10-whitelist-chan-usb-la
04:19:39.563 [ĐẠT] E10 Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây — ổ xuất hiện không lần nào, ghi được: False
04:19:39.647 [ĐẠT] E11 Danh sách cho phép: USB được phép vẫn dùng bình thường — 
04:19:54.474   [host] shot gui-quan-ly
04:19:59.796   [host] unplug A
04:20:07.031   [host] unplug B
04:20:14.268   [host] plug B
04:20:14.415   theo dõi USB B {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
04:20:14.461 [ĐẠT] E12 Rút USB được phép ra cắm lại vẫn dùng được — ghi được sau 0 ms
04:20:17.736   > UsbGuard.exe whitelist remove UGALLOW0002 MatKhauE2E@2026 (mã 0)
04:20:19.428   theo dõi USB B {"disk_dau":0,"disk_cuoi":1429,"vol_dau":0,"vol_cuoi":1429,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
04:20:19.498 [ĐẠT] E13 Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay — còn ổ: False
04:20:24.257   > UsbGuard.exe devices (mã 0)
04:20:24.287 ß╗ö USB ─æang cß║»m: 0
Thiß║┐t bß╗ï USB l╞░u trß╗» ─æang cß║»m (kß╗â cß║ú ─æang bß╗ï chß║╖n): 2
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 47)]
    ID: USB\VID_46F4&PID_0001\UGALLOW0002
    Gß╗úi ├╜ th├¬m whitelist: UGALLOW0002
    Cß╗òng: 3 tr├¬n hub USB\ROOT_HUB30\4&1D3628F5&0&0
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 47)]
    ID: USB\VID_46F4&PID_0001\1-0000:00:02.0-2
    Gß╗úi ├╜ th├¬m whitelist: 1-0000:00:02.0-2
    Cß╗òng: 2 tr├¬n hub USB\ROOT_HUB30\4&10DC1CB6&0&0
04:20:24.333 [ĐẠT] E18 USB bị chặn khi đang cắm (Windows đã tháo) vẫn hiện trong danh sách thiết bị — 
04:20:27.287   > UsbGuard.exe whitelist add UGALLOW0002 MatKhauE2E@2026 (mã 0)
04:20:27.670   theo dõi USB B {"disk_dau":201,"disk_cuoi":201,"vol_dau":201,"vol_cuoi":201,"ghi_duoc":true,"ghi_ms":201,"con_disk":true,"con_vol":true}
04:20:27.746   nhật ký dịch vụ: 2026-11-25 04:18:32 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 1): QEMU USB HARDDRIVE | ID: USB\VID_46F4&PID_0001\UGALLOW0002 || 2026-11-25 04:18:45 [INFO] Thêm whitelist: UGALLOW0002 (qua CLI). || 2026-11-25 04:18:46 [INFO] Chế độ: DANH SÁCH CHO PHÉP (1 mục) || 2026-11-25 04:18:46 [INFO] Cho Windows cài lại USB từng bị cấm cài (đang cắm): USB\VID_46F4&PID_0001\UGALLOW0002 (mã 0) || 2026-11-25 04:18:50 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGBLOCK0001&0 ; USB\VID_46F4&PID_0001\UGBLOCK0001 ; UGBLOCK0001 || 2026-11-25 04:20:17 [INFO] Xoá whitelist: UGALLOW0002 (qua CLI). || 2026-11-25 04:20:19 [INFO] Chế độ: CHẶN TẤT CẢ || 2026-11-25 04:20:19 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGALLOW0002&0 ; USB\VID_46F4&PID_0001\UGALLOW0002 ; UGALLOW0002 || 2026-11-25 04:20:27 [INFO] Thêm whitelist: UGALLOW0002 (qua CLI). || 2026-11-25 04:20:27 [INFO] Chế độ: DANH SÁCH CHO PHÉP (1 mục) || 2026-11-25 04:20:27 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\UGALLOW0002 | cổng 3 || 
04:20:28.164   > UsbGuard.exe devices (mã 0)
04:20:28.194 ß╗ö USB ─æang cß║»m: 1
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
04:20:28.261 [ĐẠT] E19 Cho phép lại USB đang bị tháo: tự hiện lại trong This PC, không cần rút ra cắm lại — ghi được sau 201 ms; nhật ký: 2026-11-25 04:20:27 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\UGALLOW0002 | cổng 3
04:20:31.084   > UsbGuard.exe whitelist remove UGALLOW0002 MatKhauE2E@2026 (mã 0)
04:20:31.479   theo dõi USB B {"disk_dau":0,"disk_cuoi":158,"vol_dau":0,"vol_cuoi":158,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
04:20:34.253   > UsbGuard.exe pause 5 MatKhauE2E@2026 (mã 0)
04:20:36.336   theo dõi USB B {"disk_dau":1161,"disk_cuoi":1161,"vol_dau":1161,"vol_cuoi":1161,"ghi_duoc":true,"ghi_ms":1161,"con_disk":true,"con_vol":true}
04:20:36.393   nhật ký dịch vụ: 2026-11-25 04:20:27 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\UGALLOW0002 | cổng 3 || 2026-11-25 04:20:30 [INFO] Xoá whitelist: UGALLOW0002 (qua CLI). || 2026-11-25 04:20:31 [INFO] Chế độ: CHẶN TẤT CẢ || 2026-11-25 04:20:34 [INFO] Tạm dừng chặn USB trong 5 phút (qua CLI). || 2026-11-25 04:20:35 [INFO] Chế độ: TẠM DỪNG || 2026-11-25 04:20:35 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\UGALLOW0002 | cổng 3 || 2026-11-25 04:20:35 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\1-0000:00:02.0-2 | cổng 2 || 
04:20:36.451 [ĐẠT] E20 Tạm dừng khi USB đang bị tháo: tự dùng được, không cần rút ra cắm lại — ghi được sau 1161 ms
04:20:39.285   > UsbGuard.exe resume MatKhauE2E@2026 (mã 0)
04:20:39.790   theo dõi USB B {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
04:20:45.039   [host] unplug B
04:20:52.329   [host] plug A
04:21:05.472 [ĐẠT] E14 Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được — dịch vụ: Running
04:21:10.691   [host] unplug A
04:21:38.669 [ĐẠT] E15 Trình gỡ của bộ cài, sai mật khẩu: không gỡ được — 
04:21:43.911   [host] plug A
04:21:50.029   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
04:21:50.083   trước khi gỡ, USB A dùng được: False
04:22:04.240 [ĐẠT] E16 Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB — USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False
04:22:04.336   theo dõi USB A {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
04:22:04.362 [ĐẠT] E21 Gỡ cài đặt khi USB đang cắm và bị chặn: USB tự dùng được, không cần rút ra cắm lại — ghi được sau 0 ms
04:22:09.569   [host] unplug A
04:22:16.827   [host] plug A
04:22:16.935   theo dõi USB A {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
04:22:16.963 [ĐẠT] E17 Sau khi gỡ: cắm USB dùng lại bình thường — ghi được sau 0 ms
04:22:22.185   [host] unplug A
04:22:35.561   [host] shot setup-1-dieu-khoan
04:22:35.772   đã chụp giao diện bộ cài
04:22:35.953 === KẾT QUẢ: 21/21 ca ĐẠT ===
```

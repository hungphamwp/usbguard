# Kiểm thử cắm USB thật: Microsoft Windows 10 Pro

Phiên bản Windows: 10.0.19045 · Thời điểm: 2026-11-21 00:41:25 · Kết quả: **20/20 ca đạt**

USB: ổ QEMU usb-storage cắm nóng vào cổng xHCI (Windows nhận là USB flash disk thật: bus USB, driver USBSTOR).

| Mã | Ca kiểm thử | Kết quả | Chi tiết |
|---|---|---|---|
| E01 | Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file | Đạt | bus=USB, có ký tự ổ sau 3 ms, ghi file sau 3 ms |
| E02 | Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu | Đạt | mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True |
| E03 | Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) | Đạt | thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE |
| E04 | Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng | Đạt | 2026-11-21 00:36:19 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device / ID: USB\VID_46F4&PID_0001\UGBLOCK0001 |
| E05 | Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận | Đạt | trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK |
| E06 | Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra | Đạt | ghi được sau 259 ms kể từ lệnh tạm dừng |
| E07 | Bật lại chặn khi USB đang mở file: USB vẫn bị chặn | Đạt | còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá:  |
| E08 | Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial | Đạt |  |
| E09 | Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) | Đạt | ghi được sau 1402 ms |
| E10 | Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây | Đạt | ổ xuất hiện không lần nào, ghi được: False |
| E11 | Danh sách cho phép: USB được phép vẫn dùng bình thường | Đạt |  |
| E12 | Rút USB được phép ra cắm lại vẫn dùng được | Đạt | ghi được sau 16374 ms |
| E13 | Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay | Đạt | còn ổ: False |
| E18 | USB bị chặn khi đang cắm (Windows đã tháo) vẫn hiện trong danh sách thiết bị | Đạt |  |
| E19 | Cho phép lại USB đang bị tháo: tự hiện lại trong This PC, không cần rút ra cắm lại | Đạt | ghi được sau 0 ms; nhật ký: 2026-11-21 00:39:38 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device / USB\VID_46F4&PID_0001\UGALLOW0002 / cổng 3 |
| E20 | Tạm dừng khi USB đang bị tháo: tự dùng được, không cần rút ra cắm lại | Đạt | ghi được sau 561 ms |
| E14 | Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được | Đạt | dịch vụ: Running |
| E15 | Trình gỡ của bộ cài, sai mật khẩu: không gỡ được | Đạt |  |
| E16 | Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB | Đạt | USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False |
| E17 | Sau khi gỡ: cắm USB dùng lại bình thường | Đạt | ghi được sau 0 ms |

## Nhật ký chạy
```
00:35:19.037 === KIỂM THỬ CẮM USB THẬT (QEMU usb-storage) ===
00:35:19.350 Máy: DOCKERW-HGLU9JV | Microsoft Windows 10 Pro 10.0.19045 | quyền Administrator: True
00:35:45.397   [host] plug A
00:35:45.850   theo dõi USB A {"disk_dau":3,"disk_cuoi":3,"vol_dau":3,"vol_cuoi":3,"ghi_duoc":true,"ghi_ms":3,"con_disk":true,"con_vol":true}
00:35:49.928 [ĐẠT] E01 Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file — bus=USB, có ký tự ổ sau 3 ms, ghi file sau 3 ms
00:35:55.834   [host] shot e01-truoc-khi-cai
00:36:00.928   [host] unplug A
00:36:17.897 [ĐẠT] E02 Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu — mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True
00:36:23.944   [host] plug A
00:36:39.051   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:36:45.067   [host] shot e03-thong-bao-chan-usb
00:36:45.113 [ĐẠT] E03 Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) — thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE
00:36:45.160 [ĐẠT] E04 Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng — 2026-11-21 00:36:19 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device | ID: USB\VID_46F4&PID_0001\UGBLOCK0001
00:36:50.406   [host] plug K
00:37:02.609 [ĐẠT] E05 Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận — trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK
00:37:07.719   [host] unplug K
00:37:13.859   > UsbGuard.exe pause 10 MatKhauE2E@2026 (mã 0)
00:37:14.250   theo dõi USB A {"disk_dau":259,"disk_cuoi":259,"vol_dau":259,"vol_cuoi":259,"ghi_duoc":true,"ghi_ms":259,"con_disk":true,"con_vol":true}
00:37:14.281 [ĐẠT] E06 Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra — ghi được sau 259 ms kể từ lệnh tạm dừng
00:37:18.620   > UsbGuard.exe resume MatKhauE2E@2026 (mã 0)
00:37:20.526   theo dõi USB A {"disk_dau":0,"disk_cuoi":1753,"vol_dau":0,"vol_cuoi":1753,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:37:20.542   nhật ký UsbGuard: 2026-11-21 00:36:09 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\1-0000:00:02.0-2&0 ; USB\VID_46F4&PID_0001\1-0000:00:02.0-2 ; 1-0000:00:02.0-2 2026-11-21 00:37:20 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\1-0000:00:02.0-2&0 ; USB\VID_46F4&PID_0001\1-0000:00:02.0-2 ; 1-0000:00:02.0-2
00:37:20.573 [ĐẠT] E07 Bật lại chặn khi USB đang mở file: USB vẫn bị chặn — còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá: 
00:37:25.738   [host] unplug A
00:37:32.878   [host] plug B
00:37:39.088   > UsbGuard.exe devices (mã 0)
00:37:39.104 ß╗ö USB ─æang cß║»m: 0
Thiß║┐t bß╗ï USB l╞░u trß╗» ─æang cß║»m (kß╗â cß║ú ─æang bß╗ï chß║╖n): 2
- QEMU USB HARDDRIVE  [bß╗ï chß║╖n (m├ú 1)]
    ID: USB\VID_46F4&PID_0001\UGALLOW0002
    Gß╗úi ├╜ th├¬m whitelist: UGALLOW0002
    Cß╗òng: 4 tr├¬n hub USB\ROOT_HUB30\4&1D3628F5&0&0
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 47)]
    ID: USB\VID_46F4&PID_0001\1-0000:00:02.0-2
    Gß╗úi ├╜ th├¬m whitelist: 1-0000:00:02.0-2
    Cß╗òng: 2 tr├¬n hub USB\ROOT_HUB30\4&10DC1CB6&0&0
00:37:39.120 [ĐẠT] E08 Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial — 
00:37:42.882   > UsbGuard.exe whitelist add UGALLOW0002 MatKhauE2E@2026 (mã 0)
00:37:44.450   theo dõi USB B {"disk_dau":1402,"disk_cuoi":1402,"vol_dau":1402,"vol_cuoi":1402,"ghi_duoc":true,"ghi_ms":1402,"con_disk":true,"con_vol":true}
00:37:44.511 [ĐẠT] E09 Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) — ghi được sau 1402 ms
00:37:50.388   [host] plug A
00:38:30.488   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:38:30.520   nhật ký UsbGuard: 2026-11-21 00:37:46 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGBLOCK0001&0 ; USB\VID_46F4&PID_0001\UGBLOCK0001 ; UGBLOCK0001
00:38:36.426   [host] shot e10-whitelist-chan-usb-la
00:38:36.441 [ĐẠT] E10 Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây — ổ xuất hiện không lần nào, ghi được: False
00:38:36.473 [ĐẠT] E11 Danh sách cho phép: USB được phép vẫn dùng bình thường — 
00:38:51.098   [host] shot gui-quan-ly
00:38:56.207   [host] unplug A
00:39:03.285   [host] unplug B
00:39:10.379   [host] plug B
00:39:26.863   theo dõi USB B {"disk_dau":16374,"disk_cuoi":16374,"vol_dau":16374,"vol_cuoi":16374,"ghi_duoc":true,"ghi_ms":16374,"con_disk":true,"con_vol":true}
00:39:26.879 [ĐẠT] E12 Rút USB được phép ra cắm lại vẫn dùng được — ghi được sau 16374 ms
00:39:30.659   > UsbGuard.exe whitelist remove UGALLOW0002 MatKhauE2E@2026 (mã 0)
00:39:31.002   theo dõi USB B {"disk_dau":0,"disk_cuoi":124,"vol_dau":0,"vol_cuoi":124,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:39:31.033 [ĐẠT] E13 Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay — còn ổ: False
00:39:35.223   > UsbGuard.exe devices (mã 0)
00:39:35.239 ß╗ö USB ─æang cß║»m: 0
Thiß║┐t bß╗ï USB l╞░u trß╗» ─æang cß║»m (kß╗â cß║ú ─æang bß╗ï chß║╖n): 2
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 47)]
    ID: USB\VID_46F4&PID_0001\UGALLOW0002
    Gß╗úi ├╜ th├¬m whitelist: UGALLOW0002
    Cß╗òng: 3 tr├¬n hub USB\ROOT_HUB30\4&1D3628F5&0&0
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 47)]
    ID: USB\VID_46F4&PID_0001\1-0000:00:02.0-2
    Gß╗úi ├╜ th├¬m whitelist: 1-0000:00:02.0-2
    Cß╗òng: 2 tr├¬n hub USB\ROOT_HUB30\4&10DC1CB6&0&0
00:39:35.255 [ĐẠT] E18 USB bị chặn khi đang cắm (Windows đã tháo) vẫn hiện trong danh sách thiết bị — 
00:39:39.078   > UsbGuard.exe whitelist add UGALLOW0002 MatKhauE2E@2026 (mã 0)
00:39:39.157   theo dõi USB B {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
00:39:39.172   nhật ký dịch vụ: 2026-11-21 00:37:30 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 1): QEMU USB HARDDRIVE | ID: USB\VID_46F4&PID_0001\UGALLOW0002 || 2026-11-21 00:37:42 [INFO] Thêm whitelist: UGALLOW0002 (qua CLI). || 2026-11-21 00:37:44 [INFO] Chế độ: DANH SÁCH CHO PHÉP (1 mục) || 2026-11-21 00:37:44 [INFO] Cho Windows cài lại USB từng bị cấm cài (đang cắm): USB\VID_46F4&PID_0001\UGALLOW0002 (mã 0) || 2026-11-21 00:37:46 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGBLOCK0001&0 ; USB\VID_46F4&PID_0001\UGBLOCK0001 ; UGBLOCK0001 || 2026-11-21 00:39:30 [INFO] Xoá whitelist: UGALLOW0002 (qua CLI). || 2026-11-21 00:39:30 [INFO] Chế độ: CHẶN TẤT CẢ || 2026-11-21 00:39:30 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGALLOW0002&0 ; USB\VID_46F4&PID_0001\UGALLOW0002 ; UGALLOW0002 || 2026-11-21 00:39:38 [INFO] Chế độ: DANH SÁCH CHO PHÉP (1 mục) || 2026-11-21 00:39:38 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\UGALLOW0002 | cổng 3 || 2026-11-21 00:39:38 [INFO] Thêm whitelist: UGALLOW0002 (qua CLI). || 
00:39:39.378   > UsbGuard.exe devices (mã 0)
00:39:39.394 ß╗ö USB ─æang cß║»m: 1
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
00:39:39.410 [ĐẠT] E19 Cho phép lại USB đang bị tháo: tự hiện lại trong This PC, không cần rút ra cắm lại — ghi được sau 0 ms; nhật ký: 2026-11-21 00:39:38 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\UGALLOW0002 | cổng 3
00:39:43.143   > UsbGuard.exe whitelist remove UGALLOW0002 MatKhauE2E@2026 (mã 0)
00:39:44.966   theo dõi USB B {"disk_dau":0,"disk_cuoi":1652,"vol_dau":0,"vol_cuoi":1652,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:39:48.607   > UsbGuard.exe pause 5 MatKhauE2E@2026 (mã 0)
00:39:49.305   theo dõi USB B {"disk_dau":561,"disk_cuoi":561,"vol_dau":561,"vol_cuoi":561,"ghi_duoc":true,"ghi_ms":561,"con_disk":true,"con_vol":true}
00:39:49.336   nhật ký dịch vụ: 2026-11-21 00:39:38 [INFO] Thêm whitelist: UGALLOW0002 (qua CLI). || 2026-11-21 00:39:43 [INFO] Xoá whitelist: UGALLOW0002 (qua CLI). || 2026-11-21 00:39:44 [INFO] Chế độ: CHẶN TẤT CẢ || 2026-11-21 00:39:48 [INFO] Tạm dừng chặn USB trong 5 phút (qua CLI). || 2026-11-21 00:39:48 [INFO] Chế độ: TẠM DỪNG || 2026-11-21 00:39:48 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\UGALLOW0002 | cổng 3 || 2026-11-21 00:39:48 [INFO] USB được phép nhưng đã bị tháo khỏi Windows, tự nạp lại (thay cho rút ra cắm lại): USB Mass Storage Device | USB\VID_46F4&PID_0001\1-0000:00:02.0-2 | cổng 2 || 
00:39:49.352 [ĐẠT] E20 Tạm dừng khi USB đang bị tháo: tự dùng được, không cần rút ra cắm lại — ghi được sau 561 ms
00:39:53.036   > UsbGuard.exe resume MatKhauE2E@2026 (mã 0)
00:39:55.042   theo dõi USB B {"disk_dau":0,"disk_cuoi":1806,"vol_dau":0,"vol_cuoi":1806,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
00:40:00.314   [host] unplug B
00:40:07.456   [host] plug A
00:40:20.479 [ĐẠT] E14 Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được — dịch vụ: Running
00:40:25.589   [host] unplug A
00:40:52.698 [ĐẠT] E15 Trình gỡ của bộ cài, sai mật khẩu: không gỡ được — 
00:41:02.776 [ĐẠT] E16 Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB — USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False
00:41:07.998   [host] plug A
00:41:08.051   theo dõi USB A {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
00:41:08.067 [ĐẠT] E17 Sau khi gỡ: cắm USB dùng lại bình thường — ghi được sau 0 ms
00:41:13.204   [host] unplug A
00:41:25.124   [host] shot setup-1-dieu-khoan
00:41:25.186   đã chụp giao diện bộ cài
00:41:25.358 === KẾT QUẢ: 20/20 ca ĐẠT ===
```

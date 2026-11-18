# Kiểm thử cắm USB thật: Microsoft Windows 11 Pro

Phiên bản Windows: 10.0.26200 · Thời điểm: 2026-11-17 19:08:57 · Kết quả: **17/17 ca đạt**

USB: ổ QEMU usb-storage cắm nóng vào cổng xHCI (Windows nhận là USB flash disk thật: bus USB, driver USBSTOR).

| Mã | Ca kiểm thử | Kết quả | Chi tiết |
|---|---|---|---|
| E01 | Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file | Đạt | bus=USB, có ký tự ổ sau 8 ms, ghi file sau 8 ms |
| E02 | Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu | Đạt | mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True |
| E03 | Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) | Đạt | thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE |
| E04 | Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng | Đạt | 2026-11-17 19:04:07 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device / ID: USB\VID_46F4&PID_0001\UGBLOCK0001 |
| E05 | Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận | Đạt | trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK |
| E06 | Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra | Đạt | ghi được sau 1341 ms kể từ lệnh tạm dừng |
| E07 | Bật lại chặn khi USB đang mở file: USB vẫn bị chặn | Đạt | còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá:  |
| E08 | Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial | Đạt |  |
| E09 | Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) | Đạt | ghi được sau 665 ms |
| E10 | Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây | Đạt | ổ xuất hiện không lần nào, ghi được: False |
| E11 | Danh sách cho phép: USB được phép vẫn dùng bình thường | Đạt |  |
| E12 | Rút USB được phép ra cắm lại vẫn dùng được | Đạt | ghi được sau 0 ms |
| E13 | Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay | Đạt | còn ổ: False |
| E14 | Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được | Đạt | dịch vụ: Running |
| E15 | Trình gỡ của bộ cài, sai mật khẩu: không gỡ được | Đạt |  |
| E16 | Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB | Đạt | USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False |
| E17 | Sau khi gỡ: cắm USB dùng lại bình thường | Đạt | ghi được sau 0 ms |

## Nhật ký chạy
```
19:03:02.557 === KIỂM THỬ CẮM USB THẬT (QEMU usb-storage) ===
19:03:02.802 Máy: WIN-CFS9TDIAPHD | Microsoft Windows 11 Pro 10.0.26200 | quyền Administrator: True
19:03:28.819   [host] plug A
19:03:30.091   theo dõi USB A {"disk_dau":8,"disk_cuoi":8,"vol_dau":8,"vol_cuoi":8,"ghi_duoc":true,"ghi_ms":8,"con_disk":true,"con_vol":true}
19:03:38.893 [ĐẠT] E01 Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file — bus=USB, có ký tự ổ sau 8 ms, ghi file sau 8 ms
19:03:44.949   [host] shot e01-truoc-khi-cai
19:03:50.196   [host] unplug A
19:04:06.206 [ĐẠT] E02 Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu — mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True
19:04:12.656   [host] plug A
19:04:27.813   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
19:04:34.144   [host] shot e03-thong-bao-chan-usb
19:04:34.248 [ĐẠT] E03 Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) — thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE
19:04:34.338 [ĐẠT] E04 Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng — 2026-11-17 19:04:07 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device | ID: USB\VID_46F4&PID_0001\UGBLOCK0001
19:04:39.565   [host] plug K
19:04:52.009 [ĐẠT] E05 Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận — trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK
19:04:57.082   [host] unplug K
19:05:01.147   > UsbGuard.exe pause 10 MatKhauE2E@2026 (mã 0)
19:05:02.795   theo dõi USB A {"disk_dau":1341,"disk_cuoi":1341,"vol_dau":1341,"vol_cuoi":1341,"ghi_duoc":true,"ghi_ms":1341,"con_disk":true,"con_vol":true}
19:05:03.062 [ĐẠT] E06 Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra — ghi được sau 1341 ms kể từ lệnh tạm dừng
19:05:05.415   > UsbGuard.exe resume MatKhauE2E@2026 (mã 0)
19:05:06.591   theo dõi USB A {"disk_dau":0,"disk_cuoi":941,"vol_dau":0,"vol_cuoi":941,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
19:05:06.652   nhật ký UsbGuard: 2026-11-17 19:03:59 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\1-0000:00:02.0-2&0 ; USB\VID_46F4&PID_0001\1-0000:00:02.0-2 ; 1-0000:00:02.0-2
19:05:06.725 [ĐẠT] E07 Bật lại chặn khi USB đang mở file: USB vẫn bị chặn — còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá: 
19:05:11.978   [host] unplug A
19:05:19.051   [host] plug B
19:05:25.342   > UsbGuard.exe devices (mã 0)
19:05:25.396 ß╗ö USB ─æang cß║»m: 0
Thiß║┐t bß╗ï USB l╞░u trß╗» ─æang cß║»m (kß╗â cß║ú ─æang bß╗ï chß║╖n): 2
- QEMU USB HARDDRIVE  [bß╗ï chß║╖n (m├ú 1)]
    ID: USB\VID_46F4&PID_0001\UGALLOW0002
    Gß╗úi ├╜ th├¬m whitelist: UGALLOW0002
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 14)]
    ID: USB\VID_46F4&PID_0001\1-0000:00:02.0-2
    Gß╗úi ├╜ th├¬m whitelist: 1-0000:00:02.0-2
19:05:25.473 [ĐẠT] E08 Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial — 
19:05:27.803   > UsbGuard.exe whitelist add UGALLOW0002 MatKhauE2E@2026 (mã 0)
19:05:28.693   theo dõi USB B {"disk_dau":665,"disk_cuoi":665,"vol_dau":665,"vol_cuoi":665,"ghi_duoc":true,"ghi_ms":665,"con_disk":true,"con_vol":true}
19:05:28.751 [ĐẠT] E09 Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) — ghi được sau 665 ms
19:05:34.782   [host] plug A
19:06:19.053   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
19:06:19.119   nhật ký UsbGuard: 2026-11-17 19:05:30 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGBLOCK0001&0 ; USB\VID_46F4&PID_0001\UGBLOCK0001 ; UGBLOCK0001
19:06:25.154   [host] shot e10-whitelist-chan-usb-la
19:06:25.195 [ĐẠT] E10 Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây — ổ xuất hiện không lần nào, ghi được: False
19:06:25.257 [ĐẠT] E11 Danh sách cho phép: USB được phép vẫn dùng bình thường — 
19:06:39.868   [host] shot gui-quan-ly
19:06:45.199   [host] unplug A
19:06:52.435   [host] unplug B
19:06:59.693   [host] plug B
19:06:59.872   theo dõi USB B {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
19:07:00.000 [ĐẠT] E12 Rút USB được phép ra cắm lại vẫn dùng được — ghi được sau 0 ms
19:07:02.797   > UsbGuard.exe whitelist remove UGALLOW0002 MatKhauE2E@2026 (mã 0)
19:07:22.922   theo dõi USB B {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
19:07:22.984 [ĐẠT] E13 Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay — còn ổ: False
19:07:28.219   [host] unplug B
19:07:35.291   [host] plug A
19:07:48.449 [ĐẠT] E14 Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được — dịch vụ: Running
19:07:53.735   [host] unplug A
19:08:21.744 [ĐẠT] E15 Trình gỡ của bộ cài, sai mật khẩu: không gỡ được — 
19:08:32.936 [ĐẠT] E16 Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB — USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False
19:08:38.149   [host] plug A
19:08:38.259   theo dõi USB A {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
19:08:38.293 [ĐẠT] E17 Sau khi gỡ: cắm USB dùng lại bình thường — ghi được sau 0 ms
19:08:43.470   [host] unplug A
19:08:56.971   [host] shot setup-1-dieu-khoan
19:08:57.203   đã chụp giao diện bộ cài
19:08:57.405 === KẾT QUẢ: 17/17 ca ĐẠT ===
```

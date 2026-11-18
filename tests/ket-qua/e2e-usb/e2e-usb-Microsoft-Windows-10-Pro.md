# Kiểm thử cắm USB thật: Microsoft Windows 10 Pro

Phiên bản Windows: 10.0.19045 · Thời điểm: 2026-11-17 19:01:59 · Kết quả: **17/17 ca đạt**

USB: ổ QEMU usb-storage cắm nóng vào cổng xHCI (Windows nhận là USB flash disk thật: bus USB, driver USBSTOR).

| Mã | Ca kiểm thử | Kết quả | Chi tiết |
|---|---|---|---|
| E01 | Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file | Đạt | bus=USB, có ký tự ổ sau 3 ms, ghi file sau 3 ms |
| E02 | Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu | Đạt | mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True |
| E03 | Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) | Đạt | thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE |
| E04 | Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng | Đạt | 2026-11-17 18:57:50 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device / ID: USB\VID_46F4&PID_0001\UGBLOCK0001 |
| E05 | Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận | Đạt | trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK |
| E06 | Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra | Đạt | ghi được sau 504 ms kể từ lệnh tạm dừng |
| E07 | Bật lại chặn khi USB đang mở file: USB vẫn bị chặn | Đạt | còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá:  |
| E08 | Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial | Đạt |  |
| E09 | Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) | Đạt | ghi được sau 485 ms |
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
18:56:53.304 === KIỂM THỬ CẮM USB THẬT (QEMU usb-storage) ===
18:56:54.492 Máy: DOCKERW-CSVURT9 | Microsoft Windows 10 Pro 10.0.19045 | quyền Administrator: True
18:57:20.445   [host] plug A
18:57:20.835   theo dõi USB A {"disk_dau":3,"disk_cuoi":3,"vol_dau":3,"vol_cuoi":3,"ghi_duoc":true,"ghi_ms":3,"con_disk":true,"con_vol":true}
18:57:24.414 [ĐẠT] E01 Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file — bus=USB, có ký tự ổ sau 3 ms, ghi file sau 3 ms
18:57:30.320   [host] shot e01-truoc-khi-cai
18:57:35.414   [host] unplug A
18:57:48.195 [ĐẠT] E02 Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu — mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True
18:57:54.273   [host] plug A
18:58:09.358   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
18:58:15.345   [host] shot e03-thong-bao-chan-usb
18:58:15.392 [ĐẠT] E03 Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) — thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE
18:58:15.430 [ĐẠT] E04 Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng — 2026-11-17 18:57:50 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device | ID: USB\VID_46F4&PID_0001\UGBLOCK0001
18:58:20.709   [host] plug K
18:58:32.869 [ĐẠT] E05 Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận — trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK
18:58:37.967   [host] unplug K
18:58:40.733   > UsbGuard.exe pause 10 MatKhauE2E@2026 (mã 0)
18:58:41.327   theo dõi USB A {"disk_dau":504,"disk_cuoi":504,"vol_dau":504,"vol_cuoi":504,"ghi_duoc":true,"ghi_ms":504,"con_disk":true,"con_vol":true}
18:58:41.358 [ĐẠT] E06 Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra — ghi được sau 504 ms kể từ lệnh tạm dừng
18:58:42.181   > UsbGuard.exe resume MatKhauE2E@2026 (mã 0)
18:58:43.484   theo dõi USB A {"disk_dau":0,"disk_cuoi":1139,"vol_dau":0,"vol_cuoi":1139,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
18:58:43.506   nhật ký UsbGuard: 2026-11-17 18:57:40 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\1-0000:00:02.0-2&0 ; USB\VID_46F4&PID_0001\1-0000:00:02.0-2 ; 1-0000:00:02.0-2
18:58:43.538 [ĐẠT] E07 Bật lại chặn khi USB đang mở file: USB vẫn bị chặn — còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá: 
18:58:48.657   [host] unplug A
18:58:55.780   [host] plug B
18:59:01.922   > UsbGuard.exe devices (mã 0)
18:59:01.938 ß╗ö USB ─æang cß║»m: 0
Thiß║┐t bß╗ï USB l╞░u trß╗» ─æang cß║»m (kß╗â cß║ú ─æang bß╗ï chß║╖n): 2
- QEMU USB HARDDRIVE  [bß╗ï chß║╖n (m├ú 1)]
    ID: USB\VID_46F4&PID_0001\UGALLOW0002
    Gß╗úi ├╜ th├¬m whitelist: UGALLOW0002
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 14)]
    ID: USB\VID_46F4&PID_0001\1-0000:00:02.0-2
    Gß╗úi ├╜ th├¬m whitelist: 1-0000:00:02.0-2
18:59:01.969 [ĐẠT] E08 Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial — 
18:59:02.840   > UsbGuard.exe whitelist add UGALLOW0002 MatKhauE2E@2026 (mã 0)
18:59:03.474   theo dõi USB B {"disk_dau":null,"disk_cuoi":null,"vol_dau":485,"vol_cuoi":485,"ghi_duoc":true,"ghi_ms":485,"con_disk":false,"con_vol":true}
18:59:03.520 [ĐẠT] E09 Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) — ghi được sau 485 ms
18:59:09.372   [host] plug A
18:59:49.641   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
18:59:49.657   nhật ký UsbGuard: 2026-11-17 18:59:05 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGBLOCK0001&0 ; USB\VID_46F4&PID_0001\UGBLOCK0001 ; UGBLOCK0001
18:59:55.563   [host] shot e10-whitelist-chan-usb-la
18:59:55.563 [ĐẠT] E10 Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây — ổ xuất hiện không lần nào, ghi được: False
18:59:55.594 [ĐẠT] E11 Danh sách cho phép: USB được phép vẫn dùng bình thường — 
19:00:10.219   [host] shot gui-quan-ly
19:00:15.329   [host] unplug A
19:00:22.438   [host] unplug B
19:00:29.467   [host] plug B
19:00:29.498   theo dõi USB B {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
19:00:29.514 [ĐẠT] E12 Rút USB được phép ra cắm lại vẫn dùng được — ghi được sau 0 ms
19:00:30.263   > UsbGuard.exe whitelist remove UGALLOW0002 MatKhauE2E@2026 (mã 0)
19:00:31.823   theo dõi USB B {"disk_dau":0,"disk_cuoi":1389,"vol_dau":0,"vol_cuoi":1389,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
19:00:31.854 [ĐẠT] E13 Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay — còn ổ: False
19:00:37.055   [host] unplug B
19:00:44.164   [host] plug A
19:00:57.185 [ĐẠT] E14 Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được — dịch vụ: Running
19:01:02.279   [host] unplug A
19:01:29.357 [ĐẠT] E15 Trình gỡ của bộ cài, sai mật khẩu: không gỡ được — 
19:01:37.420 [ĐẠT] E16 Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB — USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False
19:01:42.625   [host] plug A
19:01:42.710   theo dõi USB A {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
19:01:42.726 [ĐẠT] E17 Sau khi gỡ: cắm USB dùng lại bình thường — ghi được sau 0 ms
19:01:47.865   [host] unplug A
19:01:59.690   [host] shot setup-1-dieu-khoan
19:01:59.737   đã chụp giao diện bộ cài
19:01:59.846 === KẾT QUẢ: 17/17 ca ĐẠT ===
```

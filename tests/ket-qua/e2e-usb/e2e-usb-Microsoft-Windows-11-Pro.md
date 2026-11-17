# Kiểm thử cắm USB thật: Microsoft Windows 11 Pro

Phiên bản Windows: 10.0.26200 · Thời điểm: 2026-11-17 08:58:40 · Kết quả: **17/17 ca đạt**

USB: ổ QEMU usb-storage cắm nóng vào cổng xHCI (Windows nhận là USB flash disk thật: bus USB, driver USBSTOR).

| Mã | Ca kiểm thử | Kết quả | Chi tiết |
|---|---|---|---|
| E01 | Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file | Đạt | bus=USB, có ký tự ổ sau 3 ms, ghi file sau 3 ms |
| E02 | Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu | Đạt | mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True |
| E03 | Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) | Đạt | thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE |
| E04 | Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng | Đạt | 2026-11-17 08:54:58 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device / ID: USB\VID_46F4&PID_0001\UGBLOCK0001 |
| E05 | Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận | Đạt | trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK |
| E06 | Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra | Đạt | ghi được sau 143 ms kể từ lệnh tạm dừng |
| E07 | Bật lại chặn khi USB đang mở file: USB vẫn bị chặn | Đạt | còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá:  |
| E08 | Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial | Đạt |  |
| E09 | Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) | Đạt | ghi được sau 1835 ms |
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
08:53:58.097 === KIỂM THỬ CẮM USB THẬT (QEMU usb-storage) ===
08:53:58.308 Máy: WIN-GBCCP920R5R | Microsoft Windows 11 Pro 10.0.26200 | quyền Administrator: True
08:54:24.562   [host] plug A
08:54:25.283   theo dõi USB A {"disk_dau":3,"disk_cuoi":3,"vol_dau":3,"vol_cuoi":3,"ghi_duoc":true,"ghi_ms":3,"con_disk":true,"con_vol":true}
08:54:31.896 [ĐẠT] E01 Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file — bus=USB, có ký tự ổ sau 3 ms, ghi file sau 3 ms
08:54:37.871   [host] shot e01-truoc-khi-cai
08:54:43.068   [host] unplug A
08:54:56.944 [ĐẠT] E02 Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu — mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True
08:55:03.346   [host] plug A
08:55:18.630   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
08:55:24.995   [host] shot e03-thong-bao-chan-usb
08:55:25.089 [ĐẠT] E03 Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) — thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE
08:55:25.143 [ĐẠT] E04 Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng — 2026-11-17 08:54:58 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device | ID: USB\VID_46F4&PID_0001\UGBLOCK0001
08:55:30.439   [host] plug K
08:55:42.701 [ĐẠT] E05 Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận — trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK
08:55:47.893   [host] unplug K
08:55:50.926   > UsbGuard.exe pause 10 MatKhauE2E@2026 (mã 0)
08:55:51.187   theo dõi USB A {"disk_dau":143,"disk_cuoi":143,"vol_dau":143,"vol_cuoi":143,"ghi_duoc":true,"ghi_ms":143,"con_disk":true,"con_vol":true}
08:55:51.231 [ĐẠT] E06 Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra — ghi được sau 143 ms kể từ lệnh tạm dừng
08:55:52.465   > UsbGuard.exe resume MatKhauE2E@2026 (mã 0)
08:55:53.432   theo dõi USB A {"disk_dau":0,"disk_cuoi":751,"vol_dau":0,"vol_cuoi":751,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
08:55:53.488   nhật ký UsbGuard: 2026-11-17 08:54:50 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\1-0000:00:02.0-2&0 ; USB\VID_46F4&PID_0001\1-0000:00:02.0-2 ; 1-0000:00:02.0-2 2026-11-17 08:55:53 [INFO] Buộc tháo 1 phân vùng của QEMU QEMU HARDDISK (đang có file mở) để gỡ USB.
08:55:53.546 [ĐẠT] E07 Bật lại chặn khi USB đang mở file: USB vẫn bị chặn — còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá: 
08:55:58.760   [host] unplug A
08:56:06.064   [host] plug B
08:56:12.266   > UsbGuard.exe devices (mã 0)
08:56:12.302 ß╗ö USB ─æang cß║»m: 0
Thiß║┐t bß╗ï USB l╞░u trß╗» ─æang cß║»m (kß╗â cß║ú ─æang bß╗ï chß║╖n): 2
- QEMU USB HARDDRIVE  [bß╗ï chß║╖n (m├ú 1)]
    ID: USB\VID_46F4&PID_0001\UGALLOW0002
    Gß╗úi ├╜ th├¬m whitelist: UGALLOW0002
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 14)]
    ID: USB\VID_46F4&PID_0001\1-0000:00:02.0-2
    Gß╗úi ├╜ th├¬m whitelist: 1-0000:00:02.0-2
08:56:12.354 [ĐẠT] E08 Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial — 
08:56:13.421   > UsbGuard.exe whitelist add UGALLOW0002 MatKhauE2E@2026 (mã 0)
08:56:15.366   theo dõi USB B {"disk_dau":1835,"disk_cuoi":1835,"vol_dau":1835,"vol_cuoi":1835,"ghi_duoc":true,"ghi_ms":1835,"con_disk":true,"con_vol":true}
08:56:15.432 [ĐẠT] E09 Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) — ghi được sau 1835 ms
08:56:21.403   [host] plug A
08:56:36.487   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
08:56:36.541   nhật ký UsbGuard: 2026-11-17 08:56:17 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGBLOCK0001&0 ; USB\VID_46F4&PID_0001\UGBLOCK0001 ; UGBLOCK0001
08:56:42.548   [host] shot e10-whitelist-chan-usb-la
08:56:42.571 [ĐẠT] E10 Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây — ổ xuất hiện không lần nào, ghi được: False
08:56:42.621 [ĐẠT] E11 Danh sách cho phép: USB được phép vẫn dùng bình thường — 
08:56:57.382   [host] shot gui-quan-ly
08:57:02.610   [host] unplug A
08:57:09.781   [host] unplug B
08:57:16.958   [host] plug B
08:57:17.047   theo dõi USB B {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
08:57:17.065 [ĐẠT] E12 Rút USB được phép ra cắm lại vẫn dùng được — ghi được sau 0 ms
08:57:17.937   > UsbGuard.exe whitelist remove UGALLOW0002 MatKhauE2E@2026 (mã 0)
08:57:19.450   theo dõi USB B {"disk_dau":0,"disk_cuoi":1315,"vol_dau":0,"vol_cuoi":1315,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
08:57:19.495 [ĐẠT] E13 Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay — còn ổ: False
08:57:24.667   [host] unplug B
08:57:31.840   [host] plug A
08:57:44.915 [ĐẠT] E14 Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được — dịch vụ: Running
08:57:50.108   [host] unplug A
08:58:17.795 [ĐẠT] E15 Trình gỡ của bộ cài, sai mật khẩu: không gỡ được — 
08:58:28.083 [ĐẠT] E16 Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB — USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False
08:58:33.250   [host] plug A
08:58:33.346   theo dõi USB A {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
08:58:33.366 [ĐẠT] E17 Sau khi gỡ: cắm USB dùng lại bình thường — ghi được sau 0 ms
08:58:38.553   [host] unplug A
08:58:40.601 === KẾT QUẢ: 17/17 ca ĐẠT ===
```

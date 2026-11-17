# Kiểm thử cắm USB thật: Microsoft Windows 10 Pro

Phiên bản Windows: 10.0.19045 · Thời điểm: 2026-11-17 08:53:21 · Kết quả: **17/17 ca đạt**

USB: ổ QEMU usb-storage cắm nóng vào cổng xHCI (Windows nhận là USB flash disk thật: bus USB, driver USBSTOR).

| Mã | Ca kiểm thử | Kết quả | Chi tiết |
|---|---|---|---|
| E01 | Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file | Đạt | bus=USB, có ký tự ổ sau 2 ms, ghi file sau 2 ms |
| E02 | Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu | Đạt | mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True |
| E03 | Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) | Đạt | thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE |
| E04 | Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng | Đạt | 2026-11-17 08:49:30 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device / ID: USB\VID_46F4&PID_0001\UGBLOCK0001 |
| E05 | Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận | Đạt | trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK |
| E06 | Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra | Đạt | ghi được sau 1872 ms kể từ lệnh tạm dừng |
| E07 | Bật lại chặn khi USB đang mở file: USB vẫn bị chặn | Đạt | còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá:  |
| E08 | Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial | Đạt |  |
| E09 | Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) | Đạt | ghi được sau 614 ms |
| E10 | Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây | Đạt | ổ xuất hiện không lần nào, ghi được: False |
| E11 | Danh sách cho phép: USB được phép vẫn dùng bình thường | Đạt |  |
| E12 | Rút USB được phép ra cắm lại vẫn dùng được | Đạt | ghi được sau 16376 ms |
| E13 | Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay | Đạt | còn ổ: False |
| E14 | Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được | Đạt | dịch vụ: Running |
| E15 | Trình gỡ của bộ cài, sai mật khẩu: không gỡ được | Đạt |  |
| E16 | Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB | Đạt | USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False |
| E17 | Sau khi gỡ: cắm USB dùng lại bình thường | Đạt | ghi được sau 0 ms |

## Nhật ký chạy
```
08:47:58.195 === KIỂM THỬ CẮM USB THẬT (QEMU usb-storage) ===
08:47:58.352 Máy: DOCKERW-B8O7JUT | Microsoft Windows 10 Pro 10.0.19045 | quyền Administrator: True
08:48:24.273   [host] plug A
08:49:00.789   theo dõi USB A {"disk_dau":2,"disk_cuoi":2,"vol_dau":2,"vol_cuoi":2,"ghi_duoc":true,"ghi_ms":2,"con_disk":true,"con_vol":true}
08:49:04.477 [ĐẠT] E01 Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file — bus=USB, có ký tự ổ sau 2 ms, ghi file sau 2 ms
08:49:10.404   [host] shot e01-truoc-khi-cai
08:49:15.564   [host] unplug A
08:49:28.471 [ĐẠT] E02 Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu — mã thoát 0, dịch vụ Running, USBSTOR Start=4, DenyDeviceIDs=1, lối tắt=True
08:49:34.534   [host] plug A
08:49:49.561   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
08:49:55.576   [host] shot e03-thong-bao-chan-usb
08:49:55.607 [ĐẠT] E03 Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được) — thấy ký tự ổ: không lần nào, ghi được: False, thiết bị USB: Error / CM_PROB_DISABLED_SERVICE
08:49:55.639 [ĐẠT] E04 Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng — 2026-11-17 08:49:30 [WARN] Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị 32): USB Mass Storage Device | ID: USB\VID_46F4&PID_0001\UGBLOCK0001
08:50:00.836   [host] plug K
08:50:13.011 [ĐẠT] E05 Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận — trước 3 thiết bị (lỗi 0), sau khi cắm bàn phím USB 4 (lỗi 0): Standard PS/2 Keyboard=OK; HID-compliant mouse=OK; HID Keyboard Device=OK; PS/2 Compatible Mouse=OK
08:50:18.120   [host] unplug K
08:50:20.917   > UsbGuard.exe pause 10 MatKhauE2E@2026 (mã 0)
08:50:22.871   theo dõi USB A {"disk_dau":1872,"disk_cuoi":1872,"vol_dau":1872,"vol_cuoi":1872,"ghi_duoc":true,"ghi_ms":1872,"con_disk":true,"con_vol":true}
08:50:22.886 [ĐẠT] E06 Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra — ghi được sau 1872 ms kể từ lệnh tạm dừng
08:50:23.960   > UsbGuard.exe resume MatKhauE2E@2026 (mã 0)
08:50:25.047   theo dõi USB A {"disk_dau":0,"disk_cuoi":911,"vol_dau":0,"vol_cuoi":911,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
08:50:25.078   nhật ký UsbGuard: 2026-11-17 08:49:20 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\1-0000:00:02.0-2&0 ; USB\VID_46F4&PID_0001\1-0000:00:02.0-2 ; 1-0000:00:02.0-2 2026-11-17 08:50:24 [INFO] Buộc tháo 1 phân vùng của QEMU QEMU HARDDISK (đang có file mở) để gỡ USB.
08:50:25.116 [ĐẠT] E07 Bật lại chặn khi USB đang mở file: USB vẫn bị chặn — còn ổ sau 25 giây: False; thiết bị bị vô hiệu hoá: 
08:50:30.226   [host] unplug A
08:50:37.366   [host] plug B
08:50:43.483   > UsbGuard.exe devices (mã 0)
08:50:43.505 ß╗ö USB ─æang cß║»m: 0
Thiß║┐t bß╗ï USB l╞░u trß╗» ─æang cß║»m (kß╗â cß║ú ─æang bß╗ï chß║╖n): 2
- QEMU USB HARDDRIVE  [bß╗ï chß║╖n (m├ú 1)]
    ID: USB\VID_46F4&PID_0001\UGALLOW0002
    Gß╗úi ├╜ th├¬m whitelist: UGALLOW0002
- USB Mass Storage Device  [bß╗ï chß║╖n (m├ú 14)]
    ID: USB\VID_46F4&PID_0001\1-0000:00:02.0-2
    Gß╗úi ├╜ th├¬m whitelist: 1-0000:00:02.0-2
08:50:43.521 [ĐẠT] E08 Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial — 
08:50:44.255   > UsbGuard.exe whitelist add UGALLOW0002 MatKhauE2E@2026 (mã 0)
08:50:44.968   theo dõi USB B {"disk_dau":614,"disk_cuoi":614,"vol_dau":614,"vol_cuoi":614,"ghi_duoc":true,"ghi_ms":614,"con_disk":true,"con_vol":true}
08:50:44.983 [ĐẠT] E09 Thêm serial vào whitelist: USB đó dùng được (không cần rút ra) — ghi được sau 614 ms
08:50:50.820   [host] plug A
08:51:05.920   theo dõi USB A {"disk_dau":null,"disk_cuoi":null,"vol_dau":null,"vol_cuoi":null,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
08:51:05.935   nhật ký UsbGuard: 2026-11-17 08:50:46 [WARN] Đã gỡ thiết bị USB không được phép: QEMU QEMU HARDDISK | ID: USBSTOR\DISK&VEN_QEMU&PROD_QEMU_HARDDISK&REV_2.5+\UGBLOCK0001&0 ; USB\VID_46F4&PID_0001\UGBLOCK0001 ; UGBLOCK0001
08:51:11.842   [host] shot e10-whitelist-chan-usb-la
08:51:11.857 [ĐẠT] E10 Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây — ổ xuất hiện không lần nào, ghi được: False
08:51:11.904 [ĐẠT] E11 Danh sách cho phép: USB được phép vẫn dùng bình thường — 
08:51:26.529   [host] shot gui-quan-ly
08:51:31.639   [host] unplug A
08:51:38.717   [host] unplug B
08:51:45.810   [host] plug B
08:52:02.232   theo dõi USB B {"disk_dau":16376,"disk_cuoi":16376,"vol_dau":16376,"vol_cuoi":16376,"ghi_duoc":true,"ghi_ms":16376,"con_disk":true,"con_vol":true}
08:52:02.248 [ĐẠT] E12 Rút USB được phép ra cắm lại vẫn dùng được — ghi được sau 16376 ms
08:52:03.007   > UsbGuard.exe whitelist remove UGALLOW0002 MatKhauE2E@2026 (mã 0)
08:52:03.678   theo dõi USB B {"disk_dau":0,"disk_cuoi":499,"vol_dau":0,"vol_cuoi":499,"ghi_duoc":false,"ghi_ms":null,"con_disk":false,"con_vol":false}
08:52:03.709 [ĐẠT] E13 Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay — còn ổ: False
08:52:08.827   [host] unplug B
08:52:15.912   [host] plug A
08:52:28.920 [ĐẠT] E14 Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được — dịch vụ: Running
08:52:34.013   [host] unplug A
08:53:01.107 [ĐẠT] E15 Trình gỡ của bộ cài, sai mật khẩu: không gỡ được — 
08:53:09.141 [ĐẠT] E16 Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB — USBSTOR Start=3, còn DenyDeviceIDs: False, còn mục gỡ cài đặt: 0, còn file: False
08:53:14.278   [host] plug A
08:53:14.331   theo dõi USB A {"disk_dau":0,"disk_cuoi":0,"vol_dau":0,"vol_cuoi":0,"ghi_duoc":true,"ghi_ms":0,"con_disk":true,"con_vol":true}
08:53:14.331 [ĐẠT] E17 Sau khi gỡ: cắm USB dùng lại bình thường — ghi được sau 0 ms
08:53:19.449   [host] unplug A
08:53:21.463 === KẾT QUẢ: 17/17 ca ĐẠT ===
```

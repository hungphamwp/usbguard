# Kết quả kiểm thử UsbGuard 1.2.1

| Bộ kiểm thử | Môi trường | Kết quả | Lần chạy |
|---|---|---|---|
| Unit test (xUnit) | Windows Server 2022, 2025 | 22/22 mỗi bản | https://github.com/hungphamwp/usbguard/actions/runs/45609957343 |
| Tích hợp: cài dịch vụ thật, 3 tầng chặn, chống tắt, chống đổi Startup type, người dùng thường, chống dò mật khẩu, gỡ (`tests/integration.ps1`) | Windows Server 2022, 2025 | 40/40 mỗi bản | https://github.com/hungphamwp/usbguard/actions/runs/45609957343 |
| Cắm USB: cài bằng setup.exe, cắm/rút ổ USB, bàn phím USB, whitelist, file đang mở, USB đã bị tháo khỏi Windows, gỡ bằng trình gỡ, gỡ khi USB đang cắm (`tests/e2e/`) | Windows 10 Pro, Windows 11 Pro (QEMU, cổng xHCI) | 21/21 mỗi bản | https://github.com/hungphamwp/usbguard/actions/runs/45609957447 |
| Thủ công trên máy Windows thật, USB vật lý (thành viên nhóm, bản 1.1.0) | Windows, USB thật | 7/7 kịch bản đạt | `may-that/Bao_cao_kiem_thu_UsbGuard_1_1_0.doc` |

Ổ USB trong kiểm thử cắm USB là ổ QEMU usb-storage cắm nóng vào cổng USB 3 (xHCI) của máy ảo. Windows nhận đúng như USB flash disk thật: bus USB, driver USBSTOR, có ký tự ổ, ghi được file (ca E01).

Bản 1.2 sửa 2 lỗi do nhóm phát hiện khi thử trên máy thật, đã tái hiện được trong máy ảo trước khi sửa (run 44881182584: E19, E20 không đạt):
- USB bị chặn khi đang cắm (Windows đã tháo, mã 47) thì khi được cho phép/tạm dừng phải rút ra cắm lại mới dùng được. Nay tự "rút ra cắm lại" cổng đó bằng phần mềm (E19, E20).
- USB đã bị tháo nhưng vẫn cắm có lúc biến khỏi danh sách. Nay đọc trạng thái cổng từ hub nên vẫn hiện (E18).

Bản 1.2.1 sửa 2 lỗi nhóm báo ngày 25/11/2026:
- Admin vào services.msc đổi Startup type thành Disabled rồi khởi động lại máy thì dịch vụ không chạy: USB vẫn bị chặn nhưng không có thông báo, cho phép USB và hết giờ tạm dừng không có tác dụng. Nay nhóm Administrators không còn quyền đổi cấu hình dịch vụ (lỗi 5, TC38); sửa thẳng Registry thì dịch vụ tự trả lại Automatic sau khoảng 2 giây (TC39), xoá cấu hình tự chạy lại cũng tự đặt lại (TC40). Giao diện quản lý thấy dịch vụ không chạy thì tự bật lại.
- Gỡ cài đặt khi USB đang cắm và bị chặn thì USB vẫn không dùng được tới khi rút ra cắm lại. Nay trình gỡ tự "rút ra cắm lại" cổng đó bằng phần mềm (E21).

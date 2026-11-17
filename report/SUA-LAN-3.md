# Sửa lần 3: cập nhật báo cáo + slide lên UsbGuard 1.1 (sản phẩm hoàn chỉnh, đã cắm USB thật)

Thư mục: `~/Project/SGU/Semi chuyên đề/UsbGuard`. Sửa `report/tao_bao_cao.py`, `report/ve_hinh.py`, `slide/tao_slide.py`, chạy lại để xuất `report/BAO-CAO-UsbGuard.docx/.pdf` và `slide/SLIDE-UsbGuard.pptx/.pdf`.

## Quy tắc bắt buộc
- Tiếng Việt có dấu đầy đủ. Mọi số lượng viết bằng chữ số ("3 tầng", "17 ca"), kể cả đầu câu và tiêu đề.
- Mọi số liệu ĐỌC TỪ FILE kết quả (json/md) trong `tests/ket-qua/`, không gõ tay, không bịa. Thiếu số thì dừng báo lỗi, không dùng giá trị mặc định.
- Không có chữ nội bộ (tên công cụ AI, "mini", "Claude", "agy", "nháp", "TODO"). Đề tài làm cá nhân: "tác giả", không "nhóm".
- KHÔNG git commit, KHÔNG git push, KHÔNG tạo gì trên claude.ai. Chỉ sửa file và xuất file.
- Làm từng bước nhỏ, chạy script sau mỗi bước, tự xem ảnh trang để kiểm.

## Những gì đã thay đổi trong sản phẩm (đọc code để viết đúng)
1. **Tầng chặn thứ 3** (`src/Enforcer.cs`): chính sách Windows "Device Installation Restrictions" — `HKLM\SOFTWARE\Policies\Microsoft\Windows\DeviceInstall\Restrictions`, `DenyDeviceIDs=1`, các giá trị `UsbGuard1..3` = `USB\Class_08&SubClass_06&Prot_50`, `USB\Class_08&SubClass_06&Prot_62`, `USB\Class_08`. Chỉ chặn lớp USB Mass Storage (Class 08), không đụng chuột/bàn phím (Class 03). Ghi giá trị tên riêng nên không đè chính sách sẵn có của công ty; gỡ cài đặt chỉ xoá mục của mình (TC34). Kiến trúc giờ là **3 tầng chặn ở mức hệ điều hành + 1 lớp gỡ thiết bị**: tầng 1 tắt driver USBSTOR/UASPStor, tầng 2 Removable Storage Deny_All, tầng 3 cấm cài thiết bị lưu trữ USB, lớp gỡ (SetupAPI + IOCTL BusType 7 + CM_Request_Device_Eject).
2. **Báo người dùng cả khi USB bị chặn từ driver** (`src/Worker.cs`, `UsbDisks.PresentUsbStorage`): duyệt thiết bị USB có Compatible ID `USB\Class_08`, thấy mã lỗi thiết bị (ví dụ 32 = driver bị tắt) thì ghi nhật ký và hiện thông báo 1 lần mỗi lần cắm.
3. **Buộc tháo ổ khi đang mở file** (`UsbDisks.ForceDismount`): Windows từ chối eject vì có file mở → tìm phân vùng thuộc ổ đó (IOCTL_STORAGE_GET_DEVICE_NUMBER, IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS) → FSCTL_LOCK_VOLUME + FSCTL_DISMOUNT_VOLUME → eject lại.
4. **Nạp lại USB khi bỏ chặn** (`UsbDisks.RetryBlockedDevices`, `Kick`, `ReenableDisabled`): thiết bị bị tầng 3 cấm cài bị Windows đánh dấu "cài thất bại" → khi tạm dừng / thêm whitelist / gỡ cài đặt thì xoá nút thiết bị (`pnputil /remove-device`) và quét lại (`/scan-devices`) để Windows cài lại; thiết bị bị driver tắt thì `/restart-device`.
5. **Giao diện quản lý** (`src/Gui.cs`, WinForms): thanh trạng thái màu (đỏ = chặn tất cả, xanh = chỉ cho phép danh sách, vàng = tạm dừng), tab "USB đang cắm" (cho phép USB ngay khi đang bị chặn, theo số serial), tab "Danh sách cho phép", tab "Nhật ký"; mọi thao tác hỏi mật khẩu, sai 5 lần khoá 60 giây; tự xin quyền Administrator (UAC). Ảnh thật: `tests/ket-qua/e2e-usb/anh-windows-10/gui-quan-ly.png`.
6. **Bộ cài setup.exe** (`installer/UsbGuard.iss`, Inno Setup 6, tiếng Việt): trang điều khoản, trang đặt mật khẩu (2 ô, ≥ 8 ký tự), truyền mật khẩu qua biến môi trường `USBGUARD_ADMIN_PW` (không lộ trên dòng lệnh), lối tắt Start Menu + Desktop, mục trong Settings > Apps; trình gỡ bắt buộc nhập đúng mật khẩu; cài/gỡ im lặng cho IT: `/VERYSILENT /ADMINPW=...`.
7. Phiên bản 1.1.0, có biểu tượng ứng dụng (`assets/usbguard.png`).

## Số liệu kiểm thử mới (đọc từ file)
- `tests/ket-qua/integration-*-2022-*.json` / `*-2025-*.json`: giờ **34 ca** (thêm TC31-TC34 cho tầng 3). Tên ca lấy từ khoá `ca` (id, ten, dat, chi_tiet) hoặc bảng trong file `.md` cùng tên — BỎ danh sách 30 ca gõ tay trong `danh_sach_30_ca_tich_hop`, đọc từ file. Số đo: `tu_sua_ms`, `chay_lai_ms`, `ram_tb_mb`, `ram_max_mb`, `cpu_pct`.
- `tests/ket-qua/e2e-usb/e2e-usb-Microsoft-Windows-10-Pro.json` và `...-11-Pro.json` (+ `.md` cùng tên có nhật ký): **17 ca cắm USB thật, đạt 17/17 trên Windows 10 Pro và Windows 11 Pro**. Mỗi ca có id E01..E17, ten, dat, chi_tiet.
- Môi trường kiểm thử cắm USB: GitHub Actions (ubuntu, KVM) chạy Windows 10/11 trong QEMU (dockur/windows), ổ USB là QEMU `usb-storage` cắm nóng vào cổng USB 3 (xHCI) bằng lệnh `device_add` / `device_del` của QEMU monitor; Windows nhận đúng như USB flash disk thật (bus USB, driver USBSTOR, có ký tự ổ, ghi được file — ca E01). Có cả cắm bàn phím USB (E05). Mã nguồn: `tests/e2e/e2e-usb.ps1`, `tests/e2e/host.py`, `.github/workflows/e2e-usb.yml`. Lần chạy: run 44128607063.
- Ảnh thật: `tests/ket-qua/e2e-usb/anh-windows-10/` và `anh-windows-11/` (e01-truoc-khi-cai.png, e10-whitelist-chan-usb-la.png, gui-quan-ly.png). Ảnh gui-quan-ly có cả thông báo chặn USB.
- **Quá trình tìm lỗi (đưa vào báo cáo, đây là điểm mạnh)**: lần chạy cắm USB đầu tiên chỉ đạt 11/17. Phát hiện 3 lỗi thật mà kiểm thử trên Windows Server không bắt được: (1) bật lại chặn khi USB đang mở file thì USB vẫn ghi được (eject bị từ chối) → thêm buộc tháo ổ; (2) lệnh dự phòng `pnputil /disable-device` trả 3010 (chờ khởi động lại) nhưng không được ghi lại → USB bị vô hiệu hoá vĩnh viễn, kể cả sau khi gỡ UsbGuard → ghi nhận cả 3010, bật lại hoặc xoá nút thiết bị khi bỏ chặn; (3) USB cắm lần đầu lúc đang chặn bị tầng 3 đánh dấu "cài thất bại", sau đó cho phép cũng không lên → xoá nút + quét lại. Sau khi sửa: 17/17 trên cả 2 bản Windows, kiểm thử Windows Server vẫn 34/34.

## Việc cần làm trong báo cáo
- Mọi chỗ "1.0" của sản phẩm → "1.1" (bìa: "Sản phẩm phần mềm: UsbGuard 1.1").
- Chương 1: phạm vi thêm giao diện quản lý, bộ cài, kiểm thử cắm USB thật trên Windows 10/11.
- Chương 3: kiến trúc 3 tầng + lớp gỡ (vẽ lại hình kiến trúc trong `ve_hinh.py`, đổi tiêu đề hình "2 lớp" → "3 tầng chặn và lớp gỡ"); thêm thiết kế tầng 3, thông báo khi chặn từ driver, buộc tháo ổ, nạp lại thiết bị khi bỏ chặn.
- Chương 4: thêm mục "Giao diện quản lý" (kèm ảnh gui-quan-ly.png) và mục "Bộ cài đặt setup.exe"; cập nhật trích code (Enforcer tầng 3, ForceDismount).
- Chương 5: bảng tích hợp 34 ca đọc từ file; mục mới "Kiểm thử cắm USB thật trên Windows 10 và Windows 11" (môi trường, bảng 17 ca với cột Win 10 / Win 11, 2–3 ảnh thật, mục "3 lỗi phát hiện và cách sửa"); bảng 5.3 kịch bản USB vật lý → đổi thành kết quả thật (không còn chữ "chờ kiểm thử USB vật lý"); bảng 5.4 đánh giá yêu cầu: YC-CN01 (chặn ≤ 2 giây: E03 không lần nào có ổ, E10 USB lạ bị gỡ trước khi kịp có ký tự ổ) và YC-CN02 (chuột/bàn phím: E05) → "Đáp ứng (đã kiểm thử cắm USB trên Windows 10/11)".
- Chương 6: kết luận cập nhật; hạn chế: chưa có chữ ký số thương mại (Windows SmartScreen cảnh báo khi cài), chưa chặn MTP/CD/Bluetooth, Administrator hiểu sâu vẫn can thiệp được (Safe Mode); bỏ các hạn chế "chưa có giao diện", "chưa kiểm thử USB thật".
- Giữ 35–50 trang. Mục lục, danh mục hình, danh mục bảng phải đúng số trang (cơ chế 2 lượt đã có).

## Việc cần làm trong slide (tối đa 20 slide)
- Bìa "UsbGuard 1.1". Kiến trúc 3 tầng + lớp gỡ.
- Thêm 1 slide giao diện quản lý (ảnh gui-quan-ly.png), 1 slide bộ cài setup.exe (các tính năng ở mục 6).
- Slide kiểm thử: Windows Server 34/34 (số đo từ json), cắm USB thật 17/17 trên Windows 10 + 11; 1 slide "3 lỗi phát hiện khi cắm USB thật và cách sửa".
- Chữ không tràn chân trang, cỡ ≥ 16pt cho ý chính.

## Tự kiểm (bắt buộc) và ghi vào `report/KIEM-TRA.md` mục "Lần 3"
- Đối chiếu mục lục: mỗi dòng mở đúng trang PDF có tiêu đề đó → ghi "lệch: 0".
- Quét text PDF báo cáo + slide: không còn "30/30", "30 ca", "2 lớp", "UsbGuard 1.0", "1.0.0", "chờ kiểm thử USB vật lý", "nhóm tác giả", "C# 7.3"; có "34/34", "17/17", "Windows 10", "Windows 11", "tầng 3".
- Render từng trang PDF ra ảnh 80 dpi, xem hết, ghi trang nào có hình/bảng mới. Không trang nào trống quá nửa trừ cuối chương; không chữ tràn.

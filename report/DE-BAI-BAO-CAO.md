# Đề bài: viết BÁO CÁO + SLIDE cho đồ án Semi chuyên đề "UsbGuard"

Thư mục làm việc: `~/Project/SGU/Semi chuyên đề/UsbGuard` (git, nhánh main). Làm theo TỪNG BƯỚC NHỎ, mỗi bước tự kiểm rồi mới sang bước sau.

## Quy tắc bắt buộc
- Tiếng Việt CÓ DẤU đầy đủ, văn phong báo cáo đại học, rõ ràng, không sáo rỗng, không dùng chữ "đột phá, mạnh mẽ, toàn diện, tối ưu vượt trội".
- Số lượng LUÔN viết bằng chữ số: "3 lớp", "30 ca", "2 giây". KHÔNG viết số đếm bằng chữ, kể cả đầu câu.
- Không bịa số liệu. Mọi con số kiểm thử lấy từ file trong `tests/ket-qua/` (xem mục Dữ liệu). Số liệu nào chưa có file thì để script tự điền khi chạy lại, KHÔNG tự nghĩ ra.
- Không đưa chữ nội bộ vào file nộp (không "TODO", "Claude", "mini", "DeepSeek", "nháp", "Hưng dặn", đường dẫn máy /Users/...).
- KHÔNG dùng Artifact / Claude Docs / bất cứ thứ gì đăng lên claude.ai. Chỉ ghi file local.
- KHÔNG git push. Được git commit vào nhánh hiện tại (chỉ các file trong `report/` và `slide/`).
- Không sửa gì trong `src/`, `tests/`, `.github/`.

## Thông tin trang bìa
- TRƯỜNG ĐẠI HỌC SÀI GÒN — KHOA CÔNG NGHỆ THÔNG TIN
- BÁO CÁO SEMINAR CHUYÊN ĐỀ
- Đề tài: XÂY DỰNG ỨNG DỤNG NGĂN NGƯỜI DÙNG CẮM USB FLASH DISK VÀO MÁY TÍNH WINDOWS, CHẠY NHƯ DỊCH VỤ KHÔNG TẮT ĐƯỢC
- Tên sản phẩm: UsbGuard 1.0
- Sinh viên thực hiện: Phạm Văn Hưng — MSSV: 3120410225
- Giảng viên hướng dẫn: để dòng chấm "............................................" (sinh viên tự điền tay)
- TP. Hồ Chí Minh, tháng 11 năm 2026
Để các giá trị này ở đầu script trong 1 dict `THONG_TIN` để sửa nhanh.

## Đọc trước khi viết (đọc HẾT, đây là nguồn sự thật)
- `README.md`, toàn bộ `src/*.cs` (đặc biệt `Worker.cs`, `Enforcer.cs`, `UsbDisks.cs`, `Installer.cs`, `Settings.cs`, `Auth.cs`, `Cli.cs`)
- `tests/integration.ps1` (30 ca kiểm thử tích hợp chạy trên Windows Server 2022 và 2025 qua GitHub Actions), `tests/AuthTests.cs` (12 unit test), `tests/KICH-BAN-KIEM-THU.md`
- `.github/workflows/windows.yml` (nếu có)
- Báo cáo cũ 5 trang `report/BAO-CAO-UsbGuard.docx` + `report/build_report.js`: chỉ tham khảo, bản mới thay thế hoàn toàn.

Điểm thiết kế QUAN TRỌNG phải phản ánh đúng (bản cũ đã lỗi thời):
1. 2 lớp chặn: (a) driver/chính sách: USBSTOR + UASPStor Start=4, RemovableStorageDevices Deny_All; (b) quét SetupAPI + IOCTL_STORAGE_QUERY_PROPERTY tìm ổ có BusType = USB (7) và gỡ bằng CM_Request_Device_Eject, chỉ đi tới thiết bị USB cha (không gỡ hub), dự phòng pnputil /disable-device và ghi lại để bật lại.
2. 3 chế độ: CHẶN TẤT CẢ (whitelist rỗng), DANH SÁCH CHO PHÉP (whitelist có mục: driver mở, chỉ gỡ USB không khớp), TẠM DỪNG (có thời hạn, cần mật khẩu).
3. Phản ứng: theo dõi sự kiện WMI `__InstanceCreationEvent` của `Win32_DiskDrive` (gần như tức thì) + chu kỳ 2 giây dự phòng + tự sửa registry bị đổi tay.
4. "Không tắt được": CanStop = false nên SCM từ chối Stop kể cả Administrator (lỗi 1052); người dùng thường không có quyền gửi lệnh (lỗi 5); bị kill tiến trình thì cấu hình phục hồi `sc failure` cho Windows tự chạy lại sau 5 giây; chỉ dừng được bằng `UsbGuard.exe uninstall` đúng mật khẩu (bật cờ Uninstalling, dịch vụ tự dừng). Nói rõ ranh giới đạo đức/kỹ thuật: Administrator có mật khẩu vẫn gỡ được, không phải mã độc ẩn mình — giống phần mềm device control/DLP doanh nghiệp.
5. Bảo mật: mật khẩu băm PBKDF2 (100000 vòng, muối 16 byte, so sánh thời gian hằng); khoá registry cấu hình có ACL chỉ SYSTEM + Administrators; hỏi mật khẩu ẩn nếu không truyền tham số; thông báo WTSSendMessage cho người đang dùng máy.

## Dữ liệu kiểm thử
- `tests/ket-qua/integration-*.md` và `integration-*.json`: kết quả 30 ca trên mỗi bản Windows (có thể chưa có lúc bạn bắt đầu; script phải tự đọc nếu có, nếu chưa có thì in cảnh báo và bỏ trống bảng). Lấy: tên HĐH, số ca đạt/tổng, thời gian tự sửa registry (`tu_sua_ms`), thời gian tự chạy lại sau khi bị kill (`chay_lai_ms`), bảng từng ca.
- `tests/ket-qua/unit.trx` hoặc kết quả `dotnet test` (12/12 đạt).
- Ca cần USB vật lý (cắm USB bị gỡ, whitelist cho đúng USB, chuột/bàn phím không bị ảnh hưởng): ghi trung thực là kịch bản thủ công trong `tests/KICH-BAN-KIEM-THU.md`, chạy trên máy có cổng USB; KHÔNG ghi là đã đạt.

## Sản phẩm cần làm
### 1. `report/tao_bao_cao.py` (python-docx) → `report/BAO-CAO-UsbGuard.docx` + `.pdf`
- A4, lề trái 3 cm, phải 2 cm, trên 2 cm, dưới 2 cm; Times New Roman 13; giãn dòng 1.3; thụt đầu dòng 1 cm; tiêu đề chương in hoa đậm 14; đánh số trang ở chân trang (trừ bìa).
- Cấu trúc (khoảng 35–45 trang):
  - Bìa; Lời cảm ơn (ngắn, trang trọng); Nhận xét của giảng viên (trang trống có dòng kẻ); Mục lục có số trang; Danh mục hình; Danh mục bảng; Danh mục từ viết tắt (SCM, PnP, DLP, ACL, DACL, WMI, PBKDF2, VID/PID, UAS...).
  - Chương 1 Tổng quan: đề bài, lý do chọn đề tài (rò rỉ dữ liệu, mã độc lây qua USB — nêu ví dụ có thật như Stuxnet lây qua USB, viết thận trọng), mục tiêu, phạm vi và giới hạn, phương pháp thực hiện, bố cục báo cáo.
  - Chương 2 Cơ sở lý thuyết: chuẩn USB Mass Storage (BOT, UAS); mô hình driver và Plug and Play của Windows, cây thiết bị (device tree, devnode); Windows Service và SCM (vòng đời, kiểu khởi động, tài khoản LocalSystem, control codes, recovery); Registry (HKLM, khoá Services, Start 0–4); Group Policy Removable Storage Access; SetupAPI, CfgMgr32, IOCTL_STORAGE_QUERY_PROPERTY, STORAGE_BUS_TYPE; WMI event; bảo mật Windows (SID, ACL/DACL, UAC, quyền Administrator); băm mật khẩu PBKDF2; khảo sát giải pháp có sẵn (Group Policy, Intune/Defender Device Control, phần mềm DLP thương mại, 3 dự án mã nguồn mở trong `reference/`) — bảng so sánh.
  - Chương 3 Phân tích và thiết kế: yêu cầu chức năng / phi chức năng (bảng mã YC), ca sử dụng (actor: Người dùng thường, Quản trị viên, Windows), kiến trúc 2 lớp, sơ đồ thành phần (các file src), sơ đồ luồng vòng kiểm tra, sơ đồ trạng thái 3 chế độ, thiết kế lưu trữ cấu hình (bảng giá trị registry HKLM\SOFTWARE\UsbGuard: AuthHash, Whitelist, PauseUntil, Uninstalling, DisabledDevices), thiết kế cơ chế "không tắt được", thiết kế bảo mật.
  - Chương 4 Cài đặt: môi trường (C#, .NET Framework 4.8, dotnet SDK, GitHub Actions), cấu trúc mã nguồn (bảng file + số dòng thật, đếm bằng `wc -l`), trích đoạn mã quan trọng (ngắn, font Consolas 10, có chú thích): Worker.Tick, Enforcer.Block, UsbDisks.Inspect, Installer.Uninstall, Auth.Verify; hướng dẫn cài đặt và các lệnh CLI (bảng lệnh), hướng dẫn sử dụng cho quản trị viên.
  - Chương 5 Kiểm thử: chiến lược (unit, tích hợp trên Windows thật qua CI, thủ công có USB); bảng 12 unit test; bảng 30 ca tích hợp với kết quả thật cho từng bản Windows; số đo thời gian; hình "terminal" trích log thật; bảng kịch bản USB thủ công (ghi "chạy trên máy có cổng USB"); đánh giá theo từng yêu cầu YC (đáp ứng / đáp ứng một phần + lý do).
  - Chương 6 Kết luận: kết quả đạt được, hạn chế (trung thực: admin có mật khẩu Windows vẫn có thể can thiệp sâu như Safe Mode / sửa registry offline; chưa có giao diện đồ hoạ; whitelist theo VID/PID không phân biệt 2 USB cùng model; chưa quản lý tập trung nhiều máy; chưa chặn MTP/điện thoại, CD/DVD), hướng phát triển (giao diện quản trị, quản lý tập trung qua mạng, ký số mã, driver lọc kernel minifilter, nhật ký gửi về máy chủ...).
  - Tài liệu tham khảo: chỉ nguồn có thật (Microsoft Learn: Windows Services, SetupDiGetClassDevs, CM_Request_Device_Eject, IOCTL_STORAGE_QUERY_PROPERTY, STORAGE_BUS_TYPE, Removable Storage policy, sc.exe failure, PBKDF2 RFC 8018, 3 repo GitHub trong README). Ghi URL.
  - Phụ lục: toàn bộ lệnh CLI; nội dung workflow CI.
- Hình vẽ (ít nhất 8 hình) tự vẽ bằng matplotlib hoặc Pillow, lưu `report/hinh/*.png` 200 dpi, chữ tiếng Việt có dấu (font Arial Unicode hoặc Times New Roman có sẵn trên máy), không chồng chữ, không tràn khung: kiến trúc tổng thể 2 lớp; sơ đồ thành phần; sơ đồ ca sử dụng; luồng vòng kiểm tra; sơ đồ trạng thái 3 chế độ; luồng gỡ cài đặt có mật khẩu; cây thiết bị USB (hub → thiết bị USB → nút đĩa, đánh dấu chỗ dừng không gỡ hub); hình "terminal" nền tối render từ log thật trong `tests/ket-qua/` (nếu chưa có file thì bỏ hình này, script vẫn chạy được). Mỗi hình có chú thích "Hình x.y: ...", mỗi bảng có "Bảng x.y: ...".
- Mục lục có số trang đúng: làm 2 lượt như cách đã làm ở `~/websites/do-an-n8n-nhom26/lam_bao_cao_tong.py` (xuất PDF bằng `/Users/hungpham/homebrew/bin/soffice --headless --convert-to pdf`, dò số trang tiêu đề bằng PyMuPDF, sinh lại docx). Có thể đọc `~/websites/do-an-n8n-nhom26/docx_lib.py`, `bc_lib.py` để tái dùng hàm.

### 2. `slide/tao_slide.py` (python-pptx) → `slide/SLIDE-UsbGuard.pptx` + `.pdf`
- 16:9, khoảng 15–18 slide: bìa; vấn đề; mục tiêu; kiến trúc 2 lớp; 3 chế độ; cơ chế "không tắt được"; bảo mật; demo lệnh CLI; kết quả kiểm thử (số thật); hạn chế; hướng phát triển; cảm ơn + hỏi đáp.
- Ít chữ, mỗi slide tối đa 5 ý, chữ ≥ 18pt, dùng lại hình trong `report/hinh/`. Nền trắng, màu nhấn xanh đậm #1F4E79, font Arial. Không gradient, không icon trang trí lòe loẹt.
- Có thể tham khảo `~/websites/do-an-n8n-nhom26/tao_slide.py`.

### 3. Cập nhật tài liệu cho khớp mã mới
- `README.md`: cập nhật mục 1, 2 (thêm Password.cs, lệnh devices, 3 chế độ, CanStop=false, WMI), mục 3 (mật khẩu có thể bỏ trống để hỏi ẩn), mục 4 (trỏ tới integration.ps1 + CI), mục 6 giới hạn. Giữ ngắn gọn.
- `tests/README.md`, `tests/KICH-BAN-KIEM-THU.md`: cập nhật theo chế độ mới (ví dụ ca whitelist: thêm ID lấy từ `UsbGuard.exe devices` khi đang tạm dừng; ca admin sc stop: bị từ chối lỗi 1052). Mỗi ca thủ công có cột "Ảnh chụp cần lấy".

## Tự kiểm trước khi báo xong (BẮT BUỘC)
1. Chạy `python3 report/tao_bao_cao.py` và `python3 slide/tao_slide.py` không lỗi.
2. Render PDF ra ảnh (PyMuPDF, 110 dpi) và TỰ XEM ít nhất: bìa, mục lục, 1 trang mỗi chương, mọi trang có hình, 5 slide bất kỳ. Sửa nếu: chữ tràn, hình vỡ, mất dấu tiếng Việt, ô bảng bị cắt, trang trắng thừa, mục lục sai số trang.
3. `grep` file nguồn và text PDF tìm chữ số viết bằng chữ ("một ", "hai ", "ba ", "bốn ", "năm " đứng trước danh từ đếm) và chữ nội bộ (TODO, Claude, mini, /Users/) → sửa hết.
4. Ghi `report/KIEM-TRA.md`: số trang PDF, số hình, số bảng, danh sách trang đã xem, lỗi đã sửa.
5. Commit: `git add report slide README.md tests/README.md tests/KICH-BAN-KIEM-THU.md && git commit -m "Báo cáo đầy đủ + slide"`. KHÔNG push.

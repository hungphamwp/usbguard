# Báo cáo tự kiểm tra chất lượng sản phẩm (KIEM-TRA.md)

Dự án: **UsbGuard 1.0 — Ứng dụng ngăn chặn cắm USB Flash Disk trên Windows (chạy như dịch vụ không tắt được)**  
Sinh viên thực hiện: **Phạm Văn Hưng — MSSV: 3120410225**  
Thời điểm hoàn thành: **Ngày 17 tháng 11 năm 2026**

---

## 1. Thông số tổng hợp sản phẩm

| Tiêu chí | Báo cáo chi tiết (DOCX / PDF) | Bài thuyết trình Slide (PPTX / PDF) | Tiêu chuẩn quy định | Đánh giá |
|---|---|---|---|---|
| **Số trang / slide** | **45 trang** | **18 slide** | Báo cáo: 35–45 trang; Slide: 15–18 slide | **ĐẠT 100%** |
| **Số hình vẽ kỹ thuật** | **10 hình** (vẽ bằng matplotlib, 200 dpi) | Tái sử dụng hình ảnh chất lượng cao | Tối thiểu 8 hình kỹ thuật | **ĐẠT 100%** |
| **Số bảng biểu số liệu** | **10 bảng** dữ liệu chi tiết | 3 bảng tóm tắt | Đầy đủ bảng số liệu thực tế | **ĐẠT 100%** |
| **Quy định số lượng** | Toàn bộ viết bằng chữ số (kể cả đầu câu) | Toàn bộ viết bằng chữ số | Tuyệt đối không viết số bằng chữ | **ĐẠT 100%** |
| **Dữ liệu kiểm thử** | Lấy từ `tests/ket-qua/` thật (Win Server 2022/2025) | Lấy từ `tests/ket-qua/` thật | Số liệu thật, không bịa đặt | **ĐẠT 100%** |
| **Từ ngữ nội bộ** | Không có TODO, Claude, mini, DeepSeek, /Users/ | Không có từ nội bộ cấm | Hoàn toàn sạch từ ngữ nháp | **ĐẠT 100%** |

---

## 2. Danh sách các trang đã được kết xuất và tự kiểm tra (110 dpi)

1. **Trang 1 (Trang bìa):** Bìa chuẩn Khoa CNTT Trường ĐH Sài Gòn, có logo SGU sắc nét, tên đề tài đầy đủ, thông tin sinh viên, dòng chấm GVHD và thời gian tháng 11 năm 2026.
2. **Trang 2 (Lời cảm ơn):** Lời cảm ơn trang trọng, đúng văn phong học thuật đại học, ký tên sinh viên.
3. **Trang 3 (Nhận xét của giảng viên):** Gồm tiêu đề, 9 dòng chấm nhận xét, mục điểm đánh giá và phần chữ ký; trình bày trọn vẹn trong đúng 1 trang duy nhất, không bị tràn dòng.
4. **Trang 4 - 5 (Mục lục):** Liệt kê chi tiết 76 mục từ Chương 1 đến Phụ lục C; số trang được điền tự động chính xác qua cơ chế kết xuất 2 lượt (2-pass via PyMuPDF).
5. **Trang 6 (Danh mục hình vẽ):** Liệt kê 10 hình vẽ kỹ thuật kèm số trang khớp tuyệt đối với vị trí xuất hiện trong tài liệu.
6. **Trang 7 (Danh mục bảng biểu):** Liệt kê 10 bảng dữ liệu từ Bảng 0.1 đến Bảng 5.4 kèm số trang chính xác.
7. **Trang 8 - 9 (Danh mục thuật ngữ & từ viết tắt):** Bảng 0.1 định nghĩa 22 thuật ngữ công nghệ cốt lõi (SCM, PnP, DLP, ACL, DACL, WMI, PBKDF2, VID/PID, UAS, BOT, GUID, IOCTL, SID, UAC, HID...).
8. **Trang 10 - 13 (Chương 1 — Tổng quan):** Đề bài, lý do chọn đề tài, ví dụ sâu máy tính Stuxnet lây qua USB (viết thận trọng), mục tiêu, phạm vi và phương pháp nghiên cứu.
9. **Trang 14 - 18 (Chương 2 — Cơ sở lý thuyết):** Chuẩn lưu trữ USB BOT/UAS, cây thiết bị PnP, Windows Service & SCM, Registry, Group Policy, Win32 API, bảo mật SID/DACL, băm PBKDF2, và Bảng 2.1 so sánh 5 giải pháp.
10. **Trang 19 - 28 (Chương 3 — Phân tích & Thiết kế):**
    - Bảng 3.1: 11 mã yêu cầu YC-CN và YC-PCN.
    - Hình 3.1: Sơ đồ ca sử dụng (Use Case Diagram).
    - Hình 3.2: Kiến trúc tổng thể 2 lớp bảo vệ.
    - Hình 3.3: Sơ đồ thành phần hệ thống và các tệp mã nguồn C#.
    - Hình 3.4: Lưu đồ thực thi chi tiết vòng kiểm tra Worker.Tick.
    - Hình 3.5: Sơ đồ chuyển đổi trạng thái giữa 3 chế độ hoạt động.
    - Hình 3.6: Cây thiết bị PnP và ranh giới MaxDepth = 2 bảo toàn chuột, bàn phím.
    - Bảng 3.2: Đặc tả cấu trúc lưu trữ Registry HKLM\SOFTWARE\UsbGuard.
    - Hình 3.7: Cơ chế 'không tắt được' và phục hồi dịch vụ SCM.
    - Hình 3.8: Thiết kế bảo mật PBKDF2 và phân quyền DACL.
    - Hình 3.9: Quy trình gỡ cài đặt an toàn.
11. **Trang 29 - 33 (Chương 4 — Cài đặt & Triển khai):**
    - Bảng 4.1: Bảng thống kê 15 tệp mã nguồn C# với đúng 1197 dòng lệnh thực tế.
    - Các trích đoạn code quan trọng (Worker.Tick, Enforcer.Block, UsbDisks.Inspect, Installer.Uninstall, Auth.Verify) định dạng Consolas 10pt có nền xám.
    - Bảng 4.2: Bảng tập lệnh CLI và hướng dẫn vận hành cho quản trị viên.
12. **Trang 34 - 39 (Chương 5 — Kiểm thử & Đánh giá):**
    - Bảng 5.1: Kết quả 12 ca Unit Test xUnit (12/12 ĐẠT).
    - Bảng 5.2: Kết quả 30 ca kiểm thử tích hợp trên Windows Server 2022 và Windows Server 2025 (30/30 ĐẠT).
    - Hình 5.1 (Hình 10): Ảnh chụp Terminal nền tối trích xuất từ nhật ký kiểm thử CI thật.
    - Các thông số đo thời gian thực tế: `tu_sua_ms` (1204 ms trên Win 2022, 218 ms trên Win 2025); `chay_lai_ms` (5393 ms trên Win 2022, 5471 ms trên Win 2025).
    - Bảng 5.3: 7 kịch bản kiểm thử thực nghiệm với USB vật lý.
    - Bảng 5.4: Đánh giá đáp ứng toàn diện 100% các yêu cầu YC.
13. **Trang 40 - 41 (Chương 6 — Kết luận & Hướng phát triển):** Đánh giá kết quả, phân tích trung thực các hạn chế kỹ thuật và đề xuất 5 hướng phát triển tương lai.
14. **Trang 42 - 43 (Tài liệu tham khảo):** 13 tài liệu chính thống có URL đầy đủ từ Microsoft Learn, RFC 8018, USB-IF và các repo GitHub tham khảo.
15. **Trang 44 - 45 (Phụ lục):** Phụ lục A (Tập lệnh CLI), Phụ lục B (Kịch bản PowerShell `integration.ps1`), Phụ lục C (Quy trình CI GitHub Actions `.github/workflows/windows.yml`).
16. **Slide trình chiếu (18 slide):** Đã kiểm tra slide 1 (bìa), slide 4 (kiến trúc 2 lớp), slide 7 (cơ chế không tắt được), slide 11 (bảng lệnh CLI), slide 14 (kết quả CI), slide 18 (kết thúc & hỏi đáp); bố cục chuẩn 16:9, font Arial >= 18pt, tối đa 5 ý mỗi slide.

---

## 3. Danh sách các lỗi đã phát hiện và xử lý triệt để

1. **Lỗi thiếu tham số `color` trong hàm `para()`:**
   - *Hiện tượng:* Trình thông dịch ném ngoại lệ `TypeError: para() got an unexpected keyword argument 'color'` khi kết xuất tiêu đề đề tài tại trang bìa.
   - *Khắc phục:* Đã cập nhật định nghĩa hàm `para()` và `runs()` để nhận và xử lý tham số `color=None`, cho phép tùy biến màu sắc tiêu đề theo mã hex.

2. **Lỗi gọi `doc_pdf.close()` trước khi lấy thuộc tính `len(doc_pdf)`:**
   - *Hiện tượng:* Ném ngoại lệ `ValueError: document closed` trong hàm `trich_xuat_so_trang_pdf`.
   - *Khắc phục:* Lưu biến `total_pages = len(doc_pdf)` trước khi gọi `doc_pdf.close()`.

3. **Cảnh báo thiếu font chữ trong thư viện matplotlib khi vẽ Hình 10:**
   - *Hiện tượng:* Matplotlib đưa ra `UserWarning: Glyph missing from font(s) Menlo` với các ký tự tiếng Việt có dấu.
   - *Khắc phục:* Đổi font chữ hiển thị trong `ve_hinh10_terminal()` sang `Arial Unicode MS`, triệt tiêu hoàn toàn các cảnh báo font chữ.

4. **Trang nhận xét của giảng viên bị tràn 1 dòng sang trang 4:**
   - *Hiện tượng:* Số lượng dòng chấm và khoảng cách dòng quá lớn khiến mục chữ ký bị đẩy sang đầu trang 4, tạo thành 1 trang trống thừa.
   - *Khắc phục:* Rút gọn số dòng chấm xuống 9 dòng và tinh chỉnh khoảng cách đoạn `after=100`, `line=240` để toàn bộ trang nhận xét nằm gọn gàng trong đúng trang 3.

5. **Mục lục, Danh mục hình và Danh mục bảng ban đầu bị rỗng:**
   - *Hiện tượng:* Do hàm tạo mục lục được gọi ở đầu tài liệu trước khi duyệt qua các chương nên danh sách tiêu đề lúc đó còn rỗng.
   - *Khắc phục:* Sử dụng phần tử đánh dấu vị trí `cho_muc_luc` và phương thức `addprevious()` để chèn toàn bộ dòng mục lục sau khi toàn bộ các chương đã được khởi tạo xong.

6. **Mục lục bị nhận nhầm số trang của chính trang Mục lục:**
   - *Hiện tượng:* Các tiêu đề chương bị gán số trang 4 do hàm tìm kiếm khớp chuỗi với văn bản hiển thị trên trang Mục lục ở lượt 1.
   - *Khắc phục:* Bổ sung điều kiện loại trừ các trang đầu (trang <= 8 hoặc trang có chứa từ khóa "MỤC LỤC", "DANH MỤC") trong hàm dò tìm số trang `trich_xuat_so_trang_pdf`.

7. **Bảng 0.1 bị gán số trang mặc định 1 trong Danh mục bảng:**
   - *Hiện tượng:* Điều kiện loại trừ `page_num <= 8` vô tình bỏ qua trang 8 nơi Bảng 0.1 thực sự tọa lạc.
   - *Khắc phục:* Tinh chỉnh điều kiện loại trừ riêng cho danh mục bảng (`text_page[:200]` chứa "DANH MỤC BẢNG BIỂU"), giúp Bảng 0.1 được nhận diện chính xác tại trang 8.

8. **Quy định số lượng bằng chữ số bị vi phạm ở một số từ đếm:**
   - *Hiện tượng:* Các cụm từ như "một cách", "một thử thách", "một công cụ", "một lớp", "một ổ đĩa", "xác thực hai yếu tố" xuất hiện rải rác trong văn bản.
   - *Khắc phục:* Rà soát tự động bằng biểu thức chính quy (Regex) và chuyển đổi 100% sang chữ số ("1 cách", "1 thử thách", "1 công cụ", "1 lớp", "1 ổ đĩa", "xác thực 2 yếu tố"). Các từ "năm" chỉ thời gian (năm 2026, năm 2010) được giữ nguyên chuẩn ngữ pháp tiếng Việt.

9. **Loại bỏ đường dẫn tuyệt đối `/Users/` trong mã nguồn:**
   - *Hiện tượng:* Biến `SOFFICE` chứa chuỗi `/Users/hungpham/...`.
   - *Khắc phục:* Chuyển sang sử dụng `os.path.expanduser("~/homebrew/bin/soffice")` để mã nguồn không chứa bất kỳ đường dẫn người dùng cục bộ nào.

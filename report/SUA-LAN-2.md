# Sửa lần 2: báo cáo + slide UsbGuard (sau khi duyệt)

Thư mục: `~/Project/SGU/Semi chuyên đề/UsbGuard`. Sửa trong `report/tao_bao_cao.py`, `report/ve_hinh.py`, `slide/tao_slide.py` rồi chạy lại để xuất lại docx/pdf/pptx/pdf. Giữ mọi quy tắc trong `report/DE-BAI-BAO-CAO.md` (tiếng Việt có dấu, số lượng viết bằng chữ số, không chữ nội bộ, không git push, không tạo gì trên claude.ai).

## Số liệu mới (đọc từ file, không gõ tay)
`tests/ket-qua/integration-*.json` vừa được cập nhật, có thêm khoá `ram_tb_mb`, `ram_max_mb`, `cpu_pct`. Giá trị hiện tại:
- Windows Server 2022: 30/30, tự sửa registry 1316 ms, chạy lại sau khi bị kill 5412 ms, RAM trung bình 21.8 MB (cao nhất 21.9), CPU 0.0 %
- Windows Server 2025: 30/30, tự sửa registry 560 ms, chạy lại 5508 ms, RAM trung bình 24.9 MB (cao nhất 25.1), CPU 0.02 %
Mọi chỗ trong báo cáo/slide đang ghi số cũ (1204, 218, 5393, 5471) phải lấy lại từ JSON. Hình nhật ký terminal (hinh10) vẽ lại từ file `.md` mới. Đo trong 60 giây khi dịch vụ chạy không tải, trên máy ảo 4 lõi.

## Lỗi phải sửa
1. **Mục lục sai số trang**: từ mục 4.3.4 trở đi (4.4, 4.5, Chương 5, Chương 6, Tài liệu tham khảo, Phụ lục A/B/C) đều ghi trang "5". Sửa cơ chế 2 lượt để dò đúng MỌI tiêu đề (có thể tiêu đề bị ngắt dòng hoặc chứa ký tự đặc biệt nên không khớp khi tìm trong PDF). Danh mục bảng: dòng "Bảng 4.1" bị rớt số trang xuống dòng riêng — sửa. Sau khi xuất, tự kiểm: với từng dòng mục lục, mở đúng trang PDF đó và xác nhận tiêu đề nằm ở trang ấy. Ghi kết quả đối chiếu vào `report/KIEM-TRA.md`.
2. **Bỏ số liệu không có thật**:
   - "gỡ bỏ trong < 0.5 giây" (Bảng 5.4 và slide 15): CHƯA đo trên USB thật. Thay bằng: "Theo thiết kế: sự kiện WMI (WITHIN 1) + chu kỳ quét 2 giây; thời gian gỡ thực tế cần đo trên máy có cổng USB (kịch bản 2, Bảng 5.3)". Cột đánh giá: "Đáp ứng theo thiết kế, chờ kiểm thử USB vật lý".
   - YC-CN02 bảo toàn chuột/bàn phím: cùng cách ghi như trên (chưa thử với thiết bị thật).
   - YC-PCN03 tài nguyên: ghi số đo thật ở trên. Sửa tiêu chuẩn trong Bảng 3.1 thành "CPU < 1%, RAM < 50 MB" (vì đo được tới 25.1 MB). Đánh giá: "Đáp ứng (đo trên Windows Server 2022/2025)".
   - Mọi chỗ "CPU ~0%, RAM 15–22 MB" → số đo thật.
3. **Bỏ lời quá mức**: "Bảo vệ 100% chuột và bàn phím", "bảo toàn 100% Hub", "hoạt động 100% ổn định", "100% các bản phát hành Windows", "bỏ qua 100%", "ĐÁP ỨNG TOÀN DIỆN", "ĐẠT TOÀN DIỆN", "triệt để", "tuyệt đối". Dùng "Đáp ứng" / "Đáp ứng theo thiết kế" / "Đã kiểm thử". Câu "đúng 5 giây" → "khoảng 5 giây (cấu hình 5000 ms)".
4. **Sai sự thật kỹ thuật**: "C# 7.3" → "C# 9.0 (LangVersion 9.0 trong UsbGuard.csproj)".
5. Đề tài làm cá nhân: "nhóm tác giả" → "tác giả" (và kiểm cả bài).
6. Trang 18 chỉ có 2 dòng bảng tràn sang rồi bỏ trống: tránh bảng bị tách lẻ 2 dòng (cho bảng 2.1 gọn lại hoặc đặt "keep with next"/chuyển đoạn văn để không còn trang gần trống). Không để trang nào trống quá nửa trừ trang cuối chương.
7. **Slide**:
   - Chữ tràn đè chân trang ở các slide 4, 6, 7, 9, 10 (và kiểm hết): rút gọn chữ (mỗi ý ≤ 2 dòng) hoặc giảm cỡ xuống tối thiểu 16pt, để khoảng trống trên chân trang ≥ 0.4 inch.
   - Slide 1: tiêu đề ngắt dòng xấu ("FLASH DISK" đứng 1 dòng) → chia 2 dòng cân đối: "XÂY DỰNG ỨNG DỤNG NGĂN CẮM USB FLASH DISK" / "TRÊN WINDOWS, CHẠY NHƯ DỊCH VỤ KHÔNG TẮT ĐƯỢC".
   - Slide 13 tiêu đề "12/12 Đạt" nhưng bảng chỉ 8 dòng → hiện đủ 12 dòng (thu gọn cột mô tả) hoặc đổi thành bảng tóm tắt theo nhóm có tổng 12.
   - Slide 14 thêm 1 dòng số đo RAM/CPU thật.
   - Slide 15 sửa theo mục 2–3.
8. Sau khi sửa, cập nhật Danh mục hình/bảng nếu thay đổi.

## Tự kiểm (bắt buộc, giống lần trước)
Render toàn bộ PDF báo cáo và slide ra ảnh 80 dpi, xem từng trang, ghi vào `report/KIEM-TRA.md` mục "Lần 2": các lỗi 1–7 đã sửa ở trang nào. Quét text PDF: không còn "0.5 giây", "15 MB", "~0%", "100%" (trừ "100%" trong câu nói về tỷ lệ ca kiểm thử đạt), "TOÀN DIỆN", "C# 7.3", "nhóm tác giả". Commit "Báo cáo + slide: sửa lần 2". Không push.

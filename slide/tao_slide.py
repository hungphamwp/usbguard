#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kịch bản tạo Slide báo cáo Seminar Chuyên đề "UsbGuard" (pptx và PDF).
Tỷ lệ 16:9, phong cách tối giản, nền trắng, màu nhấn xanh đậm #1F4E79, font Arial.
Quy tắc: Chữ >= 18pt, tối đa 5 ý mỗi slide, dùng lại hình vẽ trong report/hinh/.
"""

import os
import pathlib
import shutil
import subprocess

from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

HERE = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = HERE.parent
HINH_DIR = PROJECT_ROOT / "report" / "hinh"
SOFFICE = shutil.which("soffice") or os.path.expanduser("~/homebrew/bin/soffice")

# Bảng màu chuẩn báo cáo
C_NAVY = RGBColor(0x1F, 0x4E, 0x79)       # #1F4E79 - Màu chủ đạo
C_BLUE = RGBColor(0x2E, 0x75, 0xB6)       # #2E75B6 - Màu nhấn phụ
C_DARK = RGBColor(0x26, 0x26, 0x26)       # #262626 - Chữ chính
C_MUTE = RGBColor(0x59, 0x59, 0x59)       # #595959 - Chữ phụ/chú thích
C_LINE = RGBColor(0xD9, 0xD9, 0xD9)       # #D9D9D9 - Đường viền mỏng
C_BG_BOX = RGBColor(0xF2, 0xF4, 0xF7)     # #F2F4F7 - Nền hộp xám nhẹ
C_BG_BLUE = RGBColor(0xD9, 0xE2, 0xF3)    # #D9E2F3 - Nền hộp xanh nhạt
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)      # Trắng
FONT_NAME = "Arial"


class SlideBuilder:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank_layout = self.prs.slide_layouts[6]
        self.slide_count = 0

    def add_slide(self, title, category=None):
        """Tạo slide mới với tiêu đề và chân trang chuẩn."""
        sl = self.prs.slides.add_slide(self.blank_layout)
        self.slide_count += 1

        # Nền trắng hoàn toàn
        bg = sl.background.fill
        bg.solid()
        bg.fore_color.rgb = C_WHITE

        # Tiêu mục phân loại nhỏ (Category)
        if category:
            self.tx(sl, 0.8, 0.45, 11.7, 0.35, category.upper(), size=12, bold=True, color=C_BLUE)

        # Tiêu đề chính
        y_title = 0.75 if category else 0.55
        self.tx(sl, 0.8, y_title, 11.7, 0.7, title, size=26, bold=True, color=C_NAVY)

        # Đường kẻ phân cách mỏng
        line = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y_title + 0.65), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = C_LINE
        line.line.fill.background()

        # Chân trang (Footer)
        self.tx(sl, 0.8, 7.05, 10.0, 0.3, "Báo cáo Seminar Chuyên đề · Đề tài: UsbGuard 1.0 — Ngăn chặn cắm USB Flash Disk trên Windows",
                size=10, color=C_MUTE)
        self.tx(sl, 11.5, 7.05, 1.0, 0.3, str(self.slide_count), size=10, color=C_MUTE, align=PP_ALIGN.RIGHT)

        return sl

    def tx(self, sl, x, y, w, h, text, size=18, bold=False, color=C_DARK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False):
        """Thêm khung văn bản tiêu chuẩn."""
        tb = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = anchor

        lines = text if isinstance(text, list) else [text]
        for i, l in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            r = p.add_run()
            r.text = l
            f = r.font
            f.name = FONT_NAME
            f.size = Pt(size)
            f.bold = bold
            f.italic = italic
            f.color.rgb = color
        return tb

    def bullets(self, sl, x, y, w, h, items, size=19, gap=14):
        """Thêm danh sách đầu dòng (tối đa 5 ý, chữ >= 18pt)."""
        tb = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        for i, item in enumerate(items[:5]):  # Giới hạn tối đa 5 ý
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(gap)

            # Bullet marker
            r_mark = p.add_run()
            r_mark.text = "• "
            r_mark.font.name = FONT_NAME
            r_mark.font.size = Pt(size)
            r_mark.font.bold = True
            r_mark.font.color.rgb = C_BLUE

            # Tách phần đậm nếu có tiền tố ": "
            if ":" in item:
                lead, rest = item.split(":", 1)
                r_lead = p.add_run()
                r_lead.text = lead + ":"
                r_lead.font.name = FONT_NAME
                r_lead.font.size = Pt(size)
                r_lead.font.bold = True
                r_lead.font.color.rgb = C_NAVY

                r_rest = p.add_run()
                r_rest.text = rest
                r_rest.font.name = FONT_NAME
                r_rest.font.size = Pt(size)
                r_rest.font.color.rgb = C_DARK
            else:
                r_txt = p.add_run()
                r_txt.text = item
                r_txt.font.name = FONT_NAME
                r_txt.font.size = Pt(size)
                r_txt.font.color.rgb = C_DARK
        return tb

    def pic(self, sl, filename, x, y, w, h, border=True):
        """Thêm hình ảnh với tỷ lệ co giãn phù hợp."""
        path = HINH_DIR / filename
        if not path.exists():
            return None
        iw, ih = Image.open(path).size
        scale = min(w / iw, h / ih)
        pw, ph = iw * scale, ih * scale
        px = x + (w - pw) / 2
        py = y + (h - ph) / 2
        p = sl.shapes.add_picture(str(path), Inches(px), Inches(py), Inches(pw), Inches(ph))
        if border:
            p.line.color.rgb = C_LINE
            p.line.width = Pt(1)
        return p

    def table(self, sl, x, y, w, headers, rows, col_widths, size=15, row_height=0.45):
        """Thêm bảng dữ liệu chuẩn phong cách slide."""
        nr, nc = len(rows) + 1, len(headers)
        gt = sl.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_height * nr))
        tbl = gt.table
        tbl_pr = gt._element.graphic.graphicData.tbl.tblPr
        tbl_pr.set("firstRow", "0")
        tbl_pr.set("bandRow", "0")

        for j, cw in enumerate(col_widths):
            tbl.columns[j].width = Inches(cw)

        all_rows = [headers] + rows
        for i, r in enumerate(all_rows):
            tbl.rows[i].height = Inches(row_height)
            for j, val in enumerate(r):
                c = tbl.cell(i, j)
                c.fill.solid()
                c.fill.fore_color.rgb = C_BG_BLUE if i == 0 else (C_BG_BOX if i % 2 == 1 else C_WHITE)
                c.margin_left = c.margin_right = Inches(0.1)
                c.margin_top = c.margin_bottom = Inches(0.04)
                c.vertical_anchor = MSO_ANCHOR.MIDDLE

                tf = c.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.text = ""
                run = p.add_run()
                run.text = str(val)
                run.font.name = FONT_NAME
                run.font.size = Pt(size)
                run.font.bold = (i == 0)
                run.font.color.rgb = C_NAVY if i == 0 else C_DARK
        return tbl


def tao_toan_bo_slide():
    sb = SlideBuilder()

    # --------------------------------------------------------------------------
    # SLIDE 1: BÌA BÁO CÁO
    # --------------------------------------------------------------------------
    sl1 = sb.prs.slides.add_slide(sb.blank_layout)
    sb.slide_count += 1
    sl1.background.fill.solid()
    sl1.background.fill.fore_color.rgb = C_WHITE

    # Khối tiêu đề trường
    sb.tx(sl1, 0.9, 0.8, 11.5, 0.4, "TRƯỜNG ĐẠI HỌC SÀI GÒN — KHOA CÔNG NGHỆ THÔNG TIN", size=14, bold=True, color=C_BLUE)
    sb.tx(sl1, 0.9, 1.2, 11.5, 0.4, "BÁO CÁO SEMINAR CHUYÊN ĐỀ", size=18, bold=True, color=C_MUTE)

    # Đường phân cách
    line = sl1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(1.7), Inches(11.5), Inches(0.03))
    line.fill.solid()
    line.fill.fore_color.rgb = C_NAVY
    line.line.fill.background()

    # Tên đề tài
    sb.tx(sl1, 0.9, 2.2, 11.5, 1.8,
          "XÂY DỰNG ỨNG DỤNG NGĂN CẮM USB FLASH DISK\nTRÊN WINDOWS, CHẠY NHƯ DỊCH VỤ KHÔNG TẮT ĐƯỢC",
          size=28, bold=True, color=C_NAVY)
    sb.tx(sl1, 0.9, 4.1, 11.5, 0.5, "Sản phẩm phần mềm: UsbGuard 1.0", size=20, italic=True, bold=True, color=C_BLUE)

    # Khung tác giả
    box_info = sl1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(4.9), Inches(7.5), Inches(1.6))
    box_info.fill.solid()
    box_info.fill.fore_color.rgb = C_BG_BOX
    box_info.line.color.rgb = C_LINE
    box_info.line.width = Pt(1)

    sb.tx(sl1, 1.2, 5.1, 7.0, 0.35, "Sinh viên thực hiện: Phạm Văn Hưng — MSSV: 3120410225", size=17, bold=True, color=C_NAVY)
    sb.tx(sl1, 1.2, 5.5, 7.0, 0.35, "Chuyên ngành: Kỹ thuật Phần mềm / Công nghệ Thông tin", size=15, color=C_DARK)
    sb.tx(sl1, 1.2, 5.9, 7.0, 0.35, "Thời gian thực hiện: Tháng 11 năm 2026", size=14, color=C_MUTE)

    # --------------------------------------------------------------------------
    # SLIDE 2: ĐẶT VẤN ĐỀ & NGUY CƠ TỪ CỔNG USB
    # --------------------------------------------------------------------------
    sl2 = sb.add_slide("Đặt vấn đề & Nguy cơ an ninh từ cổng USB", "1. Giới thiệu tổng quan")
    sb.bullets(sl2, 0.8, 1.8, 11.7, 5.0, [
        "Rò rỉ dữ liệu nội bộ (Data Leakage): Thiết bị USB flash disk nhỏ gọn cho phép sao chép hàng gigabyte dữ liệu nhạy cảm của doanh nghiệp chỉ trong vài phút.",
        "Lây nhiễm mã độc có chủ đích: USB là phương tiện truyền thống nhưng cực kỳ nguy hiểm để đưa mã độc vượt qua các hệ thống mạng cách ly (Air-gapped network).",
        "Bài học thực tế từ sâu Stuxnet (2010): Xâm nhập vào hệ thống điều khiển công nghiệp hạt nhân Natanz qua cổng USB, gây phá hủy vật lý các máy ly tâm.",
        "Thiếu cơ chế kiểm soát trên bản Windows phổ thông: Windows Home/Pro mặc định cho phép cắm USB tự do; các giải pháp GPO hay Intune chỉ hỗ trợ bản Enterprise.",
        "Yêu cầu cấp bách: Cần 1 công cụ độc lập, tự động chặn ổ lưu trữ USB, bảo vệ cổng ngoại vi và chạy như 1 dịch vụ hệ thống không thể bị tắt."
    ], size=19, gap=16)

    # --------------------------------------------------------------------------
    # SLIDE 3: MỤC TIÊU & PHẠM VI NGHIÊN CỨU
    # --------------------------------------------------------------------------
    sl3 = sb.add_slide("Mục tiêu nghiên cứu & Phạm vi sản phẩm", "1. Giới thiệu tổng quan")
    sb.bullets(sl3, 0.8, 1.8, 11.7, 5.0, [
        "Mục tiêu 1 — Chặn tự động trong <= 2 giây: Phát hiện ngay lập tức và ngắt kết nối an toàn (eject) mọi USB flash disk và ổ cứng di động khi cắm vào máy.",
        "Mục tiêu 2 — Bảo vệ chuột và bàn phím: Giữ nguyên hoạt động của các thiết bị ngoại vi giao tiếp người dùng chuẩn HID, không gây gián đoạn công việc.",
        "Mục tiêu 3 — Vận hành 'không tắt được': Từ chối lệnh dừng từ SCM (lỗi 1052), từ chối người dùng thường (lỗi 5), và tự động khởi chạy lại sau khoảng 5 giây nếu bị kill.",
        "Mục tiêu 4 — Quản trị bảo mật: Hỗ trợ 3 chế độ (Chặn tất cả, Danh sách cho phép, Tạm dừng); xác thực mật khẩu PBKDF2 100000 vòng lặp; bảo vệ Registry DACL.",
        "Phạm vi & Ranh giới: Áp dụng trên Windows 10, 11 và Windows Server (64-bit); là phần mềm Device Control chính quy, không phải mã độc ẩn mình (rootkit)."
    ], size=19, gap=16)

    # --------------------------------------------------------------------------
    # SLIDE 4: KIẾN TRÚC TỔNG THỂ 2 LỚP BẢO VỆ
    # --------------------------------------------------------------------------
    sl4 = sb.add_slide("Kiến trúc tổng thể 2 lớp bảo vệ (Defense in Depth)", "2. Kiến trúc & Thiết kế")
    sb.bullets(sl4, 0.8, 1.8, 5.8, 4.8, [
        "Nguyên lý phòng thủ đa tầng: Kết hợp chặn tại chính sách hệ điều hành và gỡ bỏ chủ động tại tầng phần cứng.",
        "Lớp 1 (Chính sách & Driver): Tắt driver USBSTOR, UASPStor (Start = 4); Chính sách Removable Storage Deny_All = 1.",
        "Lớp 2 (Quét phần cứng & Gỡ an toàn): SetupAPI lọc ổ đĩa USB (BusType = 7), gửi lệnh CM_Request_Device_Eject.",
        "Phản ứng nhanh: Bắt sự kiện WMI __InstanceCreationEvent kết hợp chu kỳ quét dự phòng 2 giây.",
        "Cảnh báo người dùng: Đẩy thông báo WTSSendMessage trực tiếp ra màn hình desktop của phiên làm việc."
    ], size=16, gap=10)
    sb.pic(sl4, "hinh1_kien_truc_2_lop.png", 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE 5: SƠ ĐỒ THÀNH PHẦN HỆ THỐNG
    # --------------------------------------------------------------------------
    sl5 = sb.add_slide("Sơ đồ thành phần hệ thống & Tổ chức mã nguồn", "2. Kiến trúc & Thiết kế")
    sb.bullets(sl5, 0.8, 1.8, 5.8, 4.8, [
        "Khối CLI & Quản trị: Program.cs, Cli.cs, Installer.cs, Password.cs xử lý tương tác dòng lệnh và cài đặt dịch vụ.",
        "Khối Dịch vụ cốt lõi: Worker.cs điều phối vòng kiểm tra; Enforcer.cs quản lý Registry driver; UsbDisks.cs quét và eject đĩa.",
        "Khối Bảo mật & Lưu trữ: Auth.cs băm mật khẩu PBKDF2; Settings.cs đọc ghi cấu hình; Reg.cs thiết lập phân quyền DACL.",
        "Khối Tương tác tầng thấp: Native.cs khai báo Win32 P/Invoke (SetupAPI, CfgMgr32, Kernel32, Wtsapi32); Sys.cs và Log.cs phụ trợ.",
        "Quy mô tinh gọn: 15 tệp mã nguồn C#, tổng cộng 1197 dòng lệnh thực tế, tối ưu hóa hiệu năng hệ thống."
    ], size=16, gap=10)
    sb.pic(sl5, "hinh2_so_do_thanh_phan.png", 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE 6: 3 CHẾ ĐỘ HOẠT ĐỘNG LINH HOẠT
    # --------------------------------------------------------------------------
    sl6 = sb.add_slide("Vận hành linh hoạt với 3 chế độ hoạt động", "2. Kiến trúc & Thiết kế")
    sb.bullets(sl6, 0.8, 1.8, 5.8, 4.8, [
        "Chế độ 1 — CHẶN TẤT CẢ (Mặc định): Whitelist rỗng. Driver Start = 4, Deny_All = 1. Mọi USB cắm vào đều bị gỡ.",
        "Chế độ 2 — DANH SÁCH CHO PHÉP: Whitelist có >= 1 mục. Driver mở (Start = 3), chỉ gỡ USB không khớp ID.",
        "Chế độ 3 — TẠM DỪNG (Có thời hạn): Lệnh pause đúng mật khẩu. Mở toàn bộ USB để bảo trì hoặc sao chép.",
        "Tự động hoàn nguyên: Hết hạn tạm dừng (Ticks UTC), hệ thống tự động quay về chế độ chặn trước đó.",
        "Đồng bộ không gián đoạn: Chuyển đổi chế độ an toàn qua CLI mà không cần khởi động lại dịch vụ."
    ], size=16, gap=10)
    sb.pic(sl6, "hinh5_trang_thai_3_che_do.png", 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE 7: CƠ CHẾ "KHÔNG TẮT ĐƯỢC" & PHỤC HỒI SCM
    # --------------------------------------------------------------------------
    sl7 = sb.add_slide("Cơ chế 'Không tắt được' & Tự phục hồi sau sự cố", "2. Kiến trúc & Thiết kế")
    sb.bullets(sl7, 0.8, 1.8, 5.8, 4.8, [
        "Từ chối dừng từ SCM (CanStop = false): SCM từ chối mọi yêu cầu dừng kể cả từ Administrator (lỗi 1052).",
        "Chặn tài khoản thường: Phân quyền DACL từ chối mọi thao tác sc stop, sc config, sc delete (lỗi 5).",
        "Tự phục hồi khi bị kill (sc failure): Bị taskkill /F bởi Admin, Windows tự chạy lại sau khoảng 5 giây.",
        "Dừng an toàn duy nhất: Chỉ lệnh UsbGuard.exe uninstall với đúng mật khẩu mới kích hoạt dừng.",
        "Ranh giới minh bạch: Admin có mật khẩu vẫn gỡ được; tuân thủ chuẩn phần mềm Device Control."
    ], size=16, gap=10)
    sb.pic(sl7, "hinh8_co_che_khong_tat_duoc.png", 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE 8: THIẾT KẾ BẢO MẬT & PHÂN QUYỀN REGISTRY
    # --------------------------------------------------------------------------
    sl8 = sb.add_slide("Thiết kế bảo mật mật khẩu & Phân quyền Registry", "2. Kiến trúc & Thiết kế")
    sb.bullets(sl8, 0.8, 1.8, 5.8, 4.8, [
        "Băm mật khẩu PBKDF2 (RFC 8018): 100000 vòng lặp HMAC-SHA1 với muối ngẫu nhiên 16 byte an toàn.",
        "So sánh thời gian hằng (Constant-Time): Duyệt toàn bộ mảng byte bằng phép XOR, chống tấn công kênh kề.",
        "Khóa cấu hình HKLM\\SOFTWARE\\UsbGuard: Lưu AuthHash, danh sách Whitelist, PauseUntil và cờ gỡ bỏ.",
        "Phân quyền nghiêm ngặt DACL: Ngắt kế thừa, chỉ cấp FullControl cho SYSTEM và Administrators.",
        "Nhập mật khẩu ẩn: Console.ReadKey(true) không hiển thị ký tự trên màn hình, không lưu vết dòng lệnh."
    ], size=16, gap=10)
    sb.pic(sl8, "hinh9_mo_hinh_bao_mat_pbkdf2.png", 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE 9: CÂY THIẾT BỊ & BẢO TOÀN THIẾT BỊ HID
    # --------------------------------------------------------------------------
    sl9 = sb.add_slide("Cây thiết bị PnP & Bảo toàn chuột, bàn phím", "2. Kiến trúc & Thiết kế")
    sb.bullets(sl9, 0.8, 1.8, 5.8, 4.8, [
        "Vấn đề gỡ nhầm ngoại vi: Nếu phần mềm gỡ nhầm cổng Hub, chuột và bàn phím cắm cùng cổng sẽ bị ngắt.",
        "Lọc chính xác lớp thiết bị: Chỉ truy vấn GUID_DEVINTERFACE_DISK, bỏ qua GUID_DEVINTERFACE_HID.",
        "Ranh giới cô lập MaxDepth = 2: Chỉ duyệt từ Nút đĩa (Disk Node) lên Nút thiết bị USB cha (Parent USB Node).",
        "Không can thiệp nút Hub: Dừng lại trước nút Generic Hub / Root Hub, giữ nguyên kết nối cho chuột và bàn phím.",
        "Dự phòng pnputil an toàn: Nếu CM_Request_Device_Eject bị từ chối do khóa tệp, chỉ disable đúng nút USB cha."
    ], size=16, gap=10)
    sb.pic(sl9, "hinh7_cay_thiet_bi_usb.png", 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE 10: QUY TRÌNH GỠ CÀI ĐẶT AN TOÀN
    # --------------------------------------------------------------------------
    sl10 = sb.add_slide("Quy trình gỡ cài đặt an toàn & Khôi phục hệ thống", "2. Kiến trúc & Thiết kế")
    sb.bullets(sl10, 0.8, 1.8, 5.8, 4.8, [
        "Xác thực đa tầng: Yêu cầu quyền Administrator (UAC) và xác thực chính xác mật khẩu qua Auth.Verify.",
        "Đồng bộ qua cờ Registry: Ghi Uninstalling = 1; tiến trình Worker phát hiện cờ và chủ động gọi Stop().",
        "Chờ kết thúc an toàn: Vòng lặp chờ tối đa 20 giây cho dịch vụ chuyển hẳn sang STOPPED trước khi xóa.",
        "Hoàn trả cài đặt gốc: Trả USBSTOR và UASPStor về Start = 3, xóa Deny_All, bật lại thiết bị tắt bởi pnputil.",
        "Dọn dẹp hệ thống: Xóa toàn bộ khóa Registry HKLM\\SOFTWARE\\UsbGuard và xóa thư mục cài đặt."
    ], size=16, gap=10)
    sb.pic(sl10, "hinh6_luong_go_cai_dat.png", 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE 11: TẬP LỆNH ĐIỀU KHIỂN DÒNG LỆNH CLI
    # --------------------------------------------------------------------------
    sl11 = sb.add_slide("Tập lệnh điều khiển dòng lệnh CLI quản trị", "3. Triển khai & Sử dụng")
    headers_cli = ["Lệnh CLI", "Quyền", "Ý nghĩa chức năng thực thi"]
    rows_cli = [
        ["UsbGuard.exe install [pw]", "Admin", "Cài đặt dịch vụ vào SCM, đặt mật khẩu quản trị, tự khởi động."],
        ["UsbGuard.exe uninstall [pw]", "Admin", "Xác thực mật khẩu, dừng dịch vụ, xóa SCM và hoàn trả mặc định."],
        ["UsbGuard.exe status", "Tất cả", "Xem trạng thái (RUNNING), chế độ hoạt động và danh sách whitelist."],
        ["UsbGuard.exe pause <phút> [pw]", "Admin", "Tạm dừng chế độ chặn trong N phút (1 - 1440) để chép dữ liệu."],
        ["UsbGuard.exe resume [pw]", "Admin", "Kích hoạt lại chế độ chặn ngay lập tức, không chờ hết giờ."],
        ["UsbGuard.exe devices [--all]", "Tất cả", "Liệt kê ổ USB đang cắm kèm loại bus để lấy ID thêm whitelist."],
        ["UsbGuard.exe whitelist add/rm", "Admin", "Thêm hoặc xóa chuỗi ID thiết bị khỏi danh sách cho phép."],
        ["UsbGuard.exe passwd [cũ] [mới]", "Admin", "Thay đổi mật khẩu quản trị hệ thống."]
    ]
    sb.table(sl11, 0.8, 1.8, 11.7, headers_cli, rows_cli, [3.2, 1.2, 7.3], size=14, row_height=0.48)

    # --------------------------------------------------------------------------
    # SLIDE 12: CHIẾN LƯỢC KIỂM THỬ ĐA TẦNG
    # --------------------------------------------------------------------------
    sl12 = sb.add_slide("Chiến lược kiểm thử đa tầng bảo đảm chất lượng", "4. Kiểm thử & Đánh giá")
    sb.bullets(sl12, 0.8, 1.8, 11.7, 5.0, [
        "Tầng 1 — Unit Test tự động (tests/AuthTests.cs): 12 ca kiểm thử xUnit độc lập, kiểm tra thuật toán băm PBKDF2 và so khớp Whitelist.",
        "Tầng 2 — Kiểm thử tích hợp CI (tests/integration.ps1): 30 ca kiểm thử tự động trên Windows Server 2022 và Windows Server 2025.",
        "Kiểm thử hành vi SCM thật: Kiểm tra từ chối sc stop của Admin (lỗi 1052), kiểm tra từ chối tài khoản thường (lỗi 5).",
        "Đo đạc chỉ số thời gian: Đo thời gian tự sửa Registry khi bị đổi tay và thời gian tự khởi động lại sau khi bị taskkill cưỡng chế.",
        "Tầng 3 — Kiểm thử thực nghiệm với USB vật lý: 7 kịch bản kiểm tra trên máy tính có cổng USB thật, đánh giá gỡ đĩa và bảo toàn chuột/phím."
    ], size=19, gap=16)

    # --------------------------------------------------------------------------
    # SLIDE 13: KẾT QUẢ KIỂM THỬ UNIT TEST (12/12 ĐẠT)
    # --------------------------------------------------------------------------
    sl13 = sb.add_slide("Kết quả kiểm thử Unit Test xUnit (12/12 Đạt)", "4. Kiểm thử & Đánh giá")
    headers_ut = ["Mã test", "Phương thức kiểm thử", "Mục đích kiểm tra", "Kết quả"]
    rows_ut = [
        ["UT01", "Hash_RoiVerify_DungMatKhau_PhaiDung", "Băm và xác thực lại đúng mật khẩu ban đầu.", "ĐẠT (PASS)"],
        ["UT02", "Verify_SaiMatKhau_PhaiSai", "Xác thực với mật khẩu sai khác trả về false.", "ĐẠT (PASS)"],
        ["UT03", "Verify_ChuoiLuuRong_PhaiSai", "Chuỗi băm rỗng trả về false, không crash.", "ĐẠT (PASS)"],
        ["UT04", "Verify_SaiDinhDang_KhongDuocNem", "Chuỗi băm sai định dạng không ném ngoại lệ.", "ĐẠT (PASS)"],
        ["UT05", "Hash_HaiLanGoiLienTiep_RaMuoiKhacNhau", "2 lần băm cùng mật khẩu sinh 2 muối khác nhau.", "ĐẠT (PASS)"],
        ["UT06", "Verify_ThieuIteration_PhaiSai", "Từ chối số vòng lặp < 1000 chống hash giả mạo.", "ĐẠT (PASS)"],
        ["UT07", "IsValidEntry_ChuoiQuaNgan_KhongHopLe", "Mục whitelist rỗng hoặc < 4 ký tự không hợp lệ.", "ĐẠT (PASS)"],
        ["UT08", "IsValidEntry_DuDaiToiThieu_HopLe", "Mục whitelist từ 4 ký tự trở lên (VID_0951) hợp lệ.", "ĐẠT (PASS)"],
        ["UT09", "Matches_ThietBiCoIdNamTrongWhitelist", "Thiết bị có ID khớp whitelist được cấp phép.", "ĐẠT (PASS)"],
        ["UT10", "Matches_KhongPhanBietHoaThuong", "So khớp không phân biệt chữ hoa, chữ thường.", "ĐẠT (PASS)"],
        ["UT11", "Matches_WhitelistRong_KhongKhopGi", "Whitelist rỗng thì từ chối toàn bộ thiết bị.", "ĐẠT (PASS)"],
        ["UT12", "Matches_MucWhitelistQuaNgan_BiBoQua", "Mục whitelist < 4 ký tự tự động bị bỏ qua.", "ĐẠT (PASS)"]
    ]
    sb.table(sl13, 0.8, 1.8, 11.7, headers_ut, rows_ut, [0.9, 4.3, 4.9, 1.6], size=11, row_height=0.34)

    # --------------------------------------------------------------------------
    # SLIDE 14: KẾT QUẢ KIỂM THỬ TÍCH HỢP TRÊN WINDOWS SERVER
    # --------------------------------------------------------------------------
    sl14 = sb.add_slide("Kết quả kiểm thử tích hợp CI trên Windows Server", "4. Kiểm thử & Đánh giá")
    sb.bullets(sl14, 0.8, 1.8, 5.8, 4.8, [
        "100% ca kiểm thử đạt (30/30 ca): Chạy tự động qua GitHub Actions trên cả Windows Server 2022 và Windows Server 2025.",
        "Cơ chế 'không tắt được': Admin sc stop bị chặn (lỗi 1052); User thường bị chặn (lỗi 5); Taskkill tự hồi sinh sau 5412 ms (2022) và 5508 ms (2025).",
        "Thời gian tự sửa Registry (tu_sua_ms): Khôi phục Start = 4 sau 1316 ms (Win 2022) và 560 ms (Win 2025) khi bị đổi tay.",
        "Tài nguyên thực tế (đo 60 giây không tải): Win 2022 tiêu thụ 21.8 MB RAM, CPU 0.0%; Win 2025 tiêu thụ 24.9 MB RAM, CPU 0.02%.",
        "Gỡ cài đặt hoàn trả gốc: Dịch vụ tự dừng sau 1.9s, xóa sạch tệp và khôi phục hoàn toàn mặc định hệ thống."
    ], size=16, gap=10)
    sb.pic(sl14, "hinh10_terminal_log.png", 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE 15: ĐÁNH GIÁ ĐÁP ỨNG MỤC TIÊU ĐỀ TÀI
    # --------------------------------------------------------------------------
    sl15 = sb.add_slide("Đánh giá mức độ đáp ứng các yêu cầu đề tài", "4. Kiểm thử & Đánh giá")
    headers_dg = ["Mã yêu cầu", "Tiêu chuẩn thiết kế", "Kết quả thực tế đạt được", "Đánh giá"]
    rows_dg = [
        ["YC-CN01", "Chặn USB lưu trữ trong <= 2 giây.", "Theo thiết kế: sự kiện WMI + quét 2s; đo thực tế kịch bản 2.", "Đáp ứng theo thiết kế, chờ kiểm thử USB vật lý"],
        ["YC-CN02", "Bảo vệ chuột, bàn phím HID.", "Theo thiết kế: MaxDepth = 2 cô lập nút USB; đo thực tế kịch bản 6.", "Đáp ứng theo thiết kế, chờ kiểm thử USB vật lý"],
        ["YC-CN03", "Hỗ trợ 3 chế độ hoạt động.", "Chuyển đổi chính xác giữa 3 chế độ (All/Allow/Pause).", "Đáp ứng (30/30 ca CI đạt)"],
        ["YC-CN06", "Xác thực mật khẩu quản trị.", "Băm PBKDF2 100000 vòng lặp, thời gian hằng.", "Đáp ứng (12/12 unit test đạt)"],
        ["YC-PCN01", "Cơ chế 'không tắt được'.", "SCM từ chối sc stop (lỗi 1052); User thường bị chặn (lỗi 5).", "Đáp ứng (đã kiểm thử CI)"],
        ["YC-PCN02", "Tự phục hồi sau khi bị kill.", "Windows tự khởi động lại sau khoảng 5 giây qua sc failure.", "Đáp ứng (đã kiểm thử CI)"],
        ["YC-PCN03", "Tiêu chuẩn: CPU < 1%, RAM < 50 MB.", "Thực tế: RAM 21.8 - 25.1 MB, CPU 0.0% - 0.02%.", "Đáp ứng (đo trên Win Server 2022/2025)"]
    ]
    sb.table(sl15, 0.8, 1.8, 11.7, headers_dg, rows_dg, [1.3, 3.2, 4.6, 2.6], size=12, row_height=0.55)

    # --------------------------------------------------------------------------
    # SLIDE 16: HẠN CHẾ CỦA GIẢI PHÁP HIỆN TẠI
    # --------------------------------------------------------------------------
    sl16 = sb.add_slide("Hạn chế kỹ thuật của giải pháp hiện tại", "5. Kết luận & Mở rộng")
    sb.bullets(sl16, 0.8, 1.8, 11.7, 5.0, [
        "Nhận diện VID/PID với thiết bị trùng model: Với các USB giá rẻ không có số serial duy nhất, việc thêm VID/PID vào whitelist sẽ áp dụng cho mọi USB cùng loại; giải pháp là ưu tiên dùng chế độ pause có thời hạn.",
        "Giới hạn quyền Administrator cấp cao nhất: Administrator can thiệp vào Safe Mode hoặc tháo ổ cứng sửa Registry ngoại tuyến (offline) vẫn có thể vô hiệu hóa dịch vụ (giới hạn tự nhiên của mô hình phân quyền phần mềm).",
        "Chưa có giao diện đồ họa (GUI): Hiện tại hệ thống vận hành hoàn toàn qua dòng lệnh CLI, rất thuận tiện cho quản trị viên và kịch bản tự động nhưng chưa thân thiện với người dùng phổ thông.",
        "Giới hạn phân loại thiết bị: Phiên bản hiện tại tập trung kiểm soát thiết bị lưu trữ dạng khối (USB Mass Storage và UAS), chưa chặn giao thức truyền thông đa phương tiện MTP/PTP (điện thoại thông minh).",
        "Vận hành độc lập: Chưa có máy chủ quản trị tập trung để điều khiển và thu thập nhật ký đồng loạt cho hàng nghìn máy trạm trong mạng nội bộ."
    ], size=17, gap=12)

    # --------------------------------------------------------------------------
    # SLIDE 17: HƯỚNG PHÁT TRIỂN TRONG TƯƠNG LAI
    # --------------------------------------------------------------------------
    sl17 = sb.add_slide("Hướng nghiên cứu & Phát triển tiếp theo", "5. Kết luận & Mở rộng")
    sb.bullets(sl17, 0.8, 1.8, 11.7, 5.0, [
        "Xây dựng Dashboard quản lý tập trung qua mạng: Cho phép quản trị viên an ninh mạng phân phối Whitelist, phát lệnh khóa/mở và giám sát nhật ký vi phạm thời gian thực qua giao diện Web.",
        "Phát triển Kernel-Mode Filter Driver: Chuyển dịch cơ chế chặn xuống trình điều khiển lọc tầng nhân để can thiệp ngay trong giai đoạn nạp ngăn xếp I/O, giảm thiểu tối đa độ trễ phần cứng.",
        "Ký số chứng chỉ số WHQL (Microsoft): Đăng ký chứng chỉ phần cứng Windows Hardware Quality Labs để bộ cài đặt đạt độ tin cậy cao với hệ điều hành và phần mềm diệt virus.",
        "Mở rộng kiểm soát thiết bị ngoại vi: Tích hợp bộ lọc kiểm soát giao thức truyền thông MTP (điện thoại thông minh), giao tiếp Bluetooth và cổng Thunderbolt/FireWire.",
        "Tích hợp xác thực 2 yếu tố (2FA): Bổ sung xác thực OTP hoặc khóa bảo mật FIDO2 khi quản trị viên thực hiện các lệnh nhạy cảm như tạm dừng hoặc gỡ cài đặt."
    ], size=17, gap=12)

    # --------------------------------------------------------------------------
    # SLIDE 18: LỜI CẢM ƠN & HỎI ĐÁP
    # --------------------------------------------------------------------------
    sl18 = sb.prs.slides.add_slide(sb.blank_layout)
    sb.slide_count += 1
    sl18.background.fill.solid()
    sl18.background.fill.fore_color.rgb = C_WHITE

    sb.tx(sl18, 1.0, 1.8, 11.3, 1.0, "XIN CHÂN THÀNH CẢM ƠN QUÝ THẦY, CÔ\nVÀ HỘI ĐỒNG ĐÃ LẮNG NGHE!",
          size=32, bold=True, color=C_NAVY, align=PP_ALIGN.CENTER)

    line = sl18.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.5), Inches(3.2), Inches(4.333), Inches(0.04))
    line.fill.solid()
    line.fill.fore_color.rgb = C_BLUE
    line.line.fill.background()

    sb.tx(sl18, 1.0, 3.8, 11.3, 0.6, "PHIÊN HỎI ĐÁP & ĐÓNG GÓP Ý KIẾN", size=24, bold=True, color=C_BLUE, align=PP_ALIGN.CENTER)
    sb.tx(sl18, 1.0, 4.6, 11.3, 0.5, "Rất mong nhận được những nhận xét quý báu từ quý Thầy, Cô để hoàn thiện giải pháp.",
          size=18, italic=True, color=C_DARK, align=PP_ALIGN.CENTER)

    box_contact = sl18.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.2), Inches(5.4), Inches(6.9), Inches(1.2))
    box_contact.fill.solid()
    box_contact.fill.fore_color.rgb = C_BG_BOX
    box_contact.line.color.rgb = C_LINE
    box_contact.line.width = Pt(1)

    sb.tx(sl18, 3.4, 5.6, 6.5, 0.35, "Sinh viên: Phạm Văn Hưng — MSSV: 3120410225", size=16, bold=True, color=C_NAVY, align=PP_ALIGN.CENTER)
    sb.tx(sl18, 3.4, 6.0, 6.5, 0.35, "Khoa Công nghệ Thông tin — Trường Đại học Sài Gòn", size=14, color=C_MUTE, align=PP_ALIGN.CENTER)

    return sb


def chuyen_doi_pptx_sang_pdf(pptx_path, out_dir):
    """Chuyển đổi PPTX sang PDF bằng LibreOffice headless."""
    env_dir = f"file:///tmp/usbguard_slide_lo_env_{os.getpid()}"
    cmd = [
        SOFFICE,
        f"-env:UserInstallation={env_dir}",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(out_dir),
        str(pptx_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    print("=================================================================")
    print("BẮT ĐẦU QUY TRÌNH TẠO SLIDE THUYẾT MINH USBGUARD")
    print("=================================================================")

    pptx_file = HERE / "SLIDE-UsbGuard.pptx"
    pdf_file = HERE / "SLIDE-UsbGuard.pdf"

    print("1. Xây dựng bản trình chiếu PowerPoint (16:9, phong cách tối giản)...")
    sb = tao_toan_bo_slide()
    sb.prs.save(str(pptx_file))
    print(f"   -> Đã lưu tệp PPTX: {pptx_file} ({sb.slide_count} slide)")

    print("2. Chuyển đổi Slide sang tệp PDF bằng LibreOffice...")
    chuyen_doi_pptx_sang_pdf(pptx_file, HERE)

    print("=================================================================")
    print("HOÀN TẤT TẠO SLIDE:")
    print(f"- Tệp PPTX: {pptx_file} ({pptx_file.stat().st_size // 1024} KB)")
    print(f"- Tệp PDF:  {pdf_file} ({pdf_file.stat().st_size // 1024} KB)")
    print(f"- Tổng số slide: {sb.slide_count} slide (Yêu cầu: 15-18 slide).")
    print("=================================================================")


if __name__ == "__main__":
    main()

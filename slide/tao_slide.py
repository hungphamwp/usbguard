#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kịch bản tạo Slide báo cáo Seminar Chuyên đề "UsbGuard" (pptx và PDF).
Tỷ lệ 16:9, phong cách tối giản, nền trắng, màu nhấn xanh đậm #1F4E79, font Arial.
Quy tắc: Chữ >= 18pt, tối đa 5 ý mỗi slide, dùng lại hình vẽ trong report/hinh/.
"""

import os

# ---- Số liệu kiểm thử đọc từ tests/ket-qua qua report/ket_qua.py (không gõ tay) ----
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "report"))
import ket_qua as kq
K22, K25 = kq.tich_hop(2022), kq.tich_hop(2025)
W10, W11 = kq.e2e(10), kq.e2e(11)
U22, U25 = kq.unit(2022), kq.unit(2025)
for _d in (K22, K25, W10, W11, U22, U25):
    if _d["dat"] != _d["tong"]:
        raise SystemExit(f"[LỖI] Có ca không đạt trong {_d['_tep']}: {_d['dat']}/{_d['tong']}")
SO_TEP, SO_DONG = len(kq.ma_nguon()), sum(n for _, n in kq.ma_nguon())
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
        self.tx(sl, 0.8, 7.05, 10.0, 0.3, "Báo cáo Seminar Chuyên đề · Đề tài: UsbGuard 1.2 — Ngăn chặn cắm USB Flash Disk trên Windows",
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
        path = filename if isinstance(filename, pathlib.Path) else HINH_DIR / filename
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
    sb.tx(sl1, 0.9, 4.1, 11.5, 0.5, "Sản phẩm phần mềm: UsbGuard 1.2", size=20, italic=True, bold=True, color=C_BLUE)

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
        "Mục tiêu 4 — Quản trị bảo mật: Hỗ trợ 3 chế độ (Chặn tất cả, Danh sách cho phép, Tạm dừng); mật khẩu PBKDF2-SHA256 600000 vòng, khoá chống dò; bảo vệ Registry DACL.",
        "Phạm vi: Dịch vụ chặn 3 tầng, giao diện quản lý, bộ cài setup.exe và kiểm thử cắm USB trên Windows 10, 11 và trên máy thật; là phần mềm Device Control chính quy, không phải rootkit."
    ], size=19, gap=16)

    # --------------------------------------------------------------------------
    # SLIDE 4: KIẾN TRÚC TỔNG THỂ 2 LỚP BẢO VỆ
    # --------------------------------------------------------------------------
    sl4 = sb.add_slide("Kiến trúc 3 tầng chặn và lớp gỡ thiết bị", "2. Kiến trúc & Thiết kế")
    sb.bullets(sl4, 0.8, 1.8, 5.8, 4.8, [
        "Tầng 1 (Driver): Tắt USBSTOR và UASPStor (Start = 4).",
        "Tầng 2 (Chính sách): Removable Storage Deny_All = 1, chặn đọc, ghi, chạy.",
        "Tầng 3 (Cài thiết bị): Device Installation Restrictions cấm ID lớp 08, không đụng chuột, bàn phím.",
        "Lớp gỡ: SetupAPI + IOCTL (BusType 7), eject, buộc tháo ổ khi đang mở tệp, nạp lại thiết bị khi bỏ chặn.",
        f"Quy mô: {SO_TEP} tệp C#, {SO_DONG} dòng; Auth, AdminAuth (mật khẩu), UsbPorts (nạp lại cổng USB) là phần mới của bản 1.2."
    ], size=16, gap=10)
    sb.pic(sl4, "hinh1_kien_truc_3_tang.png", 6.8, 1.8, 5.8, 4.8)

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
        "Băm mật khẩu PBKDF2 (RFC 8018): HMAC-SHA256, 600000 vòng, muối ngẫu nhiên 16 byte; mã băm cũ (SHA1) tự nâng cấp.",
        "So sánh thời gian hằng (Constant-Time): Duyệt toàn bộ mảng byte bằng phép XOR, chống tấn công kênh kề.",
        "Khóa cấu hình HKLM\\SOFTWARE\\UsbGuard: Lưu AuthHash, Whitelist, PauseUntil, số lần sai và vị trí cổng USB.",
        "Phân quyền nghiêm ngặt DACL: Ngắt kế thừa, chỉ cấp FullControl cho SYSTEM và Administrators.",
        "Chống dò mật khẩu: sai 5 lần khoá 30 giây, mỗi lần sai tiếp gấp đôi, tối đa 1 giờ; đếm trong HKLM, dùng cho giao diện, dòng lệnh và trình gỡ."
    ], size=16, gap=10)
    sb.pic(sl8, "hinh9_mo_hinh_bao_mat_pbkdf2.png", 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE 10: QUY TRÌNH GỠ CÀI ĐẶT AN TOÀN
    # --------------------------------------------------------------------------
    sl10 = sb.add_slide("Quy trình gỡ cài đặt an toàn & Khôi phục hệ thống", "2. Kiến trúc & Thiết kế")
    sb.bullets(sl10, 0.8, 1.8, 5.8, 4.8, [
        "Xác thực đa tầng: Yêu cầu quyền Administrator (UAC) và xác thực chính xác mật khẩu qua Auth.Verify.",
        "Đồng bộ qua cờ Registry: Ghi Uninstalling = 1; tiến trình Worker phát hiện cờ và chủ động gọi Stop().",
        "Chờ kết thúc an toàn: Vòng lặp chờ tối đa 20 giây cho dịch vụ chuyển hẳn sang STOPPED trước khi xóa.",
        "Hoàn trả cài đặt gốc: Trả USBSTOR và UASPStor về Start = 3, xóa Deny_All và chỉ các mục UsbGuardN của tầng 3, bật lại thiết bị bị chặn.",
        "Dọn dẹp hệ thống: Xóa toàn bộ khóa Registry HKLM\\SOFTWARE\\UsbGuard và xóa thư mục cài đặt."
    ], size=16, gap=10)
    sb.pic(sl10, "hinh6_luong_go_cai_dat.png", 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE: GIAO DIỆN QUẢN LÝ
    # --------------------------------------------------------------------------
    slg = sb.add_slide("Giao diện quản lý đồ họa", "3. Triển khai & Sử dụng")
    sb.bullets(slg, 0.8, 1.8, 5.8, 4.8, [
        "Thanh trạng thái màu: Đỏ chặn tất cả, xanh chỉ cho phép danh sách, vàng tạm dừng, xám chưa cài.",
        "3 tab: USB đang cắm, Danh sách cho phép, Nhật ký; cho phép 1 USB bằng 1 lần bấm, không cần rút ra.",
        "Trạng thái rõ hơn: danh sách USB hiện \"Bị chặn (đã tháo)\"; thanh tạm dừng ghi \"Muốn chặn ngay, bấm Bật lại chặn\".",
        "Mọi thao tác hỏi mật khẩu quản trị; sai 5 lần thì khoá 30 giây, tăng dần.",
    ], size=16, gap=10)
    sb.pic(slg, kq.anh_gui(), 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE: BỘ CÀI SETUP.EXE
    # --------------------------------------------------------------------------
    sls = sb.add_slide("Bộ cài setup.exe", "3. Triển khai & Sử dụng")
    sb.bullets(sls, 0.8, 1.8, 5.2, 4.8, [
        "Đóng gói Inno Setup 6, giao diện tiếng Việt.",
        "Trang đặt mật khẩu quản trị: 2 ô nhập, tối thiểu 8 ký tự.",
        "Mật khẩu chuyển qua biến môi trường USBGUARD_ADMIN_PW, không hiện trên dòng lệnh.",
        "Tạo lối tắt Start Menu, Desktop và mục Apps & features.",
        "Trình gỡ bắt buộc đúng mật khẩu; cài im lặng bằng /VERYSILENT /ADMINPW=..."
    ], size=16, gap=10)
    sb.pic(sls, "hinh11_bo_cai_setup.png", 6.2, 2.2, 6.4, 3.6)

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
    # SLIDE: CHIẾN LƯỢC KIỂM THỬ 3 CẤP
    # --------------------------------------------------------------------------
    sl12 = sb.add_slide("Chiến lược kiểm thử: 3 cấp tự động và thử trên máy thật", "4. Kiểm thử & Đánh giá")
    sb.bullets(sl12, 0.8, 1.8, 11.7, 5.0, [
        f"Cấp 1 — Unit test (xUnit): {U22['dat']}/{U22['tong']} ca đạt trên Windows Server 2022 và {U25['dat']}/{U25['tong']} ca đạt trên Windows Server 2025, kiểm tra băm PBKDF2, khoá chống dò và so khớp danh sách.",
        f"Cấp 2 — Tích hợp trên Windows Server: {K22['dat']}/{K22['tong']} ca đạt trên Windows Server 2022 và {K25['dat']}/{K25['tong']} ca đạt trên Windows Server 2025, gồm cả chống dò mật khẩu (TC35 đến TC37).",
        f"Cấp 3 — Cắm USB thật trên Windows 10 và Windows 11: {W10['dat']}/{W10['tong']} ca đạt trên Windows 10 và {W11['dat']}/{W11['tong']} ca đạt trên Windows 11, cài bằng setup.exe rồi cắm, rút USB.",
        "Thử thủ công trên máy Windows thật: 1 thành viên nhóm thử bản 1.1.0 với USB vật lý, 7 kịch bản đều đạt; phản hồi dẫn tới bản 1.2.",
        "Mọi con số được đọc trực tiếp từ các tệp kết quả của lần chạy."
    ], size=19, gap=16)

    # --------------------------------------------------------------------------
    # SLIDE: KẾT QUẢ TÍCH HỢP WINDOWS SERVER
    # --------------------------------------------------------------------------
    sl14 = sb.add_slide(f"Kiểm thử tích hợp Windows Server: {K22['dat']}/{K22['tong']} ca đạt", "4. Kiểm thử & Đánh giá")
    sb.bullets(sl14, 0.8, 1.8, 5.8, 4.8, [
        f"Kết quả: {K22['dat']}/{K22['tong']} ca đạt trên Windows Server 2022 và {K25['dat']}/{K25['tong']} ca đạt trên Windows Server 2025.",
        f"Cơ chế 'không tắt được': sc stop bị chặn (lỗi 1052); taskkill thì dịch vụ chạy lại sau {K22['chay_lai_ms']} ms (2022) và {K25['chay_lai_ms']} ms (2025).",
        f"Tự sửa Registry: khôi phục Start = 4 sau {K22['tu_sua_ms']} ms (2022) và {K25['tu_sua_ms']} ms (2025).",
        f"Tài nguyên: Server 2022 dùng {K22['ram_tb_mb']} MB RAM, CPU {K22['cpu_pct']}%; Server 2025 dùng {K25['ram_tb_mb']} MB RAM, CPU {K25['cpu_pct']}%.",
        f"Gỡ cài đặt: dịch vụ dừng và bị xoá sau {K22['go_ms']} ms (2022) và {K25['go_ms']} ms (2025), chỉ xoá mục của UsbGuard."
    ], size=16, gap=10)
    sb.pic(sl14, "hinh10_terminal_log.png", 6.8, 1.8, 5.8, 4.8)

    # --------------------------------------------------------------------------
    # SLIDE: KIỂM THỬ CẮM USB THẬT
    # --------------------------------------------------------------------------
    sl_e = sb.add_slide(f"Cắm USB thật: {W10['dat']}/{W10['tong']} ca đạt trên Windows 10 và Windows 11", "4. Kiểm thử & Đánh giá")
    def _kqe(d, m):
        return "Đạt" if d["theo_ma"][m]["dat"] else "Không đạt"
    chon = [("E03", "Chặn tất cả: cắm USB không có ổ, không ghi được"),
            ("E05", "Chuột, bàn phím vẫn chạy, cắm thêm bàn phím vẫn nhận"),
            ("E06", "Tạm dừng: USB đang cắm dùng được, không cần rút"),
            ("E10", "Danh sách cho phép: USB lạ bị gỡ, USB được phép dùng"),
            ("E14", "Kill dịch vụ khi đang cắm: Windows chạy lại, USB vẫn bị chặn"),
            ("E16", "Gỡ đúng mật khẩu: trả lại cấu hình USB"),
            ("E19", "USB bị Windows tháo: cho phép lại thì tự hiện lại, không cần rút")]
    rows_e = [[m, mo, _kqe(W10, m), _kqe(W11, m)] for m, mo in chon]
    sb.table(sl_e, 0.8, 1.8, 11.7, ["Ca", "Kịch bản", "Windows 10", "Windows 11"], rows_e, [0.9, 7.6, 1.6, 1.6], size=16, row_height=0.55)
    sb.tx(sl_e, 0.8, 6.55, 11.7, 0.4, f"Tổng cộng {W10['tong']} ca (E01 đến E{W10['tong']:02d}) chạy trên máy ảo QEMU, USB cắm nóng bằng device_add.", size=16, color=C_MUTE)

    # --------------------------------------------------------------------------
    # SLIDE: 3 LỖI PHÁT HIỆN KHI CẮM USB THẬT
    # --------------------------------------------------------------------------
    sl_l = sb.add_slide("3 lỗi phát hiện khi cắm USB thật và cách sửa", "4. Kiểm thử & Đánh giá")
    sb.bullets(sl_l, 0.8, 1.8, 11.7, 4.8, [
        "Lỗi 1 — Bật lại chặn khi USB đang mở tệp: Windows từ chối eject. Sửa: buộc tháo ổ (khoá và dismount volume) rồi eject lại.",
        "Lỗi 2 — Lệnh pnputil /disable-device trả mã 3010 mà không được ghi lại: thiết bị bị vô hiệu hoá vĩnh viễn. Sửa: ghi nhận mã 3010, bật lại hoặc xoá nút thiết bị khi bỏ chặn.",
        "Lỗi 3 — USB cắm lần đầu lúc đang chặn: tầng 3 làm Windows đánh dấu 'cài thất bại', sau cho phép vẫn không lên. Sửa: xoá nút thiết bị bằng pnputil /remove-device rồi quét lại.",
        f"Kết quả: sau sửa, bộ cắm USB đạt đủ trên Windows 10 và Windows 11; bản 1.2 có thêm 3 ca (E18 đến E20), đạt {W10['dat']}/{W10['tong']} và {W11['dat']}/{W11['tong']}.",
    ], size=18, gap=14)

    # --------------------------------------------------------------------------
    # SLIDE: KIỂM THỬ TRÊN MÁY WINDOWS THẬT
    # --------------------------------------------------------------------------
    sl_mt = sb.add_slide("Kiểm thử thủ công trên máy Windows thật: 7/7 kịch bản đạt", "4. Kiểm thử & Đánh giá")
    rows_mt = [
        ["Cài đặt, tự khởi động cùng Windows", "sc query: STATE 4 RUNNING sau khi khởi động lại", "Đạt"],
        ["Chặn USB lưu trữ", "Hiện thông báo; không có ổ trong This PC; devices báo mã 47", "Đạt"],
        ["Tạm dừng, bật lại, danh sách cho phép", "USB dùng được khi tạm dừng; thêm serial thì USB hiện lại", "Đạt"],
        ["Administrator gửi sc stop", "Lỗi 1052, dịch vụ vẫn RUNNING", "Đạt"],
        ["Phiên không nâng quyền gửi sc stop", "Lỗi 5 (Access is denied)", "Đạt"],
        ["Chuột và bàn phím USB", "Vẫn dùng được khi chặn tất cả", "Đạt"],
        ["Gỡ cài đặt", "Sai mật khẩu bị từ chối; gỡ xong USBSTOR Start = 3, Deny_All đã xóa", "Đạt"],
    ]
    sb.table(sl_mt, 0.8, 1.8, 11.7, ["Kịch bản (bản 1.1.0)", "Kết quả quan sát", "Đánh giá"], rows_mt, [3.9, 6.6, 1.2], size=14, row_height=0.5)
    sb.tx(sl_mt, 0.8, 6.15, 11.7, 0.6, "1 thành viên nhóm thử với USB vật lý. Giới hạn: whitelist mới xác nhận với USB đã thử; cần thử thêm nhiều loại USB và nhiều máy.", size=16, color=C_MUTE)

    # --------------------------------------------------------------------------
    # SLIDE: PHẢN HỒI TỪ MÁY THẬT VÀ BẢN 1.2
    # --------------------------------------------------------------------------
    sl_p = sb.add_slide("Phản hồi kiểm thử máy thật và bản 1.2", "4. Kiểm thử & Đánh giá")
    sb.bullets(sl_p, 0.8, 1.8, 11.7, 5.0, [
        "Phản hồi 1 — USB bị tháo khi được cho phép: bị chặn lúc đang cắm thì Windows tháo an toàn (mã 47), cho phép hoặc tạm dừng xong phải rút ra cắm lại. Sửa: nhớ hub và số cổng, tự rút ra cắm lại cổng bằng IOCTL_USB_HUB_CYCLE_PORT, tối đa 3 lần cách 10 giây; không dùng pnputil /restart-device vì USB chuyển sang mã 14.",
        "Phản hồi 2 — USB biến khỏi danh sách: Sửa: đọc trạng thái cổng từ driver hub (IOCTL_USB_GET_NODE_CONNECTION_INFORMATION), hiện \"Bị chặn (đã tháo)\".",
        f"Kiểm chứng: tái hiện trong máy ảo trước khi sửa (E19, E20 không đạt), sau sửa đạt {W10['dat']}/{W10['tong']} trên Windows 10 và {W11['dat']}/{W11['tong']} trên Windows 11.",
        "Mật khẩu: PBKDF2-SHA256 600000 vòng (trước là SHA1, 100000 vòng), tự nâng cấp mã băm cũ; sai 5 lần khoá 30 giây, gấp đôi mỗi lần, tối đa 1 giờ (TC35 đến TC37).",
        "Giao diện: thanh tạm dừng ghi \"Muốn chặn ngay: bấm Bật lại chặn\"; danh sách hiện trạng thái \"Bị chặn (đã tháo)\"."
    ], size=16, gap=10)

    # --------------------------------------------------------------------------
    # SLIDE: ĐÁNH GIÁ ĐÁP ỨNG
    # --------------------------------------------------------------------------
    sl15 = sb.add_slide("Đánh giá mức độ đáp ứng các yêu cầu đề tài", "4. Kiểm thử & Đánh giá")
    headers_dg = ["Yêu cầu", "Tiêu chuẩn", "Kết quả", "Đánh giá"]
    rows_dg = [
        ["YC-CN01", "Chặn USB <= 2 giây", "E03, E10 đạt", "Đáp ứng (USB thật)"],
        ["YC-CN02", "Bảo toàn chuột, phím", "E05 đạt", "Đáp ứng (USB thật)"],
        ["YC-CN03", "3 chế độ", f"{K22['dat']}/{K22['tong']} ca tích hợp", "Đáp ứng"],
        ["YC-CN06", "Mật khẩu quản trị", f"{U22['dat']}/{U22['tong']} unit test; TC35 đến TC37", "Đáp ứng"],
        ["YC-PCN01", "Không tắt được", "Lỗi 1052 và 5", "Đáp ứng"],
        ["YC-PCN03", "CPU < 1%, RAM < 50 MB", f"RAM {min(K22['ram_tb_mb'],K25['ram_tb_mb'])} - {max(K22['ram_max_mb'],K25['ram_max_mb'])} MB, CPU {max(K22['cpu_pct'],K25['cpu_pct'])}%", "Đáp ứng"]
    ]
    sb.table(sl15, 0.8, 1.8, 11.7, headers_dg, rows_dg, [1.8, 3.4, 3.6, 2.9], size=16, row_height=0.6)

    # --------------------------------------------------------------------------
    # SLIDE: HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN
    # --------------------------------------------------------------------------
    sl16 = sb.add_slide("Hạn chế và hướng phát triển", "5. Kết luận & Mở rộng")
    sb.bullets(sl16, 0.8, 1.8, 11.7, 5.0, [
        "Chưa có chứng chỉ ký số thương mại: Windows SmartScreen có thể cảnh báo khi cài; hướng phát triển là mua chứng chỉ ký mã.",
        "Chưa chặn MTP/PTP, ổ CD/DVD và Bluetooth: bổ sung bộ lọc cho các loại thiết bị này.",
        "Administrator hiểu sâu hệ thống vẫn can thiệp được (Safe Mode, sửa Registry ngoại tuyến): giới hạn của giải pháp phần mềm.",
        "Phạm vi kiểm thử: đã có 1 lượt thử trên máy thật (bản 1.1.0), cần thử thêm nhiều loại USB và máy; USB giá rẻ không có serial chỉ khớp theo VID/PID.",
        "Hướng phát triển: máy chủ quản trị tập trung nhiều máy trạm, driver lọc chế độ nhân, xác thực 2 yếu tố."
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
    print(f"- Tổng số slide: {sb.slide_count} slide (Yêu cầu: tối đa 20 slide).")
    print("=================================================================")


if __name__ == "__main__":
    main()

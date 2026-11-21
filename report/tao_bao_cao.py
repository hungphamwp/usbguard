#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kịch bản sinh Báo cáo Seminar Chuyên đề "UsbGuard" (docx và PDF).
Thực hiện sinh 2 lượt để tính số trang chính xác cho Mục lục, Danh mục hình và Danh mục bảng.
Định dạng chuẩn: A4, lề trái 3 cm, lề phải 2 cm, lề trên 2 cm, lề dưới 2 cm.
Font: Times New Roman 13 pt, giãn dòng 1.3, thụt đầu dòng 1 cm, tiêu đề chương in hoa đậm 14 pt.
"""

import json
import os
import pathlib
import re
import shutil
import subprocess
from xml.sax.saxutils import escape

import docx
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
import fitz  # PyMuPDF
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.resolve()))
import ket_qua as kq

# ==============================================================================
# THÔNG TIN TRANG BÌA VÀ DỰ ÁN
# ==============================================================================
THONG_TIN = {
    "truong": "TRƯỜNG ĐẠI HỌC SÀI GÒN",
    "khoa": "KHOA CÔNG NGHỆ THÔNG TIN",
    "loai_bao_cao": "BÁO CÁO SEMINAR CHUYÊN ĐỀ",
    "de_tai": "XÂY DỰNG ỨNG DỤNG NGĂN NGƯỜI DÙNG CẮM USB FLASH DISK VÀO MÁY TÍNH WINDOWS, CHẠY NHƯ DỊCH VỤ KHÔNG TẮT ĐƯỢC",
    "ten_san_pham": "UsbGuard 1.2",
    "sinh_vien": "Phạm Văn Hưng",
    "mssv": "3120410225",
    "giang_vien": "............................................",
    "dia_diem_thoi_gian": "TP. Hồ Chí Minh, tháng 11 năm 2026",
}

HERE = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = HERE.parent
HINH_DIR = HERE / "hinh"
SOFFICE = shutil.which("soffice") or os.path.expanduser("~/homebrew/bin/soffice")
CACHE_DIR = pathlib.Path("/tmp/usbguard_report_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_DU_LIEU = {}


def lay_du_lieu():
    """Đọc 1 lần toàn bộ số liệu kiểm thử từ tests/ket-qua/ (thiếu thì dừng, không dùng giá trị mặc định)."""
    if not _DU_LIEU:
        d = {"t22": kq.tich_hop("2022"), "t25": kq.tich_hop("2025"), "w10": kq.e2e("10"), "w11": kq.e2e("11"),
             "u22": kq.unit("2022"), "u25": kq.unit("2025")}
        for a, b in (("t22", "t25"), ("w10", "w11")):
            if [c["id"] for c in d[a]["ca"]] != [c["id"] for c in d[b]["ca"]]:
                raise SystemExit(f"[LỖI] Danh sách ca của {d[a]['_tep']} và {d[b]['_tep']} không trùng nhau")
        if d["u22"]["tong"] != d["u25"]["tong"]:
            raise SystemExit("[LỖI] Số ca unit test của 2 bản Windows Server khác nhau")
        _DU_LIEU.update(d)
    return _DU_LIEU


def ghep_doc(duong_dan, ten_tep, hop=(400, 290, 900, 530)):
    """Cắt vùng quanh hộp thoại của từng ảnh chụp thật rồi xếp dọc thành 1 ảnh (lưu vào thư mục đệm)."""
    from PIL import Image
    ims = []
    for d in duong_dan:
        if not pathlib.Path(d).exists():
            raise SystemExit(f"[LỖI] Thiếu ảnh chụp {d}")
        ims.append(Image.open(d).convert("RGB").crop(hop))
    w = max(i.width for i in ims)
    kc = 8
    out = Image.new("RGB", (w, sum(i.height for i in ims) + kc * (len(ims) - 1)), "white")
    y = 0
    for i in ims:
        out.paste(i, (0, y))
        y += i.height + kc
    ra = CACHE_DIR / ten_tep
    out.save(ra)
    return ra


def gon(text):
    """Bỏ dòng trống thừa trong đoạn mã trích."""
    return "\n".join(l.rstrip() for l in text.strip().splitlines() if l.strip())


def kqs(d):
    return f"{d['dat']}/{d['tong']}"


def kq_chu(b):
    return "Đạt" if b else "Không đạt"


def ok_ca(d):
    return d["dat"] == d["tong"]


def ct(d, ma):
    return d["theo_ma"][ma].get("chi_tiet", "")


def ms(d, ma):
    v = kq.so_ms(ct(d, ma), r"sau (\d+) ms")
    if v is None:
        raise SystemExit(f"[LỖI] Ca {ma} trong {d['_tep']} không có số đo 'sau N ms'")
    return v


NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')


# ==============================================================================
# HÀM HỖ TRỢ ĐỊNH DẠNG OPENXML CHO DOCX
# ==============================================================================
def rpr(b=False, i=False, sz=26, font="Times New Roman", color=None):
    f = f'<w:rFonts w:ascii="{font}" w:cs="{font}" w:eastAsia="{font}" w:hAnsi="{font}"/>'
    c_tag = f'<w:color w:val="{color}"/>' if color else ''
    return f'<w:rPr>{f}<w:b w:val="{int(b)}"/><w:bCs w:val="{int(b)}"/><w:i w:val="{int(i)}"/><w:iCs w:val="{int(i)}"/>{c_tag}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr>'


def runs(text, sz=26, b=False, i=False, font="Times New Roman", color=None):
    """Phân tích chuỗi có định dạng **đậm**, *nghiêng*, và `mã nguồn`."""
    out = []
    # Regex tách theo **đậm**, *nghiêng*, `mã`
    parts = re.split(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            out.append(runs(part[2:-2], sz, True, i, font, color))
        elif part.startswith("*") and part.endswith("*") and not part.startswith("**"):
            out.append(f'<w:r>{rpr(b, True, sz, font, color)}<w:t xml:space="preserve">{escape(part[1:-1])}</w:t></w:r>')
        elif part.startswith("`") and part.endswith("`"):
            out.append(f'<w:r>{rpr(b, i, max(sz-4, 20), "Consolas", color)}<w:t xml:space="preserve">{escape(part[1:-1])}</w:t></w:r>')
        else:
            out.append(f'<w:r>{rpr(b, i, sz, font, color)}<w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
    return "".join(out)


def para(text, jc="both", after=120, before=0, line=312, sz=26, b=False, i=False, ind_left=0, first_line=567, keep=False, font="Times New Roman", color=None):
    """Tạo đoạn văn chuẩn: Times New Roman 13pt, thụt dòng 1cm, giãn dòng 1.3."""
    ppr = f'<w:spacing w:after="{after}" w:before="{before}" w:line="{line}" w:lineRule="auto"/>'
    if ind_left > 0 or first_line > 0:
        ppr += f'<w:ind w:left="{ind_left}" w:firstLine="{first_line}"/>'
    if jc:
        ppr += f'<w:jc w:val="{jc}"/>'
    if keep:
        ppr += '<w:keepNext/>'
    return parse_xml(f'<w:p {NS}><w:pPr>{ppr}</w:pPr>{runs(text, sz, b, i, font, color)}</w:p>')


def bullet(text, sz=26):
    """Đoạn văn dạng danh sách đầu dòng (bullet)."""
    ppr = '<w:spacing w:after="80" w:before="0" w:line="288" w:lineRule="auto"/><w:ind w:left="850" w:hanging="284"/><w:jc w:val="left"/>'
    bullet_symbol = f'<w:r>{rpr(False, False, sz, "Times New Roman")}<w:t xml:space="preserve">•  </w:t></w:r>'
    return parse_xml(f'<w:p {NS}><w:pPr>{ppr}</w:pPr>{bullet_symbol}{runs(text, sz, False, False)}</w:p>')


def code_box(code_str, sz=20, keep=True):
    """Khối mã nguồn hiển thị font Consolas 10pt có nền xám nhẹ."""
    paragraphs = []
    lines = code_str.strip().split("\n")
    for idx, l in enumerate(lines):
        after_sp = 0 if idx < len(lines) - 1 else 120
        kn = '<w:keepNext/><w:keepLines/>' if keep and idx < len(lines) - 1 else ''
        ppr = f'{kn}<w:spacing w:after="{after_sp}" w:before="0" w:line="240" w:lineRule="auto"/><w:ind w:left="567"/><w:shd w:val="clear" w:fill="F2F4F7"/>'
        line_escaped = escape(l) if l else " "
        r = f'<w:r>{rpr(False, False, sz, "Consolas")}<w:t xml:space="preserve">{line_escaped}</w:t></w:r>'
        paragraphs.append(parse_xml(f'<w:p {NS}><w:pPr>{ppr}</w:pPr>{r}</w:p>'))
    return paragraphs


def page_break():
    return parse_xml(f'<w:p {NS}><w:r><w:br w:type="page"/></w:r></w:p>')


def h1_chap(title_text, pb=False):
    """Tiêu đề chương: in hoa, đậm, cỡ 14pt (28 half-points), căn giữa."""
    ppr = ('<w:keepNext/>' + ('<w:pageBreakBefore/>' if pb else '') + '<w:spacing w:before="240" w:after="160" w:line="312" w:lineRule="auto"/><w:jc w:val="center"/>')
    return parse_xml(f'<w:p {NS}><w:pPr>{ppr}</w:pPr>{runs(title_text, 28, True, False, "Times New Roman")}</w:p>')


def h2_sec(title_text):
    """Tiêu đề mục 2 cấp: đậm, cỡ 13pt (26 half-points), căn trái."""
    ppr = '<w:spacing w:before="200" w:after="100" w:line="312" w:lineRule="auto"/><w:jc w:val="left"/><w:keepNext/>'
    return parse_xml(f'<w:p {NS}><w:pPr>{ppr}</w:pPr>{runs(title_text, 26, True, False, "Times New Roman")}</w:p>')


def h3_sub(title_text):
    """Tiêu đề mục 3 cấp: đậm nghiêng, cỡ 13pt (26 half-points), căn trái."""
    ppr = '<w:spacing w:before="140" w:after="80" w:line="312" w:lineRule="auto"/><w:jc w:val="left"/><w:keepNext/>'
    return parse_xml(f'<w:p {NS}><w:pPr>{ppr}</w:pPr>{runs(title_text, 26, True, True, "Times New Roman")}</w:p>')


def img_para(doc, path, width_cm=15.0):
    """Chèn ảnh căn giữa vào tài liệu."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.add_run().add_picture(str(path), width=Cm(width_cm))
    el = p._p
    el.getparent().remove(el)
    return el


def caption_fig(text):
    """Chú thích hình vẽ: in nghiêng, căn giữa, đặt phía dưới hình."""
    ppr = '<w:spacing w:before="60" w:after="160" w:line="288" w:lineRule="auto"/><w:jc w:val="center"/>'
    return parse_xml(f'<w:p {NS}><w:pPr>{ppr}</w:pPr>{runs(text, 24, False, True, "Times New Roman")}</w:p>')


def caption_tbl(text):
    """Chú thích bảng biểu: in nghiêng, căn giữa, đặt phía trên bảng."""
    ppr = '<w:spacing w:before="140" w:after="60" w:line="288" w:lineRule="auto"/><w:jc w:val="center"/><w:keepNext/>'
    return parse_xml(f'<w:p {NS}><w:pPr>{ppr}</w:pPr>{runs(text, 24, False, True, "Times New Roman")}</w:p>')


def table_xml(headers, rows, widths, sz=22, alignments=None):
    """Tạo bảng dữ liệu chuẩn: tiêu đề nền xanh nhạt D9E2F3, viền xám mỏng, canh lề linh hoạt."""
    tot = sum(widths)
    aligns = alignments or ["left"] * len(headers)
    bd = '<w:tcBorders>' + ''.join(f'<w:{s} w:val="single" w:color="808080" w:sz="4"/>' for s in ("top", "left", "bottom", "right")) + '</w:tcBorders>'
    mar = '<w:tcMar><w:top w:type="dxa" w:w="80"/><w:left w:type="dxa" w:w="120"/><w:bottom w:type="dxa" w:w="80"/><w:right w:type="dxa" w:w="120"/></w:tcMar>'

    def cell(text, w, is_head=False, align="left"):
        shd = '<w:shd w:fill="D9E2F3" w:val="clear"/>' if is_head else ''
        ps = []
        for line in str(text).split("\n"):
            line_jc = 'center' if is_head else align
            ps.append(f'<w:p><w:pPr><w:spacing w:before="20" w:after="20"/><w:jc w:val="{line_jc}"/></w:pPr>{runs(line, sz, is_head, False)}</w:p>')
        return f'<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="{w}"/>{bd}{shd}{mar}</w:tcPr>{"".join(ps)}</w:tc>'

    trs = [f'<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>{"".join(cell(h, w, True, "center") for h, w in zip(headers, widths))}</w:tr>']
    for r in rows:
        trs.append(f'<w:tr><w:trPr><w:cantSplit/></w:trPr>{"".join(cell(c, w, False, a) for c, w, a in zip(r, widths, aligns))}</w:tr>')

    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    tbl_borders = '<w:tblBorders>' + ''.join(f'<w:{s} w:val="single" w:color="808080" w:sz="4"/>' for s in ("top", "left", "bottom", "right", "insideH", "insideV")) + '</w:tblBorders>'
    return parse_xml(f'<w:tbl {NS}><w:tblPr><w:tblW w:type="dxa" w:w="{tot}"/><w:jc w:val="center"/>{tbl_borders}<w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>{"".join(trs)}</w:tbl>')


def toc_entry(title, page_num, level=1):
    """Dòng mục lục: thụt lề theo cấp, có chấm nối (dot leader) đến số trang."""
    ind = 0 if level == 1 else (360 if level == 2 else 720)
    is_bold = level == 1
    sz = 26 if level == 1 else 24
    ppr = f'<w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9071"/></w:tabs><w:spacing w:after="40" w:before="20" w:line="288"/><w:ind w:left="{ind}"/></w:pPr>'
    r_text = runs(title, sz, is_bold, False)
    r_tab = f'<w:r>{rpr(is_bold, False, sz)}<w:tab/></w:r>'
    r_page = f'<w:r>{rpr(is_bold, False, sz)}<w:t>{page_num}</w:t></w:r>'
    return parse_xml(f'<w:p {NS}>{ppr}{r_text}{r_tab}{r_page}</w:p>')


# ==============================================================================
# LỚP TẠO BÁO CÁO USBGUARD
# ==============================================================================
class BaoCaoUsbGuard:
    def __init__(self, page_map=None):
        self.doc = Document()
        self.page_map = page_map or {}
        self.headings = []   # (level, title)
        self.figures = []    # (fig_id, title)
        self.tables = []     # (tbl_id, title)
        
        # Thiết lập trang A4 và lề tiêu chuẩn
        section = self.doc.sections[0]
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.0)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        
        # Cấu hình chân trang: trang bìa không hiện số trang, các trang sau đánh số giữa
        section.different_first_page_header_footer = True
        footer = section.footer
        footer_p = footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Thêm trường PAGE vào footer
        footer_p._p.append(parse_xml(f'<w:fldSimple {NS} w:instr="PAGE"><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="22"/></w:rPr><w:t>1</w:t></w:r></w:fldSimple>'))
        
        self.body = self.doc.element.body
        self.sect_pr = list(self.body.iterchildren())[-1]

    def add(self, *elements):
        for el in elements:
            if isinstance(el, list):
                for sub in el:
                    self.sect_pr.addprevious(sub)
            else:
                self.sect_pr.addprevious(el)

    def h1(self, text, page_break_before=True):
        self.headings.append((1, text))
        self.add(h1_chap(text, page_break_before))

    def h2(self, text):
        self.headings.append((2, text))
        self.add(h2_sec(text))

    def h3(self, text):
        self.headings.append((3, text))
        self.add(h3_sub(text))

    def p(self, text):
        self.add(para(text))

    def b(self, text):
        self.add(bullet(text))

    def code(self, code_text, sz=20, keep=True):
        self.add(code_box(code_text, sz, keep))

    def fig(self, fig_name, caption_text, width_cm=15.0):
        img_path = fig_name if isinstance(fig_name, pathlib.Path) else HINH_DIR / fig_name
        self.figures.append((str(fig_name), caption_text))
        if img_path.exists():
            self.add(img_para(self.doc, img_path, width_cm))
        else:
            self.add(para(f"[HÌNH ẢNH: {fig_name}]", jc="center", b=True, color="C00000"))
        self.add(caption_fig(caption_text))

    def tbl(self, tbl_id, caption_text, headers, rows, widths, aligns=None, sz=22):
        self.tables.append((tbl_id, caption_text))
        self.add(caption_tbl(caption_text))
        self.add(table_xml(headers, rows, widths, sz=sz, alignments=aligns))

    # ==========================================================================
    # CÁC PHẦN ĐẦU TÀI LIỆU (BÌA, LỜI CẢM ƠN, NHẬN XÉT, MỤC LỤC...)
    # ==========================================================================
    def tao_trang_bia(self):
        """Trang bìa theo chuẩn báo cáo khoa CNTT Trường ĐH Sài Gòn."""
        self.add(para("ỦY BAN NHÂN DÂN THÀNH PHỐ HỒ CHÍ MINH", jc="center", b=True, sz=26, after=40, line=260, first_line=0))
        self.add(para(THONG_TIN["truong"], jc="center", b=True, sz=28, after=40, line=260, first_line=0))
        self.add(para(THONG_TIN["khoa"], jc="center", b=True, sz=28, after=120, line=260, first_line=0))
        
        # Đường kẻ ngang trang trí
        ke = parse_xml(f'<w:p {NS}><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="12" w:space="1" w:color="1F4E79"/></w:pBdr><w:spacing w:after="240" w:line="120" w:lineRule="exact"/><w:ind w:left="2500" w:right="2500"/></w:pPr></w:p>')
        self.add(ke)
        
        # Logo trường
        logo_path = HINH_DIR / "logo-sgu.png"
        if logo_path.exists():
            self.add(img_para(self.doc, logo_path, 4.8))
        else:
            self.add(para("", after=400))
            
        self.add(para(THONG_TIN["loai_bao_cao"], jc="center", b=True, sz=30, before=240, after=200, line=280, first_line=0))
        self.add(para("ĐỀ TÀI:", jc="center", b=True, sz=24, after=80, line=260, first_line=0))
        self.add(para(THONG_TIN["de_tai"], jc="center", b=True, sz=32, after=200, line=340, color="1F4E79", first_line=0))
        self.add(para(f"Sản phẩm phần mềm: **{THONG_TIN['ten_san_pham']}**", jc="center", i=True, sz=24, after=480, line=260, first_line=0))
        
        # Bảng thông tin sinh viên và giảng viên
        cell_xml = lambda t, w, is_b=False: f'<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="{w}"/></w:tcPr><w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr>{runs(t, 26, is_b)}</w:p></w:tc>'
        rows = [
            f'<w:tr>{cell_xml("Sinh viên thực hiện:", 3000, True)}{cell_xml(THONG_TIN["sinh_vien"], 3500, True)}{cell_xml("MSSV: " + THONG_TIN["mssv"], 2500, False)}</w:tr>',
            f'<w:tr>{cell_xml("Giảng viên hướng dẫn:", 3000, True)}{cell_xml(THONG_TIN["giang_vien"], 3500, False)}{cell_xml("", 2500, False)}</w:tr>'
        ]
        grid = '<w:gridCol w:w="3000"/><w:gridCol w:w="3500"/><w:gridCol w:w="2500"/>'
        tbl = parse_xml(f'<w:tbl {NS}><w:tblPr><w:tblW w:type="dxa" w:w="9000"/><w:jc w:val="center"/><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>{"".join(rows)}</w:tbl>')
        self.add(tbl)
        
        self.add(para(THONG_TIN["dia_diem_thoi_gian"], jc="center", sz=26, before=600, after=0, line=260, first_line=0))

    def tao_loi_cam_on(self):
        """Trang lời cảm ơn trang trọng."""
        self.add(page_break())
        self.add(para("LỜI CẢM ƠN", jc="center", b=True, sz=28, before=120, after=240, first_line=0))
        self.p("Lời đầu tiên, em xin bày tỏ lòng biết ơn sâu sắc đến quý Thầy, Cô Khoa Công nghệ Thông tin — Trường Đại học Sài Gòn, những người đã tận tâm truyền đạt tri thức quý báu, nền tảng lý thuyết vững chắc và rèn luyện kỹ năng thực hành cho em trong suốt quá trình học tập tại nhà trường.")
        self.p("Đặc biệt, em xin gửi lời cảm ơn chân thành nhất đến Thầy/Cô hướng dẫn học phần Seminar Chuyên đề. Sự định hướng khoa học, những góp ý chuyên môn chuẩn xác và tinh thần làm việc nghiêm túc của Thầy/Cô là kim chỉ nam giúp em hoàn thiện đồ án này 1 cách chặt chẽ và chỉn chu nhất.")
        self.p("Đề tài *'Xây dựng ứng dụng ngăn người dùng cắm USB flash disk vào máy tính Windows, chạy như dịch vụ không tắt được'* là 1 thử thách thực tế có hàm lượng kỹ thuật hệ thống rất cao, đòi hỏi sự am hiểu sâu rộng về cấu trúc nhân hệ điều hành Windows, mô hình quản lý thiết bị Plug and Play, Service Control Manager, cơ chế bảo mật và giao diện lập trình Win32 API tầng thấp. Dù đã nỗ lực tối đa để hoàn thiện sản phẩm và bản báo cáo này, đề tài khó tránh khỏi những điểm còn có thể phát triển thêm. Em rất mong nhận được những nhận xét, đóng góp quý báu từ quý Thầy, Cô để giải pháp được hoàn thiện hơn nữa trong tương lai.")
        self.p("Kính chúc quý Thầy, Cô luôn dồi dào sức khỏe, niềm vui và tiếp tục gặt hái nhiều thành công trong sự nghiệp giáo dục cao quý.")
        
        self.add(para("TP. Hồ Chí Minh, ngày 17 tháng 11 năm 2026", jc="right", i=True, sz=26, before=240, after=40, first_line=0))
        self.add(para("Sinh viên thực hiện", jc="right", b=True, sz=26, after=180, first_line=0))
        self.add(para(THONG_TIN["sinh_vien"], jc="right", b=True, sz=26, after=0, first_line=0))

    def tao_nhan_xet_giang_vien(self):
        """Trang nhận xét của giảng viên hướng dẫn."""
        self.add(page_break())
        self.add(para("NHẬN XÉT CỦA GIẢNG VIÊN HƯỚNG DẪN", jc="center", b=True, sz=28, before=100, after=200, first_line=0))
        for _ in range(9):
            self.add(para("...................................................................................................................................", jc="left", after=100, line=240, first_line=0))
        
        self.add(para("Điểm đánh giá: .................... (Bằng chữ: ....................................................................)", jc="left", b=True, sz=26, before=140, after=180, first_line=0))
        self.add(para("TP. Hồ Chí Minh, ngày ...... tháng ...... năm 2026", jc="right", i=True, sz=26, after=40, first_line=0))
        self.add(para("Giảng viên hướng dẫn", jc="right", b=True, sz=26, after=160, first_line=0))
        self.add(para("(Ký và ghi rõ họ tên)", jc="right", i=True, sz=22, after=0, first_line=0))

    def tao_muc_luc(self):
        """Tạo vị trí cho Mục lục (sẽ điền nội dung sau khi duyệt toàn bộ chương)."""
        self.add(page_break())
        self.add(para("MỤC LỤC", jc="center", b=True, sz=28, before=120, after=200, first_line=0))
        self.cho_muc_luc = para("", after=0, first_line=0)
        self.add(self.cho_muc_luc)

    def tao_danh_muc_hinh(self):
        """Tạo vị trí cho Danh mục hình vẽ."""
        self.add(page_break())
        self.add(para("DANH MỤC HÌNH VẼ", jc="center", b=True, sz=28, before=120, after=200, first_line=0))
        self.cho_danh_muc_hinh = para("", after=0, first_line=0)
        self.add(self.cho_danh_muc_hinh)

    def tao_danh_muc_bang(self):
        """Tạo vị trí cho Danh mục bảng biểu."""
        self.add(page_break())
        self.add(para("DANH MỤC BẢNG BIỂU", jc="center", b=True, sz=28, before=120, after=200, first_line=0))
        self.cho_danh_muc_bang = para("", after=0, first_line=0)
        self.add(self.cho_danh_muc_bang)

    def hoan_tat_muc_luc(self):
        """Điền nội dung các mục vào Mục lục, Danh mục hình và Danh mục bảng."""
        # 1. Điền Mục lục
        for lv, title in self.headings:
            # Bỏ qua chính trang mục lục và bìa
            if title in ("MỤC LỤC", "DANH MỤC HÌNH VẼ", "DANH MỤC BẢNG BIỂU"):
                continue
            pg = self.page_map.get(title, "1")
            self.cho_muc_luc.addprevious(toc_entry(title, pg, level=lv))

        # 2. Điền Danh mục hình vẽ
        for fig_id, caption_text in self.figures:
            pg = self.page_map.get(caption_text, "1")
            self.cho_danh_muc_hinh.addprevious(toc_entry(caption_text, pg, level=1))

        # 3. Điền Danh mục bảng biểu
        for tbl_id, caption_text in self.tables:
            pg = self.page_map.get(caption_text, "1")
            self.cho_danh_muc_bang.addprevious(toc_entry(caption_text, pg, level=1))

    def tao_danh_muc_tu_viet_tat(self):
        """Bảng tra cứu các thuật ngữ viết tắt trong báo cáo."""
        self.add(page_break())
        self.add(para("DANH MỤC THUẬT NGỮ VÀ TỪ VIẾT TẮT", jc="center", b=True, sz=28, before=120, after=200, first_line=0))
        
        headers = ["Từ viết tắt", "Tên tiếng Anh đầy đủ", "Ý nghĩa trong hệ thống UsbGuard"]
        widths = [1500, 3100, 4471]
        rows = [
            ["ACL", "Access Control List", "Danh sách kiểm soát quyền truy cập tài nguyên của Windows."],
            ["API", "Application Programming Interface", "Giao diện lập trình ứng dụng kết nối với hệ điều hành."],
            ["BOT", "Bulk-Only Transport", "Giao thức truyền tải dữ liệu tuần tự chuẩn cho USB Mass Storage."],
            ["CfgMgr32", "Configuration Manager API", "Thư viện Win32 quản lý trạng thái thiết bị và gỡ an toàn."],
            ["CI/CD", "Continuous Integration / Deployment", "Hệ thống tự động tích hợp và kiểm thử liên tục."],
            ["DACL", "Discretionary Access Control List", "Danh sách phân quyền chi tiết cho người dùng và tiến trình."],
            ["DLP", "Data Loss Prevention", "Giải pháp phòng chống thất thoát dữ liệu trong doanh nghiệp."],
            ["GPO", "Group Policy Object", "Đối tượng chính sách nhóm quản trị tập trung trên Windows."],
            ["GUID", "Globally Unique Identifier", "Mã định danh duy nhất toàn cầu phân loại thiết bị phần cứng."],
            ["HID", "Human Interface Device", "Chuẩn thiết bị ngoại vi giao tiếp người dùng (chuột, bàn phím)."],
            ["HKLM", "HKEY_LOCAL_MACHINE", "Phân nhánh Registry lưu cấu hình phần cứng và hệ thống."],
            ["IOCTL", "Input/Output Control", "Mã lệnh giao tiếp tầng thấp giữa ứng dụng và driver thiết bị."],
            ["PBKDF2", "Password-Based Key Derivation Function 2", "Thuật toán băm và dẫn xuất khóa bảo mật theo chuẩn RFC 8018."],
            ["PID", "Product Identifier", "Mã nhận dạng chủng loại sản phẩm do nhà sản xuất gắn vào USB."],
            ["PnP", "Plug and Play", "Cơ chế tự động phát hiện và cấu hình phần cứng của Windows."],
            ["SCM", "Service Control Manager", "Tiến trình quản lý vòng đời toàn bộ dịch vụ của Windows."],
            ["SetupAPI", "Device Installation API", "Bộ hàm Win32 liệt kê và truy vấn thuộc tính phần cứng."],
            ["SID", "Security Identifier", "Mã định danh bảo mật duy nhất cho tài khoản và nhóm người dùng."],
            ["UAC", "User Account Control", "Cơ chế kiểm soát phân quyền tài khoản quản trị trên Windows."],
            ["UAS", "USB Attached SCSI Protocol", "Giao thức lưu trữ USB tốc độ cao sử dụng tập lệnh SCSI."],
            ["VID", "Vendor Identifier", "Mã định danh nhà sản xuất thiết bị do tổ chức USB-IF cấp."],
            ["WMI", "Windows Management Instrumentation", "Hạ tầng quản lý và theo dõi sự kiện phần cứng của Windows."]
        ]
        self.tbl("TBL_ABBR", "Bảng 0.1: Danh mục thuật ngữ và từ viết tắt kỹ thuật", headers, rows, widths, ["center", "left", "left"], sz=17)

    # ==========================================================================
    # CHƯƠNG 1: TỔNG QUAN
    # ==========================================================================
    def tao_chuong_1(self):
        self.h1("CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI")
        
        self.h2("1.1. Đề tài và bối cảnh nghiên cứu")
        self.p("Trong kỷ nguyên chuyển đổi số hiện nay, an toàn thông tin tại các cơ quan, doanh nghiệp và trường học đối mặt với những thách thức ngày càng tinh vi. Thiết bị lưu trữ di động kết nối qua cổng USB (USB flash disk, ổ cứng di động) là phương tiện trao đổi dữ liệu vô cùng tiện lợi và phổ biến nhờ kích thước nhỏ gọn, dung lượng lớn và khả năng tương thích cao. Tuy nhiên, tính tiện lợi này đồng thời biến cổng USB thành 1 trong những vectơ tấn công nguy hiểm hàng đầu đối với an ninh máy tính.")
        self.p("Đề tài Seminar Chuyên đề được đặt ra với nhiệm vụ trọng tâm: *'Xây dựng ứng dụng ngăn người dùng cắm USB flash disk vào máy hệ điều hành Windows, ứng dụng được chạy như dịch vụ không tắt được'*. Mục tiêu là tạo ra 1 công cụ kiểm soát thiết bị ngoại vi chuyên dụng, mang tên **UsbGuard 1.2**, nhằm vô hiệu hóa khả năng đọc/ghi dữ liệu trái phép qua các thiết bị lưu trữ USB mà không làm gián đoạn các thiết bị ngoại vi cần thiết khác như chuột và bàn phím. Sản phẩm hoàn chỉnh gồm dịch vụ chạy nền, giao diện quản lý đồ họa và bộ cài `setup.exe`, đã được kiểm thử bằng cách cắm USB thật vào Windows 10 và Windows 11, cùng 1 lượt thử thủ công trên máy Windows thật với USB vật lý.")

        self.h2("1.2. Lý do chọn đề tài và tính cấp thiết")
        self.p("Thực tế vận hành tại các tổ chức cho thấy cổng USB tiềm ẩn 2 rủi ro an ninh nghiêm trọng bậc nhất:")
        self.b("**Rò rỉ dữ liệu nội bộ (Data Leakage):** Nhân viên hoặc người lạ có thể cắm USB flash disk vào máy tính nội bộ và sao chép hàng gigabyte tài liệu mật, mã nguồn, thông tin khách hàng chỉ trong vài phút. Theo các báo cáo an ninh mạng toàn cầu, các vụ thất thoát dữ liệu do sử dụng USB trái phép chiếm tỷ trọng đáng kể trong các vi phạm an toàn nội bộ.")
        self.b("**Lây nhiễm mã độc có chủ đích (Malware Propagation):** Thiết bị USB là phương tiện truyền thống nhưng cực kỳ hiệu quả để đưa mã độc vượt qua các lớp phòng thủ tường lửa và mạng cách ly (air-gapped networks). Minh chứng lịch sử rõ ràng nhất là sâu máy tính Stuxnet được phát hiện năm 2010; mã độc này đã lây nhiễm thành công vào hệ thống điều khiển công nghiệp ly tâm tại nhà máy hạt nhân Natanz thông qua thiết bị USB flash disk của các chuyên gia kỹ thuật, gây thiệt hại vật lý nặng nề cho các thiết bị điều khiển logic khả trình (PLC). Viết lại bài học này, các chuyên gia an ninh khẳng định việc cô lập cổng USB vật lý đối với thiết bị lưu trữ là yêu cầu sống còn của các hệ thống trọng yếu.")
        self.p("Các hệ điều hành Windows mặc định cho phép người dùng cắm và sử dụng thiết bị USB tự do. Mặc dù các phiên bản Windows cao cấp (Windows Enterprise / Education) có hỗ trợ Group Policy hoặc Intune, chi phí triển khai giải pháp này là rất lớn và không phù hợp với các hệ thống Windows Home/Pro đơn lẻ hoặc các phòng thực hành tin học giáo dục. Do đó, việc xây dựng 1 giải pháp độc lập, gọn nhẹ, chạy như 1 dịch vụ hệ thống không thể bị tắt bởi người dùng thông thường là yêu cầu vô cùng cấp thiết.")

        self.h2("1.3. Mục tiêu nghiên cứu và phát triển sản phẩm")
        self.p("Đề tài tập trung giải quyết các mục tiêu khoa học và kỹ thuật cụ thể sau:")
        self.b("**Mục tiêu 1:** Ngăn chặn hiệu quả mọi thiết bị USB flash disk và ổ lưu trữ di động khi cắm vào máy tính Windows, đạt thời gian phản ứng dưới 2 giây.")
        self.b("**Mục tiêu 2:** Bảo toàn hoạt động bình thường của các thiết bị ngoại vi giao tiếp người dùng chuẩn HID (Human Interface Device) như chuột quang USB, bàn phím USB, không gây gián đoạn công việc của người dùng.")
        self.b("**Mục tiêu 3:** Đạt tính chất 'không tắt được': Dịch vụ từ chối mọi lệnh dừng từ người dùng thường (mã lỗi 5), từ chối lệnh dừng trực tiếp từ Administrator qua SCM (mã lỗi 1052), và tự động phục hồi sau 5 giây nếu tiến trình bị cưỡng chế kết thúc.")
        self.b("**Mục tiêu 4:** Hỗ trợ cơ chế quản trị linh hoạt và bảo mật: Hỗ trợ 3 chế độ vận hành (CHẶN TẤT CẢ, DANH SÁCH CHO PHÉP, TẠM DỪNG); xác thực quản trị bằng thuật toán băm PBKDF2; bảo vệ cấu hình trong Registry bằng phân quyền DACL nghiêm ngặt.")

        self.h2("1.4. Đối tượng, phạm vi và giới hạn của đề tài")
        self.p("**Đối tượng nghiên cứu:** Kiến trúc hệ thống Windows, cây thiết bị Plug and Play, mô hình Windows Service, Service Control Manager (SCM), Windows Registry, chuẩn lưu trữ USB Mass Storage (BOT/UAS), và các API Win32 tầng thấp.")
        self.p("**Phạm vi áp dụng:** Hệ điều hành Microsoft Windows 64-bit (bao gồm Windows 10, Windows 11, Windows Server 2022 và Windows Server 2025).")
        self.p("**Phạm vi sản phẩm:** UsbGuard 1.2 gồm dịch vụ chạy nền (3 tầng chặn, lớp gỡ thiết bị, 3 chế độ vận hành, cơ chế 'không tắt được'), giao diện quản lý đồ họa WinForms, bộ cài `setup.exe` tiếng Việt có đặt mật khẩu và trình gỡ, cùng quy trình kiểm thử tự động có cắm USB thật trên Windows 10 và Windows 11. Bản 1.2 bổ sung tự nạp lại USB đã bị Windows tháo và khoá chống dò mật khẩu.")
        self.p("**Giới hạn kỹ thuật đã xác định:**")
        self.b("Phiên bản hiện tại tập trung vào kiểm soát các thiết bị lưu trữ dạng khối (Mass Storage Class và UAS). Các thiết bị truyền thông đa phương tiện MTP/PTP (như điện thoại thông minh Android/iOS) và ổ đĩa quang CD/DVD chưa nằm trong phạm vi xử lý.")
        self.b("Danh sách cho phép nhận diện USB theo số serial (hoặc chuỗi VID/PID); với các thiết bị cùng model không có số serial duy nhất từ nhà sản xuất, chính sách sẽ áp dụng chung.")
        self.b("Ranh giới đạo đức và kỹ thuật: UsbGuard là giải pháp Device Control chính quy của doanh nghiệp, không phải mã độc ẩn mình (rootkit). Quản trị viên nắm mật khẩu hợp lệ luôn có quyền gỡ cài đặt công khai qua lệnh `uninstall`.")

        self.h2("1.5. Phương pháp nghiên cứu và thực hiện")
        self.p("Đề tài kết hợp phương pháp nghiên cứu lý thuyết chuyên sâu và thực nghiệm kỹ thuật đa tầng:")
        self.b("Nghiên cứu tài liệu chính thống của Microsoft về kiến trúc trình điều khiển, mô hình bảo mật Windows, và chuẩn RFC 8018 về mật mã học.")
        self.b("Khảo sát và đối chiếu thiết kế với 4 dự án mã nguồn mở uy tín cùng chủ đề.")
        self.b("Phát triển sản phẩm bằng ngôn ngữ C# trên nền tảng .NET Framework 4.8, sử dụng kỹ thuật P/Invoke để tương tác trực tiếp với các thư viện lõi hệ thống (`setupapi.dll`, `cfgmgr32.dll`, `kernel32.dll`, `advapi32.dll`, `wtsapi32.dll`).")
        D = lay_du_lieu()
        self.b(f"Xây dựng quy trình kiểm thử tự động trên GitHub Actions: {D['u22']['tong']} ca unit test, {D['t22']['tong']} ca kiểm thử tích hợp trên Windows Server 2022 và 2025, {D['w10']['tong']} ca kiểm thử cắm USB thật trên Windows 10 và Windows 11, cùng 1 lượt thử trên máy thật.")

        self.h2("1.6. Bố cục của báo cáo")
        self.p("Nội dung báo cáo được cấu trúc thành 6 chương logic:")
        self.b("**Chương 1:** Bối cảnh, lý do chọn đề tài, mục tiêu, phạm vi và phương pháp.")
        self.b("**Chương 2:** Cơ sở lý thuyết (USB, PnP, SCM, Registry, chính sách thiết bị) và khảo sát giải pháp hiện có.")
        self.b("**Chương 3:** Phân tích và thiết kế: yêu cầu, ca sử dụng, kiến trúc 3 tầng chặn và lớp gỡ thiết bị, 3 chế độ, cơ chế không tắt được, bảo mật.")
        self.b("**Chương 4:** Cài đặt: mã nguồn cốt lõi, tập lệnh CLI, giao diện quản lý, bộ cài `setup.exe`, hướng dẫn vận hành.")
        self.b(f"**Chương 5:** Kiểm thử: {D['u22']['tong']} ca unit, {D['t22']['tong']} ca tích hợp trên Windows Server, {D['w10']['tong']} ca cắm USB thật trên Windows 10 và Windows 11, thử trên máy thật, các lỗi phát hiện và cách sửa, đánh giá yêu cầu.")
        self.b("**Chương 6:** Kết luận, hạn chế và hướng phát triển.")

    # ==========================================================================
    # CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ KHẢO SÁT HIỆN TRẠNG
    # ==========================================================================
    def tao_chuong_2(self):
        self.h1("CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ KHẢO SÁT HIỆN TRẠNG")
        
        self.h2("2.1. Chuẩn giao tiếp và giao thức lưu trữ USB Mass Storage")
        self.p("Chuẩn USB Mass Storage Class (MSC) là tập hợp các đặc tả kỹ thuật do tổ chức USB Implementers Forum (USB-IF) ban hành, cho phép các thiết bị lưu trữ ngoại vi kết nối và trao đổi dữ liệu với máy tính chủ. Trong môi trường Windows, 2 giao thức truyền tải chính được áp dụng:")
        self.b("**Bulk-Only Transport (BOT):** Là giao thức truyền thống sử dụng 3 giai đoạn tuần tự: Command Transport (gửi lệnh qua gói CBW), Data Transport (truyền nhận dữ liệu qua luồng Bulk), và Status Transport (nhận trạng thái thực thi qua gói CSW). Do hoạt động theo mô hình 1 lệnh tại 1 thời điểm (half-duplex), BOT có hiệu năng hạn chế nhưng tương thích với hầu hết thiết bị USB flash disk đời cũ.")
        self.b("**USB Attached SCSI Protocol (UAS/UASP):** Là giao thức hiện đại chuẩn hóa trên USB 3.0, đưa tập lệnh SCSI (Small Computer System Interface) vào kênh truyền USB. UAS hỗ trợ kỹ thuật xếp hàng lệnh Native Command Queuing (NCQ) lên đến 32 lệnh song song, nâng cao tốc độ truyền tải ngẫu nhiên cho các ổ cứng di động SSD và USB flash disk tốc độ cao.")
        self.p("Khi người dùng cắm USB vào máy, hệ điều hành tự động nạp trình điều khiển `USBSTOR.SYS` (đối với chuẩn BOT) hoặc `UASPSTOR.SYS` (đối với chuẩn UAS). Do đó, 1 giải pháp chặn thiết bị USB hiệu quả bắt buộc phải tác động đồng thời lên cả 2 trình điều khiển này.")

        self.h2("2.2. Mô hình Driver và cơ chế Plug and Play (PnP) của Windows")
        self.p("Cơ chế Plug and Play (PnP) là phân hệ cốt lõi của Windows chịu trách nhiệm phát hiện, nạp trình điều khiển và cấu hình tài nguyên cho các thiết bị phần cứng mới kết nối. PnP tổ chức toàn bộ phần cứng trong hệ thống dưới dạng 1 cây phân cấp (Device Tree), trong đó mỗi thiết bị là 1 nút thực thể (devnode).")
        self.p("Mỗi devnode chứa các thông tin định danh phần cứng quan trọng:")
        self.b("**Device Instance ID:** Chuỗi định danh duy nhất của thiết bị trong hệ thống, ví dụ: `USB\\VID_0951&PID_1666\\08606E6B`. Chuỗi này bao gồm mã nhà sản xuất (VID - Vendor ID), mã sản phẩm (PID - Product ID) và số serial thiết bị.")
        self.b("**Class GUID:** Mã định danh lớp thiết bị. Đối với ổ đĩa lưu trữ, mã lớp chuẩn là `GUID_DEVINTERFACE_DISK` (`{53f56307-b6bf-11d0-94f2-00a0c91efb8b}`).")
        self.p("Quan hệ cha-con trong cây thiết bị là chìa khóa then chốt cho bài toán cô lập an toàn: Nút ổ đĩa lưu trữ (Disk Node) là con của Nút thiết bị USB vật lý (Parent USB Node), và Nút USB vật lý này lại là con của Bộ chia cổng USB (USB Hub). Nếu 1 chương trình thực hiện gỡ bỏ nhầm vào nút USB Hub, toàn bộ các thiết bị cắm chung cổng hub đó (bao gồm chuột và bàn phím) sẽ bị ngắt kết nối hoàn toàn.")

        self.h2("2.3. Kiến trúc Windows Service và Service Control Manager (SCM)")
        self.p("Windows Service là 1 ứng dụng chạy ngầm trong không gian người dùng đặc quyền mà không cần có phiên đăng nhập tương tác (chạy ngay cả khi chưa có người dùng đăng nhập vào màn hình desktop). Trung tâm điều phối toàn bộ dịch vụ trên hệ điều hành là **Service Control Manager (SCM)** (`services.exe`).")
        self.p("Vòng đời và đặc tính kỹ thuật của Windows Service bao gồm:")
        self.b("**Tài khoản thực thi:** Dịch vụ bảo mật chạy dưới tài khoản `NT AUTHORITY\\LocalSystem`. Đây là tài khoản dịch vụ có đặc quyền cao nhất trong hệ điều hành Windows, có toàn quyền can thiệp vào Registry hệ thống và gọi các API điều khiển thiết bị.")
        self.b("**Kiểu khởi động (Start Type):** Cấu hình `auto` (Automatic) đảm bảo dịch vụ tự động khởi chạy cùng hệ điều hành trước khi màn hình đăng nhập của người dùng xuất hiện.")
        self.b("**Mã điều khiển (Control Codes):** SCM giao tiếp với dịch vụ qua các thông điệp điều khiển như `SERVICE_CONTROL_STOP`, `SERVICE_CONTROL_PAUSE`, `SERVICE_CONTROL_SHUTDOWN`. Lớp `ServiceBase` trong .NET cho phép lập trình viên kiểm soát việc chấp nhận hay từ chối các mã điều khiển này thông qua các thuộc tính chuyên biệt.")
        self.b("**Cơ chế phục hồi sự cố (Service Recovery):** Lệnh hệ thống `sc.exe failure` cho phép đăng ký với SCM các hành động tự động khi tiến trình dịch vụ bị chấm dứt bất thường (crash hoặc bị kill bởi taskkill), ví dụ: khởi động lại dịch vụ sau 1 khoảng thời gian xác định.")

        self.h2("2.4. Cấu trúc Windows Registry và các khóa quản lý phần cứng")
        self.p("Windows Registry là cơ sở dữ liệu cấu hình phân cấp trung tâm của hệ điều hành. Các khóa Registry đóng vai trò quyết định trong việc hệ thống có nạp trình điều khiển phần cứng hay không:")
        self.p("Tại phân nhánh `HKLM\\SYSTEM\\CurrentControlSet\\Services\\<DriverName>`, giá trị `Start` (kiểu DWORD) quy định chế độ nạp trình điều khiển:")
        self.b("`Start = 0` (Boot): Nạp bởi boot loader của hệ điều hành.")
        self.b("`Start = 1` (System): Nạp trong giai đoạn khởi tạo kernel.")
        self.b("`Start = 2` (Automatic): Nạp tự động bởi tiến trình khởi động hệ thống.")
        self.b("`Start = 3` (Demand/Manual): Nạp theo nhu cầu khi thiết bị phần cứng tương ứng được cắm vào máy (đây là giá trị mặc định của `USBSTOR` và `UASPStor`).")
        self.b("`Start = 4` (Disabled): Trình điều khiển bị vô hiệu hóa hoàn toàn. Hệ điều hành từ chối nạp driver cho thiết bị.")

        self.h2("2.5. Chính sách Group Policy về thiết bị lưu trữ di động")
        self.p("Trên các phiên bản Windows chuyên nghiệp, Microsoft cung cấp chính sách quản lý lưu trữ di động tại đường dẫn Registry: `HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\RemovableStorageDevices`. Khi kích hoạt giá trị `Deny_All = 1`, hệ điều hành sẽ chặn toàn bộ các thao tác đọc và ghi đối với mọi thiết bị thuộc phân lớp lưu trữ tháo rời (`DiskClass`: `{53f56307-b6bf-11d0-94f2-00a0c91efb8b}` với các cờ `Deny_Read = 1`, `Deny_Write = 1`, `Deny_Execute = 1`). Kết hợp giá trị chính sách này với việc khóa driver `Start = 4` sẽ tạo ra 1 lớp phòng ngự chính sách vững chắc.")
        self.p("Windows còn có chính sách thứ 2 là **Device Installation Restrictions** (hạn chế cài đặt thiết bị) tại `HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeviceInstall\\Restrictions`. Khi giá trị `DenyDeviceIDs = 1`, Windows từ chối cài đặt mọi thiết bị có Hardware ID hoặc Compatible ID nằm trong danh sách ở khoá con `DenyDeviceIDs` (mỗi mục là 1 giá trị chuỗi). Mọi ổ USB lưu trữ đều có Compatible ID bắt đầu bằng `USB\\Class_08` (lớp Mass Storage), còn chuột và bàn phím thuộc lớp HID (`Class_03`), nên có thể cấm đúng ổ lưu trữ mà không ảnh hưởng thiết bị nhập liệu.")

        self.h2("2.6. Bộ giao diện lập trình Win32 API tầng thấp")
        self.p("Để can thiệp sâu vào phần cứng và điều khiển thiết bị theo thời gian thực, UsbGuard sử dụng kỹ thuật Platform Invoke (P/Invoke) để gọi trực tiếp các hàm Win32 API từ các thư viện động (DLL) chuẩn của Windows:")
        self.b("**SetupAPI (`setupapi.dll`):** Hàm `SetupDiGetClassDevs` khởi tạo danh sách thiết bị thuộc lớp `GUID_DEVINTERFACE_DISK`. Hàm `SetupDiEnumDeviceInterfaces` và `SetupDiGetDeviceInterfaceDetail` cho phép duyệt qua từng ổ đĩa và lấy đường dẫn thiết bị dạng chuỗi (`\\\\?\\usbstor#disk...`).")
        self.b("**Storage IOCTL (`kernel32.dll`):** Ứng dụng mở thiết bị bằng `CreateFile` với cờ truy cập thuộc tính (quyền 0) và gửi mã điều khiển `IOCTL_STORAGE_QUERY_PROPERTY` qua hàm `DeviceIoControl`. Cấu trúc trả về `STORAGE_DEVICE_DESCRIPTOR` chứa trường `BusType`. Khi `BusType = 7` (`BusTypeUsb`), ứng dụng xác định chính xác ổ đĩa này đang kết nối qua bus USB.")
        self.b("**Configuration Manager (`cfgmgr32.dll`):** Hàm `CM_Request_Device_Eject` gửi yêu cầu ngắt kết nối an toàn thiết bị phần cứng tới PnP Manager. Hàm `CM_Get_Parent` cho phép truy ngược cây thiết bị lên nút cha để lấy thông tin USB vật lý.")
        self.b("**Terminal Services (`wtsapi32.dll`):** Dịch vụ chạy trong Session 0 tách biệt. Để hiển thị cảnh báo cho người dùng đang ngồi trước màn hình máy tính, ứng dụng gọi `WTSGetActiveConsoleSessionId` và `WTSSendMessage` để đẩy hộp thoại cảnh báo ra màn hình desktop thực tế.")

        self.h2("2.7. Cơ chế theo dõi sự kiện qua Windows Management Instrumentation (WMI)")
        self.p("Để đạt thời gian phản ứng tức thì khi người dùng vừa cắm thiết bị, thay vì chỉ dựa vào vòng lặp kiểm tra định kỳ (polling) gây trễ, UsbGuard đăng ký lắng nghe sự kiện WMI thông qua lớp `ManagementEventWatcher`. Câu truy vấn WQL:")
        self.code("SELECT * FROM __InstanceCreationEvent WITHIN 1 WHERE TargetInstance ISA 'Win32_DiskDrive'")
        self.p("Ngay khi Windows phát hiện 1 ổ đĩa mới xuất hiện trong hệ thống, sự kiện `EventArrived` được kích hoạt ngay lập tức, cho phép UsbGuard quét và gỡ bỏ ổ đĩa USB trong vòng vài phần trăm giây trước khi người dùng kịp mở File Explorer.")

        self.h2("2.8. Mô hình phân quyền bảo mật Windows (SID, ACL/DACL và UAC)")
        self.p("Hệ điều hành Windows quản lý quyền truy cập tài nguyên (tệp tin, khóa Registry, dịch vụ) thông qua hệ thống mô tả bảo mật (Security Descriptor). Mỗi người dùng và tiến trình được gán 1 mã định danh bảo mật duy nhất gọi là **SID (Security Identifier)**:")
        self.b("`S-1-5-18` (`WellKnownSidType.LocalSystemSid`): Tài khoản LocalSystem của dịch vụ.")
        self.b("`S-1-5-32-544` (`WellKnownSidType.BuiltinAdministratorsSid`): Nhóm quản trị viên máy tính.")
        self.b("`S-1-5-32-545` (`WellKnownSidType.BuiltinUsersSid`): Nhóm người dùng thông thường.")
        self.p("Danh sách kiểm soát quyền truy cập tùy ý (**DACL - Discretionary Access Control List**) quy định cụ thể quyền đọc, ghi, xóa của từng SID trên đối tượng. Khi tạo khóa Registry `HKLM\\SOFTWARE\\UsbGuard`, nếu ứng dụng ngắt quyền kế thừa từ khóa cha và chỉ gán quyền `FullControl` cho LocalSystem và Administrators, thì nhóm Users thông thường sẽ bị hệ điều hành từ chối hoàn toàn khi cố gắng truy cập khóa này.")

        self.h2("2.9. Chuẩn băm và dẫn xuất khóa bảo mật PBKDF2")
        self.p("Để bảo vệ mật khẩu quản trị, UsbGuard tuân thủ chuẩn mật mã học quốc tế **RFC 8018 (PKCS #5 v2.0)** về hàm dẫn xuất khóa dựa trên mật khẩu (**PBKDF2** - Password-Based Key Derivation Function 2):")
        self.b("**Muối ngẫu nhiên (Salt):** Mỗi lần băm mật khẩu, hệ thống sinh ra 1 chuỗi muối ngẫu nhiên 16 byte (128 bit) bằng bộ sinh số ngẫu nhiên an toàn mật mã học (`RandomNumberGenerator`). Việc sử dụng muối riêng biệt ngăn chặn các cuộc tấn công tra cứu bảng tính sẵn (Rainbow Table).")
        self.b("**Số vòng lặp (Iterations):** Bản 1.2 dùng HMAC-SHA256, 600000 vòng (trước là SHA1, 100000 vòng). Số vòng lớn làm tăng chi phí tính toán, chống vét cạn (brute-force) bằng GPU.")
        self.b("**So sánh thời gian hằng (Constant-Time Comparison):** Khi kiểm tra mật khẩu, việc so sánh 2 mảng byte được thực hiện bằng toán tử XOR trên toàn bộ độ dài chuỗi (`diff |= a[i] ^ b[i]`), không dừng sớm khi phát hiện ký tự sai. Kỹ thuật này ngăn chặn nguy cơ rò rỉ thông tin qua tấn công kênh kề đo thời gian thực thi (Timing Attack).")

        self.h2("2.10. Khảo sát các giải pháp hiện có và bảng so sánh")
        self.p("Trước khi thiết kế UsbGuard, tác giả đã khảo sát và phân tích ưu, nhược điểm của các giải pháp kỹ thuật hiện có trên thị trường:")
        self.b("**Group Policy (GPO):** Phù hợp môi trường mạng Active Directory, nhưng không khả dụng trên Windows Home và đòi hỏi hạ tầng máy chủ phức tạp.")
        self.b("**Microsoft Intune / Defender Device Control:** Quản trị đám mây mạnh mẽ nhưng đòi hỏi thuê bao đắt đỏ (gói E5) và kết nối mạng liên tục.")
        self.b("**Phần mềm DLP thương mại (Symantec, McAfee):** Chi phí cao, cấu hình cồng kềnh và chiếm dụng lớn tài nguyên bộ nhớ (trên 500 MB RAM).")
        self.b("**Các dự án mã nguồn mở tham khảo:** `JBalanza/USBBlocker` (khóa màn hình khi cắm USB lạ, gây bất tiện); `sidd607/usbAlert` (bắt sự kiện SetupAPI nhưng thiếu lớp chặn driver và chống tắt); `amir13872/usb-control-application` (chạy dạng ứng dụng thường, dễ bị tắt qua Task Manager); `Den-Sec/USBBlocker` (PowerShell thao tác Registry khóa USBSTOR).")

        headers_ss = ["Tiêu chí so sánh", "Group Policy (GPO)", "Microsoft Intune", "Dự án nguồn mở tham khảo", "Giải pháp UsbGuard 1.2"]
        widths_ss = [2200, 2200, 2200, 2200, 2271]
        rows_ss = [
            ["Yêu cầu hạ tầng", "Active Directory / Domain", "Đám mây Azure / Intune", "Máy tính cá nhân", "Độc lập, mọi bản Windows"],
            ["Kiến trúc phòng thủ", "1 lớp (Chính sách)", "Đa lớp (Cloud + Kernel)", "1 lớp (Hook hoặc Polling)", "3 tầng chặn + lớp gỡ thiết bị"],
            ["Cơ chế chống tắt", "Phụ thuộc quyền Domain", "Dịch vụ bảo vệ chuyên biệt", "Dễ bị tắt qua Task Manager", "CanStop=false + DACL + sc failure"],
            ["Chế độ Whitelist", "Hỗ trợ theo Device ID", "Hỗ trợ linh hoạt", "Hỗ trợ cơ bản", "Hỗ trợ 3 chế độ (All/Allow/Pause)"],
            ["Bảo vệ chuột/bàn phím", "Cần cấu hình phân lớp", "Tự động phân lớp", "Dễ bị xung đột gỡ nhầm", "Bảo toàn nhờ MaxDepth=2"],
            ["Chi phí bản quyền", "Bản quyền Windows Pro+", "Chi phí thuê bao đắt đỏ", "Miễn phí", "Mã nguồn mở, hoàn toàn miễn phí"]
        ]
        self.tbl("TBL_SS", "Bảng 2.1: So sánh tổng hợp các giải pháp kiểm soát cổng USB", headers_ss, rows_ss, widths_ss, ["left", "left", "left", "left", "left"], sz=18)

    # ==========================================================================
    # CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG
    # ==========================================================================
    def tao_chuong_3(self):
        self.h1("CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG")
        
        self.h2("3.1. Yêu cầu hệ thống")
        self.p("Dựa trên đề bài và mục tiêu an ninh, hệ thống UsbGuard được thiết kế với danh sách các yêu cầu chức năng (YC-CN) và yêu cầu phi chức năng (YC-PCN) nghiêm ngặt sau:")
        
        headers_yc = ["Mã yêu cầu", "Phân loại", "Mô tả chi tiết nội dung yêu cầu", "Tiêu chuẩn chấp thuận"]
        widths_yc = [1500, 1600, 4200, 3771]
        rows_yc = [
            ["YC-CN01", "Chức năng", "Chặn tự động mọi USB flash disk và ổ đĩa di động.", "Ổ đĩa bị chặn hoặc gỡ trong thời gian <= 2 giây."],
            ["YC-CN02", "Chức năng", "Bảo vệ các thiết bị ngoại vi HID (chuột, bàn phím).", "Chuột và bàn phím hoạt động liên tục, không bị ảnh hưởng."],
            ["YC-CN03", "Chức năng", "Hỗ trợ 3 chế độ hoạt động linh hoạt.", "Chuyển đổi mượt mà giữa CHẶN TẤT CẢ, CHO PHÉP, TẠM DỪNG."],
            ["YC-CN04", "Chức năng", "Quản lý danh sách thiết bị cho phép (Whitelist).", "Cho phép thêm, xóa, xem các thiết bị USB được phê duyệt."],
            ["YC-CN05", "Chức năng", "Tạm dừng chế độ chặn có thời hạn định mức.", "Tự động kích hoạt lại chế độ chặn khi hết thời gian tạm dừng."],
            ["YC-CN06", "Chức năng", "Xác thực bảo mật mật khẩu quản trị.", "Yêu cầu mật khẩu đối với mọi lệnh quản trị nhạy cảm; nhập sai nhiều lần thì bị khoá tăng dần."],
            ["YC-CN07", "Chức năng", "Gỡ cài đặt an toàn và hoàn trả cài đặt gốc.", "Dừng dịch vụ đúng quy trình, khôi phục mặc định Registry."],
            ["YC-CN08", "Chức năng", "Giao diện quản lý đồ họa cho người không rành dòng lệnh.", "Xem trạng thái, cho phép USB đang cắm, tạm dừng, gỡ cài đặt có mật khẩu."],
            ["YC-CN09", "Chức năng", "Bộ cài setup.exe có đặt mật khẩu và trình gỡ.", "Cài đủ 3 tầng chặn; gỡ bắt buộc đúng mật khẩu."],
            ["YC-PCN01", "Phi chức năng", "Cơ chế 'không tắt được' đối với người dùng.", "SCM từ chối lệnh Stop (lỗi 1052); User thường bị chặn (lỗi 5)."],
            ["YC-PCN02", "Phi chức năng", "Tự phục hồi sau sự cố cưỡng chế tiến trình.", "Windows tự động chạy lại dịch vụ sau khoảng 5 giây (cấu hình 5000 ms)."],
            ["YC-PCN03", "Phi chức năng", "Hiệu năng tiêu thụ tài nguyên tối thiểu.", "Chiếm dụng CPU < 1%, tiêu thụ bộ nhớ RAM < 50 MB."],
            ["YC-PCN04", "Phi chức năng", "Bảo mật thông tin cấu hình và mã băm mật khẩu.", "DACL khóa chặt HKLM\\SOFTWARE\\UsbGuard, chỉ SYSTEM/Admin đọc."]
        ]
        self.tbl("TBL_YC", "Bảng 3.1: Danh mục yêu cầu chức năng và phi chức năng của UsbGuard", headers_yc, rows_yc, widths_yc, ["center", "center", "left", "left"])

        self.h2("3.2. Phân tích tác nhân và biểu đồ ca sử dụng (Use Case)")
        self.p("Hệ thống tương tác với 3 tác nhân (Actor) chính:")
        self.b("**Người dùng thông thường (Standard User):** Là người sử dụng máy tính với tài khoản không có quyền quản trị. Người dùng này chỉ có quyền cắm thiết bị ngoại vi và xem trạng thái công khai của dịch vụ, bị từ chối khi cố tình can thiệp dịch vụ hoặc chỉnh sửa Registry.")
        self.b("**Quản trị viên (Administrator):** Là người có quyền quản trị cao nhất trên máy tính và nắm mật khẩu quản trị UsbGuard. Quản trị viên có toàn quyền cài đặt, tạm dừng, cấu hình whitelist, đổi mật khẩu và gỡ cài đặt hệ thống.")
        self.b("**Hệ điều hành Windows (Windows OS / SCM):** Là môi trường nền tảng thực thi dịch vụ, phát sinh sự kiện cắm rút phần cứng qua WMI, quản lý phân quyền và kích hoạt cơ chế tự phục hồi dịch vụ sau sự cố.")
        
        self.fig("hinh3_so_do_ca_su_dung.png", "Hình 3.1: Sơ đồ ca sử dụng của hệ thống UsbGuard 1.2", width_cm=13.5)

        self.h2("3.3. Thiết kế kiến trúc 3 tầng chặn và lớp gỡ thiết bị (Defense in Depth)")
        self.p("Nguyên lý phòng thủ đa tầng (Defense in Depth) được áp dụng trong UsbGuard nhằm đảm bảo không có khe hở nào cho phép thiết bị USB trái phép hoạt động. Kiến trúc gồm 3 tầng chặn ở mức hệ điều hành (do `Enforcer.cs` đặt) và 1 lớp gỡ thiết bị chủ động (do `UsbDisks.cs` thực hiện):")
        self.b("**Tầng 1 — Tắt driver lưu trữ:** Đặt `Start = 4` cho 2 driver `USBSTOR` và `UASPStor`. Windows từ chối nạp driver, nên ổ USB cắm vào không thể thành ổ đĩa.")
        self.b("**Tầng 2 — Chính sách Removable Storage Deny_All:** Đặt `RemovableStorageDevices\\Deny_All = 1` cùng các cờ `Deny_Read`, `Deny_Write`, `Deny_Execute` trên lớp đĩa, cấm đọc, ghi và chạy tệp trên mọi ổ lưu trữ di động.")
        self.b("**Tầng 3 — Cấm cài đặt thiết bị lưu trữ USB:** Chính sách Device Installation Restrictions với `DenyDeviceIDs`, từ chối cài đặt mọi thiết bị thuộc lớp USB Mass Storage (Class 08). Thiết kế chi tiết ở mục 3.4.")
        self.b("**Lớp gỡ thiết bị (`UsbDisks.cs`):** Tuyến dự phòng chủ động cho thiết bị đã được nạp sẵn (cắm trước khi dịch vụ chạy, hoặc đang ở chế độ danh sách cho phép). Lớp này quét ổ đĩa qua SetupAPI, xác định bus qua IOCTL, gỡ bằng `CM_Request_Device_Eject`, buộc tháo ổ khi đang mở tệp và nạp lại thiết bị khi bỏ chặn.")
        self.p("Cả 3 tầng đều là cơ chế chuẩn mà doanh nghiệp vẫn đặt qua Group Policy hoặc Intune, nên không gây xung đột với công cụ quản trị sẵn có. Dịch vụ gọi lại `Enforcer.Block()` mỗi chu kỳ nên nếu ai đó đổi tay giá trị Registry thì dịch vụ tự sửa lại.")

        self.fig("hinh1_kien_truc_3_tang.png", "Hình 3.2: Kiến trúc 3 tầng chặn và lớp gỡ thiết bị của UsbGuard", width_cm=12.5)

        self.h2("3.4. Thiết kế tầng chặn thứ 3: cấm cài đặt thiết bị lưu trữ USB")
        self.p("Tầng 1 và tầng 2 chặn ở khâu nạp driver và truy cập dữ liệu, nhưng Windows vẫn có thể cài nút thiết bị cho ổ USB mới. Tầng 3 chặn sớm hơn, ngay ở khâu cài đặt thiết bị, bằng chính sách Windows \"Device Installation Restrictions\":")
        self.p("Cấu hình do UsbGuard ghi vào Registry:")
        self.code("""HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeviceInstall\\Restrictions
    DenyDeviceIDs = 1                                    (DWORD, bật chính sách)
    DenyDeviceIDs\\                                      (khoá con: danh sách mã bị cấm)
        UsbGuard1 = USB\\Class_08&SubClass_06&Prot_50      (BOT)
        UsbGuard2 = USB\\Class_08&SubClass_06&Prot_62      (UAS)
        UsbGuard3 = USB\\Class_08                          (mọi thiết bị lớp lưu trữ)""", 20, True)
        self.b("**Không đụng chuột, bàn phím:** Chỉ lớp Mass Storage (Class 08) bị cấm. Chuột và bàn phím thuộc lớp HID (Class 03) nên vẫn cài và hoạt động bình thường.")
        self.b("**Không đè chính sách của công ty:** UsbGuard chỉ ghi các giá trị mang tên riêng `UsbGuardN`. Khi bỏ chặn hoặc gỡ cài đặt, chương trình chỉ xóa các giá trị này và chỉ gỡ cờ `DenyDeviceIDs` khi danh sách không còn mục nào của người khác.")
        self.b("**Hệ quả cần xử lý:** USB cắm lần đầu lúc đang chặn bị Windows đánh dấu \"cài thất bại\"; khi bỏ chặn cần nạp lại thiết bị (mục 3.5).")

        self.h2("3.5. Thiết kế lớp gỡ nâng cao: thông báo, buộc tháo ổ và nạp lại thiết bị")
        self.p("Khi kiểm thử cắm USB thật, lớp gỡ được bổ sung 3 cơ chế để xử lý các tình huống mà môi trường Windows Server không tái hiện được:")
        self.b("**Báo người dùng cả khi USB bị chặn từ driver:** Khi tầng 1 chặn, thiết bị không bao giờ thành ổ đĩa nên cách quét ổ đĩa không thấy gì. Hàm `UsbDisks.PresentUsbStorage` duyệt mọi thiết bị USB có Compatible ID `USB\\Class_08`, đọc mã lỗi thiết bị (ví dụ mã 32 nghĩa là driver bị tắt), ghi nhật ký và hiện hộp thoại báo 1 lần mỗi lần cắm.")
        self.b("**Buộc tháo ổ khi đang mở tệp (`UsbDisks.ForceDismount`):** Nếu có tệp đang mở trên USB, Windows từ chối lệnh eject. Chương trình tìm các phân vùng thuộc ổ đó bằng `IOCTL_STORAGE_GET_DEVICE_NUMBER` và `IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS`, gọi `FSCTL_LOCK_VOLUME` rồi `FSCTL_DISMOUNT_VOLUME`, sau đó eject lại và giữ khoá cho tới khi USB được gỡ hoặc rút ra.")
        self.b("**Nạp lại USB khi bỏ chặn (`RetryBlockedDevices`, `Kick`, `ReenableDisabled`):** Thiết bị bị tầng 3 cấm cài mang cờ \"cài thất bại\", nên khi tạm dừng, thêm vào danh sách cho phép hoặc gỡ cài đặt, chương trình xóa nút thiết bị bằng `pnputil /remove-device` và quét lại bằng `/scan-devices` để Windows cài lại như USB mới. Thiết bị chỉ bị tắt driver thì dùng `/restart-device`.")

        self.h2("3.6. Sơ đồ thành phần hệ thống và tổ chức mã nguồn")
        self.p("Hệ thống được thiết kế theo mô hình mô-đun hóa cao, phân định trách nhiệm rõ ràng giữa các tệp mã nguồn C# (.NET Framework 4.8):")
        self.b("**Khối điều khiển, giao diện & Quản trị:** `Program.cs` (điểm khởi nhập), `Cli.cs` (bộ phân tích lệnh quản trị), `Gui.cs` (giao diện quản lý WinForms), `Installer.cs` (cài đặt và cấu hình SCM), `Password.cs` (nhập mật khẩu ẩn an toàn).")
        self.b("**Khối dịch vụ & Thực thi:** `Worker.cs` (lớp dịch vụ nền tảng, điều phối sự kiện), `Enforcer.cs` (đặt 3 tầng chặn), `UsbDisks.cs` (quét, gỡ và nạp lại thiết bị), `UsbPorts.cs` (đọc và nạp lại cổng USB qua driver hub), `Whitelist.cs` (thuật toán so khớp ID).")
        self.b("**Khối bảo mật & Lưu trữ:** `Auth.cs` (băm PBKDF2-SHA256), `AdminAuth.cs` (kiểm tra mật khẩu và khoá chống dò), `Settings.cs` (đọc ghi HKLM\\SOFTWARE\\UsbGuard), `Reg.cs` (phân quyền DACL).")
        self.b("**Khối hạ tầng tầng thấp:** `Native.cs` (khai báo P/Invoke Win32 API), `Sys.cs` (thực thi tiến trình phụ trợ), `Log.cs` (nhật ký hệ thống), `Constants.cs` (hằng số).")

        self.fig("hinh2_so_do_thanh_phan.png", "Hình 3.3: Sơ đồ thành phần hệ thống và các tệp mã nguồn", width_cm=13.0)

        self.h2("3.7. Thiết kế luồng xử lý vòng kiểm tra dịch vụ (Worker.Tick)")
        self.p("Trái tim của dịch vụ là phương thức `Worker.Tick`. Mỗi khi được kích hoạt (bởi sự kiện WMI tức thì hoặc bởi Timer định kỳ 2 giây), luồng xử lý thực hiện tuần tự các bước:")
        self.b("Bước 1: Sử dụng khóa luồng `lock (_gate)` để ngăn chặn việc chạy lồng nhau nếu vòng kiểm tra trước chưa kết thúc.")
        self.b("Bước 2: Kiểm tra cờ `Settings.Uninstalling`. Nếu cờ bật, dịch vụ dừng Timer và chủ động gọi `Stop()` để kết thúc an toàn.")
        self.b("Bước 3: Kiểm tra trạng thái tạm dừng `Settings.IsPaused`. Nếu đang tạm dừng, thả khoá các ổ đã buộc tháo, mở driver (`Enforcer.Unblock()`), bật lại các thiết bị bị tắt và nạp lại thiết bị đã bị chặn.")
        self.b("Bước 4: Đọc danh sách Whitelist. Nếu rỗng, đặt chế độ CHẶN TẤT CẢ và gọi `Enforcer.Block()` (đủ 3 tầng). Nếu có mục, đặt chế độ DANH SÁCH CHO PHÉP và gọi `Enforcer.Unblock()` để thiết bị hợp lệ chạy được.")
        self.b("Bước 5: Gọi `UsbDisks.Scan()` lấy danh sách ổ đĩa USB đang kết nối. Ổ nào không khớp Whitelist thì gỡ bằng `UsbDisks.Eject(disk)` (có buộc tháo ổ khi cần), hiện cảnh báo `WTSSendMessage` và ghi nhật ký.")
        self.b("Bước 6: Duyệt `UsbDisks.PresentUsbStorage()` để báo người dùng về thiết bị bị chặn ngay từ driver, và nạp lại 1 lần USB được phép nhưng đang ở trạng thái lỗi.")
        self.b("Bước 7 (bản 1.2): Gọi `ReviveEjected` để ghi nhớ cổng USB và \"rút ra cắm lại bằng phần mềm\" USB được phép đã bị tháo (mục 3.14).")

        self.fig("hinh4_luong_vong_kiem_tra.png", "Hình 3.4: Lưu đồ thực thi chi tiết của vòng kiểm tra Worker.Tick", width_cm=12.0)

        self.h2("3.8. Thiết kế chuyển đổi trạng thái 3 chế độ hoạt động")
        self.p("UsbGuard vận hành linh hoạt dựa trên máy trạng thái hữu hạn với 3 chế độ hoạt động rõ ràng:")
        self.b("**Chế độ 1 — CHẶN TẤT CẢ (Block All):** Là trạng thái mặc định khi danh sách Whitelist rỗng. Đủ 3 tầng chặn bật: driver `USBSTOR`/`UASPStor` tắt (`Start = 4`), chính sách `Deny_All = 1` và cấm cài thiết bị lớp 08. Mọi ổ USB cắm vào đều không dùng được.")
        self.b("**Chế độ 2 — DANH SÁCH CHO PHÉP (Allow List):** Tự động kích hoạt khi danh sách Whitelist có ít nhất 1 mục. Driver lưu trữ được mở lại (`Start = 3`), gỡ `Deny_All` và các mục của tầng 3 để hệ thống nhận diện thiết bị. Lớp gỡ giám sát và gỡ ngay bất kỳ ổ USB nào không có ID khớp với Whitelist.")
        self.b("**Chế độ 3 — TẠM DỪNG (Paused):** Được kích hoạt khi quản trị viên tạm dừng (lệnh `pause <số_phút>` hoặc nút \"Tạm dừng chặn\") với đúng mật khẩu. Hệ thống mở lại toàn bộ driver, nạp lại thiết bị đang bị chặn và tạm dừng cơ chế quét gỡ. Hết thời gian, hệ thống tự quay về trạng thái chặn.")

        self.fig("hinh5_trang_thai_3_che_do.png", "Hình 3.5: Sơ đồ chuyển đổi giữa 3 chế độ hoạt động của UsbGuard", width_cm=13.0)

        self.h2("3.9. Thiết kế cây thiết bị và ranh giới cô lập an toàn")
        self.p("Vấn đề khó khăn của các phần mềm chặn USB là nguy cơ ngắt nhầm chuột hoặc bàn phím cắm chung cổng hub USB. Để giải quyết vấn đề này, UsbGuard thiết lập 1 ranh giới cô lập phần cứng chuẩn xác:")
        self.b("Lớp gỡ chỉ nhắm vào giao diện đĩa `GUID_DEVINTERFACE_DISK` và kiểm tra `BusType == BusTypeUsb` (giá trị 7). Chuột, bàn phím thuộc giao diện `GUID_DEVINTERFACE_HID` nên bị bỏ qua ngay từ vòng lọc đầu tiên. Tầng 3 cũng chỉ nhắm lớp 08 nên không ảnh hưởng thiết bị HID.")
        self.b("Khi duyệt cây thiết bị để tìm ID và gỡ bỏ, hằng số `MaxDepth = 2` giới hạn việc duyệt chỉ đi từ Nút đĩa (Disk Node) lên Nút thiết bị USB cha (Parent USB Node). Ứng dụng **không duyệt tiếp lên Nút Hub (USB Generic Hub hoặc Root Hub)**, nên cổng hub vật lý vẫn duy trì tín hiệu cho chuột, bàn phím.")

        self.fig("hinh7_cay_thiet_bi_usb.png", "Hình 3.6: Cây thiết bị PnP và ranh giới gỡ bỏ an toàn tránh ảnh hưởng hub", width_cm=13.0)

        self.h2("3.10. Thiết kế cấu trúc lưu trữ cấu hình trong Windows Registry")
        self.p("Toàn bộ trạng thái và cấu hình vận hành của UsbGuard được lưu trữ tập trung tại phân nhánh Registry hệ thống `HKLM\\SOFTWARE\\UsbGuard`:")

        headers_reg = ["Tên giá trị (Value)", "Kiểu dữ liệu", "Mục đích sử dụng", "Ví dụ giá trị thực tế"]
        widths_reg = [2000, 1800, 3600, 3671]
        rows_reg = [
            ["AuthHash", "REG_SZ", "Chuỗi băm mật khẩu quản trị chuẩn PBKDF2-SHA256.", "pbkdf2-sha256$600000$rQ...==$Ab...=="],
            ["Uninstalling", "REG_QWORD", "Cờ báo hiệu dịch vụ cần tự dừng để phục vụ gỡ cài đặt.", "0L (bình thường), 1L (đang gỡ)"],
            ["PauseUntil", "REG_QWORD", "Thời điểm hết hạn tạm dừng tính theo Ticks UTC.", "638989536000000000L"],
            ["Whitelist", "REG_MULTI_SZ", "Danh sách các chuỗi định danh USB được phép sử dụng.", "VID_0951&PID_1666\\0 08606E6B..."],
            ["DisabledDevices", "REG_MULTI_SZ", "Danh sách thiết bị tạm bị vô hiệu hóa bởi pnputil.", "USB\\VID_0951&PID_1666\\0860..."],
            ["SeenUsb", "REG_MULTI_SZ", "Vị trí cổng (hub và số cổng) của các USB lưu trữ từng thấy, dùng để nạp lại USB đã bị tháo.", "USB\\VID_0951&PID_1666\\0860...|<hub>|3|..."],
            ["AuthFails, AuthLockUntil", "REG_QWORD", "Số lần nhập sai mật khẩu liên tiếp và thời điểm hết khoá (Ticks UTC).", "5L, 638989536300000000L"]
        ]
        self.tbl("TBL_REG", "Bảng 3.2: Đặc tả cấu trúc lưu trữ cấu hình HKLM\\SOFTWARE\\UsbGuard", headers_reg, rows_reg, widths_reg, ["center", "center", "left", "left"])

        self.h2("3.11. Thiết kế cơ chế 'không tắt được' và tự phục hồi dịch vụ")
        self.p("Để đáp ứng yêu cầu 'chạy như dịch vụ không tắt được' theo đúng chuẩn mực bảo mật doanh nghiệp, UsbGuard kết hợp 3 lớp cơ chế kỹ thuật đồng bộ:")
        self.b("**Lớp từ chối SCM (`CanStop = false`):** Lớp dịch vụ `Worker` khai báo `CanStop = false`, `CanPauseAndContinue = false`, `CanShutdown = false`. Khi quản trị viên mở `services.msc` hoặc chạy `sc.exe stop UsbGuard`, SCM kiểm tra thuộc tính này và từ chối, trả về mã lỗi `1052 (ERROR_INVALID_SERVICE_CONTROL)`.")
        self.b("**Lớp phân quyền truy cập DACL:** Người dùng thông thường không có quyền gửi mã điều khiển tới SCM hoặc chỉnh sửa cấu hình dịch vụ. Mọi lệnh `sc stop`, `sc delete`, `sc config` từ người dùng thường đều bị chặn với mã lỗi `5 (ERROR_ACCESS_DENIED)`.")
        self.b("**Lớp phục hồi tự động sau sự cố (`sc.exe failure`):** Nếu tiến trình `UsbGuard.exe` bị cưỡng chế kết thúc (`taskkill /F` từ quyền Administrator), cấu hình phục hồi ra lệnh cho Windows chạy lại tiến trình sau khoảng 5 giây (`actions= restart/5000/restart/30000`).")

        self.fig("hinh8_co_che_khong_tat_duoc.png", "Hình 3.7: Cơ chế 'không tắt được' và tự phục hồi dịch vụ của UsbGuard", width_cm=13.0)

        self.h2("3.12. Thiết kế bảo mật thông tin và phân quyền Registry DACL")
        self.p("Hệ thống áp dụng các tiêu chuẩn an ninh thông tin nghiêm ngặt để bảo vệ toàn vẹn dữ liệu cấu hình:")
        self.b("Khóa Registry `HKLM\\SOFTWARE\\UsbGuard` được ngắt kế thừa quyền (`SetAccessRuleProtection(true, false)`) và chỉ cấp `FullControl` cho 2 SID: `LocalSystem` và `BuiltinAdministrators`. Nhóm người dùng thường không có quyền đọc, ngăn việc sao chép chuỗi mã băm `AuthHash` để bẻ khóa ngoại tuyến.")
        self.b("Cơ chế nhập mật khẩu an toàn (`Password.cs`): đọc phím với thuộc tính ẩn `Console.ReadKey(true)`, không hiển thị ký tự và không ghi vết vào lịch sử dòng lệnh. Giao diện quản lý hỏi mật khẩu cho mọi thao tác.")
        self.b("**Băm mật khẩu (bản 1.2):** PBKDF2-HMAC-SHA256, muối ngẫu nhiên 16 byte, 600000 vòng (trước đây là SHA1, 100000 vòng). Mã băm của bản cũ vẫn dùng được và được băm lại ở lần nhập đúng kế tiếp (`Auth.NeedsRehash`).")
        self.b("**Chống dò mật khẩu (`AdminAuth.cs`):** Số lần sai lưu trong Registry HKLM (người dùng thường không sửa được) nên đóng mở lại phần mềm không xóa được. Sai 4 lần đầu chưa khoá; lần thứ 5 khoá 30 giây, mỗi lần sai tiếp gấp đôi, tối đa 1 giờ; nhập đúng thì về 0. Giao diện, dòng lệnh và trình gỡ dùng chung 1 hàm kiểm tra.")

        self.fig("hinh9_mo_hinh_bao_mat_pbkdf2.png", "Hình 3.8: Thiết kế bảo mật mật khẩu PBKDF2 và phân quyền DACL", width_cm=13.0)

        self.h2("3.13. Thiết kế quy trình gỡ cài đặt an toàn có xác thực mật khẩu")
        self.p("Vì dịch vụ không nhận lệnh Stop trực tiếp, quy trình gỡ cài đặt được thiết kế thông qua cơ chế cờ báo hiệu an toàn:")
        self.b("Người dùng chạy `UsbGuard.exe uninstall <mật_khẩu>` (hoặc nút \"Gỡ cài đặt\", hoặc trình gỡ của bộ cài). Chương trình kiểm tra quyền Administrator và xác thực mật khẩu qua PBKDF2.")
        self.b("Nếu xác thực thành công, chương trình ghi cờ `Uninstalling = 1` vào Registry. Dịch vụ `Worker` trong vòng kiểm tra tiếp theo đọc cờ này sẽ chủ động dừng Timer và gọi `Stop()`.")
        self.b("Tiến trình gỡ chờ dịch vụ dừng hẳn (tối đa 20 giây), xóa dịch vụ khỏi SCM (`sc delete`), trả lại cấu hình Windows (`USBSTOR Start = 3`, xóa `Deny_All`, xóa các mục `UsbGuardN` của tầng 3 và giữ nguyên mục của công ty), bật lại và nạp lại thiết bị bị chặn, xóa khóa `HKLM\\SOFTWARE\\UsbGuard` và các tệp cài đặt.")

        self.fig("hinh6_luong_go_cai_dat.png", "Hình 3.9: Quy trình gỡ cài đặt bảo mật và khôi phục cài đặt gốc Windows", width_cm=12.5)

        self.h2("3.14. Thiết kế nạp lại USB đã bị Windows tháo (bản 1.2)")
        self.p("Lượt thử trên máy Windows thật (mục 5.6) cho thấy 2 vấn đề: (a) USB bị chặn lúc đang cắm thì Windows \"tháo an toàn\" (mã 47), nên khi được cho phép hoặc tạm dừng phải rút ra cắm lại mới dùng được; (b) USB đó có lúc biến khỏi danh sách trong phần mềm. Bản 1.2 xử lý bằng `UsbPorts.cs` và `Worker.ReviveEjected`:")
        self.b("**Ghi nhớ vị trí cổng:** Dịch vụ lưu vào Registry (`SeenUsb`) Instance ID, hub và số cổng của mỗi USB lưu trữ đang cắm, nên vẫn nhận ra USB dù Windows không còn liệt kê nó (lỗi b).")
        self.b("**Đọc trạng thái cổng từ driver hub:** Gửi `IOCTL_USB_GET_NODE_CONNECTION_INFORMATION` tới hub để biết cổng còn cắm đúng USB (VID, PID) không. Hết cắm thì quên; vẫn cắm nhưng đã bị tháo thì hiện lại với trạng thái \"Bị chặn (đã tháo)\".")
        self.b("**Rút ra cắm lại bằng phần mềm:** Khi USB được phép dùng (đang tạm dừng hoặc có trong danh sách cho phép) mà đã bị tháo, gửi `IOCTL_USB_HUB_CYCLE_PORT` tới đúng cổng đó. Windows nhận lại USB như vừa cắm vào, không ảnh hưởng thiết bị khác. Thử tối đa 3 lần, mỗi lần cách nhau 10 giây (khắc phục lỗi a).")
        self.b("**Không dùng `pnputil /restart-device` cho USB mã 47:** lệnh này làm USB chuyển sang mã 14 (đòi khởi động lại máy).")

    # ==========================================================================
    # CHƯƠNG 4: CÀI ĐẶT VÀ TRIỂN KHAI ỨNG DỤNG
    # ==========================================================================
    VAI_TRO_TEP = {
        "Program.cs": "Điểm khởi nhập (Main), phân luồng các lệnh CLI và giao diện.",
        "Worker.cs": "Lớp ServiceBase, vòng lặp 2s, giám sát WMI, điều phối 3 chế độ, thông báo, nạp lại USB đã bị tháo.",
        "Enforcer.cs": "Đặt và gỡ 3 tầng chặn: driver USBSTOR/UASPStor, Deny_All, DenyDeviceIDs.",
        "UsbDisks.cs": "Lớp gỡ: quét SetupAPI/IOCTL, eject, buộc tháo ổ, nạp lại thiết bị.",
        "Gui.cs": "Giao diện quản lý WinForms: thanh trạng thái, 3 tab, hộp thoại mật khẩu.",
        "Installer.cs": "Cài đặt/gỡ dịch vụ qua sc.exe, cấu hình phục hồi, xác thực khi gỡ.",
        "Settings.cs": "Đọc/ghi cấu hình Registry tại HKLM\\SOFTWARE\\UsbGuard.",
        "Cli.cs": "Xử lý các lệnh quản trị: pause, resume, whitelist, passwd, devices.",
        "Native.cs": "Khai báo P/Invoke các hàm Win32 API tầng thấp.",
        "Auth.cs": "Băm mật khẩu PBKDF2-SHA256 600000 vòng, nâng cấp mã băm cũ, tính thời gian khoá.",
        "Log.cs": "Ghi nhật ký ra tệp usbguard.log và Windows Event Log.",
        "Reg.cs": "Tiện ích Registry an toàn và phân quyền DACL.",
        "Whitelist.cs": "So khớp chuỗi ID thiết bị với danh sách cho phép.",
        "Password.cs": "Đọc mật khẩu ẩn không hiện ký tự từ bàn phím console.",
        "Sys.cs": "Khởi chạy tiến trình hệ thống (sc.exe, pnputil.exe).",
        "Constants.cs": "Hằng số tên dịch vụ, tên hiển thị và mô tả hệ thống.",
        "UsbPorts.cs": "Đọc trạng thái cổng USB từ driver hub và rút ra cắm lại bằng phần mềm (IOCTL).",
        "AdminAuth.cs": "Kiểm tra mật khẩu quản trị dùng chung, đếm số lần sai trong HKLM và khoá tăng dần.",
    }

    def tao_chuong_4(self):
        self.h1("CHƯƠNG 4: CÀI ĐẶT VÀ TRIỂN KHAI ỨNG DỤNG")

        self.h2("4.1. Môi trường phát triển và công nghệ sử dụng")
        self.p("Dự án UsbGuard được xây dựng trên môi trường công nghệ chuẩn mực, hướng đến tính gọn nhẹ và sự ổn định tối đa:")
        self.b("**Ngôn ngữ lập trình:** C# 9.0 (LangVersion 9.0 trong UsbGuard.csproj).")
        self.b("**Nền tảng mục tiêu:** .NET Framework 4.8, đã tích hợp sẵn trên Windows 10, Windows 11 và Windows Server hiện đại, nên ứng dụng chạy ngay mà không cần cài thêm thư viện phụ thuộc.")
        self.b("**Giao diện và bộ cài:** Giao diện quản lý bằng WinForms; bộ cài `setup.exe` đóng gói bằng Inno Setup 6 (`installer/UsbGuard.iss`).")
        self.b("**Công cụ biên dịch:** .NET SDK (gói tham chiếu `Microsoft.NETFramework.ReferenceAssemblies` cho phép biên dịch chéo đa nền tảng).")
        self.b("**Tích hợp liên tục (CI):** GitHub Actions chạy trên máy ảo Windows Server 2022, Windows Server 2025 và trên máy ảo QEMU chứa Windows 10, Windows 11 (kiểm thử cắm USB thật).")

        self.h2("4.2. Cấu trúc mã nguồn chi tiết")
        nguon = sorted(kq.ma_nguon(), key=lambda t: -t[1])
        tong_dong = sum(n for _, n in nguon)
        self.p(f"Mã nguồn ứng dụng được tổ chức trong thư mục `src/`, gồm {len(nguon)} tệp mã nguồn C# với tổng cộng {tong_dong} dòng (số liệu đếm trực tiếp từ thư mục `src/` khi sinh báo cáo):")

        headers_src = ["STT", "Tên tệp nguồn", "Số dòng", "Vai trò và chức năng chính"]
        widths_src = [800, 2300, 1100, 6871]
        rows_src = []
        for i, (ten, n) in enumerate(nguon, 1):
            if ten not in self.VAI_TRO_TEP:
                raise SystemExit(f"[LỖI] Tệp nguồn {ten} chưa có mô tả vai trò trong VAI_TRO_TEP")
            rows_src.append([str(i), ten, str(n), self.VAI_TRO_TEP[ten]])
        self.tbl("TBL_SRC", "Bảng 4.1: Cấu trúc tệp mã nguồn và số dòng lệnh của UsbGuard", headers_src, rows_src, widths_src, ["center", "left", "center", "left"], sz=21)

        self.h2("4.3. Phân tích các trích đoạn mã nguồn quan trọng")
        self.p("Dưới đây là các trích đoạn mã nguồn tiêu biểu (đã rút gọn) thể hiện giải pháp kỹ thuật cốt lõi của UsbGuard 1.2:")

        self.h3("4.3.1. Điều phối vòng lặp và xử lý chế độ (Worker.Tick)")
        self.p("Đoạn mã thể hiện việc kiểm tra cờ dừng, xác định 3 chế độ, quét gỡ thiết bị vi phạm và báo thiết bị bị chặn từ driver:")
        self.code("""// Trích rút gọn từ src/Worker.cs
private void Tick(object sender, ElapsedEventArgs e)
{
    lock (_gate) { if (_busy) return; _busy = true; }
    try
    {
        if (!Settings.Exists()) return;
        if (Settings.Uninstalling) { if (!_interactive) { _timer.Stop(); Stop(); } return; }
        if (Settings.IsPaused)
        {
            UsbDisks.ReleaseLocksExcept(null);
            SetMode("TẠM DỪNG"); Enforcer.Unblock(); AfterUnblock();
            ReviveEjected(UsbDisks.PresentUsbStorage(), d => true); return;
        }
        var whitelist = Settings.GetWhitelist();
        if (whitelist.Count == 0) { SetMode("CHẶN TẤT CẢ"); Enforcer.Block(); }
        else { SetMode("DANH SÁCH CHO PHÉP"); Enforcer.Unblock(); AfterUnblock(); }

        foreach (var disk in UsbDisks.Scan())          // lớp gỡ
            if (!Whitelist.Matches(disk.Ids, whitelist)) { UsbDisks.Eject(disk); Notify(disk.Name); }

        foreach (var dev in UsbDisks.PresentUsbStorage())   // bị chặn từ driver
            if (dev.Problem != 0 && !Whitelist.Matches(dev.Ids, whitelist)) Notify(dev.Name);
        ReviveEjected(UsbDisks.PresentUsbStorage(), d => Whitelist.Matches(d.Ids, whitelist));
    }
    finally { lock (_gate) { _busy = false; } }
}""")

        self.h3("4.3.2. Chặn bằng 3 tầng ở mức hệ điều hành (Enforcer.Block)")
        self.p("Đoạn mã đặt đồng bộ driver, chính sách Removable Storage (tầng 1, 2) và chính sách cấm cài thiết bị (tầng 3). Tầng 3 chỉ ghi giá trị mang tên riêng `UsbGuardN`:")
        self.code("""// Trích từ src/Enforcer.cs
public static void Block()
{
    using (var hk = Reg.Hklm())
    {
        foreach (var d in Drivers)                       // tầng 1: USBSTOR, UASPStor
            Reg.SetDword(hk, @"SYSTEM\\CurrentControlSet\\Services\\" + d, "Start", 4, true);
        Reg.SetDword(hk, PolicyRoot, "Deny_All", 1, false);        // tầng 2
        var cls = PolicyRoot + "\\\\" + DiskClass;
        Reg.SetDword(hk, cls, "Deny_Read", 1, false);
        Reg.SetDword(hk, cls, "Deny_Write", 1, false);
        Reg.SetDword(hk, cls, "Deny_Execute", 1, false);

        Reg.SetDword(hk, DevInstRoot, "DenyDeviceIDs", 1, false);  // tầng 3
        using (var k = hk.CreateSubKey(DenyListKey))
            for (int i = 0; i < DenyIds.Length; i++)     // USB\\Class_08...
                k.SetValue("UsbGuard" + (i + 1), DenyIds[i], RegistryValueKind.String);
    }
}""")

        self.h3("4.3.3. Truy vấn thuộc tính phần cứng và BusType (UsbDisks.Inspect)")
        self.p("Đoạn mã mở thiết bị và gửi lệnh IOCTL để xác định BusType và lấy danh sách ID:")
        self.code("""// Trích từ src/UsbDisks.cs
private static UsbDisk Inspect(string path, uint devInst)
{
    using (var h = Native.CreateFile(path, 0, 3, IntPtr.Zero, 3, 0, IntPtr.Zero))
    {
        if (h.IsInvalid) return null;
        IntPtr q = Marshal.AllocHGlobal(12), o = Marshal.AllocHGlobal(1024);
        try
        {
            uint ret;
            if (!Native.DeviceIoControl(h, IOCTL_STORAGE_QUERY_PROPERTY, q, 12, o, 1024, out ret, IntPtr.Zero) || ret < 32)
                return null;
            var d = new UsbDisk { DevInst = devInst, BusType = Marshal.ReadInt32(o, 28) };
            uint node = devInst;
            for (int depth = 0; depth < MaxDepth && node != 0; depth++)
            {
                var sb = new StringBuilder(260);
                if (Native.CM_Get_Device_ID(node, sb, sb.Capacity, 0) == 0) d.Ids.Add(sb.ToString());
                uint parent; if (Native.CM_Get_Parent(out parent, node, 0) != 0) break;
                node = parent;
            }
            return d;
        }
        finally { Marshal.FreeHGlobal(q); Marshal.FreeHGlobal(o); }
    }
}""")

        self.h3("4.3.4. Buộc tháo ổ khi đang mở tệp (UsbDisks.ForceDismount)")
        self.p("Khi Windows từ chối eject vì có tệp đang mở, đoạn mã khoá và tháo (dismount) mọi phân vùng thuộc ổ USB đó, rồi giữ khoá để không ai đọc ghi được nữa:")
        self.code("""// Trích rút gọn từ src/UsbDisks.cs
private static int ForceDismount(UsbDisk d)
{
    if (IsLocked(d.Key)) return 0;
    int diskNo = DiskNumber(d.Path);       // IOCTL_STORAGE_GET_DEVICE_NUMBER
    if (diskNo < 0) return 0;
    int count = 0;
    IntPtr fh = Native.FindFirstVolume(vn, vn.Capacity);
    do
    {
        var h = Native.CreateFile(vol, 0xC0000000, 3, IntPtr.Zero, 3, 0, IntPtr.Zero);
        if (h.IsInvalid || !OnDisk(h, diskNo)) { h.Dispose(); continue; }   // VOLUME_DISK_EXTENTS
        bool locked = Native.DeviceIoControl(h, FSCTL_LOCK_VOLUME, ...);
        Native.DeviceIoControl(h, FSCTL_DISMOUNT_VOLUME, ...);   // tệp đang mở mất hiệu lực
        if (!locked) locked = Native.DeviceIoControl(h, FSCTL_LOCK_VOLUME, ...);
        if (locked) { count++; Held[d.Key].Add(h); }   // giữ khoá tới khi gỡ được USB
        else h.Dispose();
    } while (Native.FindNextVolume(fh, vn, vn.Capacity));
    return count;
}""")

        self.h2("4.4. Tập lệnh điều khiển dòng lệnh CLI")
        self.p("Ngoài giao diện đồ họa, ứng dụng có tập lệnh dòng lệnh (CLI) phục vụ quản trị và tự động hóa:")

        headers_cli = ["Cú pháp dòng lệnh", "Quyền yêu cầu", "Chức năng và ý nghĩa thực thi"]
        widths_cli = [3500, 2000, 5571]
        rows_cli = [
            ["UsbGuard.exe gui", "Người dùng / Admin", "Mở giao diện quản lý (tự xin quyền Administrator qua UAC khi cần)."],
            ["UsbGuard.exe install [mật_khẩu]", "Administrator", "Cài đặt dịch vụ vào SCM, đặt mật khẩu quản trị, kích hoạt tự khởi động."],
            ["UsbGuard.exe uninstall [mật_khẩu]", "Administrator", "Xác thực mật khẩu, dừng dịch vụ, xóa khỏi SCM và khôi phục mặc định."],
            ["UsbGuard.exe status", "Người dùng / Admin", "Xem trạng thái dịch vụ, chế độ hoạt động, whitelist và 3 tầng chặn."],
            ["UsbGuard.exe pause <phút> [mật_khẩu]", "Administrator", "Tạm dừng chế độ chặn trong N phút (1 - 1440 phút)."],
            ["UsbGuard.exe resume [mật_khẩu]", "Administrator", "Kích hoạt lại chế độ chặn ngay lập tức."],
            ["UsbGuard.exe devices [--all]", "Người dùng / Admin", "Liệt kê ổ USB đang cắm (kể cả đang bị chặn) kèm số serial để thêm whitelist."],
            ["UsbGuard.exe whitelist list", "Administrator", "Xem danh sách các ID thiết bị đang được phép hoạt động."],
            ["UsbGuard.exe whitelist add <ID> [mật_khẩu]", "Administrator", "Thêm ID hoặc số serial vào danh sách cho phép (chuyển sang Chế độ 2)."],
            ["UsbGuard.exe whitelist remove <ID> [mật_khẩu]", "Administrator", "Xóa khỏi whitelist (nếu rỗng quay về Chế độ 1)."],
            ["UsbGuard.exe passwd [cũ] [mới]", "Administrator", "Thay đổi mật khẩu quản trị hệ thống."],
            ["UsbGuard.exe --console", "Người dùng / Admin", "Chạy thử trực tiếp trên console (không qua SCM) để chẩn đoán."]
        ]
        self.tbl("TBL_CLI", "Bảng 4.2: Danh mục tập lệnh điều khiển dòng lệnh của UsbGuard", headers_cli, rows_cli, widths_cli, ["left", "center", "left"], sz=21)

        self.h2("4.5. Giao diện quản lý")
        self.p("Để người dùng không rành dòng lệnh vẫn quản trị được, UsbGuard 1.2 có giao diện quản lý WinForms (`src/Gui.cs`), mở bằng lối tắt trên Start Menu hoặc Desktop. Giao diện tự xin quyền Administrator (UAC), cập nhật trạng thái mỗi 2 giây và dùng chung mã Enforcer, Settings, UsbDisks với dịch vụ.")
        self.fig(kq.anh_gui(), "Hình 4.1: Giao diện quản lý UsbGuard 1.2 ở chế độ danh sách cho phép", width_cm=11.0)
        headers_gui = ["Thành phần", "Chức năng"]
        widths_gui = [2800, 6271]
        rows_gui = [
            ["Thanh trạng thái màu", "Đỏ: chặn tất cả; xanh: chỉ cho phép danh sách; vàng: tạm dừng (kèm dòng \"Muốn chặn ngay: bấm Bật lại chặn\"); xám: chưa cài đặt. Kèm dòng báo dịch vụ không tắt được."],
            ["Tab \"USB đang cắm\"", "Liệt kê USB đang cắm (kể cả đang bị chặn) theo số serial, kèm trạng thái \"Bị chặn (đã tháo)\" nếu Windows đã tháo; chọn 1 USB rồi bấm \"Cho phép USB đã chọn\" mà không cần tạm dừng."],
            ["Tab \"Danh sách cho phép\"", "Xem, thêm theo ID và xóa mục. Danh sách trống nghĩa là chặn tất cả."],
            ["Tab \"Nhật ký\"", "Hiển thị nhật ký hoạt động, có nút mở thư mục chứa tệp nhật ký."],
            ["Hàng nút dưới", "Tạm dừng chặn, Bật lại chặn, Đổi mật khẩu, Gỡ cài đặt (hoặc Cài đặt khi chưa cài)."],
            ["Bảo vệ thao tác", "Mọi thao tác thay đổi đều hỏi mật khẩu quản trị; nhập sai 5 lần liên tiếp thì khoá 30 giây, gấp đôi mỗi lần sai tiếp, tối đa 1 giờ."]
        ]
        self.tbl("TBL_GUI", "Bảng 4.3: Các thành phần của giao diện quản lý", headers_gui, rows_gui, widths_gui, ["left", "left"], sz=21)

        self.h2("4.6. Bộ cài đặt setup.exe")
        self.p("Bộ cài `UsbGuard-Setup-<phiên bản>.exe` được đóng gói bằng Inno Setup 6 (`installer/UsbGuard.iss`), giao diện tiếng Việt, giúp người dùng cài UsbGuard như phần mềm Windows thông thường:")
        self.fig("hinh11_bo_cai_setup.png", "Hình 4.2: Các bước của bộ cài setup.exe và trình gỡ cài đặt", width_cm=12.5)
        headers_set = ["Tính năng", "Mô tả"]
        widths_set = [3000, 6071]
        rows_set = [
            ["Trang điều khoản", "Hiển thị giấy phép sử dụng bằng tiếng Việt trước khi cài."],
            ["Đặt mật khẩu quản trị", "Trang 2 ô nhập, tối thiểu 8 ký tự, phải khớp nhau mới cho đi tiếp."],
            ["Truyền mật khẩu an toàn", "Mật khẩu chuyển cho bước cài qua biến môi trường `USBGUARD_ADMIN_PW`, không xuất hiện trên dòng lệnh."],
            ["Lối tắt và mục gỡ", "Tạo lối tắt Start Menu, Desktop và mục UsbGuard trong Settings > Apps."],
            ["Trình gỡ có mật khẩu", "Khi gỡ, bắt buộc nhập đúng mật khẩu quản trị; sai thì không gỡ."],
            ["Cài và gỡ im lặng", "Dành cho IT: `/VERYSILENT /ADMINPW=...` để triển khai hàng loạt."]
        ]
        self.tbl("TBL_SET", "Bảng 4.4: Các tính năng của bộ cài setup.exe", headers_set, rows_set, widths_set, ["left", "left"], sz=21)

        self.h2("4.7. Hướng dẫn vận hành dành cho quản trị viên hệ thống")
        self.p("Quy trình vận hành chuẩn trong thực tế của quản trị viên:")
        self.b("**Bước 1 (Cài đặt):** Chạy `setup.exe`, đồng ý điều khoản, đặt mật khẩu quản trị. Dịch vụ được cài, tự khởi động cùng Windows và vào chế độ CHẶN TẤT CẢ. Có thể cài bằng dòng lệnh: `UsbGuard.exe install <mật_khẩu>`.")
        self.b("**Bước 2 (Cho phép USB hợp lệ):** Cắm USB công vụ vào máy (không cần tạm dừng), mở giao diện quản lý, vào tab \"USB đang cắm\", chọn USB và bấm \"Cho phép USB đã chọn\". Từ lúc này chỉ USB đó dùng được (dòng lệnh: `devices` rồi `whitelist add <serial>`).")
        self.b("**Bước 3 (Kiểm tra nhật ký):** Mở tab \"Nhật ký\" hoặc tệp `C:\\ProgramData\\UsbGuard\\usbguard.log` để theo dõi lịch sử cắm rút.")
        self.b("**Bước 4 (Gỡ cài đặt):** Dùng Settings > Apps hoặc nút \"Gỡ cài đặt\" trong giao diện; nhập đúng mật khẩu quản trị để hoàn trả cấu hình USB mặc định của Windows.")

    # ==========================================================================
    # CHƯƠNG 5: KIỂM THỬ VÀ ĐÁNH GIÁ KẾT QUẢ
    # ==========================================================================
    MO_TA_UNIT = {
        "Hash_RoiVerify_DungMatKhau_PhaiDung": "Băm mật khẩu và xác thực lại với đúng mật khẩu ban đầu.",
        "Verify_SaiMatKhau_PhaiSai": "Xác thực với mật khẩu sai khác phải trả về false.",
        "Verify_ChuoiLuuRong_PhaiSai": "Chuỗi băm rỗng hoặc null phải trả về false, không ném ngoại lệ.",
        "Verify_SaiDinhDang_KhongDuocNem": "Chuỗi băm sai định dạng không được gây crash.",
        "Hash_HaiLanGoiLienTiep_RaMuoiKhacNhau": "2 lần băm cùng 1 mật khẩu phải sinh ra 2 muối khác nhau.",
        "Verify_ThieuIteration_PhaiSai": "Số vòng lặp quá thấp bị từ chối để chống hash giả mạo.",
        "IsValidEntry_ChuoiQuaNgan_KhongHopLe": "Mục whitelist rỗng hoặc quá ngắn không được chấp nhận.",
        "IsValidEntry_DuDaiToiThieu_HopLe": "Mục whitelist đủ độ dài tối thiểu (ví dụ VID_0951) là hợp lệ.",
        "Matches_ThietBiCoIdNamTrongWhitelist_PhaiKhop": "Thiết bị có ID khớp với mục whitelist được phê duyệt.",
        "Matches_KhongPhanBietHoaThuong": "So khớp whitelist không phân biệt chữ hoa, chữ thường.",
        "Matches_WhitelistRong_KhongKhopGi": "Whitelist rỗng thì không khớp với bất kỳ thiết bị nào.",
        "Matches_MucWhitelistQuaNgan_BiBoQua": "Mục whitelist quá ngắn tự động bị bỏ qua trong thuật toán khớp.",
        "Hash_MoiDungSha256_600000Vong": "Mã băm mới dùng PBKDF2-SHA256 với 600000 vòng và xác thực đúng.",
        "Verify_MaBamCuaBan11_VanDung_VaCanBamLai": "Mã băm SHA1 của bản 1.1 vẫn đăng nhập được và được đánh dấu cần băm lại.",
        "LockSeconds_TangGapDoi_ToiDa1Gio": "Thời gian khoá khi nhập sai: 4 lần đầu không khoá, lần 5 khoá 30 giây, gấp đôi mỗi lần, tối đa 1 giờ.",
    }

    def tao_chuong_5(self):
        D = lay_du_lieu()
        t22, t25, w10, w11, u22, u25 = D["t22"], D["t25"], D["w10"], D["w11"], D["u22"], D["u25"]
        self.h1("CHƯƠNG 5: KIỂM THỬ VÀ ĐÁNH GIÁ KẾT QUẢ")

        self.h2("5.1. Chiến lược kiểm thử hệ thống")
        self.p("Để đảm bảo độ tin cậy cao cho 1 ứng dụng can thiệp tầng sâu hệ thống, tác giả xây dựng chiến lược kiểm thử đa tầng gồm 3 cấp độ chạy tự động trên GitHub Actions, bổ sung 1 lượt thử thủ công trên máy Windows thật:")
        self.b(f"**Cấp độ 1 — Unit Test (`tests/AuthTests.cs`):** {u22['tong']} ca kiểm tra các thuật toán nghiệp vụ độc lập (băm PBKDF2, so khớp whitelist) bằng xUnit.")
        self.b(f"**Cấp độ 2 — Kiểm thử tích hợp trên Windows Server (`tests/integration.ps1`):** {t22['tong']} ca chạy trên Windows Server 2022 và Windows Server 2025: cài dịch vụ thật, đo phản ứng Registry, kiểm tra 3 tầng chặn, thử tắt dịch vụ bằng Administrator và người dùng thường, chống dò mật khẩu, gỡ cài đặt.")
        self.b(f"**Cấp độ 3 — Kiểm thử cắm USB thật trên Windows 10 và Windows 11 (`tests/e2e/`):** {w10['tong']} ca cài bằng setup.exe rồi cắm, rút ổ USB và bàn phím USB vào máy ảo Windows 10 Pro và Windows 11 Pro, kiểm tra chặn, danh sách cho phép, tệp đang mở, USB đã bị Windows tháo và gỡ bằng trình gỡ.")
        self.b("**Thử thủ công trên máy thật:** 1 thành viên nhóm cài bản 1.1.0 lên máy Windows thật, dùng USB vật lý thử 7 kịch bản (mục 5.6). Kết quả này sinh ra các cải tiến của bản 1.2.")

        self.h2("5.2. Kết quả kiểm thử Unit Test")
        self.p(f"Bộ kiểm thử đơn vị gồm {u22['tong']} ca, kết quả đọc từ tệp `.trx` do GitHub Actions xuất ra: **{kqs(u22)} ca đạt** trên Windows Server 2022 và **{kqs(u25)} ca đạt** trên Windows Server 2025.")
        headers_ut = ["Mã test", "Tên phương thức kiểm thử", "Mục đích kiểm tra", "Kết quả"]
        widths_ut = [900, 3700, 3971, 1500]
        thu_tu = list(self.MO_TA_UNIT)
        gop = {}
        for t, o in u22["ca"]:
            gop.setdefault(t.split("(")[0], []).append(o)
        u22_ca = [(k, all(v)) for k, v in gop.items()]
        ca_ut = sorted(u22_ca, key=lambda c: (thu_tu.index(c[0].split("(")[0]) if c[0].split("(")[0] in thu_tu else 99, c[0]))
        gop25 = {}
        for t, o in u25["ca"]:
            gop25.setdefault(t.split("(")[0], []).append(o)
        kq25 = {k: all(v) for k, v in gop25.items()}
        rows_ut = []
        for i, (ten, ok) in enumerate(ca_ut, 1):
            ok = ok and kq25.get(ten, False)
            n_ca = len(gop[ten])
            rows_ut.append([f"UT{i:02d}", ten + (f" ({n_ca} ca tham số)" if n_ca > 1 else ""), self.MO_TA_UNIT.get(ten, "Xem mã nguồn trong tests/."), "Đạt" if ok else "Không đạt"])
        self.tbl("TBL_UT", f"Bảng 5.1: Kết quả thực thi {u22['tong']} ca kiểm thử đơn vị (Unit Test) xUnit", headers_ut, rows_ut, widths_ut, ["center", "left", "left", "center"], sz=20)

        self.h2(f"5.3. Kết quả kiểm thử tích hợp tự động trên Windows Server ({t22['tong']} ca)")
        self.p(f"Kịch bản `tests/integration.ps1` kiểm tra tự động vòng đời và các hành vi an ninh của UsbGuard trên Windows Server 2022 và Windows Server 2025 qua GitHub Actions. Kết quả: **{kqs(t22)} ca đạt** trên Windows Server 2022 và **{kqs(t25)} ca đạt** trên Windows Server 2025. Tên ca đọc trực tiếp từ tệp kết quả:")
        headers_it = ["Mã ca", "Tên ca kiểm thử tích hợp", "Windows Server 2022", "Windows Server 2025"]
        widths_it = [900, 5271, 1450, 1450]
        rows_it = []
        for c in t22["ca"]:
            c25 = t25["theo_ma"].get(c["id"])
            rows_it.append([c["id"], c["ten"], kq_chu(c["dat"]), kq_chu(c25["dat"]) if c25 else "Thiếu"])
        self.tbl("TBL_IT", f"Bảng 5.2: Kết quả {t22['tong']} ca kiểm thử tích hợp trên Windows Server", headers_it, rows_it, widths_it, ["center", "left", "center", "center"], sz=20)

        self.fig("hinh10_terminal_log.png", f"Hình 5.1: Nhật ký chạy kiểm thử tích hợp {t22['tong']} ca trên Windows Server", width_cm=11.5)

        self.p("Các thông số đo thời gian phản ứng ghi nhận qua kiểm thử tích hợp trên 2 nền tảng Windows Server:")
        self.b(f"**Thời gian tự sửa Registry (`tu_sua_ms`):** Khi sửa tay `USBSTOR\\Start = 3`, dịch vụ phát hiện và khôi phục `Start = 4` sau **{t22['tu_sua_ms']} ms** (Windows Server 2022) và **{t25['tu_sua_ms']} ms** (Windows Server 2025).")
        self.b(f"**Thời gian tự chạy lại sau khi bị kill (`chay_lai_ms`):** Khi tiến trình `UsbGuard.exe` bị `taskkill /F`, cấu hình phục hồi `sc failure` khiến Windows chạy lại dịch vụ sau **{t22['chay_lai_ms']} ms** (Windows Server 2022) và **{t25['chay_lai_ms']} ms** (Windows Server 2025), khớp với độ trễ phục hồi 5000 ms đã cấu hình.")
        self.b(f"**Tài nguyên hệ thống (RAM/CPU):** Đo khi dịch vụ chạy không tải. Windows Server 2022: RAM trung bình **{t22['ram_tb_mb']} MB** (cao nhất **{t22['ram_max_mb']} MB**), CPU **{t22['cpu_pct']} %**. Windows Server 2025: RAM trung bình **{t25['ram_tb_mb']} MB** (cao nhất **{t25['ram_max_mb']} MB**), CPU **{t25['cpu_pct']} %**.")

        self.h2("5.4. Kiểm thử cắm USB thật trên Windows 10 và Windows 11")
        self.p("Môi trường Windows Server trên CI không có cổng USB, nên các tình huống như cắm ổ USB, đang mở tệp, bàn phím USB chưa được kiểm chứng. Tác giả xây dựng môi trường kiểm thử cắm USB thật chạy trên GitHub Actions:")
        self.b("**Máy ảo:** Runner Ubuntu bật KVM chạy Windows 10 Pro và Windows 11 Pro trong QEMU (dockur/windows).")
        self.b("**Ổ USB:** Ổ QEMU `usb-storage` cắm nóng vào cổng USB 3 (xHCI) bằng lệnh `device_add` và `device_del` của QEMU monitor. Windows nhận đúng như USB flash disk thật: bus USB, driver USBSTOR, có ký tự ổ và ghi được tệp (ca E01). Ca E05 còn cắm thêm bàn phím USB.")
        self.b("**Mã nguồn kiểm thử:** `tests/e2e/e2e-usb.ps1` (chạy trong Windows), `tests/e2e/host.py` (điều khiển cắm rút từ máy chủ) và `.github/workflows/e2e-usb.yml`.")
        self.fig("hinh12_moi_truong_e2e.png", "Hình 5.2: Môi trường kiểm thử cắm USB thật", width_cm=12.0)
        self.p(f"Kết quả: **{kqs(w10)} ca đạt trên {w10['he_dieu_hanh'].replace('Microsoft ', '')}** và **{kqs(w11)} ca đạt trên {w11['he_dieu_hanh'].replace('Microsoft ', '')}**. Bảng 5.3 liệt kê từng ca:")
        headers_e2e = ["Mã ca", "Ca kiểm thử cắm USB thật", "Windows 10", "Windows 11"]
        widths_e2e = [800, 5771, 1250, 1250]
        rows_e2e = []
        for c in w10["ca"]:
            c11 = w11["theo_ma"].get(c["id"])
            rows_e2e.append([c["id"], c["ten"], kq_chu(c["dat"]), kq_chu(c11["dat"]) if c11 else "Thiếu"])
        self.tbl("TBL_E2E", f"Bảng 5.3: Kết quả {w10['tong']} ca cắm USB thật trên Windows 10 và 11", headers_e2e, rows_e2e, widths_e2e, ["center", "left", "center", "center"], sz=20)

        self.p("Các số đo và quan sát rút ra từ nhật ký kiểm thử:")
        self.b(f"**Chặn tất cả (E03):** Windows 10: {ct(w10, 'E03').split(',')[0]}; Windows 11: {ct(w11, 'E03').split(',')[0]}. Windows ghi nhận thiết bị USB ở trạng thái lỗi do driver bị tắt và dịch vụ hiện thông báo cho người dùng (E04).")
        self.b(f"**Danh sách cho phép (E10):** USB lạ bị gỡ trước khi kịp có ký tự ổ. Windows 10: {ct(w10, 'E10')}; Windows 11: {ct(w11, 'E10')}.")
        self.b(f"**Chuột và bàn phím (E05):** Windows 10: {ct(w10, 'E05').split(':')[0]}; Windows 11: {ct(w11, 'E05').split(':')[0]}.")
        self.b(f"**Cho phép USB đang cắm không cần rút ra:** sau lệnh tạm dừng (E06) USB ghi được sau {ms(w10, 'E06')} ms (Windows 10) và {ms(w11, 'E06')} ms (Windows 11); sau khi thêm serial vào danh sách cho phép (E09) là {ms(w10, 'E09')} ms và {ms(w11, 'E09')} ms.")
        self.b(f"**Rút ra cắm lại USB được phép (E12):** ghi được sau {ms(w10, 'E12')} ms (Windows 10) và {ms(w11, 'E12')} ms (Windows 11) tính từ lúc bắt đầu theo dõi ổ.")

        self.fig(pathlib.Path(PROJECT_ROOT / "release" / "anh" / "thong-bao-chan.png"), "Hình 5.3: Hộp thoại UsbGuard báo người dùng khi USB bị chặn", width_cm=7.5)
        self.fig(w11["anh_dir"] / "gui-quan-ly.png", "Hình 5.4: Windows 11 Pro, giao diện quản lý khi chặn USB lạ", width_cm=8.0)

        self.h2("5.5. 3 lỗi phát hiện khi cắm USB thật và cách sửa")
        self.p("Ở bản 1.1, lần chạy kiểm thử cắm USB đầu tiên (khi đó có 17 ca) chỉ đạt 11/17 ca. Việc cắm USB thật đã phát hiện 3 lỗi mà kiểm thử trên Windows Server không bắt được. Sau khi sửa cả 3 lỗi, bộ kiểm thử khi đó đạt đủ 17 ca trên cả Windows 10 và Windows 11. Ở bản 1.2 bộ kiểm thử có thêm 3 ca (E18 đến E20) và đạt toàn bộ (Bảng 5.3).")
        headers_bug = ["Lỗi", "Hiện tượng", "Nguyên nhân và cách sửa"]
        widths_bug = [1900, 3000, 4171]
        rows_bug = [
            ["1. Bật lại chặn khi USB đang mở tệp", "USB vẫn ghi được dù đã bật lại chặn.", "Windows từ chối eject vì có tệp đang mở. Sửa: thêm buộc tháo ổ (ForceDismount) bằng FSCTL_LOCK_VOLUME và FSCTL_DISMOUNT_VOLUME rồi eject lại (ca E07)."],
            ["2. Lệnh dự phòng pnputil trả mã 3010", "USB bị vô hiệu hóa vĩnh viễn, kể cả sau khi gỡ UsbGuard.", "`pnputil /disable-device` trả 3010 (chờ khởi động lại) nhưng không được ghi lại. Sửa: ghi nhận cả mã 3010, khi bỏ chặn thì bật lại hoặc xóa nút thiết bị (ca E16, E17)."],
            ["3. USB cắm lần đầu lúc đang chặn", "Sau đó cho phép, USB cũng không lên.", "Tầng 3 làm Windows đánh dấu \"cài thất bại\". Sửa: khi bỏ chặn, xóa nút thiết bị bằng `pnputil /remove-device` rồi quét lại `/scan-devices` (ca E06, E09)."]
        ]
        self.tbl("TBL_BUG", "Bảng 5.4: 3 lỗi phát hiện khi cắm USB thật và cách sửa", headers_bug, rows_bug, widths_bug, ["left", "left", "left"], sz=21)

        self.h2("5.6. Kiểm thử thủ công trên máy Windows thật (bản 1.1.0)")
        self.p("Sau các lượt kiểm thử tự động, 1 thành viên nhóm đã cài UsbGuard 1.1.0 (bản Release, biên dịch với 0 cảnh báo và 0 lỗi) lên máy Windows thật và thử bằng USB vật lý. Các thao tác được đối chiếu qua This PC, trạng thái dịch vụ, lệnh `devices` và Registry. Cả 7 kịch bản đều cho kết quả đạt:")
        headers_mt = ["STT", "Kịch bản", "Kết quả quan sát", "Đánh giá"]
        widths_mt = [750, 2400, 4721, 1200]
        rows_mt = [
            ["1", "Cài đặt và tự khởi động cùng Windows", "Sau khi khởi động lại máy, `sc.exe query UsbGuard` trả về STATE: 4 RUNNING.", "Đạt"],
            ["2", "Chặn USB lưu trữ ở chế độ CHẶN TẤT CẢ", "Hiện thông báo chặn; ổ USB không xuất hiện trong This PC; lệnh `devices` ghi nhận thiết bị bị chặn với mã 47.", "Đạt"],
            ["3", "Tạm dừng, bật lại và danh sách cho phép", "USB dùng được khi tạm dừng và bị chặn lại sau khi bật lại; thêm số serial vào danh sách thì dịch vụ chuyển sang DANH SÁCH CHO PHÉP và USB hiện lại trong This PC.", "Đạt (với USB đã thử)"],
            ["4", "Administrator gửi lệnh dừng dịch vụ", "`sc.exe stop UsbGuard` trả lỗi 1052; truy vấn ngay sau đó vẫn báo RUNNING.", "Đạt"],
            ["5", "Phiên PowerShell không nâng quyền gửi lệnh dừng", "`sc.exe stop UsbGuard` trả lỗi 5 (Access is denied).", "Đạt"],
            ["6", "Chuột và bàn phím USB", "Vẫn dùng được khi ở chế độ CHẶN TẤT CẢ.", "Đạt"],
            ["7", "Gỡ cài đặt và khôi phục cấu hình", "Sai mật khẩu bị từ chối, dịch vụ vẫn chạy; đúng mật khẩu thì gỡ thành công. Sau khi gỡ: `sc.exe query` trả mã 1060, USBSTOR Start = 3, giá trị Deny_All và khóa cấu hình UsbGuard đã bị xóa.", "Đạt"]
        ]
        self.tbl("TBL_MAYTHAT", "Bảng 5.5: Kết quả 7 kịch bản thử thủ công trên máy Windows thật (bản 1.1.0)", headers_mt, rows_mt, widths_mt, ["center", "left", "left", "center"], sz=20)
        self.p("Giới hạn của lượt thử này: whitelist mới được xác nhận với USB đã thử; kết quả từ chối `sc.exe stop` chỉ xác nhận các tình huống đã thực hiện, không chứng minh dịch vụ không thể bị dừng bằng mọi phương thức; chưa ghi lại kết quả cắm lại USB sau khi gỡ cài đặt, cũng như thông tin chi tiết về phiên bản Windows, cấu hình máy và số lượng USB đã dùng. Vì vậy cần thử thêm nhiều loại USB và nhiều máy.")

        self.h2("5.7. Phản hồi từ thử nghiệm máy thật và các thay đổi ở bản 1.2")
        self.p("Ngoài 7 kịch bản đạt, lượt thử trên máy thật cho thấy 2 điểm chưa hoàn thiện về trải nghiệm. Cả 2 đã được tái hiện trong môi trường máy ảo Windows trước khi sửa (lần chạy 44881182584: ca E19 và E20 không đạt), rồi đạt sau khi sửa (lần chạy 44884948981). Bản 1.2 cũng nâng cấp bảo mật mật khẩu và hoàn thiện giao diện:")
        headers_p = ["Phản hồi / thay đổi", "Hiện tượng hoặc mục tiêu", "Cách xử lý ở bản 1.2 và ca kiểm chứng"]
        widths_p = [1900, 2900, 4271]
        rows_p = [
            ["a. USB bị tháo khi được cho phép", "USB bị chặn lúc đang cắm thì Windows tháo an toàn (mã 47). Khi được cho phép hoặc tạm dừng, phải rút ra cắm lại mới dùng được.", f"Ghi nhớ vị trí hub và số cổng; \"rút ra cắm lại bằng phần mềm\" bằng `IOCTL_USB_HUB_CYCLE_PORT`, tối đa 3 lần cách 10 giây; không dùng `pnputil /restart-device` vì chuyển USB sang mã 14 (đòi khởi động lại máy). Ca E19, E20: ghi được sau {ms(w10, 'E19')} ms và {ms(w10, 'E20')} ms (Windows 10), {ms(w11, 'E19')} ms và {ms(w11, 'E20')} ms (Windows 11)."],
            ["b. USB biến khỏi danh sách", "USB đã bị tháo nhưng vẫn cắm có lúc không còn trong danh sách của phần mềm.", "Đọc trạng thái cổng từ driver hub (`IOCTL_USB_GET_NODE_CONNECTION_INFORMATION`) nên USB vẫn hiện, với trạng thái \"Bị chặn (đã tháo)\" (ca E18)."],
            ["c. Mật khẩu mạnh hơn", "Giảm nguy cơ bị dò mật khẩu, kể cả khi lộ mã băm hoặc thử liên tục.", f"PBKDF2-HMAC-SHA256 600000 vòng, tự nâng cấp mã băm cũ; sai 5 lần khoá 30 giây, mỗi lần sai tiếp gấp đôi, tối đa 1 giờ, áp dụng cho giao diện, dòng lệnh và trình gỡ (ca TC35, TC36, TC37: {kqs(t22)} ca tích hợp đạt)."],
            ["d. Giao diện rõ hơn", "Người dùng dễ nhầm khi đang tạm dừng và khi USB đã bị tháo.", "Thanh tạm dừng ghi \"Muốn chặn ngay: bấm Bật lại chặn\"; danh sách USB hiện trạng thái \"Bị chặn (đã tháo)\"."]
        ]
        self.tbl("TBL_MT12", "Bảng 5.6: Phản hồi từ thử nghiệm máy thật và các thay đổi ở bản 1.2", headers_p, rows_p, widths_p, ["left", "left", "left"], sz=20)

        self.h2("5.8. Đánh giá mức độ đáp ứng các yêu cầu hệ thống")
        self.p("Đối chiếu kết quả thực nghiệm với các yêu cầu đã đặt ra tại Chương 3. Một yêu cầu chỉ được ghi là đáp ứng khi toàn bộ ca kiểm thử liên quan đều đạt trong các tệp kết quả:")
        okS = ok_ca(t22) and ok_ca(t25)
        okU = ok_ca(u22) and ok_ca(u25)
        okE = lambda *ids: all(w["theo_ma"][i]["dat"] for w in (w10, w11) for i in ids)
        okT = lambda *ids: all(t["theo_ma"][i]["dat"] for t in (t22, t25) for i in ids)
        ok_dg = lambda cond, text: text if cond else "CHƯA ĐẠT: có ca kiểm thử không đạt"
        headers_dg = ["Mã yêu cầu", "Tiêu chuẩn thiết kế", "Kết quả thực tế đạt được", "Đánh giá mức độ đáp ứng"]
        widths_dg = [1250, 2500, 3721, 1600]
        rows_dg = [
            ["YC-CN01", "Chặn USB lưu trữ trong <= 2 giây.", f"E03: {ct(w10, 'E03').split(',')[0]}. E10: USB lạ bị gỡ trước khi có ký tự ổ ({ct(w10, 'E10')}).", ok_dg(okE("E03", "E10"), "Đáp ứng (đã kiểm thử cắm USB trên Windows 10/11)")],
            ["YC-CN02", "Bảo toàn chuột, bàn phím HID.", f"E05: {ct(w10, 'E05').split(':')[0]}; không thiết bị nào báo lỗi.", ok_dg(okE("E05"), "Đáp ứng (đã kiểm thử cắm USB trên Windows 10/11)")],
            ["YC-CN03", "Hỗ trợ 3 chế độ hoạt động.", f"Chuyển đúng giữa chặn tất cả, danh sách cho phép, tạm dừng ({kqs(t22)} ca tích hợp; E06, E09, E13).", ok_dg(okS and okE("E06", "E09", "E13"), "Đáp ứng (CI và cắm USB thật)")],
            ["YC-CN04", "Quản lý danh sách Whitelist.", "Thêm, xóa, xem danh sách theo serial; USB được phép dùng, USB lạ bị gỡ (E09, E10, E11, E13).", ok_dg(okS and okE("E09", "E10", "E11", "E13"), "Đáp ứng (CI và cắm USB thật)")],
            ["YC-CN05", "Tạm dừng chặn có thời hạn.", "Tạm dừng mở USB đang cắm, kể cả USB đã bị Windows tháo (E06, E20); hết hạn tự chặn lại (ca tích hợp).", ok_dg(okS and okE("E06", "E20"), "Đáp ứng (CI và cắm USB thật)")],
            ["YC-CN06", "Xác thực mật khẩu quản trị.", f"PBKDF2-SHA256 600000 vòng, so sánh thời gian hằng, khoá tăng dần khi sai (TC35 đến TC37); {kqs(u22)} unit test; sai mật khẩu bị từ chối (E15).", ok_dg(okU and okE("E15") and okT("TC35", "TC36", "TC37"), f"Đáp ứng ({kqs(u22)} unit test đạt)")],
            ["YC-CN07", "Gỡ cài đặt hoàn trả mặc định.", "Gỡ đúng mật khẩu trả lại cấu hình USB, USB dùng lại bình thường (E16, E17).", ok_dg(okS and okE("E16", "E17"), "Đáp ứng (CI và cắm USB thật)")],
            ["YC-CN08", "Giao diện quản lý đồ họa.", "Giao diện cho phép USB đang cắm, tạm dừng, gỡ cài đặt; ảnh chụp trên Windows 10/11 (Hình 4.1, 5.4).", ok_dg(okE("E06", "E09"), "Đáp ứng (đã chạy trên Windows 10/11)")],
            ["YC-CN09", "Bộ cài setup.exe.", "Cài đặt đủ 3 tầng chặn, có lối tắt; trình gỡ sai mật khẩu không gỡ được (E02, E15, E16).", ok_dg(okE("E02", "E15", "E16"), "Đáp ứng (đã cài và gỡ trên Windows 10/11)")],
            ["YC-PCN01", "Cơ chế 'không tắt được'.", "SCM từ chối sc stop (lỗi 1052); user thường bị từ chối (lỗi 5); kill khi USB đang cắm vẫn chặn (E14).", ok_dg(okS and okE("E14"), "Đáp ứng (CI và cắm USB thật)")],
            ["YC-PCN02", "Tự phục hồi khi bị kill.", f"Windows chạy lại dịch vụ sau {t22['chay_lai_ms']} ms (Server 2022) và {t25['chay_lai_ms']} ms (Server 2025).", ok_dg(okS, "Đáp ứng (đã kiểm thử CI)")],
            ["YC-PCN03", "Tài nguyên: CPU < 1%, RAM < 50 MB.", f"RAM trung bình {t22['ram_tb_mb']} MB (cao nhất {t22['ram_max_mb']} MB), CPU {t22['cpu_pct']}% (Server 2022); RAM {t25['ram_tb_mb']} MB (cao nhất {t25['ram_max_mb']} MB), CPU {t25['cpu_pct']}% (Server 2025).", ok_dg(max(t22['ram_max_mb'], t25['ram_max_mb']) < 50 and max(t22['cpu_pct'], t25['cpu_pct']) < 1, "Đáp ứng (đo trên Windows Server 2022/2025)")],
            ["YC-PCN04", "Bảo mật cấu hình Registry.", "DACL ngắt kế thừa, chỉ SYSTEM và Administrators truy cập; user thường bị từ chối (ca tích hợp).", ok_dg(okS, "Đáp ứng (đã kiểm thử CI)")]
        ]
        self.tbl("TBL_DG", "Bảng 5.7: Đánh giá mức độ đáp ứng các yêu cầu hệ thống", headers_dg, rows_dg, widths_dg, ["center", "left", "left", "center"], sz=20)

    # ==========================================================================
    # CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
    # ==========================================================================
    def tao_chuong_6(self):
        D = lay_du_lieu()
        t22, t25, w10, w11, u22 = D["t22"], D["t25"], D["w10"], D["w11"], D["u22"]
        self.h1("CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")

        self.h2("6.1. Các kết quả chính đã đạt được")
        self.p("Sau quá trình nghiên cứu lý thuyết và triển khai thực nghiệm, đề tài Seminar Chuyên đề đã hoàn thành các mục tiêu đề ra:")
        self.b("**Xây dựng sản phẩm UsbGuard 1.2:** Ứng dụng chạy như 1 Windows Service độc lập, gọn nhẹ trên C# 9.0 và .NET Framework 4.8, kèm giao diện quản lý đồ họa và bộ cài `setup.exe`, ngăn chặn mọi USB flash disk và ổ cứng di động.")
        self.b("**Kiến trúc 3 tầng chặn và lớp gỡ thiết bị:** Tầng 1 tắt driver `USBSTOR`/`UASPStor`, tầng 2 chính sách `Deny_All`, tầng 3 cấm cài thiết bị lớp USB Mass Storage; lớp gỡ dùng SetupAPI, IOCTL, `CM_Request_Device_Eject`, buộc tháo ổ khi đang mở tệp và nạp lại thiết bị khi bỏ chặn.")
        self.b("**Bảo vệ an toàn cho thiết bị HID:** Nhờ ranh giới `MaxDepth = 2` và tầng 3 chỉ nhắm lớp 08, chuột và bàn phím USB hoạt động liên tục (ca E05 đạt trên Windows 10 và Windows 11).")
        self.b("**Hiện thực hóa tính chất 'không tắt được':** `CanStop = false` để từ chối lệnh dừng từ SCM (lỗi 1052), DACL từ chối người dùng thường (lỗi 5) và `sc failure` tự chạy lại dịch vụ sau khoảng 5 giây nếu bị kill.")
        self.b("**Bảo mật và quản trị chuyên nghiệp:** 3 chế độ vận hành (CHẶN TẤT CẢ, DANH SÁCH CHO PHÉP, TẠM DỪNG); mật khẩu băm PBKDF2-SHA256 600000 vòng; khoá tăng dần sau 5 lần nhập sai (30 giây, gấp đôi mỗi lần, tối đa 1 giờ) cho giao diện, dòng lệnh và trình gỡ; trình gỡ bắt buộc đúng mật khẩu.")
        self.b(f"**Kiểm chứng tự động trên Windows thật:** {kqs(u22)} ca unit test; {kqs(t22)} ca tích hợp trên Windows Server 2022 và {kqs(t25)} trên Windows Server 2025; {kqs(w10)} ca cắm USB thật trên Windows 10 và {kqs(w11)} trên Windows 11; thêm 1 lượt thử thủ công trên máy Windows thật với 7 kịch bản đều đạt.")
        self.b("**Quá trình tìm và sửa lỗi:** Kiểm thử cắm USB thật phát hiện 3 lỗi mà Windows Server không bắt được (mục 5.5) và đều đã được sửa. Lượt thử trên máy thật tiếp tục cho phản hồi về USB bị Windows tháo, dẫn tới bản 1.2 tự nạp lại USB bằng cách rút ra cắm lại cổng bằng phần mềm (mục 3.14, 5.7), minh chứng cho giá trị của việc thử trên thiết bị thật.")

        self.h2("6.2. Hạn chế của giải pháp hiện tại")
        self.p("Nhìn nhận khách quan, UsbGuard 1.2 còn một số hạn chế kỹ thuật:")
        self.b("**Chưa có chữ ký số thương mại:** `setup.exe` và `UsbGuard.exe` chưa được ký bằng chứng chỉ thương mại nên Windows SmartScreen có thể cảnh báo khi cài đặt.")
        self.b("**Phạm vi loại thiết bị:** Chưa kiểm soát giao thức MTP/PTP (điện thoại thông minh), ổ đĩa quang CD/DVD và thiết bị truyền dữ liệu qua Bluetooth.")
        self.b("**Giới hạn quyền Administrator:** Nếu kẻ tấn công là Administrator hiểu sâu hệ thống, khởi động vào Safe Mode hoặc sửa Registry ngoại tuyến (offline registry editing) thì vẫn can thiệp được. Đây là giới hạn của giải pháp phần mềm khi không có TPM và BitLocker.")
        self.b("**Nhận diện thiết bị theo VID/PID:** Các USB giá rẻ thường không có số serial duy nhất mà chỉ dùng chung cặp VID/PID, nên đưa ID này vào whitelist sẽ cho phép mọi USB cùng model. Khi đó nên dùng số serial (nếu có) hoặc chế độ tạm dừng có thời hạn.")
        self.b("**Phạm vi kiểm thử phần cứng:** Đã có 1 lượt thử thủ công trên máy Windows thật với USB vật lý (bản 1.1.0, mục 5.6) và các lượt cắm USB trên máy ảo (ổ QEMU `usb-storage`), nên cần thử thêm nhiều loại USB và nhiều máy, kể cả sau khi gỡ cài đặt.")

        self.h2("6.3. Hướng nghiên cứu và phát triển tiếp theo")
        self.p("Để nâng UsbGuard thành giải pháp phòng chống thất thoát dữ liệu (DLP) hoàn chỉnh hơn, các hướng phát triển tiếp theo gồm:")
        self.b("**Quản lý tập trung qua mạng:** Phát triển máy chủ điều khiển (Dashboard Web) để đẩy cấu hình Whitelist, phát lệnh khóa/mở và giám sát nhật ký vi phạm của nhiều máy trạm.")
        self.b("**Kernel-Mode Filter Driver:** Chuyển một phần cơ chế chặn xuống driver lọc tầng nhân để chặn ngay trong giai đoạn nạp ngăn xếp I/O.")
        self.b("**Ký số chương trình:** Mua chứng chỉ ký mã (code signing) cho `UsbGuard.exe` và `setup.exe` để không bị SmartScreen hay phần mềm diệt virus cảnh báo nhầm.")
        self.b("**Mở rộng kiểm soát thiết bị ngoại vi:** Bổ sung bộ lọc cho MTP (điện thoại), Thunderbolt, FireWire và Bluetooth.")

    # ==========================================================================
    # TÀI LIỆU THAM KHẢO VÀ PHỤ LỤC
    # ==========================================================================
    def tao_tai_lieu_tham_khao(self):
        self.h1("TÀI LIỆU THAM KHẢO")

        tai_lieu = [
            "[1] Microsoft Corporation, *Windows Services Architecture and Service Control Manager*, Microsoft Learn Documentation, 2024. URL: https://learn.microsoft.com/en-us/windows/win32/services/services",
            "[2] Microsoft Corporation, *SetupAPI Device Installation Guide: SetupDiGetClassDevs function*, Microsoft Learn, 2024. URL: https://learn.microsoft.com/en-us/windows/win32/api/setupapi/nf-setupapi-setupdigetclassdevsw",
            "[3] Microsoft Corporation, *Configuration Manager API: CM_Request_Device_Eject function*, Microsoft Learn, 2024. URL: https://learn.microsoft.com/en-us/windows/win32/api/cfgmgr32/nf-cfgmgr32-cm_request_device_ejectw",
            "[4] Microsoft Corporation, *IOCTL_STORAGE_QUERY_PROPERTY control code and STORAGE_BUS_TYPE enumeration*, Microsoft Learn, 2024. URL: https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-ioctl_storage_query_property",
            "[5] Microsoft Corporation, *Removable Storage Access Group Policy Settings and Registry Keys*, Windows Security Baseline Documentation, 2024. URL: https://learn.microsoft.com/en-us/windows/security/threat-protection/device-control/control-usb-devices-using-intune",
            "[6] Microsoft Corporation, *Service Failure Operations: sc.exe failure command*, Microsoft Learn Command-Line Reference, 2024. URL: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-failure",
            "[7] K. Moriarty, B. Kaliski, A. Rusch, *PKCS #5: Password-Based Cryptography Specification Version 2.1 (RFC 8018)*, Internet Engineering Task Force (IETF), 2017. URL: https://datatracker.ietf.org/doc/html/rfc8018",
            "[8] USB Implementers Forum, *Universal Serial Bus Mass Storage Class - Bulk-Only Transport Specification (Revision 1.0)*, USB-IF, 1999. URL: https://www.usb.org/document-library/mass-storage-bulk-only-10",
            "[9] USB Implementers Forum, *Universal Serial Bus Attached SCSI Protocol (UASP) v1.0*, USB-IF, 2009. URL: https://www.usb.org/document-library/usb-attached-scsi-protocol-uasp-v10",
            "[10] JBalanza, *USBBlocker: Windows Service to block unauthorized USB storage devices*, GitHub Repository, 2021. URL: https://github.com/JBalanza/USBBlocker",
            "[11] sidd607, *usbAlert: Windows Service monitoring USB device insertion via SetupAPI*, GitHub Repository, 2020. URL: https://github.com/sidd607/usbAlert",
            "[12] amir13872, *usb-control-application: Endpoint device control with whitelist authentication*, GitHub Repository, 2021. URL: https://github.com/amir13872/usb-control-application",
            "[13] Den-Sec, *USBBlocker PowerShell utility for managing USBSTOR driver state*, Git Repository, 2022. URL: https://gitblind.noratr.app/Den-Sec/USBBlocker",
            "[14] Microsoft Corporation, *Manage Device Installation with Group Policy (Device Installation Restrictions)*, Microsoft Learn, 2024. URL: https://learn.microsoft.com/en-us/windows/client-management/manage-device-installation-with-group-policy",
            "[15] J. Russell, *Inno Setup Documentation*, jrsoftware.org. URL: https://jrsoftware.org/ishelp/",
            "[16] QEMU Project, *USB emulation (usb-storage, xHCI)*, QEMU Documentation. URL: https://www.qemu.org/docs/master/system/devices/usb.html",
            "[17] dockur, *Windows in a Docker container (dockur/windows)*, GitHub Repository. URL: https://github.com/dockur/windows"
        ]
        for item in tai_lieu:
            self.add(para(item, after=120, line=288, first_line=0))

    def tao_phu_luc(self):
        self.h1("PHỤ LỤC")

        iss = open(PROJECT_ROOT / "installer" / "UsbGuard.iss", encoding="utf-8-sig").read()
        m1 = re.search(r"\[Files\].*?(?=\[Code\])", iss, re.S)
        m2 = re.search(r"procedure CurStepChanged.*?\nend;", iss, re.S)
        if not m1 or not m2:
            raise SystemExit("[LỖI] Không trích được nội dung installer/UsbGuard.iss")
        self.h2("Phụ lục A: Cấu hình bộ cài đặt (installer/UsbGuard.iss)")
        self.p("Trích đoạn tệp Inno Setup: các mục tệp, lối tắt, chạy sau cài và bước truyền mật khẩu qua biến môi trường:")
        self.code("; Trích từ installer/UsbGuard.iss\n" + gon(m1.group(0)) + "\n" + gon(m2.group(0)), 17, False)

        self.h2("Phụ lục B: Kịch bản kiểm thử tích hợp PowerShell (tests/integration.ps1)")
        self.p("Trích đoạn mã cấu trúc thực thi kiểm thử tự động của tệp `tests/integration.ps1`:")
        self.code(sz=17, keep=False, code_text="""# Trích đoạn mã từ tests/integration.ps1
param(
    [Parameter(Mandatory = $true)][string]$Exe,
    [string]$OutDir = (Join-Path $PSScriptRoot 'ket-qua')
)
$Pw = 'MatKhauTest@2026'; $Svc = 'UsbGuard'
# TC01: Cài đặt dịch vụ
$r = Run-Exe @('install', $Pw)
$t = Wait-Until { (Svc-State) -eq 'Running' } 15000
Check 'TC01' 'Cài đặt, dịch vụ chạy' ($r.rc -eq 0 -and $t -ge 0)
# TC08: Administrator thử dừng dịch vụ trực tiếp
$r = Run-Cmd 'sc.exe' "stop $Svc"
Check 'TC08' 'Admin sc stop bị từ chối' ($r.rc -ne 0 -and (Svc-State) -eq 'Running')
# TC10: Bị kill tiến trình thì Windows tự chạy lại
$pid1 = Svc-Pid; Run-Cmd 'taskkill.exe' "/F /PID $pid1"
$t = Wait-Until { (Svc-State) -eq 'Running' -and (Svc-Pid) -ne $pid1 } 20000
Check 'TC10' 'Windows tự khởi động lại dịch vụ' ($t -ge 0)""")

        wf = open(PROJECT_ROOT / ".github" / "workflows" / "windows.yml", encoding="utf-8-sig").read()
        phan = wf.split("      - name: Dong goi bo cai")[0].rstrip()
        self.h2("Phụ lục C: Cấu hình quy trình CI GitHub Actions (.github/workflows/windows.yml)")
        self.p("Tệp cấu hình quy trình tích hợp liên tục chạy kiểm thử trên Windows Server 2022 và Windows Server 2025 (phần build và kiểm thử; các bước đóng gói bộ cài và tải kết quả được lược bỏ):")
        self.code("# Trích từ .github/workflows/windows.yml\n" + gon(phan), 17, False)



# ==============================================================================
# QUY TRÌNH KẾT XUẤT 2 LƯỢT ĐỂ TÍNH TOÁN SỐ TRANG CHÍNH XÁC
# ==============================================================================
def trich_xuat_so_trang_pdf(pdf_path, headings, figures, tables):
    """Sử dụng PyMuPDF duyệt qua từng trang PDF và tìm vị trí tiêu đề để lập bản đồ trang."""
    doc_pdf = fitz.open(pdf_path)
    total_pages = len(doc_pdf)
    trang_map = {}
    
    # Xác định trang bắt đầu phần thân tài liệu (Chương 1)
    body_start = 1
    for pn, page in enumerate(doc_pdf):
        text_page = page.get_text()
        lines = [l.strip() for l in text_page.split('\n') if l.strip()]
        for l in lines:
            if l.startswith("CHƯƠNG 1") and "..." not in l:
                body_start = pn + 1
                break
        if body_start > 1:
            break
            
    print(f"   [PyMuPDF] Xác định phần thân tài liệu (Chương 1) bắt đầu từ trang {body_start}.")
    
    # 1. Dò số trang cho Headings (chỉ tìm trong phần thân từ body_start trở đi)
    for pn in range(body_start - 1, total_pages):
        page_num = pn + 1
        text_page = doc_pdf[pn].get_text()
        haystack_norm = re.sub(r'\s+', ' ', text_page)
        
        for lv, t in headings:
            if t in trang_map:
                continue
            needle_norm = re.sub(r'\s+', ' ', t).strip()
            if needle_norm in haystack_norm or (len(needle_norm) > 25 and needle_norm[:25] in haystack_norm):
                trang_map[t] = str(page_num)

    # 2. Dò số trang cho Figures (Hình x.y - toàn bộ nằm từ body_start trở đi)
    for pn in range(body_start - 1, total_pages):
        page_num = pn + 1
        text_page = doc_pdf[pn].get_text()
        haystack_norm = re.sub(r'\s+', ' ', text_page)
        for fig_id, caption in figures:
            if caption in trang_map:
                continue
            needle_norm = re.sub(r'\s+', ' ', caption).strip()
            if needle_norm in haystack_norm or (len(needle_norm) > 20 and needle_norm[:20] in haystack_norm):
                trang_map[caption] = str(page_num)

    # 3. Dò số trang cho Tables (Bảng x.y)
    for pn in range(total_pages):
        page_num = pn + 1
        text_page = doc_pdf[pn].get_text()
        if "DANH MỤC BẢNG BIỂU" in text_page[:200]:
            continue
        haystack_norm = re.sub(r'\s+', ' ', text_page)
        for tbl_id, caption in tables:
            if caption in trang_map:
                continue
            needle_norm = re.sub(r'\s+', ' ', caption).strip()
            if needle_norm in haystack_norm or (len(needle_norm) > 20 and needle_norm[:20] in haystack_norm):
                trang_map[caption] = str(page_num)

    doc_pdf.close()
    
    # Tự kiểm tra tính đầy đủ
    chua_khop = [t for _, t in headings if t not in trang_map]
    chua_khop += [cap for _, cap in figures if cap not in trang_map]
    chua_khop += [cap for _, cap in tables if cap not in trang_map]
    if chua_khop:
        print(f"   [CẢNH BÁO] Có {len(chua_khop)} mục chưa khớp trang: {chua_khop[:5]}")
    else:
        print(f"   [XÁC NHẬN] 100% mục ({len(headings)} tiêu đề, {len(figures)} hình, {len(tables)} bảng) đã khớp số trang!")

    return trang_map, total_pages


def tao_toan_bo_tai_lieu(page_map=None):
    """Khởi tạo tài liệu và xây dựng đầy đủ các phần."""
    bc = BaoCaoUsbGuard(page_map=page_map)
    bc.tao_trang_bia()
    bc.tao_loi_cam_on()
    bc.tao_nhan_xet_giang_vien()
    bc.tao_muc_luc()
    bc.tao_danh_muc_hinh()
    bc.tao_danh_muc_bang()
    bc.tao_danh_muc_tu_viet_tat()
    bc.tao_chuong_1()
    bc.tao_chuong_2()
    bc.tao_chuong_3()
    bc.tao_chuong_4()
    bc.tao_chuong_5()
    bc.tao_chuong_6()
    bc.tao_tai_lieu_tham_khao()
    bc.tao_phu_luc()
    bc.hoan_tat_muc_luc()
    return bc


def chuyen_doi_docx_sang_pdf(docx_path, out_dir):
    """Gọi LibreOffice headless để chuyển đổi docx sang PDF."""
    env_dir = f"file:///tmp/usbguard_lo_env_{os.getpid()}"
    cmd = [
        SOFFICE,
        f"-env:UserInstallation={env_dir}",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(out_dir),
        str(docx_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    print("=================================================================")
    print("BẮT ĐẦU QUY TRÌNH SINH BÁO CÁO SEMINAR CHUYÊN ĐỀ USBGUARD")
    print("=================================================================")
    
    # Bước 1: Đảm bảo các hình vẽ đã được sinh ra
    print("1. Kiểm tra và vẽ lại các sơ đồ kỹ thuật (report/ve_hinh.py)...")
    ve_hinh_script = HERE / "ve_hinh.py"
    if ve_hinh_script.exists():
        subprocess.run(["python3", str(ve_hinh_script)], check=True)
    
    docx_file = HERE / "BAO-CAO-UsbGuard.docx"
    pdf_file = HERE / "BAO-CAO-UsbGuard.pdf"
    
    # LƯỢT 1: Sinh docx sơ bộ không có số trang mục lục
    print("2. [Lượt 1] Tạo tệp docx sơ bộ...")
    bc1 = tao_toan_bo_tai_lieu(page_map={})
    bc1.doc.save(str(docx_file))
    
    # Lưu danh sách tiêu đề để dò trang
    danh_sach_tim_trang = [t for _, t in bc1.headings] + [cap for _, cap in bc1.figures] + [cap for _, cap in bc1.tables]
    
    print("3. [Lượt 1] Xuất PDF sơ bộ bằng LibreOffice để dò số trang...")
    chuyen_doi_docx_sang_pdf(docx_file, HERE)
    
    print("4. [Lượt 1] Dò số trang của từng tiêu đề, hình vẽ và bảng biểu qua PyMuPDF...")
    page_map, tong_so_trang_1 = trich_xuat_so_trang_pdf(pdf_file, bc1.headings, bc1.figures, bc1.tables)
    print(f"   -> Phát hiện {len(page_map)} mục trên tổng số {tong_so_trang_1} trang.")
    
    # LƯỢT 2: Sinh docx hoàn chỉnh với số trang mục lục chính xác
    print("5. [Lượt 2] Tạo tệp docx chính thức với Mục lục có số trang chính xác...")
    bc2 = tao_toan_bo_tai_lieu(page_map=page_map)
    bc2.doc.save(str(docx_file))
    
    print("6. [Lượt 2] Xuất PDF hoàn chỉnh bằng LibreOffice...")
    chuyen_doi_docx_sang_pdf(docx_file, HERE)
    
    # Lặp tới khi số trang trong mục lục khớp với PDF cuối (bố cục có thể xê dịch sau khi điền mục lục)
    for lan in range(3):
        page_map2, _ = trich_xuat_so_trang_pdf(pdf_file, bc2.headings, bc2.figures, bc2.tables)
        if page_map2 == page_map:
            break
        print(f"   [Lượt bổ sung {lan + 1}] Số trang xê dịch, dựng lại mục lục...")
        page_map = page_map2
        bc2 = tao_toan_bo_tai_lieu(page_map=page_map)
        bc2.doc.save(str(docx_file))
        chuyen_doi_docx_sang_pdf(docx_file, HERE)

    # Kiểm tra lại số trang lần cuối
    doc_cuoi = fitz.open(pdf_file)
    tong_so_trang_cuoi = len(doc_cuoi)
    doc_cuoi.close()
    
    print("=================================================================")
    print(f"KẾT QUẢ SINH BÁO CÁO THÀNH CÔNG:")
    print(f"- Tệp Word: {docx_file} ({docx_file.stat().st_size // 1024} KB)")
    print(f"- Tệp PDF:  {pdf_file} ({pdf_file.stat().st_size // 1024} KB)")
    print(f"- Tổng số trang tài liệu: {tong_so_trang_cuoi} trang (Yêu cầu: 35-50 trang).")
    print(f"- Số lượng hình vẽ kỹ thuật: {len(bc2.figures)} hình.")
    print(f"- Số lượng bảng biểu số liệu: {len(bc2.tables)} bảng.")
    print("=================================================================")


if __name__ == "__main__":
    main()

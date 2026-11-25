#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slide UsbGuard bản trình chiếu (HTML 1920x1080 -> PDF + PPTX ảnh).
Số liệu kiểm thử đọc từ tests/ket-qua qua report/ket_qua.py, không gõ tay.
Chạy: python3 slide/tao_slide_html.py
"""
import os, sys, pathlib, shutil, subprocess, html

HERE = pathlib.Path(__file__).parent.resolve()
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "report"))
import ket_qua as kq

K22, K25 = kq.tich_hop(2022), kq.tich_hop(2025)
W10, W11 = kq.e2e(10), kq.e2e(11)
U22, U25 = kq.unit(2022), kq.unit(2025)
for _d in (K22, K25, W10, W11, U22, U25):
    if _d["dat"] != _d["tong"]:
        raise SystemExit(f"[LỖI] Có ca không đạt: {_d['_tep']}")
SO_TEP, SO_DONG = len(kq.ma_nguon()), sum(n for _, n in kq.ma_nguon())
HINH = ROOT / "report" / "hinh"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def vn(x, nd=1):
    """Số kiểu Việt: 5,4 ; 600.000"""
    if isinstance(x, int):
        return f"{x:,}".replace(",", ".")
    return f"{x:.{nd}f}".replace(".", ",")


def giay(ms):
    return vn(ms / 1000, 1) + " giây"


def img(name):
    p = pathlib.Path(name)
    if not p.is_absolute():
        p = HINH / name
    return p.as_uri()


def e(s):
    return html.escape(s)


PHAN = ["Đặt vấn đề", "Thiết kế", "Triển khai", "Kiểm thử", "Kết luận"]

CSS = r"""
@page { size: 1920px 1080px; margin: 0; }
:root{
  --ink:#15202c; --muted:#5d6876; --line:#d9dee5; --tint:#f2f4f7; --paper:#ffffff;
  --accent:#1c4f9c; --accent-2:#e7eef9;
  --red:#c0392b; --red-2:#fbeceb; --green:#1f8a4c; --green-2:#e6f4ec; --amber:#b7791f; --amber-2:#fbf2e2;
  --mono: Menlo, "SF Mono", Consolas, monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff}
body{font-family:"Be Vietnam Pro",sans-serif;color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.s{width:1920px;height:1080px;position:relative;overflow:hidden;background:var(--paper);page-break-after:always;padding:84px 120px 120px;display:flex;flex-direction:column}
.top{position:absolute;left:120px;right:120px;top:44px;display:flex;justify-content:space-between;font-size:20px;color:var(--muted)}
.top b{color:var(--ink);font-weight:600}
.nav{position:absolute;left:120px;right:120px;bottom:40px;display:flex;gap:10px}
.nav div{flex:1;border-top:4px solid var(--line);padding-top:10px;font-size:18px;color:#9aa3ae}
.nav div.on{border-color:var(--accent);color:var(--ink);font-weight:600}
h1{font-size:58px;line-height:1.12;font-weight:700;letter-spacing:-.5px;margin-top:40px;max-width:1500px}
.lead{font-size:28px;color:var(--muted);margin-top:16px;max-width:1400px;line-height:1.45}
.body{position:relative;flex:1;margin-top:56px}
p,li{font-size:28px;line-height:1.45}
.mono{font-family:var(--mono)}
.muted{color:var(--muted)}
.row{display:flex;gap:56px;height:100%}
.col{flex:1;min-width:0}
.shot{border:1px solid var(--line);border-radius:10px;box-shadow:0 18px 40px rgba(20,32,44,.12);display:block;max-width:100%}
.tag{display:inline-block;font-size:20px;font-weight:600;padding:5px 14px;border-radius:999px}
.t-red{background:var(--red-2);color:var(--red)} .t-green{background:var(--green-2);color:var(--green)} .t-amber{background:var(--amber-2);color:var(--amber)}
.t-blue{background:var(--accent-2);color:var(--accent)}
table{border-collapse:collapse;width:100%}
th{font-size:22px;color:var(--muted);font-weight:500;text-align:left;padding:0 18px 14px;border-bottom:2px solid var(--ink)}
td{font-size:28px;padding:22px 18px;border-bottom:1px solid var(--line);vertical-align:top;line-height:1.35}
.ok{color:var(--green);font-weight:700}
.big{font-size:120px;font-weight:700;line-height:1;letter-spacing:-3px}
.num{font-weight:700;letter-spacing:-1px}
.term{background:#10161d;color:#d6dde6;border-radius:12px;padding:30px 36px;font-family:var(--mono);font-size:23px;line-height:1.6}
.term>div{white-space:pre}
.term .c{color:#7d8896} .term .p{color:#7fb2ff} .term .r{color:#ff8a7a} .term .g{color:#7dd3a0} .term .y{color:#f0c674}
li{margin-bottom:14px}
.note{font-size:24px;color:var(--muted);line-height:1.45}
"""


def trang(n, phan, tieu_de, noi_dung, lead=None):
    nav = "".join(f'<div class="{"on" if i == phan else ""}">{p}</div>' for i, p in enumerate(PHAN))
    ld = f'<div class="lead">{lead}</div>' if lead else ""
    return f'''<section class="s">
<div class="top"><span><b>UsbGuard 1.2.1</b> · Seminar chuyên đề</span><span>{n:02d} / 20</span></div>
<h1>{tieu_de}</h1>{ld}
<div class="body">{noi_dung}</div>
<div class="nav">{nav}</div></section>'''


S = []

# 1. Bìa
S.append(f'''<section class="s" style="padding:0">
<div style="position:absolute;left:120px;top:110px;width:820px">
  <div style="display:flex;align-items:center;gap:22px">
    <img src="{img('logo-sgu.png')}" style="height:84px">
    <div style="font-size:22px;line-height:1.4"><b>Trường Đại học Sài Gòn</b><br><span class="muted">Khoa Công nghệ Thông tin · Seminar chuyên đề</span></div>
  </div>
  <div style="font-size:30px;color:var(--accent);font-weight:600;margin-top:120px">UsbGuard</div>
  <div style="font-size:64px;font-weight:700;line-height:1.14;letter-spacing:-1px;margin-top:14px">Ngăn cắm USB trên Windows bằng một dịch vụ không tắt được</div>
  <div style="font-size:28px;color:var(--muted);margin-top:30px;line-height:1.5">Cắm USB lạ: ổ đĩa không hiện, không chép được dữ liệu.<br>Chuột, bàn phím vẫn dùng bình thường.</div>
  <div style="position:absolute;top:780px;font-size:24px;line-height:1.6">
    <b>Phạm Văn Hưng</b> · MSSV 3120410225<br><span class="muted">Tháng 11 năm 2026</span></div>
</div>
<div style="position:absolute;right:0;top:0;bottom:0;width:820px;background:var(--tint)"></div>
<img class="shot" src="{img('gui-quan-ly-1-2.png')}" style="position:absolute;right:90px;top:150px;width:820px">
<img class="shot" src="{img('e10-whitelist-chan-usb-la.png')}" style="position:absolute;right:300px;top:640px;width:600px">
</section>''')

# 2. Vấn đề
S.append(trang(2, 0, "1 chiếc USB, vài phút, và dữ liệu đã ra khỏi công ty", f'''
<div class="row">
 <div class="col" style="flex:1.15">
  <table>
   <tr><td style="width:190px;padding-left:0"><span class="tag t-red">Rò rỉ</span></td><td>USB nhỏ, chép được hàng chục GB dữ liệu nội bộ trong vài phút, không để lại dấu vết trên mạng.</td></tr>
   <tr><td style="padding-left:0"><span class="tag t-red">Mã độc</span></td><td>USB đưa mã độc vào cả những mạng tách biệt Internet (air-gapped).</td></tr>
   <tr><td style="padding-left:0"><span class="tag t-red">Stuxnet</span></td><td>Năm 2010, sâu Stuxnet theo USB vào nhà máy Natanz, phá hỏng máy ly tâm.</td></tr>
  </table>
 </div>
 <div class="col" style="background:var(--tint);border-radius:14px;padding:44px 48px">
  <div class="note" style="font-size:22px">Trên Windows Home / Pro</div>
  <p style="font-size:34px;font-weight:600;margin-top:14px;line-height:1.35">Không có công cụ chặn USB đi kèm. GPO và Intune chỉ tiện trên bản Enterprise, cần máy chủ quản lý.</p>
  <p style="margin-top:34px" class="muted">Cần 1 phần mềm tự chạy trên từng máy: tự chặn ổ USB, không làm ảnh hưởng chuột, bàn phím, và người dùng không tự tắt được.</p>
 </div>
</div>'''))

# 3. Mục tiêu
S.append(trang(3, 0, "4 mục tiêu, mỗi mục đo được bằng kiểm thử", f'''
<table>
<tr><th style="width:300px">Đo bằng</th><th>Mục tiêu</th></tr>
<tr><td><span class="num" style="font-size:54px">≤ 2</span> <span class="muted">giây</span></td><td><b>Chặn ngay khi cắm.</b> Ổ USB, ổ cứng di động, đầu đọc thẻ không hiện trong This PC.</td></tr>
<tr><td><span class="num" style="font-size:54px">0</span> <span class="muted">gián đoạn</span></td><td><b>Không đụng chuột, bàn phím.</b> Chỉ chặn thiết bị lưu trữ (lớp USB 08).</td></tr>
<tr><td><span class="num mono" style="font-size:46px">1052 · 5</span></td><td><b>Không tắt được.</b> Admin dừng dịch vụ nhận lỗi 1052, người dùng thường nhận lỗi 5; bị kill thì Windows tự chạy lại.</td></tr>
<tr><td><span class="num" style="font-size:54px">3</span> <span class="muted">chế độ</span></td><td><b>Quản trị có mật khẩu.</b> Chặn tất cả, chỉ cho phép danh sách, tạm dừng có hạn giờ.</td></tr>
</table>'''))

# 4. Kiến trúc 3 tầng
def cong(x, ten, mo_ta, mau="var(--accent)"):
    return f'''<g transform="translate({x},0)">
<rect x="0" y="60" width="300" height="230" rx="12" fill="#fff" stroke="{mau}" stroke-width="3"/>
<text x="24" y="110" font-size="26" font-weight="700" fill="{mau}">{ten}</text>
{"".join(f'<text x="24" y="{150+i*34}" font-size="23" fill="#15202c">{e(t)}</text>' for i, t in enumerate(mo_ta))}
</g>'''

S.append(trang(4, 1, "3 lớp chặn nối tiếp: lọt lớp này còn lớp sau", f'''
<svg width="1680" height="600" viewBox="0 0 1650 560" font-family="Be Vietnam Pro">
 <defs><marker id="a" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="#15202c"/></marker></defs>
 <g transform="translate(0,0)">
  <rect x="0" y="120" width="150" height="110" rx="14" fill="#15202c"/>
  <text x="75" y="185" font-size="26" font-weight="700" fill="#fff" text-anchor="middle">USB</text>
 </g>
 <line x1="150" y1="175" x2="200" y2="175" stroke="#15202c" stroke-width="3" marker-end="url(#a)"/>
 {cong(210, "Tầng 3 · Cài thiết bị", ["Cấm cài mọi thiết bị", "lớp lưu trữ (08)", "Chuột, phím: lớp khác"])}
 <line x1="510" y1="175" x2="560" y2="175" stroke="#15202c" stroke-width="3" marker-end="url(#a)"/>
 {cong(570, "Tầng 1 · Driver", ["Tắt USBSTOR,", "UASPStor", "Start = 4"])}
 <line x1="870" y1="175" x2="920" y2="175" stroke="#15202c" stroke-width="3" marker-end="url(#a)"/>
 {cong(930, "Tầng 2 · Chính sách", ["Removable Storage", "Deny_All = 1", "Cấm đọc, ghi, chạy"])}
 <line x1="1230" y1="175" x2="1300" y2="175" stroke="#c0392b" stroke-width="3" stroke-dasharray="8 6"/>
 <rect x="1310" y="120" width="330" height="110" rx="14" fill="#fbeceb"/>
 <text x="1475" y="168" font-size="26" font-weight="700" fill="#c0392b" text-anchor="middle">Không có ổ đĩa</text>
 <text x="1475" y="202" font-size="22" fill="#c0392b" text-anchor="middle">trong This PC</text>
 <rect x="210" y="360" width="1020" height="150" rx="12" fill="#f2f4f7"/>
 <text x="240" y="408" font-size="24" font-weight="700" fill="#15202c">Dịch vụ UsbGuard (chạy dưới quyền SYSTEM, kiểm tra mỗi 1 giây)</text>
 <text x="240" y="448" font-size="22" fill="#5d6876">Thấy USB lọt qua thì gỡ ngay (eject), ổ đang mở tệp thì buộc tháo.</text>
 <text x="240" y="482" font-size="22" fill="#5d6876">Ai sửa Registry để mở lại thì tự đặt lại trong khoảng 1 giây.</text>
 <path d="M720,360 L720,300" stroke="#5d6876" stroke-width="2" stroke-dasharray="6 6"/>
</svg>
<p class="note" style="margin-top:6px">Mã nguồn: {SO_TEP} tệp C#, {vn(SO_DONG)} dòng, .NET Framework 4.8 có sẵn trên Windows 10, 11.</p>'''))

# 5. 3 chế độ
S.append(trang(5, 1, "3 chế độ, cùng màu với phần mềm", f'''
<div class="row" style="gap:40px;height:auto">
 <div class="col" style="border-top:10px solid var(--red);background:var(--red-2);border-radius:12px;padding:36px">
  <div style="font-size:34px;font-weight:700;color:var(--red)">Chặn tất cả</div>
  <div class="note" style="margin-top:6px">Mặc định sau khi cài</div>
  <p style="margin-top:26px">Mọi USB lưu trữ cắm vào đều bị chặn. Bật đủ 3 tầng.</p>
 </div>
 <div class="col" style="border-top:10px solid var(--green);background:var(--green-2);border-radius:12px;padding:36px">
  <div style="font-size:34px;font-weight:700;color:var(--green)">Danh sách cho phép</div>
  <div class="note" style="margin-top:6px">Có ít nhất 1 USB được phép</div>
  <p style="margin-top:26px">Chỉ USB đúng số serial trong danh sách dùng được, USB khác vẫn bị gỡ.</p>
 </div>
 <div class="col" style="border-top:10px solid var(--amber);background:var(--amber-2);border-radius:12px;padding:36px">
  <div style="font-size:34px;font-weight:700;color:var(--amber)">Tạm dừng</div>
  <div class="note" style="margin-top:6px">1 đến 1.440 phút</div>
  <p style="margin-top:26px">Mở mọi USB để chép dữ liệu. Hết giờ tự quay về chế độ cũ, hoặc bấm “Bật lại chặn”.</p>
 </div>
</div>
<div style="display:flex;align-items:center;gap:22px;margin-top:60px;font-size:26px">
 <span class="tag t-red" style="font-size:24px">Chặn tất cả</span><span class="muted">thêm 1 USB vào danh sách →</span>
 <span class="tag t-green" style="font-size:24px">Danh sách cho phép</span><span class="muted">xoá hết danh sách → quay về chặn tất cả</span></div>
<div style="display:flex;align-items:center;gap:22px;margin-top:26px;font-size:26px">
 <span class="muted">Từ chế độ nào cũng có thể</span><span class="tag t-amber" style="font-size:24px">Tạm dừng</span><span class="muted">→ hết giờ tự quay về chế độ trước đó</span></div>
<p class="note" style="position:absolute;bottom:0">Đổi chế độ cần mật khẩu quản trị, không phải khởi động lại dịch vụ hay máy.</p>'''))

# 6. Không tắt được
S.append(trang(6, 1, "Thử tắt UsbGuard: bị chặn hoặc tự chạy lại", f'''
<div class="term">
<div><span class="c"># Administrator</span></div>
<div><span class="p">&gt;</span> sc stop UsbGuard</div>
<div class="r">[SC] ControlService FAILED 1052: dịch vụ không nhận lệnh dừng</div>
<div style="margin-top:18px"><span class="c"># Người dùng thường</span></div>
<div><span class="p">&gt;</span> sc stop UsbGuard &nbsp;·&nbsp; sc config &nbsp;·&nbsp; sc delete</div>
<div class="r">[SC] OpenService FAILED 5: Access is denied</div>
<div style="margin-top:18px"><span class="c"># Administrator ép tắt tiến trình</span></div>
<div><span class="p">&gt;</span> taskkill /F /IM UsbGuard.exe</div>
<div class="y">Windows chạy lại dịch vụ sau {giay(K22['chay_lai_ms'])} (Server 2022), {giay(K25['chay_lai_ms'])} (Server 2025)</div>
<div style="margin-top:18px"><span class="c"># Admin vào services.msc đổi Startup type thành Disabled</span></div>
<div><span class="p">&gt;</span> sc config UsbGuard start= disabled</div>
<div class="r">[SC] ChangeServiceConfig FAILED 5: Access is denied</div>
<div style="margin-top:18px"><span class="c"># Sửa Registry để mở USB</span></div>
<div><span class="p">&gt;</span> reg add ...\\USBSTOR /v Start /d 3</div>
<div class="y">Dịch vụ đặt lại Start = 4 sau {giay(K22['tu_sua_ms'])} (2022), {giay(K25['tu_sua_ms'])} (2025)</div>
<div style="margin-top:18px"><span class="c"># Cách duy nhất</span></div>
<div><span class="p">&gt;</span> UsbGuard.exe uninstall <span class="g">[đúng mật khẩu]</span></div>
</div>
<p class="note" style="margin-top:20px">Số đo lấy từ kiểm thử tích hợp. Admin có mật khẩu vẫn gỡ được: đây là phần mềm quản lý thiết bị công khai, không phải rootkit.</p>'''))

# 7. Mật khẩu
khoa = [(5, 30), (6, 60), (7, 120), (8, 240), (9, 480), (10, 960), (11, 1920), (12, 3600)]
bars = ""
for i, (lan, s) in enumerate(khoa):
    h = 40 + int(320 * (s / 3600) ** 0.5)
    x = i * 98
    nhan = f"{s} giây" if s < 60 else (f"{s // 60} phút" if s < 3600 else "1 giờ")
    bars += f'<rect x="{x}" y="{400 - h}" width="70" height="{h}" rx="6" fill="{"#c0392b" if s == 3600 else "#1c4f9c"}"/>'
    bars += f'<text x="{x + 35}" y="{390 - h}" font-size="19" text-anchor="middle" fill="#15202c">{nhan}</text>'
    bars += f'<text x="{x + 35}" y="436" font-size="20" text-anchor="middle" fill="#5d6876">{lan}</text>'
S.append(trang(7, 1, "Mật khẩu: khó dò offline, khó đoán online", f'''
<div class="row">
 <div class="col">
  <table>
   <tr><td style="padding-left:0;width:250px" class="muted">Cách băm</td><td><b>PBKDF2-SHA256</b>, {vn(600000)} vòng, muối ngẫu nhiên 16 byte</td></tr>
   <tr><td style="padding-left:0" class="muted">Nơi lưu</td><td class="mono" style="font-size:22px">HKLM\\SOFTWARE\\UsbGuard</td></tr>
   <tr><td style="padding-left:0" class="muted">Ai đọc được</td><td>Chỉ SYSTEM và Administrators. Người dùng thường không lấy được mã băm.</td></tr>
   <tr><td style="padding-left:0" class="muted">So sánh</td><td>Thời gian hằng, không lộ qua thời gian phản hồi</td></tr>
   <tr><td style="padding-left:0" class="muted">Bản cũ</td><td>Mã băm SHA1 tự nâng cấp ở lần đăng nhập đúng kế tiếp</td></tr>
  </table>
 </div>
 <div class="col">
  <div style="font-size:26px;font-weight:600">Thời gian khoá sau mỗi lần nhập sai</div>
  <svg width="800" height="470" viewBox="-10 0 800 470" font-family="Be Vietnam Pro" style="margin-top:20px">{bars}
   <text x="380" y="466" font-size="19" text-anchor="middle" fill="#5d6876">Lần nhập sai liên tiếp</text></svg>
  <p class="note">Đếm trong HKLM: tắt mở phần mềm hay khởi động lại máy không xoá được. Áp dụng cho giao diện, dòng lệnh và trình gỡ.</p>
 </div>
</div>'''))

# 8. Gỡ cài đặt
buoc = [("Xác thực", "Quyền Admin (UAC) và đúng mật khẩu"),
        ("Báo dừng", "Ghi cờ Uninstalling = 1, dịch vụ tự dừng"),
        ("Chờ", "Tối đa 20 giây tới khi STOPPED"),
        ("Trả lại", "USBSTOR Start = 3, xoá Deny_All, bật lại USB bị chặn"),
        ("Dọn", "Xoá khoá Registry và thư mục cài")]
o = "".join(f'''<div style="flex:1;position:relative">
 <div style="width:64px;height:64px;border-radius:50%;background:{'var(--green)' if i == 4 else 'var(--accent)'};color:#fff;font-size:28px;font-weight:700;display:flex;align-items:center;justify-content:center;position:relative;z-index:2">{i + 1}</div>
 <div style="font-size:32px;font-weight:700;margin-top:26px">{t}</div>
 <p style="margin-top:10px;padding-right:30px" class="muted">{m}</p></div>''' for i, (t, m) in enumerate(buoc))
S.append(trang(8, 1, "Gỡ cài đặt: 5 bước, máy trở về như chưa cài", f'''
<div style="position:relative;display:flex;margin-top:40px">
 <div style="position:absolute;left:32px;right:20%;top:31px;height:3px;background:var(--line)"></div>{o}
</div>
<p class="note" style="position:absolute;bottom:0">Chỉ xoá đúng mục do UsbGuard tạo, không đụng chính sách USB của quản trị viên đặt từ trước. Gỡ xong trong {giay(K22['go_ms'])} (Server 2022).</p>'''))

# 9. Giao diện
S.append(trang(9, 2, "Giao diện: nhìn màu là biết máy đang ở chế độ nào", f'''
<div class="row">
 <div style="flex:1.35"><img class="shot" src="{img(kq.anh_gui())}" style="width:100%"></div>
 <div class="col">
  <table>
   <tr><td style="padding-left:0"><b>Thanh màu</b><br><span class="muted">Đỏ chặn tất cả, xanh danh sách cho phép, vàng tạm dừng</span></td></tr>
   <tr><td style="padding-left:0"><b>Cho phép 1 USB</b><br><span class="muted">Chọn USB đang cắm, bấm 1 nút. Không cần rút ra cắm lại</span></td></tr>
   <tr><td style="padding-left:0"><b>3 tab</b><br><span class="muted">USB đang cắm, danh sách cho phép, nhật ký</span></td></tr>
   <tr><td style="padding-left:0"><b>Mọi thao tác hỏi mật khẩu</b></td></tr>
  </table>
 </div>
</div>'''))

# 10. Người dùng thấy gì
S.append(trang(10, 2, "Cắm USB lạ: 1 thông báo, ổ không hiện", f'''
<div class="row">
 <div style="flex:1.5"><img class="shot" src="{img(str(HERE / '_anh' / 'e10-cat.png'))}" style="width:100%"></div>
 <div class="col">
  <p>Thông báo bằng tiếng Việt, ghi đúng tên thiết bị và cách xin cấp quyền.</p>
  <p style="margin-top:26px" class="muted">Ảnh chụp từ kiểm thử E10 trên Windows 10: máy đã cho phép 1 USB, cắm thêm USB khác thì USB đó bị chặn.</p>
 </div>
</div>'''))

# 11. Bộ cài
_bc = [("Chọn thư mục", "Mặc định Program Files"), ("Đặt mật khẩu", "Nhập 2 lần, ít nhất 8 ký tự"), ("Cài dịch vụ", "Chạy ngay, chặn USB từ lúc này"), ("Xong", "Lối tắt Start Menu, Desktop")]
BUOC_CAI = '<div style="display:flex;gap:24px">' + "".join(f'''<div style="flex:1;background:var(--tint);border-radius:12px;padding:40px 36px;min-height:300px">
 <div style="font-size:22px;color:var(--accent);font-weight:700">Bước {i + 1}</div>
 <div style="font-size:34px;font-weight:700;margin-top:10px">{a}</div>
 <p class="muted" style="margin-top:8px">{b}</p></div>''' for i, (a, b) in enumerate(_bc)) + '</div>'
S.append(trang(11, 2, "Bộ cài setup.exe: cài như phần mềm bình thường", f'''
{BUOC_CAI}
<div class="row" style="height:auto;margin-top:80px;gap:40px">
 <div class="col"><b style="font-size:26px">Tiếng Việt</b><p class="note">Inno Setup 6, lối tắt Start Menu, Desktop, Apps &amp; features</p></div>
 <div class="col"><b style="font-size:26px">Đặt mật khẩu khi cài</b><p class="note">2 ô nhập, tối thiểu 8 ký tự, không lộ trên dòng lệnh</p></div>
 <div class="col"><b style="font-size:26px">Cài hàng loạt</b><p class="note mono" style="font-size:20px">/VERYSILENT /ADMINPW=...</p></div>
</div>'''))

# 12. CLI
S.append(trang(12, 2, "Dòng lệnh cho bộ phận IT", f'''
<div class="term" style="font-size:27px;line-height:1.8">
<div><span class="p">&gt;</span> UsbGuard.exe status <span class="c">            # chế độ, dịch vụ, danh sách cho phép</span></div>
<div><span class="p">&gt;</span> UsbGuard.exe devices <span class="c">           # USB đang cắm, trạng thái, cổng</span></div>
<div><span class="p">&gt;</span> UsbGuard.exe whitelist add &lt;id&gt; <span class="c">  # cho phép 1 USB</span></div>
<div><span class="p">&gt;</span> UsbGuard.exe pause 30 <span class="c">           # tạm dừng 30 phút</span></div>
<div><span class="p">&gt;</span> UsbGuard.exe resume <span class="c">             # bật lại chặn ngay</span></div>
<div><span class="p">&gt;</span> UsbGuard.exe passwd <span class="c">             # đổi mật khẩu</span></div>
<div><span class="p">&gt;</span> UsbGuard.exe install | uninstall</div>
</div>
<p class="note" style="margin-top:22px">status và devices ai cũng xem được; các lệnh còn lại cần quyền Admin và mật khẩu.</p>'''))

# 13. Chiến lược kiểm thử
cap = [(f"{U22['dat']}/{U22['tong']}", "Unit test", "Băm mật khẩu, khoá chống dò, so khớp danh sách", "Windows Server 2022, 2025"),
       (f"{K22['dat']}/{K22['tong']}", "Tích hợp", "Cài thật, thử tắt, sửa Registry, đo RAM, CPU, gỡ cài", "Windows Server 2022, 2025"),
       (f"{W10['dat']}/{W10['tong']}", "Cắm USB thật", "Cài bằng setup.exe rồi cắm, rút USB vào máy ảo", "Windows 10, Windows 11"),
       ("7/7", "Máy thật", "Thành viên nhóm thử với USB vật lý", "Bản 1.1.0")]
rows = "".join(f'''<tr><td style="padding-left:0;width:260px"><span class="num ok" style="font-size:64px">{a}</span></td>
<td><b>{b}</b><br><span class="muted">{c}</span></td><td class="muted" style="width:360px">{d}</td></tr>''' for a, b, c, d in cap)
S.append(trang(13, 3, "Kiểm thử 4 cấp, tất cả đều đạt", f'''<table>{rows}</table>
<p class="note" style="margin-top:22px">Chạy tự động trên GitHub Actions. Số liệu trong slide đọc thẳng từ tệp kết quả của lần chạy cuối.</p>'''))

# 14. Tích hợp Server
def o_so(so, don_vi, mo_ta):
    return f'''<div style="border-top:3px solid var(--ink);padding-top:22px">
<div><span class="num" style="font-size:76px">{so}</span> <span style="font-size:28px" class="muted">{don_vi}</span></div>
<div class="note" style="margin-top:8px">{mo_ta}</div></div>'''
S.append(trang(14, 3, f"Windows Server 2022, 2025: {K22['dat']}/{K22['tong']} ca đạt", f'''
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:48px">
 {o_so(f"{K22['dat']}/{K22['tong']}", "ca", "Đạt trên cả 2 bản Windows Server")}
 {o_so("1052", "mã lỗi", "Admin gửi sc stop, dịch vụ vẫn chạy")}
 {o_so(vn(max(K22['ram_max_mb'], K25['ram_max_mb'])), "MB RAM", "Cao nhất khi chạy (yêu cầu dưới 50 MB)")}
 {o_so(vn(max(K22['cpu_pct'], K25['cpu_pct']), 2), "% CPU", "Trung bình (yêu cầu dưới 1%)")}
</div>
<table style="margin-top:56px">
<tr><th style="padding-left:0">Đo trong kiểm thử tích hợp</th><th style="width:300px">Server 2022</th><th style="width:300px">Server 2025</th></tr>
<tr><td style="padding-left:0">Bị taskkill, dịch vụ chạy lại sau</td><td>{giay(K22['chay_lai_ms'])}</td><td>{giay(K25['chay_lai_ms'])}</td></tr>
<tr><td style="padding-left:0">Sửa Registry, tự đặt lại sau</td><td>{giay(K22['tu_sua_ms'])}</td><td>{giay(K25['tu_sua_ms'])}</td></tr>
<tr><td style="padding-left:0">Gỡ cài đặt xong sau</td><td>{giay(K22['go_ms'])}</td><td>{giay(K25['go_ms'])}</td></tr>
</table>'''))

# 15. Cắm USB thật
chon = [("E03", "Chặn tất cả: cắm USB không có ổ, không ghi được"),
        ("E05", "Chuột, bàn phím vẫn chạy"),
        ("E06", "Tạm dừng: USB đang cắm dùng được ngay"),
        ("E10", "Danh sách cho phép: USB lạ bị gỡ, USB được phép dùng được"),
        ("E14", "Kill dịch vụ khi đang cắm: chạy lại, USB vẫn bị chặn"),
        ("E16", "Gỡ đúng mật khẩu: USB dùng lại được"),
        ("E19", "USB đã bị Windows tháo: cho phép là tự hiện lại")]
def dau(d, m):
    return '<span class="ok">✓</span>' if d["theo_ma"][m]["dat"] else '<span style="color:var(--red)">✗</span>'
rows = "".join(f'<tr><td class="mono muted" style="padding-left:0">{m}</td><td>{t}</td><td style="text-align:center">{dau(W10, m)}</td><td style="text-align:center">{dau(W11, m)}</td></tr>' for m, t in chon)
S.append(trang(15, 3, f"Cắm USB thật: {W10['dat']}/{W10['tong']} ca đạt trên Windows 10 và 11", f'''
<table><tr><th style="padding-left:0;width:110px">Ca</th><th>Kịch bản (7 trong {W10['tong']} ca)</th><th style="width:190px;text-align:center">Windows 10</th><th style="width:190px;text-align:center">Windows 11</th></tr>{rows}</table>
<p class="note" style="margin-top:18px">Máy ảo QEMU, USB cắm nóng bằng lệnh device_add, cài bằng đúng setup.exe gửi người dùng.</p>'''))

# 16. 3 lỗi tìm ra
loi = [("USB đang mở tệp", "Windows từ chối tháo khi bật lại chặn", "Khoá và tháo ổ trước rồi mới eject"),
       ("pnputil trả mã 3010", "Thiết bị bị tắt vĩnh viễn, cho phép lại cũng không lên", "Ghi nhận 3010, bỏ chặn thì bật lại thiết bị"),
       ("USB cắm lần đầu lúc đang chặn", "Windows ghi “cài thất bại”, cho phép xong vẫn không có ổ", "Xoá nút thiết bị rồi quét lại")]
rows = "".join(f'<tr><td style="padding-left:0"><b>{a}</b></td><td class="muted">{b}</td><td>{c}</td></tr>' for a, b, c in loi)
S.append(trang(16, 3, "3 lỗi chỉ lộ ra khi cắm USB thật, đã sửa", f'''
<table><tr><th style="padding-left:0;width:420px">Tình huống</th><th>Trước khi sửa</th><th style="width:520px">Cách sửa</th></tr>{rows}</table>
<p class="note" style="margin-top:22px">Kiểm thử tích hợp trên Windows Server không có USB nên không thấy 3 lỗi này. Đây là lý do thêm cấp kiểm thử cắm USB.</p>'''))

# 17. Máy thật
mt = [("Cài, tự khởi động cùng Windows", "Dịch vụ RUNNING sau khi khởi động lại"),
      ("Chặn USB lưu trữ", "Có thông báo, không có ổ trong This PC"),
      ("Tạm dừng, bật lại, cho phép", "USB dùng được khi tạm dừng hoặc được cho phép"),
      ("Administrator gửi sc stop", "Lỗi 1052, dịch vụ vẫn chạy"),
      ("Người dùng thường gửi sc stop", "Lỗi 5, Access is denied"),
      ("Chuột và bàn phím USB", "Vẫn dùng được khi chặn tất cả"),
      ("Gỡ cài đặt", "Sai mật khẩu bị từ chối, gỡ xong USB dùng lại được")]
rows = "".join(f'<tr><td style="padding-left:0"><span class="ok">✓</span>&nbsp; {a}</td><td class="muted">{b}</td></tr>' for a, b in mt)
S.append(trang(17, 3, "Máy Windows thật, USB thật: 7/7 kịch bản đạt", f'''
<table><tr><th style="padding-left:0;width:760px">Kịch bản (bản 1.1.0)</th><th>Quan sát được</th></tr>{rows}</table>
<p class="note" style="margin-top:18px">Thành viên nhóm tự thử và gửi báo cáo. Các góp ý kèm theo dẫn tới bản 1.2.</p>'''))

# 18. Phản hồi -> 1.2
S.append(trang(18, 3, "Góp ý từ máy thật: bản 1.2 và 1.2.1", f'''
<div class="row" style="gap:48px;height:auto">
 <div class="col" style="background:var(--red-2);border-radius:14px;padding:34px 38px">
  <span class="tag" style="background:#fff;color:var(--red)">Bản 1.1</span>
  <p style="margin-top:18px">USB bị chặn khi đang cắm → Windows “tháo an toàn” (mã 47) → bấm cho phép → <b>ổ không hiện, phải rút ra cắm lại</b>. USB còn biến khỏi danh sách.</p>
 </div>
 <div class="col" style="background:var(--green-2);border-radius:14px;padding:34px 38px">
  <span class="tag" style="background:#fff;color:var(--green)">Bản 1.2</span>
  <p style="margin-top:18px">Nhớ hub và số cổng của USB → khi được phép, <b>tự “rút ra cắm lại” cổng đó bằng phần mềm</b> (IOCTL_USB_HUB_CYCLE_PORT). Danh sách hiện “Bị chặn (đã tháo)”.</p>
 </div>
</div>
<table style="margin-top:44px">
 <tr><td style="padding-left:0;width:300px" class="muted">Kiểm chứng</td><td>Tái hiện lỗi trong máy ảo trước (E19, E20 không đạt), sửa xong đạt {W10['dat']}/{W10['tong']} trên Windows 10 và {W11['dat']}/{W11['tong']} trên Windows 11</td></tr>
 <tr><td style="padding-left:0" class="muted">Bản 1.2.1</td><td>Admin đổi dịch vụ sang Disabled bị từ chối, sửa Registry thì tự trả lại (TC38 đến TC40). Gỡ cài đặt khi USB đang cắm: USB dùng được ngay (E21)</td></tr>
</table>'''))

# 19. Đáp ứng yêu cầu
yc = [("Chặn USB trong 2 giây", "E03, E10 đạt trên Windows 10, 11"),
      ("Không ảnh hưởng chuột, phím", "E05 đạt"),
      ("3 chế độ hoạt động", f"{K22['dat']}/{K22['tong']} ca tích hợp"),
      ("Mật khẩu quản trị", f"{U22['dat']}/{U22['tong']} unit test, TC35 đến TC37"),
      ("Không tắt được", "Lỗi 1052 và lỗi 5, tự chạy lại khi bị kill"),
      ("Nhẹ: CPU dưới 1%, RAM dưới 50 MB", f"RAM {vn(min(K22['ram_tb_mb'], K25['ram_tb_mb']))} đến {vn(max(K22['ram_max_mb'], K25['ram_max_mb']))} MB, CPU {vn(max(K22['cpu_pct'], K25['cpu_pct']), 2)}%")]
rows = "".join(f'<tr><td style="padding-left:0"><b>{a}</b></td><td class="muted">{b}</td><td><span class="tag t-green">Đáp ứng</span></td></tr>' for a, b in yc)
S.append(trang(19, 4, "6/6 yêu cầu của đề tài đã đáp ứng", f'''
<table><tr><th style="padding-left:0;width:620px">Yêu cầu</th><th>Bằng chứng</th><th style="width:200px"></th></tr>{rows}</table>'''))

# 20. Hạn chế + cảm ơn
S.append(trang(20, 4, "Còn thiếu gì, và làm tiếp ra sao", f'''
<div class="row" style="gap:64px;height:auto">
 <div class="col">
  <div style="font-size:26px;font-weight:700;color:var(--red)">Hạn chế</div>
  <ul style="margin:18px 0 0 30px">
   <li>Chưa có chữ ký số: trình duyệt, SmartScreen còn cảnh báo khi tải</li>
   <li>Chưa chặn điện thoại (MTP), ổ CD/DVD, Bluetooth</li>
   <li>Admin rành hệ thống vẫn vượt được qua Safe Mode</li>
   <li>Mới thử máy thật với ít loại USB</li>
  </ul>
 </div>
 <div class="col">
  <div style="font-size:26px;font-weight:700;color:var(--accent)">Hướng phát triển</div>
  <ul style="margin:18px 0 0 30px">
   <li>Mua chứng chỉ ký mã</li>
   <li>Máy chủ quản lý tập trung nhiều máy</li>
   <li>Driver lọc ở chế độ nhân</li>
   <li>Xác thực 2 yếu tố cho quản trị viên</li>
  </ul>
 </div>
</div>
<div style="position:absolute;bottom:0;left:0;right:0;border-top:1px solid var(--line);padding-top:30px;display:flex;justify-content:space-between;align-items:flex-end">
 <div><div style="font-size:44px;font-weight:700">Cảm ơn thầy cô đã lắng nghe</div><div class="note" style="margin-top:8px">Rất mong nhận được góp ý để hoàn thiện sản phẩm.</div></div>
 <div class="note" style="text-align:right">Phạm Văn Hưng · 3120410225<br>github.com/hungphamwp/usbguard</div>
</div>'''))

assert len(S) == 20, len(S)


def main():
    from PIL import Image
    (HERE / "_anh").mkdir(exist_ok=True)
    Image.open(HINH / "e10-whitelist-chan-usb-la.png").crop((330, 250, 970, 570)).save(HERE / "_anh" / "e10-cat.png")
    out = HERE / "SLIDE-UsbGuard.html"
    out.write_text(f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>UsbGuard slide</title><style>{CSS}</style></head><body>{"".join(S)}</body></html>', encoding="utf-8")
    pdf = HERE / "SLIDE-UsbGuard.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    f"--print-to-pdf={pdf}", out.as_uri()], check=True, capture_output=True)
    # PPTX: mỗi slide 1 ảnh full HD (để chiếu trên máy không có font)
    tmp = HERE / "_png"
    shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir()
    subprocess.run(["pdftoppm", "-scale-to", "1920", "-png", str(pdf), str(tmp / "s")], check=True)
    from pptx import Presentation
    from pptx.util import Inches
    prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    for f in sorted(tmp.glob("s-*.png")):
        sl = prs.slides.add_slide(prs.slide_layouts[6])
        sl.shapes.add_picture(str(f), 0, 0, prs.slide_width, prs.slide_height)
    prs.save(HERE / "SLIDE-UsbGuard.pptx")
    n = len(list(tmp.glob("s-*.png")))
    print("Xong:", pdf, n, "trang")


if __name__ == "__main__":
    main()

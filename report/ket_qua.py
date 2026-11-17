# -*- coding: utf-8 -*-
"""
Đọc toàn bộ số liệu kiểm thử từ thư mục tests/ket-qua/ (json, md, trx).
Báo cáo và slide chỉ lấy số từ đây: thay các tệp kết quả bằng lần chạy mới rồi chạy lại script là số tự cập nhật.
Thiếu tệp hoặc thiếu khoá thì dừng và báo lỗi, không dùng giá trị mặc định.
"""
import glob
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
KQ = ROOT / "tests" / "ket-qua"
E2E = KQ / "e2e-usb"
SRC = ROOT / "src"


def _loi(msg):
    raise SystemExit(f"[LỖI] {msg}")


def _tim(thu_muc, mau):
    kq = sorted(glob.glob(str(thu_muc / mau)))
    if not kq:
        _loi(f"Không tìm thấy tệp kết quả {thu_muc.name}/{mau}")
    return pathlib.Path(kq[0])


def _json(path):
    try:
        return json.load(open(path, encoding="utf-8-sig"))
    except Exception as ex:
        _loi(f"Không đọc được {path.name}: {ex}")


def _co(d, khoa, nguon):
    if khoa not in d:
        _loi(f"Thiếu khoá '{khoa}' trong {nguon}")
    return d[khoa]


def _sap_xep_ma(ca):
    return sorted(ca, key=lambda c: (re.sub(r"\d+", "", c["id"]), int(re.sub(r"\D", "", c["id"]))))


def _ca(d, nguon):
    ds = _co(d, "ca", nguon)
    for c in ds:
        for k in ("id", "ten", "dat"):
            if k not in c:
                _loi(f"Ca kiểm thử thiếu khoá '{k}' trong {nguon}")
    return _sap_xep_ma(ds)


def tich_hop(ver):
    """Kết quả kiểm thử tích hợp trên Windows Server `ver` (2022 hoặc 2025)."""
    f = _tim(KQ, f"integration-*{ver}*.json")
    d = _json(f)
    for k in ("he_dieu_hanh", "dat", "tong", "tu_sua_ms", "chay_lai_ms", "ram_tb_mb", "ram_max_mb", "cpu_pct"):
        _co(d, k, f.name)
    d["ca"] = _ca(d, f.name)
    d["_tep"] = f.name
    d["theo_ma"] = {c["id"]: c for c in d["ca"]}
    md = f.with_suffix(".md")
    if not md.exists():
        _loi(f"Thiếu tệp {md.name}")
    d["_md"] = open(md, encoding="utf-8-sig").read()
    m = re.search(r"TC29 .*?mất (\d+) ms", d["_md"])
    if not m:
        _loi(f"Không tìm thấy thời gian gỡ cài đặt (TC29) trong {md.name}")
    d["go_ms"] = int(m.group(1))
    return d


def e2e(ver):
    """Kết quả kiểm thử cắm USB thật trên Windows `ver` (10 hoặc 11)."""
    f = _tim(E2E, f"e2e-usb-*Windows-{ver}-*.json")
    d = _json(f)
    for k in ("he_dieu_hanh", "phien_ban", "dat", "tong"):
        _co(d, k, f.name)
    d["ca"] = _ca(d, f.name)
    d["_tep"] = f.name
    d["theo_ma"] = {c["id"]: c for c in d["ca"]}
    d["anh_dir"] = E2E / f"anh-windows-{ver}"
    return d


def unit(ver):
    """Kết quả unit test (xUnit) đọc từ tệp .trx. Trả về tổng, đạt và danh sách (tên, đạt)."""
    f = _tim(KQ, f"unit-*{ver}*.trx")
    try:
        root = ET.parse(f).getroot()
    except Exception as ex:
        _loi(f"Không đọc được {f.name}: {ex}")
    ns = {"t": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}
    ca = []
    for r in root.findall(".//t:UnitTestResult", ns):
        ca.append((r.get("testName").split(".")[-1], r.get("outcome") == "Passed"))
    c = root.find(".//t:Counters", ns)
    if c is None:
        _loi(f"Thiếu thẻ Counters trong {f.name}")
    return {"tong": int(c.get("total")), "dat": int(c.get("passed")), "ca": ca, "_tep": f.name}


def so_ms(chi_tiet, mau=r"(\d+) ms"):
    """Lấy số mili giây đầu tiên trong chuỗi chi tiết của 1 ca."""
    m = re.search(mau, chi_tiet or "")
    return int(m.group(1)) if m else None


def ma_nguon():
    """Số tệp và số dòng mã nguồn C# thật trong src/ (đếm trực tiếp)."""
    ds = sorted(SRC.glob("*.cs"))
    if not ds:
        _loi("Không có tệp .cs trong src/")
    out = []
    for p in ds:
        out.append((p.name, len(open(p, encoding="utf-8-sig").read().splitlines())))
    return out

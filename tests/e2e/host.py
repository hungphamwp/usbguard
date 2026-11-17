"""Chạy trên máy chủ Linux (GitHub Actions): theo dõi yêu cầu cắm/rút USB do máy ảo Windows ghi vào thư mục
chia sẻ, thực hiện bằng QEMU monitor trong container dockur, chụp màn hình máy ảo, chờ tới khi kiểm thử xong."""
import os, subprocess, sys, time, zlib, struct, glob

SHARED, STORAGE, TIMEOUT = sys.argv[1], sys.argv[2], int(sys.argv[3])
SHOTS = os.path.join(SHARED, "anh")
os.makedirs(SHOTS, exist_ok=True)
DEV = {
    "A": ("usbA", "UGBLOCK0001"),
    "B": ("usbB", "UGALLOW0002"),
}

def hmp(*cmds):
    r = subprocess.run(["docker", "exec", "win", "python3", "/oem/hmp.py", *cmds], capture_output=True, text=True, timeout=60)
    out = (r.stdout + r.stderr).strip()
    print(out, flush=True)
    return out

def ppm_to_png(src, dst):
    data = open(src, "rb").read()
    parts, pos = [], 0
    while len(parts) < 4:
        while data[pos:pos+1].isspace(): pos += 1
        if data[pos:pos+1] == b"#":
            pos = data.index(b"\n", pos) + 1; continue
        end = pos
        while not data[end:end+1].isspace(): end += 1
        parts.append(data[pos:end]); pos = end
    pos += 1
    w, h = int(parts[1]), int(parts[2])
    px = data[pos:pos + w * h * 3]
    raw = b"".join(b"\x00" + px[y*w*3:(y+1)*w*3] for y in range(h))
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")
    open(dst, "wb").write(png)

def shot(name):
    os.makedirs(os.path.join(STORAGE, "shots"), exist_ok=True)
    hmp(f"screendump /storage/shots/{name}.ppm")
    time.sleep(1.5)
    src = os.path.join(STORAGE, "shots", f"{name}.ppm")
    if os.path.exists(src):
        ppm_to_png(src, os.path.join(SHOTS, f"{name}.png")); os.remove(src)

def do(cmd):
    p = cmd.split()
    if p[0] == "plug" and p[1] in DEV:
        drv, serial = DEV[p[1]]
        hmp(f"drive_add 0 if=none,id={drv},file=/storage/{drv}.img,format=raw",
            f"device_add usb-storage,bus=ugx.0,drive={drv},id=dev{p[1]},serial={serial},removable=on")
    elif p[0] == "plug" and p[1] == "K":
        hmp("device_add usb-kbd,bus=ugx.0,id=devK")
    elif p[0] == "unplug":
        hmp(f"device_del dev{p[1]}")
        time.sleep(1.5)
    elif p[0] == "shot":
        shot(p[1])
    return "ok"

start, last_note, n_prog = time.time(), 0, 0
done_reqs = set()
while time.time() - start < TIMEOUT:
    for req in sorted(glob.glob(os.path.join(SHARED, "req-*.txt")), key=lambda f: int(f.split("-")[-1][:-4])):
        if req in done_reqs: continue
        try: cmd = open(req, encoding="ascii", errors="ignore").read().strip()
        except OSError: continue
        if not cmd: continue
        print(f"[{int(time.time()-start)}s] yêu cầu: {cmd}", flush=True)
        try: res = do(cmd)
        except Exception as e: res = f"lỗi {e}"
        done_reqs.add(req)
        open(req.replace("req-", "ack-"), "w").write(res)
    if os.path.exists(os.path.join(SHARED, "done.txt")):
        print("KIỂM THỬ XONG:", open(os.path.join(SHARED, "done.txt")).read().strip(), flush=True)
        sys.exit(0)
    if time.time() - last_note > 300:
        last_note = time.time(); n_prog += 1
        log = subprocess.run(["docker", "logs", "--tail", "3", "win"], capture_output=True, text=True).stdout.strip()
        print(f"[{int(time.time()-start)}s] đang chờ máy ảo... {log[-300:]}", flush=True)
        try: shot(f"tien-trinh-{n_prog:02d}")
        except Exception as e: print("không chụp được:", e)
    time.sleep(0.3)
print("HẾT GIỜ CHỜ KIỂM THỬ", flush=True)
sys.exit(1)

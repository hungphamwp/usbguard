# Chạy BÊN TRONG container dockur: gửi lệnh tới QEMU monitor (HMP) ở 127.0.0.1:4444 và in phản hồi.
import socket, sys, time
def talk(cmds):
    s = socket.create_connection(("127.0.0.1", 4444), timeout=10)
    buf = b""
    def until_prompt():
        nonlocal buf
        end = time.time() + 20
        while b"(qemu)" not in buf and time.time() < end:
            try:
                d = s.recv(65536)
                if not d: break
                buf += d
            except socket.timeout:
                break
        out = buf; buf = b""
        return out.decode("utf-8", "replace")
    until_prompt()
    for c in cmds:
        s.sendall((c + "\n").encode())
        r = until_prompt()
        r = r.replace("(qemu)", "").replace(c, "", 1)
        # bỏ ký tự điều khiển terminal
        r = "".join(ch for ch in r if ch == "\n" or ch >= " ").strip()
        print(f"> {c}\n{r}")
    s.close()
talk(sys.argv[1:])

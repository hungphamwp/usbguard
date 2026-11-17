#!/usr/bin/env python3
"""Tạo các hình vẽ kỹ thuật cho báo cáo UsbGuard bằng matplotlib (200 dpi)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Cấu hình font chữ hỗ trợ tiếng Việt có dấu
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Times New Roman', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUT_DIR = os.path.join(os.path.dirname(__file__), "hinh")
os.makedirs(OUT_DIR, exist_ok=True)

# Bảng màu chuẩn báo cáo kỹ thuật
C_NAVY = "#1F4E79"
C_BLUE = "#2E75B6"
C_LIGHT_BLUE = "#D9E2F3"
C_VERY_LIGHT_BLUE = "#F2F7FC"
C_GREEN = "#385723"
C_LIGHT_GREEN = "#E2EFDA"
C_RED = "#C00000"
C_LIGHT_RED = "#FCE4D6"
C_ORANGE = "#ED7D31"
C_YELLOW = "#FFF2CC"
C_GRAY = "#595959"
C_LIGHT_GRAY = "#F2F4F7"
C_DARK = "#262626"


def draw_box(ax, x, y, w, h, title, lines, bg_color=C_LIGHT_BLUE, border_color=C_NAVY, title_color=C_NAVY, title_size=10, text_size=9, radius=0.015):
    """Vẽ một hộp nội dung có bo góc nhẹ và văn bản căn chỉnh."""
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                                 facecolor=bg_color, edgecolor=border_color, linewidth=1.5)
    ax.add_patch(box)
    
    if title:
        ax.text(x + w / 2, y + h - 0.04, title, ha='center', va='top', fontsize=title_size,
                fontweight='bold', color=title_color)
        line_start_y = y + h - 0.09
    else:
        line_start_y = y + h - 0.04
        
    line_spacing = 0.038
    for i, line in enumerate(lines):
        ax.text(x + 0.02, line_start_y - i * line_spacing, line, ha='left', va='top',
                fontsize=text_size, color=C_DARK)


def draw_arrow(ax, x1, y1, x2, y2, label="", color=C_NAVY, lw=1.5, style="->", label_pos=0.5, label_offset=0.02, label_side="top"):
    """Vẽ mũi tên kết nối kèm nhãn."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, shrinkA=0, shrinkB=0))
    if label:
        xm = x1 + (x2 - x1) * label_pos
        ym = y1 + (y2 - y1) * label_pos
        if label_side == "top":
            ax.text(xm, ym + label_offset, label, ha='center', va='bottom', fontsize=8, color=color, fontweight='bold')
        elif label_side == "bottom":
            ax.text(xm, ym - label_offset, label, ha='center', va='top', fontsize=8, color=color, fontweight='bold')
        elif label_side == "right":
            ax.text(xm + label_offset, ym, label, ha='left', va='center', fontsize=8, color=color, fontweight='bold')
        else:
            ax.text(xm - label_offset, ym, label, ha='right', va='center', fontsize=8, color=color, fontweight='bold')


# ==============================================================================
# HÌNH 1: Kiến trúc tổng thể 2 lớp bảo vệ
# ==============================================================================
def ve_hinh1():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Tiêu đề
    ax.text(0.5, 0.96, "KIẾN TRÚC TỔNG THỂ 2 LỚP BẢO VỆ CỦA USBGUARD",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)

    # Khối thiết bị USB cắm vào
    draw_box(ax, 0.05, 0.72, 0.22, 0.17, "Thiết bị USB cắm vào",
             ["- USB Flash Disk (BOT/UAS)", "- Ổ cứng di động USB", "- Thiết bị lưu trữ ngoài"],
             bg_color=C_YELLOW, border_color=C_ORANGE, title_color=C_ORANGE)

    # Khối Lớp 1
    draw_box(ax, 0.35, 0.58, 0.60, 0.32, "LỚP 1: Chặn ở mức Driver & Chính sách (Enforcer)",
             ["• Tắt driver lưu trữ: HKLM\\...\\Services\\USBSTOR (Start = 4)",
              "• Tắt driver UAS: HKLM\\...\\Services\\UASPStor (Start = 4)",
              "• Áp dụng chính sách Group Policy di động: RemovableStorageDevices\\Deny_All = 1",
              "• Cấm quyền truy cập phân lớp đĩa: Deny_Read=1, Deny_Write=1, Deny_Execute=1",
              "-> Ngăn chặn Windows tự động nạp driver lưu trữ ngay từ tầng gốc hệ điều hành."],
             bg_color=C_LIGHT_BLUE, border_color=C_NAVY, title_color=C_NAVY)

    # Khối Lớp 2
    draw_box(ax, 0.35, 0.18, 0.60, 0.34, "LỚP 2: Quét phần cứng & Gỡ an toàn (UsbDisks)",
             ["• Liệt kê giao diện ổ đĩa: SetupAPI (GUID_DEVINTERFACE_DISK)",
              "• Truy vấn thuộc tính bus: IOCTL_STORAGE_QUERY_PROPERTY (BusType = 7 USB)",
              "• So khớp danh sách cho phép (Whitelist) theo VID/PID hoặc số serial",
              "• Gỡ bỏ an toàn: CM_Request_Device_Eject (lên tới nút USB cha, độ sâu <= 2)",
              "• Dự phòng: pnputil /disable-device khi thiết bị bị khóa tệp bởi tiến trình khác",
              "-> Xử lý các thiết bị cắm sẵn trước khi chạy hoặc driver đã nạp."],
             bg_color=C_LIGHT_GREEN, border_color=C_GREEN, title_color=C_GREEN)

    # Khối Điều phối & Giám sát
    draw_box(ax, 0.05, 0.30, 0.22, 0.34, "Điều phối trung tâm\n(Worker Service)",
             ["- WMI Event Watcher:", "  Bắt sự kiện tức thì", "  __InstanceCreationEvent",
              "- Timer định kỳ 2 giây:", "  Kiểm tra bổ trợ", "  Tự sửa Registry",
              "- Điều phối 3 chế độ", "- Phục hồi khi bị kill"],
             bg_color=C_LIGHT_GRAY, border_color=C_GRAY, title_color=C_NAVY)

    # Khối Cảnh báo
    draw_box(ax, 0.05, 0.05, 0.22, 0.18, "Cảnh báo người dùng",
             ["- WTSSendMessage", "- Hộp thoại cảnh báo", "- Ghi nhật ký (Log)"],
             bg_color=C_LIGHT_RED, border_color=C_RED, title_color=C_RED)

    # Mũi tên kết nối
    draw_arrow(ax, 0.27, 0.80, 0.35, 0.80, "Cắm vào", C_NAVY)
    draw_arrow(ax, 0.16, 0.72, 0.16, 0.64, "Sự kiện", C_NAVY)
    draw_arrow(ax, 0.27, 0.50, 0.35, 0.65, "Kích hoạt Lớp 1", C_NAVY)
    draw_arrow(ax, 0.27, 0.40, 0.35, 0.32, "Kích hoạt Lớp 2", C_NAVY)
    draw_arrow(ax, 0.35, 0.25, 0.27, 0.12, "Gỡ thiết bị / Báo động", C_RED)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hinh1_kien_truc_2_lop.png"), dpi=200)
    plt.close()


# ==============================================================================
# HÌNH 2: Sơ đồ thành phần hệ thống
# ==============================================================================
def ve_hinh2():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax.text(0.5, 0.96, "SƠ ĐỒ THÀNH PHẦN HỆ THỐNG VÀ CÁC TỆP MÃ NGUỒN C#",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)

    # Nhóm 1: Giao diện CLI & Quản trị
    draw_box(ax, 0.04, 0.64, 0.28, 0.27, "Thành phần CLI & Quản trị",
             ["• Program.cs: Điểm khởi nhập CLI",
              "• Cli.cs: Xử lý lệnh pause, resume,",
              "  whitelist, passwd, devices",
              "• Password.cs: Nhập mật khẩu ẩn",
              "• Installer.cs: Cài đặt / Gỡ dịch vụ"],
             bg_color=C_LIGHT_BLUE, border_color=C_NAVY)

    # Nhóm 2: Lõi Dịch vụ nền tảng
    draw_box(ax, 0.36, 0.50, 0.30, 0.41, "Lõi Dịch vụ (Windows Service)",
             ["• Worker.cs: ServiceBase, vòng lặp 2s,",
              "  lắng nghe WMI __InstanceCreationEvent,",
              "  điều phối 3 chế độ hoạt động",
              "• Enforcer.cs: Khóa driver & Registry policy",
              "• UsbDisks.cs: Quét SetupAPI, IOCTL,",
              "  gỡ đĩa CM_Request_Device_Eject",
              "• Whitelist.cs: So khớp chuỗi định danh"],
             bg_color=C_VERY_LIGHT_BLUE, border_color=C_BLUE)

    # Nhóm 3: Lưu trữ cấu hình & Bảo mật
    draw_box(ax, 0.70, 0.64, 0.26, 0.27, "Bảo mật & Cấu hình",
             ["• Settings.cs: Lưu HKLM\\SOFTWARE",
              "  (AuthHash, Whitelist, PauseUntil)",
              "• Auth.cs: Băm PBKDF2-SHA1,",
              "  100000 vòng lặp, muối 16 byte",
              "• Reg.cs: Thiết lập DACL an toàn"],
             bg_color=C_LIGHT_GREEN, border_color=C_GREEN, title_color=C_GREEN)

    # Nhóm 4: Tương tác Hệ thống tầng thấp (P/Invoke)
    draw_box(ax, 0.20, 0.08, 0.60, 0.34, "Tương tác Hệ điều hành & API Tầng thấp (Win32 P/Invoke)",
             ["• Native.cs: Khai báo P/Invoke Win32 API:",
              "  - SetupAPI.dll: SetupDiGetClassDevs, SetupDiEnumDeviceInterfaces",
              "  - CfgMgr32.dll: CM_Request_Device_Eject, CM_Get_Parent, CM_Get_Device_ID",
              "  - Kernel32.dll: CreateFile, DeviceIoControl (IOCTL_STORAGE_QUERY_PROPERTY)",
              "  - Wtsapi32.dll: WTSSendMessage, WTSGetActiveConsoleSessionId",
              "• Sys.cs: Thực thi tiến trình phụ trợ (sc.exe, pnputil.exe, taskkill.exe)",
              "• Log.cs: Ghi nhật ký vào ProgramData\\UsbGuard\\usbguard.log và Event Log"],
             bg_color=C_LIGHT_GRAY, border_color=C_GRAY, title_color=C_DARK)

    # Mũi tên tương tác
    draw_arrow(ax, 0.32, 0.75, 0.36, 0.75, "Gọi dịch vụ", C_NAVY)
    draw_arrow(ax, 0.66, 0.75, 0.70, 0.75, "Đọc/Ghi", C_NAVY)
    draw_arrow(ax, 0.50, 0.50, 0.50, 0.42, "P/Invoke API", C_NAVY)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hinh2_so_do_thanh_phan.png"), dpi=200)
    plt.close()


# ==============================================================================
# HÌNH 3: Sơ đồ ca sử dụng (Use Case Diagram)
# ==============================================================================
def ve_hinh3():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax.text(0.5, 0.96, "SƠ ĐỒ CA SỬ DỤNG HỆ THỐNG USBGUARD (USE CASE DIAGRAM)",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)

    # Hộp ranh giới hệ thống UsbGuard
    sys_box = patches.FancyBboxPatch((0.26, 0.05), 0.48, 0.86, boxstyle="round,pad=0,rounding_size=0.02",
                                     facecolor="#FAFAFA", edgecolor=C_NAVY, linewidth=2, linestyle='--')
    ax.add_patch(sys_box)
    ax.text(0.50, 0.88, "HỆ THỐNG USBGUARD 1.0", ha='center', va='center', fontsize=11, fontweight='bold', color=C_NAVY)

    # Actor 1: Người dùng thường (bên trái)
    ax.plot(0.10, 0.70, 'o', markersize=14, color=C_NAVY)
    ax.plot([0.10, 0.10], [0.63, 0.68], color=C_NAVY, lw=2)
    ax.plot([0.06, 0.14], [0.66, 0.66], color=C_NAVY, lw=2)
    ax.plot([0.10, 0.07], [0.63, 0.57], color=C_NAVY, lw=2)
    ax.plot([0.10, 0.13], [0.63, 0.57], color=C_NAVY, lw=2)
    ax.text(0.10, 0.53, "Người dùng\nthông thường", ha='center', va='top', fontsize=9, fontweight='bold', color=C_NAVY)

    # Actor 2: Quản trị viên (bên phải)
    ax.plot(0.90, 0.70, 'o', markersize=14, color=C_RED)
    ax.plot([0.90, 0.90], [0.63, 0.68], color=C_RED, lw=2)
    ax.plot([0.86, 0.94], [0.66, 0.66], color=C_RED, lw=2)
    ax.plot([0.90, 0.87], [0.63, 0.57], color=C_RED, lw=2)
    ax.plot([0.90, 0.93], [0.63, 0.57], color=C_RED, lw=2)
    ax.text(0.90, 0.53, "Quản trị viên\n(Administrator)", ha='center', va='top', fontsize=9, fontweight='bold', color=C_RED)

    # Actor 3: Windows OS / SCM (dưới)
    ax.plot(0.10, 0.25, 's', markersize=16, color=C_GREEN)
    ax.text(0.10, 0.17, "Hệ điều hành\nWindows / SCM", ha='center', va='top', fontsize=9, fontweight='bold', color=C_GREEN)

    # Các use case hình ellipse
    use_cases = [
        ("UC01: Cắm USB và nhận cảnh báo gỡ", 0.79, C_YELLOW, C_ORANGE),
        ("UC02: Cố gắng can thiệp/tắt dịch vụ (bị từ chối)", 0.69, C_LIGHT_RED, C_RED),
        ("UC03: Cài đặt dịch vụ (install)", 0.59, C_LIGHT_BLUE, C_NAVY),
        ("UC04: Gỡ cài đặt với mật khẩu (uninstall)", 0.49, C_LIGHT_BLUE, C_NAVY),
        ("UC05: Tạm dừng / Kích hoạt lại (pause/resume)", 0.39, C_LIGHT_BLUE, C_NAVY),
        ("UC06: Quản lý Whitelist & Quét thiết bị (devices)", 0.29, C_LIGHT_BLUE, C_NAVY),
        ("UC07: Đổi mật khẩu & Xem trạng thái (passwd/status)", 0.19, C_LIGHT_BLUE, C_NAVY),
        ("UC08: Tự khởi động & Phục hồi khi bị kill (sc failure)", 0.09, C_LIGHT_GREEN, C_GREEN),
    ]

    for text, y, bg, border in use_cases:
        ellipse = patches.FancyBboxPatch((0.29, y - 0.035), 0.42, 0.07, boxstyle="round,pad=0,rounding_size=0.035",
                                        facecolor=bg, edgecolor=border, linewidth=1.2)
        ax.add_patch(ellipse)
        ax.text(0.50, y, text, ha='center', va='center', fontsize=8.5, color=C_DARK, fontweight='bold')

    # Kết nối Actor 1
    ax.plot([0.15, 0.29], [0.65, 0.79], color=C_GRAY, lw=1)
    ax.plot([0.15, 0.29], [0.63, 0.69], color=C_GRAY, lw=1)

    # Kết nối Actor 2
    ax.plot([0.85, 0.71], [0.65, 0.59], color=C_GRAY, lw=1)
    ax.plot([0.85, 0.71], [0.63, 0.49], color=C_GRAY, lw=1)
    ax.plot([0.85, 0.71], [0.60, 0.39], color=C_GRAY, lw=1)
    ax.plot([0.85, 0.71], [0.57, 0.29], color=C_GRAY, lw=1)
    ax.plot([0.85, 0.71], [0.54, 0.19], color=C_GRAY, lw=1)

    # Kết nối Actor 3
    ax.plot([0.15, 0.29], [0.25, 0.09], color=C_GRAY, lw=1)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hinh3_so_do_ca_su_dung.png"), dpi=200)
    plt.close()


# ==============================================================================
# HÌNH 4: Sơ đồ luồng vòng kiểm tra (Worker.Tick)
# ==============================================================================
def ve_hinh4():
    fig, ax = plt.subplots(figsize=(9, 7.5), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax.text(0.5, 0.97, "LƯU ĐỒ THỰC THI VÒNG KIỂM TRA (WORKER.TICK)",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)

    # Khối Bắt đầu
    draw_box(ax, 0.35, 0.89, 0.30, 0.06, "Kích hoạt Tick()",
             ["WMI Event hoặc Timer 2s"], bg_color=C_YELLOW, border_color=C_ORANGE, title_size=9, text_size=8)

    # Bước 1: Khóa luồng
    draw_box(ax, 0.35, 0.79, 0.30, 0.06, "Khóa luồng (_gate)",
             ["Bỏ qua nếu vòng trước chưa xong"], bg_color=C_LIGHT_GRAY, border_color=C_GRAY, title_size=9, text_size=8)
    draw_arrow(ax, 0.50, 0.89, 0.50, 0.85, "", C_NAVY)

    # Bước 2: Kiểm tra cờ Uninstalling
    draw_box(ax, 0.32, 0.69, 0.36, 0.06, "Cờ Settings.Uninstalling = 1?",
             ["Kiểm tra yêu cầu gỡ cài đặt"], bg_color=C_LIGHT_BLUE, border_color=C_NAVY, title_size=9, text_size=8)
    draw_arrow(ax, 0.50, 0.79, 0.50, 0.75, "", C_NAVY)

    # Nhánh Uninstalling = True -> Dừng
    draw_box(ax, 0.75, 0.69, 0.21, 0.06, "Dừng dịch vụ",
             ["_timer.Stop(); Stop();"], bg_color=C_LIGHT_RED, border_color=C_RED, title_size=9, text_size=8)
    draw_arrow(ax, 0.68, 0.72, 0.75, 0.72, "Đúng", C_RED)

    # Bước 3: Kiểm tra IsPaused
    draw_box(ax, 0.32, 0.58, 0.36, 0.06, "Trạng thái Settings.IsPaused?",
             ["Thời gian tạm dừng còn hiệu lực?"], bg_color=C_LIGHT_BLUE, border_color=C_NAVY, title_size=9, text_size=8)
    draw_arrow(ax, 0.50, 0.69, 0.50, 0.64, "Sai", C_NAVY)

    # Nhánh Tạm dừng = True -> Mở
    draw_box(ax, 0.75, 0.58, 0.22, 0.07, "Chế độ TẠM DỪNG",
             ["Enforcer.Unblock();", "ReenableDisabled();"], bg_color=C_LIGHT_GREEN, border_color=C_GREEN, title_size=9, text_size=8)
    draw_arrow(ax, 0.68, 0.61, 0.75, 0.61, "Đúng", C_GREEN)

    # Bước 4: Kiểm tra Whitelist
    draw_box(ax, 0.32, 0.46, 0.36, 0.07, "Whitelist có mục cấu hình?",
             ["Lấy danh sách ID cho phép"], bg_color=C_LIGHT_BLUE, border_color=C_NAVY, title_size=9, text_size=8)
    draw_arrow(ax, 0.50, 0.58, 0.50, 0.53, "Sai", C_NAVY)

    # 2 nhánh Chế độ
    draw_box(ax, 0.08, 0.34, 0.32, 0.07, "CHẶN TẤT CẢ (Rỗng)",
             ["Enforcer.Block(): Start=4,", "Deny_All=1"], bg_color=C_LIGHT_RED, border_color=C_RED, title_size=9, text_size=8)
    draw_box(ax, 0.56, 0.34, 0.36, 0.07, "DANH SÁCH CHO PHÉP (Có mục)",
             ["Enforcer.Unblock(): Start=3,", "mở driver cho USB hợp lệ"], bg_color=C_LIGHT_GREEN, border_color=C_GREEN, title_size=9, text_size=8)
    draw_arrow(ax, 0.40, 0.46, 0.24, 0.41, "Rỗng", C_RED)
    draw_arrow(ax, 0.60, 0.46, 0.74, 0.41, "Có mục", C_GREEN)

    # Bước 5: Quét thiết bị
    draw_box(ax, 0.30, 0.22, 0.40, 0.07, "Quét ổ đĩa: UsbDisks.Scan()",
             ["SetupAPI + IOCTL (BusType = 7 USB)"], bg_color=C_VERY_LIGHT_BLUE, border_color=C_NAVY, title_size=9, text_size=8)
    draw_arrow(ax, 0.24, 0.34, 0.45, 0.29, "", C_NAVY)
    draw_arrow(ax, 0.74, 0.34, 0.55, 0.29, "", C_NAVY)

    # Bước 6: Xử lý từng ổ đĩa
    draw_box(ax, 0.15, 0.08, 0.70, 0.09, "Xử lý từng ổ đĩa USB phát hiện",
             ["• Nếu khớp Whitelist: Bỏ qua cho phép hoạt động",
              "• Nếu KHÔNG khớp: UsbDisks.Eject(disk) -> Nếu lỗi dùng pnputil /disable-device",
              "• Gửi cảnh báo WTSSendMessage tới người dùng + Ghi nhật ký Log.Warn"],
             bg_color=C_LIGHT_YELLOW if hasattr(patches, 'C_LIGHT_YELLOW') else C_YELLOW, border_color=C_ORANGE, title_size=9, text_size=8)
    draw_arrow(ax, 0.50, 0.22, 0.50, 0.17, "", C_NAVY)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hinh4_luong_vong_kiem_tra.png"), dpi=200)
    plt.close()


# ==============================================================================
# HÌNH 5: Sơ đồ trạng thái 3 chế độ
# ==============================================================================
def ve_hinh5():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax.text(0.5, 0.95, "SƠ ĐỒ CHUYỂN ĐỔI TRẠNG THÁI 3 CHẾ ĐỘ HOẠT ĐỘNG",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)

    # Chế độ 1: CHẶN TẤT CẢ (trái)
    draw_box(ax, 0.05, 0.45, 0.38, 0.38, "CHẾ ĐỘ: CHẶN TẤT CẢ",
             ["• Điều kiện: Whitelist rỗng",
              "• Driver USBSTOR / UASPStor: Start = 4",
              "• Chính sách: Deny_All = 1",
              "• Hành vi: Windows từ chối gắn driver;",
              "  Mọi ổ USB cắm vào đều bị gỡ ngay;",
              "  Chuột / Bàn phím HID vẫn hoạt động.",
              "• Mặc định sau khi cài đặt."],
             bg_color=C_LIGHT_RED, border_color=C_RED, title_color=C_RED)

    # Chế độ 2: DANH SÁCH CHO PHÉP (phải)
    draw_box(ax, 0.57, 0.45, 0.38, 0.38, "CHẾ ĐỘ: DANH SÁCH CHO PHÉP",
             ["• Điều kiện: Whitelist có >= 1 mục",
              "• Driver USBSTOR / UASPStor: Start = 3",
              "• Chính sách: Deny_All được gỡ bỏ",
              "• Hành vi: Driver mở để USB hợp lệ chạy;",
              "  Quét SetupAPI và gỡ ổ không khớp ID;",
              "  USB khớp ID được phép truy cập."],
             bg_color=C_LIGHT_GREEN, border_color=C_GREEN, title_color=C_GREEN)

    # Chế độ 3: TẠM DỪNG (dưới)
    draw_box(ax, 0.31, 0.05, 0.38, 0.30, "CHẾ ĐỘ: TẠM DỪNG (PAUSED)",
             ["• Điều kiện: Lệnh pause đúng mật khẩu",
              "• Driver USBSTOR / UASPStor: Start = 3",
              "• Bật lại các thiết bị từng bị vô hiệu hóa",
              "• Tạm ngưng hoàn toàn việc quét & gỡ",
              "• Tự động quay về chế độ cũ khi hết giờ."],
             bg_color=C_YELLOW, border_color=C_ORANGE, title_color=C_ORANGE)

    # Mũi tên giữa Chế độ 1 và Chế độ 2
    draw_arrow(ax, 0.43, 0.70, 0.57, 0.70, "whitelist add <ID>", C_GREEN, label_side="top")
    draw_arrow(ax, 0.57, 0.55, 0.43, 0.55, "whitelist remove hết", C_RED, label_side="bottom")

    # Mũi tên tới Tạm dừng
    draw_arrow(ax, 0.20, 0.45, 0.31, 0.25, "pause <phút>", C_ORANGE)
    draw_arrow(ax, 0.80, 0.45, 0.69, 0.25, "pause <phút>", C_ORANGE)

    # Mũi tên quay về từ Tạm dừng
    draw_arrow(ax, 0.38, 0.35, 0.27, 0.45, "Hết giờ / resume", C_NAVY)
    draw_arrow(ax, 0.62, 0.35, 0.73, 0.45, "Hết giờ / resume", C_NAVY)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hinh5_trang_thai_3_che_do.png"), dpi=200)
    plt.close()


# ==============================================================================
# HÌNH 6: Luồng gỡ cài đặt có mật khẩu
# ==============================================================================
def ve_hinh6():
    fig, ax = plt.subplots(figsize=(9, 7), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax.text(0.5, 0.96, "QUY TRÌNH GỠ CÀI ĐẶT BẢO MẬT (USBGUARD UNINSTALL)",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)

    draw_box(ax, 0.30, 0.86, 0.40, 0.07, "Chạy lệnh Uninstall",
             ["UsbGuard.exe uninstall [mật_khẩu]"], bg_color=C_LIGHT_BLUE, border_color=C_NAVY)

    draw_box(ax, 0.30, 0.74, 0.40, 0.07, "Kiểm tra quyền Administrator?",
             ["WindowsPrincipal.IsInRole(Admin)"], bg_color=C_LIGHT_GRAY, border_color=C_GRAY)
    draw_arrow(ax, 0.50, 0.86, 0.50, 0.81, "", C_NAVY)

    # Lỗi Admin
    draw_box(ax, 0.78, 0.74, 0.18, 0.07, "Từ chối (Lỗi 5)",
             ["Access Denied"], bg_color=C_LIGHT_RED, border_color=C_RED)
    draw_arrow(ax, 0.70, 0.775, 0.78, 0.775, "Không", C_RED)

    draw_box(ax, 0.30, 0.62, 0.40, 0.07, "Xác thực mật khẩu PBKDF2",
             ["So khớp mật khẩu với AuthHash (HKLM)"], bg_color=C_LIGHT_GRAY, border_color=C_GRAY)
    draw_arrow(ax, 0.50, 0.74, 0.50, 0.69, "Có", C_NAVY)

    # Sai mật khẩu
    draw_box(ax, 0.78, 0.62, 0.18, 0.07, "Từ chối (Lỗi 3)",
             ["Sai mật khẩu"], bg_color=C_LIGHT_RED, border_color=C_RED)
    draw_arrow(ax, 0.70, 0.655, 0.78, 0.655, "Sai", C_RED)

    # Các bước tiến hành gỡ
    draw_box(ax, 0.20, 0.48, 0.60, 0.09, "1. Bật cờ Uninstalling trong Registry",
             ["Settings.SetUninstalling(true) -> Dịch vụ Worker phát hiện cờ và tự gọi Stop()"],
             bg_color=C_VERY_LIGHT_BLUE, border_color=C_BLUE)
    draw_arrow(ax, 0.50, 0.62, 0.50, 0.57, "Đúng mật khẩu", C_GREEN)

    draw_box(ax, 0.20, 0.36, 0.60, 0.08, "2. Chờ dịch vụ tự dừng an toàn & Xóa khỏi SCM",
             ["WaitStopped(20s) -> sc.exe delete UsbGuard"], bg_color=C_VERY_LIGHT_BLUE, border_color=C_BLUE)
    draw_arrow(ax, 0.50, 0.48, 0.50, 0.44, "", C_NAVY)

    draw_box(ax, 0.20, 0.23, 0.60, 0.09, "3. Khôi phục hoàn toàn cấu hình mặc định Windows",
             ["Enforcer.Unblock(): USBSTOR Start=3, xóa Deny_All",
              "ReenableDisabled(): Bật lại các thiết bị bị pnputil tắt"],
             bg_color=C_VERY_LIGHT_BLUE, border_color=C_BLUE)
    draw_arrow(ax, 0.50, 0.36, 0.50, 0.32, "", C_NAVY)

    draw_box(ax, 0.20, 0.08, 0.60, 0.11, "4. Dọn dẹp tệp tin và hoàn tất",
             ["- Xóa khóa Registry: HKLM\\SOFTWARE\\UsbGuard",
              "- Xóa thư mục cài đặt: Program Files\\UsbGuard",
              "-> Hệ thống trở về trạng thái nguyên bản của Windows."],
             bg_color=C_LIGHT_GREEN, border_color=C_GREEN, title_color=C_GREEN)
    draw_arrow(ax, 0.50, 0.23, 0.50, 0.19, "", C_NAVY)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hinh6_luong_go_cai_dat.png"), dpi=200)
    plt.close()


# ==============================================================================
# HÌNH 7: Cây thiết bị USB và ranh giới gỡ
# ==============================================================================
def ve_hinh7():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax.text(0.5, 0.96, "CÂY THIẾT BỊ PNP VÀ RANH GIỚI GỠ BỎ AN TOÀN TRÁNH ẢNH HƯỞNG HUB",
            ha='center', va='center', fontsize=12, fontweight='bold', color=C_NAVY)

    # Gốc: USB Root Hub
    draw_box(ax, 0.35, 0.83, 0.30, 0.08, "PCI Host Controller / USB Root Hub",
             ["Cổng kết nối phần cứng chính"], bg_color=C_LIGHT_GRAY, border_color=C_GRAY)

    # Cấp 2: USB Generic Hub
    draw_box(ax, 0.35, 0.67, 0.30, 0.08, "USB Generic Hub (Bộ chia cổng USB)",
             ["Quản lý chia cổng ngoại vi"], bg_color=C_LIGHT_GRAY, border_color=C_GRAY)
    draw_arrow(ax, 0.50, 0.83, 0.50, 0.75, "", C_NAVY)

    # Vùng KHÔNG GỠ (bên trái - HID)
    hid_box = patches.FancyBboxPatch((0.04, 0.10), 0.38, 0.48, boxstyle="round,pad=0,rounding_size=0.02",
                                     facecolor=C_LIGHT_GREEN, edgecolor=C_GREEN, linewidth=1.5, linestyle='--')
    ax.add_patch(hid_box)
    ax.text(0.23, 0.55, "VÙNG BẢO VỆ: THIẾT BỊ HID", ha='center', va='center', fontsize=10, fontweight='bold', color=C_GREEN)
    
    draw_box(ax, 0.08, 0.36, 0.30, 0.14, "Chuột USB (Mouse)",
             ["• HID-compliant mouse", "• BusType = USB", "• Lớp: GUID_DEVINTERFACE_HID", "• KHÔNG thuộc lớp Disk -> Bỏ qua"],
             bg_color="#FFFFFF", border_color=C_GREEN, title_size=9, text_size=8)
             
    draw_box(ax, 0.08, 0.14, 0.30, 0.14, "Bàn phím USB (Keyboard)",
             ["• HID Keyboard Device", "• Lớp: GUID_DEVINTERFACE_HID", "• Không có Storage Property", "• Hoạt động liên tục, an toàn"],
             bg_color="#FFFFFF", border_color=C_GREEN, title_size=9, text_size=8)

    draw_arrow(ax, 0.38, 0.67, 0.23, 0.50, "Cắm chung Hub", C_GREEN)

    # Vùng XỬ LÝ: LƯU TRỮ USB (bên phải)
    usb_box = patches.FancyBboxPatch((0.54, 0.10), 0.42, 0.48, boxstyle="round,pad=0,rounding_size=0.02",
                                     facecolor=C_LIGHT_RED, edgecolor=C_RED, linewidth=1.5)
    ax.add_patch(usb_box)
    ax.text(0.75, 0.55, "VÙNG XỬ LÝ: Ổ ĐĨA LƯU TRỮ USB", ha='center', va='center', fontsize=10, fontweight='bold', color=C_RED)

    # Nút thiết bị USB cha
    draw_box(ax, 0.58, 0.36, 0.34, 0.14, "Nút USB Cha (Parent USB Node)",
             ["• USB\\VID_xxxx&PID_xxxx\\Serial...",
              "• Thuộc tính BusType = 7 (USB)",
              "• [RANH GIỚI DỪNG: MaxDepth = 2]",
              "  Không đi lên Hub!"],
             bg_color="#FFFFFF", border_color=C_RED, title_color=C_RED, title_size=9, text_size=8)

    # Nút ổ đĩa con
    draw_box(ax, 0.58, 0.14, 0.34, 0.14, "Nút Ổ Đĩa (Disk Device Node)",
             ["• USBSTOR\\DiskKingston... hoặc SCSI...",
              "• GUID_DEVINTERFACE_DISK",
              "• [ĐỘ SÂU = 1]: Thử eject trước",
              "  bằng CM_Request_Device_Eject"],
             bg_color="#FFFFFF", border_color=C_RED, title_color=C_RED, title_size=9, text_size=8)

    draw_arrow(ax, 0.62, 0.67, 0.75, 0.50, "Cắm chung Hub", C_RED)
    draw_arrow(ax, 0.75, 0.36, 0.75, 0.28, "CM_Get_Parent", C_RED)

    # Chú thích đường cấm
    ax.text(0.50, 0.60, "Ranh giới dừng:\nKhông bao giờ gỡ Hub\nđể bảo vệ Chuột & Bàn phím!",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color=C_RED,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=C_YELLOW, edgecolor=C_ORANGE, lw=1))

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hinh7_cay_thiet_bi_usb.png"), dpi=200)
    plt.close()


# ==============================================================================
# HÌNH 8: Cơ chế không tắt được & tự phục hồi dịch vụ
# ==============================================================================
def ve_hinh8():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax.text(0.5, 0.96, "CƠ CHẾ 'KHÔNG TẮT ĐƯỢC' VÀ TỰ PHỤC HỒI DỊCH VỤ SCM",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)

    # Tình huống 1: Admin sc stop
    draw_box(ax, 0.05, 0.64, 0.42, 0.26, "Tình huống 1: Administrator dùng 'sc stop'",
             ["• Lệnh gọi: sc stop UsbGuard hoặc services.msc",
              "• SCM kiểm tra thuộc tính dịch vụ:",
              "  CanStop = false, CanPauseAndContinue = false",
              "• Windows từ chối gửi lệnh dừng:",
              "  Báo lỗi 1052 (ERROR_INVALID_SERVICE_CONTROL)",
              "-> Kể cả Administrator cũng không dừng được trực tiếp!"],
             bg_color=C_LIGHT_BLUE, border_color=C_NAVY)

    # Tình huống 2: Người dùng thường can thiệp
    draw_box(ax, 0.53, 0.64, 0.42, 0.26, "Tình huống 2: Người dùng thông thường",
             ["• Lệnh gọi: sc stop, sc config, sc delete",
              "• SCM kiểm tra phân quyền DACL của dịch vụ:",
              "  Chỉ SYSTEM và Administrators có quyền kiểm soát",
              "• Windows chặn ngay lập tức:",
              "  Báo lỗi 5 (ERROR_ACCESS_DENIED)",
              "-> Người dùng thường không thể tác động lên dịch vụ!"],
             bg_color=C_LIGHT_BLUE, border_color=C_NAVY)

    # Tình huống 3: Bị cưỡng chế kết thúc (taskkill /F)
    draw_box(ax, 0.05, 0.18, 0.42, 0.38, "Tình huống 3: Cưỡng chế kill tiến trình",
             ["• Tiến trình UsbGuard.exe bị kết thúc:",
              "  Bằng taskkill /F hoặc Task Manager (Admin)",
              "• Service Control Manager (SCM) phát hiện sự cố",
              "• Kích hoạt cấu hình phục hồi đã đăng ký:",
              "  sc failure UsbGuard reset= 86400",
              "  actions= restart/5000/restart/30000",
              "• Hệ điều hành Windows tự khởi động lại dịch vụ:",
              "  Tự hồi sinh sau khoảng 5 giây!"],
             bg_color=C_LIGHT_RED, border_color=C_RED, title_color=C_RED)

    # Cách duy nhất để dừng an toàn
    draw_box(ax, 0.53, 0.18, 0.42, 0.38, "CÁCH DUY NHẤT ĐỂ DỪNG DỊCH VỤ",
             ["• Lệnh: UsbGuard.exe uninstall <mật_khẩu>",
              "• Yêu cầu bắt buộc 2 điều kiện:",
              "  1. Chạy với quyền Administrator (UAC)",
              "  2. Đúng mật khẩu quản trị (xác thực PBKDF2)",
              "• Chương trình ghi cờ Uninstalling = 1 vào Registry",
              "• Dịch vụ đọc thấy cờ và chủ động gọi Stop()",
              "-> Ranh giới kỹ thuật rõ ràng: Phần mềm Device Control",
              "   chính thống, không phải mã độc ẩn mình."],
             bg_color=C_LIGHT_GREEN, border_color=C_GREEN, title_color=C_GREEN)

    # Dải tóm tắt bên dưới
    ax.text(0.5, 0.08, "Tổng kết: CanStop = false (chống sc stop) + DACL (chống user thường) + sc failure (chống taskkill) = Không thể bị tắt trái phép",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color=C_NAVY,
            bbox=dict(boxstyle="round,pad=0.4", facecolor=C_YELLOW, edgecolor=C_ORANGE, lw=1))

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hinh8_co_che_khong_tat_duoc.png"), dpi=200)
    plt.close()


# ==============================================================================
# HÌNH 9: Thiết kế bảo mật PBKDF2 & Phân quyền Registry DACL
# ==============================================================================
def ve_hinh9():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax.text(0.5, 0.96, "THIẾT KẾ BẢO MẬT MẬT KHẨU VÀ PHÂN QUYỀN REGISTRY DACL",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)

    # Phần 1: Băm mật khẩu PBKDF2
    draw_box(ax, 0.04, 0.46, 0.44, 0.44, "1. Cơ chế băm mật khẩu PBKDF2 (Auth.cs)",
             ["• Chuẩn: RFC 8018 / PKCS #5 v2.0 (Rfc2898DeriveBytes)",
              "• Muối ngẫu nhiên (Salt): 16 byte tạo từ RNGCryptoServiceProvider",
              "• Số vòng lặp (Iterations): 100000 vòng",
              "  (tăng chi phí tính toán, chống tấn công brute-force)",
              "• Độ dài khóa dẫn xuất: 32 byte (256-bit)",
              "• Định dạng lưu trữ: pbkdf2$100000$<salt_b64>$<hash_b64>",
              "• So sánh xác thực thời gian hằng (ConstantTimeEquals):",
              "  diff |= a[i] ^ b[i] -> Chống tấn công thời gian (timing attack)"],
             bg_color=C_VERY_LIGHT_BLUE, border_color=C_NAVY)

    # Phần 2: Phân quyền Registry DACL
    draw_box(ax, 0.52, 0.46, 0.44, 0.44, "2. Bảo vệ khóa Registry cấu hình (Settings & Reg.cs)",
             ["• Vị trí: HKLM\\SOFTWARE\\UsbGuard",
              "• Khóa quyền kế thừa từ nút cha (SetAccessRuleProtection):",
              "  Loại bỏ hoàn toàn quyền mặc định của nhóm Users",
              "• Thiết lập DACL nghiêm ngặt (SystemAndAdminsOnly):",
              "  - LocalSystem SID: FullControl",
              "  - BuiltinAdministrators SID: FullControl",
              "• Kết quả: Người dùng thường không thể:",
              "  - Xem hay sửa cấu hình Whitelist, PauseUntil",
              "  - Đọc chuỗi AuthHash để đem bẻ khóa offline (cracking)"],
             bg_color=C_LIGHT_GREEN, border_color=C_GREEN, title_color=C_GREEN)

    # Phần 3: Nhập mật khẩu an toàn
    draw_box(ax, 0.04, 0.08, 0.92, 0.32, "3. Cơ chế giao tiếp dòng lệnh an toàn (Password.cs & WTSSendMessage)",
             ["• Nhập mật khẩu ẩn trên console (Password.Ask):",
              "  Sử dụng Console.ReadKey(intercept: true), không hiển thị ký tự trên màn hình và không lưu lịch sử lệnh",
              "  -> Ngăn chặn người bên cạnh nhìn trộm (shoulder surfing) và không để lộ mật khẩu trong danh sách tiến trình hệ thống.",
              "• Gửi thông báo an toàn ra phiên tương tác của người dùng (WTSSendMessage):",
              "  Dịch vụ chạy trong Session 0 (LocalSystem) không có giao diện đồ họa trực tiếp.",
              "  UsbGuard gọi WTSGetActiveConsoleSessionId() và WTSSendMessage() để đẩy hộp thoại cảnh báo ra Session người dùng thật."],
             bg_color=C_YELLOW, border_color=C_ORANGE, title_color=C_ORANGE)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hinh9_mo_hinh_bao_mat_pbkdf2.png"), dpi=200)
    plt.close()


# ==============================================================================
# HÌNH 10: Ảnh chụp màn hình Terminal chạy kiểm thử tích hợp thực tế
# ==============================================================================
def ve_hinh10_terminal():
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Khung cửa sổ Terminal nền tối
    term_bg = patches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0,rounding_size=0.015",
                                     facecolor="#1E1E1E", edgecolor="#3C3C3C", linewidth=1.5)
    ax.add_patch(term_bg)

    # Thanh tiêu đề cửa sổ (Title bar)
    title_bar = patches.Rectangle((0.02, 0.92), 0.96, 0.06, facecolor="#2D2D2D", edgecolor="#3C3C3C", linewidth=1)
    ax.add_patch(title_bar)

    # Các nút điều khiển cửa sổ (Close, Minimize, Maximize)
    ax.plot(0.05, 0.95, 'o', markersize=7, color="#FF5F56")
    ax.plot(0.075, 0.95, 'o', markersize=7, color="#FFBD2E")
    ax.plot(0.10, 0.95, 'o', markersize=7, color="#27C93F")

    ax.text(0.50, 0.95, "Administrator: Windows PowerShell — tests\\integration.ps1",
            ha='center', va='center', fontsize=9, fontweight='bold', color="#CCCCCC", fontfamily="Arial Unicode MS")

    # Nội dung nhật ký trích từ kết quả kiểm thử thật
    log_lines = [
        ("=== KIỂM THỬ TÍCH HỢP USBGUARD (CI GITHUB ACTIONS) ===", "#4EC9B0", True),
        ("Máy: runnervm9zap3 | Windows Server 2022 Datacenter 10.0.20348", "#9CDCFE", False),
        ("Chạy bằng: runnervm9zap3\\runneradmin  |  USBSTOR trước khi cài: Start = 3", "#808080", False),
        ("", "#CCCCCC", False),
        ("--- TC01 Cài đặt dịch vụ ---", "#DCDCAA", True),
        ("> UsbGuard.exe install ********   (mã thoát 0)", "#CE9178", False),
        ("  Đã cài đặt và khởi động dịch vụ UsbGuard.", "#CCCCCC", False),
        ("[ĐẠT] TC01 Cài đặt, dịch vụ chạy — mã thoát 0, trạng thái Running", "#4EC9B0", True),
        ("[ĐẠT] TC02 Khởi động tự động cùng Windows — StartType = Automatic", "#4EC9B0", True),
        ("[ĐẠT] TC03 Cấu hình tự khởi động lại khi bị kill — sc qfailure có RESTART", "#4EC9B0", True),
        ("[ĐẠT] TC04 Chạy dưới tài khoản LocalSystem — SERVICE_START_NAME = LocalSystem", "#4EC9B0", True),
        ("[ĐẠT] TC05 USBSTOR bị tắt (Start = 4) — Start = 4, sau 2 ms", "#4EC9B0", True),
        ("[ĐẠT] TC06 Chính sách Removable Storage Deny_All = 1", "#4EC9B0", True),
        ("[ĐẠT] TC07 Tự sửa khi registry bị đổi tay — khôi phục Start = 4 sau 1316 ms", "#4EC9B0", True),
        ("[ĐẠT] TC08 Admin 'sc stop' bị từ chối — mã 1052 (không nhận Stop), trạng thái Running", "#4EC9B0", True),
        ("[ĐẠT] TC10 Bị kill tiến trình thì Windows tự chạy lại — PID 5544 -> 512, chạy lại sau 5412 ms", "#4EC9B0", True),
        ("[ĐẠT] TC11 User thường 'sc stop' bị từ chối quyền — mã 5 (Access is denied)", "#4EC9B0", True),
        ("[ĐẠT] TC14 User thường không đọc được hash — từ chối truy cập qua DACL", "#4EC9B0", True),
        ("[ĐẠT] TC20 Chuyển sang chế độ Whitelist — driver mở cho USB hợp lệ sau 1198 ms", "#4EC9B0", True),
        ("[ĐẠT] TC29 Gỡ đúng mật khẩu — dịch vụ tự dừng an toàn sau 1926 ms", "#4EC9B0", True),
        ("[ĐẠT] TC30 Trả lại mặc định Windows sau khi gỡ — Start = 3, Deny_All xóa sạch", "#4EC9B0", True),
        ("", "#CCCCCC", False),
        ("=== KẾT QUẢ TỔNG HỢP: 30/30 CA KIỂM THỬ ĐẠT (100% PASS) ===", "#4EC9B0", True)
    ]

    y_pos = 0.88
    line_h = 0.035
    for text, color, is_bold in log_lines:
        if text:
            ax.text(0.05, y_pos, text, ha='left', va='center', fontsize=7.8,
                    fontweight='bold' if is_bold else 'normal', color=color, fontfamily="Arial Unicode MS")
        y_pos -= line_h

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hinh10_terminal_log.png"), dpi=200)
    plt.close()


def main():
    print("Bắt đầu vẽ các hình minh họa kỹ thuật...")
    ve_hinh1(); print("- Hình 1: Kiến trúc tổng thể 2 lớp")
    ve_hinh2(); print("- Hình 2: Sơ đồ thành phần hệ thống")
    ve_hinh3(); print("- Hình 3: Sơ đồ ca sử dụng")
    ve_hinh4(); print("- Hình 4: Sơ đồ luồng vòng kiểm tra")
    ve_hinh5(); print("- Hình 5: Sơ đồ trạng thái 3 chế độ")
    ve_hinh6(); print("- Hình 6: Sơ đồ luồng gỡ cài đặt")
    ve_hinh7(); print("- Hình 7: Cây thiết bị USB và ranh giới gỡ")
    ve_hinh8(); print("- Hình 8: Cơ chế không tắt được & tự phục hồi")
    ve_hinh9(); print("- Hình 9: Thiết kế bảo mật PBKDF2 & Phân quyền DACL")
    ve_hinh10_terminal(); print("- Hình 10: Nhật ký chạy kiểm thử tích hợp trên Windows Server")
    print(f"Hoàn tất vẽ 10 hình kỹ thuật trong {OUT_DIR}")


if __name__ == "__main__":
    main()

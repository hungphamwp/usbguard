using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Security.Principal;

namespace UsbGuard
{
    /// <summary>
    /// Cài đặt/gỡ cài đặt dịch vụ bằng sc.exe (cơ chế chuẩn của Windows).
    /// Dịch vụ chạy LocalSystem, khởi động tự động (auto). Theo phân quyền mặc định của Windows,
    /// chỉ tài khoản Administrator mới Start/Stop/Delete được service — người dùng thường chỉ xem trạng thái.
    /// Đây là lý do "không tắt được" (với người dùng thường), không phải cơ chế chống gỡ của chương trình.
    /// </summary>
    internal static class Installer
    {
        public static readonly string InstallDir =
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "UsbGuard");
        public static readonly string InstalledExe = Path.Combine(InstallDir, "UsbGuard.exe");

        public static bool IsAdmin()
        {
            using (var id = WindowsIdentity.GetCurrent())
                return new WindowsPrincipal(id).IsInRole(WindowsBuiltInRole.Administrator);
        }

        public static bool ServiceExists()
        {
            string o;
            return Sys.Run("sc.exe", "query " + Hardening.ServiceName, out o) != 1060;
        }

        public static int Install(string password)
        {
            if (!IsAdmin()) { Console.WriteLine("Cần chạy với quyền Administrator (Run as administrator)."); return 5; }
            if (!Whitelist.IsValidEntry(password) || password.Length < 8)
            {
                Console.WriteLine("Mật khẩu quản trị phải có ít nhất 8 ký tự.");
                return 1;
            }
            if (ServiceExists())
            {
                Console.WriteLine("UsbGuard đã được cài đặt. Dùng lệnh 'uninstall' trước nếu muốn cài lại.");
                return 1;
            }

            string self = Assembly.GetExecutingAssembly().Location;
            Directory.CreateDirectory(InstallDir);
            if (!string.Equals(Path.GetFullPath(self), InstalledExe, StringComparison.OrdinalIgnoreCase))
                File.Copy(self, InstalledExe, true);

            try
            {
                if (!EventLog.SourceExists(Log.EventSource))
                    EventLog.CreateEventSource(Log.EventSource, "Application");
            }
            catch (Exception ex) { Console.WriteLine("Cảnh báo: không tạo được nguồn Event Log: " + ex.Message); }

            Settings.InitFirstTime(Auth.Hash(password));
            Settings.LockAcl();

            string output;
            int rc = Sys.Run("sc.exe",
                "create " + Hardening.ServiceName + " binPath= \"" + InstalledExe + "\" " +
                "start= auto DisplayName= \"" + Hardening.DisplayName + "\"", out output);
            if (rc != 0)
            {
                Console.WriteLine("Tạo dịch vụ thất bại (mã " + rc + "): " + output);
                return 2;
            }
            Sys.Run("sc.exe", "description " + Hardening.ServiceName + " \"" + Hardening.Description + "\"");
            // Tự khởi động lại nếu service crash — hành vi hợp lệ, chuẩn Windows, không phải chống gỡ.
            Sys.Run("sc.exe", "failure " + Hardening.ServiceName + FailureArgs);

            rc = Sys.Run("sc.exe", "start " + Hardening.ServiceName, out output);
            if (rc != 0 && rc != 1056)
            {
                Console.WriteLine("Cảnh báo: khởi động dịch vụ thất bại (mã " + rc + "): " + output);
            }

            Log.Info("Đã cài đặt UsbGuard.");
            Console.WriteLine("Đã cài đặt và khởi động dịch vụ UsbGuard.");
            Console.WriteLine("Kiểm tra: UsbGuard.exe status");
            return 0;
        }

        private const string FailureArgs = " reset= 86400 actions= restart/5000/restart/30000/\"\"/0";

        /// <summary>
        /// Admin đổi "Startup type" của dịch vụ trong services.msc (Disabled/Manual) hoặc xoá cấu hình tự chạy lại:
        /// trả lại Automatic + restart khi bị kill. Đổi kiểu khởi động không cần dừng dịch vụ nên CanStop = false không chặn được,
        /// phải tự sửa. Trả về mô tả những gì đã sửa (rỗng nếu không phải sửa).
        /// </summary>
        public static string RepairServiceConfig()
        {
            int start = -1; bool hasFailure;
            using (var hk = Reg.Hklm())
            using (var k = hk.OpenSubKey(@"SYSTEM\CurrentControlSet\Services\" + Hardening.ServiceName))
            {
                if (k == null) return "";
                var v = k.GetValue("Start");
                if (v is int) start = (int)v;
                // SERVICE_FAILURE_ACTIONS lưu dạng nhị phân: số hành động ở byte 12, hành động đầu (loại, chờ) từ byte 20; 1 = RESTART.
                var b = k.GetValue("FailureActions") as byte[];
                hasFailure = b != null && b.Length >= 28 && BitConverter.ToInt32(b, 12) > 0 && BitConverter.ToInt32(b, 20) == 1;
            }
            string fixedWhat = "";
            if (start != 2)
            {
                Sys.Run("sc.exe", "config " + Hardening.ServiceName + " start= auto");
                fixedWhat = "kiểu khởi động " + (start == 4 ? "Disabled" : start == 3 ? "Manual" : "Start=" + start) + " → Automatic";
            }
            if (!hasFailure)
            {
                Sys.Run("sc.exe", "failure " + Hardening.ServiceName + FailureArgs);
                fixedWhat += (fixedWhat.Length > 0 ? ", " : "") + "cấu hình tự chạy lại khi bị kill";
            }
            return fixedWhat;
        }

        /// <summary>Dịch vụ đang chạy không (RUNNING hoặc đang khởi động).</summary>
        public static bool ServiceRunning()
        {
            string o;
            Sys.Run("sc.exe", "query " + Hardening.ServiceName, out o);
            return o.IndexOf("RUNNING", StringComparison.OrdinalIgnoreCase) >= 0 || o.IndexOf("START_PENDING", StringComparison.OrdinalIgnoreCase) >= 0;
        }

        public static int Uninstall(string password, bool keepFiles = false)
        {
            if (!IsAdmin()) { Console.WriteLine("Cần chạy với quyền Administrator."); return 5; }
            if (!ServiceExists()) { Console.WriteLine("UsbGuard chưa được cài đặt."); return 0; }
            string err;
            if (Settings.Exists() && !AdminAuth.Check(password, "gỡ cài đặt", out err))
            {
                Console.WriteLine(err);
                return 3;
            }

            // Dịch vụ từ chối lệnh Stop (CanStop = false). Bật cờ Uninstalling, dịch vụ thấy cờ thì tự dừng.
            Settings.SetUninstalling(true);
            Log.Info("Nhận lệnh gỡ cài đặt (đúng mật khẩu), chờ dịch vụ tự dừng.");
            if (!WaitStopped(TimeSpan.FromSeconds(20)))
            {
                Console.WriteLine("Dịch vụ chưa tự dừng sau 20 giây, buộc kết thúc tiến trình.");
                Sys.Run("sc.exe", "failure " + Hardening.ServiceName + " reset= 0 actions= \"\"/0");
                Sys.Run("taskkill.exe", "/F /IM UsbGuard.exe /FI \"PID ne " + System.Diagnostics.Process.GetCurrentProcess().Id + "\"");
                WaitStopped(TimeSpan.FromSeconds(10));
            }
            WaitServiceProcessGone(TimeSpan.FromSeconds(10));
            string output;
            int rc = Sys.Run("sc.exe", "delete " + Hardening.ServiceName, out output);
            if (rc != 0) { Console.WriteLine("Xoá dịch vụ thất bại (mã " + rc + "): " + output); return 2; }

            Enforcer.Unblock();
            UsbDisks.ReenableDisabled();
            try { UsbDisks.RetryBlockedDevices(); } catch { }
            ReplugBlockedUsb();
            Settings.Delete();
            // Cài bằng bộ cài (setup.exe) thì để trình gỡ của bộ cài tự xoá file và mục trong "Apps & features".
            if (!keepFiles)
            {
                string self = Path.GetFullPath(Assembly.GetExecutingAssembly().Location);
                foreach (var f in Directory.Exists(InstallDir) ? Directory.GetFiles(InstallDir) : new string[0])
                {
                    if (string.Equals(Path.GetFullPath(f), self, StringComparison.OrdinalIgnoreCase)) continue;
                    try { File.Delete(f); } catch { }
                }
                try { Directory.Delete(InstallDir, true); } catch { /* đang chạy chính file trong thư mục này: Windows tự dọn khi khởi động lại không cần thiết */ }
            }

            Console.WriteLine("Đã gỡ cài đặt UsbGuard và khôi phục cấu hình USB mặc định của Windows.");
            return 0;
        }

        /// <summary>
        /// USB đang cắm mà bị chặn lúc gỡ (Windows đã "tháo an toàn" nó, mã 47/14, hoặc còn lỗi khác): bỏ chặn xong
        /// "rút ra cắm lại" cổng đó bằng phần mềm để USB dùng được ngay. Không có bước này người dùng phải rút tay
        /// (dịch vụ đã dừng nên không còn ai nạp lại). Phải chạy trước Settings.Delete vì cần danh sách cổng đã nhớ.
        /// </summary>
        private static void ReplugBlockedUsb()
        {
            try
            {
                System.Threading.Thread.Sleep(2500);   // cho Windows kịp nạp lại các USB chỉ cần bật driver
                foreach (var d in UsbDisks.ListForDisplay())
                {
                    if (d.Problem == 0) continue;
                    bool cycled = d.Port != null && UsbPorts.Cycle(d.Port);
                    if (!cycled) UsbDisks.Kick(d);
                    Log.Info("Gỡ cài đặt: nạp lại USB đang cắm (mã " + d.Problem + (d.Ejected ? ", đã tháo" : "") + "): " + d.Name +
                             " | " + d.InstanceId + (cycled ? " | rút ra cắm lại cổng " + d.Port.Port : " | nạp lại thiết bị"));
                }
            }
            catch (Exception ex) { Log.Warn("Gỡ cài đặt: không nạp lại được USB đang cắm: " + ex.Message); }
        }

        /// <summary>Chờ tiến trình dịch vụ thoát hẳn (để bộ cài xoá được file UsbGuard.exe ngay, không phải chờ khởi động lại).</summary>
        private static void WaitServiceProcessGone(TimeSpan timeout)
        {
            int me = Process.GetCurrentProcess().Id;
            var until = DateTime.UtcNow + timeout;
            while (DateTime.UtcNow < until)
            {
                bool other = false;
                foreach (var p in Process.GetProcessesByName("UsbGuard"))
                {
                    try { if (p.Id != me && p.SessionId == 0) other = true; } catch { }
                    p.Dispose();
                }
                if (!other) return;
                System.Threading.Thread.Sleep(300);
            }
        }

        /// <summary>Đọc trạng thái dịch vụ qua "sc query", chờ tới khi STOPPED hoặc hết thời gian.</summary>
        private static bool WaitStopped(TimeSpan timeout)
        {
            var until = DateTime.UtcNow + timeout;
            while (DateTime.UtcNow < until)
            {
                string o;
                int rc = Sys.Run("sc.exe", "query " + Hardening.ServiceName, out o);
                if (rc == 1060 || o.IndexOf("STOPPED", StringComparison.OrdinalIgnoreCase) >= 0) return true;
                System.Threading.Thread.Sleep(500);
            }
            return false;
        }

        public static int Status()
        {
            if (!ServiceExists()) { Console.WriteLine("UsbGuard: chưa cài đặt."); return 1; }
            string output;
            Sys.Run("sc.exe", "query " + Hardening.ServiceName, out output);
            Console.WriteLine(output);
            bool exists;
            try { exists = Settings.Exists(); }
            catch (Exception) { Console.WriteLine("Cần quyền Administrator để xem chi tiết cấu hình (whitelist, chế độ chặn)."); return 0; }
            if (exists)
            {
                var wl = Settings.GetWhitelist();
                Console.WriteLine(Settings.IsPaused
                    ? "Trạng thái chặn: ĐANG TẠM DỪNG đến " + Settings.PauseUntilUtc.ToLocalTime()
                    : wl.Count == 0 ? "Trạng thái chặn: ĐANG BẬT, chế độ CHẶN TẤT CẢ"
                                    : "Trạng thái chặn: ĐANG BẬT, chế độ DANH SÁCH CHO PHÉP");
                Console.WriteLine("Whitelist (" + wl.Count + " mục):");
                foreach (var w in wl) Console.WriteLine("  - " + w);
                Console.WriteLine(Enforcer.Describe());
            }
            return 0;
        }
    }
}

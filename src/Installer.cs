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
            Sys.Run("sc.exe", "failure " + Hardening.ServiceName + " reset= 86400 actions= restart/5000/restart/30000/\"\"/0");

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

        public static int Uninstall(string password)
        {
            if (!IsAdmin()) { Console.WriteLine("Cần chạy với quyền Administrator."); return 5; }
            if (!ServiceExists()) { Console.WriteLine("UsbGuard chưa được cài đặt."); return 0; }
            if (Settings.Exists() && !Auth.Verify(password, Settings.AuthHash))
            {
                Console.WriteLine("Sai mật khẩu quản trị.");
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
            string output;
            int rc = Sys.Run("sc.exe", "delete " + Hardening.ServiceName, out output);
            if (rc != 0) { Console.WriteLine("Xoá dịch vụ thất bại (mã " + rc + "): " + output); return 2; }

            Enforcer.Unblock();
            UsbDisks.ReenableDisabled();
            Settings.Delete();
            try { Directory.Delete(InstallDir, true); } catch (Exception ex) { Console.WriteLine("Không xoá được " + InstallDir + ": " + ex.Message); }

            Console.WriteLine("Đã gỡ cài đặt UsbGuard và khôi phục cấu hình USB mặc định của Windows.");
            return 0;
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
            }
            return 0;
        }
    }
}

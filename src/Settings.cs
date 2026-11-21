using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Win32;

namespace UsbGuard
{
    /// <summary>
    /// Trạng thái lưu ở HKLM\SOFTWARE\UsbGuard. Khoá được đặt ACL riêng: chỉ SYSTEM và Administrators truy cập,
    /// người dùng thường không đọc được (không lấy được mã băm mật khẩu để dò offline).
    /// </summary>
    internal static class Settings
    {
        public const string KeyPath = @"SOFTWARE\UsbGuard";

        public static bool Exists()
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.OpenSubKey(KeyPath)) return k != null;
        }

        public static string AuthHash { get { return GetString("AuthHash"); } }
        public static bool Uninstalling { get { return GetLong("Uninstalling") == 1; } }

        public static void InitFirstTime(string authHash)
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.CreateSubKey(KeyPath))
            {
                k.SetValue("AuthHash", authHash, RegistryValueKind.String);
                k.SetValue("Uninstalling", 0L, RegistryValueKind.QWord);
                k.SetValue("PauseUntil", 0L, RegistryValueKind.QWord);
            }
        }

        /// <summary>Đặt ACL: SYSTEM + Administrators toàn quyền, bỏ kế thừa (Users mất quyền đọc). Gọi khi cài và khi dịch vụ khởi động.</summary>
        public static void LockAcl()
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.OpenSubKey(KeyPath, RegistryKeyPermissionCheck.ReadWriteSubTree,
                System.Security.AccessControl.RegistryRights.ChangePermissions |
                System.Security.AccessControl.RegistryRights.ReadKey))
            {
                if (k != null) k.SetAccessControl(Reg.SystemAndAdminsOnly());
            }
        }

        public static void SetAuthHash(string h) { SetString("AuthHash", h); }
        public static void SetUninstalling(bool v) { SetLong("Uninstalling", v ? 1 : 0); }

        public static DateTime PauseUntilUtc
        {
            get
            {
                long t = GetLong("PauseUntil");
                if (t <= 0) return DateTime.MinValue;
                try { return new DateTime(t, DateTimeKind.Utc); } catch { return DateTime.MinValue; }
            }
        }

        public static bool IsPaused { get { return PauseUntilUtc > DateTime.UtcNow; } }
        public static bool IsPausedSafe() { try { return IsPaused; } catch { return false; } }
        public static void PauseFor(TimeSpan span) { SetLong("PauseUntil", DateTime.UtcNow.Add(span).Ticks); }
        public static void Resume() { SetLong("PauseUntil", 0); }

        public static List<string> GetWhitelist() { return GetMulti("Whitelist"); }
        public static void SetWhitelist(List<string> list) { SetMulti("Whitelist", list); }

        private static List<string> GetMulti(string name)
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.OpenSubKey(KeyPath))
            {
                var v = k == null ? null : k.GetValue(name) as string[];
                return v == null ? new List<string>() : v.Where(s => !string.IsNullOrWhiteSpace(s)).ToList();
            }
        }

        private static void SetMulti(string name, List<string> list)
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.CreateSubKey(KeyPath))
                k.SetValue(name, list.ToArray(), RegistryValueKind.MultiString);
        }

        public static List<string> GetDisabledDevices() { return GetMulti("DisabledDevices"); }
        public static List<string> GetDisabledDevicesSafe() { try { return GetDisabledDevices(); } catch { return new List<string>(); } }
        public static void SetDisabledDevices(List<string> list) { SetMulti("DisabledDevices", list); }
        public static void AddDisabledDevice(string id)
        {
            var l = GetDisabledDevices();
            if (!l.Exists(x => x.Equals(id, StringComparison.OrdinalIgnoreCase))) { l.Add(id); SetDisabledDevices(l); }
        }

        /// <summary>Vị trí cổng của các USB lưu trữ đang/vừa cắm (dịch vụ ghi, giao diện đọc), để nhận ra USB đã bị tháo nhưng vẫn cắm.</summary>
        public static List<UsbPortRef> GetSeenUsb()
        {
            var l = new List<UsbPortRef>();
            foreach (var s in GetMulti("SeenUsb")) { var r = UsbPortRef.Parse(s); if (r != null) l.Add(r); }
            return l;
        }
        public static List<UsbPortRef> GetSeenUsbSafe() { try { return GetSeenUsb(); } catch { return new List<UsbPortRef>(); } }
        public static void SetSeenUsb(List<UsbPortRef> list) { SetMulti("SeenUsb", list.ConvertAll(r => r.Serialize())); }

        /// <summary>Số lần nhập sai mật khẩu liên tiếp và thời điểm hết khoá (lưu ở HKLM nên đóng/mở lại phần mềm không xoá được).</summary>
        public static int FailCount { get { return (int)GetLong("AuthFails"); } set { SetLong("AuthFails", value); } }
        public static DateTime LockUntilUtc
        {
            get { long t = GetLong("AuthLockUntil"); try { return t > 0 ? new DateTime(t, DateTimeKind.Utc) : DateTime.MinValue; } catch { return DateTime.MinValue; } }
            set { SetLong("AuthLockUntil", value.Ticks); }
        }

        public static void Delete()
        {
            using (var hk = Reg.Hklm()) hk.DeleteSubKeyTree(KeyPath, false);
        }

        private static string GetString(string name)
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.OpenSubKey(KeyPath)) return k == null ? null : k.GetValue(name) as string;
        }

        private static long GetLong(string name)
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.OpenSubKey(KeyPath))
            {
                var v = k == null ? null : k.GetValue(name);
                return v is long ? (long)v : (v is int ? (int)v : 0L);
            }
        }

        private static void SetString(string name, string v)
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.CreateSubKey(KeyPath)) k.SetValue(name, v, RegistryValueKind.String);
        }

        private static void SetLong(string name, long v)
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.CreateSubKey(KeyPath)) k.SetValue(name, v, RegistryValueKind.QWord);
        }
    }
}

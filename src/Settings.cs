using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Win32;

namespace UsbGuard
{
    /// <summary>Trạng thái lưu ở HKLM\SOFTWARE\UsbGuard (chỉ SYSTEM ghi được sau khi dịch vụ chạy).</summary>
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

        /// <summary>Khoá ACL: chỉ SYSTEM ghi, Administrators chỉ đọc. Dịch vụ gọi lúc khởi động.</summary>
        public static void LockAcl()
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.OpenSubKey(KeyPath, RegistryKeyPermissionCheck.ReadWriteSubTree,
                System.Security.AccessControl.RegistryRights.ChangePermissions |
                System.Security.AccessControl.RegistryRights.ReadKey))
            {
                if (k != null) k.SetAccessControl(Reg.SystemOnlyFullAdminsRead());
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
        public static void PauseFor(TimeSpan span) { SetLong("PauseUntil", DateTime.UtcNow.Add(span).Ticks); }
        public static void Resume() { SetLong("PauseUntil", 0); }

        public static List<string> GetWhitelist()
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.OpenSubKey(KeyPath))
            {
                var v = k == null ? null : k.GetValue("Whitelist") as string[];
                return v == null ? new List<string>() : v.Where(s => !string.IsNullOrWhiteSpace(s)).ToList();
            }
        }

        public static void SetWhitelist(List<string> list)
        {
            using (var hk = Reg.Hklm())
            using (var k = hk.CreateSubKey(KeyPath))
                k.SetValue("Whitelist", list.ToArray(), RegistryValueKind.MultiString);
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

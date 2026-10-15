using System;
using Microsoft.Win32;

namespace UsbGuard
{
    /// <summary>
    /// Lớp chặn thứ nhất, ở mức driver/chính sách: tắt driver USBSTOR + UASPStor và đặt chính sách
    /// "Removable Storage Access" (Deny_All) giống Group Policy. Gọi lặp lại mỗi giây để tự sửa nếu bị đổi.
    /// </summary>
    internal static class Enforcer
    {
        private const string DiskClass = "{53f56307-b6bf-11d0-94f2-00a0c91efb8b}";
        private const string PolicyRoot = @"SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices";
        private static readonly string[] Drivers = { "USBSTOR", "UASPStor" };

        public static void Block()
        {
            using (var hk = Reg.Hklm())
            {
                foreach (var d in Drivers)
                    Reg.SetDword(hk, @"SYSTEM\CurrentControlSet\Services\" + d, "Start", 4, true);
                Reg.SetDword(hk, PolicyRoot, "Deny_All", 1, false);
                var cls = PolicyRoot + "\\" + DiskClass;
                Reg.SetDword(hk, cls, "Deny_Read", 1, false);
                Reg.SetDword(hk, cls, "Deny_Write", 1, false);
                Reg.SetDword(hk, cls, "Deny_Execute", 1, false);
            }
        }

        /// <summary>Trả về mặc định của Windows (dùng khi tạm dừng, chế độ whitelist hoặc gỡ cài đặt).</summary>
        public static void Unblock()
        {
            using (var hk = Reg.Hklm())
            {
                foreach (var d in Drivers)
                    Reg.SetDword(hk, @"SYSTEM\CurrentControlSet\Services\" + d, "Start", 3, true);
                hk.DeleteSubKeyTree(PolicyRoot + "\\" + DiskClass, false);
                using (var k = hk.OpenSubKey(PolicyRoot, true))
                    if (k != null) k.DeleteValue("Deny_All", false);
            }
        }
    }
}

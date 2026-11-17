using System;
using Microsoft.Win32;

namespace UsbGuard
{
    /// <summary>
    /// Các tầng chặn ở mức hệ điều hành, đều là cơ chế chuẩn mà doanh nghiệp vẫn đặt qua Group Policy / Intune:
    ///  1. Tắt driver USBSTOR + UASPStor (Start = 4): Windows không nạp driver cho ổ USB.
    ///  2. Chính sách "Removable Storage Access" (Deny_All): cấm đọc/ghi/chạy trên ổ rời.
    ///  3. Chính sách "Device Installation Restrictions" (DenyDeviceIDs = USB\Class_08...): Windows từ chối
    ///     cài đặt thiết bị lưu trữ USB mới. Chỉ chặn lớp Mass Storage (Class 08), không đụng chuột/bàn phím (Class 03).
    /// Gọi lặp lại mỗi chu kỳ để tự sửa nếu bị đổi tay.
    /// </summary>
    internal static class Enforcer
    {
        private const string DiskClass = "{53f56307-b6bf-11d0-94f2-00a0c91efb8b}";
        private const string PolicyRoot = @"SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices";
        public const string DevInstRoot = @"SOFTWARE\Policies\Microsoft\Windows\DeviceInstall\Restrictions";
        public const string DenyListKey = DevInstRoot + @"\DenyDeviceIDs";
        private static readonly string[] Drivers = { "USBSTOR", "UASPStor" };

        /// <summary>Mã lớp USB Mass Storage (BOT và UAS). Khớp với Compatible ID mà Windows gán cho mọi ổ USB.</summary>
        public static readonly string[] DenyIds =
        {
            @"USB\Class_08&SubClass_06&Prot_50",
            @"USB\Class_08&SubClass_06&Prot_62",
            @"USB\Class_08"
        };
        private const string ValuePrefix = "UsbGuard";

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

                // Tầng 3. Chỉ ghi giá trị mang tên riêng "UsbGuardN" để không đè danh sách của quản trị viên công ty.
                Reg.SetDword(hk, DevInstRoot, "DenyDeviceIDs", 1, false);
                using (var k = hk.CreateSubKey(DenyListKey))
                {
                    for (int i = 0; i < DenyIds.Length; i++)
                    {
                        string name = ValuePrefix + (i + 1);
                        if (!string.Equals(k.GetValue(name) as string, DenyIds[i], StringComparison.Ordinal))
                            k.SetValue(name, DenyIds[i], RegistryValueKind.String);
                    }
                }
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

                bool listEmpty = true;
                using (var k = hk.OpenSubKey(DenyListKey, true))
                {
                    if (k != null)
                    {
                        foreach (var n in k.GetValueNames())
                            if (n.StartsWith(ValuePrefix, StringComparison.OrdinalIgnoreCase)) k.DeleteValue(n, false);
                        listEmpty = k.GetValueNames().Length == 0;
                    }
                }
                // Chỉ gỡ cờ bật chính sách khi danh sách không còn mục nào của người khác.
                if (listEmpty)
                {
                    hk.DeleteSubKeyTree(DenyListKey, false);
                    using (var k = hk.OpenSubKey(DevInstRoot, true))
                        if (k != null) k.DeleteValue("DenyDeviceIDs", false);
                }
            }
        }

        /// <summary>Tầng nào đang bật (dùng cho màn hình trạng thái và kiểm thử).</summary>
        public static string Describe()
        {
            using (var hk = Reg.Hklm())
            {
                int start = -1;
                using (var k = hk.OpenSubKey(@"SYSTEM\CurrentControlSet\Services\USBSTOR"))
                    if (k != null && k.GetValue("Start") is int) start = (int)k.GetValue("Start");
                bool denyAll, denyInstall = false;
                using (var k = hk.OpenSubKey(PolicyRoot)) denyAll = k != null && Equals(k.GetValue("Deny_All"), 1);
                using (var k = hk.OpenSubKey(DenyListKey))
                    if (k != null) foreach (var n in k.GetValueNames())
                        if (n.StartsWith(ValuePrefix, StringComparison.OrdinalIgnoreCase)) denyInstall = true;
                return "Tầng 1 driver USBSTOR: " + (start == 4 ? "TẮT (chặn)" : start == 3 ? "bật (mặc định)" : "Start=" + start) +
                       " | Tầng 2 Deny_All: " + (denyAll ? "BẬT" : "tắt") +
                       " | Tầng 3 cấm cài USB lưu trữ: " + (denyInstall ? "BẬT" : "tắt");
            }
        }
    }
}

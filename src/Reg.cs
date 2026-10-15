using System;
using System.Security.AccessControl;
using System.Security.Principal;
using Microsoft.Win32;

namespace UsbGuard
{
    internal static class Reg
    {
        public static RegistryKey Hklm()
        {
            return RegistryKey.OpenBaseKey(RegistryHive.LocalMachine,
                Environment.Is64BitOperatingSystem ? RegistryView.Registry64 : RegistryView.Default);
        }

        /// <summary>Chỉ ghi khi giá trị khác, để không tạo nhiễu nhật ký registry.</summary>
        public static void SetDword(RegistryKey root, string subKey, string name, int value, bool onlyIfKeyExists)
        {
            RegistryKey k = onlyIfKeyExists ? root.OpenSubKey(subKey, true) : root.CreateSubKey(subKey);
            if (k == null) return;
            using (k)
            {
                var cur = k.GetValue(name);
                if (!(cur is int) || (int)cur != value) k.SetValue(name, value, RegistryValueKind.DWord);
            }
        }

        public static RegistrySecurity SystemOnlyFullAdminsRead()
        {
            var rs = new RegistrySecurity();
            rs.SetAccessRuleProtection(true, false);
            var sys = new SecurityIdentifier(WellKnownSidType.LocalSystemSid, null);
            var adm = new SecurityIdentifier(WellKnownSidType.BuiltinAdministratorsSid, null);
            rs.AddAccessRule(new RegistryAccessRule(sys, RegistryRights.FullControl,
                InheritanceFlags.ContainerInherit, PropagationFlags.None, AccessControlType.Allow));
            rs.AddAccessRule(new RegistryAccessRule(adm, RegistryRights.ReadKey,
                InheritanceFlags.ContainerInherit, PropagationFlags.None, AccessControlType.Allow));
            return rs;
        }
    }
}

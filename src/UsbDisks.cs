using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

namespace UsbGuard
{
    internal sealed class UsbDisk
    {
        public uint DevInst;
        public string Name = "";
        public List<string> Ids = new List<string>();   // ID thiết bị + tổ tiên + serial, dùng so khớp whitelist
        public string Key { get { return Ids.Count > 0 ? Ids[0] : Name; } }
    }

    /// <summary>Lớp chặn thứ hai: tìm mọi ổ đĩa có bus USB và gỡ an toàn (eject) bằng Configuration Manager.</summary>
    internal static class UsbDisks
    {
        private static Guid DiskGuid = new Guid("53f56307-b6bf-11d0-94f2-00a0c91efb8b");
        private const uint DIGCF_PRESENT = 0x2, DIGCF_DEVICEINTERFACE = 0x10;
        private const uint IOCTL_STORAGE_QUERY_PROPERTY = 0x2D1400;
        private const int BusTypeUsb = 7;

        public static List<UsbDisk> Scan()
        {
            var result = new List<UsbDisk>();
            IntPtr set = Native.SetupDiGetClassDevs(ref DiskGuid, IntPtr.Zero, IntPtr.Zero, DIGCF_PRESENT | DIGCF_DEVICEINTERFACE);
            if (set == new IntPtr(-1)) return result;
            try
            {
                for (uint i = 0; ; i++)
                {
                    var ifd = new Native.SP_DEVICE_INTERFACE_DATA { cbSize = Marshal.SizeOf(typeof(Native.SP_DEVICE_INTERFACE_DATA)) };
                    if (!Native.SetupDiEnumDeviceInterfaces(set, IntPtr.Zero, ref DiskGuid, i, ref ifd)) break;

                    var did = new Native.SP_DEVINFO_DATA { cbSize = Marshal.SizeOf(typeof(Native.SP_DEVINFO_DATA)) };
                    uint need;
                    Native.SetupDiGetDeviceInterfaceDetail(set, ref ifd, IntPtr.Zero, 0, out need, ref did);
                    if (need == 0) continue;
                    IntPtr buf = Marshal.AllocHGlobal((int)need);
                    try
                    {
                        Marshal.WriteInt32(buf, IntPtr.Size == 8 ? 8 : 6);   // cbSize của SP_DEVICE_INTERFACE_DETAIL_DATA
                        if (!Native.SetupDiGetDeviceInterfaceDetail(set, ref ifd, buf, need, out need, ref did)) continue;
                        string path = Marshal.PtrToStringUni(buf + 4);
                        var disk = Inspect(path, did.DevInst);
                        if (disk != null) result.Add(disk);
                    }
                    finally { Marshal.FreeHGlobal(buf); }
                }
            }
            finally { Native.SetupDiDestroyDeviceInfoList(set); }
            return result;
        }

        private static UsbDisk Inspect(string path, uint devInst)
        {
            using (var h = Native.CreateFile(path, 0, 3, IntPtr.Zero, 3, 0, IntPtr.Zero))
            {
                if (h.IsInvalid) return null;
                IntPtr q = Marshal.AllocHGlobal(12), o = Marshal.AllocHGlobal(1024);
                try
                {
                    for (int b = 0; b < 12; b++) Marshal.WriteByte(q, b, 0);   // StorageDeviceProperty, PropertyStandardQuery
                    uint ret;
                    if (!Native.DeviceIoControl(h, IOCTL_STORAGE_QUERY_PROPERTY, q, 12, o, 1024, out ret, IntPtr.Zero) || ret < 32)
                        return null;
                    if (Marshal.ReadInt32(o, 28) != BusTypeUsb) return null;

                    var d = new UsbDisk { DevInst = devInst };
                    d.Name = (AnsiAt(o, Marshal.ReadInt32(o, 12)) + " " + AnsiAt(o, Marshal.ReadInt32(o, 16))).Trim();
                    uint node = devInst;
                    for (int depth = 0; depth < 4 && node != 0; depth++)
                    {
                        var sb = new StringBuilder(260);
                        if (Native.CM_Get_Device_ID(node, sb, sb.Capacity, 0) == 0) d.Ids.Add(sb.ToString());
                        uint parent;
                        if (Native.CM_Get_Parent(out parent, node, 0) != 0) break;
                        node = parent;
                    }
                    string serial = AnsiAt(o, Marshal.ReadInt32(o, 24));
                    if (serial.Length > 0) d.Ids.Add(serial);
                    return d;
                }
                finally { Marshal.FreeHGlobal(q); Marshal.FreeHGlobal(o); }
            }
        }

        private static string AnsiAt(IntPtr buf, int offset)
        {
            if (offset <= 0 || offset >= 1024) return "";
            return (Marshal.PtrToStringAnsi(buf + offset) ?? "").Trim();
        }

        /// <summary>Gỡ an toàn: thử nút đĩa rồi lần lượt các nút cha (thiết bị USB). Trả về true nếu Windows chấp nhận.</summary>
        public static bool Eject(UsbDisk d)
        {
            uint node = d.DevInst;
            for (int depth = 0; depth < 4 && node != 0; depth++)
            {
                int veto;
                var name = new StringBuilder(260);
                if (Native.CM_Request_Device_Eject(node, out veto, name, name.Capacity, 0) == 0) return true;
                uint parent;
                if (Native.CM_Get_Parent(out parent, node, 0) != 0) break;
                node = parent;
            }
            // Dự phòng: vô hiệu hoá nút thiết bị bằng pnputil (Windows 10 2004+).
            if (d.Ids.Count > 1)
            {
                string o;
                if (Sys.Run("pnputil.exe", "/disable-device \"" + d.Ids[1] + "\"", out o) == 0) return true;
            }
            return false;
        }
    }
}

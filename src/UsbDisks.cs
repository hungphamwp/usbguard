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
        public int BusType;
        /// <summary>ID của nút đĩa, ID của thiết bị USB cha (nếu có) và số serial — dùng so khớp whitelist.</summary>
        public List<string> Ids = new List<string>();
        public string Key { get { return Ids.Count > 0 ? Ids[0] : Name; } }
        /// <summary>ID của thiết bị USB vật lý (nút cha của nút đĩa), dùng khi phải vô hiệu hoá bằng pnputil.</summary>
        public string UsbDeviceId { get { return Ids.Count > 1 && Ids[1].StartsWith("USB\\", StringComparison.OrdinalIgnoreCase) ? Ids[1] : null; } }
        public bool IsUsb { get { return BusType == UsbDisks.BusTypeUsb; } }
    }

    /// <summary>
    /// Thiết bị USB lớp Mass Storage đang cắm, nhìn từ phía USB (có cả khi Windows không nạp được driver vì đang bị chặn).
    /// </summary>
    internal sealed class UsbStorageDevice
    {
        public uint DevInst;
        public string InstanceId = "";
        public string Name = "";
        public uint Problem;
        public List<string> Ids = new List<string>();

        /// <summary>Số serial lấy từ cuối Instance ID. Windows tự sinh ID có dấu "&amp;" khi thiết bị không có serial.</summary>
        public string Serial
        {
            get
            {
                int i = InstanceId.LastIndexOf('\\');
                string s = i >= 0 ? InstanceId.Substring(i + 1) : "";
                return s.IndexOf('&') >= 0 ? "" : s;
            }
        }

        /// <summary>Mục nên thêm vào whitelist: serial nếu có, không thì VID/PID.</summary>
        public string SuggestedEntry
        {
            get
            {
                if (Whitelist.IsValidEntry(Serial)) return Serial;
                int a = InstanceId.IndexOf("VID_", StringComparison.OrdinalIgnoreCase);
                int b = InstanceId.IndexOf('\\', Math.Max(a, 0));
                return a >= 0 && b > a ? InstanceId.Substring(a, b - a) : InstanceId;
            }
        }
    }

    /// <summary>Lớp chặn thứ hai: tìm mọi ổ đĩa có bus USB và gỡ an toàn (eject) bằng Configuration Manager.</summary>
    internal static class UsbDisks
    {
        private static Guid DiskGuid = new Guid("53f56307-b6bf-11d0-94f2-00a0c91efb8b");
        private const uint DIGCF_PRESENT = 0x2, DIGCF_DEVICEINTERFACE = 0x10;
        private const uint IOCTL_STORAGE_QUERY_PROPERTY = 0x2D1400;
        public const int BusTypeUsb = 7;

        /// <summary>
        /// Chỉ đi lên tối đa 2 nút: nút đĩa (USBSTOR\Disk... hoặc SCSI\Disk... với UAS) và thiết bị USB cha (USB\VID_...).
        /// Không đi tiếp lên hub/root hub: gỡ hub sẽ kéo theo chuột, bàn phím cắm chung hub.
        /// </summary>
        private const int MaxDepth = 2;

        private static readonly string[] BusNames =
        {
            "Unknown", "SCSI", "ATAPI", "ATA", "IEEE1394", "SSA", "Fibre", "USB", "RAID", "iSCSI",
            "SAS", "SATA", "SD", "MMC", "Virtual", "FileBackedVirtual", "Spaces", "NVMe", "SCM", "UFS"
        };

        public static string BusName(int t) { return t >= 0 && t < BusNames.Length ? BusNames[t] : "Bus" + t; }

        /// <summary>Các ổ đĩa đang cắm có bus USB.</summary>
        public static List<UsbDisk> Scan() { return ScanAll().FindAll(d => d.IsUsb); }

        /// <summary>Mọi ổ đĩa đang có mặt (kèm loại bus) — dùng cho lệnh chẩn đoán "devices --all".</summary>
        public static List<UsbDisk> ScanAll()
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
                        // cbSize của SP_DEVICE_INTERFACE_DETAIL_DATA_W: 8 trên tiến trình 64-bit, 6 trên 32-bit.
                        Marshal.WriteInt32(buf, IntPtr.Size == 8 ? 8 : 6);
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
            // Quyền truy cập 0: chỉ hỏi thuộc tính, không đọc dữ liệu trên đĩa.
            using (var h = Native.CreateFile(path, 0, 3, IntPtr.Zero, 3, 0, IntPtr.Zero))
            {
                if (h.IsInvalid) return null;
                IntPtr q = Marshal.AllocHGlobal(12), o = Marshal.AllocHGlobal(1024);
                try
                {
                    for (int b = 0; b < 12; b++) Marshal.WriteByte(q, b, 0);   // StorageDeviceProperty, PropertyStandardQuery
                    for (int b = 0; b < 1024; b++) Marshal.WriteByte(o, b, 0);
                    uint ret;
                    if (!Native.DeviceIoControl(h, IOCTL_STORAGE_QUERY_PROPERTY, q, 12, o, 1024, out ret, IntPtr.Zero) || ret < 32)
                        return null;

                    // STORAGE_DEVICE_DESCRIPTOR: VendorIdOffset@12, ProductIdOffset@16, SerialNumberOffset@24, BusType@28
                    var d = new UsbDisk { DevInst = devInst, BusType = Marshal.ReadInt32(o, 28) };
                    d.Name = (AnsiAt(o, Marshal.ReadInt32(o, 12), ret) + " " + AnsiAt(o, Marshal.ReadInt32(o, 16), ret)).Trim();
                    uint node = devInst;
                    for (int depth = 0; depth < MaxDepth && node != 0; depth++)
                    {
                        var sb = new StringBuilder(260);
                        if (Native.CM_Get_Device_ID(node, sb, sb.Capacity, 0) == 0) d.Ids.Add(sb.ToString());
                        uint parent;
                        if (Native.CM_Get_Parent(out parent, node, 0) != 0) break;
                        node = parent;
                    }
                    string serial = AnsiAt(o, Marshal.ReadInt32(o, 24), ret);
                    if (serial.Length > 0) d.Ids.Add(serial);
                    return d;
                }
                finally { Marshal.FreeHGlobal(q); Marshal.FreeHGlobal(o); }
            }
        }

        private static string AnsiAt(IntPtr buf, int offset, uint valid)
        {
            if (offset <= 0 || offset >= valid || offset >= 1024) return "";
            return (Marshal.PtrToStringAnsi(buf + offset) ?? "").Trim();
        }

        /// <summary>
        /// Gỡ an toàn: thử nút đĩa rồi tới thiết bị USB cha. Nếu Windows từ chối (đang có file mở...),
        /// dự phòng bằng pnputil /disable-device trên đúng thiết bị USB đó và ghi lại để bật lại khi gỡ cài đặt/tạm dừng.
        /// </summary>
        public static bool Eject(UsbDisk d)
        {
            uint node = d.DevInst;
            for (int depth = 0; depth < MaxDepth && node != 0; depth++)
            {
                int veto;
                var name = new StringBuilder(260);
                if (Native.CM_Request_Device_Eject(node, out veto, name, name.Capacity, 0) == 0) return true;
                uint parent;
                if (Native.CM_Get_Parent(out parent, node, 0) != 0) break;
                node = parent;
            }
            string usbId = d.UsbDeviceId;
            if (usbId != null)
            {
                string o;
                if (Sys.Run("pnputil.exe", "/disable-device \"" + usbId + "\"", out o) == 0)
                {
                    Settings.AddDisabledDevice(usbId);
                    return true;
                }
            }
            return false;
        }

        private const uint DIGCF_ALLCLASSES = 0x4;
        private const uint SPDRP_DEVICEDESC = 0x0, SPDRP_HARDWAREID = 0x1, SPDRP_COMPATIBLEIDS = 0x2, SPDRP_FRIENDLYNAME = 0xC;

        /// <summary>
        /// Mọi thiết bị USB lớp Mass Storage (Compatible ID bắt đầu bằng USB\Class_08) đang cắm, kể cả thiết bị
        /// đang lỗi vì bị chặn driver/cài đặt. Dùng để báo người dùng và để quản trị viên lấy ID mà không cần tạm dừng.
        /// </summary>
        public static List<UsbStorageDevice> PresentUsbStorage()
        {
            var result = new List<UsbStorageDevice>();
            IntPtr set = Native.SetupDiGetClassDevsByEnumerator(IntPtr.Zero, "USB", IntPtr.Zero, DIGCF_ALLCLASSES | DIGCF_PRESENT);
            if (set == new IntPtr(-1)) return result;
            try
            {
                for (uint i = 0; ; i++)
                {
                    var did = new Native.SP_DEVINFO_DATA { cbSize = Marshal.SizeOf(typeof(Native.SP_DEVINFO_DATA)) };
                    if (!Native.SetupDiEnumDeviceInfo(set, i, ref did)) break;
                    var compat = MultiSz(set, ref did, SPDRP_COMPATIBLEIDS);
                    if (!compat.Exists(c => c.StartsWith(@"USB\Class_08", StringComparison.OrdinalIgnoreCase))) continue;

                    var dev = new UsbStorageDevice { DevInst = did.DevInst };
                    var sb = new StringBuilder(260);
                    if (Native.CM_Get_Device_ID(did.DevInst, sb, sb.Capacity, 0) == 0) dev.InstanceId = sb.ToString();
                    var names = MultiSz(set, ref did, SPDRP_FRIENDLYNAME);
                    if (names.Count == 0) names = MultiSz(set, ref did, SPDRP_DEVICEDESC);
                    dev.Name = names.Count > 0 ? names[0] : "Thiết bị lưu trữ USB";
                    uint st, prob;
                    if (Native.CM_Get_DevNode_Status(out st, out prob, did.DevInst, 0) == 0) dev.Problem = prob;
                    dev.Ids.Add(dev.InstanceId);
                    dev.Ids.AddRange(MultiSz(set, ref did, SPDRP_HARDWAREID));
                    result.Add(dev);
                }
            }
            finally { Native.SetupDiDestroyDeviceInfoList(set); }
            return result;
        }

        private static List<string> MultiSz(IntPtr set, ref Native.SP_DEVINFO_DATA did, uint prop)
        {
            var list = new List<string>();
            uint type, need;
            var buf = new byte[2048];
            if (!Native.SetupDiGetDeviceRegistryProperty(set, ref did, prop, out type, buf, (uint)buf.Length, out need)) return list;
            foreach (var part in Encoding.Unicode.GetString(buf, 0, (int)Math.Min(need, (uint)buf.Length)).Split('\0'))
                if (part.Length > 0) list.Add(part);
            return list;
        }

        /// <summary>
        /// Sau khi bỏ chặn (tạm dừng, whitelist, gỡ cài đặt): cho Windows thử lại các ổ USB đang cắm mà trước đó
        /// không nạp được driver, để người dùng không phải rút ra cắm lại.
        /// </summary>
        public static void RetryBlockedDevices()
        {
            bool any = false;
            foreach (var d in PresentUsbStorage())
            {
                if (d.Problem == 0 || d.Problem == 22 /* đang bị vô hiệu hoá, ReenableDisabled lo */) continue;
                any = true;
                string o;
                Sys.Run("pnputil.exe", "/restart-device \"" + d.InstanceId + "\"", out o);
            }
            if (any) Sys.Run("pnputil.exe", "/scan-devices");
        }

        /// <summary>Bật lại các thiết bị đã bị vô hiệu hoá bằng pnputil (khi tạm dừng, thêm whitelist, gỡ cài đặt).</summary>
        public static void ReenableDisabled()
        {
            var list = Settings.GetDisabledDevices();
            if (list.Count == 0) return;
            var remain = new List<string>();
            foreach (var id in list)
            {
                string o;
                int rc = Sys.Run("pnputil.exe", "/enable-device \"" + id + "\"", out o);
                if (rc == 0) Log.Info("Đã bật lại thiết bị bị vô hiệu hoá: " + id);
                else if (o.IndexOf("not found", StringComparison.OrdinalIgnoreCase) < 0) remain.Add(id);
            }
            Settings.SetDisabledDevices(remain);
        }
    }
}

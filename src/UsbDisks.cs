using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

namespace UsbGuard
{
    internal sealed class UsbDisk
    {
        public uint DevInst;
        public string Path = "";
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
        public bool Present = true;
        public uint ConfigFlags;
        public bool HasDriver;
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
                    var d = new UsbDisk { DevInst = devInst, Path = path, BusType = Marshal.ReadInt32(o, 28) };
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

        private const uint IOCTL_STORAGE_GET_DEVICE_NUMBER = 0x2D1080;
        private const uint IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS = 0x560000;
        private const uint FSCTL_LOCK_VOLUME = 0x90018, FSCTL_DISMOUNT_VOLUME = 0x90020;

        /// <summary>
        /// Gỡ USB: thử gỡ an toàn (eject) nút đĩa rồi thiết bị USB cha. Nếu Windows từ chối vì đang có file mở trên USB,
        /// buộc tháo các phân vùng của ổ đó (dismount: mọi file đang mở trên USB mất hiệu lực) rồi gỡ lại.
        /// Dự phòng cuối: vô hiệu hoá đúng thiết bị USB đó bằng pnputil và ghi lại để bật lại sau.
        /// </summary>
        public static bool Eject(UsbDisk d)
        {
            string veto;
            if (TryEject(d, out veto)) return true;
            int n = ForceDismount(d);
            if (n > 0) Log.Info("Windows từ chối gỡ " + d.Name + " (" + veto + "): đã tháo và khoá " + n + " phân vùng, không ai truy cập được.");
            System.Threading.Thread.Sleep(300);
            if (TryEject(d, out veto)) { ReleaseLocks(d.Key); return true; }
            if (n > 0 || IsLocked(d.Key)) return true;   // ổ đã bị khoá, chu kỳ sau thử gỡ tiếp

            string usbId = d.UsbDeviceId;
            if (usbId != null)
            {
                string o;
                int rc = Sys.Run("pnputil.exe", "/disable-device \"" + usbId + "\"", out o);
                // 3010 = đã ghi nhận nhưng chờ khởi động lại: vẫn phải ghi lại để sau này bật lại, nếu không USB hỏng luôn.
                if (rc == 0 || rc == 3010) Settings.AddDisabledDevice(usbId);
                if (rc == 0) return true;
            }
            return false;
        }

        private static bool TryEject(UsbDisk d, out string vetoInfo)
        {
            vetoInfo = "";
            uint node = d.DevInst;
            for (int depth = 0; depth < MaxDepth && node != 0; depth++)
            {
                int veto;
                var name = new StringBuilder(260);
                uint cr = Native.CM_Request_Device_Eject(node, out veto, name, name.Capacity, 0);
                if (cr == 0 && veto == 0) return true;
                if (vetoInfo.Length == 0) vetoInfo = "mã " + cr + ", lý do " + veto + (name.Length > 0 ? " " + name : "");
                uint parent;
                if (Native.CM_Get_Parent(out parent, node, 0) != 0) break;
                node = parent;
            }
            return false;
        }

        /// <summary>Khoá đang giữ trên phân vùng của USB chưa gỡ được: (khoá thiết bị, handle phân vùng).</summary>
        private static readonly Dictionary<string, List<Microsoft.Win32.SafeHandles.SafeFileHandle>> Held =
            new Dictionary<string, List<Microsoft.Win32.SafeHandles.SafeFileHandle>>(StringComparer.OrdinalIgnoreCase);

        public static bool IsLocked(string key) { lock (Held) return Held.ContainsKey(key); }

        public static void ReleaseLocks(string key)
        {
            lock (Held)
            {
                List<Microsoft.Win32.SafeHandles.SafeFileHandle> l;
                if (!Held.TryGetValue(key, out l)) return;
                foreach (var h in l) try { h.Dispose(); } catch { }
                Held.Remove(key);
            }
        }

        /// <summary>Thả khoá của những USB không còn cần khoá (đã rút ra, đã được phép, đang tạm dừng).</summary>
        public static void ReleaseLocksExcept(ICollection<string> keepKeys)
        {
            List<string> drop;
            lock (Held) drop = new List<string>(Held.Keys);
            foreach (var k in drop) if (keepKeys == null || !keepKeys.Contains(k)) ReleaseLocks(k);
        }

        /// <summary>
        /// Tháo (dismount) mọi phân vùng trên ổ này: file đang mở trên USB mất hiệu lực. Sau đó khoá phân vùng và GIỮ khoá
        /// (Windows không tự gắn lại được, không ai đọc/ghi được) cho tới khi gỡ được USB hoặc USB bị rút. Trả về số phân vùng đã khoá.
        /// </summary>
        private static int ForceDismount(UsbDisk d)
        {
            if (IsLocked(d.Key)) return 0;
            int diskNo = DiskNumber(d.Path);
            if (diskNo < 0) return 0;
            int count = 0;
            var vn = new StringBuilder(300);
            IntPtr fh = Native.FindFirstVolume(vn, vn.Capacity);
            if (fh == new IntPtr(-1)) return 0;
            try
            {
                do
                {
                    string vol = vn.ToString().TrimEnd('\\');
                    var h = Native.CreateFile(vol, 0xC0000000 /* đọc + ghi */, 3, IntPtr.Zero, 3, 0, IntPtr.Zero);
                    if (h.IsInvalid || !OnDisk(h, diskNo)) { h.Dispose(); continue; }
                    uint ret;
                    bool locked = Native.DeviceIoControl(h, FSCTL_LOCK_VOLUME, IntPtr.Zero, 0, IntPtr.Zero, 0, out ret, IntPtr.Zero);
                    Native.DeviceIoControl(h, FSCTL_DISMOUNT_VOLUME, IntPtr.Zero, 0, IntPtr.Zero, 0, out ret, IntPtr.Zero);
                    // Dismount làm mọi handle khác mất hiệu lực, nên giờ khoá chắc chắn được.
                    if (!locked) locked = Native.DeviceIoControl(h, FSCTL_LOCK_VOLUME, IntPtr.Zero, 0, IntPtr.Zero, 0, out ret, IntPtr.Zero);
                    if (locked)
                    {
                        count++;
                        lock (Held)
                        {
                            List<Microsoft.Win32.SafeHandles.SafeFileHandle> l;
                            if (!Held.TryGetValue(d.Key, out l)) Held[d.Key] = l = new List<Microsoft.Win32.SafeHandles.SafeFileHandle>();
                            l.Add(h);
                        }
                    }
                    else h.Dispose();
                } while (Native.FindNextVolume(fh, vn, vn.Capacity));
            }
            finally { Native.FindVolumeClose(fh); }
            return count;
        }

        private static int DiskNumber(string diskPath)
        {
            if (string.IsNullOrEmpty(diskPath)) return -1;
            using (var h = Native.CreateFile(diskPath, 0, 3, IntPtr.Zero, 3, 0, IntPtr.Zero))
            {
                if (h.IsInvalid) return -1;
                IntPtr o = Marshal.AllocHGlobal(12);
                try
                {
                    uint ret;
                    return Native.DeviceIoControl(h, IOCTL_STORAGE_GET_DEVICE_NUMBER, IntPtr.Zero, 0, o, 12, out ret, IntPtr.Zero)
                        ? Marshal.ReadInt32(o, 4) : -1;
                }
                finally { Marshal.FreeHGlobal(o); }
            }
        }

        private static bool OnDisk(Microsoft.Win32.SafeHandles.SafeFileHandle vol, int diskNo)
        {
            IntPtr o = Marshal.AllocHGlobal(512);
            try
            {
                uint ret;
                if (!Native.DeviceIoControl(vol, IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS, IntPtr.Zero, 0, o, 512, out ret, IntPtr.Zero)) return false;
                int n = Marshal.ReadInt32(o, 0);
                for (int i = 0; i < n && 8 + i * 24 + 4 <= 512; i++)
                    if (Marshal.ReadInt32(o, 8 + i * 24) == diskNo) return true;   // DISK_EXTENT: DiskNumber, (pad), StartingOffset, ExtentLength
                return false;
            }
            finally { Marshal.FreeHGlobal(o); }
        }

        private const uint DIGCF_ALLCLASSES = 0x4;
        private const uint SPDRP_DEVICEDESC = 0x0, SPDRP_HARDWAREID = 0x1, SPDRP_COMPATIBLEIDS = 0x2, SPDRP_DRIVER = 0x9,
            SPDRP_CONFIGFLAGS = 0xA, SPDRP_FRIENDLYNAME = 0xC;
        private const uint CONFIGFLAG_DISABLED = 0x1, CONFIGFLAG_FAILEDINSTALL = 0x40;
        private const uint CM_PROB_FAILED_INSTALL = 28, CM_PROB_DISABLED = 22;

        /// <summary>
        /// Mọi thiết bị USB lớp Mass Storage (Compatible ID bắt đầu bằng USB\Class_08) đang cắm, kể cả thiết bị
        /// đang lỗi vì bị chặn driver/cài đặt. Dùng để báo người dùng và để quản trị viên lấy ID mà không cần tạm dừng.
        /// </summary>
        public static List<UsbStorageDevice> PresentUsbStorage() { return UsbStorageNodes(true); }

        /// <summary>Nút thiết bị USB lưu trữ: chỉ đang cắm, hoặc cả các nút Windows còn nhớ từ những lần cắm trước.</summary>
        public static List<UsbStorageDevice> UsbStorageNodes(bool presentOnly)
        {
            var result = new List<UsbStorageDevice>();
            IntPtr set = Native.SetupDiGetClassDevsByEnumerator(IntPtr.Zero, "USB", IntPtr.Zero, DIGCF_ALLCLASSES | (presentOnly ? DIGCF_PRESENT : 0));
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
                    else dev.Present = false;
                    var cf = Prop(set, ref did, SPDRP_CONFIGFLAGS);
                    if (cf != null && cf.Length >= 4) dev.ConfigFlags = BitConverter.ToUInt32(cf, 0);
                    dev.HasDriver = MultiSz(set, ref did, SPDRP_DRIVER).Count > 0;
                    dev.Ids.Add(dev.InstanceId);
                    dev.Ids.AddRange(MultiSz(set, ref did, SPDRP_HARDWAREID));
                    result.Add(dev);
                }
            }
            finally { Native.SetupDiDestroyDeviceInfoList(set); }
            return result;
        }

        private static byte[] Prop(IntPtr set, ref Native.SP_DEVINFO_DATA did, uint prop)
        {
            uint type, need;
            var buf = new byte[64];
            if (!Native.SetupDiGetDeviceRegistryProperty(set, ref did, prop, out type, buf, (uint)buf.Length, out need)) return null;
            Array.Resize(ref buf, (int)Math.Min(need, 64));
            return buf;
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
        /// Sau khi bỏ chặn (tạm dừng, whitelist, gỡ cài đặt): cho Windows nạp lại các ổ USB đã bị chặn để dùng được ngay.
        ///  - Đang cắm, bị chặn vì driver tắt (mã 32...): khởi động lại thiết bị.
        ///  - Từng bị tầng 3 cấm cài (chưa có driver / cờ "cài thất bại"): xoá nút thiết bị để Windows cài lại như USB mới,
        ///    kể cả nút của USB đã rút ra (nếu không, lần cắm sau Windows vẫn nhớ là "cài thất bại" và không thử lại).
        /// </summary>
        public static void RetryBlockedDevices()
        {
            bool rescan = false;
            var mine = new HashSet<string>(Settings.GetDisabledDevicesSafe(), StringComparer.OrdinalIgnoreCase);
            foreach (var d in UsbStorageNodes(false))
            {
                if (mine.Contains(d.InstanceId)) continue;                       // ReenableDisabled lo
                bool failedInstall = !d.HasDriver || (d.ConfigFlags & CONFIGFLAG_FAILEDINSTALL) != 0 || d.Problem == CM_PROB_FAILED_INSTALL;
                string o;
                if (failedInstall)
                {
                    int rc = Sys.Run("pnputil.exe", "/remove-device \"" + d.InstanceId + "\"", out o);
                    Log.Info("Cho Windows cài lại USB từng bị cấm cài (" + (d.Present ? "đang cắm" : "đã rút") + "): " + d.InstanceId + " (mã " + rc + ")");
                    rescan |= d.Present;
                }
                else if (d.Present && d.Problem != 0 && d.Problem != CM_PROB_DISABLED)
                {
                    Sys.Run("pnputil.exe", "/restart-device \"" + d.InstanceId + "\"", out o);
                    rescan = true;
                }
            }
            if (rescan) Sys.Run("pnputil.exe", "/scan-devices");
        }

        /// <summary>Cho Windows nạp lại 1 thiết bị: chưa cài được thì xoá nút cho cài lại, không thì khởi động lại.</summary>
        public static void Kick(UsbStorageDevice d)
        {
            string o;
            if (!d.HasDriver || d.Problem == CM_PROB_FAILED_INSTALL || (d.ConfigFlags & CONFIGFLAG_FAILEDINSTALL) != 0)
            {
                Sys.Run("pnputil.exe", "/remove-device \"" + d.InstanceId + "\"", out o);
                Sys.Run("pnputil.exe", "/scan-devices");
            }
            else Sys.Run("pnputil.exe", "/restart-device \"" + d.InstanceId + "\"", out o);
        }

        /// <summary>
        /// Bật lại các thiết bị UsbGuard đã phải vô hiệu hoá bằng pnputil. allow = null: bật lại tất cả.
        /// Thiết bị không bật lại được (đã rút ra) thì xoá nút thiết bị để lần cắm sau Windows nhận lại bình thường.
        /// </summary>
        public static void ReenableDisabled(Func<string, bool> allow = null)
        {
            var list = Settings.GetDisabledDevices();
            if (list.Count == 0) return;
            var remain = new List<string>();
            foreach (var id in list)
            {
                if (allow != null && !allow(id)) { remain.Add(id); continue; }
                string o;
                int rc = Sys.Run("pnputil.exe", "/enable-device \"" + id + "\"", out o);
                if (rc != 0 && rc != 3010) rc = Sys.Run("pnputil.exe", "/remove-device \"" + id + "\"", out o);
                if (rc == 0 || rc == 3010) Log.Info("Đã bật lại thiết bị từng bị vô hiệu hoá: " + id);
                else remain.Add(id);
            }
            Settings.SetDisabledDevices(remain);
            Sys.Run("pnputil.exe", "/scan-devices");
        }
    }
}

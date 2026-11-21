using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

namespace UsbGuard
{
    /// <summary>Vị trí vật lý của 1 USB: hub nó cắm vào và số cổng trên hub.</summary>
    internal sealed class UsbPortRef
    {
        public string InstanceId = "";   // USB\VID_xxxx&PID_yyyy\serial
        public string HubId = "";        // Instance ID của hub
        public int Port;
        public string Name = "";

        public string Vid { get { return Part("VID_"); } }
        public string Pid { get { return Part("PID_"); } }

        private string Part(string tag)
        {
            int i = InstanceId.IndexOf(tag, StringComparison.OrdinalIgnoreCase);
            return i >= 0 && i + 8 <= InstanceId.Length ? InstanceId.Substring(i + 4, 4).ToUpperInvariant() : "";
        }

        public string Serialize() { return InstanceId + "|" + HubId + "|" + Port + "|" + Name.Replace("|", " "); }

        public static UsbPortRef Parse(string s)
        {
            var p = (s ?? "").Split('|');
            int port;
            if (p.Length < 3 || !int.TryParse(p[2], out port) || port <= 0) return null;
            return new UsbPortRef { InstanceId = p[0], HubId = p[1], Port = port, Name = p.Length > 3 ? p[3] : "" };
        }
    }

    /// <summary>
    /// Làm việc với cổng USB qua driver hub (giống công cụ USBView của Microsoft):
    ///  - Biết USB còn cắm trong cổng hay không, kể cả khi Windows đã "tháo an toàn" nó (không còn trong Device Manager).
    ///  - "Rút ra cắm lại bằng phần mềm" (cycle port): Windows nhận lại USB như vừa cắm vào, người dùng không phải rút tay.
    /// </summary>
    internal static class UsbPorts
    {
        private static Guid HubGuid = new Guid("f18a0e88-c30c-11d0-8815-00a0c906bed8");
        private const uint IOCTL_USB_GET_NODE_CONNECTION_INFORMATION = 0x22040C;
        private const uint IOCTL_USB_HUB_CYCLE_PORT = 0x220444;
        private const uint CM_DRP_ADDRESS = 0x1D;

        /// <summary>Lấy vị trí cổng của nút thiết bị USB (nếu là 1 giao diện của thiết bị tổng hợp thì lấy nút cha).</summary>
        public static UsbPortRef Locate(uint devInst)
        {
            try
            {
                string id = DeviceId(devInst);
                if (id.IndexOf("&MI_", StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    uint p;
                    if (Native.CM_Get_Parent(out p, devInst, 0) != 0) return null;
                    devInst = p; id = DeviceId(devInst);
                }
                uint hub;
                if (Native.CM_Get_Parent(out hub, devInst, 0) != 0) return null;
                var buf = new byte[4];
                uint len = 4, type;
                if (Native.CM_Get_DevNode_Registry_Property(devInst, CM_DRP_ADDRESS, out type, buf, ref len, 0) != 0) return null;
                int port = BitConverter.ToInt32(buf, 0);
                if (port <= 0 || port > 255) return null;
                return new UsbPortRef { InstanceId = id, HubId = DeviceId(hub), Port = port };
            }
            catch { return null; }
        }

        private static string DeviceId(uint devInst)
        {
            var sb = new StringBuilder(260);
            return Native.CM_Get_Device_ID(devInst, sb, sb.Capacity, 0) == 0 ? sb.ToString() : "";
        }

        private static string HubPath(string hubId)
        {
            uint size;
            if (Native.CM_Get_Device_Interface_List_Size(out size, ref HubGuid, hubId, 0) != 0 || size <= 1) return null;
            var buf = new char[size];
            if (Native.CM_Get_Device_Interface_List(ref HubGuid, hubId, buf, size, 0) != 0) return null;
            string s = new string(buf);
            int z = s.IndexOf('\0');
            s = z >= 0 ? s.Substring(0, z) : s;
            return s.Length > 0 ? s : null;
        }

        /// <summary>
        /// USB đúng hãng/mẫu này có đang cắm trong cổng đó không (đọc mô tả thiết bị từ hub, không cần Windows đang dùng nó).
        /// </summary>
        public static bool IsConnected(UsbPortRef r)
        {
            string path = HubPath(r.HubId);
            if (path == null) return false;
            using (var h = Native.CreateFile(path, 0x40000000 /* ghi */, 2, IntPtr.Zero, 3, 0, IntPtr.Zero))
            {
                if (h.IsInvalid) return false;
                const int size = 512;
                IntPtr b = Marshal.AllocHGlobal(size);
                try
                {
                    for (int i = 0; i < size; i++) Marshal.WriteByte(b, i, 0);
                    Marshal.WriteInt32(b, 0, r.Port);
                    uint ret;
                    if (!Native.DeviceIoControl(h, IOCTL_USB_GET_NODE_CONNECTION_INFORMATION, b, size, b, size, out ret, IntPtr.Zero) || ret < 35)
                        return false;
                    // USB_NODE_CONNECTION_INFORMATION (pack 1): ConnectionIndex@0, DeviceDescriptor@4 (idVendor@12, idProduct@14), ConnectionStatus@31
                    int status = Marshal.ReadInt32(b, 31);
                    if (status != 1) return false;   // 1 = DeviceConnected
                    string vid = ((ushort)Marshal.ReadInt16(b, 12)).ToString("X4"), pid = ((ushort)Marshal.ReadInt16(b, 14)).ToString("X4");
                    return (r.Vid.Length == 0 || vid == r.Vid) && (r.Pid.Length == 0 || pid == r.Pid);
                }
                finally { Marshal.FreeHGlobal(b); }
            }
        }

        /// <summary>Cho Windows nhận lại USB như vừa rút ra cắm vào (chỉ đúng cổng đó, không ảnh hưởng thiết bị khác trên hub).</summary>
        public static bool Cycle(UsbPortRef r)
        {
            string path = HubPath(r.HubId);
            if (path == null) return false;
            using (var h = Native.CreateFile(path, 0x40000000, 2, IntPtr.Zero, 3, 0, IntPtr.Zero))
            {
                if (h.IsInvalid) return false;
                IntPtr b = Marshal.AllocHGlobal(8);
                try
                {
                    Marshal.WriteInt32(b, 0, r.Port);
                    Marshal.WriteInt32(b, 4, 0);
                    uint ret;
                    return Native.DeviceIoControl(h, IOCTL_USB_HUB_CYCLE_PORT, b, 8, b, 8, out ret, IntPtr.Zero);
                }
                finally { Marshal.FreeHGlobal(b); }
            }
        }

        /// <summary>Nạp lại hub (dự phòng khi không cycle được cổng).</summary>
        public static void RescanHub(UsbPortRef r)
        {
            uint dn;
            if (Native.CM_Locate_DevNode(out dn, r.HubId, 0) == 0) Native.CM_Reenumerate_DevNode(dn, 0);
        }

        /// <summary>
        /// USB lưu trữ từng thấy mà giờ Windows không còn nhận (đã bị tháo an toàn) nhưng vẫn đang cắm trong cổng.
        /// Không có danh sách này thì USB "biến mất" khỏi phần mềm dù vẫn cắm trên máy.
        /// </summary>
        public static List<UsbPortRef> ConnectedButGone(List<UsbStorageDevice> present)
        {
            var result = new List<UsbPortRef>();
            var seen = Settings.GetSeenUsbSafe();
            foreach (var r in seen)
            {
                bool usable = present.Exists(d => d.Problem == 0 && SameDevice(d, r));
                bool listed = present.Exists(d => SameDevice(d, r));
                if (usable || listed) continue;
                try { if (IsConnected(r)) result.Add(r); } catch { }
            }
            return result;
        }

        public static bool SameDevice(UsbStorageDevice d, UsbPortRef r)
        {
            return d.InstanceId.Equals(r.InstanceId, StringComparison.OrdinalIgnoreCase) ||
                   (d.Port != null && d.Port.InstanceId.Equals(r.InstanceId, StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>Biến vị trí cổng thành mục hiển thị trong danh sách USB (trạng thái: bị tháo khỏi Windows).</summary>
        public static UsbStorageDevice AsDevice(UsbPortRef r)
        {
            var d = new UsbStorageDevice
            {
                InstanceId = r.InstanceId,
                Name = r.Name.Length > 0 ? r.Name : "Thiết bị lưu trữ USB",
                Problem = UsbDisks.ProblemHeldForEject,
                Ejected = true,
                Port = r
            };
            d.Ids.Add(r.InstanceId);
            if (r.Vid.Length > 0) d.Ids.Add(@"USB\VID_" + r.Vid + "&PID_" + r.Pid);
            return d;
        }
    }
}

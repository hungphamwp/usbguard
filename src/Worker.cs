using System;
using System.Collections.Generic;
using System.Management;
using System.ServiceProcess;
using System.Timers;

namespace UsbGuard
{
    /// <summary>
    /// Thân dịch vụ. Mỗi chu kỳ (2 giây, và ngay lập tức khi Windows báo có ổ đĩa mới qua WMI):
    ///  - Đang tạm dừng: trả USB về mặc định Windows, bật lại thiết bị đã bị vô hiệu hoá.
    ///  - Whitelist rỗng (chế độ CHẶN TẤT CẢ): tắt driver USBSTOR/UASPStor + chính sách Deny_All, gỡ mọi ổ USB.
    ///  - Whitelist có mục (chế độ DANH SÁCH CHO PHÉP): để driver chạy (USB được phép mới dùng được),
    ///    gỡ ngay ổ USB nào không khớp whitelist.
    ///
    /// "Không tắt được": dịch vụ khai báo CanStop = false nên Windows từ chối lệnh Stop
    /// (sc stop / services.msc báo lỗi 1052), kể cả với Administrator. Người dùng thường thì ngay cả
    /// quyền gửi lệnh tới dịch vụ cũng không có (lỗi 5 Access denied). Nếu tiến trình bị kill,
    /// cấu hình phục hồi (sc failure) cho Windows tự khởi động lại sau 5 giây.
    /// Cách duy nhất để dừng là "UsbGuard.exe uninstall" với đúng mật khẩu quản trị: lệnh đó bật cờ
    /// Uninstalling, dịch vụ thấy cờ thì tự dừng.
    /// </summary>
    public sealed class Worker : ServiceBase
    {
        private readonly Timer _timer = new Timer(2000);
        private readonly object _gate = new object();
        /// <summary>Thiết bị đã được báo trong lần cắm hiện tại; rút ra thì xoá khỏi đây để lần cắm sau báo lại.</summary>
        private readonly HashSet<string> _notified = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        private bool _wasBlocking = true;
        private readonly HashSet<string> _kicked = new HashSet<string>(StringComparer.OrdinalIgnoreCase);   // lần đầu không chặn thì thử nạp lại thiết bị đã lỗi từ trước
        private ManagementEventWatcher _watcher;
        private bool _busy;
        private bool _interactive;
        private string _mode = "";

        public Worker()
        {
            ServiceName = Hardening.ServiceName;
            CanStop = false;               // từ chối lệnh Stop từ SCM
            CanPauseAndContinue = false;
            CanShutdown = false;
            AutoLog = false;
        }

        protected override void OnStart(string[] args)
        {
            Log.Info("Dịch vụ khởi động (phiên bản " + Program.Version + ").");
            try { Settings.LockAcl(); } catch (Exception ex) { Log.Warn("Không đặt được ACL cho khoá cấu hình: " + ex.Message); }
            Tick(null, null);
            _timer.Elapsed += Tick;
            _timer.AutoReset = true;
            _timer.Start();
            StartWatcher();
        }

        protected override void OnStop()
        {
            _timer.Stop();
            StopWatcher();
            Log.Info("Dịch vụ dừng (theo lệnh uninstall có mật khẩu).");
        }

        /// <summary>Nghe sự kiện "có ổ đĩa mới" của WMI để phản ứng gần như tức thì thay vì chờ chu kỳ 2 giây.</summary>
        private void StartWatcher()
        {
            try
            {
                var q = new WqlEventQuery("SELECT * FROM __InstanceCreationEvent WITHIN 1 WHERE TargetInstance ISA 'Win32_DiskDrive'");
                _watcher = new ManagementEventWatcher(q);
                _watcher.EventArrived += (s, e) => Tick(null, null);
                _watcher.Start();
            }
            catch (Exception ex)
            {
                _watcher = null;
                Log.Warn("Không bật được theo dõi WMI, chỉ dùng chu kỳ 2 giây: " + ex.Message);
            }
        }

        private void StopWatcher()
        {
            try { if (_watcher != null) { _watcher.Stop(); _watcher.Dispose(); } } catch { }
            _watcher = null;
        }

        private void Tick(object sender, ElapsedEventArgs e)
        {
            lock (_gate) { if (_busy) return; _busy = true; }
            try
            {
                if (!Settings.Exists()) return;
                if (Settings.Uninstalling)
                {
                    if (!_interactive) { _timer.Stop(); Stop(); }
                    return;
                }

                if (Settings.IsPaused)
                {
                    bool changed = SetMode("TẠM DỪNG");
                    Enforcer.Unblock();
                    if (changed) UsbDisks.ReenableDisabled();
                    AfterUnblock();
                    _notified.Clear();
                    return;
                }

                var whitelist = Settings.GetWhitelist();
                if (whitelist.Count == 0)
                {
                    SetMode("CHẶN TẤT CẢ");
                    Enforcer.Block();
                    _wasBlocking = true;
                }
                else
                {
                    SetMode("DANH SÁCH CHO PHÉP (" + whitelist.Count + " mục)");
                    Enforcer.Unblock();
                    AfterUnblock();
                    // USB vừa được thêm vào whitelist mà trước đó UsbGuard đã phải vô hiệu hoá: bật lại.
                    if (Settings.GetDisabledDevices().Exists(id => Whitelist.Matches(new[] { id }, whitelist)))
                        UsbDisks.ReenableDisabled(id => Whitelist.Matches(new[] { id }, whitelist));
                }

                // Lớp gỡ: ổ USB nào đã lên được (driver chạy) mà không có trong whitelist thì gỡ ngay.
                foreach (var disk in UsbDisks.Scan())
                {
                    if (Whitelist.Matches(disk.Ids, whitelist)) continue;
                    bool ok = UsbDisks.Eject(disk);
                    string key = disk.UsbDeviceId ?? disk.Key;
                    if (_notified.Add(key))
                    {
                        Log.Warn((ok ? "Đã gỡ thiết bị USB không được phép: " : "Phát hiện USB không được phép nhưng gỡ thất bại: ")
                                 + disk.Name + " | ID: " + string.Join(" ; ", disk.Ids));
                        Notify(disk.Name);
                    }
                }

                // Thiết bị bị chặn ngay từ driver (không bao giờ thành ổ đĩa): vẫn báo người dùng 1 lần mỗi lần cắm.
                var present = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                foreach (var dev in UsbDisks.PresentUsbStorage())
                {
                    present.Add(dev.InstanceId);
                    if (Whitelist.Matches(dev.Ids, whitelist))
                    {
                        // USB được phép nhưng đang lỗi (bị gỡ/bị chặn trước khi được thêm vào danh sách): nạp lại 1 lần.
                        if (dev.Problem != 0 && dev.Problem != 22 && _kicked.Add(dev.InstanceId))
                        {
                            Log.Info("Nạp lại USB được phép: " + dev.Name + " | " + dev.InstanceId);
                            UsbDisks.Kick(dev);
                        }
                        continue;
                    }
                    if (dev.Problem != 0 && _notified.Add(dev.InstanceId))
                    {
                        Log.Warn("Đã chặn thiết bị USB lưu trữ (Windows không nạp driver, mã lỗi thiết bị " + dev.Problem + "): "
                                 + dev.Name + " | ID: " + dev.InstanceId);
                        Notify(dev.Name);
                    }
                }
                _notified.RemoveWhere(k => !present.Contains(k));
                _kicked.RemoveWhere(k => !present.Contains(k));
            }
            catch (Exception ex)
            {
                Log.Warn("Lỗi trong vòng kiểm tra: " + ex.Message);
            }
            finally
            {
                lock (_gate) { _busy = false; }
            }
        }

        /// <summary>Vừa chuyển từ chặn sang không chặn: cho Windows nạp lại driver các ổ USB đang cắm.</summary>
        private void AfterUnblock()
        {
            if (!_wasBlocking) return;
            _wasBlocking = false;
            try { UsbDisks.RetryBlockedDevices(); } catch (Exception ex) { Log.Warn("Không nạp lại được thiết bị USB: " + ex.Message); }
        }

        private bool SetMode(string mode)
        {
            if (mode == _mode) return false;
            _mode = mode;
            Log.Info("Chế độ: " + mode);
            return true;
        }

        /// <summary>Báo cho người đang ngồi máy biết USB bị chặn (hộp thoại tự đóng sau 15 giây, không chờ trả lời).</summary>
        private void Notify(string deviceName)
        {
            if (_interactive) { Console.WriteLine("[UsbGuard] Chặn: " + deviceName); return; }
            try
            {
                const string title = "UsbGuard";
                string msg = "Thiết bị lưu trữ USB \"" + deviceName + "\" không được phép sử dụng trên máy này nên đã bị chặn.\n" +
                             "Liên hệ quản trị viên nếu bạn cần dùng thiết bị này.";
                uint resp;
                uint session = Native.WTSGetActiveConsoleSessionId();
                if (session != 0xFFFFFFFF)
                    Native.WTSSendMessage(IntPtr.Zero, session, title, title.Length * 2, msg, msg.Length * 2,
                        0x30 /* MB_ICONWARNING */, 15, out resp, false);
            }
            catch { }
        }

        /// <summary>Chạy thử trực tiếp trong console (không cần cài đặt) để debug trên máy dev.</summary>
        public void RunInteractive()
        {
            _interactive = true;
            Console.WriteLine("Chạy chế độ console. Nhấn Enter để dừng.");
            OnStart(null);
            Console.ReadLine();
            OnStop();
        }
    }
}

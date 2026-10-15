using System;
using System.ServiceProcess;
using System.Timers;

namespace UsbGuard
{
    /// <summary>
    /// Thân dịch vụ. Mỗi chu kỳ (2 giây):
    ///  1) Nếu không bị tạm dừng: khoá lại driver USBSTOR/chính sách (tự sửa nếu ai đó đổi registry tay).
    ///  2) Quét các ổ đĩa USB đang cắm; ổ nào không có trong whitelist thì gỡ an toàn (eject).
    /// Nếu đang tạm dừng (Settings.IsPaused) hoặc whitelist rỗng và chế độ là "chặn tất cả" thì xử lý tương ứng.
    /// </summary>
    public sealed class Worker : ServiceBase
    {
        private readonly Timer _timer = new Timer(2000);
        private readonly object _gate = new object();
        private bool _busy;

        public Worker()
        {
            ServiceName = Hardening.ServiceName;
            CanStop = true;
            CanPauseAndContinue = false;
            AutoLog = false;
        }

        protected override void OnStart(string[] args)
        {
            Log.Info("Dịch vụ khởi động.");
            Tick(null, null);
            _timer.Elapsed += Tick;
            _timer.AutoReset = true;
            _timer.Start();
        }

        protected override void OnStop()
        {
            _timer.Stop();
            Log.Info("Dịch vụ dừng (do Administrator).");
        }

        private void Tick(object sender, ElapsedEventArgs e)
        {
            lock (_gate) { if (_busy) return; _busy = true; }
            try
            {
                if (!Settings.Exists() || Settings.Uninstalling) return;

                if (Settings.IsPaused)
                {
                    Enforcer.Unblock();
                    return;
                }

                Enforcer.Block();

                var whitelist = Settings.GetWhitelist();
                foreach (var disk in UsbDisks.Scan())
                {
                    if (Whitelist.Matches(disk.Ids, whitelist)) continue;
                    if (UsbDisks.Eject(disk))
                        Log.Warn("Đã gỡ thiết bị USB không được phép: " + disk.Name + " (" + disk.Key + ")");
                    else
                        Log.Warn("Phát hiện thiết bị USB không được phép nhưng gỡ thất bại: " + disk.Name);
                }
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

        /// <summary>Cho phép chạy thử trực tiếp trong console (không cần cài đặt) để debug trên máy dev.</summary>
        public void RunInteractive()
        {
            Console.WriteLine("Chạy chế độ console (Ctrl+C để thoát). Nhấn Enter để dừng.");
            OnStart(null);
            Console.ReadLine();
            OnStop();
        }
    }
}

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Windows.Forms;

namespace UsbGuard
{
    /// <summary>
    /// Giao diện quản lý cho người không rành dòng lệnh. Mọi thao tác dùng chung lõi với dòng lệnh
    /// (Settings, Auth, Installer), thao tác thay đổi đều hỏi mật khẩu quản trị.
    /// </summary>
    internal static class Gui
    {
        public static int Launch()
        {
            // Mở từ Start Menu thì Windows tạo sẵn 1 cửa sổ console chỉ cho riêng tiến trình này: đóng nó đi.
            try
            {
                var ids = new uint[4];
                if (Native.GetConsoleProcessList(ids, 4) == 1) Native.FreeConsole();
            }
            catch { }

            if (!Installer.IsAdmin())
            {
                // Tự xin quyền Administrator (hộp thoại UAC) rồi mở lại.
                try
                {
                    Process.Start(new ProcessStartInfo(Assembly.GetExecutingAssembly().Location, "gui")
                    { UseShellExecute = true, Verb = "runas" });
                    return 0;
                }
                catch
                {
                    MessageBox.Show("UsbGuard cần quyền Administrator để quản lý.", "UsbGuard",
                        MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return 5;
                }
            }

            var t = new Thread(() =>
            {
                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);
                Application.Run(new MainForm());
            });
            t.SetApartmentState(ApartmentState.STA);
            t.Start();
            t.Join();
            return 0;
        }

        /// <summary>Gọi hàm lõi (vốn in ra console) và lấy lại chữ nó in để hiện lên hộp thoại.</summary>
        public static int Captured(Func<int> f, out string text)
        {
            var old = Console.Out;
            var sw = new StringWriter();
            Console.SetOut(sw);
            try { return f(); }
            catch (Exception ex) { sw.WriteLine("Lỗi: " + ex.Message); return -1; }
            finally { Console.SetOut(old); text = sw.ToString().Trim(); }
        }

        public static Icon AppIcon()
        {
            try { return Icon.ExtractAssociatedIcon(Assembly.GetExecutingAssembly().Location); } catch { return null; }
        }
    }

    internal sealed class MainForm : Form
    {
        private static readonly Color Red = Color.FromArgb(192, 57, 43), Green = Color.FromArgb(39, 174, 96),
            Amber = Color.FromArgb(211, 132, 0), Grey = Color.FromArgb(110, 110, 110), Blue = Color.FromArgb(31, 78, 121);

        private readonly Panel _header = new Panel { Dock = DockStyle.Top, Height = 92, Padding = new Padding(18, 12, 18, 10) };
        private readonly Label _title = new Label { AutoSize = true, Font = new Font("Segoe UI", 16f, FontStyle.Bold), ForeColor = Color.White };
        private readonly Label _sub = new Label { AutoSize = true, Font = new Font("Segoe UI", 9.5f), ForeColor = Color.White };

        private readonly ListView _devices = new ListView { Dock = DockStyle.Fill, View = View.Details, FullRowSelect = true, MultiSelect = false, HideSelection = false };
        private readonly ListBox _whitelist = new ListBox { Dock = DockStyle.Fill, IntegralHeight = false };
        private readonly TextBox _log = new TextBox { Dock = DockStyle.Fill, Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Both, WordWrap = false, Font = new Font("Consolas", 9f), BackColor = Color.White };

        private readonly Button _btnInstall = Btn("Cài đặt…"), _btnPause = Btn("Tạm dừng chặn…"), _btnResume = Btn("Bật lại chặn"),
            _btnPw = Btn("Đổi mật khẩu…"), _btnUninstall = Btn("Gỡ cài đặt…"), _btnAllow = Btn("Cho phép USB đã chọn"),
            _btnAdd = Btn("Thêm theo ID…"), _btnRemove = Btn("Xoá mục đã chọn"), _btnOpenLog = Btn("Mở thư mục nhật ký");

        private readonly System.Windows.Forms.Timer _timer = new System.Windows.Forms.Timer { Interval = 2000 };
        private string _lastLog = "";

        private static Button Btn(string text)
        {
            return new Button { Text = text, AutoSize = true, Height = 32, Padding = new Padding(8, 0, 8, 0), Margin = new Padding(0, 0, 8, 0), Font = new Font("Segoe UI", 9.5f) };
        }

        public MainForm()
        {
            Text = "UsbGuard " + Program.Version + " - Quản lý chặn USB";
            Font = new Font("Segoe UI", 9.5f);
            StartPosition = FormStartPosition.CenterScreen;
            ClientSize = new Size(900, 600);
            MinimumSize = new Size(760, 520);
            var ic = Gui.AppIcon(); if (ic != null) Icon = ic;

            var hb = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.TopDown, WrapContents = false, BackColor = Color.Transparent };
            hb.Controls.Add(_title); hb.Controls.Add(_sub);
            _header.Controls.Add(hb);

            var tabs = new TabControl { Dock = DockStyle.Fill, Padding = new Point(14, 6) };

            // Tab 1: USB đang cắm
            _devices.Columns.Add("Thiết bị", 260);
            _devices.Columns.Add("Trạng thái", 150);
            _devices.Columns.Add("Số serial / ID", 420);
            var t1 = new TabPage("USB đang cắm") { Padding = new Padding(10) };
            var t1Bar = Bar(_btnAllow);
            var t1Hint = Hint("Cắm USB cần cho phép vào máy (không cần tạm dừng), chọn nó trong danh sách rồi bấm \"Cho phép USB đã chọn\". " +
                              "Từ đó chỉ USB trong danh sách cho phép mới dùng được, mọi USB khác vẫn bị chặn.");
            t1.Controls.Add(_devices); t1.Controls.Add(t1Hint); t1.Controls.Add(t1Bar);

            // Tab 2: danh sách cho phép
            var t2 = new TabPage("Danh sách cho phép") { Padding = new Padding(10) };
            var t2Hint = Hint("Danh sách trống = chặn TẤT CẢ USB lưu trữ. Có ít nhất 1 mục = chỉ cho phép đúng các USB này.");
            t2.Controls.Add(_whitelist); t2.Controls.Add(t2Hint); t2.Controls.Add(Bar(_btnAdd, _btnRemove));

            // Tab 3: nhật ký
            var t3 = new TabPage("Nhật ký") { Padding = new Padding(10) };
            t3.Controls.Add(_log); t3.Controls.Add(Bar(_btnOpenLog));

            tabs.TabPages.Add(t1); tabs.TabPages.Add(t2); tabs.TabPages.Add(t3);

            var bottom = new FlowLayoutPanel { Dock = DockStyle.Bottom, Height = 52, Padding = new Padding(12, 10, 12, 8) };
            bottom.Controls.AddRange(new Control[] { _btnInstall, _btnPause, _btnResume, _btnPw, _btnUninstall });

            Controls.Add(tabs);
            Controls.Add(bottom);
            Controls.Add(_header);

            _btnInstall.Click += (s, e) => DoInstall();
            _btnPause.Click += (s, e) => DoPause();
            _btnResume.Click += (s, e) => { if (Ask("Bật lại chặn USB ngay")) { Settings.Resume(); Log.Info("Bật lại chặn USB (qua giao diện)."); RefreshAll(); } };
            _btnPw.Click += (s, e) => DoChangePassword();
            _btnUninstall.Click += (s, e) => DoUninstall();
            _btnAllow.Click += (s, e) => DoAllowSelected();
            _btnAdd.Click += (s, e) => DoAddById();
            _btnRemove.Click += (s, e) => DoRemove();
            _btnOpenLog.Click += (s, e) => { try { Directory.CreateDirectory(Log.DataDir); Process.Start("explorer.exe", Log.DataDir); } catch { } };
            _timer.Tick += (s, e) => RefreshAll();
            Load += (s, e) => { RefreshAll(); _timer.Start(); };
        }

        private static FlowLayoutPanel Bar(params Button[] buttons)
        {
            var p = new FlowLayoutPanel { Dock = DockStyle.Bottom, Height = 44, Padding = new Padding(0, 8, 0, 0) };
            p.Controls.AddRange(buttons);
            return p;
        }

        private static Label Hint(string text)
        {
            return new Label { Text = text, Dock = DockStyle.Top, Height = 44, ForeColor = Color.FromArgb(70, 70, 70) };
        }

        private bool _svcRunning = true;
        private DateTime _lastSvcStart = DateTime.MinValue;

        private static bool Installed()
        {
            try { return Installer.ServiceExists() && Settings.Exists(); } catch { return false; }
        }

        private void RefreshAll()
        {
            bool inst = Installed();
            string svc = "";
            if (inst)
            {
                _svcRunning = Installer.ServiceRunning();
                if (!_svcRunning && DateTime.UtcNow - _lastSvcStart > TimeSpan.FromSeconds(15))
                {
                    // Dịch vụ bị đặt Disabled rồi khởi động lại máy (hoặc chưa kịp chạy): không có dịch vụ thì
                    // cho phép/tạm dừng không có tác dụng (USB kẹt "Đang nạp lại…"). Bật lại ngay, không cần mật khẩu
                    // vì việc này chỉ làm máy được bảo vệ chặt hơn.
                    _lastSvcStart = DateTime.UtcNow;
                    string fx = "";
                    try { fx = Installer.RepairServiceConfig(); } catch { }
                    int rc = Sys.Run("sc.exe", "start " + Hardening.ServiceName);
                    Log.Warn("Giao diện thấy dịch vụ UsbGuard không chạy" + (fx.Length > 0 ? " (" + fx + ")" : "") + ", đã bật lại (sc start mã " + rc + ").");
                    _svcRunning = Installer.ServiceRunning();
                }
                svc = _svcRunning ? "Dịch vụ đang chạy, không tắt được" : "CẢNH BÁO: dịch vụ không chạy, thay đổi chưa có tác dụng";
            }

            List<string> wl = inst ? Settings.GetWhitelist() : new List<string>();
            if (!inst)
            {
                SetHeader(Grey, "CHƯA CÀI ĐẶT", "Bấm \"Cài đặt…\" để bật chặn USB trên máy này. Phiên bản " + Program.Version);
            }
            else if (Settings.IsPaused)
            {
                SetHeader(Amber, "ĐANG TẠM DỪNG CHẶN", "USB dùng bình thường đến " + Settings.PauseUntilUtc.ToLocalTime().ToString("HH:mm dd/MM/yyyy") +
                          ", sau đó tự chặn lại. Muốn chặn ngay: bấm \"Bật lại chặn\". " + svc + ".");
            }
            else if (wl.Count == 0)
            {
                SetHeader(Red, "ĐANG CHẶN TẤT CẢ USB LƯU TRỮ", "Chuột, bàn phím, máy in vẫn dùng bình thường. " + svc + ".");
            }
            else
            {
                SetHeader(Green, "CHỈ CHO PHÉP " + wl.Count + " USB TRONG DANH SÁCH", "Mọi USB lưu trữ khác đều bị chặn. " + svc + ".");
            }

            _btnInstall.Visible = !inst;
            foreach (var b in new[] { _btnPause, _btnResume, _btnPw, _btnUninstall, _btnAllow, _btnAdd, _btnRemove }) b.Enabled = inst;
            _btnResume.Enabled = inst && Settings.IsPaused;

            // Danh sách thiết bị: giữ nguyên dòng đang chọn.
            string sel = _devices.SelectedItems.Count > 0 ? (string)_devices.SelectedItems[0].Tag : null;
            List<UsbStorageDevice> devs;
            try { devs = UsbDisks.ListForDisplay(); } catch { devs = new List<UsbStorageDevice>(); }
            string sig = string.Join("|", devs.Select(d => d.InstanceId + d.Problem)) + "#" + string.Join("|", wl) + Settings.IsPausedSafe() + _svcRunning;
            if (!sig.Equals(_devices.Tag as string))
            {
                _devices.Tag = sig;
                _devices.BeginUpdate();
                _devices.Items.Clear();
                foreach (var d in devs)
                {
                    bool allowed = Whitelist.Matches(d.Ids, wl);
                    bool paused = Settings.IsPausedSafe();
                    string st = d.Problem == 0 ? (allowed ? "Được phép" : "Đang dùng được")
                              : (allowed || paused) && !_svcRunning ? "Chờ dịch vụ chạy"
                              : allowed || paused ? "Đang nạp lại…"
                              : d.Ejected ? "Bị chặn (đã tháo)" : "Bị chặn";
                    var it = new ListViewItem(new[] { d.Name, st, d.Serial.Length > 0 ? d.Serial : d.InstanceId }) { Tag = d.InstanceId };
                    it.ForeColor = allowed ? Green : d.Problem == 0 ? Color.Black : Red;
                    if (d.InstanceId == sel) it.Selected = true;
                    _devices.Items.Add(it);
                }
                if (devs.Count == 0) _devices.Items.Add(new ListViewItem(new[] { "(Không có USB lưu trữ nào đang cắm)", "", "" }) { ForeColor = Grey });
                _devices.EndUpdate();
            }

            string wsig = string.Join("|", wl);
            if (!wsig.Equals(_whitelist.Tag as string))
            {
                _whitelist.Tag = wsig;
                _whitelist.Items.Clear();
                foreach (var w in wl) _whitelist.Items.Add(w);
            }

            try
            {
                string path = Path.Combine(Log.DataDir, "usbguard.log");
                string txt = File.Exists(path) ? string.Join(Environment.NewLine, File.ReadAllLines(path).Reverse().Take(300)) : "(chưa có nhật ký)";
                if (txt != _lastLog) { _lastLog = txt; _log.Text = txt; }
            }
            catch { }
        }

        private void SetHeader(Color c, string title, string sub)
        {
            _header.BackColor = c; _title.Text = title; _sub.Text = sub;
        }

        /// <summary>Hỏi mật khẩu quản trị. Sai nhiều lần thì bị khoá tăng dần (30 giây, 1 phút, 2 phút... tối đa 1 giờ), lưu trong HKLM.</summary>
        private bool Ask(string action)
        {
            var until = Settings.LockUntilUtc;
            if (until > DateTime.UtcNow)
            {
                Msg("Nhập sai mật khẩu quá nhiều lần. Thử lại sau " + Auth.Describe(until - DateTime.UtcNow) + ".", MessageBoxIcon.Warning);
                return false;
            }
            string pw = PasswordDialog.Ask(this, action, "Nhập mật khẩu quản trị UsbGuard:");
            if (pw == null) return false;
            string err;
            bool ok;
            Cursor = Cursors.WaitCursor;
            try { ok = AdminAuth.Check(pw, "giao diện: " + action, out err); } finally { Cursor = Cursors.Default; }
            if (ok) return true;
            Msg(err, MessageBoxIcon.Error);
            return false;
        }

        private void Msg(string text, MessageBoxIcon icon)
        {
            MessageBox.Show(this, text, "UsbGuard", MessageBoxButtons.OK, icon);
        }

        private void DoInstall()
        {
            var pws = PasswordDialog.AskNew(this, "Cài đặt UsbGuard", "Đặt mật khẩu quản trị (ít nhất 8 ký tự). Ghi lại mật khẩu này, quên thì không gỡ được.");
            if (pws == null) return;
            string text;
            int rc = Gui.Captured(() => Installer.Install(pws), out text);
            Msg(rc == 0 ? "Đã cài đặt. Từ giờ mọi USB lưu trữ đều bị chặn." : text, rc == 0 ? MessageBoxIcon.Information : MessageBoxIcon.Error);
            RefreshAll();
        }

        private void DoPause()
        {
            int minutes = PauseDialog.Ask(this);
            if (minutes <= 0 || !Ask("Tạm dừng chặn " + minutes + " phút")) return;
            Settings.PauseFor(TimeSpan.FromMinutes(minutes));
            Log.Info("Tạm dừng chặn USB trong " + minutes + " phút (qua giao diện).");
            RefreshAll();
        }

        private void DoChangePassword()
        {
            if (!Ask("Đổi mật khẩu")) return;
            var pw = PasswordDialog.AskNew(this, "Đổi mật khẩu", "Mật khẩu mới (ít nhất 8 ký tự):");
            if (pw == null) return;
            Settings.SetAuthHash(Auth.Hash(pw));
            Log.Info("Đổi mật khẩu quản trị (qua giao diện).");
            Msg("Đã đổi mật khẩu.", MessageBoxIcon.Information);
        }

        private void DoAllowSelected()
        {
            if (_devices.SelectedItems.Count == 0 || _devices.SelectedItems[0].Tag == null)
            { Msg("Chọn 1 USB trong danh sách trước.", MessageBoxIcon.Information); return; }
            string id = (string)_devices.SelectedItems[0].Tag;
            var dev = UsbDisks.ListForDisplay().FirstOrDefault(d => d.InstanceId == id);
            if (dev == null) { Msg("USB đã bị rút ra.", MessageBoxIcon.Information); return; }
            string entry = dev.SuggestedEntry;
            if (!Whitelist.IsValidEntry(entry)) { Msg("Không lấy được ID hợp lệ của USB này.", MessageBoxIcon.Error); return; }
            if (dev.Serial.Length == 0 &&
                MessageBox.Show(this, "USB này không có số serial nên sẽ cho phép theo mã hãng/mẫu (" + entry + "): " +
                    "mọi USB cùng hãng, cùng mẫu cũng được dùng. Tiếp tục?", "UsbGuard", MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes)
                return;
            if (!Ask("Cho phép USB \"" + dev.Name + "\"")) return;
            AddEntry(entry);
            Msg("Đã cho phép USB này. Ổ sẽ hiện trong This PC sau vài giây, không cần rút ra cắm lại.", MessageBoxIcon.Information);
        }

        private void DoAddById()
        {
            string entry = TextDialog.Ask(this, "Thêm vào danh sách cho phép", "Số serial hoặc ID thiết bị (ví dụ VID_0951&PID_1666):");
            if (entry == null) return;
            entry = entry.Trim();
            if (!Whitelist.IsValidEntry(entry)) { Msg("ID quá ngắn (tối thiểu " + Whitelist.MinEntryLength + " ký tự).", MessageBoxIcon.Error); return; }
            if (!Ask("Thêm \"" + entry + "\" vào danh sách cho phép")) return;
            AddEntry(entry);
        }

        private void AddEntry(string entry)
        {
            var list = Settings.GetWhitelist();
            if (!list.Any(x => x.Equals(entry, StringComparison.OrdinalIgnoreCase))) list.Add(entry);
            Settings.SetWhitelist(list);
            Log.Info("Thêm whitelist: " + entry + " (qua giao diện).");
            RefreshAll();
        }

        private void DoRemove()
        {
            var entry = _whitelist.SelectedItem as string;
            if (entry == null) { Msg("Chọn 1 mục trong danh sách trước.", MessageBoxIcon.Information); return; }
            if (!Ask("Xoá \"" + entry + "\" khỏi danh sách cho phép")) return;
            var list = Settings.GetWhitelist();
            list.RemoveAll(x => x.Equals(entry, StringComparison.OrdinalIgnoreCase));
            Settings.SetWhitelist(list);
            Log.Info("Xoá whitelist: " + entry + " (qua giao diện).");
            RefreshAll();
        }

        private void DoUninstall()
        {
            // Cài bằng setup.exe: dùng trình gỡ của bộ cài để xoá luôn mục trong "Apps & features" (trình gỡ tự hỏi mật khẩu).
            string unins = Path.Combine(Installer.InstallDir, "unins000.exe");
            if (File.Exists(unins))
            {
                try { Process.Start(unins); Close(); } catch (Exception ex) { Msg(ex.Message, MessageBoxIcon.Error); }
                return;
            }
            if (MessageBox.Show(this, "Gỡ UsbGuard khỏi máy này? USB sẽ dùng lại bình thường.", "UsbGuard",
                    MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;
            string pw = PasswordDialog.Ask(this, "Gỡ cài đặt", "Nhập mật khẩu quản trị UsbGuard:");
            if (pw == null) return;
            string text;
            int rc = Gui.Captured(() => Installer.Uninstall(pw), out text);
            Msg(text, rc == 0 ? MessageBoxIcon.Information : MessageBoxIcon.Error);
            RefreshAll();
        }

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            _timer.Stop();
            base.OnFormClosed(e);
        }
    }

    /// <summary>Hộp thoại nhỏ dùng chung: 1 hoặc 2 ô nhập.</summary>
    internal static class PasswordDialog
    {
        public static string Ask(IWin32Window owner, string title, string label)
        {
            var r = Show(owner, title, label, null, true);
            return r == null ? null : r[0];
        }

        /// <summary>Hỏi mật khẩu mới 2 lần, kiểm tra độ dài và khớp nhau.</summary>
        public static string AskNew(IWin32Window owner, string title, string label)
        {
            while (true)
            {
                var r = Show(owner, title, label, "Nhập lại mật khẩu:", true);
                if (r == null) return null;
                if (r[0].Length < 8) { MessageBox.Show(owner, "Mật khẩu phải có ít nhất 8 ký tự.", "UsbGuard"); continue; }
                if (r[0] != r[1]) { MessageBox.Show(owner, "Mật khẩu nhập lại không khớp.", "UsbGuard"); continue; }
                return r[0];
            }
        }

        internal static string[] Show(IWin32Window owner, string title, string label1, string label2, bool secret)
        {
            using (var f = new Form { Text = title, FormBorderStyle = FormBorderStyle.FixedDialog, MaximizeBox = false, MinimizeBox = false,
                       StartPosition = FormStartPosition.CenterParent, ClientSize = new Size(420, label2 == null ? 150 : 210),
                       Font = new Font("Segoe UI", 9.5f), ShowInTaskbar = false })
            {
                var l1 = new Label { Text = label1, Left = 16, Top = 14, Width = 388, Height = 38 };
                var t1 = new TextBox { Left = 16, Top = 54, Width = 388, UseSystemPasswordChar = secret };
                f.Controls.Add(l1); f.Controls.Add(t1);
                TextBox t2 = null;
                if (label2 != null)
                {
                    f.Controls.Add(new Label { Text = label2, Left = 16, Top = 88, Width = 388 });
                    t2 = new TextBox { Left = 16, Top = 112, Width = 388, UseSystemPasswordChar = secret };
                    f.Controls.Add(t2);
                }
                int y = label2 == null ? 100 : 160;
                var ok = new Button { Text = "Đồng ý", DialogResult = DialogResult.OK, Left = 228, Top = y, Width = 84, Height = 30 };
                var cancel = new Button { Text = "Huỷ", DialogResult = DialogResult.Cancel, Left = 320, Top = y, Width = 84, Height = 30 };
                f.Controls.Add(ok); f.Controls.Add(cancel);
                f.AcceptButton = ok; f.CancelButton = cancel;
                if (f.ShowDialog(owner) != DialogResult.OK) return null;
                return new[] { t1.Text, t2 == null ? null : t2.Text };
            }
        }
    }

    internal static class TextDialog
    {
        public static string Ask(IWin32Window owner, string title, string label)
        {
            var r = PasswordDialog.Show(owner, title, label, null, false);
            return r == null ? null : r[0];
        }
    }

    internal static class PauseDialog
    {
        public static int Ask(IWin32Window owner)
        {
            using (var f = new Form { Text = "Tạm dừng chặn", FormBorderStyle = FormBorderStyle.FixedDialog, MaximizeBox = false, MinimizeBox = false,
                       StartPosition = FormStartPosition.CenterParent, ClientSize = new Size(380, 140), Font = new Font("Segoe UI", 9.5f), ShowInTaskbar = false })
            {
                f.Controls.Add(new Label { Text = "Cho dùng USB trong bao nhiêu phút? Hết giờ UsbGuard tự chặn lại.", Left = 16, Top = 14, Width = 350, Height = 40 });
                var n = new NumericUpDown { Left = 16, Top = 58, Width = 90, Minimum = 1, Maximum = 1440, Value = 15 };
                f.Controls.Add(n);
                f.Controls.Add(new Label { Text = "phút (tối đa 1440 = 1 ngày)", Left = 114, Top = 61, Width = 250 });
                var ok = new Button { Text = "Tiếp tục", DialogResult = DialogResult.OK, Left = 188, Top = 96, Width = 84, Height = 30 };
                var cancel = new Button { Text = "Huỷ", DialogResult = DialogResult.Cancel, Left = 280, Top = 96, Width = 84, Height = 30 };
                f.Controls.Add(ok); f.Controls.Add(cancel); f.AcceptButton = ok; f.CancelButton = cancel;
                return f.ShowDialog(owner) == DialogResult.OK ? (int)n.Value : 0;
            }
        }
    }
}

using System;

namespace UsbGuard
{
    /// <summary>
    /// Kiểm tra mật khẩu quản trị dùng chung cho giao diện, dòng lệnh và trình gỡ cài đặt. Đếm số lần sai trong HKLM
    /// (người dùng thường không sửa được), khoá tăng dần để không dò được mật khẩu bằng cách thử liên tục.
    /// </summary>
    internal static class AdminAuth
    {
        private static readonly object Gate = new object();

        public static bool Check(string password, string source, out string error)
        {
            lock (Gate)
            {
                error = null;
                var until = Settings.LockUntilUtc;
                if (until > DateTime.UtcNow)
                {
                    error = "Nhập sai mật khẩu quá nhiều lần. Thử lại sau " + Auth.Describe(until - DateTime.UtcNow) + ".";
                    return false;
                }
                string stored = Settings.AuthHash;
                if (Auth.Verify(password, stored))
                {
                    if (Settings.FailCount != 0) Settings.FailCount = 0;
                    if (Settings.LockUntilUtc != DateTime.MinValue) Settings.LockUntilUtc = DateTime.MinValue;
                    if (Auth.NeedsRehash(stored))
                    {
                        try { Settings.SetAuthHash(Auth.Hash(password)); Log.Info("Đã nâng cấp cách lưu mật khẩu quản trị lên PBKDF2-SHA256."); }
                        catch { }
                    }
                    return true;
                }
                int fails = Settings.FailCount + 1;
                Settings.FailCount = fails;
                int lockSec = Auth.LockSeconds(fails);
                if (lockSec > 0) Settings.LockUntilUtc = DateTime.UtcNow.AddSeconds(lockSec);
                Log.Warn("Nhập sai mật khẩu quản trị (" + source + "), lần sai liên tiếp thứ " + fails +
                         (lockSec > 0 ? ", khoá " + Auth.Describe(TimeSpan.FromSeconds(lockSec)) : "") + ".");
                error = "Sai mật khẩu quản trị." + (lockSec > 0 ? " Đã sai " + fails + " lần liên tiếp, thử lại sau " + Auth.Describe(TimeSpan.FromSeconds(lockSec)) + "." : "");
                return false;
            }
        }
    }
}

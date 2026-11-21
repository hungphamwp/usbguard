using System;
using System.Security.Cryptography;

namespace UsbGuard
{
    /// <summary>
    /// Băm và kiểm tra mật khẩu quản trị: PBKDF2-HMAC-SHA256, muối ngẫu nhiên 16 byte, 600.000 vòng (mức OWASP khuyến nghị).
    /// Vẫn đọc được mã băm cũ của bản 1.0/1.1 (PBKDF2-SHA1) và tự nâng cấp ở lần nhập đúng kế tiếp.
    /// </summary>
    public static class Auth
    {
        public const int Iterations = 600000;
        private const string Sha256Tag = "pbkdf2-sha256", Sha1Tag = "pbkdf2";

        /// <summary>Số lần sai được phép trước khi bắt đầu khoá.</summary>
        public const int FreeAttempts = 4;
        public const int MaxLockSeconds = 3600;

        public static string Hash(string password)
        {
            var salt = new byte[16];
            using (var rng = RandomNumberGenerator.Create()) rng.GetBytes(salt);
            return Sha256Tag + "$" + Iterations + "$" + Convert.ToBase64String(salt) + "$" +
                   Convert.ToBase64String(Derive(password, salt, Iterations, true));
        }

        public static bool Verify(string password, string stored)
        {
            if (string.IsNullOrEmpty(stored) || password == null) return false;
            var p = stored.Split('$');
            if (p.Length != 4 || (p[0] != Sha256Tag && p[0] != Sha1Tag)) return false;
            int iter;
            if (!int.TryParse(p[1], out iter) || iter < 1000 || iter > 10000000) return false;
            byte[] salt, expected;
            try { salt = Convert.FromBase64String(p[2]); expected = Convert.FromBase64String(p[3]); }
            catch (FormatException) { return false; }
            return ConstantTimeEquals(Derive(password, salt, iter, p[0] == Sha256Tag), expected);
        }

        /// <summary>Mã băm cũ hoặc ít vòng hơn hiện tại: nên băm lại khi người dùng nhập đúng.</summary>
        public static bool NeedsRehash(string stored)
        {
            var p = (stored ?? "").Split('$');
            int iter;
            return p.Length != 4 || p[0] != Sha256Tag || !int.TryParse(p[1], out iter) || iter < Iterations;
        }

        /// <summary>
        /// Thời gian khoá sau lần sai thứ <paramref name="fails"/> liên tiếp: 4 lần đầu không khoá, lần 5 khoá 30 giây,
        /// mỗi lần sai tiếp theo gấp đôi (1 phút, 2 phút, 4 phút...), tối đa 1 giờ. Đóng mở lại phần mềm không xoá được.
        /// </summary>
        public static int LockSeconds(int fails)
        {
            if (fails <= FreeAttempts) return 0;
            int n = fails - FreeAttempts - 1;
            return n >= 7 ? MaxLockSeconds : Math.Min(MaxLockSeconds, 30 << n);
        }

        public static string Describe(TimeSpan t)
        {
            int s = (int)Math.Ceiling(t.TotalSeconds);
            return s < 60 ? s + " giây" : (s + 59) / 60 + " phút";
        }

        private static byte[] Derive(string pw, byte[] salt, int iter, bool sha256)
        {
            using (var kdf = sha256 ? new Rfc2898DeriveBytes(pw, salt, iter, HashAlgorithmName.SHA256) : new Rfc2898DeriveBytes(pw, salt, iter))
                return kdf.GetBytes(32);
        }

        private static bool ConstantTimeEquals(byte[] a, byte[] b)
        {
            if (a.Length != b.Length) return false;
            int diff = 0;
            for (int i = 0; i < a.Length; i++) diff |= a[i] ^ b[i];
            return diff == 0;
        }
    }
}

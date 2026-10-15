using System;
using System.Security.Cryptography;

namespace UsbGuard
{
    /// <summary>Băm và kiểm tra mật khẩu quản trị (PBKDF2-SHA1, có muối).</summary>
    public static class Auth
    {
        private const int Iterations = 100000;

        public static string Hash(string password)
        {
            var salt = new byte[16];
            using (var rng = RandomNumberGenerator.Create()) rng.GetBytes(salt);
            return Format(Iterations, salt, Derive(password, salt, Iterations));
        }

        public static bool Verify(string password, string stored)
        {
            if (string.IsNullOrEmpty(stored) || password == null) return false;
            var p = stored.Split('$');
            if (p.Length != 4 || p[0] != "pbkdf2") return false;
            int iter;
            if (!int.TryParse(p[1], out iter) || iter < 1000) return false;
            byte[] salt, expected;
            try { salt = Convert.FromBase64String(p[2]); expected = Convert.FromBase64String(p[3]); }
            catch (FormatException) { return false; }
            return ConstantTimeEquals(Derive(password, salt, iter), expected);
        }

        private static byte[] Derive(string pw, byte[] salt, int iter)
        {
            using (var kdf = new Rfc2898DeriveBytes(pw, salt, iter)) return kdf.GetBytes(32);
        }

        private static string Format(int iter, byte[] salt, byte[] hash)
        {
            return "pbkdf2$" + iter + "$" + Convert.ToBase64String(salt) + "$" + Convert.ToBase64String(hash);
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

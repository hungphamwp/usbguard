using System;
using System.Text;

namespace UsbGuard
{
    /// <summary>
    /// Lấy mật khẩu quản trị: từ đối số dòng lệnh (tiện cho script) hoặc hỏi trực tiếp, không hiện ký tự
    /// (tránh lộ mật khẩu trong lịch sử lệnh và danh sách tiến trình).
    /// </summary>
    internal static class Password
    {
        public static string FromArgs(string[] args, int index, string prompt)
        {
            return args.Length > index ? args[index] : Ask(prompt);
        }

        public static string Ask(string prompt)
        {
            Console.Write(prompt);
            if (Console.IsInputRedirected) { string line = Console.ReadLine(); return line ?? ""; }
            var sb = new StringBuilder();
            while (true)
            {
                var k = Console.ReadKey(true);
                if (k.Key == ConsoleKey.Enter) break;
                if (k.Key == ConsoleKey.Backspace) { if (sb.Length > 0) sb.Length--; continue; }
                if (!char.IsControl(k.KeyChar)) sb.Append(k.KeyChar);
            }
            Console.WriteLine();
            return sb.ToString();
        }
    }
}

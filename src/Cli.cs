using System;
using System.Collections.Generic;
using System.Linq;

namespace UsbGuard
{
    /// <summary>Các lệnh quản trị gọi tới dịch vụ đang chạy, thông qua Settings (HKLM), có xác thực mật khẩu.</summary>
    internal static class Cli
    {
        private static bool CheckAuth(string password)
        {
            if (!Settings.Exists()) { Console.WriteLine("UsbGuard chưa được cài đặt."); return false; }
            if (!Auth.Verify(password, Settings.AuthHash)) { Console.WriteLine("Sai mật khẩu quản trị."); return false; }
            return true;
        }

        public static int Pause(string[] args)
        {
            if (args.Length < 3) { Console.WriteLine("Dùng: UsbGuard.exe pause <phut> <mat_khau>"); return 1; }
            int minutes;
            if (!int.TryParse(args[1], out minutes) || minutes <= 0 || minutes > 24 * 60)
            {
                Console.WriteLine("Số phút không hợp lệ (1 - 1440).");
                return 1;
            }
            if (!CheckAuth(args[2])) return 3;
            Settings.PauseFor(TimeSpan.FromMinutes(minutes));
            Log.Info("Tạm dừng chặn USB trong " + minutes + " phút (qua CLI).");
            Console.WriteLine("Đã tạm dừng chặn USB trong " + minutes + " phút.");
            return 0;
        }

        public static int Resume(string[] args)
        {
            if (args.Length < 2) { Console.WriteLine("Dùng: UsbGuard.exe resume <mat_khau>"); return 1; }
            if (!CheckAuth(args[1])) return 3;
            Settings.Resume();
            Log.Info("Bật lại chặn USB (qua CLI).");
            Console.WriteLine("Đã bật lại chặn USB.");
            return 0;
        }

        public static int Whitelist(string[] args)
        {
            if (args.Length < 2) { PrintWhitelistUsage(); return 1; }
            string sub = args[1].ToLowerInvariant();

            if (sub == "list")
            {
                if (!Settings.Exists()) { Console.WriteLine("UsbGuard chưa được cài đặt."); return 1; }
                var list = Settings.GetWhitelist();
                Console.WriteLine(list.Count + " thiết bị trong whitelist:");
                foreach (var w in list) Console.WriteLine("  - " + w);
                return 0;
            }

            if (sub == "add" || sub == "remove")
            {
                if (args.Length < 4) { PrintWhitelistUsage(); return 1; }
                string entry = args[2].Trim();
                string password = args[3];
                if (!CheckAuth(password)) return 3;
                if (sub == "add" && !UsbGuard.Whitelist.IsValidEntry(entry))
                {
                    Console.WriteLine("ID thiết bị quá ngắn (tối thiểu " + UsbGuard.Whitelist.MinEntryLength + " ký tự). " +
                        "Ví dụ: VID_0951&PID_1666 hoặc số serial lấy từ 'UsbGuard.exe status' sau khi cắm thử.");
                    return 1;
                }

                var list = Settings.GetWhitelist();
                if (sub == "add")
                {
                    if (!list.Any(x => x.Equals(entry, StringComparison.OrdinalIgnoreCase))) list.Add(entry);
                }
                else
                {
                    list.RemoveAll(x => x.Equals(entry, StringComparison.OrdinalIgnoreCase));
                }
                Settings.SetWhitelist(list);
                Log.Info((sub == "add" ? "Thêm" : "Xoá") + " whitelist: " + entry + " (qua CLI).");
                Console.WriteLine("OK.");
                return 0;
            }

            PrintWhitelistUsage();
            return 1;
        }

        public static int ChangePassword(string[] args)
        {
            if (args.Length < 3) { Console.WriteLine("Dùng: UsbGuard.exe passwd <mat_khau_cu> <mat_khau_moi>"); return 1; }
            if (!CheckAuth(args[1])) return 3;
            string newPw = args[2];
            if (newPw.Length < 8) { Console.WriteLine("Mật khẩu mới phải có ít nhất 8 ký tự."); return 1; }
            Settings.SetAuthHash(Auth.Hash(newPw));
            Log.Info("Đổi mật khẩu quản trị (qua CLI).");
            Console.WriteLine("Đã đổi mật khẩu.");
            return 0;
        }

        private static void PrintWhitelistUsage()
        {
            Console.WriteLine("Dùng:");
            Console.WriteLine("  UsbGuard.exe whitelist list");
            Console.WriteLine("  UsbGuard.exe whitelist add <id_thiet_bi> <mat_khau>");
            Console.WriteLine("  UsbGuard.exe whitelist remove <id_thiet_bi> <mat_khau>");
        }
    }
}

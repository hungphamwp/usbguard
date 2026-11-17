using System;
using System.ServiceProcess;

namespace UsbGuard
{
    public static class Program
    {
        public const string Version = "1.0.0";

        public static int Main(string[] args)
        {
            if (args.Length == 0)
            {
                // Không có đối số: SCM (Service Control Manager) gọi theo cách này khi khởi động dịch vụ.
                if (Environment.UserInteractive)
                {
                    PrintUsage();
                    return 1;
                }
                ServiceBase.Run(new Worker());
                return 0;
            }

            try { Console.OutputEncoding = System.Text.Encoding.UTF8; } catch { }
            string cmd = args[0].ToLowerInvariant();
            switch (cmd)
            {
                case "--console":
                    new Worker().RunInteractive();
                    return 0;

                case "install":
                {
                    string pw = Password.FromArgs(args, 1, "Đặt mật khẩu quản trị (ít nhất 8 ký tự): ");
                    if (args.Length <= 1 && pw != Password.Ask("Nhập lại mật khẩu: "))
                    {
                        Console.WriteLine("Mật khẩu nhập lại không khớp.");
                        return 1;
                    }
                    return Installer.Install(pw);
                }

                case "uninstall":
                    return Installer.Uninstall(Password.FromArgs(args, 1, "Mật khẩu quản trị: "));

                case "devices":
                    return Cli.Devices(args);

                case "status":
                    return Installer.Status();

                case "pause":
                    return Cli.Pause(args);

                case "resume":
                    return Cli.Resume(args);

                case "whitelist":
                    return Cli.Whitelist(args);

                case "passwd":
                    return Cli.ChangePassword(args);

                case "version":
                    Console.WriteLine("UsbGuard " + Version);
                    return 0;

                default:
                    PrintUsage();
                    return 1;
            }
        }

        private static void PrintUsage()
        {
            Console.OutputEncoding = System.Text.Encoding.UTF8;
            Console.WriteLine("UsbGuard " + Version + " - Chan thiet bi luu tru USB tren Windows (chay nhu dich vu)");
            Console.WriteLine();
            Console.WriteLine("Cach dung (chay voi quyen Administrator):");
            Console.WriteLine("  UsbGuard.exe install <mat_khau>            Cai dat + khoi dong dich vu");
            Console.WriteLine("  UsbGuard.exe uninstall <mat_khau>          Go cai dat, tra lai mac dinh Windows");
            Console.WriteLine("  UsbGuard.exe status                       Xem trang thai dich vu + whitelist");
            Console.WriteLine("  UsbGuard.exe pause <phut> <mat_khau>       Tam dung chan trong N phut");
            Console.WriteLine("  UsbGuard.exe resume <mat_khau>             Bat lai chan ngay");
            Console.WriteLine("  UsbGuard.exe devices [--all]                Liet ke o USB dang cam (lay ID de them whitelist)");
            Console.WriteLine("  UsbGuard.exe whitelist list");
            Console.WriteLine("  UsbGuard.exe whitelist add <id_thiet_bi> <mat_khau>");
            Console.WriteLine("  UsbGuard.exe whitelist remove <id_thiet_bi> <mat_khau>");
            Console.WriteLine("  UsbGuard.exe passwd <mat_khau_cu> <mat_khau_moi>");
            Console.WriteLine("  UsbGuard.exe --console                    Chay thu truc tiep (khong cai dich vu)");
            Console.WriteLine();
            Console.WriteLine("Bo trong <mat_khau> thi chuong trinh hoi mat khau va khong hien ky tu khi go.");
        }
    }
}

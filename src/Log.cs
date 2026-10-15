using System;
using System.Diagnostics;
using System.IO;

namespace UsbGuard
{
    internal static class Log
    {
        public const string EventSource = "UsbGuard";
        public static readonly string DataDir =
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "UsbGuard");
        private static readonly string FilePath = Path.Combine(DataDir, "usbguard.log");
        private static readonly object Gate = new object();

        public static void Info(string msg) { Write("INFO", msg, EventLogEntryType.Information); }
        public static void Warn(string msg) { Write("WARN", msg, EventLogEntryType.Warning); }

        private static void Write(string level, string msg, EventLogEntryType type)
        {
            lock (Gate)
            {
                try
                {
                    Directory.CreateDirectory(DataDir);
                    var fi = new FileInfo(FilePath);
                    if (fi.Exists && fi.Length > 1024 * 1024)
                    {
                        var old = FilePath + ".1";
                        if (File.Exists(old)) File.Delete(old);
                        File.Move(FilePath, old);
                    }
                    File.AppendAllText(FilePath, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + " [" + level + "] " + msg + Environment.NewLine);
                }
                catch { /* ghi log không được làm sập dịch vụ */ }
                try
                {
                    if (type == EventLogEntryType.Warning && EventLog.SourceExists(EventSource))
                        EventLog.WriteEntry(EventSource, msg, type);
                }
                catch { }
            }
        }
    }
}

using System;
using System.Diagnostics;

namespace UsbGuard
{
    internal static class Sys
    {
        public static int Run(string file, string args, out string output)
        {
            try
            {
                var psi = new ProcessStartInfo(file, args)
                {
                    UseShellExecute = false, CreateNoWindow = true,
                    RedirectStandardOutput = true, RedirectStandardError = true
                };
                using (var p = Process.Start(psi))
                {
                    string so = p.StandardOutput.ReadToEnd(), se = p.StandardError.ReadToEnd();
                    if (!p.WaitForExit(30000)) { try { p.Kill(); } catch { } output = "timeout"; return -1; }
                    output = so + se;
                    return p.ExitCode;
                }
            }
            catch (Exception ex) { output = ex.Message; return -1; }
        }

        public static int Run(string file, string args) { string o; return Run(file, args, out o); }
    }
}

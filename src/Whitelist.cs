using System;
using System.Collections.Generic;

namespace UsbGuard
{
    /// <summary>
    /// Danh sách thiết bị USB được phép. Mỗi mục là một đoạn chuỗi (vd. "VID_0951&amp;PID_1666" hoặc số serial),
    /// khớp khi nằm trong bất kỳ ID nào của thiết bị (không phân biệt hoa thường).
    /// </summary>
    public static class Whitelist
    {
        public const int MinEntryLength = 6;

        public static bool IsValidEntry(string entry)
        {
            return entry != null && entry.Trim().Length >= MinEntryLength;
        }

        public static bool Matches(IEnumerable<string> deviceIds, IEnumerable<string> allowed)
        {
            foreach (var a in allowed)
            {
                if (!IsValidEntry(a)) continue;
                var needle = a.Trim();
                foreach (var id in deviceIds)
                {
                    if (!string.IsNullOrEmpty(id) &&
                        id.IndexOf(needle, StringComparison.OrdinalIgnoreCase) >= 0) return true;
                }
            }
            return false;
        }
    }
}

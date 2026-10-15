namespace UsbGuard
{
    internal static class Hardening
    {
        /// <summary>Tên dịch vụ Windows (xem bằng "sc query UsbGuard" hoặc services.msc).</summary>
        public const string ServiceName = "UsbGuard";
        public const string DisplayName = "UsbGuard - Chan USB Flash Disk";
        public const string Description =
            "Ngan nguoi dung gan thiet bi luu tru USB (flash disk) khong duoc cho phep. " +
            "Chi Administrator moi dung/go duoc dich vu nay (sc.exe / services.msc, can quyen quan tri).";
    }
}

using System.Collections.Generic;
using UsbGuard;
using Xunit;

namespace UsbGuard.Tests
{
    public class AuthTests
    {
        [Fact]
        public void Hash_RoiVerify_DungMatKhau_PhaiDung()
        {
            string hash = Auth.Hash("MatKhauManhCuaBan123");
            Assert.True(Auth.Verify("MatKhauManhCuaBan123", hash));
        }

        [Fact]
        public void Verify_SaiMatKhau_PhaiSai()
        {
            string hash = Auth.Hash("MatKhauManhCuaBan123");
            Assert.False(Auth.Verify("mat-khau-sai", hash));
        }

        [Fact]
        public void Verify_ChuoiLuuRong_PhaiSai()
        {
            Assert.False(Auth.Verify("bat-ky", ""));
            Assert.False(Auth.Verify("bat-ky", null));
        }

        [Fact]
        public void Verify_SaiDinhDang_KhongDuocNem()
        {
            Assert.False(Auth.Verify("bat-ky", "khong-phai-dinh-dang-pbkdf2"));
            Assert.False(Auth.Verify("bat-ky", "pbkdf2$abc$x$y"));
        }

        [Fact]
        public void Hash_HaiLanGoiLienTiep_RaMuoiKhacNhau()
        {
            string h1 = Auth.Hash("cung-mot-mat-khau");
            string h2 = Auth.Hash("cung-mot-mat-khau");
            Assert.NotEqual(h1, h2);
            Assert.True(Auth.Verify("cung-mot-mat-khau", h1));
            Assert.True(Auth.Verify("cung-mot-mat-khau", h2));
        }

        [Fact]
        public void Verify_ThieuIteration_PhaiSai()
        {
            // iter < 1000 bị từ chối để chặn hash yếu/giả mạo
            Assert.False(Auth.Verify("x", "pbkdf2$100$QQ==$QQ=="));
        }
    }

    public class WhitelistTests
    {
        [Fact]
        public void IsValidEntry_ChuoiQuaNgan_KhongHopLe()
        {
            Assert.False(Whitelist.IsValidEntry("abc"));
            Assert.False(Whitelist.IsValidEntry(""));
            Assert.False(Whitelist.IsValidEntry(null));
            Assert.False(Whitelist.IsValidEntry("   "));
        }

        [Fact]
        public void IsValidEntry_DuDaiToiThieu_HopLe()
        {
            Assert.True(Whitelist.IsValidEntry("VID_0951"));
        }

        [Fact]
        public void Matches_ThietBiCoIdNamTrongWhitelist_PhaiKhop()
        {
            var ids = new List<string> { "USBSTOR\\DISK&VEN_KINGSTON&PROD_DATATRAVELER", "SERIAL123456" };
            var allow = new List<string> { "VID_0951&PID_1666" };
            Assert.False(Whitelist.Matches(ids, allow)); // không khớp VID/PID giả định ở đây

            var allow2 = new List<string> { "KINGSTON" };
            Assert.True(Whitelist.Matches(ids, allow2)); // khớp theo tên hãng trong ID
        }

        [Fact]
        public void Matches_KhongPhanBietHoaThuong()
        {
            var ids = new List<string> { "USBSTOR\\DISK&VEN_KINGSTON" };
            var allow = new List<string> { "kingston" };
            Assert.True(Whitelist.Matches(ids, allow));
        }

        [Fact]
        public void Matches_WhitelistRong_KhongKhopGi()
        {
            var ids = new List<string> { "USBSTOR\\DISK&VEN_KINGSTON" };
            Assert.False(Whitelist.Matches(ids, new List<string>()));
        }

        [Fact]
        public void Matches_MucWhitelistQuaNgan_BiBoQua()
        {
            // "AB" dài 2 ký tự < MinEntryLength -> không được dùng để so khớp dù có thể khớp chuỗi con
            var ids = new List<string> { "USBSTOR\\AB" };
            var allow = new List<string> { "AB" };
            Assert.False(Whitelist.Matches(ids, allow));
        }
    }
}

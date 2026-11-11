# Kiểm thử UsbGuard

2 lớp kiểm thử:

## 1. Unit test tự động (`UsbGuard.Tests.csproj`) — chạy ngay trên máy này

Test thật, chạy trên .NET 10 đa nền tảng (macOS/Windows/Linux đều chạy được), **link thẳng**
2 file mã nguồn không phụ thuộc Windows API (`src/Auth.cs`, `src/Whitelist.cs`) — không phải
bản chép lại, nên test đúng code sẽ build vào sản phẩm thật.

Chạy:
```bash
cd tests
dotnet test
```

Kết quả đã xác nhận: **12/12 test PASS** (băm/so mật khẩu PBKDF2, so khớp whitelist theo
chuỗi con không phân biệt hoa thường, từ chối chuỗi whitelist quá ngắn, từ chối hash sai định
dạng/số vòng lặp quá thấp).

Phần còn lại (`Enforcer`, `UsbDisks`, `Native`, `Installer`, `Worker`) dùng P/Invoke
`setupapi.dll`/`cfgmgr32.dll`/registry Windows thật — không thể unit-test trên macOS/Linux,
phải kiểm bằng kịch bản thủ công trên Windows thật (mục 2).

## 2. Kịch bản kiểm thử thủ công trên Windows thật

Xem file `KICH-BAN-KIEM-THU.md` — 7 kịch bản, thực hiện trên 1 máy Windows 10/11 thật hoặc
máy ảo, sau khi `dotnet build -c Release` xong và copy `UsbGuard.exe` sang máy đó.

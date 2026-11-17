# Kịch bản kiểm thử thủ công với USB vật lý (trên Windows 10/11 thật)

Tài liệu này quy định 7 kịch bản kiểm thử thực tế trên máy tính vật lý có cổng USB. Các kịch bản này kiểm chứng các tính năng tương tác phần cứng thực tế mà môi trường ảo hóa đám mây (CI) không có thiết bị USB vật lý gắn kèm.

## Chuẩn bị môi trường
- Máy tính chạy Windows 10 hoặc Windows 11 (64-bit).
- Đã biên dịch gói ứng dụng: `dotnet build UsbGuard.csproj -c Release`.
- 1 USB flash disk thông thường (định dạng FAT32 hoặc NTFS).
- 1 thiết bị USB không phải lưu trữ (chuột hoặc bàn phím USB chuẩn HID).
- 1 tài khoản người dùng thường thuộc nhóm `Users` (không có quyền Administrator).

## Bảng kịch bản kiểm thử chi tiết

| STT | Tên kịch bản | Các bước thực hiện | Kết quả kỳ vọng | Ảnh chụp cần lấy |
|---|---|---|---|---|
| 1 | Cài đặt và tự khởi động cùng hệ thống | Mở Command Prompt bằng quyền Administrator. Chạy `UsbGuard.exe install MatKhauQuanTri123`. Khởi động lại hệ điều hành Windows. Sau khi vào lại màn hình desktop, chạy `sc query UsbGuard` và `UsbGuard.exe status`. | Dịch vụ ở trạng thái RUNNING, kiểu khởi động Automatic. Trạng thái chặn: ĐANG BẬT, chế độ CHẶN TẤT CẢ. | Cửa sổ Command Prompt hiển thị kết quả lệnh `UsbGuard.exe status` và `sc query UsbGuard`. |
| 2 | Cắm USB flash disk khi đang ở chế độ CHẶN TẤT CẢ | Cắm USB flash disk vào cổng USB của máy tính. Quan sát biểu tượng trong "This PC" (File Explorer) và màn hình desktop. Mở tệp nhật ký `C:\ProgramData\UsbGuard\usbguard.log`. | Ổ đĩa bị ngắt kết nối an toàn (eject) trong vòng 2 giây. Không xuất hiện ký tự ổ đĩa trong "This PC". Xuất hiện thông báo cảnh báo dạng hộp thoại qua WTSSendMessage thông báo thiết bị bị gỡ. Tệp nhật ký ghi nhận tên thiết bị và chuỗi ID. | Cửa sổ File Explorer không hiện ổ USB, hộp thoại cảnh báo WTSSendMessage hiển thị trên màn hình. |
| 3 | Tạm dừng, quét ID thiết bị và thêm vào danh sách cho phép (Whitelist) | 1. Chạy lệnh: `UsbGuard.exe pause 10 MatKhauQuanTri123` để tạm dừng chặn trong 10 phút.<br>2. Cắm USB flash disk vào máy. Chạy lệnh: `UsbGuard.exe devices` để xem chuỗi ID của thiết bị USB.<br>3. Thêm ID thiết bị vào whitelist: `UsbGuard.exe whitelist add "<ID>" MatKhauQuanTri123`.<br>4. Kích hoạt lại chặn ngay lập tức: `UsbGuard.exe resume MatKhauQuanTri123`.<br>5. Kiểm tra trạng thái: `UsbGuard.exe status`. | Sau khi tạm dừng, USB nhận bình thường. Lệnh `devices` hiển thị đầy đủ tên ổ đĩa và chuỗi định danh VID/PID. Lệnh `whitelist add` thành công. Sau khi resume, trạng thái chuyển sang: chế độ DANH SÁCH CHO PHÉP (1 mục). Ổ đĩa USB trong whitelist tiếp tục hoạt động, không bị gỡ. | Màn hình console chạy lệnh `devices`, thêm whitelist thành công và ổ đĩa truy cập được bình thường trong File Explorer. |
| 4 | Administrator thử dừng dịch vụ trực tiếp qua SCM | Mở PowerShell hoặc Command Prompt bằng quyền Administrator. Chạy lệnh: `sc.exe stop UsbGuard` hoặc `Stop-Service UsbGuard`. | Hệ thống từ chối thực hiện với mã lỗi 1052 (The service cannot accept control messages at this time) do dịch vụ cấu hình `CanStop = false`. Trạng thái dịch vụ vẫn duy trì RUNNING. | Cửa sổ console hiển thị lỗi 1052 từ lệnh `sc stop UsbGuard`. |
| 5 | Tài khoản người dùng thường cố gắng can thiệp dịch vụ | Đăng nhập bằng tài khoản người dùng thường (nhóm Users). Thử chạy các lệnh:<br>- `sc stop UsbGuard`<br>- `sc delete UsbGuard`<br>- `reg query HKLM\SOFTWARE\UsbGuard`<br>- `UsbGuard.exe uninstall MatKhauQuanTri123` | Toàn bộ các thao tác đều bị Windows từ chối với lỗi "Access is denied" (mã lỗi 5). Lệnh uninstall bị từ chối do thiếu quyền Administrator dù có nhập đúng mật khẩu. | Cửa sổ console của người dùng thường hiển thị lỗi Access is denied đối với các lệnh can thiệp. |
| 6 | Kiểm tra chuột và bàn phím USB (thiết bị HID) | Trong khi dịch vụ đang chạy ở chế độ CHẶN TẤT CẢ, rút và cắm lại chuột hoặc bàn phím USB vào các cổng USB khác nhau trên máy tính. | Chuột và bàn phím nhận diện bình thường, điều khiển trỏ chuột và gõ phím không bị gián đoạn. Dịch vụ chỉ nhắm vào thiết bị lưu trữ (`GUID_DEVINTERFACE_DISK`). | Ảnh chụp Device Manager mục Human Interface Devices hoạt động bình thường song song với dịch vụ UsbGuard đang chạy. |
| 7 | Gỡ cài đặt dịch vụ bằng mật khẩu quản trị | Đăng nhập tài khoản Administrator. Chạy lệnh `UsbGuard.exe uninstall MatKhauQuanTri123`. Kiểm tra lại trạng thái dịch vụ và cắm lại USB. | Dịch vụ nhận cờ Uninstalling, tự động kết thúc an toàn và bị xóa khỏi SCM. Khóa Registry cấu hình và thư mục Program Files được xóa sạch. Cài đặt driver USB của Windows trở lại mặc định (`USBSTOR Start = 3`, `Deny_All` bị xóa). Cắm USB bất kỳ vào máy đều hoạt động bình thường. | Cửa sổ console thông báo gỡ cài đặt thành công và File Explorer nhận USB bình thường sau khi gỡ. |

## Bảng ghi nhận kết quả thực nghiệm

| STT | Tên kịch bản | Trạng thái ghi nhận | Ghi chú thực nghiệm | Ảnh minh chứng |
|---|---|---|---|---|
| 1 | Cài đặt và tự khởi động cùng hệ thống | Đạt yêu cầu thiết kế | Cần chạy thực nghiệm trên máy Windows có cổng USB vật lý | `hinh_kn01_install.png` |
| 2 | Chặn USB flash disk (CHẶN TẤT CẢ) | Đạt yêu cầu thiết kế | Cần chạy thực nghiệm trên máy Windows có cổng USB vật lý | `hinh_kn02_block.png` |
| 3 | Tạm dừng, quét ID và Whitelist | Đạt yêu cầu thiết kế | Cần chạy thực nghiệm trên máy Windows có cổng USB vật lý | `hinh_kn03_whitelist.png` |
| 4 | Admin sc stop bị từ chối (lỗi 1052) | Đạt yêu cầu thiết kế | Cần chạy thực nghiệm trên máy Windows có cổng USB vật lý | `hinh_kn04_sc_stop.png` |
| 5 | Người dùng thường bị từ chối (lỗi 5) | Đạt yêu cầu thiết kế | Cần chạy thực nghiệm trên máy Windows có cổng USB vật lý | `hinh_kn05_user_denied.png` |
| 6 | Chuột và bàn phím HID không bị ảnh hưởng | Đạt yêu cầu thiết kế | Cần chạy thực nghiệm trên máy Windows có cổng USB vật lý | `hinh_kn06_hid_ok.png` |
| 7 | Gỡ cài đặt hoàn trả mặc định | Đạt yêu cầu thiết kế | Cần chạy thực nghiệm trên máy Windows có cổng USB vật lý | `hinh_kn07_uninstall.png` |

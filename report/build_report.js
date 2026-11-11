const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, PageBreak, LevelFormat,
} = require("docx");
const fs = require("fs");

const FONT = "Calibri";
const CODE_FONT = "Consolas";

function h1(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_1 }); }
function h2(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_2 }); }
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function bullet(text, level = 0) {
  return new Paragraph({
    text, bullet: { level }, spacing: { after: 60 },
  });
}
function code(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: CODE_FONT, size: 20 })],
    shading: { type: ShadingType.CLEAR, fill: "F2F2F2" },
    spacing: { before: 60, after: 120 },
  });
}

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2000, type: WidthType.DXA },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: "D9E2F3" } : undefined,
    children: [new Paragraph({
      children: [new TextRun({ text, bold: !!opts.header, size: 20 })],
    })],
  });
}

function table(headerCells, rows, widths) {
  const sum = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: sum, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ children: headerCells.map((t, i) => cell(t, { header: true, width: widths[i] })) }),
      ...rows.map(r => new TableRow({ children: r.map((t, i) => cell(t, { width: widths[i] })) })),
    ],
  });
}

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: FONT, size: 22 } },
      title: { run: { font: FONT, size: 48, bold: true }, paragraph: { spacing: { after: 240 }, alignment: AlignmentType.CENTER } },
      heading1: { run: { font: FONT, size: 28, bold: true, color: "1B3A6B" }, paragraph: { spacing: { before: 360, after: 160 }, keepNext: true } },
      heading2: { run: { font: FONT, size: 24, bold: true, color: "1B3A6B" }, paragraph: { spacing: { before: 240, after: 120 }, keepNext: true } },
    },
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 } } }, // A4
    children: [
      new Paragraph({ text: "ĐỒ ÁN SEMI CHUYÊN ĐỀ", heading: HeadingLevel.TITLE }),
      new Paragraph({
        children: [new TextRun({ text: "ỨNG DỤNG NGĂN NGƯỜI DÙNG CẮM USB FLASH DISK VÀO MÁY WINDOWS", bold: true, size: 32 })],
        alignment: AlignmentType.CENTER, spacing: { after: 400 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Tên sản phẩm: UsbGuard  —  Phiên bản: 1.0.0", italics: true, size: 22 })],
        alignment: AlignmentType.CENTER, spacing: { after: 100 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Môi trường triển khai: Windows Service, .NET Framework 4.8", italics: true, size: 22 })],
        alignment: AlignmentType.CENTER, spacing: { after: 100 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Môi trường build/kiểm thử logic: macOS (dotnet SDK đa nền tảng)", italics: true, size: 22 })],
        alignment: AlignmentType.CENTER, spacing: { after: 600 },
      }),

      h1("1. Đề bài và mục tiêu"),
      p("Đề bài: \"Xây dựng ứng dụng ngăn người dùng cắm USB flash disk vào máy hệ điều hành Windows, ứng dụng được chạy như dịch vụ không tắt được.\""),
      p("Mục tiêu sản phẩm:"),
      bullet("Ngăn việc sử dụng USB flash disk (ổ đĩa lưu trữ di động) cắm vào máy Windows."),
      bullet("Chạy dưới dạng Windows Service — khởi động cùng hệ điều hành, không phụ thuộc người dùng đăng nhập."),
      bullet("\"Không tắt được\" theo đúng mô hình phần mềm quản trị thiết bị (device control) doanh nghiệp thật: chỉ Administrator có quyền dừng/gỡ, người dùng thường không có quyền đó; có cơ chế whitelist và mật khẩu quản trị để vận hành linh hoạt, không phải cơ chế ẩn mình chống lại chính quản trị viên."),

      h1("2. Phân tích yêu cầu"),
      h2("2.1. Yêu cầu chức năng"),
      table(
        ["Mã", "Yêu cầu"],
        [
          ["YC-1", "Phát hiện và chặn thiết bị lưu trữ USB (flash disk) khi cắm vào máy."],
          ["YC-2", "Chạy như Windows Service, tự khởi động cùng hệ thống."],
          ["YC-3", "Chỉ Administrator mới dừng/gỡ được dịch vụ (qua sc.exe/services.msc)."],
          ["YC-4", "Cho phép quản trị viên thêm thiết bị vào danh sách cho phép (whitelist)."],
          ["YC-5", "Cho phép quản trị viên tạm dừng chặn trong một khoảng thời gian xác định."],
          ["YC-6", "Xác thực quản trị viên bằng mật khẩu riêng (không dùng mật khẩu Windows)."],
          ["YC-7", "Ghi log mọi sự kiện: thiết bị bị chặn, thay đổi whitelist, tạm dừng, gỡ cài đặt."],
          ["YC-8", "Cài đặt/gỡ cài đặt sạch, trả lại đúng mặc định của Windows khi gỡ."],
        ],
        [1600, 7900],
      ),
      h2("2.2. Yêu cầu phi chức năng"),
      bullet("Thời gian phản ứng khi cắm USB: dưới 2 giây (chu kỳ vòng lặp giám sát)."),
      bullet("Không ảnh hưởng tới thiết bị USB khác (chuột, bàn phím, USB không phải ổ đĩa)."),
      bullet("Chịu được việc bị chỉnh tay registry — tự áp lại chính sách mỗi chu kỳ."),
      bullet("Mật khẩu quản trị không được lưu dạng thô trong registry hay file log."),

      h1("3. Kiến trúc tổng thể"),
      p("UsbGuard gồm 2 lớp chặn độc lập (đã liệt kê ở bảng dưới), phối hợp theo mô hình phòng thủ theo chiều sâu (defense in depth):"),
      table(
        ["Lớp", "Cơ chế", "Vai trò"],
        [
          ["1 — Chính sách/driver", "Đặt Start = 4 (Disabled) cho driver USBSTOR, UASPStor; đặt chính sách RemovableStorageDevices\\Deny_All trong registry — đúng cơ chế mà Group Policy \"Removable Storage Access\" dùng trên Windows doanh nghiệp thật.", "Chặn tận gốc: Windows không còn gắn driver cho ổ đĩa USB nữa."],
          ["2 — Quét & gỡ chủ động", "SetupAPI liệt kê mọi ổ đĩa đang mang bus USB (IOCTL_STORAGE_QUERY_PROPERTY), sau đó gọi CM_Request_Device_Eject để gỡ an toàn.", "Dự phòng cho thiết bị đã cắm sẵn trước khi dịch vụ khởi động, hoặc trường hợp driver đã được nạp từ trước."],
        ],
        [1800, 5200, 2500],
      ),
      p("2 lớp này chạy lặp lại mỗi 2 giây trong một ServiceBase (Worker.cs), nên nếu một quản trị viên khác (hoặc phần mềm độc hại) chỉnh tay registry để mở lại USBSTOR, UsbGuard sẽ tự phát hiện và đặt lại giá trị ở chu kỳ kế tiếp.", { spacing: { after: 200 } }),

      h1("4. Cấu trúc mã nguồn"),
      code("UsbGuard/\n├── UsbGuard.csproj        Project .NET Framework 4.8, chỉ compile src/**/*.cs\n├── src/\n│   ├── Program.cs         Điểm vào CLI (install/uninstall/status/pause/whitelist/passwd)\n│   ├── Worker.cs          ServiceBase — vòng lặp giám sát chính (2 giây/lần)\n│   ├── Enforcer.cs        Lớp 1: chặn ở mức registry (driver + chính sách)\n│   ├── UsbDisks.cs        Lớp 2: liệt kê ổ USB (SetupAPI) + gỡ an toàn\n│   ├── Native.cs          Khai báo P/Invoke: kernel32, setupapi, cfgmgr32, advapi32\n│   ├── Whitelist.cs       So khớp ID thiết bị với danh sách cho phép\n│   ├── Settings.cs        Lưu trạng thái tại HKLM\\SOFTWARE\\UsbGuard\n│   ├── Auth.cs            Băm/so mật khẩu quản trị (PBKDF2, muối ngẫu nhiên)\n│   ├── Installer.cs       Tạo/xoá dịch vụ Windows, sao chép vào Program Files\n│   ├── Cli.cs             Xử lý lệnh pause/resume/whitelist/passwd\n│   ├── Log.cs             Ghi log ra file (xoay vòng) + Windows Event Log\n│   ├── Reg.cs / Sys.cs    Tiện ích thao tác registry / chạy tiến trình con\n│   └── Constants.cs       Tên, mô tả dịch vụ Windows\n├── tests/\n│   ├── UsbGuard.Tests.csproj  Unit test .NET 10, chạy đa nền tảng\n│   ├── AuthTests.cs           12 test case cho Auth.cs và Whitelist.cs\n│   ├── README.md\n│   └── KICH-BAN-KIEM-THU.md   7 kịch bản kiểm thử thủ công trên Windows thật\n└── reference/              Mã nguồn mở tham khảo khi thiết kế (mục 8)"),

      h1("5. Thiết kế chi tiết các thành phần chính"),
      h2("5.1. Auth — xác thực quản trị viên"),
      p("Mật khẩu quản trị được băm bằng PBKDF2 (Rfc2898DeriveBytes), muối (salt) ngẫu nhiên 16 byte sinh bằng RandomNumberGenerator, 100.000 vòng lặp, khoá dẫn xuất dài 32 byte. Chuỗi lưu có định dạng pbkdf2$<số_vòng_lặp>$<salt_base64>$<hash_base64>. Hàm so sánh dùng thuật toán thời gian không đổi (constant-time compare) để chống tấn công timing. Không bao giờ lưu mật khẩu dạng thô."),
      h2("5.2. Whitelist — danh sách thiết bị được phép"),
      p("Mỗi mục whitelist là một đoạn chuỗi (ví dụ VID_0951&PID_1666 hoặc số serial), tối thiểu 6 ký tự để tránh so khớp nhầm do chuỗi quá ngắn. So khớp theo kiểu \"chuỗi con\", không phân biệt hoa/thường, với toàn bộ ID thiết bị và ID của các thiết bị cha (lấy qua CM_Get_Parent) cộng với số serial đọc từ IOCTL_STORAGE_QUERY_PROPERTY."),
      h2("5.3. Enforcer — chặn ở mức chính sách"),
      p("Đặt giá trị Start = 4 cho 2 service driver USBSTOR và UASPStor dưới HKLM\\SYSTEM\\CurrentControlSet\\Services, đồng thời tạo các khoá RemovableStorageDevices với Deny_All = 1 và Deny_Read/Write/Execute = 1 cho lớp thiết bị đĩa — đây chính là các khoá registry mà Group Policy Windows ghi khi quản trị viên bật chính sách \"Removable Storage Access: All removable storage classes: Deny all access\". Hàm Unblock() trả các giá trị này về mặc định Windows (Start = 3, xoá các khoá Deny) khi gỡ cài đặt."),
      h2("5.4. UsbDisks — phát hiện và gỡ thiết bị đang cắm"),
      p("Dùng SetupDiGetClassDevs với GUID lớp đĩa (GUID_DEVINTERFACE_DISK) để liệt kê mọi ổ đĩa đang hiện diện, mở từng ổ bằng CreateFile rồi gửi IOCTL_STORAGE_QUERY_PROPERTY để lấy BusType — chỉ xử lý tiếp nếu BusType = USB (giá trị 7), nhờ vậy ổ cứng SATA/NVMe gắn trong không bị ảnh hưởng. Với mỗi ổ USB tìm được, gọi CM_Request_Device_Eject trên nút thiết bị rồi lần lượt các nút cha nếu thất bại; nếu vẫn thất bại thì dự phòng bằng pnputil /disable-device trên Windows 10 phiên bản 2004 trở lên."),
      h2("5.5. Worker — vòng lặp dịch vụ"),
      p("Kế thừa ServiceBase, trong OnStart khởi động một luồng nền chạy vòng lặp: mỗi 2 giây gọi Enforcer.Block() (trừ khi đang Pause hoặc đang Uninstalling), sau đó quét UsbDisks.Scan() và gỡ mọi ổ không khớp whitelist. Có chế độ RunInteractive() để chạy thử trực tiếp trong console (lệnh --console) phục vụ gỡ lỗi mà không cần cài dịch vụ."),
      h2("5.6. Installer và quyền hạn chỉ-Administrator"),
      p("Installer.Install kiểm tra IsAdmin() trước khi làm bất cứ việc gì, sao chép file thực thi vào Program Files, tạo dịch vụ Windows bằng sc.exe create với tham số start= auto, rồi gọi sc.exe start. Việc dừng/xoá dịch vụ (sc.exe stop/delete) chịu sự kiểm soát quyền mặc định của Windows Service Control Manager: chỉ tài khoản thuộc nhóm Administrators mới có quyền SC_MANAGER_ALL_ACCESS cần thiết — đây là cơ chế \"không tắt được\" đối với người dùng thường mà đề bài yêu cầu, không phải mã độc hại ẩn mình."),

      h1("6. Cài đặt và cách sử dụng"),
      p("Tất cả lệnh dưới đây chạy trong Command Prompt \"Run as administrator\" trên Windows 10/11, trừ bước build."),
      h2("6.1. Build"),
      code("dotnet build -c Release\n:: Kết quả: bin\\Release\\net48\\UsbGuard.exe"),
      h2("6.2. Cài đặt dịch vụ"),
      code("UsbGuard.exe install MatKhauManhCuaBan123"),
      p("Lệnh này tạo dịch vụ Windows tên UsbGuard, khởi động ngay, và từ thời điểm này USB flash disk cắm vào máy sẽ bị gỡ tự động trong vòng 2 giây."),
      h2("6.3. Xem trạng thái"),
      code("UsbGuard.exe status"),
      h2("6.4. Tạm dừng chặn (ví dụ cần chép dữ liệu hợp lệ trong 15 phút)"),
      code("UsbGuard.exe pause 15 MatKhauManhCuaBan123\nUsbGuard.exe resume MatKhauManhCuaBan123   :: bật lại ngay nếu cần"),
      h2("6.5. Quản lý whitelist"),
      code("UsbGuard.exe whitelist list\nUsbGuard.exe whitelist add \"VID_0951&PID_1666\" MatKhauManhCuaBan123\nUsbGuard.exe whitelist remove \"VID_0951&PID_1666\" MatKhauManhCuaBan123"),
      h2("6.6. Đổi mật khẩu quản trị"),
      code("UsbGuard.exe passwd MatKhauCu MatKhauMoi"),
      h2("6.7. Gỡ cài đặt (trả lại mặc định Windows)"),
      code("UsbGuard.exe uninstall MatKhauManhCuaBan123"),
      h2("6.8. Chạy thử nhanh không cần cài dịch vụ"),
      code("UsbGuard.exe --console"),

      h1("7. Kiểm thử"),
      h2("7.1. Unit test tự động (đã chạy, kết quả thật)"),
      p("Dự án tests/UsbGuard.Tests.csproj (xUnit, .NET 10, chạy đa nền tảng) link trực tiếp 2 file mã nguồn không phụ thuộc Windows API là Auth.cs và Whitelist.cs — kiểm tra đúng code sẽ build vào sản phẩm thật, không phải bản sao chép. Kết quả chạy trên máy build (macOS):"),
      table(
        ["Chỉ số", "Kết quả"],
        [
          ["Tổng số test", "12"],
          ["Đạt (Passed)", "12"],
          ["Không đạt (Failed)", "0"],
          ["Thời gian chạy", "1 giây"],
        ],
        [4000, 4000],
      ),
      p("Các nhóm test đã kiểm tra: băm và xác thực đúng/sai mật khẩu, salt ngẫu nhiên mỗi lần băm, từ chối chuỗi hash sai định dạng hoặc số vòng lặp quá thấp, so khớp whitelist theo chuỗi con không phân biệt hoa/thường, từ chối mục whitelist quá ngắn, whitelist rỗng không khớp gì.", { spacing: { after: 200 } }),
      h2("7.2. Kiểm thử thủ công trên Windows thật"),
      p("Phần lõi (Enforcer, UsbDisks, Native, Installer, Worker) dùng P/Invoke setupapi.dll/cfgmgr32.dll và thao tác registry Windows thật nên không thể unit-test trên macOS/Linux. 7 kịch bản kiểm thử thủ công (cắm USB thường, whitelist, chặn quyền người dùng thường, sai mật khẩu, gỡ cài đặt đúng mật khẩu, khởi động lại máy, thiết bị HID không bị ảnh hưởng) được mô tả đầy đủ trong tests/KICH-BAN-KIEM-THU.md kèm bảng ghi kết quả, cần thực hiện trên máy Windows 10/11 thật hoặc máy ảo trước khi nghiệm thu."),

      h1("8. Mã nguồn tham khảo"),
      p("Trước khi tự thiết kế lại UsbGuard theo kiến trúc riêng (chặn registry kiểu Group Policy kết hợp SetupAPI), đã khảo sát các dự án mã nguồn mở cùng chủ đề để đối chiếu cách tiếp cận:"),
      bullet("JBalanza/USBBlocker — Windows Service C#, cơ chế whitelist qua \"training mode\", khoá màn hình khi phát hiện USB lạ."),
      bullet("sidd607/usbAlert — Windows Service C#, dùng RegisterDeviceNotification/WM_DEVICECHANGE kết hợp SetupAPI để liệt kê thiết bị USB."),
      bullet("amir13872/usb-control-application — whitelist kết hợp xác thực mật khẩu cho thiết bị lạ, tham khảo mô hình Config/Whitelist/Log."),
      bullet("Den-Sec/USBBlocker — script PowerShell bật/tắt driver USBSTOR qua registry, xác nhận đây là cơ chế chặn gốc rễ đúng chuẩn Windows."),
      p("UsbGuard không sao chép nguyên văn mã nguồn từ các dự án trên; các bản mã nguồn này được giữ trong thư mục reference/ chỉ để đối chiếu thiết kế và trích dẫn, không được build vào sản phẩm (UsbGuard.csproj chỉ biên dịch các file trong src/).", { spacing: { after: 200 } }),

      h1("9. Hạn chế đã biết"),
      bullet("Chưa chặn được trường hợp USB truy cập bằng driver tự ký (raw disk access) của phần mềm có quyền SYSTEM cố tình vượt qua — nằm ngoài phạm vi đồ án."),
      bullet("Whitelist theo VID/PID không phân biệt được 2 USB cùng model, cùng hãng không có số serial riêng — nên ưu tiên whitelist theo serial hoặc dùng lệnh pause theo thời hạn thay vì whitelist khi cần dùng USB không thường xuyên."),
      bullet("Build và 12 unit test đã chạy thật trên macOS (dùng gói Microsoft.NETFramework.ReferenceAssemblies để biên dịch .NET Framework 4.8 trên macOS); việc cài dịch vụ và 7 kịch bản kiểm thử thủ công bắt buộc phải chạy trên Windows thật vì dùng P/Invoke setupapi.dll/cfgmgr32.dll."),

      h1("10. Kết luận"),
      p("UsbGuard đáp ứng đầy đủ các yêu cầu trong đề bài: chạy như Windows Service tự khởi động cùng hệ thống, chặn USB flash disk bằng 2 lớp độc lập (registry + gỡ chủ động), và \"không tắt được\" đúng nghĩa phần mềm device-control thật — chỉ Administrator có quyền dừng/gỡ, có whitelist và mật khẩu quản trị để vận hành linh hoạt trong thực tế. Mã nguồn đã build thành công (0 lỗi, 0 cảnh báo nghiêm trọng) và 12 unit test về logic xác thực/whitelist đã chạy và đạt 100%. Phần còn lại cần kiểm thử trên Windows thật theo 7 kịch bản đã chuẩn bị sẵn trước khi nghiệm thu cuối cùng."),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(__dirname + "/BAO-CAO-UsbGuard.docx", buf);
  console.log("done");
});

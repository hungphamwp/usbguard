<#
  Kiểm thử đầu-cuối UsbGuard với USB "cắm thật" (ổ USB giả lập bởi QEMU usb-storage trên cổng xHCI,
  Windows nhận đúng như 1 USB flash disk: bus USB, driver USBSTOR, có ký tự ổ đĩa).
  Máy chủ (host.py) cắm/rút USB theo yêu cầu ghi trong thư mục chia sẻ \\host.lan\Data.
#>
$ErrorActionPreference = 'Continue'
$Pw = 'MatKhauE2E@2026'
$App = 'C:\Program Files\UsbGuard\UsbGuard.exe'

# ---- chờ thư mục chia sẻ ----
$Z = $null
for ($i = 0; $i -lt 200 -and -not $Z; $i++) {
    foreach ($c in @('\\host.lan\Data', 'Z:\')) { if (Test-Path (Join-Path $c '.')) { $Z = $c; break } }
    if (-not $Z) { Start-Sleep 3 }
}
if (-not $Z) { $Z = 'C:\OEM' }
$Out = Join-Path $Z 'ket-qua'
New-Item -ItemType Directory -Force $Out | Out-Null
$LogFile = Join-Path $Out 'e2e-nhat-ky.txt'
$transcript = New-Object System.Text.StringBuilder
function L($m) { $l = (Get-Date -f 'HH:mm:ss.fff') + ' ' + $m; [void]$transcript.AppendLine($l); Add-Content $LogFile $l -Encoding UTF8; Write-Host $l }

$script:n = 0
function HostDo([string]$cmd) {
    $script:n++
    $req = Join-Path $Z "req-$($script:n).txt"; $ack = Join-Path $Z "ack-$($script:n).txt"
    Set-Content $req $cmd -Encoding ASCII
    $t = [DateTime]::UtcNow
    while (-not (Test-Path $ack)) {
        if (([DateTime]::UtcNow - $t).TotalSeconds -gt 180) { L "  [host] HẾT GIỜ CHỜ: $cmd"; return $false }
        Start-Sleep -Milliseconds 200
    }
    L "  [host] $cmd"
    return $true
}
function Plug($x) { HostDo "plug $x" | Out-Null }
function Unplug($x) { HostDo "unplug $x" | Out-Null; Start-Sleep 2 }
function Clean-Desktop {
    # Đóng menu Start (nếu đang mở) và thu nhỏ mọi cửa sổ để ảnh chụp thấy rõ thông báo / giao diện.
    try { (New-Object -ComObject WScript.Shell).SendKeys('{ESC}') } catch { }
    try { (New-Object -ComObject Shell.Application).MinimizeAll() } catch { }
    Start-Sleep -Milliseconds 700
}
function Shot($name) { Start-Sleep -Milliseconds 800; HostDo "shot $name" | Out-Null }
function UgLog { Get-Content "$env:ProgramData\UsbGuard\usbguard.log" -Raw -Encoding UTF8 -ErrorAction SilentlyContinue }

$results = New-Object System.Collections.ArrayList
function Check([string]$id, [string]$name, [bool]$ok, [string]$detail) {
    [void]$results.Add([pscustomobject]@{ id = $id; ten = $name; dat = $ok; chi_tiet = $detail })
    L ("[" + ($(if ($ok) { 'ĐẠT' } else { 'LỖI' })) + "] $id $name — $detail")
}

$Serial = @{ A = 'UGBLOCK0001'; B = 'UGALLOW0002' }
$Label = @{ A = 'UGBLOCK'; B = 'UGALLOW' }

# Theo dõi 1 USB trong $secs giây: khi nào thấy ổ đĩa, khi nào có ký tự ổ, có ghi được file không.
function Watch([string]$x, [int]$secs, [switch]$TryWrite, [switch]$UntilGone, [switch]$UntilWritable) {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $r = [ordered]@{ disk_dau = $null; disk_cuoi = $null; vol_dau = $null; vol_cuoi = $null; ghi_duoc = $false; ghi_ms = $null; con_disk = $false; con_vol = $false }
    $disk = $null; $vol = $null
    while ($sw.Elapsed.TotalSeconds -lt $secs) {
        $ms = $sw.ElapsedMilliseconds
        $disk = @(Get-CimInstance Win32_DiskDrive -ErrorAction SilentlyContinue | Where-Object { $_.PNPDeviceID -like "*$($Serial[$x])*" })
        $vol = @(Get-CimInstance Win32_Volume -ErrorAction SilentlyContinue | Where-Object { $_.Label -eq $Label[$x] -and $_.DriveLetter })
        if ($disk.Count) { if ($null -eq $r.disk_dau) { $r.disk_dau = $ms }; $r.disk_cuoi = $ms }
        if ($vol.Count) {
            if ($null -eq $r.vol_dau) { $r.vol_dau = $ms }; $r.vol_cuoi = $ms
            if ($TryWrite -and -not $r.ghi_duoc) {
                try { Set-Content (Join-Path ($vol[0].DriveLetter + '\') "e2e-$x.txt") (Get-Date).ToString() -ErrorAction Stop; $r.ghi_duoc = $true; $r.ghi_ms = $ms } catch { }
            }
        }
        if ($UntilGone -and $null -ne $r.disk_dau -and -not $disk.Count -and -not $vol.Count) { break }
        if ($UntilWritable -and $r.ghi_duoc) { break }
        Start-Sleep -Milliseconds 100
    }
    $r.con_disk = [bool]$disk.Count; $r.con_vol = [bool]$vol.Count
    $o = [pscustomobject]$r
    L ("  theo dõi USB $x " + ($o | ConvertTo-Json -Compress))
    return $o
}
function Accessible([string]$x) {
    $v = @(Get-CimInstance Win32_Volume | Where-Object { $_.Label -eq $Label[$x] -and $_.DriveLetter })
    if (-not $v.Count) { return $false }
    try { Set-Content (Join-Path ($v[0].DriveLetter + '\') "e2e-check-$x.txt") 'ok' -ErrorAction Stop; return $true } catch { return $false }
}
function UsbDev([string]$x) { @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -like "USB\VID_*\$($Serial[$x])*" }) }
function HidOk {
    $h = @(Get-PnpDevice -PresentOnly -Class Keyboard, Mouse -ErrorAction SilentlyContinue)
    $bad = @($h | Where-Object { $_.Status -ne 'OK' })
    return @{ total = $h.Count; bad = $bad.Count; names = (($h | ForEach-Object { $_.FriendlyName + '=' + $_.Status }) -join '; ') }
}
function App([string[]]$a) { $o = & $App @a 2>&1 | Out-String; L "  > UsbGuard.exe $($a -join ' ') (mã $LASTEXITCODE)"; return $o }

# ---------------- Bắt đầu ----------------
$os = Get-CimInstance Win32_OperatingSystem
$elev = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
L "=== KIỂM THỬ CẮM USB THẬT (QEMU usb-storage) ==="
L "Máy: $env:COMPUTERNAME | $($os.Caption) $($os.Version) | quyền Administrator: $elev"
Start-Sleep 20   # để Windows ổn định sau lần đăng nhập đầu
Clean-Desktop

# E01: trước khi cài, USB giả lập phải hoạt động như USB thật
Plug A
$w = Watch A 40 -TryWrite -UntilWritable
$bus = (Get-Disk -ErrorAction SilentlyContinue | Where-Object { $_.SerialNumber -like "*$($Serial.A)*" } | Select-Object -First 1).BusType
Check 'E01' 'Trước khi cài: cắm USB thì Windows nhận ổ và ghi được file' ($w.ghi_duoc) ("bus=$bus, có ký tự ổ sau $($w.vol_dau) ms, ghi file sau $($w.ghi_ms) ms")
Shot 'e01-truoc-khi-cai'
Unplug A

# E02: cài bằng bộ cài setup.exe (chế độ im lặng)
$setup = Get-ChildItem 'C:\OEM' -Filter 'UsbGuard-Setup-*.exe' | Select-Object -First 1
$p = Start-Process $setup.FullName -ArgumentList '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', "/ADMINPW=$Pw" -Wait -PassThru
Start-Sleep 5
$svc = Get-Service UsbGuard -ErrorAction SilentlyContinue
$st = (Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\USBSTOR).Start
$deny = (Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeviceInstall\Restrictions' -ErrorAction SilentlyContinue).DenyDeviceIDs
$lnk = Test-Path "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\UsbGuard - Quản lý chặn USB.lnk"
Check 'E02' 'Cài bằng setup.exe: dịch vụ chạy, bật đủ 3 tầng chặn, có lối tắt Start Menu' ($p.ExitCode -eq 0 -and $svc.Status -eq 'Running' -and $st -eq 4 -and $deny -eq 1 -and $lnk) ("mã thoát $($p.ExitCode), dịch vụ $($svc.Status), USBSTOR Start=$st, DenyDeviceIDs=$deny, lối tắt=$lnk")

# E03: chế độ CHẶN TẤT CẢ, cắm USB
$hid0 = HidOk
Clean-Desktop
Plug A
$w = Watch A 15 -TryWrite
$dev = UsbDev A
Shot 'e03-thong-bao-chan-usb'
$logTxt = UgLog
Check 'E03' 'Chặn tất cả: cắm USB không dùng được (không có ổ, không ghi được)' (-not $w.ghi_duoc -and -not $w.con_vol -and -not $w.con_disk) ("thấy ký tự ổ: " + $(if ($null -ne $w.vol_dau) { "có, $($w.vol_dau)-$($w.vol_cuoi) ms" } else { 'không lần nào' }) + ", ghi được: $($w.ghi_duoc), thiết bị USB: $($dev.Status) / $($dev.Problem)")
Check 'E04' 'Chặn tất cả: dịch vụ ghi nhật ký và báo người dùng' ($logTxt -match [regex]::Escape('Đã chặn thiết bị USB lưu trữ') -or $logTxt -match 'Đã gỡ thiết bị USB') ((($logTxt -split "`n") | Where-Object { $_ -match 'chặn thiết bị|gỡ thiết bị' } | Select-Object -Last 1))

# E05: chuột/bàn phím không bị ảnh hưởng, kể cả cắm thêm bàn phím USB mới
$hid1 = HidOk
Plug K
Start-Sleep 12
$kb = @(Get-PnpDevice -PresentOnly -Class Keyboard | Where-Object { $_.InstanceId -like 'HID\*' -or $_.InstanceId -like 'USB\*' })
$hid2 = HidOk
Check 'E05' 'Chuột, bàn phím vẫn hoạt động; cắm bàn phím USB mới vẫn nhận' ($hid1.bad -eq 0 -and $hid2.bad -eq 0 -and $hid2.total -gt $hid1.total) ("trước $($hid1.total) thiết bị (lỗi $($hid1.bad)), sau khi cắm bàn phím USB $($hid2.total) (lỗi $($hid2.bad)): $($hid2.names)")
Unplug K

# E06: tạm dừng khi USB đang cắm sẵn (đang bị chặn) -> dùng được mà không phải rút ra
App @('pause', '10', $Pw) | Out-Null
$w = Watch A 40 -TryWrite -UntilWritable
Check 'E06' 'Tạm dừng: USB đang cắm (đang bị chặn) tự dùng được, không cần rút ra' ($w.ghi_duoc) ("ghi được sau $($w.ghi_ms) ms kể từ lệnh tạm dừng")
if (-not $w.ghi_duoc) { Unplug A; Plug A; $w = Watch A 40 -TryWrite -UntilWritable; L "  rút ra cắm lại: ghi được = $($w.ghi_duoc)" }

# E07: bật lại chặn khi USB đang mở file -> vẫn bị chặn (gỡ hoặc vô hiệu hoá)
$vol = @(Get-CimInstance Win32_Volume | Where-Object { $_.Label -eq $Label.A -and $_.DriveLetter })[0]
$fs = $null
try { $fs = [IO.File]::Open((Join-Path ($vol.DriveLetter + '\') 'dang-mo.txt'), 'OpenOrCreate', 'ReadWrite', 'ReadWrite') } catch { L "  không mở được file: $_" }
App @('resume', $Pw) | Out-Null
$w = Watch A 25 -UntilGone
$disabled = (Get-ItemProperty HKLM:\SOFTWARE\UsbGuard -ErrorAction SilentlyContinue).DisabledDevices
L ("  nhật ký UsbGuard: " + (((UgLog) -split "`n") | Where-Object { $_ -match 'Buộc tháo|gỡ thiết bị' } | Select-Object -Last 2) -join ' / ')
$okE07 = -not (Accessible A)
Check 'E07' 'Bật lại chặn khi USB đang mở file: USB vẫn bị chặn' $okE07 ("còn ổ sau 25 giây: $($w.con_vol); thiết bị bị vô hiệu hoá: $($disabled -join ',')")
if ($fs) { try { $fs.Close() } catch { } }
Unplug A

# E08: whitelist theo số serial (lấy ID ngay khi đang bị chặn, không cần tạm dừng)
Plug B
Start-Sleep 6
$devOut = App @('devices')
L ($devOut.Trim())
Check 'E08' 'Lệnh devices thấy USB đang bị chặn và gợi ý đúng số serial' ($devOut -match $Serial.B) ((($devOut -split "`n") | Where-Object { $_ -match 'Gợi ý|bị chặn' }) -join ' / ')
App @('whitelist', 'add', $Serial.B, $Pw) | Out-Null
$w = Watch B 40 -TryWrite -UntilWritable
Check 'E09' 'Thêm serial vào whitelist: USB đó dùng được (không cần rút ra)' ($w.ghi_duoc) ("ghi được sau $($w.ghi_ms) ms")

# E10: chế độ danh sách cho phép, cắm USB lạ -> bị gỡ nhanh; USB được phép vẫn dùng
$logLen = (UgLog).Length
Clean-Desktop
Plug A
$w = Watch A 15 -TryWrite
$newLog = (UgLog).Substring($logLen)
L ("  nhật ký UsbGuard: " + (($newLog -split "`n") | Where-Object { $_ -match 'gỡ|chặn|Buộc' } | Select-Object -First 3) -join ' / ')
$expose = if ($null -ne $w.vol_dau) { $w.vol_cuoi - $w.vol_dau } else { 0 }
Shot 'e10-whitelist-chan-usb-la'
Check 'E10' 'Danh sách cho phép: USB lạ bị gỡ, ổ tồn tại tối đa 2 giây' (-not $w.con_vol -and -not $w.con_disk -and $expose -le 2000 -and $newLog -match 'không được phép') ("ổ xuất hiện " + $(if ($null -ne $w.vol_dau) { "lúc $($w.vol_dau) ms, mất lúc $($w.vol_cuoi) ms, tồn tại khoảng $expose ms" } else { 'không lần nào' }) + ", ghi được: $($w.ghi_duoc)")
Check 'E11' 'Danh sách cho phép: USB được phép vẫn dùng bình thường' (Accessible B) ''

# GUI: chụp màn hình giao diện quản lý khi đang có 1 USB được phép + 1 USB bị chặn
Clean-Desktop
$gui = Start-Process $App -ArgumentList 'gui' -PassThru
Start-Sleep 8
Shot 'gui-quan-ly'
try { Stop-Process -Id $gui.Id -Force } catch { }
Unplug A

# E12: rút USB được phép ra cắm lại vẫn dùng được
Unplug B
Plug B
$w = Watch B 40 -TryWrite -UntilWritable
Check 'E12' 'Rút USB được phép ra cắm lại vẫn dùng được' ($w.ghi_duoc) ("ghi được sau $($w.ghi_ms) ms")

# E13: xoá khỏi whitelist -> USB đó bị chặn lại
App @('whitelist', 'remove', $Serial.B, $Pw) | Out-Null
$w = Watch B 20 -UntilGone
Check 'E13' 'Xoá khỏi whitelist: USB đang cắm bị chặn lại ngay' (-not (Accessible B)) ("còn ổ: $($w.con_vol)")
Unplug B

# E14: tiến trình bị kill trong lúc USB đang cắm -> sau khi tự chạy lại vẫn chặn
Plug A
Start-Sleep 4
Stop-Process -Name UsbGuard -Force -ErrorAction SilentlyContinue
Start-Sleep 9
$svc = Get-Service UsbGuard
Check 'E14' 'Kill dịch vụ khi USB đang cắm: Windows tự chạy lại, USB vẫn không dùng được' ($svc.Status -eq 'Running' -and -not (Accessible A)) ("dịch vụ: $($svc.Status)")
Unplug A

# E15: gỡ sai mật khẩu bằng trình gỡ của bộ cài -> không gỡ được
$unins = 'C:\Program Files\UsbGuard\unins000.exe'
Start-Process $unins -ArgumentList '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/ADMINPW=sai-mat-khau-1' | Out-Null
Start-Sleep 25
Check 'E15' 'Trình gỡ của bộ cài, sai mật khẩu: không gỡ được' ((Get-Service UsbGuard -ErrorAction SilentlyContinue).Status -eq 'Running' -and (Test-Path $App)) ''

# E16: gỡ đúng mật khẩu -> sạch, USB dùng lại được
Start-Process $unins -ArgumentList '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', "/ADMINPW=$Pw" | Out-Null
$t = [DateTime]::UtcNow
while (([DateTime]::UtcNow - $t).TotalSeconds -lt 90 -and ((Get-Service UsbGuard -ErrorAction SilentlyContinue) -or (Test-Path $App))) { Start-Sleep 1 }
Start-Sleep 5
$st = (Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\USBSTOR).Start
$denyKey = Test-Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeviceInstall\Restrictions\DenyDeviceIDs'
$uninsEntry = @(Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall' | Where-Object { (Get-ItemProperty $_.PSPath).DisplayName -like 'UsbGuard*' }).Count
Check 'E16' 'Gỡ đúng mật khẩu: xoá dịch vụ, file, mục Apps & features, trả lại cấu hình USB' (-not (Get-Service UsbGuard -ErrorAction SilentlyContinue) -and -not (Test-Path $App) -and $st -eq 3 -and -not $denyKey -and $uninsEntry -eq 0) ("USBSTOR Start=$st, còn DenyDeviceIDs: $denyKey, còn mục gỡ cài đặt: $uninsEntry, còn file: $(Test-Path $App)")
Plug A
$w = Watch A 40 -TryWrite -UntilWritable
Check 'E17' 'Sau khi gỡ: cắm USB dùng lại bình thường' ($w.ghi_duoc) ("ghi được sau $($w.ghi_ms) ms")
Unplug A

# ---------------- Ghi kết quả ----------------
$pass = @($results | Where-Object { $_.dat }).Count
L "=== KẾT QUẢ: $pass/$($results.Count) ca ĐẠT ==="
$md = New-Object System.Text.StringBuilder
[void]$md.AppendLine("# Kiểm thử cắm USB thật: $($os.Caption)")
[void]$md.AppendLine("")
[void]$md.AppendLine("Phiên bản Windows: $($os.Version) · Thời điểm: $(Get-Date -f 'yyyy-MM-dd HH:mm:ss') · Kết quả: **$pass/$($results.Count) ca đạt**")
[void]$md.AppendLine("")
[void]$md.AppendLine("USB: ổ QEMU usb-storage cắm nóng vào cổng xHCI (Windows nhận là USB flash disk thật: bus USB, driver USBSTOR).")
[void]$md.AppendLine("")
[void]$md.AppendLine("| Mã | Ca kiểm thử | Kết quả | Chi tiết |")
[void]$md.AppendLine("|---|---|---|---|")
foreach ($r in $results) { [void]$md.AppendLine("| $($r.id) | $($r.ten) | $(if ($r.dat) { 'Đạt' } else { 'KHÔNG ĐẠT' }) | $(($r.chi_tiet -replace '\|', '/')) |") }
[void]$md.AppendLine("")
[void]$md.AppendLine("## Nhật ký chạy")
[void]$md.AppendLine('```')
[void]$md.Append($transcript.ToString())
[void]$md.AppendLine('```')
$tag = ($os.Caption -replace '[^A-Za-z0-9]+', '-').Trim('-')
[IO.File]::WriteAllText((Join-Path $Out "e2e-usb-$tag.md"), $md.ToString(), (New-Object System.Text.UTF8Encoding $true))
$json = @{ he_dieu_hanh = $os.Caption; phien_ban = $os.Version; dat = $pass; tong = $results.Count; ca = $results } | ConvertTo-Json -Depth 4
[IO.File]::WriteAllText((Join-Path $Out "e2e-usb-$tag.json"), $json, (New-Object System.Text.UTF8Encoding $true))
Set-Content (Join-Path $Z 'done.txt') "$pass/$($results.Count)" -Encoding ASCII

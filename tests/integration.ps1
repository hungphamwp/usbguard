<#
  Kiểm thử tích hợp UsbGuard trên Windows thật (chạy với quyền Administrator).
  Cài dịch vụ thật, đo phản ứng thật trên registry/SCM, thử tắt bằng admin và bằng user thường, rồi gỡ sạch.
  Không cần USB vật lý: các ca cắm USB thật nằm trong KICH-BAN-KIEM-THU.md (chạy trên máy có cổng USB).

  Dùng:  powershell -ExecutionPolicy Bypass -File tests\integration.ps1 -Exe bin\Release\net48\UsbGuard.exe
  Kết quả: tests\ket-qua\integration-<máy>.md và .json
#>
param(
    [Parameter(Mandatory = $true)][string]$Exe,
    [string]$OutDir = (Join-Path $PSScriptRoot 'ket-qua')
)

$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Exe = (Resolve-Path $Exe).Path
$Pw = 'MatKhauTest@2026'
$Svc = 'UsbGuard'
$UsbStor = 'HKLM:\SYSTEM\CurrentControlSet\Services\USBSTOR'
$Policy = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices'
$results = New-Object System.Collections.ArrayList
$transcript = New-Object System.Text.StringBuilder
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Say($s) { Write-Host $s; [void]$transcript.AppendLine($s) }

function Run-Exe([string[]]$a) {
    $out = & $Exe @a 2>&1 | Out-String
    $rc = $LASTEXITCODE
    Say ("> UsbGuard.exe " + ($a -join ' ').Replace($Pw, '********') + "   (mã thoát $rc)")
    foreach ($l in ($out.TrimEnd() -split "`r?`n")) { if ($l) { Say ("  " + $l) } }
    return @{ rc = $rc; out = $out }
}

function Run-Cmd([string]$file, [string]$argline) {
    $out = cmd.exe /c "$file $argline 2>&1" | Out-String
    $rc = $LASTEXITCODE
    Say ("> $file $argline   (mã thoát $rc)")
    foreach ($l in ($out.TrimEnd() -split "`r?`n")) { if ($l.Trim()) { Say ("  " + $l.Trim()) } }
    return @{ rc = $rc; out = $out }
}

function Check([string]$id, [string]$name, [bool]$ok, [string]$detail) {
    $r = [pscustomobject]@{ id = $id; ten = $name; dat = $ok; chi_tiet = $detail }
    [void]$results.Add($r)
    $mark = if ($ok) { "[ĐẠT] " } else { "[LỖI] " }
    Say ($mark + "$id $name — $detail")
}

function Get-Start { (Get-ItemProperty $UsbStor -Name Start -ErrorAction SilentlyContinue).Start }
function Get-DenyAll { (Get-ItemProperty $Policy -Name Deny_All -ErrorAction SilentlyContinue).Deny_All }
function Svc-State { $s = Get-Service $Svc -ErrorAction SilentlyContinue; if ($s) { [string]$s.Status } else { 'KHÔNG CÓ' } }
function Svc-Pid { (Get-CimInstance Win32_Service -Filter "Name='$Svc'" -ErrorAction SilentlyContinue).ProcessId }

# Chờ tới khi điều kiện đúng, trả về số mili giây đã chờ (hoặc -1 nếu hết giờ)
function Wait-Until([scriptblock]$cond, [int]$timeoutMs) {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    while ($sw.ElapsedMilliseconds -lt $timeoutMs) {
        if (& $cond) { return [int]$sw.ElapsedMilliseconds }
        Start-Sleep -Milliseconds 100
    }
    return -1
}

$os = Get-CimInstance Win32_OperatingSystem
Say "=== KIỂM THỬ TÍCH HỢP USBGUARD ==="
Say ("Máy: $env:COMPUTERNAME | " + $os.Caption + " " + $os.Version + " | " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Say ("Chạy bằng: " + [Security.Principal.WindowsIdentity]::GetCurrent().Name)
Say ("USBSTOR trước khi cài: Start = " + (Get-Start))
$hasUsbStor = Test-Path $UsbStor
# Giả lập công ty đã có sẵn 1 mục chính sách cấm cài thiết bị: UsbGuard không được đè hay xoá mục này.
$DevRestr = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeviceInstall\Restrictions'
$DenyList = "$DevRestr\DenyDeviceIDs"
New-Item -Path $DenyList -Force | Out-Null
Set-ItemProperty $DevRestr -Name DenyDeviceIDs -Value 1 -Type DWord
Set-ItemProperty $DenyList -Name '1' -Value 'USB\VID_DEAD&PID_BEEF'
Say "Chính sách có sẵn của 'công ty': DenyDeviceIDs\1 = USB\VID_DEAD&PID_BEEF"
function Get-OurDeny { $k = Get-ItemProperty $DenyList -ErrorAction SilentlyContinue; if ($k) { @($k.PSObject.Properties | Where-Object { $_.Name -like 'UsbGuard*' } | ForEach-Object { $_.Value }) } else { @() } }
Say ""

# ---------- TC01: cài đặt ----------
Say "--- TC01 Cài đặt dịch vụ ---"
$r = Run-Exe @('install', $Pw)
$t = Wait-Until { (Svc-State) -eq 'Running' } 15000
$svcObj = Get-Service $Svc -ErrorAction SilentlyContinue
Check 'TC01' 'Cài đặt, dịch vụ chạy' ($r.rc -eq 0 -and $t -ge 0) ("mã thoát $($r.rc), trạng thái " + (Svc-State))
Check 'TC02' 'Khởi động tự động cùng Windows' ($svcObj -and [string]$svcObj.StartType -eq 'Automatic') ("StartType = " + $svcObj.StartType)
$qf = Run-Cmd 'sc.exe' "qfailure $Svc"
Check 'TC03' 'Cấu hình tự khởi động lại khi bị kill' ($qf.out -match 'RESTART') 'sc qfailure có RESTART'
$qc = Run-Cmd 'sc.exe' "qc $Svc"
Check 'TC04' 'Chạy dưới tài khoản LocalSystem' ($qc.out -match 'LocalSystem') 'SERVICE_START_NAME = LocalSystem'

# ---------- TC05-07: chặn ở mức driver/chính sách ----------
Say ""; Say "--- TC05 Chặn driver lưu trữ USB ---"
if ($hasUsbStor) {
    $t = Wait-Until { (Get-Start) -eq 4 } 6000
    Check 'TC05' 'USBSTOR bị tắt (Start = 4)' ($t -ge 0) ("Start = " + (Get-Start) + ", sau $t ms")
} else { Check 'TC05' 'USBSTOR bị tắt (Start = 4)' $true 'máy không có khoá USBSTOR, bỏ qua' }
$t = Wait-Until { (Get-DenyAll) -eq 1 } 6000
Check 'TC06' 'Chính sách Removable Storage Deny_All = 1' ($t -ge 0) ("Deny_All = " + (Get-DenyAll))

if ($hasUsbStor) {
    Say "--- TC07 Sửa tay registry, dịch vụ phải tự khoá lại ---"
    Set-ItemProperty $UsbStor -Name Start -Value 3
    Say "  Đã đặt tay USBSTOR Start = 3"
    $t = Wait-Until { (Get-Start) -eq 4 } 8000
    Check 'TC07' 'Tự sửa khi registry bị đổi tay' ($t -ge 0) ("khôi phục Start = 4 sau $t ms")
    $script:repairMs = $t
}

# ---------- TC31-32: tầng 3 - cấm Windows cài thiết bị lưu trữ USB ----------
Say ""; Say "--- TC31 Tầng 3: Device Installation Restrictions ---"
$t = Wait-Until { (Get-OurDeny) -contains 'USB\Class_08' } 6000
$fl = (Get-ItemProperty $DevRestr -ErrorAction SilentlyContinue).DenyDeviceIDs
$foreign = (Get-ItemProperty $DenyList -ErrorAction SilentlyContinue).'1'
Check 'TC31' 'Tầng 3: cấm cài thiết bị lớp USB Mass Storage, giữ nguyên mục của công ty' ($t -ge 0 -and $fl -eq 1 -and $foreign -eq 'USB\VID_DEAD&PID_BEEF') ("DenyDeviceIDs = $fl, mục UsbGuard: " + ((Get-OurDeny) -join ', ') + "; mục công ty còn: $foreign")
Remove-ItemProperty $DenyList -Name 'UsbGuard3' -ErrorAction SilentlyContinue
Say "  Đã xoá tay mục UsbGuard3 (USB\Class_08)"
$t = Wait-Until { (Get-OurDeny) -contains 'USB\Class_08' } 8000
Check 'TC32' 'Tầng 3 tự sửa khi bị xoá tay' ($t -ge 0) ("khôi phục sau $t ms")

# ---------- TC08-10: "không tắt được" với Administrator ----------
Say ""; Say "--- TC08 Administrator thử dừng dịch vụ ---"
$r = Run-Cmd 'sc.exe' "stop $Svc"
Start-Sleep -Seconds 2
Check 'TC08' 'Admin "sc stop" bị từ chối' ($r.rc -ne 0 -and (Svc-State) -eq 'Running') ("mã $($r.rc) (1052 = dịch vụ không nhận lệnh Stop), trạng thái " + (Svc-State))
$err = $null
try { Stop-Service $Svc -ErrorAction Stop } catch { $err = $_.Exception.Message }
Say ("> Stop-Service UsbGuard  =>  " + $err)
Check 'TC09' 'Admin Stop-Service (PowerShell) bị từ chối' ($err -ne $null -and (Svc-State) -eq 'Running') ("trạng thái " + (Svc-State))

$pid1 = Svc-Pid
$r = Run-Cmd 'taskkill.exe' "/F /PID $pid1"
$t = Wait-Until { (Svc-State) -eq 'Running' -and (Svc-Pid) -ne $pid1 -and (Svc-Pid) -gt 0 } 20000
Check 'TC10' 'Bị kill tiến trình thì Windows tự chạy lại' ($t -ge 0) ("PID $pid1 -> " + (Svc-Pid) + ", chạy lại sau $t ms")
$script:restartMs = $t

# ---------- TC11-15: người dùng thường ----------
Say ""; Say "--- TC11 Người dùng thường (không phải Administrator) ---"
$uName = 'ugthuong'
$uPw = 'Th' + [Guid]::NewGuid().ToString('N').Substring(0, 12) + '!9'
net user $uName $uPw /add /y | Out-Null
Say "  Đã tạo tài khoản thường '$uName' (nhóm Users)."
$work = 'C:\ugtest'
New-Item -ItemType Directory -Force -Path $work | Out-Null
icacls $work /grant "${uName}:(OI)(CI)M" | Out-Null
Copy-Item $Exe "$work\UsbGuard.exe" -Force
Set-Service seclogon -StartupType Manual -ErrorAction SilentlyContinue
Start-Service seclogon -ErrorAction SilentlyContinue

$cred = New-Object Management.Automation.PSCredential($uName, (ConvertTo-SecureString $uPw -AsPlainText -Force))
function Ran($r) { return $r.rc -ge 0 -and $r.out -match 'EXIT=' }
function Run-AsUser([string]$label, [string]$cmdline) {
    $bat = "$work\$label.cmd"; $out = "$work\$label.txt"
    Set-Content $bat "@echo off`r`nchcp 65001 >nul`r`nwhoami`r`n$cmdline`r`necho EXIT=%ERRORLEVEL%" -Encoding ASCII
    try {
        # Đường dẫn không có dấu cách nên không bọc nháy (cmd /c bóc nháy sai khi có nhiều cặp nháy)
        $p = Start-Process cmd.exe -ArgumentList "/c $bat > $out 2>&1" -Credential $cred -WorkingDirectory $work -Wait -PassThru -LoadUserProfile
        Say ("  (tiến trình user thường kết thúc, mã " + $p.ExitCode + ")")
    } catch { Say ("  Không chạy được bằng user thường: " + $_.Exception.Message); return @{ rc = -999; out = '' } }
    $txt = if (Test-Path $out) { Get-Content $out -Raw -Encoding UTF8 } else { '' }
    $rc = if ($txt -match 'EXIT=(-?\d+)') { [int]$Matches[1] } else { -998 }
    Say ("> [$uName] " + $cmdline.Replace($Pw, '********') + "   (mã thoát $rc)")
    foreach ($l in ($txt.TrimEnd() -split "`r?`n")) { if ($l.Trim() -and $l -notmatch '^EXIT=') { Say ("  " + $l.Trim()) } }
    return @{ rc = $rc; out = $txt }
}

$r = Run-AsUser 'u1' "sc.exe stop $Svc"
Check 'TC11' 'User thường "sc stop" bị từ chối quyền' ($r.rc -eq 5 -and (Svc-State) -eq 'Running') ("mã $($r.rc) (5 = Access is denied)")
$r = Run-AsUser 'u2' "sc.exe config $Svc start= disabled"
Check 'TC12' 'User thường không đổi được kiểu khởi động' ($r.rc -eq 5) ("mã $($r.rc)")
$r = Run-AsUser 'u3' "sc.exe delete $Svc"
Check 'TC13' 'User thường không xoá được dịch vụ' ($r.rc -eq 5 -and (Svc-State) -eq 'Running') ("mã $($r.rc)")
$r = Run-AsUser 'u4' "reg.exe query HKLM\SOFTWARE\UsbGuard"
Check 'TC14' 'User thường không đọc được cấu hình/mã băm mật khẩu' ((Ran $r) -and $r.rc -ne 0 -and $r.out -notmatch 'pbkdf2') ("mã $($r.rc)")
$r = Run-AsUser 'u5' "UsbGuard.exe uninstall $Pw"
Check 'TC15' 'User thường gỡ cài đặt bị từ chối (kể cả biết mật khẩu)' ((Ran $r) -and $r.rc -ne 0 -and (Svc-State) -eq 'Running') ("mã $($r.rc)")
$r = Run-AsUser 'u6' "reg.exe add HKLM\SYSTEM\CurrentControlSet\Services\USBSTOR /v Start /t REG_DWORD /d 3 /f"
Check 'TC16' 'User thường không mở lại được driver USB' ((Ran $r) -and $r.rc -ne 0 -and ((-not $hasUsbStor) -or (Get-Start) -eq 4)) ("mã $($r.rc)")

# ---------- TC17-22: chức năng quản trị ----------
Say ""; Say "--- TC17 Chức năng quản trị (Administrator) ---"
$r = Run-Exe @('pause', '1', 'sai-mat-khau-123')
Check 'TC17' 'Tạm dừng với sai mật khẩu bị từ chối' ($r.rc -eq 3 -and (Get-DenyAll) -eq 1) ("mã $($r.rc)")
$r = Run-Exe @('pause', '1', $Pw)
$t = Wait-Until { (Get-DenyAll) -eq $null -and ((-not $hasUsbStor) -or (Get-Start) -eq 3) } 6000
Check 'TC18' 'Tạm dừng đúng mật khẩu: mở lại USB' ($r.rc -eq 0 -and $t -ge 0) ("USBSTOR Start = " + (Get-Start) + ", sau $t ms")
$r = Run-Exe @('resume', $Pw)
$t = Wait-Until { (Get-DenyAll) -eq 1 -and ((-not $hasUsbStor) -or (Get-Start) -eq 4) } 6000
Check 'TC19' 'Bật lại chặn' ($r.rc -eq 0 -and $t -ge 0) ("USBSTOR Start = " + (Get-Start) + ", sau $t ms")
$r = Run-Exe @('whitelist', 'add', 'VID_0951&PID_1666', $Pw)
$t = Wait-Until { (Get-DenyAll) -eq $null -and ((-not $hasUsbStor) -or (Get-Start) -eq 3) } 6000
Check 'TC20' 'Có whitelist: chuyển sang chế độ danh sách cho phép' ($r.rc -eq 0 -and $t -ge 0) ("driver mở để USB được phép chạy, sau $t ms")
$r = Run-Exe @('whitelist', 'list')
Check 'TC21' 'Xem whitelist' ($r.rc -eq 0 -and $r.out -match 'VID_0951') 'có VID_0951&PID_1666'
$r = Run-Exe @('whitelist', 'remove', 'VID_0951&PID_1666', $Pw)
$t = Wait-Until { (Get-DenyAll) -eq 1 -and ((-not $hasUsbStor) -or (Get-Start) -eq 4) } 6000
Check 'TC22' 'Xoá whitelist: quay lại chặn tất cả' ($r.rc -eq 0 -and $t -ge 0) ("sau $t ms")
$r = Run-Exe @('passwd', $Pw, 'MatKhauMoi@2026')
$r2 = Run-Exe @('passwd', 'MatKhauMoi@2026', $Pw)
Check 'TC23' 'Đổi mật khẩu quản trị' ($r.rc -eq 0 -and $r2.rc -eq 0) 'đổi sang mật khẩu mới rồi đổi lại'
$r = Run-Exe @('devices', '--all')
Check 'TC24' 'Liệt kê ổ đĩa qua SetupAPI + IOCTL (gọi API Windows thật)' ($r.rc -eq 0 -and $r.out -match 'bus ') 'đọc được loại bus của từng ổ'
$r = Run-Exe @('devices')
Check 'TC25' 'Không nhận nhầm ổ cứng trong máy là USB' ($r.rc -eq 0 -and $r.out -match ': 0') 'máy không cắm USB, kết quả 0 ổ USB'
$r = Run-Exe @('status')
Check 'TC26' 'Xem trạng thái' ($r.rc -eq 0 -and $r.out -match 'RUNNING') 'RUNNING, chế độ CHẶN TẤT CẢ'
Check 'TC33' 'Trạng thái hiện đủ 3 tầng chặn' ($r.out -match 'Tầng 1 driver USBSTOR: TẮT' -and $r.out -match 'Tầng 2 Deny_All: BẬT' -and $r.out -match 'Tầng 3 cấm cài USB lưu trữ: BẬT') ((($r.out -split "`n") | Where-Object { $_ -match 'Tầng 1' }) -join '')

$logFile = Join-Path $env:ProgramData 'UsbGuard\usbguard.log'
$logTxt = if (Test-Path $logFile) { Get-Content $logFile -Raw -Encoding UTF8 } else { '' }
Check 'TC27' 'Ghi nhật ký hoạt động' ($logTxt -match 'Chế độ' -and $logTxt -match 'khởi động') $logFile

# ---------- TC35-37: chống dò mật khẩu ----------
Say ""; Say "--- TC35 Chống dò mật khẩu ---"
$cfg = Get-ItemProperty 'HKLM:\SOFTWARE\UsbGuard' -ErrorAction SilentlyContinue
Check 'TC35' 'Mật khẩu lưu bằng PBKDF2-SHA256 600.000 vòng, có muối' ([string]$cfg.AuthHash -like 'pbkdf2-sha256$600000$*') (([string]$cfg.AuthHash -split '\$')[0..1] -join ' ')
$r5 = $null
for ($i = 1; $i -le 5; $i++) { $r5 = Run-Exe @('pause', '1', "sai-mat-khau-$i") }
$sw = [Diagnostics.Stopwatch]::StartNew()
$r = Run-Exe @('pause', '1', $Pw)
$fails = (Get-ItemProperty 'HKLM:\SOFTWARE\UsbGuard').AuthFails
Check 'TC36' 'Sai 5 lần liên tiếp: bị khoá, nhập đúng mật khẩu cũng bị từ chối tới khi hết khoá' ($r5.out -match 'thử lại sau' -and $r.rc -eq 3 -and $r.out -match 'thử lại sau' -and (Get-DenyAll) -eq 1 -and $fails -eq 5) ("lần sai thứ 5: " + (($r5.out -split "`n") | Where-Object { $_ -match 'thử lại' } | Select-Object -First 1).Trim() + " | nhập đúng khi đang khoá: mã $($r.rc)")
Start-Sleep -Milliseconds ([math]::Max(0, 31500 - $sw.ElapsedMilliseconds))
$r = Run-Exe @('resume', $Pw)
$fails = (Get-ItemProperty 'HKLM:\SOFTWARE\UsbGuard').AuthFails
Check 'TC37' 'Hết 30 giây khoá: đúng mật khẩu dùng lại được, bộ đếm sai về 0' ($r.rc -eq 0 -and $fails -eq 0) ("mã $($r.rc), số lần sai còn lại $fails")

# ---------- TC38-40: Admin đổi kiểu khởi động (services.msc / sc config / Registry) ----------
Say ""; Say "--- TC38 Đổi Startup type thành Disabled ---"
$SvcKey = "HKLM:\SYSTEM\CurrentControlSet\Services\$Svc"
$r = Run-Cmd 'sc.exe' "config $Svc start= disabled"
$st = (Get-CimInstance Win32_Service -Filter "Name='$Svc'").StartMode
Check 'TC38' 'Admin đổi Startup type (services.msc, sc config): bị từ chối' ($r.rc -eq 5 -and $st -eq 'Auto') ("sc config mã $($r.rc), StartMode = $st")
Set-ItemProperty $SvcKey -Name Start -Value 4
$t = Wait-Until { (Get-ItemProperty $SvcKey -Name Start).Start -eq 2 } 15000
Check 'TC39' 'Admin sửa thẳng Registry đặt dịch vụ Disabled: dịch vụ tự trả lại Automatic' ($t -ge 0 -and (Svc-State) -eq 'Running') ("trả lại sau $t ms")
Remove-ItemProperty $SvcKey -Name FailureActions -ErrorAction SilentlyContinue
$t = Wait-Until { $q = cmd.exe /c "sc.exe qfailure $Svc 2>&1" | Out-String; $q -match 'RESTART' } 15000
Check 'TC40' 'Admin xoá cấu hình tự chạy lại khi bị kill: dịch vụ tự đặt lại' ($t -ge 0) ("đặt lại sau $t ms")

# ---------- Đo tài nguyên (không tính đạt/lỗi, chỉ ghi số đo) ----------
Say ""; Say "--- Đo tài nguyên dịch vụ trong 60 giây ---"
$procId = Svc-Pid
$pr = Get-Process -Id $procId
$cpu0 = $pr.TotalProcessorTime.TotalMilliseconds; $sw = [Diagnostics.Stopwatch]::StartNew()
$ramMax = 0; $ramSum = 0; $nS = 0
for ($k = 0; $k -lt 60; $k++) {
    Start-Sleep -Seconds 1
    $pr.Refresh(); $mb = [math]::Round($pr.WorkingSet64 / 1MB, 1)
    $ramSum += $mb; $nS++; if ($mb -gt $ramMax) { $ramMax = $mb }
}
$pr.Refresh()
$cpuPct = [math]::Round(100 * ($pr.TotalProcessorTime.TotalMilliseconds - $cpu0) / $sw.ElapsedMilliseconds / [Environment]::ProcessorCount, 2)
$script:ramTb = [math]::Round($ramSum / $nS, 1); $script:ramMax = $ramMax; $script:cpuPct = $cpuPct
Say ("  RAM (working set): trung bình $($script:ramTb) MB, cao nhất $ramMax MB; CPU trung bình $cpuPct % (trên " + [Environment]::ProcessorCount + " lõi)")

# ---------- TC28-30: gỡ cài đặt ----------
Say ""; Say "--- TC28 Gỡ cài đặt ---"
$r = Run-Exe @('uninstall', 'sai-mat-khau-123')
Check 'TC28' 'Gỡ với sai mật khẩu bị từ chối' ($r.rc -eq 3 -and (Svc-State) -eq 'Running') ("mã $($r.rc), trạng thái " + (Svc-State))
$sw = [Diagnostics.Stopwatch]::StartNew()
$r = Run-Exe @('uninstall', $Pw)
$ms = $sw.ElapsedMilliseconds
$q = Run-Cmd 'sc.exe' "query $Svc"
Check 'TC29' 'Gỡ đúng mật khẩu: dịch vụ tự dừng và bị xoá' ($r.rc -eq 0 -and $q.rc -eq 1060) ("mất $ms ms, sc query trả 1060 (không còn dịch vụ)")
$clean = ((-not $hasUsbStor) -or (Get-Start) -eq 3) -and (Get-DenyAll) -eq $null -and -not (Test-Path 'HKLM:\SOFTWARE\UsbGuard') -and -not (Test-Path "$env:ProgramFiles\UsbGuard")
Check 'TC30' 'Trả lại mặc định Windows sau khi gỡ' $clean
$fl = (Get-ItemProperty $DevRestr -ErrorAction SilentlyContinue).DenyDeviceIDs
$foreign = (Get-ItemProperty $DenyList -ErrorAction SilentlyContinue).'1'
Check 'TC34' 'Gỡ cài đặt chỉ xoá mục của UsbGuard, giữ chính sách có sẵn của công ty' ((Get-OurDeny).Count -eq 0 -and $fl -eq 1 -and $foreign -eq 'USB\VID_DEAD&PID_BEEF') ("còn mục UsbGuard: " + (Get-OurDeny).Count + ", DenyDeviceIDs = $fl, mục công ty: $foreign")
Remove-Item $DevRestr -Recurse -Force -ErrorAction SilentlyContinue ("USBSTOR Start = " + (Get-Start) + ", Deny_All = " + (Get-DenyAll) + ", không còn khoá cấu hình và thư mục cài")

net user $uName /delete | Out-Null
Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue

# ---------- Ghi kết quả ----------
$pass = @($results | Where-Object { $_.dat }).Count
$total = $results.Count
Say ""; Say "=== KẾT QUẢ: $pass/$total ca ĐẠT ==="
$tag = ($os.Caption -replace '[^A-Za-z0-9]+', '-').Trim('-')
$md = New-Object System.Text.StringBuilder
[void]$md.AppendLine("# Kết quả kiểm thử tích hợp UsbGuard — " + $os.Caption + " (" + $os.Version + ")")
[void]$md.AppendLine("")
[void]$md.AppendLine("Thời điểm: " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + " · Kết quả: **$pass/$total ca đạt**")
[void]$md.AppendLine("")
[void]$md.AppendLine("| Mã | Ca kiểm thử | Kết quả | Chi tiết |")
[void]$md.AppendLine("|---|---|---|---|")
foreach ($x in $results) {
    $kq = if ($x.dat) { 'Đạt' } else { 'Không đạt' }
    [void]$md.AppendLine("| $($x.id) | $($x.ten) | $kq | $($x.chi_tiet) |")
}
[void]$md.AppendLine("")
[void]$md.AppendLine("## Nhật ký chạy")
[void]$md.AppendLine('```')
[void]$md.Append($transcript.ToString())
[void]$md.AppendLine('```')
[IO.File]::WriteAllText((Join-Path $OutDir "integration-$tag.md"), $md.ToString(), (New-Object Text.UTF8Encoding($false)))
[pscustomobject]@{ he_dieu_hanh = $os.Caption; phien_ban = $os.Version; dat = $pass; tong = $total; tu_sua_ms = $script:repairMs; chay_lai_ms = $script:restartMs; ram_tb_mb = $script:ramTb; ram_max_mb = $script:ramMax; cpu_pct = $script:cpuPct; ca = $results } |
    ConvertTo-Json -Depth 5 | Set-Content (Join-Path $OutDir "integration-$tag.json") -Encoding UTF8
if ($pass -ne $total) { exit 1 } else { exit 0 }

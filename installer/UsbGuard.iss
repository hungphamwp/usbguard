; Bộ cài UsbGuard (Inno Setup 6). Biên dịch: ISCC.exe /DAppVersion=1.2.1 installer\UsbGuard.iss
#ifndef AppVersion
  #define AppVersion "1.2.1"
#endif

[Setup]
AppId={{6C1E8B0A-3F2D-4E7B-9A51-2B7D4C8E9F10}
AppName=UsbGuard
AppVersion={#AppVersion}
AppVerName=UsbGuard {#AppVersion}
AppPublisher=Phạm Văn Hưng
VersionInfoVersion={#AppVersion}
VersionInfoDescription=Bộ cài UsbGuard - chặn USB flash disk trên Windows
DefaultDirName={autopf}\UsbGuard
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=no
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\dist
OutputBaseFilename=UsbGuard-Setup-{#AppVersion}
SetupIconFile=..\assets\usbguard.ico
UninstallDisplayIcon={app}\UsbGuard.exe
UninstallDisplayName=UsbGuard {#AppVersion}
WizardStyle=modern
Compression=lzma2
SolidCompression=yes
CloseApplications=no
LicenseFile=license-vi.txt

[Languages]
Name: "vi"; MessagesFile: "Vietnamese.isl"

[Files]
Source: "..\bin\Release\net48\UsbGuard.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\release\HUONG-DAN-SU-DUNG.pdf"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{autoprograms}\UsbGuard - Quản lý chặn USB"; Filename: "{app}\UsbGuard.exe"; Parameters: "gui"; Flags: runminimized
Name: "{autodesktop}\UsbGuard"; Filename: "{app}\UsbGuard.exe"; Parameters: "gui"; Flags: runminimized
Name: "{autoprograms}\Hướng dẫn sử dụng UsbGuard"; Filename: "{app}\HUONG-DAN-SU-DUNG.pdf"; Check: HasGuide

[Run]
Filename: "{app}\UsbGuard.exe"; Parameters: "gui"; Description: "Mở UsbGuard ngay"; Flags: postinstall nowait skipifsilent runascurrentuser runminimized

[Code]
function SetEnvironmentVariable(lpName, lpValue: string): Boolean;
  external 'SetEnvironmentVariableW@kernel32.dll stdcall';

var
  PwPage: TInputQueryWizardPage;

function HasGuide: Boolean;
begin
  Result := FileExists(ExpandConstant('{app}\HUONG-DAN-SU-DUNG.pdf'));
end;

function ServiceInstalled: Boolean;
var rc: Integer;
begin
  Result := Exec(ExpandConstant('{sys}\sc.exe'), 'query UsbGuard', '', SW_HIDE, ewWaitUntilTerminated, rc) and (rc <> 1060);
end;

function InitializeSetup: Boolean;
begin
  Result := True;
  if ServiceInstalled then
  begin
    SuppressibleMsgBox('UsbGuard đã được cài trên máy này. Muốn cài lại, hãy gỡ bản cũ trước (Settings > Apps > UsbGuard, hoặc nút "Gỡ cài đặt" trong UsbGuard).',
      mbInformation, MB_OK, IDOK);
    Result := False;
  end;
end;

procedure InitializeWizard;
begin
  PwPage := CreateInputQueryPage(wpLicense, 'Mật khẩu quản trị',
    'Mật khẩu dùng để tạm dừng chặn, cho phép USB và gỡ cài đặt UsbGuard.',
    'Đặt mật khẩu ít nhất 8 ký tự. Hãy ghi lại ở nơi an toàn: quên mật khẩu thì không gỡ được UsbGuard theo cách thông thường.');
  PwPage.Add('Mật khẩu:', True);
  PwPage.Add('Nhập lại mật khẩu:', True);
end;

function AdminPassword: String;
begin
  Result := ExpandConstant('{param:ADMINPW}');
  if Result = '' then Result := PwPage.Values[0];
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = PwPage.ID then
  begin
    if Length(PwPage.Values[0]) < 8 then
    begin
      MsgBox('Mật khẩu phải có ít nhất 8 ký tự.', mbError, MB_OK);
      Result := False;
    end
    else if PwPage.Values[0] <> PwPage.Values[1] then
    begin
      MsgBox('Mật khẩu nhập lại không khớp.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := (PageID = PwPage.ID) and (ExpandConstant('{param:ADMINPW}') <> '');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var rc: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    if Length(AdminPassword) < 8 then
      RaiseException('Mật khẩu quản trị phải có ít nhất 8 ký tự (tham số /ADMINPW=...).');
    // Truyền mật khẩu qua biến môi trường, không đưa lên dòng lệnh.
    SetEnvironmentVariable('USBGUARD_ADMIN_PW', AdminPassword);
    if not Exec(ExpandConstant('{app}\UsbGuard.exe'), 'install', '', SW_HIDE, ewWaitUntilTerminated, rc) or (rc <> 0) then
    begin
      SetEnvironmentVariable('USBGUARD_ADMIN_PW', '');
      SuppressibleMsgBox('Không cài được dịch vụ UsbGuard (mã ' + IntToStr(rc) + '). Hãy chạy lại bộ cài bằng quyền Administrator.', mbError, MB_OK, IDOK);
      Exit;
    end;
    SetEnvironmentVariable('USBGUARD_ADMIN_PW', '');
  end;
end;

{ ---------- Gỡ cài đặt: bắt buộc đúng mật khẩu quản trị ---------- }

function AskUninstallPassword(var pw: String): Boolean;
var
  Form: TSetupForm;
  Lbl: TNewStaticText;
  Edit: TPasswordEdit;
  Ok, Cancel: TNewButton;
begin
  Form := CreateCustomForm(ScaleX(400), ScaleY(150), False, True);
  try
    Form.Caption := 'Gỡ cài đặt UsbGuard';
    Lbl := TNewStaticText.Create(Form);
    Lbl.Parent := Form; Lbl.Left := ScaleX(16); Lbl.Top := ScaleY(16);
    Lbl.Caption := 'Nhập mật khẩu quản trị UsbGuard để gỡ cài đặt:';
    Edit := TPasswordEdit.Create(Form);
    Edit.Parent := Form; Edit.Left := ScaleX(16); Edit.Top := ScaleY(44); Edit.Width := ScaleX(368);
    Ok := TNewButton.Create(Form);
    Ok.Parent := Form; Ok.Caption := 'Gỡ cài đặt'; Ok.ModalResult := mrOk; Ok.Default := True;
    Ok.Left := ScaleX(204); Ok.Top := ScaleY(96); Ok.Width := ScaleX(88); Ok.Height := ScaleY(28);
    Cancel := TNewButton.Create(Form);
    Cancel.Parent := Form; Cancel.Caption := 'Huỷ'; Cancel.ModalResult := mrCancel; Cancel.Cancel := True;
    Cancel.Left := ScaleX(296); Cancel.Top := ScaleY(96); Cancel.Width := ScaleX(88); Cancel.Height := ScaleY(28);
    Form.ActiveControl := Edit;
    Result := Form.ShowModal = mrOk;
    pw := Edit.Text;
  finally
    Form.Free;
  end;
end;

function InitializeUninstall: Boolean;
var pw: String; rc: Integer;
begin
  Result := False;
  if not ServiceInstalled then begin Result := True; Exit; end;
  pw := ExpandConstant('{param:ADMINPW}');
  while True do
  begin
    if pw = '' then
      if UninstallSilent or not AskUninstallPassword(pw) then Exit;
    SetEnvironmentVariable('USBGUARD_ADMIN_PW', pw);
    Exec(ExpandConstant('{app}\UsbGuard.exe'), 'uninstall --keep-files', '', SW_HIDE, ewWaitUntilTerminated, rc);
    SetEnvironmentVariable('USBGUARD_ADMIN_PW', '');
    if rc = 0 then begin Result := True; Exit; end;
    if UninstallSilent then Exit;
    if rc = 3 then MsgBox('Sai mật khẩu quản trị.', mbError, MB_OK)
    else begin MsgBox('Gỡ dịch vụ thất bại (mã ' + IntToStr(rc) + ').', mbError, MB_OK); Exit; end;
    pw := '';
  end;
end;

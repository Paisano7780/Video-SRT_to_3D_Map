; Inno Setup Script for DJI 3D Mapper
; This installer handles downloading and installing FFmpeg and ExifTool

#define MyAppName "DJI 3D Mapper"
#define MyAppVersion "1.0"
#define MyAppPublisher "Paisano7780"
#define MyAppURL "https://github.com/Paisano7780/Video-SRT_to_3D_Map"
#define MyAppExeName "DJI_3D_Mapper.exe"

[Setup]
AppId={{B8F9A3E2-4C1D-4E5F-9B2A-3D7C8E9F1A2B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=DJI_3D_Mapper_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "installffmpeg"; Description: "Download and install FFmpeg (required for frame extraction)"; GroupDescription: "Dependencies:"; Flags: checkedonce
Name: "installexiftool"; Description: "Download and install ExifTool (required for geotagging)"; GroupDescription: "Dependencies:"; Flags: checkedonce

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DownloadPage: TDownloadWizardPage;
  FFmpegInstalled: Boolean;
  ExifToolInstalled: Boolean;
  
function OnDownloadProgress(const Url, FileName: String; const Progress, ProgressMax: Int64): Boolean;
begin
  if Progress = ProgressMax then
    Log(Format('Successfully downloaded %s', [FileName]));
  Result := True;
end;

function CheckFFmpegInstalled: Boolean;
var
  ResultCode: Integer;
begin
  // Check if ffmpeg is in PATH
  Result := Exec('cmd.exe', '/c ffmpeg -version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

function CheckExifToolInstalled: Boolean;
var
  ResultCode: Integer;
begin
  // Check if exiftool is in PATH
  Result := Exec('cmd.exe', '/c exiftool -ver', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

procedure InstallFFmpeg;
var
  FFmpegZip: String;
  ResultCode: Integer;
  FFmpegDir: String;
  UnzipScript: String;
  ScriptFile: String;
begin
  FFmpegZip := ExpandConstant('{tmp}\ffmpeg.zip');
  FFmpegDir := ExpandConstant('{app}\ffmpeg');
  
  if WizardIsTaskSelected('installffmpeg') then
  begin
    Log('Installing FFmpeg...');
    
    // Download FFmpeg
    DownloadPage.Add('https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip', 'ffmpeg.zip', '');
    DownloadPage.Show;
    try
      try
        DownloadPage.Download;
        
        // Create extraction script
        ScriptFile := ExpandConstant('{tmp}\extract_ffmpeg.ps1');
        UnzipScript := Format(
          '$zip = "%s"; ' +
          '$dest = "%s"; ' +
          'Expand-Archive -Path $zip -DestinationPath $dest -Force; ' +
          '$binPath = (Get-ChildItem -Path $dest -Filter "ffmpeg.exe" -Recurse | Select-Object -First 1).DirectoryName; ' +
          'Copy-Item -Path "$binPath\*" -Destination $dest -Force; ' +
          'Get-ChildItem -Path $dest -Directory | Remove-Item -Recurse -Force',
          [FFmpegZip, FFmpegDir]
        );
        SaveStringToFile(ScriptFile, UnzipScript, False);
        
        // Extract FFmpeg using PowerShell
        Exec('powershell.exe', '-ExecutionPolicy Bypass -File "' + ScriptFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
        
        // Add to PATH
        if ResultCode = 0 then
        begin
          Log('FFmpeg extracted successfully');
          // Add FFmpeg to system PATH
          Exec('setx', Format('PATH "%%PATH%%;%s"', [FFmpegDir]), '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
        end
        else
          Log('Failed to extract FFmpeg');
          
      except
        Log('Failed to download or install FFmpeg');
      end;
    finally
      DownloadPage.Hide;
    end;
  end;
end;

procedure InstallExifTool;
var
  ExifToolZip: String;
  ResultCode: Integer;
  ExifToolDir: String;
  UnzipScript: String;
  ScriptFile: String;
begin
  ExifToolZip := ExpandConstant('{tmp}\exiftool.zip');
  ExifToolDir := ExpandConstant('{app}\exiftool');
  
  if WizardIsTaskSelected('installexiftool') then
  begin
    Log('Installing ExifTool...');
    
    // Download ExifTool
    DownloadPage.Add('https://exiftool.org/exiftool-12.76_64.zip', 'exiftool.zip', '');
    DownloadPage.Show;
    try
      try
        DownloadPage.Download;
        
        // Create extraction script
        ScriptFile := ExpandConstant('{tmp}\extract_exiftool.ps1');
        UnzipScript := Format(
          '$zip = "%s"; ' +
          '$dest = "%s"; ' +
          'New-Item -ItemType Directory -Force -Path $dest | Out-Null; ' +
          'Expand-Archive -Path $zip -DestinationPath $dest -Force; ' +
          '$exiftool = Get-ChildItem -Path $dest -Filter "exiftool(-k).exe" -Recurse | Select-Object -First 1; ' +
          'if ($exiftool) { Rename-Item -Path $exiftool.FullName -NewName "exiftool.exe" -Force }',
          [ExifToolZip, ExifToolDir]
        );
        SaveStringToFile(ScriptFile, UnzipScript, False);
        
        // Extract ExifTool using PowerShell
        Exec('powershell.exe', '-ExecutionPolicy Bypass -File "' + ScriptFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
        
        // Add to PATH
        if ResultCode = 0 then
        begin
          Log('ExifTool extracted successfully');
          // Add ExifTool to system PATH
          Exec('setx', Format('PATH "%%PATH%%;%s"', [ExifToolDir]), '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
        end
        else
          Log('Failed to extract ExifTool');
          
      except
        Log('Failed to download or install ExifTool');
      end;
    finally
      DownloadPage.Hide;
    end;
  end;
end;

procedure InitializeWizard;
begin
  // Check if dependencies are already installed
  FFmpegInstalled := CheckFFmpegInstalled;
  ExifToolInstalled := CheckExifToolInstalled;
  
  // Create download page
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), @OnDownloadProgress);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Install dependencies after main installation
    if not FFmpegInstalled then
      InstallFFmpeg;
    if not ExifToolInstalled then
      InstallExifTool;
  end;
end;

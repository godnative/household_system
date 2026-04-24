#define MyAppName "HouseholdSystemWeb"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Household System"
#define MyAppExeName "start.bat"

[Setup]
AppId={{C0D7F387-8AB3-4FC1-BF54-0B0F4B778001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=HouseholdSystemWeb-Offline-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "frontend\dist\*"; DestDir: "{app}\frontend\dist"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "scripts\*"; DestDir: "{app}\scripts"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}\启动 Web 端"; Filename: "{app}\scripts\start.bat"
Name: "{autoprograms}\{#MyAppName}\关闭 Web 端"; Filename: "{app}\scripts\stop.bat"
Name: "{autodesktop}\启动 Web 端"; Filename: "{app}\scripts\start.bat"
Name: "{autodesktop}\关闭 Web 端"; Filename: "{app}\scripts\stop.bat"

[Run]
Filename: "{app}\scripts\start.bat"; Description: "启动 Web 端"; Flags: nowait postinstall skipifsilent

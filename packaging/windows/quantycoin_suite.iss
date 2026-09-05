; QuantyCoin QTY2 Combined Suite Inno Setup Installer Script
#define MyAppName "QuantyCoin Combined Suite"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "QuantyCoin Core Contributors"
#define MyAppURL "https://quantycoin.org"
#define MyAppExeName "QuantyCoinSuite.exe"

[Setup]
AppId={{D37B7B80-99E8-41C2-824A-73891461A999}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\QuantyCoin
DisableProgramGroupPage=yes
LicenseFile=..\..\COPYING
OutputDir=..\..\dist\windows
OutputBaseFilename=QuantyCoin-CombinedSuite-Setup-2.0.0
SetupIconFile=..\..\share\pixmaps\quantycoin.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\dist\bin\QuantyCoinSuite.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\bin\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\share\pixmaps\quantycoin.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\share\pixmaps\quantycoin.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

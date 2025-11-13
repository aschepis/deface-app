[Setup]
AppName=Deface
AppVersion=1.0.0
AppPublisher=Deface App Contributors
AppPublisherURL=https://github.com/aschepis/deface-app
AppSupportURL=https://github.com/aschepis/deface-app/issues
AppUpdatesURL=https://github.com/aschepis/deface-app/releases
DefaultDirName={pf}\Deface
DefaultGroupName=Deface
OutputBaseFilename=DefaceInstaller
Compression=lzma
SolidCompression=yes
LicenseFile=LICENSE
InfoBeforeFile=
InfoAfterFile=
VersionInfoVersion=1.0.0.0
VersionInfoCompany=Deface App Contributors
VersionInfoDescription=GUI application for blurring faces in images and videos
VersionInfoCopyright=Copyright (C) 2025
VersionInfoProductName=Deface
VersionInfoProductVersion=1.0.0

[Files]
Source: "dist\Deface\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Deface"; Filename: "{app}\Deface.exe"
Name: "{group}\Uninstall Deface"; Filename: "{uninstallexe}"
Name: "{userdesktop}\Deface"; Filename: "{app}\Deface.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\Deface.exe"; Description: "Launch Deface"; Flags: nowait postinstall skipifsilent

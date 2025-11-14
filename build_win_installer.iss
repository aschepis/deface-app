// Get version from preprocessor variable (set via /DAPP_VERSION=value) or environment variable
#ifndef APP_VERSION
  #define MyAppVersion GetEnv("APP_VERSION")
  #if MyAppVersion == ""
    #define MyAppVersion "1.0.0"
  #endif
#else
  #define MyAppVersion APP_VERSION
#endif

// VersionInfoVersion requires exactly 4 numeric components (X.X.X.X)
// Standard semantic versions are X.Y.Z (3 components), so append .0
// This converts "1.0.0" to "1.0.0.0" for Windows version info
#define MyAppVersionInfoVersion MyAppVersion + ".0"

[Setup]
AppName=Deface
AppVersion={#MyAppVersion}
AppPublisher=Deface App Contributors
AppPublisherURL=https://github.com/aschepis/deface-app
AppSupportURL=https://github.com/aschepis/deface-app/issues
AppUpdatesURL=https://github.com/aschepis/deface-app/releases
DefaultDirName={autopf}\Deface
DefaultGroupName=Deface
OutputDir=Output
OutputBaseFilename=DefaceInstaller
Compression=lzma
SolidCompression=yes
LicenseFile=LICENSE
InfoBeforeFile=
InfoAfterFile=
VersionInfoVersion={#MyAppVersionInfoVersion}
VersionInfoCompany=Deface App Contributors
VersionInfoDescription=GUI application for blurring faces in images and videos
VersionInfoCopyright=Copyright (C) 2025
VersionInfoProductName=Deface
VersionInfoProductVersion={#MyAppVersion}

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

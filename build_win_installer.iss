// Get version from preprocessor variable (set via /DAPP_VERSION=value) or environment variable
#ifndef APP_VERSION
  #define MyAppVersion GetEnv("APP_VERSION")
  #if MyAppVersion == ""
    #define MyAppVersion "1.0.0"
  #endif
#else
  #define MyAppVersion APP_VERSION
#endif

// Extract numeric version part (strip pre-release suffixes like -rc2, -beta, etc.)
// VersionInfoVersion requires exactly 4 numeric components (X.X.X.X)
// We need to extract just the numeric part (e.g., "1.0.0" from "1.0.0-rc2")
// and convert it to "1.0.0.0" format
// Handle both versions with and without pre-release suffixes
#define DashPos Pos("-", MyAppVersion)
#if DashPos > 0
  // Version has a dash, extract substring before it
  #define MyNumericVersion Copy(MyAppVersion, 1, DashPos - 1)
#else
  // No dash, use full version
  #define MyNumericVersion MyAppVersion
#endif

// Convert 3-component version (X.Y.Z) to 4-component (X.Y.Z.0) for VersionInfoVersion
// This handles both regular versions (1.0.0 -> 1.0.0.0) and pre-release versions (1.0.0-rc2 -> 1.0.0.0)
#define MyAppVersionInfoVersion MyNumericVersion + ".0"

[Setup]
AppName=Sightline
AppVersion={#MyAppVersion}
AppPublisher=Sightline App Contributors
AppPublisherURL=https://github.com/aschepis/sightline
AppSupportURL=https://github.com/aschepis/sightline/issues
AppUpdatesURL=https://github.com/aschepis/sightline/releases
DefaultDirName={autopf}\Sightline
DefaultGroupName=Sightline
OutputDir=Output
OutputBaseFilename=SightlineInstaller
Compression=lzma
SolidCompression=yes
LicenseFile=LICENSE
InfoBeforeFile=
InfoAfterFile=
VersionInfoVersion={#MyAppVersionInfoVersion}
VersionInfoTextVersion={#MyAppVersion}
VersionInfoCompany=Sightline App Contributors
VersionInfoDescription=Powerful tools for face blurring, manual redaction, and audio transcription in a single application.
VersionInfoCopyright=Copyright (C) 2025
VersionInfoProductName=Sightline
VersionInfoProductVersion={#MyAppVersion}

[Files]
Source: "dist\Sightline\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Sightline"; Filename: "{app}\Sightline.exe"
Name: "{group}\Uninstall Sightline"; Filename: "{uninstallexe}"
Name: "{userdesktop}\Sightline"; Filename: "{app}\Sightline.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\Sightline.exe"; Description: "Launch Sightline"; Flags: nowait postinstall skipifsilent

# PowerShell script to create Windows installer using Inno Setup
# Usage: .\scripts\create-windows-installer.ps1 -Version "1.0.0" -AppName "Sightline"

param(
    [string]$Version = "0.0.1",
    [string]$AppName = "Sightline"
)

Write-Host "Creating Windows installer..." -ForegroundColor Cyan

# Set default version if not provided
if ([string]::IsNullOrEmpty($Version)) {
    $Version = "0.0.1"
    Write-Host "Warning: VERSION not set, using default: $Version" -ForegroundColor Yellow
}

Write-Host "Looking for Inno Setup compiler..." -ForegroundColor Cyan

# Find Inno Setup compiler
$ISCCPath = $null

# Check common installation paths
$possiblePaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $ISCCPath = $path
        break
    }
}

# Check if ISCC is in PATH
if ($null -eq $ISCCPath) {
    $isccCmd = Get-Command iscc -ErrorAction SilentlyContinue
    if ($isccCmd) {
        $ISCCPath = $isccCmd.Source
    }
}

if ($null -eq $ISCCPath) {
    Write-Host "Error: Inno Setup compiler (ISCC.exe) not found" -ForegroundColor Red
    Write-Host "Please install Inno Setup or ensure ISCC.exe is in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "  Found ISCC at: $ISCCPath" -ForegroundColor Green
Write-Host "Compiling installer with version: $Version" -ForegroundColor Cyan

# Compile the installer
$issFile = "build_win_installer.iss"
if (-not (Test-Path $issFile)) {
    Write-Host "Error: $issFile not found" -ForegroundColor Red
    exit 1
}

$process = Start-Process -FilePath $ISCCPath -ArgumentList "/DAPP_VERSION=$Version", $issFile -Wait -PassThru -NoNewWindow

if ($process.ExitCode -ne 0) {
    Write-Host "Error: ISCC compilation failed with exit code $($process.ExitCode)" -ForegroundColor Red
    exit 1
}

Write-Host "Renaming installer..." -ForegroundColor Cyan

# Create dist-packages directory if it doesn't exist
$distPackagesDir = "dist-packages"
if (-not (Test-Path $distPackagesDir)) {
    New-Item -ItemType Directory -Path $distPackagesDir | Out-Null
}

# Rename the installer
$outputFile = "Output\SightlineInstaller.exe"
$newFileName = "$distPackagesDir\$AppName-$Version-Windows-Setup.exe"

if (Test-Path $outputFile) {
    Move-Item -Path $outputFile -Destination $newFileName -Force
    Write-Host "Installer created: $newFileName" -ForegroundColor Green
} else {
    Write-Host "Error: $outputFile not found" -ForegroundColor Red
    exit 1
}


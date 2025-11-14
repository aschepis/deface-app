"""PyInstaller spec for Deface GUI application.

This spec is responsible for bundling the GUI *and* the underlying
`deface` CLI so that end-users do not need to install `deface`
separately.
"""

from pathlib import Path
from shutil import which


app_name = "Deface"
bundle_id = "com.defaceapp.deface"
entry_script = "main.py"
icon_file = "icon.png"

block_cipher = None


def _collect_deface_cli() -> list:
    """Return a binaries list entry for the `deface` CLI if available.

    At build time we look up the `deface` executable in the current
    environment (typically the Conda/venv used for building). If found,
    we copy it into the root of the bundled application so the GUI can
    invoke it directly without requiring a system-wide install.
    """
    deface_path = which("deface")
    if not deface_path:
        # Building without deface installed – bundle will still work,
        # but runtime will show a clear error message.
        print("WARNING: `deface` CLI not found on PATH – it will not be bundled.")
        return []

    print(f"Bundling `deface` CLI from: {deface_path}")
    # (source, dest_dir_inside_bundle)
    # We place it next to the main executable (dist/Deface/deface[.exe]).
    return [(deface_path, ".")]


a = Analysis(
    [entry_script],
    pathex=[],
    binaries=_collect_deface_cli(),
    datas=[],
    hiddenimports=["deface"],  # ensure deface Python package is collected
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # GUI mode
)

# REQUIRED → collects libs, binaries, datas into a folder
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    a.zipfiles,
    a.zipped_data,
    strip=False,
    upx=False,
    name=app_name,
)

# macOS .app bundle build
app = BUNDLE(
    coll,
    name=f"{app_name}.app",
    icon=icon_file,
    bundle_identifier=bundle_id,
    info_plist={
        "CFBundleDisplayName": app_name,
        "CFBundleIdentifier": bundle_id,
        "CFBundleName": app_name,
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "LSMinimumSystemVersion": "10.13",
        "NSHighResolutionCapable": True,
    },
)

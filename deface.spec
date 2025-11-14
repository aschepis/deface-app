# deface.spec
app_name = "Deface"
bundle_id = "com.defaceapp.deface"
entry_script = "main.py"
icon_file = "icon.png"

block_cipher = None

a = Analysis(
    [entry_script],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    console=False,    # GUI mode
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

# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/resources/', 'app/resources/'), # Your application resources
        ('app/config.json', 'app/'),          # Configuration file
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PlanetOnDesktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    # --- macOS Specific Modifications ---
    console=False, # For a GUI application, keep this as False.
                   # True would open a terminal window alongside the app.
    # --- General settings (keep as is) ---
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None, # Keep None to auto-detect target architecture
    # --- macOS Code Signing & Entitlements ---
    # These are crucial for distributing apps on macOS, especially for notarization.
    # Replace 'Developer ID Application: Your Company Name (XXXXXXXXXX)' with your actual signing identity.
    # You'll need to have this identity configured in your Keychain Access.
    codesign_identity='Developer ID Application: Your Company Name (XXXXXXXXXX)',
    entitlements_file='path/to/your/entitlements.plist', # Path to your entitlements file (e.g., for network access, app sandboxing)
    # --- macOS Application Bundle Structure ---
    # 'contents_directory' determines the name of the main executable within the .app bundle.
    # By default, PyInstaller puts the executable directly in Contents/MacOS/.
    contents_directory='.', # This generally works fine, don't change unless you have specific needs.
    # --- macOS Icon ---
    # macOS uses .icns files for application icons.
    # You'll need to convert your .ico or .png to .icns format.
    icon=['app/resources/pod.icns'], # Path to your .icns icon file
    version='version_file.txt', # Path to your version file
    # --- UAC (Windows-specific, irrelevant for macOS) ---
    uac_admin=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PlanetOnDesktop',
)
app = BUNDLE(
    coll,
    name='PlanetOnDesktop.app', # This creates the .app bundle
    info_plist={ # Info.plist is a crucial configuration file for macOS apps
        'CFBundleName': 'PlanetOnDesktop',
        'CFBundleDisplayName': 'Planet on Desktop',
        'CFBundleIdentifier': 'com.QQT.PlanetOnDesktop', # Use your unique bundle identifier
        'CFBundleVersion': '0.3.0', # Your app version
        'CFBundleShortVersionString': '1.0', # Short public version string
        'NSHumanReadableCopyright': '© 2025 QQT',
        # Add other keys as needed, e.g., LSUIElement for menubar-only apps
        # 'LSUIElement': True, # Uncomment if this is a menubar-only app without a Dock icon
    },
)
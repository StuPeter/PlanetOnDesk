# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/resources/', 'app/resources/'), # 整个目录，保持不变，PyInstaller 会处理斜杠
        ('app/config.json', 'app/'),  # 配置或其他数据文件，保持不变
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
    # --- Ubuntu/Linux 修改点 ---
    console=False, # 如果是 GUI 应用，通常保持为 False。
                   # 如果需要命令行输出调试信息，可以改为 True，但对于桌面应用通常不需要。
    # --- 保持不变 ---
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None, # 通常保持 None，让 PyInstaller 自动检测目标架构
    codesign_identity=None,
    entitlements_file=None,
    contents_directory='.', # 保持不变
    # --- Ubuntu/Linux 图标和版本文件修改点 ---
    # Linux 应用通常不直接将图标嵌入到可执行文件，而是通过 .desktop 文件引用。
    # 但 PyInstaller 仍然可能使用这个图标来生成一些内部结构或作为默认窗口图标。
    # 路径分隔符改为正斜杠 '/'
    icon=['app/resources/pod.png'], # 强烈建议在 Linux 上使用 .png 格式的图标
    version='version_file.txt', # 版本文件路径保持不变
    uac_admin=False, # UAC 是 Windows 特有，在 Linux 上无效
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
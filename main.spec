# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
<<<<<<< HEAD
    [],
    exclude_binaries=True,
=======
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
>>>>>>> a6a789236e07ac92f83d46f9329f46461c804962
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
<<<<<<< HEAD
=======
    upx_exclude=[],
    runtime_tmpdir=None,
>>>>>>> a6a789236e07ac92f83d46f9329f46461c804962
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
<<<<<<< HEAD
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
=======
>>>>>>> a6a789236e07ac92f83d46f9329f46461c804962

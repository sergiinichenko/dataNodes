# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

added_files = [
         ('datanodes/core/qss/nodestyle.qss',      'datanodes/core/qss/'), 
         ('datanodes/core/qss/nodestyle-dark.qss', 'datanodes/core/qss/'),
         ('datanodes/icons/*.png', 'datanodes/icons/')
         ]

a = Analysis(
    ['main.py'],
    pathex=['C:\\Users\\nichenko_s\\Work\\Development\\datanodes'],
    binaries=[],
    datas = added_files,
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
    [],
    name='DataNodes',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    windowed=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='C:/Users/nichenko_s/Work/Development/datanodes/media/datanodes.ico'
)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='DataNodes')
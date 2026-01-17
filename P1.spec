# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['P1.PY'],
    pathex=[],
    binaries=[],
    datas=[('firebase_key.json', '.'), ('logo.png', '.'), ('J K Create Ledger.xlsx', '.'), ('J K Bank Statment format.xlsm', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='P1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['LOGO.ico'],
)

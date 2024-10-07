# -*- mode: python ; coding: utf-8 -*-

import os

base_path = os.path.abspath(os.path.dirname(__file__))

a = Analysis(
    [os.path.join(base_path, '../app/main.py')],
    pathex=[os.path.join(base_path, '../app/core'), os.path.join(base_path, '../app/utilities')],
    binaries=[('/usr/lib/aarch64-linux-gnu/libpython3.11.so', '.')],
    datas=[(os.path.join(base_path, '../app/core/*'), 'core'), (os.path.join(base_path, '../app/utilities/*'), 'utilities')],
    hiddenimports=['picamera2', 'numpy', 'PIL', 'cv2', 'libcamera', 'simplejpeg', 'v4l2'],
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
    [],
    exclude_binaries=True,
    name='raspycam-arm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='raspycam-arm',
)

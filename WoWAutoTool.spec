# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import inspect

block_cipher = None

# Get base path for spec file
SPEC = os.path.abspath(inspect.getfile(inspect.currentframe()))
SPEC_DIR = os.path.dirname(SPEC)

hiddenimports = [
    'cv2',
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    'mss',
    'pydirectinput',
    'PIL',
    'PIL.Image',
    'win32api',
    'win32con',
    'win32ui',
    'win32file',
    'win32timezone',
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.sip',
]

a = Analysis(
    ['main.py'],
    pathex=[SPEC_DIR],
    binaries=[],
    datas=[
        (os.path.join(SPEC_DIR, 'images'), 'images'),
        (os.path.join(SPEC_DIR, 'scripts'), 'scripts'),
        (os.path.join(SPEC_DIR, 'config.json'), '.'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'test',
    ],
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
    exclude_binaries=True,
    name='WoWAutoTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WoWAutoTool',
)

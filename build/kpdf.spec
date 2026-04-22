# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for kPDF Windows EXE.
Build from c:/Users/Klemen/Work/kpdf with:
  pyinstaller build/kpdf.spec --distpath build/dist --workpath build/work
"""

block_cipher = None

from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
src_dir = project_root / "src"
main_script = src_dir / "kpdf" / "main.py"
assets_dir = project_root / "assets"
icon_path = assets_dir / "kpdf_icon.ico"
version_info = project_root / "build" / "version_info.txt"

a = Analysis(
    [str(main_script)],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[
        (str(assets_dir), 'assets'),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "pikepdf",
        "fitz",
        "img2pdf",
        "PIL",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="kpdf",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=str(icon_path),
    version=str(version_info),
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


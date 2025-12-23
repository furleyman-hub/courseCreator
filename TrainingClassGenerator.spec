# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [('app.py', '.'), ('generator', 'generator'), ('notes_ocr.py', '.'), ('heygen_client.py', '.'), ('requirements.txt', '.'), ('C:\\Users\\julia\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\streamlit\\static', 'streamlit/static'), ('C:\\Users\\julia\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\streamlit\\runtime', 'streamlit/runtime')]
datas += copy_metadata('streamlit')
datas += copy_metadata('tqdm')
datas += copy_metadata('requests')
datas += copy_metadata('packaging')
datas += copy_metadata('numpy')


a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['streamlit', 'streamlit.web.cli', 'altair.vegalite.v5', 'notes_ocr', 'heygen_client'],
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
    name='TrainingClassGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

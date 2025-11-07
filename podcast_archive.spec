# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all backend modules
backend_modules = collect_submodules('backend')
streamlit_modules = collect_submodules('streamlit')
nltk_modules = collect_submodules('nltk')

# Collect data files
datas = [
    ('frontend/streamlit_app.py', 'frontend'),
    ('.env.example', '.'),
]

# Collect NLTK data
datas += collect_data_files('nltk')

# Collect Streamlit data
datas += collect_data_files('streamlit')

# Hidden imports
hiddenimports = backend_modules + streamlit_modules + nltk_modules + [
    'sklearn.utils._cython_blas',
    'sklearn.neighbors.typedefs',
    'sklearn.neighbors.quad_tree',
    'sklearn.tree._utils',
    'pydantic',
    'pydantic_core',
    'sqlalchemy.ext.asyncio',
    'aiosqlite',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'click',
    'httpx',
    'h11',
    'watchdog',
    'mutagen',
]

a = Analysis(
    ['podcast_archive_launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PodcastArchive',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for Windows GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)

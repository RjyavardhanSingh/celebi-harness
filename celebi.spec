# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Celebi desktop app

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['celebi/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('api', 'api'),
    ],
    hiddenimports=[
        'celebi',
        'celebi.app',
        'celebi.config',
        'celebi.agents',
        'celebi.model_fetcher',
        'celebi.workers',
        'celebi.ui',
        'celebi.ui.main_window',
        'celebi.ui.setup_wizard',
        'celebi.ui.projects_sidebar',
        'celebi.ui.project_dashboard',
        'celebi.ui.graph_view',
        'celebi.ui.settings_tab',
        'PySide6',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtCharts',
        'kuzu',
        'fastapi',
        'httpx',
        'uvicorn',
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
        'starlette',
        'starlette.responses',
        'pydantic',
        'litellm',
    ],
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
    exclude_binaries=True,
    name='celebi',
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
    name='celebi',
)

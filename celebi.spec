# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Celebi desktop app

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None


def _api_datas():
    """Bundle only the runtime API package.

    The whole api/ tree must NOT be bundled: it contains the dev .venv
    (gigabytes), caches, tests, and a dev kuzu.db. The frozen proxy child
    only needs api/app/** (imported as top-level `app`).
    """
    skip_dirs = {'.venv', '__pycache__', 'tests', '.pytest_cache', '.ruff_cache'}
    skip_files = {'kuzu.db'}
    skip_suffixes = {'.pyc'}
    root = Path('api')
    out = []
    for p in sorted((root / 'app').rglob('*')):
        if not p.is_file():
            continue
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.name in skip_files or p.suffix in skip_suffixes:
            continue
        out.append((str(p), str(Path('api') / p.relative_to(root).parent)))
    return out


# litellm reads pricing/config JSONs at runtime via importlib.resources.
# Subpackages need their own entries (top-level pattern doesn't recurse).
LITELLM_DATAS = (
    collect_data_files('litellm', includes=['*.json'])
    + collect_data_files('litellm.litellm_core_utils.tokenizers', includes=['*.json'])
    + collect_data_files('litellm.proxy.public_endpoints', includes=['*.json'])
)

API_DATAS = _api_datas()

# ---------------------------------------------------------------------------
# LiteLLM uses lazy imports for every provider.  PyInstaller cannot discover
# these through static analysis, so we list the ones we actually support plus
# the core litellm subpackages that are always needed.
# ---------------------------------------------------------------------------
LITELLM_HIDDEN_IMPORTS = [
    # core
    'litellm',
    'litellm.utils',
    'litellm.main',
    'litellm.litellm_core_utils',
    'litellm.litellm_core_utils.core_helpers',
    'litellm.litellm_core_utils.get_provider_info',
    'litellm.litellm_core_utils.logging',
    'litellm.models_response',
    'litellm.types',
    'litellm.types.utils',
    'litellm.types.files',
    'litellm.types.responses',
    'litellm.cost_calculator',
    'litellm.proxy._types',
    'litellm.proxy.proxy_server',
    # imported only via importlib.resources string refs (litellm/utils.py)
    'litellm.litellm_core_utils.tokenizers',
    'litellm.secret_managers.main',
    # providers we actually use (from celebi config / model_fetcher)
    'litellm.llms.openai.openai',
    'litellm.llms.openai.openai_handler',
    'litellm.llms.anthropic.anthropic',
    'litellm.llms.anthropic.anthropic_handler',
    'litellm.llms.gemini.gemini',
    'litellm.llms.gemini.gemini_handler',
    # other providers that litellm auto-discovers at runtime
    'litellm.llms.deepseek.deepseek',
    'litellm.llms.groq.groq',
    'litellm.llms.mistral.mistral',
    'litellm.llms.cohere.cohere',
    'litellm.llms.bedrock.bedrock',
]

# ---------------------------------------------------------------------------
# Exclude heavy provider SDKs we don't use to keep bundle size down.
# Users who need extra providers can rebuild with these removed from the list.
# ---------------------------------------------------------------------------
LITELLM_EXCLUDES = [
    'litellm.llms.vertex',
    'litellm.llms.vertex_httpx',
    'litellm.llms.palm',
    'litellm.llms.azure',
    'litellm.llms.azure_ai',
    'litellm.llms.anthropic.experimental',
    'litellm.llms.text_completion_openai',
    'litellm.llms.cloudflare',
    'litellm.llms.nlp_cloud',
    'litellm.llms.huggingface',
    'litellm.llms.maker',
    'litellm.llms.ai21',
    'litellm.llms.petal',
    'litellm.llms.ollama',
    'litellm.llms.volcengine',
    'litellm.llms.dynamiq',
    'litellm.llms.galileo',
    'litellm.llms.luminary',
    'litellm.llms.predibase',
    'litellm.llms.databricks',
    'litellm.llms.sagemaker',
    'litellm.llms.sagemaker_common',
    'litellm.llms.WatsonX_AI',
    'litellm.llms.clarifai',
    'litellm.llms.vllm',
    'litellm.llms.nvidia_nim',
    'litellm.llms.mirqa',
    'litellm.llms.gradio_title',
]

a = Analysis(
    ['celebi/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        *API_DATAS,
        *LITELLM_DATAS,
    ],
    hiddenimports=[
        # --- celebi ---
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
        # --- PySide6 ---
        'PySide6',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtCharts',
        # --- graph DB ---
        'kuzu',
        # --- FastAPI / uvicorn ---
        'fastapi',
        'fastapi.responses',
        'httpx',
        'uvicorn',
        'uvicorn.config',
        'uvicorn.server',
        'uvicorn.main',
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
        'uvicorn.lifespan.off',
        'starlette',
        'starlette.responses',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.cors',
        'pydantic',
        # --- litellm (comprehensive) ---
        *LITELLM_HIDDEN_IMPORTS,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        *LITELLM_EXCLUDES,
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

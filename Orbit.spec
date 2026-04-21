# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Orbit."""

import os
import sys

block_cipher = None

# Project root
ROOT = os.path.abspath('.')

a = Analysis(
    ['main.py'],
    pathex=[ROOT],
    binaries=[],
    datas=[
        ('Frontend/Data', 'Frontend/Data'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'Backend',
        'Backend.config',
        'Backend.github_fetcher',
        'Backend.hf_fetcher',
        'Backend.reddit_fetcher',
        'Backend.devto_fetcher',
        'Backend.gh_trending_fetcher',
        'Backend.digest_generator',
        'Backend.emailer',
        'Backend.scheduler',
        'Backend.sources',
        'Backend.sources.base',
        'Backend.sources.github_source',
        'Backend.sources.hf_source',
        'Backend.sources.reddit_source',
        'Backend.sources.devto_source',
        'Backend.sources.gh_trending_source',
        'Frontend',
        'Frontend.GUI',
        'groq',
        'github',
        'schedule',
        'mistune',
        'litellm',
        'tenacity',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Orbit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file when available
)

# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[
        'C:\\Windows\\System32',
        'C:\\Windows\\SysWOW64',
        'C:\\ProgramData\\miniconda3\\envs\\mini\\Lib\\site-packages',
    ],
    binaries=[
        # Qt DLLs
        ('C:\\ProgramData\\miniconda3\\envs\\mini\\Lib\\site-packages\\PyQt6\\Qt6\\bin\\*.dll', '.'),
        ('C:\\ProgramData\\miniconda3\\envs\\mini\\Lib\\site-packages\\PyQt6\\Qt6\\plugins\\*', './plugins'),
        
        # Conda 环境 DLLs
        ('C:\\ProgramData\\miniconda3\\envs\\mini\\Library\\bin\\*.dll', '.'),
    ],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'anthropic',
        'openai',
        'python-dotenv',
        'python-pptx',
        'markdown',
        'mutagen',
        'zhipuai'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CourseForgeMini',
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
    icon=['app.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CourseForgeMini',
)

# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 添加 .env 文件到打包资源
        ('.env', '.'),  # 从项目根目录复制到打包目录的根目录
    ],
    hiddenimports=[
        'anthropic',
        'openai',
        'PyQt6',
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
    icon=['images/app.icns'],
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

app = BUNDLE(
    coll,
    name='CourseForgeMini.app',
    icon='images/app.icns',
    bundle_identifier=None,
)

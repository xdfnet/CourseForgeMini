# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'], # 主程序
    pathex=[],  # 路径
    binaries=[], # 二进制文件
    datas=[],    # 数据文件
    hiddenimports=[], # 隐藏导入
    hookspath=[],   # 钩子路径
    hooksconfig={}, # 钩子配置
    runtime_hooks=[], # 运行时钩子
    excludes=[],     # 排除项
    noarchive=False, # 不归档
    optimize=0,      # 优化级别
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,                # 纯Python对象
    a.scripts,          # 脚本
    a.binaries,         # 二进制文件
    a.datas,            # 数据文件
    [],                 # 排除项
    name='CourseForge', # 可执行文件名
    debug=False,        # 调试模式
    bootloader_ignore_signals=False, # 忽略信号
    strip=False,        # 不剥离
    upx=True,           # 使用UPX压缩
    upx_exclude=[],     # 不压缩的文件
    runtime_tmpdir=None, # 运行时临时目录
    console=False,      # 不使用控制台
    disable_windowed_traceback=False, # 禁用窗口化回溯
    argv_emulation=False, # 禁用参数模拟
    target_arch=None,    # 目标架构
    codesign_identity=None, # 代码签名标识
    entitlements_file=None, # 权限文件
    icon=['app.ico'],    # 图标文件
)

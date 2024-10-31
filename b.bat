@echo off
REM 激活 Conda 环境
CALL "C:\opt\miniconda3\Scripts\activate.bat" mini

REM 删除 build 和 dist 目录
echo 删除 build 和 dist 目录...
rmdir /s /q build
rmdir /s /q dist

REM 执行 PyInstaller
echo 执行 PyInstaller...
pyinstaller swin.spec

echo 构建完成！
pause
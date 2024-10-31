#!/bin/bash
source /opt/miniconda3/etc/profile.d/conda.sh

conda activate mini

rm -rf build dist

pyinstaller smac.spec


# 设置目标目录
TARGET_DIR="/Users/apple/Library/CloudStorage/ShellBean/虚拟机88/iCode/CourseForgeMini"

echo "正在复制文件到目标目录..."

# 确保目标目录存在
mkdir -p "$TARGET_DIR"

# 使用 find 命令找到所有文件（不包括目录），并复制
find . -type f -maxdepth 1 -exec cp {} "$TARGET_DIR/" \;

if [ $? -eq 0 ]; then
    echo "文件复制完成!"
else
    echo "文件复制失败!"
    exit 1
fi



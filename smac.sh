#!/bin/bash


echo "开始激活环境..."
source /opt/miniconda3/etc/profile.d/conda.sh
conda activate mini


echo "开始清理..."
rm -rf build dist

echo "开始打包..."
pyinstaller smac.spec



#!/bin/bash

# 检查系统状态
echo "=== 系统信息 ==="
uname -a
echo

echo "=== CPU信息 ==="
cat /proc/cpuinfo | grep "model name" | head -1
echo "CPU核心数: $(nproc)"
echo

echo "=== 内存信息 ==="
free -h
echo

echo "=== 磁盘信息 ==="
df -h
echo

echo "=== Python信息 ==="
python --version
pip --version
echo

echo "=== vnpy信息 ==="
python -c "import vnpy; print(f'vnpy版本: {vnpy.__version__}')"
echo

echo "=== 网络信息 ==="
ip addr | grep inet
echo

echo "=== 进程信息 ==="
ps aux | grep -E 'python|vnpy' | grep -v grep
echo

echo "=== 系统检查完成 ==="

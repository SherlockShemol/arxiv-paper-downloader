#!/bin/bash

# ArXiv AI论文每日下载脚本
# 使用方法: ./daily_download.sh [选项]
# 选项: today, yesterday, week (默认为yesterday)

set -e  # 遇到错误时退出

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查Python脚本是否存在
if [ ! -f "arxiv_downloader.py" ]; then
    echo "错误: 找不到 arxiv_downloader.py 文件"
    exit 1
fi

# 检查Python和依赖
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3 命令"
    exit 1
fi

# 检查requests库
if ! python3 -c "import requests" 2>/dev/null; then
    echo "正在安装依赖 requests..."
    pip3 install requests
fi

# 获取参数，默认为yesterday
OPTION=${1:-yesterday}

echo "=== ArXiv AI论文下载器 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "选项: $OPTION"
echo

case $OPTION in
    "today")
        echo "下载今天的AI论文..."
        python3 arxiv_downloader.py --today --max-results 20
        ;;
    "yesterday")
        echo "下载昨天的AI论文..."
        python3 arxiv_downloader.py --yesterday --max-results 20
        ;;
    "week")
        echo "下载最近一周的AI论文..."
        python3 arxiv_downloader.py --last-week --max-results 50
        ;;
    *)
        echo "使用方法: $0 [today|yesterday|week]"
        echo "默认选项: yesterday"
        exit 1
        ;;
esac

echo
echo "下载完成！"
echo "文件位置: /Users/shemol/Downloads/arvix_paper"
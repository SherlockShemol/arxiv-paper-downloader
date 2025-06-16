#!/bin/bash

# ArXiv AI Papers Daily Download Script
# Usage: ./daily_download.sh [option]
# Options: today, yesterday, week (default: yesterday)

set -e  # Exit on error

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python script exists
if [ ! -f "arxiv_downloader.py" ]; then
    echo "Error: arxiv_downloader.py file not found"
    exit 1
fi

# Check Python and dependencies
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 command not found"
    exit 1
fi

# Check requests library
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing dependency requests..."
    pip3 install requests
fi

# Get parameter, default to yesterday
OPTION=${1:-yesterday}

echo "=== ArXiv AI Paper Downloader ==="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Option: $OPTION"
echo

# Execute different download tasks based on option
case $OPTION in
    "today")
        echo "Downloading today's AI papers..."
        python3 arxiv_downloader.py --query "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV" --date-from "$(date '+%Y-%m-%d')" --max-results 50
        ;;
    "yesterday")
        echo "Downloading yesterday's AI papers..."
        python3 arxiv_downloader.py --query "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV" --date-from "$(date -d 'yesterday' '+%Y-%m-%d')" --date-to "$(date -d 'yesterday' '+%Y-%m-%d')" --max-results 100
        ;;
    "week")
        echo "Downloading AI papers from the past week..."
        python3 arxiv_downloader.py --query "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV" --date-from "$(date -d '7 days ago' '+%Y-%m-%d')" --max-results 200
        ;;
    *)
        echo "Usage: $0 [today|yesterday|week]"
        echo "Default option: yesterday"
        exit 1
        ;;
esac

echo
echo "Download completed!"
echo "File location: ./arxiv_papers"
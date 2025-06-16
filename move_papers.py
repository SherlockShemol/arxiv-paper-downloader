#!/usr/bin/env python3
"""
Script to move papers downloaded by arxiv MCP server to specified directory
"""

import os
import shutil
from pathlib import Path
import glob

def move_papers_to_directory():
    """Find and move downloaded papers to target directory"""
    
    # Target directory
    target_dir = Path('./arxiv_papers')
    
    # Possible source directories (MCP server usually stores files in these locations)
    possible_source_dirs = [
        Path.home() / "Downloads",
        Path.cwd(),
        Path.home() / ".cache" / "arxiv",
        Path.home() / "Documents",
        Path("/tmp"),
        Path("/var/tmp"),
        Path.home() / "Library" / "Caches" / "arxiv",
    ]
    
    # Paper ID list
    paper_ids = [
        "2412.14619",
        "2412.14593",
        "2412.14588",
        "2412.14578",
        "2412.14577",
        "2412.14576",
        "2412.14575",
        "2412.14574",
        "2412.14573",
        "2412.14572",
        "2412.14571",
        "2412.14570",
        "2412.14569",
        "2412.14568",
        "2412.14567"
    ]
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Searching and moving papers to: {target_dir}")
    
    moved_count = 0
    # Search each possible source directory
    for source_dir in possible_source_dirs:
        if not source_dir.exists():
            continue
            
        print(f"\nSearching directory: {source_dir}")
        
        # Find PDF files
        for paper_id in paper_ids:
            # Try different filename patterns
            patterns = [
                f"{paper_id}.pdf",
                f"{paper_id}v*.pdf",
                f"*{paper_id}*.pdf",
                f"{paper_id}_*.pdf",
                f"arxiv_{paper_id}.pdf",
                f"paper_{paper_id}.pdf"
            ]
            
            files = []
            for pattern in patterns:
                files.extend(source_dir.glob(pattern))
            
            for file_path in files:
                if file_path.is_file():
                    filename = file_path.name
                    target_path = target_dir / filename
                    
                    try:
                        if not target_path.exists():
                            shutil.move(str(file_path), str(target_path))
                            moved_count += 1
                            print(f"✓ Moved: {filename}")
                        else:
                            print(f"○ Already exists: {filename}")
                    except Exception as e:
                        print(f"✗ Failed to move {filename}: {e}")
                        
                if files:  # Break out of pattern loop if files found
                    break
    
    # Also try searching for PDF files directly from current working directory
    print("\nSearching current directory for PDF files...")
    for pdf_file in Path.cwd().glob("*.pdf"):
        if pdf_file.is_file():
            target_path = target_dir / pdf_file.name
            try:
                if not target_path.exists():
                    shutil.move(str(pdf_file), str(target_path))
                    moved_count += 1
                    print(f"✓ Moved: {pdf_file}")
            except Exception as e:
                print(f"✗ Failed to move {pdf_file}: {e}")
    
    print(f"\nTotal moved {moved_count} files to {target_dir}")
    
    # List contents of target directory
    files_in_target = list(target_dir.glob("*.pdf"))
    
    if files_in_target:
        print(f"\nCurrent files in target directory:")
        for file_path in sorted(files_in_target):
            print(f"  - {file_path.name}")
    else:
        print(f"\nTarget directory is empty")

if __name__ == "__main__":
    move_papers_to_directory()
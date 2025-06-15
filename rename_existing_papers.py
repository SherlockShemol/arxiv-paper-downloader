#!/usr/bin/env python3
"""
Batch rename existing paper files
Change filename from paper ID-based to paper title-based
"""

import os
import re
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import time

class PaperRenamer:
    def __init__(self, download_dir="~/Downloads/arxiv_papers"):
        self.download_dir = Path(download_dir)
        self.base_url = "http://export.arxiv.org/api/query"
    
    def sanitize_filename(self, title):
        """
        Clean filename, remove or replace illegal characters
        """
        # Remove or replace illegal filename characters
        title = re.sub(r'[<>:"/\\|?*]', '', title)
        # Replace multiple spaces with single space
        title = re.sub(r'\s+', ' ', title)
        # Remove leading and trailing spaces
        title = title.strip()
        # Limit filename length (avoid too long)
        if len(title) > 100:
            title = title[:100]
        # If title is empty, use paper ID
        if not title:
            title = "Unknown_Title"
        return title
    
    def get_paper_info(self, paper_id):
        """
        Get paper information from ArXiv API
        """
        # Remove version number (if exists)
        clean_id = paper_id.replace('v1', '').replace('v2', '').replace('v3', '').replace('v4', '').replace('v5', '')
        
        params = {
            'id_list': clean_id,
            'max_results': 1
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.text)
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            entry = root.find('atom:entry', namespaces)
            if entry is not None:
                title_elem = entry.find('atom:title', namespaces)
                if title_elem is not None:
                    return title_elem.text.strip().replace('\n', ' ')
            
        except Exception as e:
            print(f"Failed to get paper {paper_id} information: {e}")
        
        return None
    
    def rename_files(self):
        """
        Rename all paper files in the directory
        """
        if not self.download_dir.exists():
            print(f"Directory does not exist: {self.download_dir}")
            return
        
        # Find all PDF files
        pdf_files = list(self.download_dir.glob('*.pdf'))
        
        # Filter files named with paper ID (format: number.numberv number.pdf)
        id_pattern = re.compile(r'^\d{4}\.\d{5}v\d+\.pdf$')
        id_files = [f for f in pdf_files if id_pattern.match(f.name)]
        
        if not id_files:
            print("No files found that need renaming")
            return
        
        print(f"Found {len(id_files)} files that need renaming")
        
        renamed_count = 0
        for pdf_file in id_files:
            paper_id = pdf_file.stem  # Remove .pdf extension
            print(f"\nProcessing: {pdf_file.name}")
            
            # Get paper title
            title = self.get_paper_info(paper_id)
            if not title:
                print(f"  Skipped: Unable to get paper title")
                continue
            
            # Clean title as filename
            clean_title = self.sanitize_filename(title)
            new_filename = f"{clean_title}.pdf"
            new_filepath = self.download_dir / new_filename
            
            # If new filename already exists, add ID suffix
            if new_filepath.exists() and new_filepath != pdf_file:
                new_filename = f"{clean_title}_{paper_id}.pdf"
                new_filepath = self.download_dir / new_filename
            
            # Rename file
            try:
                pdf_file.rename(new_filepath)
                print(f"  ✓ Renamed to: {new_filename}")
                renamed_count += 1
                
                # Also rename corresponding MD file (if exists)
                md_file = pdf_file.with_suffix('.md')
                if md_file.exists():
                    new_md_filepath = new_filepath.with_suffix('.md')
                    md_file.rename(new_md_filepath)
                    print(f"  ✓ Also renamed MD file")
                
            except Exception as e:
                print(f"  ✗ Rename failed: {e}")
            
            # Add delay to avoid too frequent API requests
            time.sleep(1)
        
        print(f"\nRename completed! Successfully renamed {renamed_count}/{len(id_files)} files")

def main():
    renamer = PaperRenamer()
    renamer.rename_files()

if __name__ == "__main__":
    main()
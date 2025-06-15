#!/usr/bin/env python3
"""
批量重命名现有论文文件
将基于论文ID的文件名改为基于论文标题的文件名
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
        清理文件名，移除或替换不合法的字符
        """
        # 移除或替换不合法的文件名字符
        title = re.sub(r'[<>:"/\\|?*]', '', title)
        # 替换多个空格为单个空格
        title = re.sub(r'\s+', ' ', title)
        # 移除首尾空格
        title = title.strip()
        # 限制文件名长度（避免过长）
        if len(title) > 100:
            title = title[:100]
        # 如果标题为空，使用论文ID
        if not title:
            title = "Unknown_Title"
        return title
    
    def get_paper_info(self, paper_id):
        """
        从ArXiv API获取论文信息
        """
        # 移除版本号（如果存在）
        clean_id = paper_id.replace('v1', '').replace('v2', '').replace('v3', '').replace('v4', '').replace('v5', '')
        
        params = {
            'id_list': clean_id,
            'max_results': 1
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # 解析XML响应
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
            print(f"获取论文 {paper_id} 信息失败: {e}")
        
        return None
    
    def rename_files(self):
        """
        重命名目录中的所有论文文件
        """
        if not self.download_dir.exists():
            print(f"目录不存在: {self.download_dir}")
            return
        
        # 查找所有PDF文件
        pdf_files = list(self.download_dir.glob('*.pdf'))
        
        # 过滤出以论文ID命名的文件（格式：数字.数字v数字.pdf）
        id_pattern = re.compile(r'^\d{4}\.\d{5}v\d+\.pdf$')
        id_files = [f for f in pdf_files if id_pattern.match(f.name)]
        
        if not id_files:
            print("没有找到需要重命名的文件")
            return
        
        print(f"找到 {len(id_files)} 个需要重命名的文件")
        
        renamed_count = 0
        for pdf_file in id_files:
            paper_id = pdf_file.stem  # 移除.pdf扩展名
            print(f"\n处理: {pdf_file.name}")
            
            # 获取论文标题
            title = self.get_paper_info(paper_id)
            if not title:
                print(f"  跳过: 无法获取论文标题")
                continue
            
            # 清理标题作为文件名
            clean_title = self.sanitize_filename(title)
            new_filename = f"{clean_title}.pdf"
            new_filepath = self.download_dir / new_filename
            
            # 如果新文件名已存在，添加ID后缀
            if new_filepath.exists() and new_filepath != pdf_file:
                new_filename = f"{clean_title}_{paper_id}.pdf"
                new_filepath = self.download_dir / new_filename
            
            # 重命名文件
            try:
                pdf_file.rename(new_filepath)
                print(f"  ✓ 重命名为: {new_filename}")
                renamed_count += 1
                
                # 同时重命名对应的MD文件（如果存在）
                md_file = pdf_file.with_suffix('.md')
                if md_file.exists():
                    new_md_filepath = new_filepath.with_suffix('.md')
                    md_file.rename(new_md_filepath)
                    print(f"  ✓ 同时重命名MD文件")
                
            except Exception as e:
                print(f"  ✗ 重命名失败: {e}")
            
            # 添加延迟避免API请求过于频繁
            time.sleep(1)
        
        print(f"\n重命名完成！成功重命名 {renamed_count}/{len(id_files)} 个文件")

def main():
    renamer = PaperRenamer()
    renamer.rename_files()

if __name__ == "__main__":
    main()
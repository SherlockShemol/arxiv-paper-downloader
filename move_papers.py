#!/usr/bin/env python3
"""
将arxiv MCP服务器下载的论文移动到指定目录的脚本
"""

import os
import shutil
import glob
from pathlib import Path

def find_and_move_papers():
    """查找并移动下载的论文到目标目录"""
    
    # 目标目录
    target_dir = "/Users/shemol/Downloads/arvix_paper"
    
    # 可能的源目录（MCP服务器通常将文件存储在这些位置）
    possible_source_dirs = [
        os.path.expanduser("~/.mcp/arxiv"),
        os.path.expanduser("~/.local/share/mcp/arxiv"),
        "/tmp/arxiv",
        os.path.expanduser("~/Downloads"),
        os.getcwd()
    ]
    
    # 论文ID列表
    paper_ids = [
        "2506.10982v1",
        "2506.10978v1", 
        "2506.10974v1",
        "2506.10973v1",
        "2506.10972v1",
        "2506.10967v1",
        "2506.10962v1",
        "2506.10960v1",
        "2506.10959v1",
        "2506.10955v1"
    ]
    
    moved_count = 0
    
    print(f"正在查找并移动论文到: {target_dir}")
    
    # 搜索每个可能的源目录
    for source_dir in possible_source_dirs:
        if not os.path.exists(source_dir):
            continue
            
        print(f"\n搜索目录: {source_dir}")
        
        # 查找PDF文件
        for paper_id in paper_ids:
            # 尝试不同的文件名模式
            patterns = [
                f"{paper_id}.pdf",
                f"*{paper_id}*.pdf",
                f"{paper_id.replace('v1', '')}.pdf"
            ]
            
            for pattern in patterns:
                search_pattern = os.path.join(source_dir, "**", pattern)
                files = glob.glob(search_pattern, recursive=True)
                
                for file_path in files:
                    if os.path.isfile(file_path):
                        filename = os.path.basename(file_path)
                        target_path = os.path.join(target_dir, filename)
                        
                        try:
                            shutil.copy2(file_path, target_path)
                            print(f"✓ 已移动: {filename}")
                            moved_count += 1
                            break
                        except Exception as e:
                            print(f"✗ 移动失败 {filename}: {e}")
                            
                if files:  # 如果找到文件就跳出pattern循环
                    break
    
    # 也尝试直接从当前工作目录查找
    print("\n搜索当前目录的PDF文件...")
    pdf_files = glob.glob("*.pdf")
    for pdf_file in pdf_files:
        target_path = os.path.join(target_dir, pdf_file)
        try:
            shutil.copy2(pdf_file, target_path)
            print(f"✓ 已移动: {pdf_file}")
            moved_count += 1
        except Exception as e:
            print(f"✗ 移动失败 {pdf_file}: {e}")
    
    print(f"\n总共移动了 {moved_count} 个文件到 {target_dir}")
    
    # 列出目标目录的内容
    if os.path.exists(target_dir):
        files_in_target = os.listdir(target_dir)
        if files_in_target:
            print(f"\n目标目录现有文件:")
            for f in files_in_target:
                print(f"  - {f}")
        else:
            print(f"\n目标目录为空")

if __name__ == "__main__":
    find_and_move_papers()
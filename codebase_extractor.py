#!/usr/bin/env python3
"""
Codebase Extractor - A tool to extract and combine code from an entire codebase
"""

import os
import sys
import argparse
import fnmatch
import time
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional

# Try to import tqdm for progress bars, handle if not installed
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Default exclusions (common binary files, hidden files, etc.)
DEFAULT_EXCLUSIONS = [
    '*.pyc', '*.pyo', '*.so', '*.o', '*.a', '*.dll', '*.lib', '*.dylib',
    '*.exe', '*.bin', '*.pkl', '*.dat', '*.db', '*.sqlite', '*.sqlite3',
    '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.svg', '*.ico',
    '*.mp3', '*.mp4', '*.wav', '*.flac', '*.ogg', '*.avi', '*.mov',
    '*.zip', '*.tar', '*.gz', '*.bz2', '*.xz', '*.rar', '*.7z',
    '*.pdf', '*.doc', '*.docx', '*.ppt', '*.pptx', '*.xls', '*.xlsx',
    '.git/', '.svn/', '.hg/', '.idea/', '.vscode/', '__pycache__/', 'node_modules/',
    'venv/', 'env/', '.env/', '.venv/', 'build/', 'dist/', 'site-packages/',
    '.DS_Store', 'Thumbs.db'
]


def count_tokens(text: str) -> int:
    """
    Count tokens in a string using a simple whitespace-based approach.
    For a more accurate count, you might want to use a proper tokenizer.
    """
    # Simple tokenization by splitting on whitespace
    return len(text.split())


def generate_tree(root_dir: str, exclusions: List[str], prefix: str = "") -> str:
    """
    Generate an ASCII tree representation of the directory structure.
    """
    if not os.path.isdir(root_dir):
        return ""
    
    tree = []
    items = sorted(os.listdir(root_dir))
    items = [item for item in items if not should_exclude(os.path.join(root_dir, item), exclusions)]
    
    for i, item in enumerate(items):
        path = os.path.join(root_dir, item)
        is_last = i == len(items) - 1
        
        # Current item
        current_prefix = "└── " if is_last else "├── "
        tree.append(f"{prefix}{current_prefix}{item}")
        
        # Recursively process directories
        if os.path.isdir(path):
            next_prefix = prefix + ("    " if is_last else "│   ")
            subtree = generate_tree(path, exclusions, next_prefix)
            if subtree:
                tree.append(subtree)
    
    return "\n".join(tree)


def should_exclude(path: str, exclusions: List[str]) -> bool:
    """
    Check if a path should be excluded based on exclusion patterns.
    """
    path_norm = path.replace("\\", "/")  # Normalize path separators
    
    # Get the relative path and basename
    rel_path = os.path.basename(path)
    
    # Check if any pattern matches
    for pattern in exclusions:
        # Check for directory patterns (patterns ending with '/')
        if pattern.endswith('/'):
            dir_pattern = pattern[:-1]
            if os.path.isdir(path) and (rel_path == dir_pattern or fnmatch.fnmatch(rel_path, dir_pattern)):
                return True
        # Check for regular patterns
        elif fnmatch.fnmatch(rel_path, pattern):
            return True
        # Check if the pattern matches a path component
        elif f"/{pattern}/" in f"/{path_norm}/":
            return True
    
    return False


def is_binary_file(path: str) -> bool:
    """
    Check if a file is binary by reading the first few bytes.
    """
    try:
        with open(path, 'tr', encoding='utf-8') as f:
            f.read(4096)
        return False
    except UnicodeDecodeError:
        return True
    except Exception:
        return True


def read_file(path: str) -> str:
    """
    Read a file with error handling for different encodings.
    """
    # Skip if file is too large (adjust threshold as needed)
    file_size = os.path.getsize(path)
    if file_size > 10 * 1024 * 1024:  # 10 MB
        return f"[File too large: {file_size/1024/1024:.2f} MB]"
    
    # Check if binary
    if is_binary_file(path):
        return "[Binary file not shown]"
    
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'windows-1252', 'ascii']
    
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return f"[Error reading file: {str(e)}]"
    
    return "[File encoding not supported]"


def process_codebase(root_dir: str, output_file: str, exclusions: List[str], show_progress: bool = True) -> None:
    """
    Process the codebase and write the output file.
    """
    if not os.path.exists(root_dir):
        print(f"❌ Error: Root directory '{root_dir}' does not exist.")
        return
    
    # Get absolute path
    root_dir = os.path.abspath(root_dir)
    
    # Collect all files
    all_files = []
    total_size = 0
    
    print(f"📊 Scanning directory: {root_dir}")
    start_time = time.time()
    
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to exclude directories
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclusions)]
        
        for file in files:
            file_path = os.path.join(root, file)
            if not should_exclude(file_path, exclusions):
                all_files.append(file_path)
                total_size += os.path.getsize(file_path)
    
    scan_time = time.time() - start_time
    print(f"📝 Found {len(all_files)} files to process (total size: {total_size/1024/1024:.2f} MB) in {scan_time:.2f}s")
    
    # Generate tree
    print(f"🌳 Generating directory tree...")
    tree_start = time.time()
    tree = generate_tree(root_dir, exclusions)
    tree_time = time.time() - tree_start
    print(f"🌳 Directory tree generated in {tree_time:.2f}s")
    
    # Process files
    print(f"🔄 Processing files...")
    process_start = time.time()
    
    all_content = ""
    total_tokens = 0
    
    # Setup progress bar
    if TQDM_AVAILABLE and show_progress:
        pbar = tqdm(all_files, unit="file")
    else:
        pbar = all_files
        print(f"⚙️ Progress: 0/{len(all_files)} files processed", end="\r")
        progress_count = 0
    
    for file_path in pbar:
        if TQDM_AVAILABLE and show_progress:
            pbar.set_description(f"Processing {os.path.basename(file_path)}")
        elif show_progress and len(all_files) > 0:
            progress_count += 1
            percent = (progress_count / len(all_files)) * 100
            print(f"⚙️ Progress: {progress_count}/{len(all_files)} files processed ({percent:.1f}%)", end="\r")
        
        # Get relative path
        rel_path = os.path.relpath(file_path, root_dir)
        
        # Read file
        content = read_file(file_path)
        
        # Count tokens
        file_tokens = count_tokens(content)
        total_tokens += file_tokens
        
        # Add to all content
        file_header = f"\n\n{'='*80}\n{rel_path}\n{'='*80}\n"
        all_content += file_header + content
    
    if not TQDM_AVAILABLE and show_progress:
        print()  # New line after progress
    
    process_time = time.time() - process_start
    print(f"🔄 Files processed in {process_time:.2f}s")
    
    # Write output file
    print(f"💾 Writing output to: {output_file}")
    write_start = time.time()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write token count
        f.write(f"Total Tokens: {total_tokens}\n\n")
        
        # Write file tree
        f.write(f"Directory Structure:\n\n{tree}\n\n")
        
        # Write list of files
        f.write("Files Included:\n\n")
        for file_path in all_files:
            rel_path = os.path.relpath(file_path, root_dir)
            f.write(f"- {rel_path}\n")
        
        # Write all content
        f.write(all_content)
    
    write_time = time.time() - write_start
    total_time = time.time() - start_time
    
    print(f"💾 Output file written in {write_time:.2f}s")
    print(f"✅ Extraction complete! Total tokens: {total_tokens}")
    print(f"⏱️ Total time: {total_time:.2f}s")


def main():
    """
    Main function to parse arguments and process the codebase.
    """
    # ASCII art banner
    banner = """
 ██████╗ ██████╗ ██████╗ ███████╗██████╗  █████╗ ███████╗███████╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝
██║     ██║   ██║██║  ██║█████╗  ██████╔╝███████║███████╗█████╗  
██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗██╔══██║╚════██║██╔══╝  
╚██████╗╚██████╔╝██████╔╝███████╗██████╔╝██║  ██║███████║███████╗
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝
                                                                  
███████╗██╗  ██╗████████╗██████╗  █████╗  ██████╗████████╗ ██████╗ ██████╗ 
██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗
█████╗   ╚███╔╝    ██║   ██████╔╝███████║██║        ██║   ██║   ██║██████╔╝
██╔══╝   ██╔██╗    ██║   ██╔══██╗██╔══██║██║        ██║   ██║   ██║██╔══██╗
███████╗██╔╝ ██╗   ██║   ██║  ██║██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║
╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
"""
    print(banner)
    
    # Argument parsing
    parser = argparse.ArgumentParser(description="Extract code from an entire codebase into a single file")
    parser.add_argument("--root", "-r", dest="root_dir", default=".",
                        help="Root directory to start extraction (default: current directory)")
    parser.add_argument("--output", "-o", dest="output_file", default="codebase_extract.txt",
                        help="Output file name (default: codebase_extract.txt)")
    parser.add_argument("--exclude", "-e", dest="exclusions", action="append", default=None,
                        help="Exclude patterns (can be used multiple times)")
    parser.add_argument("--no-defaults", dest="no_defaults", action="store_true",
                        help="Don't use default exclusions")
    parser.add_argument("--no-progress", dest="no_progress", action="store_true",
                        help="Don't show progress bar")
    
    args = parser.parse_args()
    
    # Process exclusions
    exclusions = []
    if not args.no_defaults:
        exclusions.extend(DEFAULT_EXCLUSIONS)
    if args.exclusions:
        exclusions.extend(args.exclusions)
    
    # Process the codebase
    process_codebase(args.root_dir, args.output_file, exclusions, not args.no_progress)


if __name__ == "__main__":
    main()
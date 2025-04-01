#!/usr/bin/env python3

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


def should_include_content(path: str, root_dir: str, include_patterns: List[str]) -> bool:
    """
    Check if a file's content should be included based on inclusion patterns.
    When no include patterns are specified, all files are included.
    
    Supports:
    - Individual files by name or path
    - Wildcards for matching multiple files
    - Directory paths to include all files within a directory and its subdirectories
    """
    if not include_patterns:
        return True
    
    # Get relative path to match against patterns
    rel_path = os.path.relpath(path, root_dir)
    rel_path_norm = rel_path.replace("\\", "/")  # Normalize path separators
    
    for pattern in include_patterns:
        # Check for directory pattern (ending with '/')
        if pattern.endswith('/'):
            # Check if file is inside this directory or any of its subdirectories
            dir_path = pattern
            if rel_path_norm.startswith(dir_path) or rel_path.startswith(dir_path):
                return True
        # Check if pattern doesn't end with '/' but is a directory
        elif not pattern.endswith('/') and os.path.isdir(os.path.join(root_dir, pattern)):
            # Ensure pattern has trailing slash for proper directory matching
            dir_path = pattern if pattern.endswith('/') else pattern + '/'
            if rel_path_norm.startswith(dir_path) or rel_path.startswith(dir_path):
                return True
        # Regular file patterns with wildcards
        elif fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(rel_path_norm, pattern):
            return True
        # Exact file match
        elif rel_path == pattern or rel_path_norm == pattern:
            return True
        # Basename match
        elif os.path.basename(rel_path) == pattern:
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


def normalize_include_patterns(patterns: List[str], root_dir: str) -> List[str]:
    """
    Normalize inclusion patterns to handle directories consistently.
    
    For directory patterns:
    - Ensure they end with a trailing slash
    - If a pattern is a valid directory but doesn't end with '/', add the trailing '/'
    """
    normalized = []
    
    for pattern in patterns:
        # Check if the pattern is a directory path
        pattern_path = os.path.join(root_dir, pattern)
        
        if os.path.isdir(pattern_path):
            # Ensure directory patterns end with a trailing slash
            if not pattern.endswith('/'):
                pattern = pattern + '/'
        
        normalized.append(pattern)
    
    return normalized


def process_codebase(
    root_dir: str, 
    output_file: str, 
    exclusions: List[str], 
    include_patterns: List[str] = None,
    show_progress: bool = True, 
    overwrite: bool = False
) -> None:
    """
    Process the codebase and write the output file.
    """
    if not os.path.exists(root_dir):
        print(f"❌ Error: Root directory '{root_dir}' does not exist.")
        return
    
    # Get absolute path
    root_dir = os.path.abspath(root_dir)
    output_file_abs = os.path.abspath(output_file)
    
    # Check if output file already exists
    if os.path.exists(output_file_abs) and not overwrite:
        print(f"⚠️ Warning: Output file '{output_file}' already exists.")
        response = input("Do you want to overwrite it? [y/N]: ").strip().lower()
        if response != 'y' and response != 'yes':
            print("❌ Operation cancelled.")
            return
    
    # Always exclude the output file from being processed
    output_file_name = os.path.basename(output_file_abs)
    if output_file_name not in exclusions:
        exclusions.append(output_file_name)
    
    # Normalize include patterns to handle directories consistently
    if include_patterns:
        include_patterns = normalize_include_patterns(include_patterns, root_dir)
    
    # Collect all files
    all_files = []
    included_files = []
    total_size = 0
    included_size = 0
    
    print(f"📊 Scanning directory: {root_dir}")
    start_time = time.time()
    
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to exclude directories
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclusions)]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip the output file itself
            if os.path.abspath(file_path) == output_file_abs:
                continue
                
            if not should_exclude(file_path, exclusions):
                all_files.append(file_path)
                total_size += os.path.getsize(file_path)
                
                # Check if we should include this file's content
                if should_include_content(file_path, root_dir, include_patterns):
                    included_files.append(file_path)
                    included_size += os.path.getsize(file_path)
    
    scan_time = time.time() - start_time
    
    # Report on all found files and those selected for content inclusion
    if include_patterns:
        print(f"📝 Found {len(all_files)} total files (total size: {total_size/1024/1024:.2f} MB)")
        print(f"📑 Selected {len(included_files)} files for content inclusion (size: {included_size/1024/1024:.2f} MB)")
        if len(included_files) == 0:
            print(f"⚠️ Warning: No files matched the inclusion patterns: {include_patterns}")
            choice = input("Continue with just directory structure? [y/N]: ").strip().lower()
            if choice != 'y' and choice != 'yes':
                print("❌ Operation cancelled.")
                return
    else:
        print(f"📝 Found {len(all_files)} files to process (total size: {total_size/1024/1024:.2f} MB)")
    
    print(f"⏱️ Scan completed in {scan_time:.2f}s")
    
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
    
    # Determine which files to process for content
    files_to_process = included_files if include_patterns else all_files
    
    # Setup progress bar
    if TQDM_AVAILABLE and show_progress:
        pbar = tqdm(files_to_process, unit="file")
    else:
        pbar = files_to_process
        print(f"⚙️ Progress: 0/{len(files_to_process)} files processed", end="\r")
        progress_count = 0
    
    for file_path in pbar:
        if TQDM_AVAILABLE and show_progress:
            pbar.set_description(f"Processing {os.path.basename(file_path)}")
        elif show_progress and len(files_to_process) > 0:
            progress_count += 1
            percent = (progress_count / len(files_to_process)) * 100
            print(f"⚙️ Progress: {progress_count}/{len(files_to_process)} files processed ({percent:.1f}%)", end="\r")
        
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
        
        # Note about selective inclusion if applicable
        if include_patterns:
            f.write(f"Note: Only selected files are included with content. Inclusion patterns: {', '.join(include_patterns)}\n\n")
        
        # Write file tree
        f.write(f"Directory Structure:\n\n{tree}\n\n")
        
        # Write list of all files
        f.write("All Files (Structure Only):\n\n")
        for file_path in all_files:
            rel_path = os.path.relpath(file_path, root_dir)
            f.write(f"- {rel_path}\n")
        
        # If selective inclusion, write list of included files
        if include_patterns:
            f.write("\nFiles With Content Included:\n\n")
            for file_path in included_files:
                rel_path = os.path.relpath(file_path, root_dir)
                f.write(f"- {rel_path}\n")
        
        # Write all content
        f.write(all_content)
    
    write_time = time.time() - write_start
    total_time = time.time() - start_time
    
    print(f"💾 Output file written in {write_time:.2f}s")
    print(f"✅ Extraction complete! Total tokens: {total_tokens}")
    print(f"⏱️ Total time: {total_time:.2f}s")


def parse_include_patterns(patterns_arg: str) -> List[str]:
    """
    Parse include patterns from command line argument.
    Supports both comma-separated and space-separated formats.
    """
    if not patterns_arg:
        return []
    
    # First try comma-separation
    patterns = [p.strip() for p in patterns_arg.split(',')]
    
    # If only one pattern was found, try space-separation
    if len(patterns) == 1:
        patterns = [p.strip() for p in patterns_arg.split()]
    
    # Filter out empty patterns
    return [p for p in patterns if p]


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
    parser.add_argument("--include", "-i", dest="include", default=None,
                        help="Only include content for these files or directories (space or comma separated)")
    parser.add_argument("--no-defaults", dest="no_defaults", action="store_true",
                        help="Don't use default exclusions")
    parser.add_argument("--no-progress", dest="no_progress", action="store_true",
                        help="Don't show progress bar")
    parser.add_argument("--force", "-f", dest="force", action="store_true",
                        help="Force overwrite if output file exists")
    
    args = parser.parse_args()
    
    # Process exclusions
    exclusions = []
    if not args.no_defaults:
        exclusions.extend(DEFAULT_EXCLUSIONS)
    if args.exclusions:
        exclusions.extend(args.exclusions)
    
    # Process inclusion patterns
    include_patterns = parse_include_patterns(args.include) if args.include else None
    
    # Process the codebase
    process_codebase(
        args.root_dir, 
        args.output_file, 
        exclusions,
        include_patterns, 
        not args.no_progress, 
        args.force
    )


if __name__ == "__main__":
    main()
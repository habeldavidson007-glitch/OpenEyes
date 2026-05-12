#!/usr/bin/env python3
"""
File Organization Utility - Moves files to their proper locations
Cleans up root directory by organizing scattered files
"""

import os
import shutil
from pathlib import Path

WORKSPACE = Path('/workspace')

# Define file categories and their destination directories
FILE_ORGANIZATION = {
    # Root files that should stay
    'root_keep': ['.gitignore', 'LICENSE', 'README.md', 'pyproject.toml', 'requirements.txt', 'setup.py'],
    
    # Python test files -> scripts/test_scripts/
    'test_scripts': ['test_suite_50.py'],
    
    # JSON result files -> test_results/
    'test_results': [],  # Will dynamically find .json files
    
    # Markdown docs -> docs/
    'docs': [],  # Will dynamically find .md files (except README)
    
    # Logs -> logs/
    'logs': [],  # Will dynamically find .log files
}

def organize_files():
    """Move files from root to their proper locations."""
    
    print("=" * 60)
    print("FILE ORGANIZER - Cleaning up root directory")
    print("=" * 60)
    
    # Get all files in root (not directories)
    root_files = [f for f in WORKSPACE.iterdir() if f.is_file()]
    
    moved_count = 0
    deleted_count = 0
    kept_count = 0
    
    for file_path in root_files:
        file_name = file_path.name
        
        # Skip hidden files and essential root files
        if file_name.startswith('.'):
            kept_count += 1
            print(f"  ✓ Keeping: {file_name}")
            continue
            
        if file_name in FILE_ORGANIZATION['root_keep']:
            kept_count += 1
            print(f"  ✓ Keeping: {file_name}")
            continue
        
        # Determine destination based on file type
        dest_dir = None
        should_delete = False
        
        if file_name.endswith('.py') and 'test' in file_name.lower():
            dest_dir = WORKSPACE / 'scripts' / 'test_scripts'
        elif file_name.endswith('.json'):
            dest_dir = WORKSPACE / 'test_results'
        elif file_name.endswith('.md') and file_name != 'README.md':
            dest_dir = WORKSPACE / 'docs'
        elif file_name.endswith('.log'):
            dest_dir = WORKSPACE / 'logs'
        elif file_name.endswith(('.txt', '.toml', '.cfg', '.ini')) and file_name not in FILE_ORGANIZATION['root_keep']:
            dest_dir = WORKSPACE / 'scripts' / 'build_scripts'
        else:
            # Unknown file type - check if it's obsolete
            print(f"  ? Unknown file type: {file_name}")
            # Don't delete, just report
            continue
        
        if dest_dir:
            # Create destination directory if needed
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Move file
            dest_path = dest_dir / file_name
            
            # Handle duplicate names
            if dest_path.exists():
                base, ext = os.path.splitext(file_name)
                counter = 1
                while dest_path.exists():
                    new_name = f"{base}_{counter}{ext}"
                    dest_path = dest_dir / new_name
                    counter += 1
            
            shutil.move(str(file_path), str(dest_path))
            moved_count += 1
            print(f"  → Moved: {file_name} → {dest_path.relative_to(WORKSPACE)}")
    
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  Kept in root: {kept_count} files")
    print(f"  Moved: {moved_count} files")
    print(f"  Deleted: {deleted_count} files")
    print("=" * 60)
    
    # Show final root directory state
    print("\nFinal root directory contents:")
    remaining_files = [f.name for f in WORKSPACE.iterdir() if f.is_file()]
    for f in sorted(remaining_files):
        print(f"  - {f}")

if __name__ == "__main__":
    organize_files()

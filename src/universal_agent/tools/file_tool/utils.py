"""
Utility functions for file operations in the Universal Agent FileTool.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Any, Dict, Tuple


def safe_path(repo_root: str, user_path: str) -> str:
    """
    Ensure path is within repo_root directory.
    
    Args:
        repo_root: The root directory that's considered safe
        user_path: Path provided by the user
        
    Returns:
        Normalized and validated path
        
    Raises:
        ValueError: If path is outside the allowed directory
    """
    normalized = os.path.normpath(user_path)
    full_path = os.path.join(repo_root, normalized)
    if not os.path.abspath(full_path).startswith(os.path.abspath(repo_root)):
        raise ValueError("Path is outside the repository root")
    return full_path


def read_file(filepath: str) -> str:
    """
    Read the entire contents of a file.
    
    Args:
        filepath: Path to file
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def read_file_lines(filepath: str) -> List[str]:
    """
    Read a file and return its contents as a list of lines.
    
    Args:
        filepath: Path to file
        
    Returns:
        List of lines from the file
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.readlines()


def read_lines_range(filepath: str, start_line: int, end_line: int) -> Tuple[List[str], List[str]]:
    """
    Read specific lines from a file.
    
    Args:
        filepath: Path to file
        start_line: Starting line number (1-based)
        end_line: Ending line number (1-based)
        
    Returns:
        Tuple of (raw_lines, formatted_lines_with_numbers)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If line range is invalid
    """
    lines = read_file_lines(filepath)
    
    if start_line < 1 or end_line > len(lines):
        raise ValueError(f"Line numbers out of range (1-{len(lines)})")
    if end_line < start_line:
        raise ValueError(f"End line {end_line} cannot be less than start line {start_line}")
    
    selected_lines = lines[start_line-1:end_line]
    
    # Format lines with line numbers for display
    formatted_lines = []
    for i, line in enumerate(selected_lines, start=start_line):
        formatted_lines.append(f"{i}: {line.rstrip()}")
    
    return selected_lines, formatted_lines


def write_file(filepath: str, content: str) -> None:
    """
    Write content to a file, creating parent directories if needed.
    
    Args:
        filepath: Path to file
        content: Content to write
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def append_file(filepath: str, content: str) -> None:
    """
    Append content to a file.
    
    Args:
        filepath: Path to file
        content: Content to append
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found")
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)


def edit_lines(filepath: str, start_line: int, end_line: int, new_content: str) -> None:
    """
    Replace lines in a file with new content.
    
    Args:
        filepath: Path to file
        start_line: Starting line number (1-based)
        end_line: Ending line number (1-based)
        new_content: Content to insert in place of the lines
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If line range is invalid
    """
    lines = read_file_lines(filepath)
    
    if start_line < 1 or end_line > len(lines):
        raise ValueError(f"Line numbers out of range (1-{len(lines)})")
    
    # Replace the specified lines with the new content
    new_lines = new_content.splitlines()
    
    # Add newline characters to the new lines
    new_lines_with_nl = [line + '\n' for line in new_lines]
    
    # Replace the lines
    lines[start_line-1:end_line] = new_lines_with_nl
    
    # Write the modified lines back to the file
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)


def str_replace(filepath: str, old_str: str, new_str: str) -> Tuple[str, List[int]]:
    """
    Replace all occurrences of a string in a file.
    
    Args:
        filepath: Path to file
        old_str: String to replace
        new_str: String to replace with
        
    Returns:
        Tuple of (new_content, line_numbers_affected)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If string not found
    """
    content = read_file(filepath)
    
    if old_str not in content:
        raise ValueError(f"Text '{old_str}' not found in file")
    
    # Find which lines contain the search string
    lines = content.splitlines()
    line_numbers = [i+1 for i, line in enumerate(lines) if old_str in line]
    
    # Replace the string
    new_content = content.replace(old_str, new_str)
    
    # Write back to the file
    write_file(filepath, new_content)
    
    return new_content, line_numbers


def list_directory(dirpath: str, recursive: bool = False) -> List[str]:
    """
    List contents of a directory.
    
    Args:
        dirpath: Path to directory
        recursive: Whether to list recursively
        
    Returns:
        List of formatted directory contents
        
    Raises:
        NotADirectoryError: If path is not a directory
        FileNotFoundError: If directory doesn't exist
    """
    if not os.path.exists(dirpath):
        raise FileNotFoundError(f"Directory '{dirpath}' not found")
    if not os.path.isdir(dirpath):
        raise NotADirectoryError(f"'{dirpath}' is not a directory")
    
    result = []
    
    def list_items(dir_path, prefix=""):
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            rel_path = os.path.relpath(item_path, dirpath)
            if os.path.isdir(item_path):
                result.append(f"DIR  {prefix}{rel_path}")
                if recursive:
                    list_items(item_path, prefix + "  ")
            else:
                result.append(f"FILE {prefix}{rel_path}")
    
    list_items(dirpath)
    return result


def make_directory(dirpath: str, exist_ok: bool = True) -> None:
    """
    Create a directory.
    
    Args:
        dirpath: Path to directory
        exist_ok: Whether to succeed if directory already exists
    """
    os.makedirs(dirpath, exist_ok=exist_ok)


def delete_path(path: str) -> None:
    """
    Delete a file or directory.
    
    Args:
        path: Path to delete
        
    Raises:
        FileNotFoundError: If path doesn't exist
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path '{path}' not found")
    
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


def copy_path(src: str, dest: str) -> None:
    """
    Copy a file or directory.
    
    Args:
        src: Source path
        dest: Destination path
        
    Raises:
        FileNotFoundError: If source doesn't exist
    """
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source '{src}' not found")
    
    # Create destination directory if it doesn't exist
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    
    if os.path.isdir(src):
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)


def move_path(src: str, dest: str) -> None:
    """
    Move a file or directory.
    
    Args:
        src: Source path
        dest: Destination path
        
    Raises:
        FileNotFoundError: If source doesn't exist
    """
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source '{src}' not found")
    
    # Create destination directory if it doesn't exist
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    
    shutil.move(src, dest)

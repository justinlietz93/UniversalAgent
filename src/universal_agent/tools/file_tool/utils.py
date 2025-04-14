"""
Utility functions for file operations in the Universal Agent FileTool.
"""

import os
import re
import shutil
import difflib
from pathlib import Path
from typing import List, Optional, Any, Dict, Tuple, Union


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


def verify_text_context(filepath: str, expected_text: str, location_desc: str = "") -> Tuple[bool, str]:
    """
    Verify that the exact text exists in the file.
    Used for pre-validation before applying edits.
    
    Args:
        filepath: Path to file
        expected_text: Text expected to exist in the file
        location_desc: Optional description of where the text should be (for error messages)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.isfile(filepath):
        return False, f"File '{filepath}' not found"
    
    content = read_file(filepath)
    
    if expected_text not in content:
        closest_match = find_closest_match(content, expected_text)
        error_msg = f"Expected text not found {location_desc}"
        if closest_match:
            error_msg += f"\n{closest_match}"
        return False, error_msg
    
    return True, ""


def verify_lines_context(filepath: str, start_line: int, end_line: int, expected_lines: List[str]) -> Tuple[bool, str]:
    """
    Verify that the lines in the given range match the expected lines.
    Used for pre-validation before applying line-based edits.
    
    Args:
        filepath: Path to file
        start_line: Starting line number (1-based)
        end_line: Ending line number (1-based)
        expected_lines: Lines expected to exist in the file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        lines = read_file_lines(filepath)
        
        if start_line < 1 or end_line > len(lines):
            return False, f"Line numbers out of range (1-{len(lines)})"
        
        actual_lines = lines[start_line-1:end_line]
        
        # Check if the lines match exactly
        if actual_lines != expected_lines:
            # Format a diff between expected and actual
            diff = format_diff_with_context(actual_lines, expected_lines, start_line)
            return False, f"Lines {start_line}-{end_line} do not match expected content:\n{diff}"
        
        return True, ""
    except Exception as e:
        return False, str(e)


def find_closest_match(content: str, search_text: str) -> str:
    """
    Find the closest matching text to the search text.
    
    Args:
        content: Content to search in
        search_text: Text to search for
        
    Returns:
        Formatted string showing the difference
    """
    lines = content.splitlines()
    search_lines = search_text.splitlines()
    
    # If search text is just one line, find closest line
    if len(search_lines) == 1:
        closest_match = None
        closest_distance = float('inf')
        closest_index = -1
        
        for i, line in enumerate(lines):
            # Calculate Levenshtein distance ratio (higher = more similar)
            similarity = difflib.SequenceMatcher(None, search_lines[0], line).ratio()
            distance = 1 - similarity
            
            if distance < closest_distance:
                closest_distance = distance
                closest_match = line
                closest_index = i
        
        if closest_match and closest_distance < 0.5:  # Threshold for relevance
            return (f"Closest match at line {closest_index + 1}:\n"
                   f"Expected: {search_lines[0]}\n"
                   f"Found:    {closest_match}")
        return ""
    
    # For multi-line search, try to find the best block match
    matcher = difflib.SequenceMatcher(None, search_lines, lines)
    blocks = list(matcher.get_matching_blocks())
    
    if not blocks or blocks[0].size < 2:  # Need at least 2 matching lines to be useful
        return ""
    
    best_block = blocks[0]
    context_start = max(0, best_block.b - 2)
    context_end = min(len(lines), best_block.b + best_block.size + 2)
    
    result = f"Found similar section at lines {context_start+1}-{context_end}:\n"
    for i in range(context_start, context_end):
        line_marker = "→ " if context_start <= i < context_start + best_block.size else "  "
        result += f"{line_marker}{i+1}: {lines[i]}\n"
    
    return result


def format_diff_with_context(actual_lines: List[str], expected_lines: List[str], start_line: int = 1) -> str:
    """
    Format a human-readable diff between actual and expected lines.
    
    Args:
        actual_lines: The lines that were actually found
        expected_lines: The lines that were expected
        start_line: The line number where the actual lines start (1-based)
        
    Returns:
        Formatted diff string
    """
    actual_text = "".join(actual_lines)
    expected_text = "".join(expected_lines)
    
    differ = difflib.Differ()
    diff = list(differ.compare(actual_text.splitlines(), expected_text.splitlines()))
    
    result = []
    line_num = start_line
    
    for line in diff:
        if line.startswith("  "):  # Unchanged line
            result.append(f"{line_num:4d}:     {line[2:]}")
            line_num += 1
        elif line.startswith("- "):  # Line in actual but not in expected
            result.append(f"{line_num:4d}: (−) {line[2:]}")
            line_num += 1
        elif line.startswith("+ "):  # Line in expected but not in actual
            result.append(f"    : (+) {line[2:]}")
    
    return "\n".join(result)


def parse_patch(patch_content: str) -> List[Dict[str, Any]]:
    """
    Parse a patch in unified diff format.
    
    Args:
        patch_content: Content of the patch/diff
        
    Returns:
        List of parsed hunks, each with file path, line numbers, and changes
    """
    # Parse the patch content (unified diff format)
    hunks = []
    current_file = None
    current_hunk = None
    
    for line in patch_content.splitlines():
        # File headers
        if line.startswith("--- "):
            # Old file (a)
            path = line[4:].strip()
            current_file = {"old_path": path.split('\t')[0]}
        elif line.startswith("+++ "):
            # New file (b)
            if current_file:
                path = line[4:].strip()
                current_file["new_path"] = path.split('\t')[0]
            
        # Hunk headers
        elif line.startswith("@@ "):
            if current_file:
                # Parse hunk header like @@ -10,7 +10,8 @@
                match = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
                if match:
                    old_start, old_count, new_start, new_count = match.groups()
                    old_start = int(old_start)
                    old_count = int(old_count) if old_count else 1
                    new_start = int(new_start)
                    new_count = int(new_count) if new_count else 1
                    
                    current_hunk = {
                        "file": current_file["new_path"],
                        "old_start": old_start,
                        "old_count": old_count,
                        "new_start": new_start,
                        "new_count": new_count,
                        "lines": []
                    }
                    hunks.append(current_hunk)
        
        # Content lines
        elif current_hunk is not None:
            if line.startswith("+") or line.startswith("-") or line.startswith(" "):
                current_hunk["lines"].append(line)
    
    return hunks


def apply_patch(filepath: str, patch_content: str, dry_run: bool = False) -> Tuple[bool, str, List[int]]:
    """
    Apply a patch to a file.
    
    Args:
        filepath: File to apply patch to  
        patch_content: Patch content in unified diff format
        dry_run: If True, validates patch can be applied but doesn't modify the file
        
    Returns:
        Tuple of (success, message, affected_lines)
    """
    if not os.path.isfile(filepath):
        return False, f"File '{filepath}' not found", []
    
    # Read original file
    with open(filepath, "r", encoding="utf-8") as f:
        original_lines = f.readlines()
    
    # Make a copy of the original lines for modification
    patched_lines = original_lines.copy()
    
    # Parse the patch
    try:
        hunks = parse_patch(patch_content)
    except Exception as e:
        return False, f"Failed to parse patch: {str(e)}", []
    
    # Validate the hunks match the file
    affected_lines = []
    for hunk in hunks:
        file_path = hunk.get("file", "")
        if file_path and not (file_path.endswith(os.path.basename(filepath)) or file_path == "/dev/null"):
            return False, f"Patch target file '{file_path}' doesn't match '{filepath}'", []
        
        # Start line in the original file (1-based in the patch, need to convert to 0-based)
        old_start = hunk["old_start"] - 1
        old_count = hunk["old_count"]
        
        # Check that the context lines in the hunk match the file
        context_matches = True
        hunk_lines = [line[1:] for line in hunk["lines"]]  # Remove the +/- prefix
        file_lines = [line.rstrip("\n") for line in original_lines[old_start:old_start + old_count]]
        
        hunk_idx = 0
        file_idx = 0
        
        while hunk_idx < len(hunk["lines"]) and file_idx < len(file_lines):
            hunk_line = hunk["lines"][hunk_idx]
            
            if hunk_line.startswith(" "):  # Context line
                # Check if context line matches
                if file_idx < len(file_lines) and hunk_line[1:].rstrip("\n") != file_lines[file_idx]:
                    context_matches = False
                    break
                hunk_idx += 1
                file_idx += 1
            elif hunk_line.startswith("-"):  # Removed line
                # Check if removed line matches
                if file_idx < len(file_lines) and hunk_line[1:].rstrip("\n") != file_lines[file_idx]:
                    context_matches = False
                    break
                hunk_idx += 1
                file_idx += 1
            elif hunk_line.startswith("+"):  # Added line
                # Added lines don't need to match anything in the original file
                hunk_idx += 1
        
        if not context_matches:
            context_error = format_diff_with_context(
                original_lines[old_start:old_start + old_count], 
                [line + "\n" for line in hunk_lines], 
                old_start + 1
            )
            return False, f"Patch context doesn't match at line {old_start + 1}:\n{context_error}", []
        
        # Record affected lines
        affected_range = list(range(old_start + 1, old_start + old_count + 1))
        affected_lines.extend(affected_range)
        
        # Skip if in dry run mode
        if dry_run:
            continue
        
        # Apply the patch
        
        # Process the hunk lines and modify the file content
        line_index = old_start
        hunk_index = 0
        
        while hunk_index < len(hunk["lines"]):
            hunk_line = hunk["lines"][hunk_index]
            
            if hunk_line.startswith(" "):  # Context line
                line_index += 1
                hunk_index += 1
            elif hunk_line.startswith("-"):  # Line to remove
                patched_lines.pop(line_index)
                hunk_index += 1
            elif hunk_line.startswith("+"):  # Line to add
                patched_lines.insert(line_index, hunk_line[1:] + "\n")
                line_index += 1
                hunk_index += 1
    
    # Skip file write if dry run
    if not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(patched_lines)
    
    return True, f"Successfully {'validated' if dry_run else 'applied'} patch", sorted(set(affected_lines))

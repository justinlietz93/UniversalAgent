"""
Read operation handlers for the FileTool.
"""

import os
from typing import Dict, Any

from src.universal_agent.interfaces.types import ToolResult

from ..utils import safe_path, read_file, read_file_lines, read_lines_range, list_directory


async def handle_read(create_result_method, repo_root: str, path: str) -> ToolResult:
    """
    Handle the read operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to read
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        if os.path.isdir(full_path):
            # If path is a directory, list its contents
            result = list_directory(full_path)
            return create_result_method(success=True, data={
                "operation": "read",
                "path": path,
                "is_directory": True,
                "content": "\n".join(result)
            })
        
        content = read_file(full_path)
        
        return create_result_method(success=True, data={
            "operation": "read",
            "path": path,
            "content": content
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error reading file: {str(e)}")


async def handle_read_lines(create_result_method, repo_root: str, path: str, start_line: int, end_line: int) -> ToolResult:
    """
    Handle the read_lines operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to read
        start_line: Starting line number (1-based)
        end_line: Ending line number (1-based)
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        _, formatted_lines = read_lines_range(full_path, start_line, end_line)
        
        return create_result_method(success=True, data={
            "operation": "read_lines",
            "path": path,
            "start_line": start_line,
            "end_line": end_line,
            "lines": "\n".join(formatted_lines)
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error reading lines: {str(e)}")


async def handle_read_chunk(create_result_method, repo_root: str, path: str, start_line: int, num_lines: int) -> ToolResult:
    """
    Handle the read_chunk operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to read
        start_line: Starting line number (1-based)
        num_lines: Number of lines to read
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        end_line = start_line + num_lines - 1
        
        # Use read_lines_range but cap end_line at the file's actual line count
        lines = read_file_lines(full_path)
        end_line = min(end_line, len(lines))
        
        _, formatted_lines = read_lines_range(full_path, start_line, end_line)
        
        return create_result_method(success=True, data={
            "operation": "read_chunk",
            "path": path,
            "start_line": start_line,
            "end_line": end_line,
            "num_lines": len(formatted_lines),
            "lines": "\n".join(formatted_lines)
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error reading chunk: {str(e)}")

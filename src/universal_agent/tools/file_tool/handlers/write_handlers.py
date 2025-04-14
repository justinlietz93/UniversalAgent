"""
Write operation handlers for the FileTool.
"""

import os
from typing import Dict, Any

from src.universal_agent.interfaces.types import ToolResult

from ..utils import safe_path, read_file, write_file, append_file


async def handle_write(create_result_method, repo_root: str, path: str, content: str, file_history: Dict) -> ToolResult:
    """
    Handle the write operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to write to
        content: Content to write
        file_history: Dictionary for tracking file history
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        # Save history if file exists (for potential undo)
        if os.path.exists(full_path):
            try:
                file_history[full_path].append(read_file(full_path))
            except Exception:
                pass
                
        write_file(full_path, content)
        
        return create_result_method(success=True, data={
            "operation": "write",
            "path": path,
            "message": f"Successfully wrote {len(content)} characters to {path}"
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error writing file: {str(e)}")


async def handle_append(create_result_method, repo_root: str, path: str, content: str, file_history: Dict) -> ToolResult:
    """
    Handle the append operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to append to
        content: Content to append
        file_history: Dictionary for tracking file history
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        # Save history (for potential undo)
        if os.path.exists(full_path):
            try:
                file_history[full_path].append(read_file(full_path))
            except Exception:
                pass
        
        # If the file doesn't exist, create it instead of appending
        if not os.path.exists(full_path):
            write_file(full_path, content)
        else:
            # Always add a newline before appending unless content already starts with one
            if content and not content.startswith("\n"):
                content = "\n" + content
            append_file(full_path, content)
        
        return create_result_method(success=True, data={
            "operation": "append",
            "path": path,
            "message": f"Successfully appended {len(content)} characters to {path}"
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error appending to file: {str(e)}")

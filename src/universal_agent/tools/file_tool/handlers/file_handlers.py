"""
File management operation handlers for the FileTool.
"""

import os
from typing import Dict, Any

from src.universal_agent.interfaces.types import ToolResult

from ..utils import safe_path, copy_path, move_path


async def handle_copy(create_result_method, repo_root: str, src: str, dest: str) -> ToolResult:
    """
    Handle the copy operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        src: Source path to copy from
        dest: Destination path to copy to
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_src = safe_path(repo_root, src)
        full_dest = safe_path(repo_root, dest)
        
        if not os.path.exists(full_src):
            return create_result_method(success=False, error=f"Source not found: {src}")
        
        is_dir = os.path.isdir(full_src)
        
        copy_path(full_src, full_dest)
        
        return create_result_method(success=True, data={
            "operation": "copy",
            "source": src,
            "destination": dest,
            "is_directory": is_dir,
            "message": f"Successfully copied {'directory' if is_dir else 'file'} from {src} to {dest}"
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error copying: {str(e)}")


async def handle_move(create_result_method, repo_root: str, src: str, dest: str, file_history: Dict) -> ToolResult:
    """
    Handle the move operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        src: Source path to move from
        dest: Destination path to move to
        file_history: Dictionary for tracking file history
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_src = safe_path(repo_root, src)
        full_dest = safe_path(repo_root, dest)
        
        if not os.path.exists(full_src):
            return create_result_method(success=False, error=f"Source not found: {src}")
        
        is_dir = os.path.isdir(full_src)
        
        move_path(full_src, full_dest)
        
        # Update file history path if we have any
        if full_src in file_history:
            file_history[full_dest] = file_history[full_src]
            del file_history[full_src]
        
        return create_result_method(success=True, data={
            "operation": "move",
            "source": src,
            "destination": dest,
            "is_directory": is_dir,
            "message": f"Successfully moved {'directory' if is_dir else 'file'} from {src} to {dest}"
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error moving: {str(e)}")

"""
Directory operation handlers for the FileTool.
"""

import os
from typing import Dict, Any, List, Optional

from src.universal_agent.interfaces.types import ToolResult

from ..utils import safe_path, list_directory, make_directory, delete_path


async def handle_list_dir(create_result_method, repo_root: str, path: str, recursive: bool = False) -> ToolResult:
    """
    Handle the list_dir operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to the directory to list
        recursive: Whether to list recursively
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        if not os.path.exists(full_path):
            return create_result_method(success=False, error=f"Directory not found: {path}")
        
        if not os.path.isdir(full_path):
            return create_result_method(success=False, error=f"Path is not a directory: {path}")
        
        result = list_directory(full_path, recursive)
        
        return create_result_method(success=True, data={
            "operation": "list_dir",
            "path": path,
            "recursive": recursive,
            "content": "\n".join(result)
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error listing directory: {str(e)}")


async def handle_mkdir(create_result_method, repo_root: str, path: str, exist_ok: bool = True) -> ToolResult:
    """
    Handle the mkdir operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to the directory to create
        exist_ok: Whether to succeed if directory already exists
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        make_directory(full_path, exist_ok)
        
        return create_result_method(success=True, data={
            "operation": "mkdir",
            "path": path,
            "message": f"Successfully created directory {path}"
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error creating directory: {str(e)}")


async def handle_delete(create_result_method, repo_root: str, path: str) -> ToolResult:
    """
    Handle the delete operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to delete
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        if not os.path.exists(full_path):
            return create_result_method(success=False, error=f"Path not found: {path}")
        
        is_dir = os.path.isdir(full_path)
        
        delete_path(full_path)
        
        return create_result_method(success=True, data={
            "operation": "delete",
            "path": path,
            "is_directory": is_dir,
            "message": f"Successfully deleted {'directory' if is_dir else 'file'} {path}"
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error deleting: {str(e)}")

"""
Patch operation handlers for the FileTool.
"""

from typing import Dict, Any, List

from src.universal_agent.interfaces.types import ToolResult

from ..utils import safe_path, read_file, apply_patch


async def handle_patch(
    create_result_method, 
    repo_root: str, 
    path: str, 
    patch_content: str, 
    dry_run: bool = False,
    file_history: Dict = None
) -> ToolResult:
    """
    Handle the patch operation - apply a unified diff/patch to a file.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to file to patch
        patch_content: Content of patch in unified diff format
        dry_run: If True, validate but don't apply the patch
        file_history: Dictionary for tracking file history
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        # Save history for undo if needed and not doing a dry run
        if file_history is not None and not dry_run:
            try:
                file_history[full_path].append(read_file(full_path))
            except Exception:
                pass
            
        # First validate the patch (always do this)
        success, message, affected_lines = apply_patch(full_path, patch_content, dry_run=True)
        
        if not success:
            return create_result_method(success=False, error=f"Patch validation failed: {message}")
            
        # If we're not in dry run mode and validation passed, apply the patch
        if not dry_run:
            success, message, affected_lines = apply_patch(full_path, patch_content, dry_run=False)
            
            if not success:
                return create_result_method(success=False, error=f"Patch application failed: {message}")
        
        return create_result_method(success=True, data={
            "operation": "patch",
            "path": path,
            "dry_run": dry_run,
            "message": message,
            "affected_lines": affected_lines
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error applying patch: {str(e)}")

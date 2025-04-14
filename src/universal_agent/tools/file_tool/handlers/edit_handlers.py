"""
Edit operation handlers for the FileTool.
"""

from typing import Dict, Any, List

from src.universal_agent.interfaces.types import ToolResult

from ..utils import safe_path, read_file, read_file_lines, edit_lines, str_replace, write_file


async def handle_edit_lines(
    create_result_method, 
    repo_root: str, 
    path: str, 
    start_line: int, 
    end_line: int, 
    content: str, 
    file_history: Dict,
    snippet_lines: int = 4
) -> ToolResult:
    """
    Handle the edit_lines operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to edit
        start_line: Starting line number (1-based)
        end_line: Ending line number (1-based)
        content: New content for the specified lines
        file_history: Dictionary for tracking file history
        snippet_lines: Number of context lines to show around edits
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        # Save history (for potential undo)
        try:
            file_history[full_path].append(read_file(full_path))
        except Exception:
            pass
        
        edit_lines(full_path, start_line, end_line, content)
        
        # Create a snippet of the edited region plus context
        lines = read_file_lines(full_path)
        snippet_start = max(0, start_line - 1 - snippet_lines)
        snippet_end = min(len(lines), start_line - 1 + len(content.splitlines()) + snippet_lines)
        
        snippet_lines_formatted = []
        for i, line in enumerate(lines[snippet_start:snippet_end], start=snippet_start+1):
            snippet_lines_formatted.append(f"{i}: {line.rstrip()}")
        
        return create_result_method(success=True, data={
            "operation": "edit_lines",
            "path": path,
            "start_line": start_line,
            "end_line": end_line,
            "message": f"Successfully edited lines {start_line}-{end_line} in {path}",
            "snippet": "\n".join(snippet_lines_formatted)
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error editing lines: {str(e)}")


async def handle_insert(
    create_result_method, 
    repo_root: str, 
    path: str, 
    insert_line: int, 
    content: str, 
    file_history: Dict,
    snippet_lines: int = 4
) -> ToolResult:
    """
    Handle the insert operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to insert into
        insert_line: Line number to insert at (1-based)
        content: Content to insert
        file_history: Dictionary for tracking file history
        snippet_lines: Number of context lines to show around edits
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        # Save history (for potential undo)
        try:
            file_history[full_path].append(read_file(full_path))
        except Exception:
            pass
        
        # Read existing lines
        lines = read_file_lines(full_path)
        
        if insert_line < 0 or insert_line > len(lines):
            return create_result_method(
                success=False, 
                error=f"Invalid insert line {insert_line} for file with {len(lines)} lines"
            )
        
        # Split content into lines and add newlines
        content_lines = [line + '\n' for line in content.splitlines()]
        
        # Insert the new lines at the specified position
        lines[insert_line:insert_line] = content_lines
        
        # Write the file back
        with open(full_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        # Create a snippet of the inserted region plus context
        snippet_start = max(0, insert_line - snippet_lines)
        snippet_end = min(len(lines), insert_line + len(content_lines) + snippet_lines)
        
        snippet_lines_formatted = []
        for i, line in enumerate(lines[snippet_start:snippet_end], start=snippet_start+1):
            snippet_lines_formatted.append(f"{i}: {line.rstrip()}")
        
        return create_result_method(success=True, data={
            "operation": "insert",
            "path": path,
            "insert_line": insert_line,
            "message": f"Successfully inserted at line {insert_line} in {path}",
            "snippet": "\n".join(snippet_lines_formatted)
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error inserting into file: {str(e)}")


async def handle_str_replace(
    create_result_method, 
    repo_root: str, 
    path: str, 
    old_str: str, 
    new_str: str, 
    file_history: Dict,
    snippet_lines: int = 4
) -> ToolResult:
    """
    Handle the str_replace operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to modify
        old_str: String to replace
        new_str: String to replace with
        file_history: Dictionary for tracking file history
        snippet_lines: Number of context lines to show around edits
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        # Save history (for potential undo)
        try:
            file_history[full_path].append(read_file(full_path))
        except Exception:
            pass
        
        # Replace the string and get affected line numbers
        new_content, line_numbers = str_replace(full_path, old_str, new_str)
        
        # Create a snippet around the edit
        lines = new_content.splitlines()
        if line_numbers:
            # Find the lines that contain the edit
            primary_line = line_numbers[0]
            
            # Create a snippet around the first edit
            snippet_start = max(0, primary_line - 1 - snippet_lines)
            snippet_end = min(len(lines), primary_line + snippet_lines)
            
            snippet_lines_formatted = []
            for i, line in enumerate(lines[snippet_start:snippet_end], start=snippet_start+1):
                snippet_lines_formatted.append(f"{i}: {line}")
            
            snippet = "\n".join(snippet_lines_formatted)
            affected_info = f"lines {', '.join(map(str, line_numbers))}"
        else:
            snippet = ""
            affected_info = "no lines"
        
        return create_result_method(success=True, data={
            "operation": "str_replace",
            "path": path,
            "message": f"Successfully replaced '{old_str}' with '{new_str}' in {path} (affected {affected_info})",
            "affected_lines": line_numbers,
            "snippet": snippet
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error performing string replacement: {str(e)}")


async def handle_undo_edit(create_result_method, repo_root: str, path: str, file_history: Dict) -> ToolResult:
    """
    Handle the undo_edit operation.
    
    Args:
        create_result_method: Method to create success/error results
        repo_root: Root directory for operations
        path: Path to undo edits for
        file_history: Dictionary for tracking file history
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        if not file_history[full_path]:
            return create_result_method(success=False, error=f"No edit history for {path}")
        
        previous_content = file_history[full_path].pop()
        write_file(full_path, previous_content)
        
        return create_result_method(success=True, data={
            "operation": "undo_edit",
            "path": path,
            "message": f"Successfully reverted last edit to {path}"
        })
        
    except Exception as e:
        return create_result_method(success=False, error=f"Error undoing edit: {str(e)}")

"""
Edit operation handlers for the FileTool.
"""

from typing import Dict, Any, List

from src.universal_agent.interfaces.types import ToolResult

from ..utils import (
    safe_path, 
    read_file, 
    read_file_lines, 
    edit_lines, 
    str_replace, 
    write_file,
    verify_lines_context,
    verify_text_context,
    format_diff_with_context
)


async def handle_edit_lines(
    create_result_method, 
    repo_root: str, 
    path: str, 
    start_line: int, 
    end_line: int, 
    content: str, 
    file_history: Dict,
    snippet_lines: int = 4,
    expected_lines: List[str] = None,
    validate: bool = True
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
        expected_lines: If provided, these lines must match the current content
                        in the target line range for the edit to proceed
        validate: Whether to perform pre-validation (default: True)
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        # Pre-validation: Check if the current content matches expectations
        if validate:
            try:
                lines = read_file_lines(full_path)
                
                # Validate line range
                if start_line < 1 or end_line > len(lines):
                    return create_result_method(
                        success=False,
                        error=f"Line numbers out of range (1-{len(lines)})"
                    )
                
                # If expected_lines is provided, validate they match current content
                if expected_lines is not None:
                    is_valid, error_msg = verify_lines_context(
                        full_path,
                        start_line,
                        end_line,
                        expected_lines
                    )
                    
                    if not is_valid:
                        return create_result_method(
                            success=False,
                            error=f"Pre-validation failed: {error_msg}"
                        )
            except Exception as e:
                return create_result_method(
                    success=False,
                    error=f"Error during pre-validation: {str(e)}"
                )
        
        # Save history (for potential undo)
        try:
            file_history[full_path].append(read_file(full_path))
        except Exception:
            pass
        
        # Proceed with the edit
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
    snippet_lines: int = 4,
    context_line: str = None,
    validate: bool = True
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
        context_line: If provided, the line before/at insertion point must match this
                      for the insert to proceed (used for pre-validation)
        validate: Whether to perform pre-validation (default: True)
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        # Read existing lines for validation
        lines = read_file_lines(full_path)
        
        # Pre-validation
        if validate:
            try:
                # Validate line range
                if insert_line < 0 or insert_line > len(lines):
                    return create_result_method(
                        success=False, 
                        error=f"Invalid insert line {insert_line} for file with {len(lines)} lines"
                    )
                
                # If context_line is provided, validate it matches the line at the insertion point
                # (or the line before if inserting at the end)
                if context_line is not None:
                    check_line_idx = min(insert_line, len(lines)) - 1
                    if check_line_idx >= 0:
                        actual_line = lines[check_line_idx].rstrip('\n')
                        if actual_line != context_line:
                            error_msg = (
                                f"Pre-validation failed: Context mismatch at line {check_line_idx + 1}\n"
                                f"Expected: {context_line}\n"
                                f"Found:    {actual_line}"
                            )
                            return create_result_method(success=False, error=error_msg)
            except Exception as e:
                return create_result_method(
                    success=False,
                    error=f"Error during pre-validation: {str(e)}"
                )
        
        # Save history (for potential undo)
        try:
            file_history[full_path].append(read_file(full_path))
        except Exception:
            pass
        
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
    snippet_lines: int = 4,
    validate: bool = True,
    expected_content: str = None
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
        validate: Whether to perform pre-validation (default: True)
        expected_content: If provided, the file must contain this exact content
                          for the replacement to proceed (for pre-validation)
        
    Returns:
        ToolResult with operation result
    """
    try:
        full_path = safe_path(repo_root, path)
        
        # Pre-validation
        if validate:
            try:
                # Verify if old_str exists in the file
                is_valid, error_msg = verify_text_context(
                    full_path, 
                    old_str, 
                    f"in '{path}'"
                )
                
                if not is_valid:
                    return create_result_method(
                        success=False,
                        error=f"Pre-validation failed: {error_msg}"
                    )
                
                # If expected_content is provided, validate the file has this exact content
                if expected_content is not None:
                    content = read_file(full_path)
                    if content != expected_content:
                        error_msg = format_diff_with_context(
                            content.splitlines(), 
                            expected_content.splitlines()
                        )
                        return create_result_method(
                            success=False,
                            error=f"Pre-validation failed: File content has changed since last read:\n{error_msg}"
                        )
            except Exception as e:
                return create_result_method(
                    success=False,
                    error=f"Error during pre-validation: {str(e)}"
                )
        
        # Save history (for potential undo)
        try:
            file_history[full_path].append(read_file(full_path))
        except Exception:
            pass
        
        # Replace the string and get affected line numbers
        try:
            new_content, line_numbers = str_replace(full_path, old_str, new_str)
        except ValueError as e:
            # Additional error handling for a better user experience
            return create_result_method(
                success=False,
                error=f"String replacement failed: {str(e)}"
            )
        
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

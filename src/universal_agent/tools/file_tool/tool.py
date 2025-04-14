"""
Main FileTool implementation for the Universal Agent.

This file provides a unified implementation that combines functionality
from both the original file_tool.py and advanced_file_tool.py.
"""

import os
from collections import defaultdict
from typing import Dict, Any, Optional

from dotenv import load_dotenv

from src.universal_agent.interfaces.types import ToolParams, ToolResult
from src.universal_agent.tools.base_tool import BaseTool

from .operations import FileOperation
from .handlers.read_handlers import handle_read, handle_read_lines, handle_read_chunk
from .handlers.write_handlers import handle_write, handle_append
from .handlers.edit_handlers import handle_edit_lines, handle_insert, handle_str_replace, handle_undo_edit
from .handlers.dir_handlers import handle_list_dir, handle_mkdir, handle_delete
from .handlers.file_handlers import handle_copy, handle_move
from .handlers.patch_handlers import handle_patch

# Load environment variables
load_dotenv()


class FileTool(BaseTool):
    """
    Unified file system tool that combines the functionality of both
    file_tool.py and advanced_file_tool.py.
    
    Provides comprehensive file and directory operations including:
    - Reading files (whole, specific lines, chunks)
    - Writing and appending content
    - Editing files (line-based, string replacements)
    - Directory operations (create, delete, list)
    - File management (copy, move, delete)
    
    Supports edit history for undo operations and has robust path safety.
    """
    
    def __init__(
        self, 
        id: str = "file", 
        name: str = "File Operations", 
        description: str = None,
        repo_root: str = None
    ):
        """
        Initialize the file tool.
        
        Args:
            id: Unique identifier for the tool
            name: Human-readable name for the tool
            description: Tool description (auto-generated if None)
            repo_root: Root directory for file operations (default: CODEBASE_PATH env var or current dir)
        """
        # Generate description if not provided
        if description is None:
            description = self._generate_description()
            
        super().__init__(id=id, name=name, description=description)
        
        # Set repo root - prioritize passed value, then env var, then current directory
        if repo_root:
            self.repo_root = os.path.abspath(repo_root)
        else:
            codebase_path = os.getenv("CODEBASE_PATH", ".")
            self.repo_root = os.path.abspath(codebase_path)
            
        # Create repo root if it doesn't exist
        os.makedirs(self.repo_root, exist_ok=True)
        
        # File edit history for undo operations
        self._file_history = defaultdict(list)
        
        # Number of context lines to show around edits
        self.snippet_lines = 4
    
    def _generate_description(self) -> str:
        """Generate a comprehensive description of the tool."""
        return (
            "A unified file system tool that provides comprehensive file and directory operations with robust error handling and pre-validation.\n\n"
            "Core Operations:\n"
            "- Reading files: read entire files, specific line ranges, or chunks\n"
            "- Writing files: create new files, append to existing files\n"
            "- Editing files: replace specific lines, find and replace strings, with pre-validation\n"
            "- Patch files: apply standard unified diff/patch format to files with validation\n"
            "- Directory operations: create, delete, list contents\n"
            "- File management: copy, move, delete files\n\n"
            
            "Enhanced Features:\n"
            "- Pre-validation of edits to prevent applying changes to outdated file state\n"
            "- Detailed error messages with context and diffs when validation fails\n"
            "- Patch application with context verification for targeted edits\n"
            "- Edit history for undo operations\n\n"
            
            "Example Usage:\n"
            "- Read a file: {'operation': 'read', 'path': 'path/to/file.py'}\n"
            "- Write a file: {'operation': 'write', 'path': 'path/to/file.py', 'content': '# New content'}\n"
            "- Edit specific lines: {'operation': 'edit_lines', 'path': 'file.py', 'start_line': 10, 'end_line': 15, 'content': 'new code'}\n"
            "- Apply a patch: {'operation': 'patch', 'path': 'file.py', 'content': '@@ -10,7 +10,7 @@\\n line1\\n-old line\\n+new line\\n line3'}\n"
            "- List directory: {'operation': 'list_dir', 'path': 'src', 'recursive': true}\n"
            "- Copy file: {'operation': 'copy', 'path': 'source.py', 'dest': 'destination.py'}\n"
        )
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """Get the parameter schema for the tool."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [e.value for e in FileOperation],
                    "description": "The operation to perform"
                },
                "path": {
                    "type": "string",
                    "description": "Target file or directory path"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write, append, or edit"
                },
                "start_line": {
                    "type": "integer",
                    "description": "Starting line number for line operations (1-based)"
                },
                "end_line": {
                    "type": "integer",
                    "description": "Ending line number for line operations (1-based)"
                },
                "num_lines": {
                    "type": "integer",
                    "description": "Number of lines to read for chunk operations"
                },
                "old_str": {
                    "type": "string",
                    "description": "String to find in replacement operations"
                },
                "new_str": {
                    "type": "string",
                    "description": "String to replace with in replacement operations"
                },
                "src": {
                    "type": "string", 
                    "description": "Source path for copy/move operations"
                },
                "dest": {
                    "type": "string",
                    "description": "Destination path for copy/move operations"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to perform operations recursively"
                }
            },
            "required": ["operation"],
            "additionalProperties": False,
            
            # Define additional required parameters based on operation
            "allOf": [
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["write", "create", "append"]}
                        }
                    },
                    "then": {
                        "required": ["path", "content"]
                    }
                },
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["read", "view", "read_chunk", "delete", "delete_file", "mkdir", "rmdir", "list_dir"]}
                        }
                    },
                    "then": {
                        "required": ["path"]
                    }
                },
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["read_lines", "edit_lines", "edit"]}
                        }
                    },
                    "then": {
                        "required": ["path", "start_line", "end_line"]
                    }
                },
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["read_chunk"]}
                        }
                    },
                    "then": {
                        "required": ["path", "start_line"]
                    }
                },
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["str_replace"]}
                        }
                    },
                    "then": {
                        "required": ["path", "old_str", "new_str"]
                    }
                },
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["insert"]}
                        }
                    },
                    "then": {
                        "required": ["path", "start_line", "content"]
                    }
                },
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["copy", "move"]}
                        }
                    },
                    "then": {
                        "required": ["path", "dest"]
                    }
                },
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["patch"]}
                        }
                    },
                    "then": {
                        "required": ["path", "content"],
                        "properties": {
                            "dry_run": {
                                "type": "boolean",
                                "description": "If true, validate but don't apply the patch"
                            }
                        }
                    }
                }
            ]
        }
    
    def create_success_result(self, data: Dict[str, Any]) -> ToolResult:
        """Create a successful result."""
        return self.create_result(success=True, data=data)
    
    def create_error_result(self, error: str) -> ToolResult:
        """Create an error result."""
        return self.create_result(success=False, error=error)
        
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the file operation with the given parameters.
        
        Args:
            params: Dictionary containing operation-specific parameters
                
        Returns:
            ToolResult with the operation result
        """
        try:
            # Extract and validate basic parameters
            operation_str = params.get("operation", "")
            
            if not operation_str:
                return self.create_error_result("operation parameter is required")
            
            try:
                operation = FileOperation(operation_str)
            except ValueError:
                return self.create_error_result(f"Invalid operation: {operation_str}")
            
            # Get the path parameter for most operations
            path_param = params.get("path", "")
            
            # Some operations use 'src' instead of 'path'
            if not path_param and operation in [FileOperation.COPY, FileOperation.MOVE]:
                path_param = params.get("src", "")
            
            # Special handling for Python files
            # Define file-specific operations that should have a .py extension if none is present
            file_operations = [
                FileOperation.READ, FileOperation.WRITE, FileOperation.READ_LINES, 
                FileOperation.EDIT_LINES, FileOperation.APPEND, FileOperation.CREATE
            ]
            
            # Check if the path already has an extension
            if path_param and operation in file_operations:
                has_extension = os.path.splitext(path_param)[1] != ""
                # Append .py only for file operations if no extension is present
                if not has_extension:
                    path_param += ".py"
            
            # Use a method reference for creating results
            create_result_method = self.create_result
            
            # Dispatch to the appropriate operation handler
            if operation in [FileOperation.READ, FileOperation.VIEW]:
                return await handle_read(create_result_method, self.repo_root, path_param)
                
            elif operation == FileOperation.READ_LINES:
                start_line = params.get("start_line")
                end_line = params.get("end_line")
                return await handle_read_lines(create_result_method, self.repo_root, path_param, start_line, end_line)
                
            elif operation == FileOperation.READ_CHUNK:
                start_line = params.get("start_line")
                num_lines = params.get("num_lines", 50)
                return await handle_read_chunk(create_result_method, self.repo_root, path_param, start_line, num_lines)
                
            elif operation in [FileOperation.WRITE, FileOperation.CREATE]:
                content = params.get("content", "")
                return await handle_write(create_result_method, self.repo_root, path_param, content, self._file_history)
                
            elif operation == FileOperation.APPEND:
                content = params.get("content", "")
                return await handle_append(create_result_method, self.repo_root, path_param, content, self._file_history)
                
            elif operation in [FileOperation.EDIT_LINES, FileOperation.EDIT]:
                start_line = params.get("start_line")
                end_line = params.get("end_line")
                content = params.get("content", "")
                return await handle_edit_lines(
                    create_result_method, 
                    self.repo_root, 
                    path_param, 
                    start_line, 
                    end_line, 
                    content, 
                    self._file_history,
                    self.snippet_lines
                )
                
            elif operation == FileOperation.INSERT:
                start_line = params.get("start_line")
                content = params.get("content", "")
                return await handle_insert(
                    create_result_method, 
                    self.repo_root, 
                    path_param, 
                    start_line, 
                    content, 
                    self._file_history,
                    self.snippet_lines
                )
                
            elif operation == FileOperation.STR_REPLACE:
                old_str = params.get("old_str", "")
                new_str = params.get("new_str", "")
                return await handle_str_replace(
                    create_result_method, 
                    self.repo_root, 
                    path_param, 
                    old_str, 
                    new_str, 
                    self._file_history,
                    self.snippet_lines
                )
                
            elif operation == FileOperation.UNDO_EDIT:
                return await handle_undo_edit(create_result_method, self.repo_root, path_param, self._file_history)
                
            elif operation in [FileOperation.LIST_DIR]:
                recursive = params.get("recursive", False)
                return await handle_list_dir(create_result_method, self.repo_root, path_param, recursive)
                
            elif operation in [FileOperation.MKDIR]:
                exist_ok = params.get("exist_ok", True)
                return await handle_mkdir(create_result_method, self.repo_root, path_param, exist_ok)
                
            elif operation in [FileOperation.RMDIR, FileOperation.DELETE, FileOperation.DELETE_FILE]:
                return await handle_delete(create_result_method, self.repo_root, path_param)
                
            elif operation == FileOperation.COPY:
                dest = params.get("dest", "")
                return await handle_copy(create_result_method, self.repo_root, path_param, dest)
                
            elif operation == FileOperation.MOVE:
                dest = params.get("dest", "")
                return await handle_move(create_result_method, self.repo_root, path_param, dest, self._file_history)
                
            elif operation == FileOperation.PATCH:
                patch_content = params.get("content", "")
                dry_run = params.get("dry_run", False)
                return await handle_patch(
                    create_result_method,
                    self.repo_root,
                    path_param,
                    patch_content,
                    dry_run,
                    self._file_history
                )
                
            else:
                return self.create_error_result(f"Operation not implemented: {operation}")
                
        except Exception as e:
            return self.create_error_result(f"Error executing file operation: {str(e)}")

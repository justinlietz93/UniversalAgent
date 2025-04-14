"""
File operation definitions for the Universal Agent FileTool.
"""

from enum import Enum, auto
from typing import Literal


class FileOperation(str, Enum):
    """
    Operations supported by the FileTool.
    
    Combines operations from both the original file_tool and advanced_file_tool.
    """
    # Standard file operations
    READ = "read"
    READ_LINES = "read_lines"
    READ_CHUNK = "read_chunk"
    WRITE = "write"
    APPEND = "append"
    
    # Directory operations
    LIST_DIR = "list_dir"
    MKDIR = "mkdir"
    RMDIR = "rmdir"
    
    # Advanced editing operations
    EDIT_LINES = "edit_lines"
    EDIT = "edit"
    INSERT = "insert"
    STR_REPLACE = "str_replace"
    UNDO_EDIT = "undo_edit"
    
    # File management operations
    DELETE_FILE = "delete_file"
    DELETE = "delete"
    COPY = "copy"
    MOVE = "move"
    
    # Legacy operation names (for backward compatibility)
    VIEW = "view"
    CREATE = "create"

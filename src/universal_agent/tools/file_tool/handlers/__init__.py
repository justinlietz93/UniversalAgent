"""
Operation handlers for the FileTool.

This package contains modular implementations of the various file operations
supported by the FileTool, organized by operation type.
"""

from .read_handlers import handle_read, handle_read_lines, handle_read_chunk
from .write_handlers import handle_write, handle_append
from .edit_handlers import handle_edit_lines, handle_insert, handle_str_replace, handle_undo_edit
from .dir_handlers import handle_list_dir, handle_mkdir, handle_delete
from .file_handlers import handle_copy, handle_move

__all__ = [
    "handle_read", "handle_read_lines", "handle_read_chunk",
    "handle_write", "handle_append",
    "handle_edit_lines", "handle_insert", "handle_str_replace", "handle_undo_edit",
    "handle_list_dir", "handle_mkdir", "handle_delete",
    "handle_copy", "handle_move"
]

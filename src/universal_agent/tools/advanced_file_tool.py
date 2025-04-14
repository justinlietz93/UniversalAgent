"""
Advanced file operations tool that is now part of the unified FileTool.

This module provides a facade that imports the actual FileTool implementation
from the file_tool package. This maintains backward compatibility with any
code that imports the advanced_file_tool.

The functionality has been merged with file_tool.py into a single, unified
FileTool implementation to avoid duplication and improve maintainability.
"""

import warnings
from src.universal_agent.tools.file_tool import FileTool, FileOperation

# Emit a deprecation warning
warnings.warn(
    "advanced_file_tool.py is deprecated and will be removed in a future version. "
    "Please use src.universal_agent.tools.file_tool.FileTool instead.",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility, create an alias with the old name
class AdvancedFileTool(FileTool):
    """Legacy alias for FileTool to maintain backward compatibility."""
    
    def __init__(self, repo_root="./"):
        """Initialize with same parameters as the old implementation."""
        super().__init__(
            id="advanced_file_operations",
            name="Advanced File Operations",
            repo_root=repo_root
        )

# Re-export for backward compatibility
__all__ = ['AdvancedFileTool']

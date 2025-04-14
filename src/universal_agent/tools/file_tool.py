"""
Unified file system tool that combines functionality from both 
file_tool.py and advanced_file_tool.py.

This module provides a facade that imports the actual FileTool implementation
from the file_tool package. This maintains backward compatibility with any
code that imports from the original location.

The FileTool has been refactored into a package structure to comply with
the QUAL-SIZE rule limiting individual code files to 500 lines.
"""

from src.universal_agent.tools.file_tool import FileTool, FileOperation

# Re-export the classes for backward compatibility
__all__ = ['FileTool', 'FileOperation']

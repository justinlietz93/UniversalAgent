"""
Unified file operations module for the Universal Agent.

This module combines the functionality from both file_tool.py and advanced_file_tool.py
into a single, comprehensive package that follows the modular structure pattern.
"""

from .tool import FileTool
from .operations import FileOperation

__all__ = ['FileTool', 'FileOperation']

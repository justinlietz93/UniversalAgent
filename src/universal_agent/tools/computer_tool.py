"""
Computer tool for controlling mouse, keyboard, screen captures, and windows.

This module provides a facade that imports the actual ComputerTool implementation
from the computer_tool package. This maintains backward compatibility with any
code that imports from the original location.

The ComputerTool has been refactored into a package structure to comply with
the QUAL-SIZE rule limiting individual code files to 500 lines.
"""

from src.universal_agent.tools.computer_tool import ComputerTool, Action, ScrollDirection

# Re-export the classes for backward compatibility
__all__ = ['ComputerTool', 'Action', 'ScrollDirection']

"""
Universal Agent

A universal wrapper for interacting with various LLM providers with dynamic capability discovery
and unified tool handling.
"""

__version__ = "1.0.0"

from .core.wrapper import UniversalAgent
from .tools.base_tool import BaseTool

__all__ = ["UniversalAgent", "BaseTool"]

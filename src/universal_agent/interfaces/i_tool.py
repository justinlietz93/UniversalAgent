# Interface definition for ITool
from abc import ABC, abstractmethod
from typing import Dict, Any, Coroutine

# Forward reference for ToolResult if defined in types.py
# from .types import ToolResult, ToolParams # Uncomment when types.py is defined

class ITool(ABC):
    """
    Abstract Base Class defining the interface for all tools
    compatible with the Universal Agent framework.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """A unique identifier for the tool."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """A human-readable name for the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of what the tool does."""
        pass

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the tool's core logic asynchronously.

        Args:
            params (Dict[str, Any]): A dictionary containing the parameters
                                     extracted by the NLP parser for this tool invocation.
                                     Corresponds to ToolParams structure.

        Returns:
            Dict[str, Any]: A dictionary containing the result of the execution.
                            Should conform to the ToolResult structure (e.g.,
                            {'success': True, 'data': ...} or
                            {'success': False, 'error': ...}).
        """
        pass

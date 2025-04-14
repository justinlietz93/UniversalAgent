# Interface definition for IUniversalAgent
from abc import ABC, abstractmethod
from typing import Dict, Any, Coroutine

# Forward reference for AgentResult if defined in types.py
# from .types import AgentResult # Uncomment when types.py is defined

class IUniversalAgent(ABC):
    """
    Abstract Base Class defining the primary interface for interacting
    with the Universal Agent framework.
    """

    @abstractmethod
    async def execute(self, command: str) -> Dict[str, Any]:
        """
        Processes a natural language command asynchronously.

        This method orchestrates the core workflow:
        1. Parses the natural language `command` using the configured
           (and MANDATORY) Transformer-based NLP parser into a structured
           `AgentRequest`.
        2. Routes the `AgentRequest` via the `IRouter` to the appropriate `ITool`.
        3. Executes the selected `ITool`.
        4. Formats and returns the final `AgentResult`.

        Args:
            command (str): The natural language command string from the client.

        Returns:
            Dict[str, Any]: A dictionary representing the final result of the
                            command execution, conforming to the AgentResult
                            structure (e.g., {'status': 'success', 'result': ...} or
                            {'status': 'error', 'message': ...}).
        """
        pass

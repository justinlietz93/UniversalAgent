# Core UniversalAgent class implementation
import logging
from typing import Dict, Any

from ..interfaces.i_universal_agent import IUniversalAgent
from ..interfaces.i_router import IRouter
from ..interfaces.types import AgentResult, ToolResult, AgentRequest
from ..utils.nlp_parser import NlpParser

# Configure logging
logger = logging.getLogger(__name__)

class UniversalAgent(IUniversalAgent):
    """
    The main orchestrator for the Universal Agent framework.
    It takes natural language commands, uses an NLP parser to understand them,
    routes them to the appropriate tool via a Router, and returns the result.
    """

    def __init__(self, router: IRouter, nlp_parser: NlpParser):
        """
        Initializes the UniversalAgent.

        Args:
            router (IRouter): An instance of the router component.
            # nlp_parser (NlpParser): An instance of the NLP parsing component.
        """
        if not isinstance(router, IRouter):
            raise TypeError("Router must implement the IRouter interface.")
        # if not isinstance(nlp_parser, NlpParser): # Add check later
        #     raise TypeError("NLP Parser must be a valid NlpParser instance.")

        self._router = router
        self._nlp_parser = nlp_parser
        logger.info("UniversalAgent initialized.")

    async def execute(self, command: str) -> Dict[str, Any]:
        """
        Processes a natural language command asynchronously.

        Orchestrates NLP parsing, routing, tool execution, and result formatting.

        Args:
            command (str): The natural language command string from the client.

        Returns:
            Dict[str, Any]: A dictionary conforming to the AgentResult structure.
        """
        logger.info(f"Received command: '{command}'")
        try:
            # Step 1: Parse command using NLP (To be implemented in Task 3.2/3.3)
            # agent_request_dict = await self._nlp_parser.parse(command)
            # logger.debug(f"NLP parsing result: {agent_request_dict}")
            # agent_request = AgentRequest.model_validate(agent_request_dict) # Validate structure

            # Placeholder for AgentRequest until NLP is implemented
            logger.warning("NLP parsing not yet implemented. Using placeholder request.")
            # Example placeholder - this will need to be replaced by actual NLP output
            if "read file" in command:
                 placeholder_request = {"tool_id": "file_reader", "params": {"path": command.split("'")[1] if "'" in command else "unknown"}}
            else:
                 placeholder_request = {"tool_id": "unknown_tool", "params": {"original_command": command}}


            # Step 2: Route request (Using placeholder request for now)
            # tool_result_dict = await self._router.route_request(agent_request.model_dump())
            tool_result_dict = await self._router.route_request(placeholder_request) # Using placeholder
            tool_result = ToolResult.model_validate(tool_result_dict) # Validate structure

            # Step 3: Format final AgentResult
            if tool_result.success:
                agent_result = AgentResult(status="success", result=tool_result.data, message="Command executed successfully.")
            else:
                # Distinguish between tool failure and tool not found if possible
                if "Tool with ID" in (tool_result.error or "") and "not found" in (tool_result.error or ""):
                     agent_result = AgentResult(status="tool_not_found", result=None, message=tool_result.error)
                else:
                     agent_result = AgentResult(status="error", result=None, message=f"Tool execution failed: {tool_result.error}")

            logger.info(f"Command execution finished. Status: {agent_result.status}")
            return agent_result.model_dump()

        except Exception as e:
            logger.exception(f"Critical error during command execution: {command}")
            # General error during parsing, routing, or result formatting
            agent_result = AgentResult(status="error", result=None, message=f"An unexpected error occurred in the agent: {str(e)}")
            return agent_result.model_dump()

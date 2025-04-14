# NLP Parser implementation using Hugging Face Transformers
import logging
from typing import Dict, Any
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Configure logging
logger = logging.getLogger(__name__)

class NlpParser:
    """
    Handles natural language command parsing using a Transformer model.
    Currently configured for the 't5-base' model.
    """

    def __init__(self, model_name: str = 't5-base'):
        """
        Initializes the NLP parser by loading the specified Transformer model and tokenizer.

        Args:
            model_name (str): The name or path of the model to load (default: 't5-base').
        """
        try:
            self.tokenizer = T5Tokenizer.from_pretrained(model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(model_name)
            logger.info(f"Loaded NLP model and tokenizer: {model_name}")
        except Exception as e:
            logger.exception(f"Failed to load NLP model/tokenizer: {e}")
            raise

    async def parse(self, command: str) -> Dict[str, Any]:
        """
        Parses a natural language command into a structured AgentRequest.

        Args:
            command (str): The natural language command string.

        Returns:
            Dict[str, Any]: A dictionary representing the parsed AgentRequest.
                            Expected keys: 'tool_id', 'params'.
        """
        try:
            # Construct a prompt that guides the T5 model to generate a structured response
            # Using a format that explicitly asks for tool_id and parameters
            input_text = (
                f"Convert the following command into a structured format:\n"
                f"Command: '{command}'\n"
                f"Extract the tool and parameters in JSON format with 'tool_id' and 'params' keys."
            )

            # Tokenize input with appropriate padding
            inputs = self.tokenizer(input_text, return_tensors='pt', padding=True, truncation=True, max_length=512)

            # Generate output using the model with better generation parameters
            output = self.model.generate(
                **inputs, 
                max_length=100,
                num_beams=4,
                early_stopping=True,
                temperature=0.7,
                no_repeat_ngram_size=2
            )

            # Decode the generated output
            generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            logger.debug(f"Generated text from T5 model: {generated_text}")

            # Parse the generated text into AgentRequest format
            import json
            import re

            # Try to extract JSON directly if it exists in the output
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            
            if json_match:
                try:
                    # Try to parse the extracted JSON
                    json_str = json_match.group(0)
                    agent_request = json.loads(json_str)
                    
                    # Validate that it has the required keys
                    if 'tool_id' not in agent_request:
                        logger.warning("Generated JSON missing 'tool_id' key, adding fallback")
                        agent_request['tool_id'] = self._extract_tool_id(command)
                    
                    if 'params' not in agent_request:
                        logger.warning("Generated JSON missing 'params' key, adding empty dict")
                        agent_request['params'] = {}
                    
                    logger.info(f"Successfully parsed command into AgentRequest: {agent_request}")
                    return agent_request
                
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse generated text into JSON: {e}")
            
            # Fallback: Extract information using heuristics
            logger.warning("Falling back to heuristic-based extraction")
            agent_request = self._fallback_parsing(command, generated_text)
            logger.info(f"Used fallback parsing to create AgentRequest: {agent_request}")
            return agent_request

        except Exception as e:
            logger.exception(f"Error during NLP parsing: {e}")
            # Fallback when everything else fails
            return self._emergency_fallback(command)
    
    def _extract_tool_id(self, command: str) -> str:
        """Extract a tool_id using simple heuristics."""
        # Simple heuristic-based tool detection
        command_lower = command.lower()
        
        if "file" in command_lower and ("read" in command_lower or "open" in command_lower):
            return "file_reader"
        elif "file" in command_lower and ("write" in command_lower or "save" in command_lower or "create" in command_lower):
            return "file_writer"
        elif "run" in command_lower or "execute" in command_lower:
            return "code_runner"
        elif "search" in command_lower or "find" in command_lower:
            return "search_tool"
        elif "shell" in command_lower or "command" in command_lower:
            return "shell_tool"
        elif "install" in command_lower or "package" in command_lower:
            return "package_manager"
        elif "browser" in command_lower or "web" in command_lower:
            return "web_browser"
        else:
            return "unknown_tool"
    
    def _extract_parameters(self, command: str) -> Dict[str, Any]:
        """Extract parameters using simple heuristics."""
        params = {}
        
        # Try to extract filenames
        import re
        file_match = re.search(r"['\"](.*?)['\"]", command)
        if file_match:
            params["path"] = file_match.group(1)
        
        # Extract code snippets if present (between backticks or triple backticks)
        code_match = re.search(r"```(.*?)```", command, re.DOTALL)
        if code_match:
            params["code"] = code_match.group(1).strip()
        else:
            code_match = re.search(r"`(.*?)`", command)
            if code_match:
                params["code"] = code_match.group(1).strip()
        
        # Add original command as a fallback
        params["original_command"] = command
        
        return params
    
    def _fallback_parsing(self, command: str, generated_text: str) -> Dict[str, Any]:
        """Fallback method when JSON parsing fails."""
        tool_id = self._extract_tool_id(command)
        params = self._extract_parameters(command)
        
        # Try to extract more information from the generated text
        # This could be improved based on the actual output patterns of the model
        if "tool" in generated_text and ":" in generated_text:
            tool_section = generated_text.split("tool:")[1].split("\n")[0].strip()
            if tool_section and not tool_section.startswith("{"):
                tool_id = tool_section
        
        return {
            "tool_id": tool_id,
            "params": params
        }
    
    def _emergency_fallback(self, command: str) -> Dict[str, Any]:
        """Last resort fallback when all else fails."""
        logger.error(f"Emergency fallback for command: {command}")
        
        # Use very basic extraction
        tool_id = self._extract_tool_id(command)
        
        return {
            "tool_id": tool_id,
            "params": {"original_command": command}
        }

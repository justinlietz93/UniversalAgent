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
            # Preprocess command if needed (e.g., lowercasing)
            input_text = f"parse command: {command.lower()}"

            # Tokenize input
            inputs = self.tokenizer(input_text, return_tensors='pt')

            # Generate output using the model
            output = self.model.generate(**inputs, max_length=50)

            # Decode the generated output
            generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)

            # Parse the generated text into AgentRequest format
            # For simplicity, assume the model generates JSON directly
            # In practice, you might need more sophisticated parsing/error handling
            import json
            try:
                agent_request = json.loads(generated_text)
                logger.debug(f"Parsed AgentRequest: {agent_request}")
                return agent_request
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse generated text into JSON: {e}")
                # Handle or re-raise as appropriate
                raise

        except Exception as e:
            logger.exception(f"Error during NLP parsing: {e}")
            # Handle or re-raise as appropriate
            raise

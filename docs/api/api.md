# Universal Agent API Reference

This document provides a comprehensive reference for the Universal Agent API.

## Core Classes

### UniversalAgent

The main class for interacting with LLMs and tools.

```python
class UniversalAgent:
    def __init__(
        self, 
        provider: str,
        credentials: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Universal Agent.
        
        Args:
            provider: The LLM provider name (e.g., 'openai', 'gemini')
            credentials: Authentication credentials dictionary (e.g., {"api_key": "..."})
            config: Optional configuration dictionary which may include:
                   - model: The model to use (e.g., "gpt-4")
                   - temperature: Sampling temperature (0.0-1.0)
                   - system_prompt: The system prompt to use
                   - max_tokens: Maximum tokens in the response
        """
        pass
        
    async def generate_response(
        self, 
        prompt: str,
        tools: Optional[List[str]] = None
    ) -> str:
        """
        Generate a response from the LLM with optional tool use.
        
        Args:
            prompt: The user prompt
            tools: Optional list of tool names to make available for this request
            
        Returns:
            The LLM response as a string
        """
        pass
    
    async def generate_streaming_response(
        self, 
        prompt: str,
        tools: Optional[List[str]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the LLM with optional tool use.
        
        Args:
            prompt: The user prompt
            tools: Optional list of tool names to make available for this request
            
        Returns:
            An async generator yielding response chunks
        """
        pass
        
    def register_tool(self, name: str, tool: BaseTool) -> None:
        """
        Register a tool for use with the agent.
        
        Args:
            name: The tool name
            tool: The tool instance
        """
        pass
        
    @contextmanager
    def register_tool(self, tool_class: Type) -> None:
        """
        Register a tool for use with the agent using a decorator.
        
        Args:
            tool_class: The tool class to register
        """
        pass
        
    def set_system_prompt(self, prompt: str) -> None:
        """
        Set the system prompt for the agent.
        
        Args:
            prompt: The system prompt to use
        """
        pass
```

### BaseTool

The base class for all tools.

```python
class BaseTool(abc.ABC):
    def __init__(self):
        """
        Initialize the base tool.
        """
        self._name = None
        self._description = None
        self._input_schema = None
        self._output_schema = None
    
    @property
    def name(self) -> str:
        """Get the tool name."""
        pass
    
    @property
    def description(self) -> str:
        """Get the tool description."""
        pass
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        """Get the tool input schema as a JSON Schema object."""
        pass
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        """Get the tool output schema as a JSON Schema object."""
        pass
    
    @abc.abstractmethod
    async def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the tool.
        
        Args:
            **kwargs: Tool input parameters
            
        Returns:
            Tool output as a dictionary
        """
        pass
```

## Provider Adapters

### LLMAdapterFactory

Factory for creating LLM provider adapters.

```python
class LLMAdapterFactory:
    def __init__(self):
        """Initialize the LLM adapter factory."""
        pass
    
    def _register_adapter(self, provider: str, adapter_class: Type[BaseLLMAdapter]) -> None:
        """
        Register an adapter class for a provider.
        
        Args:
            provider: The provider name
            adapter_class: The adapter class
        """
        pass
    
    async def create_adapter(
        self, 
        provider: str, 
        credentials: Dict[str, Any], 
        config: Optional[Dict[str, Any]] = None
    ) -> BaseLLMAdapter:
        """
        Create an LLM adapter for the specified provider.
        
        Args:
            provider: The LLM provider
            credentials: Dictionary of credentials for the provider
            config: Optional configuration dictionary
            
        Returns:
            An LLM adapter for the provider
        """
        pass
```

### BaseLLMAdapter

Base class for all LLM provider adapters.

```python
class BaseLLMAdapter(abc.ABC):
    def __init__(
        self, 
        provider: str,
        credentials: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        tool_capabilities: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the LLM adapter.
        
        Args:
            provider: The LLM provider name
            credentials: Authentication credentials for the LLM provider
            config: Optional configuration parameters
            capabilities: Optional provider capabilities
            tool_capabilities: Optional tool calling capabilities
        """
        pass
    
    @abc.abstractmethod
    async def generate_response(
        self, 
        prompt: str,
        tool_descriptions: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt for the LLM
            tool_descriptions: List of tool descriptions
            
        Returns:
            The response from the LLM
        """
        pass
    
    @abc.abstractmethod
    async def extract_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract a tool call from the LLM response.
        
        Args:
            response: The response from the LLM
            
        Returns:
            A dictionary containing the tool call information, or None if no tool call is found
        """
        pass
    
    @abc.abstractmethod
    async def process_tool_result(
        self, 
        prompt: str,
        response: str,
        tool_call: Dict[str, Any],
        tool_result: Dict[str, Any]
    ) -> str:
        """
        Process the result of a tool execution with the LLM.
        
        Args:
            prompt: The original input prompt
            response: The original LLM response
            tool_call: The tool call information
            tool_result: The result of the tool execution
            
        Returns:
            The final response from the LLM
        """
        pass
    
    @abc.abstractmethod
    async def generate_streaming_response(
        self, 
        prompt: str,
        tool_descriptions: List[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the LLM.
        
        Args:
            prompt: The input prompt for the LLM
            tool_descriptions: List of tool descriptions
            
        Returns:
            A stream of response chunks from the LLM
        """
        pass
```

## Streaming Support

### StreamingManager

Manager for streaming responses.

```python
class StreamingManager:
    def __init__(self):
        """Initialize the streaming manager."""
        pass
    
    async def process_streaming_response(
        self, 
        stream: AsyncGenerator[str, None],
        on_tool_call: Optional[callable] = None
    ) -> AsyncGenerator[str, None]:
        """
        Process a streaming response.
        
        Args:
            stream: The streaming response
            on_tool_call: Optional callback for when a tool call is detected
            
        Returns:
            An async generator yielding processed chunks
        """
        pass
    
    def get_detected_tool_call(self) -> Optional[Dict[str, Any]]:
        """
        Get the detected tool call.
        
        Returns:
            The detected tool call or None if not found
        """
        pass
```

## Documentation Analysis

### DocumentationAnalyzer

Analyzer for LLM provider documentation.

```python
class DocumentationAnalyzer:
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the documentation analyzer.
        
        Args:
            cache_dir: Optional directory for caching documentation
        """
        pass
    
    async def retrieve_documentation(self, provider: str) -> str:
        """
        Retrieve documentation for a provider.
        
        Args:
            provider: The provider name (e.g., 'gemini', 'openai')
            
        Returns:
            The documentation content as a string
        """
        pass
    
    async def analyze_capabilities(self, provider: str, documentation: str) -> Dict[str, Any]:
        """
        Analyze provider capabilities from documentation.
        
        Args:
            provider: The provider name
            documentation: The documentation content
            
        Returns:
            A dictionary of provider capabilities
        """
        pass
    
    async def determine_tool_calling_capabilities(self, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine tool calling capabilities.
        
        Args:
            capabilities: Provider capabilities
            
        Returns:
            Tool calling capabilities
        """
        pass

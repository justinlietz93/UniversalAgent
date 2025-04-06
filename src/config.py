"""
Universal Agent Configuration

This module contains all configuration values for the Universal Agent, including:
- Provider documentation sources
- Authentication configurations
- Tool capabilities
- Regex patterns
- Tool format mappings
- Default values and limits
"""
import os
from typing import Dict, Any

# Import environment variable loader
from src.env_loader import (
    get_env, get_env_bool, get_env_int, get_env_float, 
    get_env_list, get_credential, get_all_credentials
)

#################################################
# Provider Documentation Sources
#################################################
PROVIDER_DOCS = {
    "gemini": {
        "api_docs": "https://ai.google.dev/api/rest/v1beta",
        "function_calling_docs": "https://ai.google.dev/docs/function_calling",
        "github_repo": "https://github.com/google/generative-ai-docs"
    },
    "openai": {
        "api_docs": "https://platform.openai.com/docs/api-reference",
        "function_calling_docs": "https://platform.openai.com/docs/guides/function-calling",
        "github_repo": "https://github.com/openai/openai-openapi",
        "openapi_spec": "https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml"
    },
    "anthropic": {
        "api_docs": "https://docs.anthropic.com/claude/reference/getting-started-with-the-api",
        "function_calling_docs": "https://docs.anthropic.com/claude/docs/tool-use",
        "github_repo": "https://github.com/anthropics/anthropic-sdk-python"
    },
    "mistral": {
        "api_docs": "https://docs.mistral.ai/api/",
        "function_calling_docs": "https://docs.mistral.ai/guides/function-calling/",
        "github_repo": "https://github.com/mistralai/client-python"
    }
}

# Documentation section headers
DOC_SECTION_HEADERS = {
    "api": "API DOCUMENTATION:",
    "function_calling": "FUNCTION CALLING DOCUMENTATION:",
    "openapi": "OPENAPI SPECIFICATION:"
}

#################################################
# Authentication Configuration
#################################################
AUTH_CONFIG = {
    "default": {
        "method": "api_key",
        "header": "Authorization",
        "prefix": "",
    },
    "gemini": {
        "method": "api_key",
        "header": "x-goog-api-key",
        "prefix": "",
    },
    "openai": {
        "method": "api_key",
        "header": "Authorization",
        "prefix": "Bearer ",
    },
    "anthropic": {
        "method": "api_key",
        "header": "x-api-key",
        "prefix": "",
    },
    "mistral": {
        "method": "api_key",
        "header": "Authorization",
        "prefix": "Bearer ",
    }
}

#################################################
# Tool Capability Configuration
#################################################
TOOL_CAPABILITIES = {
    "default": {
        "schema_format": "json_schema",
        "maximum_tools": 10,
        "supports_multiple_calls": False
    },
    "openai": {
        "schema_format": "openai_functions",
        "maximum_tools": 128,
        "supports_multiple_calls": True
    },
    "gemini": {
        "schema_format": "google_functions",
        "maximum_tools": 64,
        "supports_multiple_calls": False
    },
    "anthropic": {
        "schema_format": "anthropic_tools",
        "maximum_tools": 16,
        "supports_multiple_calls": False
    },
    "mistral": {
        "schema_format": "json_schema",
        "maximum_tools": 32,
        "supports_multiple_calls": False
    }
}

#################################################
# Regex Patterns
#################################################
REGEX_PATTERNS = {
    # Model extraction patterns for each provider
    "model_extraction": {
        "gemini": r"gemini-([\w-]+)",
        "openai": r"gpt-([\w-]+)",
        "anthropic": r"claude-([\w-]+)",
        "mistral": r"mistral-([\w-]+)",
        "generic": r"model[\s\-_]?([\w\-]+)"
    },
    
    # Tool call detection patterns
    "tool_call": {
        "start": r'(```json|\{\"tool\"|\"function_call\"|\"tool_calls\"|<tool>)',
        "end": r'(```|\}\"|\}\]\}|\}\}|</tool>)'
    },
    
    # JSON extraction patterns
    "json_extraction": {
        "json_block": r'```json\s*(.*?)\s*```',
        "openai_function": r'\"function_call\"\s*:\s*\{(.*?)\}',
        "gemini_tool_calls": r'\"tool_calls\"\s*:\s*\[(.*?)\]',
        "xml_tool": r'<tool>(.*?)</tool>'
    }
}

#################################################
# Tool Format Mappings
#################################################
TOOL_FORMAT_MAPPINGS = {
    "openai_function_calling": "openai",
    "google_function_calling": "gemini",
    "anthropic_tool_use": "anthropic",
    "mistral_function_calling": "mistral"
}

#################################################
# Adapter Registrations
#################################################
ADAPTER_REGISTRATIONS = [
    ("gemini", "GeminiAdapter"),
    ("openai", "OpenAIAdapter"),
    ("anthropic", "AnthropicAdapter"),
    ("mistral", "MistralAdapter"),
    ("generic", "GenericAdapter")
]

#################################################
# API Endpoints and Defaults
#################################################
API_ENDPOINTS = {
    "search": {
        # Google Custom Search API
        "url": "https://www.googleapis.com/customsearch/v1",
        "params": {
            "default_num_results": get_env_int("SEARCH_DEFAULT_RESULTS", 3),
            "max_results": get_env_int("SEARCH_MAX_RESULTS", 10)
        },
        "required_credentials": ["api_key", "cx"],
        "docs_url": "https://developers.google.com/custom-search/v1/introduction"
    },
    # Add other API endpoints here
}

#################################################
# Security Settings
#################################################
SECURITY = {
    "sensitive_keys": ["password", "api_key", "secret", "token", "credentials"],
    "safe_eval_globals": {
        "__builtins__": {}
    },
    "safe_eval_locals": {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "len": len
    }
}

#################################################
# Default Values
#################################################
DEFAULTS = {
    "system_prompt": "You are a helpful AI assistant.",
    "temperature": 0.7,
    "max_tokens": 4096,
    "cache_dir": os.path.join(os.path.expanduser("~"), ".universal_agent", "cache")
}

#################################################
# Helper Functions
#################################################
def get_provider_config(provider: str, config_type: str) -> Dict[str, Any]:
    """
    Get provider-specific configuration with fallback to defaults.
    
    Args:
        provider: The provider name
        config_type: The type of configuration to get
        
    Returns:
        The provider-specific configuration
        
    Raises:
        ValueError: If the config_type is unknown
    """
    config_map = {
        "auth": AUTH_CONFIG,
        "tool_capabilities": TOOL_CAPABILITIES,
        "docs": PROVIDER_DOCS,
        "regex": REGEX_PATTERNS
    }
    
    if config_type not in config_map:
        raise ValueError(f"Unknown config type: {config_type}")
    
    config = config_map[config_type]
    provider = provider.lower()
    
    # Regex patterns are nested differently
    if config_type == "regex":
        # Return specific regex pattern category if it exists
        for category, patterns in config.items():
            if provider in patterns:
                return patterns[provider]
        # Return first generic pattern if available
        for category, patterns in config.items():
            if "generic" in patterns:
                return patterns["generic"]
        return {}
    
    return config.get(provider, config.get("default", {}))

def get_adapter_class_name(provider: str) -> str:
    """
    Get the adapter class name for a provider.
    
    Args:
        provider: The provider name
        
    Returns:
        The adapter class name
    """
    provider = provider.lower()
    
    # Check direct mappings
    for p, class_name in ADAPTER_REGISTRATIONS:
        if p == provider:
            return class_name
    
    # Check tool format mappings
    if provider in TOOL_FORMAT_MAPPINGS:
        mapped_provider = TOOL_FORMAT_MAPPINGS[provider]
        for p, class_name in ADAPTER_REGISTRATIONS:
            if p == mapped_provider:
                return class_name
    
    # Default to generic adapter
    return "GenericAdapter"

"""
Environment variable loader for the Universal LLM Tool Wrapper Interface.

This module provides functions for loading environment variables and .env files.
"""
import os
import logging
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)

def get_env(name: str, default: Any = None) -> Optional[str]:
    """
    Get an environment variable with optional default value.
    
    Args:
        name: Environment variable name
        default: Default value if environment variable is not set
        
    Returns:
        Environment variable value or default
    """
    return os.environ.get(name, default)

def get_env_bool(name: str, default: bool = False) -> bool:
    """
    Get a boolean environment variable.
    
    Args:
        name: Environment variable name
        default: Default value if environment variable is not set
        
    Returns:
        Boolean value of environment variable
    """
    value = get_env(name)
    if value is None:
        return default
    return value.lower() in ('true', 'yes', '1', 't', 'y')

def get_env_int(name: str, default: Optional[int] = None) -> Optional[int]:
    """
    Get an integer environment variable.
    
    Args:
        name: Environment variable name
        default: Default value if environment variable is not set
        
    Returns:
        Integer value of environment variable
    """
    value = get_env(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(f"Environment variable {name} is not a valid integer: {value}")
        return default

def get_env_float(name: str, default: Optional[float] = None) -> Optional[float]:
    """
    Get a float environment variable.
    
    Args:
        name: Environment variable name
        default: Default value if environment variable is not set
        
    Returns:
        Float value of environment variable
    """
    value = get_env(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        logger.warning(f"Environment variable {name} is not a valid float: {value}")
        return default

def get_env_list(name: str, separator: str = ',', default: Optional[list] = None) -> Optional[list]:
    """
    Get a list environment variable.
    
    Args:
        name: Environment variable name
        separator: Separator for list items
        default: Default value if environment variable is not set
        
    Returns:
        List value of environment variable
    """
    value = get_env(name)
    if value is None:
        return default or []
    # Handle empty string case explicitly
    if not value:
        return []
    return [item.strip() for item in value.split(separator)]

def load_dotenv(path: Optional[str] = None) -> bool:
    """
    Load environment variables from .env file.
    
    Args:
        path: Path to .env file, or None to use default locations
        
    Returns:
        True if .env file was loaded, False otherwise
    """
    try:
        # Try to import python-dotenv
        try:
            from dotenv import load_dotenv as dotenv_load
            logger.debug("Using python-dotenv for .env file loading")
        except ImportError:
            logger.warning("python-dotenv not installed, skipping .env file loading")
            return False
        
        # Load .env file
        loaded = dotenv_load(dotenv_path=path)
        if loaded:
            logger.info(f"Loaded environment variables from {path or '.env'}")
        else:
            logger.warning(f"No .env file found at {path or 'default locations'}")
        
        return loaded
    except Exception as e:
        logger.error(f"Error loading .env file: {str(e)}")
        return False

def get_credential(provider: str, credential_name: str, default: Any = None) -> Any:
    """
    Get a credential for a provider.
    
    Args:
        provider: Provider name (e.g., 'openai', 'gemini')
        credential_name: Credential name (e.g., 'api_key')
        default: Default value if credential is not set
        
    Returns:
        Credential value or default
    """
    # Normalize provider name
    provider = provider.lower().replace('-', '_')
    
    # Try provider-specific environment variable
    env_var = f"{provider.upper()}_{credential_name.upper()}"
    value = get_env(env_var)
    if value is not None:
        logger.debug(f"Found credential {credential_name} for provider {provider} in environment variable {env_var}")
        return value
    
    # Try generic environment variable
    env_var = f"UNIVERSAL_AGENT_{provider.upper()}_{credential_name.upper()}"
    value = get_env(env_var)
    if value is not None:
        logger.debug(f"Found credential {credential_name} for provider {provider} in environment variable {env_var}")
        return value
    
    return default

def get_all_credentials(provider: str) -> Dict[str, Any]:
    """
    Get all credentials for a provider.
    
    Args:
        provider: Provider name (e.g., 'openai', 'gemini')
        
    Returns:
        Dictionary of credentials
    """
    # Normalize provider name
    provider = provider.lower().replace('-', '_')
    provider_upper = provider.upper()
    
    # Get all environment variables
    credentials = {}
    
    # Check provider-specific environment variables
    prefix = f"{provider_upper}_"
    prefix_len = len(prefix)
    for key, value in os.environ.items():
        if key.startswith(prefix):
            credential_name = key[prefix_len:].lower()
            credentials[credential_name] = value
    
    # Check generic environment variables
    prefix = f"UNIVERSAL_AGENT_{provider_upper}_"
    prefix_len = len(prefix)
    for key, value in os.environ.items():
        if key.startswith(prefix):
            credential_name = key[prefix_len:].lower()
            if credential_name not in credentials:
                credentials[credential_name] = value
    
    return credentials

# Try to load .env file on import
load_dotenv()

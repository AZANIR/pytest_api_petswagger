"""Configuration settings for API tests with cross-environment support."""
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment files."""
    
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # API Configuration
    base_url: str = Field(
        default="https://petstore.swagger.io/v2",
        description="Base URL for the API"
    )
    api_key: str = Field(
        default="special-key",
        description="API key for authentication"
    )
    
    # Request Configuration
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="DEBUG",
        description="Logging level"
    )
    
    # Environment name
    env_name: str = Field(
        default="dev",
        description="Current environment name"
    )


def get_env_file_path(env_name: str) -> Optional[Path]:
    """Get path to environment file."""
    env_dir = Path(__file__).parent / "environments"
    env_file = env_dir / f"{env_name}.env"
    
    if env_file.exists():
        return env_file
    return None


@lru_cache()
def get_settings(env_name: str = "dev") -> Settings:
    """
    Get cached settings instance for the specified environment.
    
    Args:
        env_name: Environment name (dev, staging, prod)
        
    Returns:
        Settings instance with loaded configuration
    """
    env_file = get_env_file_path(env_name)
    
    if env_file:
        return Settings(_env_file=env_file, env_name=env_name)
    
    return Settings(env_name=env_name)


# Global settings instance - will be set by conftest.py
_current_settings: Optional[Settings] = None


def set_current_settings(settings: Settings) -> None:
    """Set the current settings instance."""
    global _current_settings
    _current_settings = settings


def get_current_settings() -> Settings:
    """Get the current settings instance."""
    global _current_settings
    if _current_settings is None:
        _current_settings = get_settings()
    return _current_settings


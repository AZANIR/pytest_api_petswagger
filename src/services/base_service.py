"""Base service class for API endpoints."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.http import BaseHTTPClient


class BaseService:
    """
    Base class for API service endpoints.
    
    All service classes should inherit from this class
    and use self._client for making HTTP requests.
    """
    
    def __init__(self, client: "BaseHTTPClient"):
        """
        Initialize the service.
        
        Args:
            client: HTTP client instance for making requests
        """
        self._client = client


"""Base HTTP client with session management and schema validation."""
import json
import logging
from typing import Optional
from pathlib import Path

import requests
from requests import Response

from config.settings import get_current_settings
from src.schema_validator import get_schema_validator, SwaggerSchemaValidator
from .methods import HTTPMethods


logger = logging.getLogger(__name__)


class BaseHTTPClient(HTTPMethods):
    """
    Base HTTP client with built-in logging and schema validation.
    
    Inherits HTTP methods (GET, POST, PUT, DELETE, PATCH) from HTTPMethods.
    Adds session management and optional schema validation.
    
    Usage:
        client = BaseHTTPClient()
        response = client.get("/endpoint")
        response = client.post("/endpoint", json={"key": "value"})
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
        validate_schemas: bool = True
    ):
        """
        Initialize the HTTP client.
        
        Args:
            base_url: API base URL (uses settings if not provided)
            api_key: API key for authentication (uses settings if not provided)
            timeout: Request timeout in seconds (uses settings if not provided)
            validate_schemas: Whether to validate responses against Swagger schemas
        """
        settings = get_current_settings()
        
        self.base_url = base_url or settings.base_url
        self.api_key = api_key or settings.api_key
        self.timeout = timeout or settings.timeout
        self.validate_schemas = validate_schemas
        
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "api_key": self.api_key
        })
        
        # Initialize schema validator
        self._schema_validator: Optional[SwaggerSchemaValidator] = None
        if validate_schemas:
            try:
                swagger_path = Path(__file__).parent.parent.parent / "schemas" / "swagger.json"
                self._schema_validator = get_schema_validator(swagger_path)
            except Exception as e:
                logger.warning(f"Could not initialize schema validator: {e}")
        
        logger.info(f"HTTP Client initialized with base URL: {self.base_url}")
    
    def _validate_response_schema(
        self,
        response: Response,
        path: str,
        method: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate response against Swagger schema.
        
        Args:
            response: Response object
            path: API path (e.g., "/pet/{petId}")
            method: HTTP method
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self._schema_validator or not self.validate_schemas:
            return True, None
        
        try:
            response_data = response.json()
        except (json.JSONDecodeError, ValueError):
            return True, None
        
        return self._schema_validator.validate_response(
            response_data, path, method, response.status_code
        )
    
    def request(
        self,
        method: str,
        endpoint: str,
        path_template: Optional[str] = None,
        validate_schema: bool = True,
        **kwargs
    ) -> Response:
        """
        Make an HTTP request with optional schema validation.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., "/pet/1")
            path_template: Swagger path template for schema validation
            validate_schema: Whether to validate response schema
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Response object
        """
        response = self._make_request(method, endpoint, **kwargs)
        
        # Validate response schema if enabled
        if validate_schema and path_template:
            is_valid, error = self._validate_response_schema(
                response, path_template, method
            )
            if not is_valid:
                logger.warning(f"Schema validation failed: {error}")
        
        return response
    
    def get(self, endpoint: str, path_template: Optional[str] = None, **kwargs) -> Response:
        """Make a GET request with schema validation."""
        return self.request("GET", endpoint, path_template, **kwargs)
    
    def post(self, endpoint: str, path_template: Optional[str] = None, **kwargs) -> Response:
        """Make a POST request with schema validation."""
        return self.request("POST", endpoint, path_template, **kwargs)
    
    def put(self, endpoint: str, path_template: Optional[str] = None, **kwargs) -> Response:
        """Make a PUT request with schema validation."""
        return self.request("PUT", endpoint, path_template, **kwargs)
    
    def delete(self, endpoint: str, path_template: Optional[str] = None, **kwargs) -> Response:
        """Make a DELETE request with schema validation."""
        return self.request("DELETE", endpoint, path_template, **kwargs)
    
    def patch(self, endpoint: str, path_template: Optional[str] = None, **kwargs) -> Response:
        """Make a PATCH request with schema validation."""
        return self.request("PATCH", endpoint, path_template, **kwargs)
    
    def close(self) -> None:
        """Close the session."""
        self._session.close()
        logger.info("HTTP Client session closed")
    
    def __enter__(self) -> "BaseHTTPClient":
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


"""HTTP methods mixin class."""
import json
import logging
from typing import Optional

from requests import Response, Session


logger = logging.getLogger(__name__)


class HTTPMethods:
    """
    Mixin class providing HTTP methods (GET, POST, PUT, DELETE, PATCH).
    
    This class should be used as a mixin or base class for HTTP clients.
    Requires self._session (requests.Session) and self.base_url to be set.
    """
    
    _session: Session
    base_url: str
    timeout: int
    
    def _log_request(self, method: str, url: str, **kwargs) -> None:
        """Log outgoing request details."""
        logger.info(f">>> {method.upper()} {url}")
        
        if "params" in kwargs and kwargs["params"]:
            logger.debug(f"    Query params: {kwargs['params']}")
        
        if "json" in kwargs and kwargs["json"]:
            logger.debug(f"    Request body: {json.dumps(kwargs['json'], indent=2)}")
        
        if "data" in kwargs and kwargs["data"]:
            logger.debug(f"    Form data: {kwargs['data']}")
    
    def _log_response(self, response: Response) -> None:
        """Log incoming response details."""
        logger.info(f"<<< {response.status_code} {response.reason} ({response.elapsed.total_seconds():.3f}s)")
        
        try:
            if response.content:
                response_body = response.json()
                logger.debug(f"    Response body: {json.dumps(response_body, indent=2)}")
        except (json.JSONDecodeError, ValueError):
            if response.text:
                logger.debug(f"    Response text: {response.text[:500]}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Response:
        """
        Make an HTTP request (internal method without validation).
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint (e.g., "/pet/1")
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Response object
        """
        # Remove path_template from kwargs - it's not a requests parameter
        kwargs.pop("path_template", None)
        
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", self.timeout)
        
        self._log_request(method, url, **kwargs)
        
        response = self._session.request(method, url, **kwargs)
        
        self._log_response(response)
        
        return response
    
    def get(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        **kwargs
    ) -> Response:
        """
        Make a GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def post(
        self,
        endpoint: str,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs
    ) -> Response:
        """
        Make a POST request.
        
        Args:
            endpoint: API endpoint
            json: JSON body data
            data: Form data
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return self._make_request("POST", endpoint, json=json, data=data, **kwargs)
    
    def put(
        self,
        endpoint: str,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs
    ) -> Response:
        """
        Make a PUT request.
        
        Args:
            endpoint: API endpoint
            json: JSON body data
            data: Form data
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return self._make_request("PUT", endpoint, json=json, data=data, **kwargs)
    
    def delete(
        self,
        endpoint: str,
        **kwargs
    ) -> Response:
        """
        Make a DELETE request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return self._make_request("DELETE", endpoint, **kwargs)
    
    def patch(
        self,
        endpoint: str,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs
    ) -> Response:
        """
        Make a PATCH request.
        
        Args:
            endpoint: API endpoint
            json: JSON body data
            data: Form data
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return self._make_request("PATCH", endpoint, json=json, data=data, **kwargs)


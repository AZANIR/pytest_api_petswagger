"""Schema validator for extracting and validating schemas from Swagger/OpenAPI specification."""
import json
import logging
import copy
from pathlib import Path
from typing import Any, Dict, Optional, Union

from jsonschema import Draft4Validator, ValidationError
from jsonschema.exceptions import SchemaError

logger = logging.getLogger(__name__)


class SwaggerSchemaValidator:
    """
    Validator for extracting schemas from Swagger 2.0 specification
    and validating API responses against them.
    """
    
    def __init__(self, swagger_path: Union[str, Path]):
        """
        Initialize the validator with a Swagger specification file.
        
        Args:
            swagger_path: Path to the swagger.json file
        """
        self.swagger_path = Path(swagger_path)
        self._spec: Optional[Dict[str, Any]] = None
        self._load_spec()
    
    def _load_spec(self) -> None:
        """Load and parse the Swagger specification file."""
        logger.debug(f"Loading Swagger spec from: {self.swagger_path}")
        
        if not self.swagger_path.exists():
            raise FileNotFoundError(f"Swagger file not found: {self.swagger_path}")
        
        with open(self.swagger_path, "r", encoding="utf-8") as f:
            self._spec = json.load(f)
        
        logger.info(f"Loaded Swagger spec: {self._spec.get('info', {}).get('title', 'Unknown')}")
    
    @property
    def spec(self) -> Dict[str, Any]:
        """Get the loaded Swagger specification."""
        if self._spec is None:
            raise RuntimeError("Swagger specification not loaded")
        return self._spec
    
    @property
    def definitions(self) -> Dict[str, Any]:
        """Get all model definitions from the spec."""
        return self.spec.get("definitions", {})
    
    @property
    def paths(self) -> Dict[str, Any]:
        """Get all paths from the spec."""
        return self.spec.get("paths", {})
    
    def _resolve_ref(self, ref: str) -> Dict[str, Any]:
        """
        Resolve a $ref reference to its actual schema.
        
        Args:
            ref: Reference string like "#/definitions/Pet"
            
        Returns:
            The resolved schema dictionary
        """
        if not ref.startswith("#/"):
            raise ValueError(f"Only local references are supported: {ref}")
        
        parts = ref[2:].split("/")
        schema = self.spec
        
        for part in parts:
            if part not in schema:
                raise KeyError(f"Reference not found: {ref}")
            schema = schema[part]
        
        return schema
    
    def _resolve_refs_recursively(self, schema: Dict[str, Any], visited: Optional[set] = None) -> Dict[str, Any]:
        """
        Recursively resolve all $ref references in a schema.
        
        Args:
            schema: Schema that may contain $ref references
            visited: Set of already visited refs to prevent infinite recursion
            
        Returns:
            Schema with all references resolved
        """
        if visited is None:
            visited = set()
        
        # Deep copy to avoid modifying the original
        schema = copy.deepcopy(schema)
        
        if isinstance(schema, dict):
            if "$ref" in schema:
                ref = schema["$ref"]
                
                # Prevent infinite recursion
                if ref in visited:
                    logger.warning(f"Circular reference detected: {ref}")
                    return schema
                
                visited.add(ref)
                resolved = self._resolve_ref(ref)
                return self._resolve_refs_recursively(resolved, visited)
            
            # Recursively resolve refs in nested structures
            for key, value in schema.items():
                if isinstance(value, dict):
                    schema[key] = self._resolve_refs_recursively(value, visited.copy())
                elif isinstance(value, list):
                    schema[key] = [
                        self._resolve_refs_recursively(item, visited.copy()) 
                        if isinstance(item, dict) else item
                        for item in value
                    ]
        
        return schema
    
    def get_definition_schema(self, name: str, resolve_refs: bool = True) -> Dict[str, Any]:
        """
        Get a model definition schema by name.
        
        Args:
            name: Name of the definition (e.g., "Pet", "Order", "User")
            resolve_refs: Whether to resolve $ref references
            
        Returns:
            The schema dictionary for the definition
        """
        if name not in self.definitions:
            raise KeyError(f"Definition not found: {name}")
        
        schema = self.definitions[name]
        
        if resolve_refs:
            schema = self._resolve_refs_recursively(schema)
        
        logger.debug(f"Retrieved definition schema for: {name}")
        return schema
    
    def get_response_schema(
        self, 
        path: str, 
        method: str, 
        status_code: Union[int, str] = 200,
        resolve_refs: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get the response schema for a specific endpoint.
        
        Args:
            path: API path (e.g., "/pet/{petId}")
            method: HTTP method (get, post, put, delete)
            status_code: Response status code
            resolve_refs: Whether to resolve $ref references
            
        Returns:
            The response schema or None if not defined
        """
        method = method.lower()
        status_code = str(status_code)
        
        if path not in self.paths:
            logger.warning(f"Path not found in spec: {path}")
            return None
        
        path_item = self.paths[path]
        
        if method not in path_item:
            logger.warning(f"Method {method} not found for path: {path}")
            return None
        
        operation = path_item[method]
        responses = operation.get("responses", {})
        
        # Try exact status code, then 'default'
        response = responses.get(status_code) or responses.get("default")
        
        if not response:
            logger.warning(f"Response {status_code} not found for {method.upper()} {path}")
            return None
        
        schema = response.get("schema")
        
        if schema and resolve_refs:
            schema = self._resolve_refs_recursively(schema)
        
        logger.debug(f"Retrieved response schema for: {method.upper()} {path} [{status_code}]")
        return schema
    
    def get_request_schema(
        self,
        path: str,
        method: str,
        resolve_refs: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get the request body schema for a specific endpoint.
        
        Args:
            path: API path (e.g., "/pet")
            method: HTTP method (post, put)
            resolve_refs: Whether to resolve $ref references
            
        Returns:
            The request body schema or None if not defined
        """
        method = method.lower()
        
        if path not in self.paths:
            logger.warning(f"Path not found in spec: {path}")
            return None
        
        path_item = self.paths[path]
        
        if method not in path_item:
            logger.warning(f"Method {method} not found for path: {path}")
            return None
        
        operation = path_item[method]
        parameters = operation.get("parameters", [])
        
        # Find body parameter
        for param in parameters:
            if param.get("in") == "body":
                schema = param.get("schema")
                if schema and resolve_refs:
                    schema = self._resolve_refs_recursively(schema)
                return schema
        
        return None
    
    def get_required_parameters(self, path: str, method: str) -> list:
        """
        Get list of required parameters for an endpoint.
        
        Args:
            path: API path
            method: HTTP method
            
        Returns:
            List of required parameter names
        """
        method = method.lower()
        
        if path not in self.paths:
            return []
        
        path_item = self.paths[path]
        
        if method not in path_item:
            return []
        
        operation = path_item[method]
        parameters = operation.get("parameters", [])
        
        required_params = [
            param["name"] 
            for param in parameters 
            if param.get("required", False)
        ]
        
        return required_params
    
    def validate(self, data: Any, schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate data against a JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema to validate against
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Use Draft4 for Swagger 2.0 compatibility
            validator = Draft4Validator(schema)
            errors = list(validator.iter_errors(data))
            
            if errors:
                error_messages = [
                    f"{'.'.join(str(p) for p in e.path)}: {e.message}" if e.path else e.message
                    for e in errors
                ]
                error_str = "; ".join(error_messages)
                logger.error(f"Schema validation failed: {error_str}")
                return False, error_str
            
            logger.debug("Schema validation passed")
            return True, None
            
        except SchemaError as e:
            logger.error(f"Invalid schema: {e.message}")
            return False, f"Invalid schema: {e.message}"
    
    def validate_response(
        self,
        response_data: Any,
        path: str,
        method: str,
        status_code: Union[int, str] = 200
    ) -> tuple[bool, Optional[str]]:
        """
        Validate API response data against the expected schema.
        
        Args:
            response_data: Response data to validate
            path: API path
            method: HTTP method
            status_code: Response status code
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        schema = self.get_response_schema(path, method, status_code)
        
        if schema is None:
            logger.warning(f"No schema defined for {method.upper()} {path} [{status_code}]")
            return True, None
        
        return self.validate(response_data, schema)
    
    def validate_request(
        self,
        request_data: Any,
        path: str,
        method: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate request body data against the expected schema.
        
        Args:
            request_data: Request body data to validate
            path: API path
            method: HTTP method
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        schema = self.get_request_schema(path, method)
        
        if schema is None:
            logger.warning(f"No request schema defined for {method.upper()} {path}")
            return True, None
        
        return self.validate(request_data, schema)


# Singleton instance
_validator_instance: Optional[SwaggerSchemaValidator] = None


def get_schema_validator(swagger_path: Optional[Union[str, Path]] = None) -> SwaggerSchemaValidator:
    """
    Get or create a schema validator instance.
    
    Args:
        swagger_path: Path to swagger.json (required on first call)
        
    Returns:
        SwaggerSchemaValidator instance
    """
    global _validator_instance
    
    if _validator_instance is None:
        if swagger_path is None:
            # Default path
            swagger_path = Path(__file__).parent.parent / "schemas" / "swagger.json"
        _validator_instance = SwaggerSchemaValidator(swagger_path)
    
    return _validator_instance


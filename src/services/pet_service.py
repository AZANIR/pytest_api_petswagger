"""Pet API service endpoints."""
from typing import Optional, Union

from requests import Response

from .base_service import BaseService


class PetService(BaseService):
    """
    Service class for Pet API endpoints.
    
    Provides methods for managing pets in the Petstore API.
    
    Usage:
        api = APIClient()
        api.pet.create(pet_data)
        api.pet.get_by_id(123)
        api.pet.find_by_status("available")
    """
    
    def create(self, pet_data: dict) -> Response:
        """
        Create a new pet.
        
        Args:
            pet_data: Pet data dictionary with required fields (name, photoUrls)
            
        Returns:
            Response object with created pet data
        """
        return self._client.post("/pet", path_template="/pet", json=pet_data)
    
    def update(self, pet_data: dict) -> Response:
        """
        Update an existing pet.
        
        Args:
            pet_data: Pet data dictionary with id and fields to update
            
        Returns:
            Response object with updated pet data
        """
        return self._client.put("/pet", path_template="/pet", json=pet_data)
    
    def get_by_id(self, pet_id: int) -> Response:
        """
        Get pet by ID.
        
        Args:
            pet_id: Pet ID to retrieve
            
        Returns:
            Response object with pet data or 404 if not found
        """
        return self._client.get(f"/pet/{pet_id}", path_template="/pet/{petId}")
    
    def delete(self, pet_id: int) -> Response:
        """
        Delete a pet.
        
        Args:
            pet_id: Pet ID to delete
            
        Returns:
            Response object with deletion status
        """
        return self._client.delete(f"/pet/{pet_id}", path_template="/pet/{petId}")
    
    def find_by_status(self, status: Union[str, list[str]]) -> Response:
        """
        Find pets by status.
        
        Args:
            status: Pet status ("available", "pending", "sold") or list of statuses
            
        Returns:
            Response object with array of pets matching the status
        """
        if isinstance(status, list):
            params = {"status": status}
        else:
            params = {"status": [status]}
        return self._client.get(
            "/pet/findByStatus",
            path_template="/pet/findByStatus",
            params=params
        )
    
    def find_by_tags(self, tags: list[str]) -> Response:
        """
        Find pets by tags (deprecated endpoint).
        
        Args:
            tags: List of tag names to filter by
            
        Returns:
            Response object with array of pets matching the tags
        """
        return self._client.get(
            "/pet/findByTags",
            path_template="/pet/findByTags",
            params={"tags": tags}
        )
    
    def update_with_form(
        self,
        pet_id: int,
        name: Optional[str] = None,
        status: Optional[str] = None
    ) -> Response:
        """
        Update a pet with form data.
        
        Args:
            pet_id: Pet ID to update
            name: New pet name (optional)
            status: New pet status (optional)
            
        Returns:
            Response object with update status
        """
        data = {}
        if name:
            data["name"] = name
        if status:
            data["status"] = status
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return self._client.post(
            f"/pet/{pet_id}",
            path_template="/pet/{petId}",
            data=data,
            headers=headers
        )
    
    def upload_image(
        self,
        pet_id: int,
        file_path: str,
        additional_metadata: Optional[str] = None
    ) -> Response:
        """
        Upload an image for a pet.
        
        Args:
            pet_id: Pet ID to add image to
            file_path: Path to the image file
            additional_metadata: Optional metadata string
            
        Returns:
            Response object with upload status
        """
        files = {"file": open(file_path, "rb")}
        data = {}
        if additional_metadata:
            data["additionalMetadata"] = additional_metadata
        
        return self._client.post(
            f"/pet/{pet_id}/uploadImage",
            path_template="/pet/{petId}/uploadImage",
            files=files,
            data=data
        )


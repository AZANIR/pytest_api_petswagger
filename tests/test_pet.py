"""Tests for Pet API endpoints."""
import logging
import pytest

from src.models import Pet, PetStatus

logger = logging.getLogger(__name__)


@pytest.mark.pet
class TestCreatePet:
    """Tests for POST /pet endpoint."""
    
    @pytest.mark.positive
    def test_create_pet_with_all_fields(self, api_client, pet_data, schema_validator):
        """Create a new pet with all fields and validate response schema."""
        logger.info(f"Creating pet with data: {pet_data['name']}")
        
        response = api_client.create_pet(pet_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        
        # Validate response schema
        schema = schema_validator.get_definition_schema("Pet")
        is_valid, error = schema_validator.validate(response_data, schema)
        assert is_valid, f"Schema validation failed: {error}"
        
        # Validate response content
        assert response_data["name"] == pet_data["name"]
        assert "id" in response_data
        
        # Cleanup
        if "id" in response_data:
            api_client.delete_pet(response_data["id"])
    
    @pytest.mark.positive
    def test_create_pet_with_minimal_fields(self, api_client, minimal_pet_data, schema_validator):
        """Create a new pet with only required fields (name, photoUrls)."""
        logger.info(f"Creating pet with minimal data: {minimal_pet_data['name']}")
        
        response = api_client.create_pet(minimal_pet_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        
        # Validate required fields are present
        assert "name" in response_data
        assert "photoUrls" in response_data
        
        # Cleanup
        if "id" in response_data:
            api_client.delete_pet(response_data["id"])
    
    @pytest.mark.negative
    def test_create_pet_missing_required_name(self, api_client, schema_validator):
        """Attempt to create a pet without required 'name' field."""
        invalid_data = Pet.create_invalid_missing_name()
        logger.info("Attempting to create pet without name field")
        
        # Validate request against schema (should fail)
        request_schema = schema_validator.get_definition_schema("Pet")
        is_valid, error = schema_validator.validate(invalid_data, request_schema)
        assert not is_valid, "Request should fail schema validation"
        assert "name" in error.lower(), f"Error should mention 'name': {error}"
        
        response = api_client.create_pet(invalid_data)
        
        # API may return 405 or 400 for invalid input
        assert response.status_code in [400, 405, 500], \
            f"Expected error status, got {response.status_code}"
    
    @pytest.mark.negative
    def test_create_pet_missing_required_photo_urls(self, api_client, schema_validator):
        """Attempt to create a pet without required 'photoUrls' field."""
        invalid_data = Pet.create_invalid_missing_photo_urls()
        logger.info("Attempting to create pet without photoUrls field")
        
        # Validate request against schema (should fail)
        request_schema = schema_validator.get_definition_schema("Pet")
        is_valid, error = schema_validator.validate(invalid_data, request_schema)
        assert not is_valid, "Request should fail schema validation"
        assert "photourls" in error.lower(), f"Error should mention 'photoUrls': {error}"
        
        response = api_client.create_pet(invalid_data)
        
        # API may return 405 or 400 for invalid input
        assert response.status_code in [400, 405, 500], \
            f"Expected error status, got {response.status_code}"
    
    @pytest.mark.negative
    def test_create_pet_invalid_status_value(self, api_client):
        """Attempt to create a pet with invalid status value."""
        pet = Pet.create()
        pet_data = pet.model_dump(by_alias=True, exclude_none=True)
        pet_data["status"] = "invalid_status"
        
        logger.info("Attempting to create pet with invalid status")
        
        response = api_client.create_pet(pet_data)
        
        # The API might accept this or return an error
        # Log the behavior for documentation
        logger.info(f"Response status: {response.status_code}")


@pytest.mark.pet
class TestGetPet:
    """Tests for GET /pet/{petId} endpoint."""
    
    @pytest.mark.positive
    def test_get_existing_pet(self, api_client, created_pet, schema_validator):
        """Get an existing pet by ID and validate response schema."""
        pet_id = created_pet["id"]
        logger.info(f"Getting pet with ID: {pet_id}")
        
        response = api_client.get_pet_by_id(pet_id)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        
        # Validate response schema
        schema = schema_validator.get_definition_schema("Pet")
        is_valid, error = schema_validator.validate(response_data, schema)
        assert is_valid, f"Schema validation failed: {error}"
        
        # Validate content matches
        assert response_data["id"] == pet_id
        assert response_data["name"] == created_pet["name"]
    
    @pytest.mark.negative
    def test_get_non_existing_pet(self, api_client):
        """Attempt to get a pet that doesn't exist."""
        non_existing_id = 999999999
        logger.info(f"Attempting to get non-existing pet ID: {non_existing_id}")
        
        response = api_client.get_pet_by_id(non_existing_id)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    @pytest.mark.negative
    def test_get_pet_invalid_id_format(self, api_client):
        """Attempt to get a pet with invalid ID format."""
        logger.info("Attempting to get pet with invalid ID format")
        
        # Request with string ID (API expects integer)
        response = api_client.request("GET", "/pet/invalid_id")
        
        # Should return 400 or 404
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404, got {response.status_code}"
    
    @pytest.mark.boundary
    def test_get_pet_with_zero_id(self, api_client):
        """Attempt to get a pet with ID = 0."""
        logger.info("Attempting to get pet with ID = 0")
        
        response = api_client.get_pet_by_id(0)
        
        # Zero ID is typically invalid
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404, got {response.status_code}"
    
    @pytest.mark.boundary
    def test_get_pet_with_negative_id(self, api_client):
        """Attempt to get a pet with negative ID."""
        logger.info("Attempting to get pet with negative ID")
        
        response = api_client.get_pet_by_id(-1)
        
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404, got {response.status_code}"


@pytest.mark.pet
class TestFindPetsByStatus:
    """Tests for GET /pet/findByStatus endpoint."""
    
    @pytest.mark.positive
    def test_find_pets_by_available_status(self, api_client, schema_validator):
        """Find pets with 'available' status."""
        logger.info("Finding pets with status: available")
        
        response = api_client.find_pets_by_status("available")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        
        # Response should be an array
        assert isinstance(response_data, list), "Response should be a list"
        
        # Validate each pet in response
        if response_data:
            pet_schema = schema_validator.get_definition_schema("Pet")
            for pet in response_data[:5]:  # Validate first 5 items
                is_valid, error = schema_validator.validate(pet, pet_schema)
                assert is_valid, f"Pet schema validation failed: {error}"
    
    @pytest.mark.positive
    def test_find_pets_by_multiple_statuses(self, api_client):
        """Find pets with multiple status values."""
        logger.info("Finding pets with statuses: available, pending")
        
        response = api_client.find_pets_by_status(["available", "pending"])
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert isinstance(response_data, list), "Response should be a list"
    
    @pytest.mark.positive
    def test_find_pets_by_sold_status(self, api_client):
        """Find pets with 'sold' status."""
        logger.info("Finding pets with status: sold")
        
        response = api_client.find_pets_by_status("sold")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert isinstance(response_data, list), "Response should be a list"
    
    @pytest.mark.negative
    def test_find_pets_by_invalid_status(self, api_client):
        """Attempt to find pets with invalid status value."""
        logger.info("Attempting to find pets with invalid status")
        
        response = api_client.find_pets_by_status("invalid_status")
        
        # API might return empty list or 400
        assert response.status_code in [200, 400], \
            f"Expected 200 or 400, got {response.status_code}"
        
        if response.status_code == 200:
            # If 200, response should be empty list
            response_data = response.json()
            logger.info(f"Response returned {len(response_data)} items for invalid status")


@pytest.mark.pet
class TestUpdatePet:
    """Tests for PUT /pet endpoint."""
    
    @pytest.mark.positive
    def test_update_existing_pet(self, api_client, created_pet, schema_validator):
        """Update an existing pet's data."""
        pet_id = created_pet["id"]
        updated_name = f"updated_{created_pet['name']}"
        
        logger.info(f"Updating pet {pet_id} with new name: {updated_name}")
        
        updated_data = created_pet.copy()
        updated_data["name"] = updated_name
        updated_data["status"] = "sold"
        
        response = api_client.update_pet(updated_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        
        # Validate response schema
        schema = schema_validator.get_definition_schema("Pet")
        is_valid, error = schema_validator.validate(response_data, schema)
        assert is_valid, f"Schema validation failed: {error}"
        
        # Verify update was applied
        assert response_data["name"] == updated_name
        assert response_data["status"] == "sold"
    
    @pytest.mark.negative
    def test_update_non_existing_pet(self, api_client):
        """Attempt to update a pet that doesn't exist."""
        pet_data = Pet.create(id=999999999).model_dump(by_alias=True, exclude_none=True)
        
        logger.info(f"Attempting to update non-existing pet")
        
        response = api_client.update_pet(pet_data)
        
        # API might return 404 or create a new pet
        logger.info(f"Response status: {response.status_code}")


@pytest.mark.pet
class TestDeletePet:
    """Tests for DELETE /pet/{petId} endpoint."""
    
    @pytest.mark.positive
    def test_delete_existing_pet(self, api_client, pet_data):
        """Delete an existing pet."""
        # First create a pet
        create_response = api_client.create_pet(pet_data)
        assert create_response.status_code == 200
        pet_id = create_response.json()["id"]
        
        logger.info(f"Deleting pet with ID: {pet_id}")
        
        response = api_client.delete_pet(pet_id)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify pet is deleted
        get_response = api_client.get_pet_by_id(pet_id)
        assert get_response.status_code == 404, "Pet should not exist after deletion"
    
    @pytest.mark.negative
    def test_delete_non_existing_pet(self, api_client):
        """Attempt to delete a pet that doesn't exist."""
        non_existing_id = 999999999
        logger.info(f"Attempting to delete non-existing pet ID: {non_existing_id}")
        
        response = api_client.delete_pet(non_existing_id)
        
        # API might return 404 or 400
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404, got {response.status_code}"
    
    @pytest.mark.boundary
    def test_delete_pet_with_negative_id(self, api_client):
        """Attempt to delete a pet with negative ID."""
        logger.info("Attempting to delete pet with negative ID")
        
        response = api_client.delete_pet(-1)
        
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404, got {response.status_code}"


"""Tests for Store API endpoints."""
import logging
import pytest

from src.models import Order, OrderStatus

logger = logging.getLogger(__name__)


@pytest.mark.store
class TestGetInventory:
    """Tests for GET /store/inventory endpoint."""
    
    @pytest.mark.positive
    def test_get_inventory(self, api_client, schema_validator):
        """Get store inventory and validate response schema."""
        logger.info("Getting store inventory")
        
        response = api_client.get_inventory()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        
        # Response should be an object with integer values
        assert isinstance(response_data, dict), "Response should be a dictionary"
        
        # Validate schema (object with additionalProperties of type integer)
        response_schema = schema_validator.get_response_schema(
            "/store/inventory", "get", 200
        )
        if response_schema:
            is_valid, error = schema_validator.validate(response_data, response_schema)
            assert is_valid, f"Schema validation failed: {error}"
        
        # Log inventory counts
        for status, count in response_data.items():
            logger.info(f"  {status}: {count}")


@pytest.mark.store
class TestPlaceOrder:
    """Tests for POST /store/order endpoint."""
    
    @pytest.mark.positive
    def test_place_order_with_all_fields(self, api_client, order_data, schema_validator):
        """Place a new order with all fields and validate response schema."""
        logger.info(f"Placing order: {order_data}")
        
        response = api_client.place_order(order_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        
        # Validate response schema
        schema = schema_validator.get_definition_schema("Order")
        is_valid, error = schema_validator.validate(response_data, schema)
        assert is_valid, f"Schema validation failed: {error}"
        
        # Validate response content
        assert "id" in response_data
        assert response_data["petId"] == order_data["petId"]
        
        # Cleanup
        if "id" in response_data:
            try:
                api_client.delete_order(response_data["id"])
            except Exception:
                pass
    
    @pytest.mark.positive
    def test_place_order_minimal_fields(self, api_client, schema_validator):
        """Place a new order with minimal fields."""
        minimal_order = Order.create_minimal().model_dump(by_alias=True, exclude_none=True)
        
        logger.info(f"Placing minimal order: {minimal_order}")
        
        response = api_client.place_order(minimal_order)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        
        # Validate response schema
        schema = schema_validator.get_definition_schema("Order")
        is_valid, error = schema_validator.validate(response_data, schema)
        assert is_valid, f"Schema validation failed: {error}"
        
        # Cleanup
        if "id" in response_data:
            try:
                api_client.delete_order(response_data["id"])
            except Exception:
                pass
    
    @pytest.mark.positive
    def test_place_order_with_each_status(self, api_client):
        """Test placing orders with each possible status value."""
        for status in OrderStatus:
            order = Order.create(status=status)
            order_data = order.model_dump(by_alias=True, exclude_none=True)
            
            logger.info(f"Placing order with status: {status.value}")
            
            response = api_client.place_order(order_data)
            
            assert response.status_code == 200, \
                f"Expected 200 for status {status.value}, got {response.status_code}"
            
            # Cleanup
            response_data = response.json()
            if "id" in response_data:
                try:
                    api_client.delete_order(response_data["id"])
                except Exception:
                    pass
    
    @pytest.mark.negative
    def test_place_order_invalid_status(self, api_client):
        """Attempt to place an order with invalid status value."""
        order_data = {
            "id": 1,
            "petId": 1000,
            "quantity": 1,
            "status": "invalid_status"
        }
        
        logger.info("Attempting to place order with invalid status")
        
        response = api_client.place_order(order_data)
        
        # API might accept this or return an error
        logger.info(f"Response status: {response.status_code}")


@pytest.mark.store
class TestGetOrder:
    """Tests for GET /store/order/{orderId} endpoint."""
    
    @pytest.mark.positive
    def test_get_existing_order(self, api_client, created_order, schema_validator):
        """Get an existing order by ID and validate response schema."""
        order_id = created_order["id"]
        logger.info(f"Getting order with ID: {order_id}")
        
        response = api_client.get_order_by_id(order_id)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        
        # Validate response schema
        schema = schema_validator.get_definition_schema("Order")
        is_valid, error = schema_validator.validate(response_data, schema)
        assert is_valid, f"Schema validation failed: {error}"
        
        # Validate content matches
        assert response_data["id"] == order_id
    
    @pytest.mark.boundary
    def test_get_order_with_min_valid_id(self, api_client, schema_validator):
        """Get order with minimum valid ID (1) per API spec."""
        logger.info("Getting order with ID: 1 (minimum valid)")
        
        # First create an order with id=1
        order = Order.create(id=1)
        order_data = order.model_dump(by_alias=True, exclude_none=True)
        create_response = api_client.place_order(order_data)
        
        if create_response.status_code == 200:
            response = api_client.get_order_by_id(1)
            
            # ID 1 is within valid range (1-10), should work if exists
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                schema = schema_validator.get_definition_schema("Order")
                is_valid, error = schema_validator.validate(response_data, schema)
                assert is_valid, f"Schema validation failed: {error}"
            
            # Cleanup
            try:
                api_client.delete_order(1)
            except Exception:
                pass
    
    @pytest.mark.boundary
    def test_get_order_with_max_valid_id(self, api_client, schema_validator):
        """Get order with maximum valid ID (10) per API spec."""
        logger.info("Getting order with ID: 10 (maximum valid)")
        
        # First create an order with id=10
        order = Order.create(id=10)
        order_data = order.model_dump(by_alias=True, exclude_none=True)
        create_response = api_client.place_order(order_data)
        
        if create_response.status_code == 200:
            response = api_client.get_order_by_id(10)
            
            # ID 10 is within valid range (1-10), should work if exists
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                schema = schema_validator.get_definition_schema("Order")
                is_valid, error = schema_validator.validate(response_data, schema)
                assert is_valid, f"Schema validation failed: {error}"
            
            # Cleanup
            try:
                api_client.delete_order(10)
            except Exception:
                pass
    
    @pytest.mark.negative
    def test_get_order_exceeds_max_id(self, api_client):
        """Attempt to get order with ID > 10 (outside valid range)."""
        logger.info("Getting order with ID: 11 (exceeds maximum)")
        
        response = api_client.get_order_by_id(11)
        
        # Per API spec, IDs > 10 should return error
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404 for ID > 10, got {response.status_code}"
    
    @pytest.mark.negative
    def test_get_order_with_zero_id(self, api_client):
        """Attempt to get order with ID = 0 (below valid range)."""
        logger.info("Getting order with ID: 0 (below minimum)")
        
        response = api_client.get_order_by_id(0)
        
        # Per API spec, IDs < 1 should return error
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404 for ID = 0, got {response.status_code}"
    
    @pytest.mark.negative
    def test_get_order_with_negative_id(self, api_client):
        """Attempt to get order with negative ID."""
        logger.info("Getting order with ID: -1")
        
        response = api_client.get_order_by_id(-1)
        
        # Negative IDs are invalid
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404 for negative ID, got {response.status_code}"
    
    @pytest.mark.negative
    def test_get_non_existing_order(self, api_client):
        """Attempt to get an order that doesn't exist."""
        logger.info("Getting non-existing order")
        
        # Use ID within valid range but unlikely to exist
        response = api_client.get_order_by_id(9)
        
        # Should return 404 if order doesn't exist
        logger.info(f"Response status: {response.status_code}")


@pytest.mark.store
class TestDeleteOrder:
    """Tests for DELETE /store/order/{orderId} endpoint."""
    
    @pytest.mark.positive
    def test_delete_existing_order(self, api_client, order_data):
        """Delete an existing order."""
        # First create an order
        create_response = api_client.place_order(order_data)
        assert create_response.status_code == 200
        order_id = create_response.json()["id"]
        
        logger.info(f"Deleting order with ID: {order_id}")
        
        response = api_client.delete_order(order_id)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify order is deleted
        get_response = api_client.get_order_by_id(order_id)
        assert get_response.status_code == 404, "Order should not exist after deletion"
    
    @pytest.mark.negative
    def test_delete_non_existing_order(self, api_client):
        """Attempt to delete an order that doesn't exist."""
        logger.info("Attempting to delete non-existing order")
        
        response = api_client.delete_order(999)
        
        # Should return 404
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404, got {response.status_code}"
    
    @pytest.mark.negative
    def test_delete_order_with_negative_id(self, api_client):
        """Attempt to delete order with negative ID."""
        logger.info("Attempting to delete order with negative ID")
        
        response = api_client.delete_order(-1)
        
        # Per API spec, negative values generate API errors
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404, got {response.status_code}"
    
    @pytest.mark.boundary
    def test_delete_order_with_zero_id(self, api_client):
        """Attempt to delete order with ID = 0."""
        logger.info("Attempting to delete order with ID = 0")
        
        response = api_client.delete_order(0)
        
        # Zero is below the minimum (1), should return error
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404, got {response.status_code}"


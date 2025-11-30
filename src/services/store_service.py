"""Store API service endpoints."""
from requests import Response

from .base_service import BaseService


class StoreService(BaseService):
    """
    Service class for Store API endpoints.
    
    Provides methods for managing store inventory and orders.
    
    Usage:
        api = APIClient()
        api.store.get_inventory()
        api.store.place_order(order_data)
        api.store.get_order_by_id(1)
    """
    
    def get_inventory(self) -> Response:
        """
        Get store inventory.
        
        Returns:
            Response object with inventory counts by status
        """
        return self._client.get("/store/inventory", path_template="/store/inventory")
    
    def place_order(self, order_data: dict) -> Response:
        """
        Place a new order for a pet.
        
        Args:
            order_data: Order data dictionary
            
        Returns:
            Response object with created order data
        """
        return self._client.post("/store/order", path_template="/store/order", json=order_data)
    
    def get_order_by_id(self, order_id: int) -> Response:
        """
        Get order by ID.
        
        Valid IDs are 1-10 per API specification.
        
        Args:
            order_id: Order ID to retrieve (1-10)
            
        Returns:
            Response object with order data or error
        """
        return self._client.get(
            f"/store/order/{order_id}",
            path_template="/store/order/{orderId}"
        )
    
    def delete_order(self, order_id: int) -> Response:
        """
        Delete an order.
        
        Args:
            order_id: Order ID to delete
            
        Returns:
            Response object with deletion status
        """
        return self._client.delete(
            f"/store/order/{order_id}",
            path_template="/store/order/{orderId}"
        )


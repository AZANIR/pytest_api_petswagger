"""Petstore API client that aggregates all service endpoints."""
from requests import Response

from src.http import BaseHTTPClient


class APIClient(BaseHTTPClient):
    """
    Petstore API client that aggregates all service endpoints.
    
    Provides access to Pet, Store, and User services through
    dedicated service classes.
    
    Usage (new style with services):
        api = APIClient()
        
        # Pet operations
        api.pet.create(pet_data)
        api.pet.get_by_id(123)
        api.pet.find_by_status("available")
        
        # Store operations
        api.store.get_inventory()
        api.store.place_order(order_data)
        
        # User operations
        api.user.create(user_data)
        api.user.login("username", "password")
    
    Usage (legacy style - backward compatible):
        api = APIClient()
        api.create_pet(pet_data)
        api.get_pet_by_id(123)
    """
    
    def __init__(self, **kwargs):
        """Initialize API client with all services."""
        super().__init__(**kwargs)
        
        # Import here to avoid circular imports
        from src.services.pet_service import PetService
        from src.services.store_service import StoreService
        from src.services.user_service import UserService
        
        # Initialize services
        self.pet = PetService(self)
        self.store = StoreService(self)
        self.user = UserService(self)
    
    # ==================== Backward Compatibility Methods ====================
    # These methods delegate to services for backward compatibility
    
    # Pet methods
    def create_pet(self, pet_data: dict) -> Response:
        """Create a new pet."""
        return self.pet.create(pet_data)
    
    def update_pet(self, pet_data: dict) -> Response:
        """Update an existing pet."""
        return self.pet.update(pet_data)
    
    def get_pet_by_id(self, pet_id: int) -> Response:
        """Get pet by ID."""
        return self.pet.get_by_id(pet_id)
    
    def delete_pet(self, pet_id: int) -> Response:
        """Delete a pet."""
        return self.pet.delete(pet_id)
    
    def find_pets_by_status(self, status) -> Response:
        """Find pets by status."""
        return self.pet.find_by_status(status)
    
    def find_pets_by_tags(self, tags: list[str]) -> Response:
        """Find pets by tags."""
        return self.pet.find_by_tags(tags)
    
    def update_pet_with_form(self, pet_id: int, name=None, status=None) -> Response:
        """Update a pet with form data."""
        return self.pet.update_with_form(pet_id, name, status)
    
    def upload_pet_image(self, pet_id: int, file_path: str, additional_metadata=None) -> Response:
        """Upload an image for a pet."""
        return self.pet.upload_image(pet_id, file_path, additional_metadata)
    
    # Store methods
    def get_inventory(self) -> Response:
        """Get store inventory."""
        return self.store.get_inventory()
    
    def place_order(self, order_data: dict) -> Response:
        """Place a new order."""
        return self.store.place_order(order_data)
    
    def get_order_by_id(self, order_id: int) -> Response:
        """Get order by ID."""
        return self.store.get_order_by_id(order_id)
    
    def delete_order(self, order_id: int) -> Response:
        """Delete an order."""
        return self.store.delete_order(order_id)
    
    # User methods
    def create_user(self, user_data: dict) -> Response:
        """Create a new user."""
        return self.user.create(user_data)
    
    def create_users_with_array(self, users_data: list[dict]) -> Response:
        """Create multiple users with an array."""
        return self.user.create_with_array(users_data)
    
    def create_users_with_list(self, users_data: list[dict]) -> Response:
        """Create multiple users with a list."""
        return self.user.create_with_list(users_data)
    
    def get_user_by_username(self, username: str) -> Response:
        """Get user by username."""
        return self.user.get_by_username(username)
    
    def update_user(self, username: str, user_data: dict) -> Response:
        """Update user."""
        return self.user.update(username, user_data)
    
    def delete_user(self, username: str) -> Response:
        """Delete user."""
        return self.user.delete(username)
    
    def login_user(self, username: str, password: str) -> Response:
        """Login user."""
        return self.user.login(username, password)
    
    def logout_user(self) -> Response:
        """Logout user."""
        return self.user.logout()

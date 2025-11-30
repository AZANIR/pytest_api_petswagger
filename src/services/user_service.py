"""User API service endpoints."""
from requests import Response

from .base_service import BaseService


class UserService(BaseService):
    """
    Service class for User API endpoints.
    
    Provides methods for managing users and authentication.
    
    Usage:
        api = APIClient()
        api.user.create(user_data)
        api.user.login("username", "password")
        api.user.get_by_username("john")
    """
    
    def create(self, user_data: dict) -> Response:
        """
        Create a new user.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            Response object with creation status
        """
        return self._client.post("/user", path_template="/user", json=user_data)
    
    def create_with_array(self, users_data: list[dict]) -> Response:
        """
        Create multiple users with an array.
        
        Args:
            users_data: List of user data dictionaries
            
        Returns:
            Response object with creation status
        """
        return self._client.post(
            "/user/createWithArray",
            path_template="/user/createWithArray",
            json=users_data
        )
    
    def create_with_list(self, users_data: list[dict]) -> Response:
        """
        Create multiple users with a list.
        
        Args:
            users_data: List of user data dictionaries
            
        Returns:
            Response object with creation status
        """
        return self._client.post(
            "/user/createWithList",
            path_template="/user/createWithList",
            json=users_data
        )
    
    def get_by_username(self, username: str) -> Response:
        """
        Get user by username.
        
        Args:
            username: Username to retrieve
            
        Returns:
            Response object with user data or 404 if not found
        """
        return self._client.get(f"/user/{username}", path_template="/user/{username}")
    
    def update(self, username: str, user_data: dict) -> Response:
        """
        Update user data.
        
        Args:
            username: Username of user to update
            user_data: Updated user data dictionary
            
        Returns:
            Response object with update status
        """
        return self._client.put(
            f"/user/{username}",
            path_template="/user/{username}",
            json=user_data
        )
    
    def delete(self, username: str) -> Response:
        """
        Delete a user.
        
        Args:
            username: Username to delete
            
        Returns:
            Response object with deletion status
        """
        return self._client.delete(f"/user/{username}", path_template="/user/{username}")
    
    def login(self, username: str, password: str) -> Response:
        """
        Login user into the system.
        
        Args:
            username: Username for login
            password: Password for login
            
        Returns:
            Response object with session token
        """
        return self._client.get(
            "/user/login",
            path_template="/user/login",
            params={"username": username, "password": password}
        )
    
    def logout(self) -> Response:
        """
        Logout current logged in user session.
        
        Returns:
            Response object with logout status
        """
        return self._client.get("/user/logout", path_template="/user/logout")


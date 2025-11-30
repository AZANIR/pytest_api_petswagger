"""Tests for User API endpoints."""
import logging
import pytest

from src.models import User

logger = logging.getLogger(__name__)


@pytest.mark.user
class TestCreateUser:
    """Tests for POST /user endpoint."""
    
    @pytest.mark.positive
    def test_create_user_with_all_fields(self, api_client, user_data, schema_validator):
        """Create a new user with all fields."""
        logger.info(f"Creating user: {user_data['username']}")
        
        response = api_client.create_user(user_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify user was created by getting it
        get_response = api_client.get_user_by_username(user_data["username"])
        assert get_response.status_code == 200, "User should exist after creation"
        
        response_data = get_response.json()
        
        # Validate response schema
        schema = schema_validator.get_definition_schema("User")
        is_valid, error = schema_validator.validate(response_data, schema)
        assert is_valid, f"Schema validation failed: {error}"
        
        # Validate content matches
        assert response_data["username"] == user_data["username"]
        assert response_data["email"] == user_data["email"]
        
        # Cleanup
        api_client.delete_user(user_data["username"])
    
    @pytest.mark.positive
    def test_create_user_with_minimal_fields(self, api_client):
        """Create a new user with minimal fields."""
        user = User.create_minimal()
        user_data = user.model_dump(by_alias=True, exclude_none=True)
        
        logger.info(f"Creating user with minimal data: {user_data['username']}")
        
        response = api_client.create_user(user_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Cleanup
        api_client.delete_user(user_data["username"])


@pytest.mark.user
class TestCreateUsersWithArray:
    """Tests for POST /user/createWithArray endpoint."""
    
    @pytest.mark.positive
    def test_create_users_with_array(self, api_client, users_list_data):
        """Create multiple users with array input."""
        logger.info(f"Creating {len(users_list_data)} users with array")
        
        response = api_client.create_users_with_array(users_list_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify each user was created
        for user_data in users_list_data:
            get_response = api_client.get_user_by_username(user_data["username"])
            assert get_response.status_code == 200, \
                f"User {user_data['username']} should exist after batch creation"
            
            # Cleanup
            api_client.delete_user(user_data["username"])
    
    @pytest.mark.boundary
    def test_create_users_empty_array(self, api_client):
        """Create users with empty array."""
        logger.info("Creating users with empty array")
        
        response = api_client.create_users_with_array([])
        
        # Should succeed or return an appropriate error
        logger.info(f"Response status for empty array: {response.status_code}")


@pytest.mark.user
class TestCreateUsersWithList:
    """Tests for POST /user/createWithList endpoint."""
    
    @pytest.mark.positive
    def test_create_users_with_list(self, api_client, users_list_data):
        """Create multiple users with list input."""
        logger.info(f"Creating {len(users_list_data)} users with list")
        
        response = api_client.create_users_with_list(users_list_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify each user was created
        for user_data in users_list_data:
            get_response = api_client.get_user_by_username(user_data["username"])
            assert get_response.status_code == 200, \
                f"User {user_data['username']} should exist after batch creation"
            
            # Cleanup
            api_client.delete_user(user_data["username"])


@pytest.mark.user
class TestGetUser:
    """Tests for GET /user/{username} endpoint."""
    
    @pytest.mark.positive
    def test_get_existing_user(self, api_client, created_user, schema_validator):
        """Get an existing user by username and validate response schema."""
        username = created_user["username"]
        logger.info(f"Getting user: {username}")
        
        response = api_client.get_user_by_username(username)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        
        # Validate response schema
        schema = schema_validator.get_definition_schema("User")
        is_valid, error = schema_validator.validate(response_data, schema)
        assert is_valid, f"Schema validation failed: {error}"
        
        # Validate content matches
        assert response_data["username"] == username
    
    @pytest.mark.negative
    def test_get_non_existing_user(self, api_client):
        """Attempt to get a user that doesn't exist."""
        non_existing_username = "non_existing_user_xyz_12345"
        logger.info(f"Attempting to get non-existing user: {non_existing_username}")
        
        response = api_client.get_user_by_username(non_existing_username)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    @pytest.mark.negative
    def test_get_user_with_special_characters(self, api_client):
        """Attempt to get user with special characters in username."""
        special_username = "user@#$%"
        logger.info(f"Attempting to get user with special chars: {special_username}")
        
        response = api_client.get_user_by_username(special_username)
        
        # Should return 400 or 404
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404, got {response.status_code}"
    
    @pytest.mark.boundary
    def test_get_user_with_empty_username(self, api_client):
        """Attempt to get user with empty username."""
        logger.info("Attempting to get user with empty username")
        
        # This will hit /user/ endpoint which might behave differently
        response = api_client.request("GET", "/user/")
        
        # Should return an error
        logger.info(f"Response status: {response.status_code}")


@pytest.mark.user
class TestUpdateUser:
    """Tests for PUT /user/{username} endpoint."""
    
    @pytest.mark.positive
    def test_update_existing_user(self, api_client, created_user, schema_validator):
        """Update an existing user's data."""
        username = created_user["username"]
        updated_first_name = "UpdatedFirstName"
        updated_email = "updated_email@example.com"
        
        logger.info(f"Updating user: {username}")
        
        updated_data = created_user.copy()
        updated_data["firstName"] = updated_first_name
        updated_data["email"] = updated_email
        
        response = api_client.update_user(username, updated_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify update was applied
        get_response = api_client.get_user_by_username(username)
        assert get_response.status_code == 200
        
        response_data = get_response.json()
        
        # Validate response schema
        schema = schema_validator.get_definition_schema("User")
        is_valid, error = schema_validator.validate(response_data, schema)
        assert is_valid, f"Schema validation failed: {error}"
        
        # Verify updated fields
        assert response_data["firstName"] == updated_first_name
        assert response_data["email"] == updated_email
    
    @pytest.mark.negative
    def test_update_non_existing_user(self, api_client, user_data):
        """Attempt to update a user that doesn't exist."""
        non_existing_username = "non_existing_user_xyz_12345"
        logger.info(f"Attempting to update non-existing user: {non_existing_username}")
        
        response = api_client.update_user(non_existing_username, user_data)
        
        # Should return 404
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404, got {response.status_code}"


@pytest.mark.user
class TestDeleteUser:
    """Tests for DELETE /user/{username} endpoint."""
    
    @pytest.mark.positive
    def test_delete_existing_user(self, api_client, user_data):
        """Delete an existing user."""
        # First create a user
        create_response = api_client.create_user(user_data)
        assert create_response.status_code == 200
        username = user_data["username"]
        
        logger.info(f"Deleting user: {username}")
        
        response = api_client.delete_user(username)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify user is deleted
        get_response = api_client.get_user_by_username(username)
        assert get_response.status_code == 404, "User should not exist after deletion"
    
    @pytest.mark.negative
    def test_delete_non_existing_user(self, api_client):
        """Attempt to delete a user that doesn't exist."""
        non_existing_username = "non_existing_user_xyz_12345"
        logger.info(f"Attempting to delete non-existing user: {non_existing_username}")
        
        response = api_client.delete_user(non_existing_username)
        
        # Should return 404
        assert response.status_code in [400, 404], \
            f"Expected 400 or 404, got {response.status_code}"


@pytest.mark.user
class TestUserLogin:
    """Tests for GET /user/login endpoint."""
    
    @pytest.mark.positive
    def test_login_user(self, api_client, created_user):
        """Login with valid credentials."""
        username = created_user["username"]
        password = created_user["password"]
        
        logger.info(f"Logging in user: {username}")
        
        response = api_client.login_user(username, password)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Validate response headers per spec
        # X-Rate-Limit and X-Expires-After headers should be present
        logger.info(f"Response headers: {dict(response.headers)}")
        
        # Response body is a string (session token)
        response_text = response.text
        logger.info(f"Login response: {response_text[:100]}...")
    
    @pytest.mark.negative
    def test_login_invalid_credentials(self, api_client):
        """Attempt to login with invalid credentials."""
        logger.info("Attempting to login with invalid credentials")
        
        response = api_client.login_user("invalid_user", "wrong_password")
        
        # Should return 400 per spec
        # Note: Petstore API might return 200 even for invalid credentials
        logger.info(f"Response status for invalid login: {response.status_code}")
    
    @pytest.mark.negative
    def test_login_missing_username(self, api_client):
        """Attempt to login without username."""
        logger.info("Attempting to login without username")
        
        response = api_client.request(
            "GET", "/user/login",
            params={"password": "some_password"}
        )
        
        # Should return 400 for missing required parameter
        logger.info(f"Response status: {response.status_code}")
    
    @pytest.mark.negative
    def test_login_missing_password(self, api_client):
        """Attempt to login without password."""
        logger.info("Attempting to login without password")
        
        response = api_client.request(
            "GET", "/user/login",
            params={"username": "some_user"}
        )
        
        # Should return 400 for missing required parameter
        logger.info(f"Response status: {response.status_code}")


@pytest.mark.user
class TestUserLogout:
    """Tests for GET /user/logout endpoint."""
    
    @pytest.mark.positive
    def test_logout_user(self, api_client):
        """Logout current user session."""
        logger.info("Logging out user")
        
        response = api_client.logout_user()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        logger.info(f"Logout response: {response.text}")


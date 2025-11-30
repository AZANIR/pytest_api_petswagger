"""Pytest configuration and fixtures for Petstore API tests."""
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Generator

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Settings, get_settings, set_current_settings
from src.api_client import APIClient
from src.schema_validator import SwaggerSchemaValidator, get_schema_validator
from src.models import Pet, Order, User, Category, Tag


# ==================== Pytest Hooks for CLI Options ====================

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Environment to run tests against (dev, staging, prod)"
    )
    parser.addoption(
        "--base-url",
        action="store",
        default=None,
        help="Override base URL for API requests"
    )
    parser.addoption(
        "--api-key",
        action="store",
        default=None,
        help="Override API key"
    )


def pytest_configure(config):
    """Configure pytest with environment settings."""
    # Get environment from CLI
    env_name = config.getoption("--env")
    base_url = config.getoption("--base-url")
    api_key = config.getoption("--api-key")
    
    # Load settings for the environment
    settings = get_settings(env_name)
    
    # Override with CLI options if provided
    if base_url:
        settings = Settings(
            base_url=base_url,
            api_key=settings.api_key,
            timeout=settings.timeout,
            log_level=settings.log_level,
            env_name=env_name
        )
    if api_key:
        settings = Settings(
            base_url=settings.base_url,
            api_key=api_key,
            timeout=settings.timeout,
            log_level=settings.log_level,
            env_name=env_name
        )
    
    # Set as current settings
    set_current_settings(settings)
    
    # Setup logging
    _setup_logging(settings.log_level)
    
    # Log test session info
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info(f"TEST SESSION STARTED: {datetime.now().isoformat()}")
    logger.info(f"Environment: {env_name}")
    logger.info(f"Base URL: {settings.base_url}")
    logger.info("=" * 60)
    
    # Create reports directory if not exists
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Create logs directory if not exists
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)


def pytest_unconfigure(config):
    """Cleanup after test session."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info(f"TEST SESSION ENDED: {datetime.now().isoformat()}")
    logger.info("=" * 60)


def _setup_logging(log_level: str) -> None:
    """Setup logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), logging.DEBUG)
    
    # Create logs directory
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    log_file = logs_dir / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set level for specific loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


# ==================== Pytest HTML Report Hooks ====================

def pytest_html_report_title(report):
    """Set custom title for HTML report."""
    report.title = "Petstore API Test Report"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add extra information to test report."""
    outcome = yield
    report = outcome.get_result()
    
    # Add environment info to report (use 'extras' instead of deprecated 'extra')
    if not hasattr(report, "extras"):
        report.extras = []
    
    if report.when == "call":
        # Add test docstring if available
        if item.function.__doc__:
            try:
                from pytest_html import extras
                report.extras.append(
                    extras.text(item.function.__doc__, name="Description")
                )
            except ImportError:
                pass  # pytest-html extras not available


# ==================== Fixtures ====================

@pytest.fixture(scope="session")
def settings() -> Settings:
    """Get current settings instance."""
    from config.settings import get_current_settings
    return get_current_settings()


@pytest.fixture(scope="session")
def api_client(settings) -> Generator[APIClient, None, None]:
    """
    Create API client for the test session.
    
    Yields:
        APIClient instance configured for the current environment
    """
    client = APIClient(
        base_url=settings.base_url,
        api_key=settings.api_key,
        timeout=settings.timeout,
        validate_schemas=True
    )
    
    yield client
    
    client.close()


@pytest.fixture(scope="session")
def schema_validator() -> SwaggerSchemaValidator:
    """
    Get schema validator instance.
    
    Returns:
        SwaggerSchemaValidator instance
    """
    swagger_path = project_root / "schemas" / "swagger.json"
    return get_schema_validator(swagger_path)


# ==================== Model Fixtures ====================

@pytest.fixture
def pet_data() -> dict:
    """Generate test pet data."""
    return Pet.create().model_dump(by_alias=True, exclude_none=True)


@pytest.fixture
def minimal_pet_data() -> dict:
    """Generate minimal test pet data with only required fields."""
    return Pet.create_minimal().model_dump(by_alias=True, exclude_none=True)


@pytest.fixture
def order_data() -> dict:
    """Generate test order data."""
    return Order.create().model_dump(by_alias=True, exclude_none=True)


@pytest.fixture
def user_data() -> dict:
    """Generate test user data."""
    return User.create().model_dump(by_alias=True, exclude_none=True)


@pytest.fixture
def users_list_data() -> list[dict]:
    """Generate list of test users."""
    return [u.model_dump(by_alias=True, exclude_none=True) for u in User.create_list(3)]


# ==================== Cleanup Fixtures ====================

@pytest.fixture
def created_pet(api_client, pet_data) -> Generator[dict, None, None]:
    """
    Create a pet and clean up after test.
    
    Yields:
        Created pet data with ID
    """
    response = api_client.create_pet(pet_data)
    assert response.status_code == 200, f"Failed to create pet: {response.text}"
    
    created = response.json()
    yield created
    
    # Cleanup
    if "id" in created:
        api_client.delete_pet(created["id"])


@pytest.fixture
def created_order(api_client, order_data) -> Generator[dict, None, None]:
    """
    Create an order and clean up after test.
    
    Yields:
        Created order data with ID
    """
    response = api_client.place_order(order_data)
    assert response.status_code == 200, f"Failed to create order: {response.text}"
    
    created = response.json()
    yield created
    
    # Cleanup
    if "id" in created:
        try:
            api_client.delete_order(created["id"])
        except Exception:
            pass  # Order might already be deleted


@pytest.fixture
def created_user(api_client, user_data) -> Generator[dict, None, None]:
    """
    Create a user and clean up after test.
    
    Yields:
        Created user data
    """
    response = api_client.create_user(user_data)
    assert response.status_code == 200, f"Failed to create user: {response.text}"
    
    yield user_data
    
    # Cleanup
    if "username" in user_data:
        try:
            api_client.delete_user(user_data["username"])
        except Exception:
            pass  # User might already be deleted


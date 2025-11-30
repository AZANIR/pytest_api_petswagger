# Petstore API Testing Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Pytest](https://img.shields.io/badge/pytest-8.0+-green.svg)](https://pytest.org/)
[![Tests](https://github.com/YOUR_USERNAME/pytest_api/actions/workflows/tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/pytest_api/actions/workflows/tests.yml)

Pytest framework for automated REST API testing with schema validation, logging, and multi-environment support.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Running Tests](#running-tests)
- [Schema Validation](#schema-validation)
- [Writing Tests](#writing-tests)
- [Logging](#logging)
- [Reports](#reports)
- [CI/CD](#cicd)

---

## Requirements

- Python 3.10+
- pip (Python package manager)

---

## Installation

### Step 1: Clone or download the project

```bash
git clone <repository-url>
cd pytest_api
```

### Step 2: Create virtual environment (recommended)

**Windows:**

```bash
python -m venv venv
source venv/Scripts/activate
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify installation

```bash
python -m pytest --version
```

---

## Project Structure

```text
pytest_api/
│
├── config/                          # Configuration
│   ├── __init__.py
│   ├── settings.py                  # Pydantic settings
│   └── environments/                # Environment files
│       ├── dev.env                  # Development
│       ├── staging.env              # Staging
│       └── prod.env                 # Production
│
├── src/                             # Source code
│   ├── __init__.py
│   ├── api_client.py                # Main API client
│   ├── schema_validator.py          # JSON schema validator
│   │
│   ├── http/                        # HTTP module
│   │   ├── __init__.py
│   │   ├── methods.py               # HTTP methods (GET, POST, PUT, DELETE)
│   │   └── client.py                # Base HTTP client
│   │
│   ├── services/                    # API services (endpoints)
│   │   ├── __init__.py
│   │   ├── base_service.py          # Base service class
│   │   ├── pet_service.py           # Pet API endpoints
│   │   ├── store_service.py         # Store API endpoints
│   │   └── user_service.py          # User API endpoints
│   │
│   └── models/                      # Pydantic models
│       ├── __init__.py
│       ├── pet.py                   # Pet, Category, Tag
│       ├── store.py                 # Order
│       └── user.py                  # User, ApiResponse
│
├── tests/                           # Tests
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures and configuration
│   ├── test_pet.py                  # Pet API tests
│   ├── test_store.py                # Store API tests
│   └── test_user.py                 # User API tests
│
├── schemas/                         # Swagger/OpenAPI schemas
│   └── swagger.json                 # API Swagger specification
│
├── logs/                            # Test logs (auto-created)
├── reports/                         # HTML reports (auto-created)
│
├── pytest.ini                       # Pytest configuration
├── requirements.txt                 # Python dependencies
└── README.md                        # Documentation
```

---

## Quick Start

### 1. Run all tests

```bash
# Errors only (default)
python -m pytest tests/ -v

# Show WARNING and above
python -m pytest tests/ -v --log-cli-level=WARNING

# Show INFO and above
python -m pytest tests/ -v --log-cli-level=INFO

# Show everything (DEBUG)
python -m pytest tests/ -v --log-cli-level=DEBUG

# Completely disable console logs
python -m pytest tests/ -v --log-cli-level=CRITICAL
```

### 2. Run specific test file

```bash
python -m pytest tests/test_pet.py -v
```

### 3. Run specific test

```bash
python -m pytest tests/test_pet.py::TestCreatePet::test_create_pet_with_all_fields -v
```

---

## Environment Configuration

The framework supports testing on different environments (dev, staging, prod).

### Environment Files

Located in `config/environments/`:

**dev.env** (Development):

```env
BASE_URL=https://petstore.swagger.io/v2
API_KEY=special-key
TIMEOUT=30
LOG_LEVEL=DEBUG
```

**staging.env** (Staging):

```env
BASE_URL=https://staging-petstore.swagger.io/v2
API_KEY=staging-key
TIMEOUT=60
LOG_LEVEL=INFO
```

**prod.env** (Production):

```env
BASE_URL=https://petstore.swagger.io/v2
API_KEY=prod-key
TIMEOUT=60
LOG_LEVEL=WARNING
```

### CLI Usage

```bash
# Development (default)
python -m pytest --env=dev

# Staging
python -m pytest --env=staging

# Production
python -m pytest --env=prod

# Custom URL
python -m pytest --base-url=https://my-api.example.com/v2

# Custom API key
python -m pytest --api-key=my-secret-key

# Combination
python -m pytest --env=staging --base-url=https://custom-api.com/v2
```

---

## Running Tests

### By markers (test types)

```bash
# Only positive tests
python -m pytest -m positive

# Only negative tests
python -m pytest -m negative

# Only boundary tests
python -m pytest -m boundary

# Marker combinations
python -m pytest -m "positive and pet"
python -m pytest -m "negative or boundary"
```

### By API groups

```bash
# Only Pet API
python -m pytest -m pet

# Only Store API
python -m pytest -m store

# Only User API
python -m pytest -m user

# Pet and Store
python -m pytest -m "pet or store"
```

### Additional options

```bash
# Verbose output
python -m pytest -v

# Show print statements
python -m pytest -s

# Stop on first failure
python -m pytest -x

# Run last failed tests
python -m pytest --lf

# Parallel execution (requires pytest-xdist)
python -m pytest -n auto

# Generate HTML report
python -m pytest --html=reports/report.html --self-contained-html
```

---

## Schema Validation

The framework automatically validates API responses against JSON schemas from the Swagger file.

### How it works

1. `SwaggerSchemaValidator` loads `schemas/swagger.json`
2. For each request, the expected response schema is extracted
3. Response is validated using the `jsonschema` library
4. Validation errors are logged as warnings

### Usage in tests

```python
def test_get_pet_schema(api_client, schema_validator):
    """Test with manual schema validation."""
    response = api_client.get_pet_by_id(1)
    
    # Get schema from Swagger
    pet_schema = schema_validator.get_definition_schema("Pet")
    
    # Validate response
    is_valid, error = schema_validator.validate(response.json(), pet_schema)
    
    assert is_valid, f"Schema validation failed: {error}"
```

### Required fields validation

```python
def test_required_fields(schema_validator):
    """Check that Pet has required fields."""
    pet_schema = schema_validator.get_definition_schema("Pet")
    
    # Pet requires: name, photoUrls
    invalid_pet = {"status": "available"}  # missing required fields
    
    is_valid, error = schema_validator.validate(invalid_pet, pet_schema)
    
    assert not is_valid
    assert "name" in error or "photoUrls" in error
```

---

## Writing Tests

### Basic test structure

```python
import pytest
import logging

logger = logging.getLogger(__name__)


@pytest.mark.pet
class TestPetAPI:
    """Tests for Pet API."""
    
    @pytest.mark.positive
    def test_create_pet(self, api_client, pet_data):
        """Create a new pet."""
        logger.info(f"Creating pet: {pet_data['name']}")
        
        response = api_client.create_pet(pet_data)
        
        assert response.status_code == 200
        assert response.json()["name"] == pet_data["name"]
```

### Using fixtures

```python
# Automatic fixtures from conftest.py

def test_with_pet_data(api_client, pet_data):
    """pet_data - automatically generated test data."""
    response = api_client.create_pet(pet_data)
    assert response.status_code == 200

def test_with_created_pet(api_client, created_pet):
    """created_pet - already created pet, deleted after test."""
    pet_id = created_pet["id"]
    response = api_client.get_pet_by_id(pet_id)
    assert response.status_code == 200
```

### API client usage styles

```python
def test_new_style_api(api_client):
    """New style - via services."""
    # Pet operations
    api_client.pet.create(pet_data)
    api_client.pet.get_by_id(123)
    api_client.pet.find_by_status("available")
    api_client.pet.delete(123)
    
    # Store operations
    api_client.store.get_inventory()
    api_client.store.place_order(order_data)
    
    # User operations
    api_client.user.create(user_data)
    api_client.user.login("username", "password")

def test_legacy_style_api(api_client):
    """Legacy style - direct methods (backward compatible)."""
    api_client.create_pet(pet_data)
    api_client.get_pet_by_id(123)
    api_client.find_pets_by_status("available")
```

### Creating test data with models

```python
from src.models import Pet, Order, User

def test_with_models():
    """Using Pydantic models."""
    
    # Full Pet
    pet = Pet.create(name="Buddy", status=PetStatus.AVAILABLE)
    pet_data = pet.model_dump(by_alias=True, exclude_none=True)
    
    # Minimal Pet (only required fields)
    minimal_pet = Pet.create_minimal()
    
    # Invalid data for negative tests
    invalid_data = Pet.create_invalid_missing_name()
    
    # Order
    order = Order.create(pet_id=123, quantity=2)
    
    # User
    user = User.create(username="testuser")
    users = User.create_list(count=5)  # List of 5 users
```

---

## Logging

### Automatic logging

All HTTP requests and responses are automatically logged:

```text
2024-01-15 10:30:45 [INFO] >>> POST https://petstore.swagger.io/v2/pet
2024-01-15 10:30:45 [DEBUG]     Request body: {"name": "Buddy", "photoUrls": [...]}
2024-01-15 10:30:46 [INFO] <<< 200 OK (0.523s)
2024-01-15 10:30:46 [DEBUG]     Response body: {"id": 123, "name": "Buddy", ...}
```

### Log files

- Console: ERROR level (configurable)
- File `logs/test_YYYYMMDD_HHMMSS.log`: DEBUG level

### Logging in tests

```python
import logging

logger = logging.getLogger(__name__)

def test_with_logging(api_client):
    logger.info("Starting test")
    logger.debug("Detailed debug info")
    logger.warning("Something suspicious")
    logger.error("Something went wrong")
```

---

## Reports

### HTML Report (pytest-html)

Report is automatically created in `reports/report.html` after each run.

```bash
python -m pytest --html=reports/report.html --self-contained-html
```

### CTRF JSON Report

Generate [Common Test Report Format](https://ctrf.io/) JSON report:

```bash
python -m pytest --ctrf ctrf-report.json
```

### Both reports

```bash
python -m pytest tests/ \
  --html=reports/report.html \
  --self-contained-html \
  --ctrf ctrf-report.json \
  -v
```

### Viewing reports

- **HTML Report**: Open `reports/report.html` in a browser
- **CTRF Report**: View `ctrf-report.json` or use [CTRF viewers](https://ctrf.io/)

---

## CI/CD

### GitHub Actions

The project includes a GitHub Actions workflow (`.github/workflows/tests.yml`) that:

1. **Runs tests** on Python 3.11 and 3.12
2. **Generates reports** (HTML + CTRF JSON)
3. **Publishes CTRF summary** in PR/commit comments
4. **Deploys reports** to GitHub Pages

### Enabling GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Set **Source** to `gh-pages` branch
3. Reports will be available at: `https://YOUR_USERNAME.github.io/REPO_NAME/`

### Manual workflow trigger

You can manually trigger the workflow from the **Actions** tab.

### Workflow badges

Add to your README:

```markdown
[![Tests](https://github.com/YOUR_USERNAME/REPO_NAME/actions/workflows/tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/REPO_NAME/actions/workflows/tests.yml)
```

---

## Command Examples

```bash
# Full test run with report
python -m pytest tests/ -v --html=reports/report.html

# Tests on staging with detailed logging
python -m pytest --env=staging -v -s

# Only smoke tests (positive Pet tests)
python -m pytest -m "positive and pet" -v

# Quick check - only first 3 tests
python -m pytest tests/test_pet.py -v --maxfail=3

# Run with custom URL
python -m pytest --base-url=https://my-test-server.com/v2 -v
```

---

## Troubleshooting

### Error: ModuleNotFoundError

```bash
# Make sure you're in the correct directory
cd pytest_api

# Reinstall dependencies
pip install -r requirements.txt
```

### Error: pytest command not found

```bash
# Use python -m pytest instead of pytest
python -m pytest tests/ -v
```

### Tests can't find modules

```bash
# Add PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/macOS
set PYTHONPATH=%PYTHONPATH%;%cd%          # Windows CMD
$env:PYTHONPATH += ";$(pwd)"              # Windows PowerShell
```

---

## Useful Links

- [Pytest Documentation](https://docs.pytest.org/)
- [Requests Library](https://requests.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JSON Schema](https://json-schema.org/)
- [Petstore Swagger UI](https://petstore.swagger.io/)
- [CTRF - Common Test Report Format](https://ctrf.io/)
- [pytest-json-ctrf](https://github.com/infopulse/pytest-common-test-report-json)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

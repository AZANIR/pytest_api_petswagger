# Test Plan - Petstore API

## 1. Introduction

### 1.1 Purpose

This document outlines the test plan for the Petstore API testing framework. It defines the scope, objectives, test strategy, and requirements for comprehensive API testing.

### 1.2 Scope

The test plan covers all public endpoints of the Petstore API (Swagger version 1.0.7):

- **Pet API** - Pet management operations
- **Store API** - Store inventory and order operations
- **User API** - User management and authentication operations

### 1.3 Objectives

- Verify all API endpoints function according to Swagger specification
- Validate response schemas against OpenAPI definitions
- Test positive, negative, and boundary scenarios
- Ensure proper error handling and status codes
- Validate required fields and parameters

---

## 2. Test Requirements

### 2.1 Functional Requirements

#### Pet API Requirements

| Requirement ID | Description | Priority |
|---------------|-------------|----------|
| PET-001 | Create new pet with all fields | High |
| PET-002 | Create new pet with minimal required fields (name, photoUrls) | High |
| PET-003 | Reject pet creation without required fields | High |
| PET-004 | Retrieve existing pet by ID | High |
| PET-005 | Return 404 for non-existing pet | Medium |
| PET-006 | Find pets by status (available, pending, sold) | High |
| PET-007 | Find pets by multiple statuses | Medium |
| PET-008 | Update existing pet | High |
| PET-009 | Delete existing pet | High |
| PET-010 | Handle invalid pet ID formats | Medium |
| PET-011 | Find pets by tags (deprecated) | Low |
| PET-012 | Upload pet image | Low |
| PET-013 | Update pet with form data | Medium |

#### Store API Requirements

| Requirement ID | Description | Priority |
|---------------|-------------|----------|
| STORE-001 | Retrieve store inventory | High |
| STORE-002 | Place new order with all fields | High |
| STORE-003 | Place order with minimal fields | Medium |
| STORE-004 | Retrieve order by ID (valid range 1-10) | High |
| STORE-005 | Return error for order ID outside valid range | Medium |
| STORE-006 | Delete existing order | High |
| STORE-007 | Handle invalid order IDs | Medium |

#### User API Requirements

| Requirement ID | Description | Priority |
|---------------|-------------|----------|
| USER-001 | Create single user | High |
| USER-002 | Create multiple users with array | Medium |
| USER-003 | Create multiple users with list | Medium |
| USER-004 | Retrieve user by username | High |
| USER-005 | Return 404 for non-existing user | Medium |
| USER-006 | Update existing user | High |
| USER-007 | Delete existing user | High |
| USER-008 | Login with valid credentials | High |
| USER-009 | Logout user session | Medium |
| USER-010 | Handle invalid login credentials | Medium |

### 2.2 Non-Functional Requirements

| Requirement ID | Description | Priority |
|---------------|-------------|----------|
| NFR-001 | Response time < 5 seconds for all endpoints | Medium |
| NFR-002 | All responses must conform to JSON schema | High |
| NFR-003 | Proper HTTP status codes for all scenarios | High |
| NFR-004 | Cross-environment support (dev, staging, prod) | High |
| NFR-005 | Comprehensive logging for debugging | Medium |
| NFR-006 | HTML and CTRF report generation | Medium |

---

## 3. Test Strategy

### 3.1 Test Types

#### Positive Tests

- Verify successful operations with valid data
- Validate response body matches expected schema
- Confirm correct HTTP status codes (200, 201)

#### Negative Tests

- Test with invalid or missing required fields
- Test with non-existing resources
- Verify appropriate error responses (400, 404, 405)

#### Boundary Tests

- Test edge values (0, negative numbers, max values)
- Test empty inputs and special characters
- Verify boundary conditions per API specification

### 3.2 Test Approach

```python
┌─────────────────────────────────────────────────────────┐
│                    Test Execution                       │
├─────────────────────────────────────────────────────────┤
│  1. Setup Phase                                         │
│     - Load environment configuration                    │
│     - Initialize API client with authentication         │
│     - Load Swagger schema for validation                │
│                                                         │
│  2. Test Execution Phase                                │
│     - Execute test cases by priority                    │
│     - Validate responses against schema                 │
│     - Log all requests and responses                    │
│                                                         │
│  3. Cleanup Phase                                       │
│     - Delete created test data                          │
│     - Close connections                                 │
│     - Generate reports                                  │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Schema Validation Strategy

1. **Swagger Schema Extraction**
   - Parse swagger.json at test initialization
   - Extract model definitions (Pet, Order, User, etc.)
   - Resolve $ref references dynamically

2. **Response Validation**
   - Validate every API response against expected schema
   - Use jsonschema library for validation
   - Report schema violations as test failures

3. **Request Validation**
   - Validate request bodies before sending (for negative tests)
   - Verify required fields are present
   - Check field types and formats

---

## 4. Test Environment

### 4.1 Environment Configuration

| Environment | Base URL | Purpose |
|-------------|----------|---------|
| Development | <https://petstore.swagger.io/v2> | Primary testing |
| Staging | Configurable | Pre-production testing |
| Production | Configurable | Smoke tests only |

### 4.2 Environment Selection

```bash
# Run tests on specific environment
pytest --env=dev          # Development (default)
pytest --env=staging      # Staging
pytest --env=prod         # Production

# Override base URL directly
pytest --base-url=https://custom-api.com/v2
```

---

## 5. Test Data Management

### 5.1 Test Data Strategy

- Generate unique test data using factory methods
- Use Pydantic models for data generation and validation
- Implement automatic cleanup after test execution

### 5.2 Data Models

| Model | Required Fields | Optional Fields |
|-------|-----------------|-----------------|
| Pet | name, photoUrls | id, category, tags, status |
| Order | - | id, petId, quantity, shipDate, status, complete |
| User | - | id, username, firstName, lastName, email, password, phone, userStatus |

---

## 6. Test Execution

### 6.1 Test Markers

| Marker | Description |
|--------|-------------|
| @pytest.mark.positive | Positive scenario tests |
| @pytest.mark.negative | Negative scenario tests |
| @pytest.mark.boundary | Boundary condition tests |
| @pytest.mark.pet | Pet API tests |
| @pytest.mark.store | Store API tests |
| @pytest.mark.user | User API tests |

### 6.2 Execution Commands

```bash
# Run all tests
pytest tests/ -v

# Run by test type
pytest -m positive
pytest -m negative
pytest -m boundary

# Run by API
pytest -m pet
pytest -m store
pytest -m user

# Run with HTML report
pytest --html=reports/report.html --self-contained-html

# Run with CTRF report
pytest --ctrf ctrf-report.json
```

---

## 7. Exit Criteria

### 7.1 Test Completion Criteria

- All high-priority test cases executed
- All critical defects resolved
- Schema validation passing for all endpoints
- Test coverage meets minimum threshold (80%)

### 7.2 Quality Gates

| Gate | Criteria |
|------|----------|
| Alpha | All positive tests pass |
| Beta | All positive + negative tests pass |
| Release | All tests pass including boundary |

---

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limiting | Test execution delays | Implement retry logic with backoff |
| Test data pollution | False test results | Use unique identifiers and cleanup fixtures |
| Schema changes | Test failures | Version swagger.json and monitor changes |
| Network instability | Flaky tests | Configure appropriate timeouts |

---

## 9. Deliverables

- [ ] Automated test suite
- [ ] HTML test reports
- [ ] CTRF JSON reports
- [ ] Test execution logs
- [ ] Coverage analysis documentation
- [ ] CI/CD pipeline integration

---

## 10. Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2024-01-01 | QA Team | Initial test plan |

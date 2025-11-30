<!-- 546d9eea-3f7f-4b0f-b3c7-46870d65c6c6 499ab7b2-8c8f-4537-b0ba-e98140b862fe -->
# Petstore API Testing Framework

## Архітектура проекту

```
pytest_api/
├── schemas/
│   └── swagger.json           # Існуючий файл
├── config/
│   ├── __init__.py
│   ├── settings.py            # Pydantic Settings для конфігурації
│   └── environments/
│       ├── dev.env            # Development environment
│       ├── staging.env        # Staging environment
│       └── prod.env           # Production environment
├── src/
│   ├── __init__.py
│   ├── api_client.py          # HTTP клієнт (requests)
│   ├── schema_validator.py    # Витягування та валідація схем з swagger.json
│   └── models/
│       ├── __init__.py
│       ├── pet.py             # Pydantic: Pet, Category, Tag
│       ├── store.py           # Pydantic: Order
│       └── user.py            # Pydantic: User, ApiResponse
├── tests/
│   ├── conftest.py            # Fixtures, logging setup, env selection
│   ├── test_pet.py            # Pet endpoints (8 тестів)
│   ├── test_store.py          # Store endpoints (4 тести)
│   └── test_user.py           # User endpoints (8 тестів)
├── logs/                      # Директорія для логів
├── reports/                   # HTML репорти
├── pytest.ini                 # Конфігурація pytest
└── requirements.txt
```

## Cross-Environment Configuration

### Використання

```bash
# Запуск на різних енвайронментах
pytest --env=dev                    # Development (default)
pytest --env=staging                # Staging
pytest --env=prod                   # Production
pytest --env=custom --base-url=https://my-api.com/v2  # Custom URL
```

### Environment Files (config/environments/*.env)

```env
# dev.env
BASE_URL=https://petstore.swagger.io/v2
API_KEY=special-key
TIMEOUT=30
LOG_LEVEL=DEBUG

# staging.env
BASE_URL=https://staging-petstore.swagger.io/v2
API_KEY=staging-key
TIMEOUT=60
LOG_LEVEL=INFO
```

### Settings Class ([config/settings.py](config/settings.py))

- `pydantic-settings` для валідації конфігурації
- Автоматичне завантаження з .env файлів
- Override через CLI аргументи pytest
- Поля: `BASE_URL`, `API_KEY`, `TIMEOUT`, `LOG_LEVEL`

## Ключові компоненти

### 1. Schema Validator ([src/schema_validator.py](src/schema_validator.py))

- Клас `SwaggerSchemaValidator` для роботи зі swagger.json
- Метод `get_definition_schema(name)` - отримує схему моделі (Pet, Order, User)
- Метод `get_response_schema(path, method, status_code)` - схема відповіді ендпоінта
- Метод `validate_response(data, schema)` - валідація через `jsonschema`
- Автоматичне розгортання `$ref` посилань

### 2. Pydantic Models ([src/models/](src/models/))

- `Pet`, `Category`, `Tag` з валідацією required полів (name, photoUrls)
- `Order` з enum статусами (placed, approved, delivered)
- `User` з усіма полями
- Фабричні методи для генерації тестових даних

### 3. API Client ([src/api_client.py](src/api_client.py))

- Базовий URL: `https://petstore.swagger.io/v2`
- Методи для кожного ендпоінта з логуванням запитів/відповідей
- Автоматична валідація схеми відповіді (опціонально)

### 4. Logging та Reporting

- `logging` модуль з форматом: timestamp, level, message
- Логування в файл + консоль
- `pytest-html` для HTML репортів
- Custom hook для додавання логів до репорту

## Тести

### Pet API (test_pet.py)

| Тест | Тип | Валідація |

|------|-----|-----------|

| POST /pet - створення | Positive | Schema + required fields |

| POST /pet - без required | Negative | 405 response |

| GET /pet/{id} - існуючий | Positive | Pet schema |

| GET /pet/{id} - неіснуючий | Negative | 404 response |

| GET /pet/findByStatus | Positive | Array[Pet] schema |

| GET /pet/findByStatus - invalid | Negative | 400 response |

| PUT /pet - оновлення | Positive | Schema validation |

| DELETE /pet/{id} | Positive/Negative | Status codes |

### Store API (test_store.py)

| Тест | Тип | Валідація |

|------|-----|-----------|

| GET /store/inventory | Positive | Object schema |

| POST /store/order | Positive | Order schema |

| GET /store/order/{id} - valid (1-10) | Positive | Order schema |

| GET /store/order/{id} - boundary | Boundary | 400/404 |

| DELETE /store/order/{id} | Positive/Negative | Status codes |

### User API (test_user.py)

| Тест | Тип | Валідація |

|------|-----|-----------|

| POST /user | Positive | Response validation |

| POST /user/createWithArray | Positive | Batch creation |

| GET /user/{username} | Positive | User schema |

| GET /user/{username} - неіснуючий | Negative | 404 |

| PUT /user/{username} | Positive | Update validation |

| DELETE /user/{username} | Positive/Negative | Status codes |

| GET /user/login | Positive | Headers validation |

| GET /user/logout | Positive | Response validation |

## Залежності (requirements.txt)

```
pytest>=8.0.0
pytest-html>=4.0.0
requests>=2.31.0
pydantic>=2.5.0
jsonschema>=4.20.0
```

### To-dos

- [ ] Create project structure, requirements.txt, pytest.ini
- [ ] Implement SwaggerSchemaValidator class with $ref resolution
- [ ] Create Pydantic models (Pet, Order, User) with factories
- [ ] Implement API client with logging and schema validation
- [ ] Setup conftest.py with fixtures and logging configuration
- [ ] Write Pet API tests (positive, negative, boundary)
- [ ] Write Store API tests (positive, negative, boundary)
- [ ] Write User API tests (positive, negative, boundary)
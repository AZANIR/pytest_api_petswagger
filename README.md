# Petstore API Testing Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Pytest](https://img.shields.io/badge/pytest-8.0+-green.svg)](https://pytest.org/)

Pytest фреймворк для автоматизованого тестування REST API з валідацією схем, логуванням та підтримкою різних середовищ.

## Зміст

- [Вимоги](#вимоги)
- [Встановлення](#встановлення)
- [Структура проекту](#структура-проекту)
- [Швидкий старт](#швидкий-старт)
- [Конфігурація середовищ](#конфігурація-середовищ)
- [Запуск тестів](#запуск-тестів)
- [Валідація схем](#валідація-схем)
- [Написання тестів](#написання-тестів)
- [Логування](#логування)
- [HTML Репорти](#html-репорти)

---

## Вимоги

- Python 3.10+
- pip (менеджер пакетів Python)

---

## Встановлення

### Крок 1: Клонування або завантаження проекту

```bash
git clone <repository-url>
cd pytest_api
```

### Крок 2: Створення віртуального середовища (рекомендовано)

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

### Крок 3: Встановлення залежностей

```bash
pip install -r requirements.txt
```

### Крок 4: Перевірка встановлення

```bash
python -m pytest --version
```

---

## Структура проекту

```
pytest_api/
│
├── config/                          # Конфігурація
│   ├── __init__.py
│   ├── settings.py                  # Налаштування через Pydantic
│   └── environments/                # Файли середовищ
│       ├── dev.env                  # Development
│       ├── staging.env              # Staging
│       └── prod.env                 # Production
│
├── src/                             # Вихідний код
│   ├── __init__.py
│   ├── api_client.py                # Головний API клієнт
│   ├── schema_validator.py          # Валідатор JSON схем
│   │
│   ├── http/                        # HTTP модуль
│   │   ├── __init__.py
│   │   ├── methods.py               # HTTP методи (GET, POST, PUT, DELETE)
│   │   └── client.py                # Базовий HTTP клієнт
│   │
│   ├── services/                    # API сервіси (ендпоінти)
│   │   ├── __init__.py
│   │   ├── base_service.py          # Базовий клас сервісу
│   │   ├── pet_service.py           # Pet API ендпоінти
│   │   ├── store_service.py         # Store API ендпоінти
│   │   └── user_service.py          # User API ендпоінти
│   │
│   └── models/                      # Pydantic моделі
│       ├── __init__.py
│       ├── pet.py                   # Pet, Category, Tag
│       ├── store.py                 # Order
│       └── user.py                  # User, ApiResponse
│
├── tests/                           # Тести
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures та конфігурація
│   ├── test_pet.py                  # Тести Pet API
│   ├── test_store.py                # Тести Store API
│   └── test_user.py                 # Тести User API
│
├── schemas/                         # Swagger/OpenAPI схеми
│   └── swagger.json                 # Swagger специфікація API
│
├── logs/                            # Логи тестів (автостворюється)
├── reports/                         # HTML репорти (автостворюється)
│
├── pytest.ini                       # Конфігурація pytest
├── requirements.txt                 # Залежності Python
└── README.md                        # Документація
```

---

## Швидкий старт

### 1. Запуск всіх тестів

```bash
# Тільки помилки (за замовчуванням)
python -m pytest tests/ -v

# Показати WARNING і вище
python -m pytest tests/ -v --log-cli-level=WARNING

# Показати INFO і вище  
python -m pytest tests/ -v --log-cli-level=INFO

# Показати все (DEBUG)
python -m pytest tests/ -v --log-cli-level=DEBUG

# Повністю вимкнути логи в консолі
python -m pytest tests/ -v --log-cli-level=CRITICAL
```

### 2. Запуск конкретного тест-файлу

```bash
python -m pytest tests/test_pet.py -v
```

### 3. Запуск конкретного тесту

```bash
python -m pytest tests/test_pet.py::TestCreatePet::test_create_pet_with_all_fields -v
```

---

## Конфігурація середовищ

Фреймворк підтримує тестування на різних середовищах (dev, staging, prod).

### Файли середовищ

Знаходяться в `config/environments/`:

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

### Використання через CLI

```bash
# Development (за замовчуванням)
python -m pytest --env=dev

# Staging
python -m pytest --env=staging

# Production
python -m pytest --env=prod

# Custom URL
python -m pytest --base-url=https://my-api.example.com/v2

# Custom API key
python -m pytest --api-key=my-secret-key

# Комбінація
python -m pytest --env=staging --base-url=https://custom-api.com/v2
```

---

## Запуск тестів

### По маркерам (типам тестів)

```bash
# Тільки позитивні тести
python -m pytest -m positive

# Тільки негативні тести
python -m pytest -m negative

# Тільки boundary тести
python -m pytest -m boundary

# Комбінація маркерів
python -m pytest -m "positive and pet"
python -m pytest -m "negative or boundary"
```

### По API групах

```bash
# Тільки Pet API
python -m pytest -m pet

# Тільки Store API
python -m pytest -m store

# Тільки User API
python -m pytest -m user

# Pet та Store
python -m pytest -m "pet or store"
```

### Додаткові опції

```bash
# Verbose output
python -m pytest -v

# Показати print statements
python -m pytest -s

# Зупинитись на першій помилці
python -m pytest -x

# Запустити останні failed тести
python -m pytest --lf

# Паралельний запуск (потребує pytest-xdist)
python -m pytest -n auto

# Генерація HTML репорту
python -m pytest --html=reports/report.html --self-contained-html
```

---

## Валідація схем

Фреймворк автоматично валідує відповіді API проти JSON схем зі Swagger файлу.

### Як це працює

1. `SwaggerSchemaValidator` завантажує `schemas/swagger.json`
2. При кожному запиті витягується очікувана схема відповіді
3. Відповідь валідується через `jsonschema` бібліотеку
4. Помилки валідації логуються як warnings

### Використання в тестах

```python
def test_get_pet_schema(api_client, schema_validator):
    """Тест з ручною валідацією схеми."""
    response = api_client.get_pet_by_id(1)
    
    # Отримати схему з Swagger
    pet_schema = schema_validator.get_definition_schema("Pet")
    
    # Валідувати відповідь
    is_valid, error = schema_validator.validate(response.json(), pet_schema)
    
    assert is_valid, f"Schema validation failed: {error}"
```

### Валідація required полів

```python
def test_required_fields(schema_validator):
    """Перевірка що Pet має required поля."""
    pet_schema = schema_validator.get_definition_schema("Pet")
    
    # Pet requires: name, photoUrls
    invalid_pet = {"status": "available"}  # missing required fields
    
    is_valid, error = schema_validator.validate(invalid_pet, pet_schema)
    
    assert not is_valid
    assert "name" in error or "photoUrls" in error
```

---

## Написання тестів

### Базова структура тесту

```python
import pytest
import logging

logger = logging.getLogger(__name__)


@pytest.mark.pet
class TestPetAPI:
    """Тести для Pet API."""
    
    @pytest.mark.positive
    def test_create_pet(self, api_client, pet_data):
        """Створення нового pet."""
        logger.info(f"Creating pet: {pet_data['name']}")
        
        response = api_client.create_pet(pet_data)
        
        assert response.status_code == 200
        assert response.json()["name"] == pet_data["name"]
```

### Використання fixtures

```python
# Автоматичні fixtures з conftest.py

def test_with_pet_data(api_client, pet_data):
    """pet_data - автоматично згенеровані тестові дані."""
    response = api_client.create_pet(pet_data)
    assert response.status_code == 200

def test_with_created_pet(api_client, created_pet):
    """created_pet - вже створений pet, видаляється після тесту."""
    pet_id = created_pet["id"]
    response = api_client.get_pet_by_id(pet_id)
    assert response.status_code == 200
```

### Нові стилі використання API клієнта

```python
def test_new_style_api(api_client):
    """Новий стиль - через сервіси."""
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
    """Старий стиль - прямі методи (backward compatible)."""
    api_client.create_pet(pet_data)
    api_client.get_pet_by_id(123)
    api_client.find_pets_by_status("available")
```

### Створення тестових даних через моделі

```python
from src.models import Pet, Order, User

def test_with_models():
    """Використання Pydantic моделей."""
    
    # Повний Pet
    pet = Pet.create(name="Buddy", status=PetStatus.AVAILABLE)
    pet_data = pet.model_dump(by_alias=True, exclude_none=True)
    
    # Мінімальний Pet (тільки required поля)
    minimal_pet = Pet.create_minimal()
    
    # Невалідні дані для негативних тестів
    invalid_data = Pet.create_invalid_missing_name()
    
    # Order
    order = Order.create(pet_id=123, quantity=2)
    
    # User
    user = User.create(username="testuser")
    users = User.create_list(count=5)  # Список з 5 користувачів
```

---

## Логування

### Автоматичне логування

Всі HTTP запити та відповіді автоматично логуються:

```
2024-01-15 10:30:45 [INFO] >>> POST https://petstore.swagger.io/v2/pet
2024-01-15 10:30:45 [DEBUG]     Request body: {"name": "Buddy", "photoUrls": [...]}
2024-01-15 10:30:46 [INFO] <<< 200 OK (0.523s)
2024-01-15 10:30:46 [DEBUG]     Response body: {"id": 123, "name": "Buddy", ...}
```

### Файли логів

- Консоль: INFO рівень
- Файл `logs/test_YYYYMMDD_HHMMSS.log`: DEBUG рівень

### Логування в тестах

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

## HTML Репорти

### Автоматична генерація

Репорт автоматично створюється в `reports/report.html` після кожного запуску.

### Ручна генерація

```bash
python -m pytest --html=reports/my_report.html --self-contained-html
```

### Перегляд репорту

Відкрийте файл `reports/report.html` в браузері.

---

## Приклади команд

```bash
# Повний тест-ран з репортом
python -m pytest tests/ -v --html=reports/report.html

# Тести на staging з детальним логуванням
python -m pytest --env=staging -v -s

# Тільки smoke тести (позитивні Pet тести)
python -m pytest -m "positive and pet" -v

# Швидка перевірка - тільки перші 3 тести
python -m pytest tests/test_pet.py -v --maxfail=3

# Запуск з custom URL
python -m pytest --base-url=https://my-test-server.com/v2 -v
```

---

## Troubleshooting

### Помилка: ModuleNotFoundError

```bash
# Переконайтесь що ви в правильній директорії
cd pytest_api

# Перевстановіть залежності
pip install -r requirements.txt
```

### Помилка: pytest command not found

```bash
# Використовуйте python -m pytest замість pytest
python -m pytest tests/ -v
```

### Тести не знаходять модулі

```bash
# Додайте PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/macOS
set PYTHONPATH=%PYTHONPATH%;%cd%          # Windows CMD
$env:PYTHONPATH += ";$(pwd)"              # Windows PowerShell
```

---

## Корисні посилання

- [Pytest Documentation](https://docs.pytest.org/)
- [Requests Library](https://requests.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JSON Schema](https://json-schema.org/)
- [Petstore Swagger UI](https://petstore.swagger.io/)


---
icon: lucide/sparkles
---

# Features

Database Utils provides a set of utilities designed to simplify working with databases in Python, without sacrificing flexibility or control.

## Core Features

### Repository Pattern

A generic and type-safe abstraction for database operations. The repository pattern provides a consistent interface for accessing data, regardless of the underlying implementation.

- **Generic typing** - Full support for TypeVar, maintaining type safety
- **Flexible implementations** - Extend with your own operations
- **Abstraction layer** - Decouple your code from the specific database

### Zero Dependencies Core

The core module has no external dependencies. Install only what you need:

- Core `database-utils` - No dependencies
- SQLAlchemy extras - Install only when you use it with `[sqlalchemy]`
- Easy to integrate into existing projects

### Type Safety

Full type hints throughout the library:

- **IDE autocompletion** - Excellent editor support
- **Type checking** - Compatible with mypy and other checkers
- **Runtime validation** - Leverage Pydantic when you need it

### Extensible Design

Designed to be extended:

- **Custom implementations** - Create repositories for different databases
- **Mixins** - Share behavior between models
- **Pluggable adapters** - Integrate with your tech stack

## SQLAlchemy Module

Complete SQLAlchemy integration for production applications.

### SQLAlchemyBase

Declarative base class with built-in naming conventions:

```python
from database_utils.sqlalchemy import SQLAlchemyBase

class User(SQLAlchemyBase):
    __tablename__ = "users"
    # Your model here
```

**Benefits:**

- **Naming conventions** - Consistent conventions for constraints
  - Indexes: `idx_tablename_column`
  - Foreign keys: `fk_tablename_column_referred_table`
  - Unique constraints: `uq_tablename_column`
  - Check constraints: `ck_tablename_constraint`

- **Alembic ready** - Compatible with automatic migrations
- **Production grade** - Designed for production projects

### SQLAlchemyRepository

Ready-to-use implementation of the repository pattern:

```python
from sqlalchemy.orm import Session
from database_utils.sqlalchemy import SQLAlchemyRepository

class UserRepository(SQLAlchemyRepository):
    model_type = User

repo = UserRepository(session)
users = repo.list()
user = repo.get(user_id)
```

**Common operations:**

- `list()` - Get all records
- `get(id)` - Get a record by ID
- `create(obj_in)` - Create a new record
- `update(db_obj, obj_in)` - Update a record
- `delete(id)` - Delete a record

### Model Mixins

Reusable mixins for common functionality:

```python
from database_utils.sqlalchemy.mixins import TimestampMixin

class Article(SQLAlchemyBase, TimestampMixin):
    __tablename__ = "articles"
    title: Mapped[str] = mapped_column(String)
    # created_at and updated_at automatically included
```

**Available mixins:**

- `TimestampMixin` - Automatic `created_at` and `updated_at` fields
- Customize for your specific needs

## Use Cases

### Modern Web Applications

Perfect for FastAPI, Flask, or any web framework:

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database_utils.sqlalchemy import SQLAlchemyRepository

app = FastAPI()

async def get_repository(session: Session = Depends(get_session)):
    return UserRepository(session)

@app.get("/users")
async def list_users(repo: UserRepository = Depends(get_repository)):
    return repo.list()
```

### Microservices

Keep a clean and testable data access layer:

```python
# models.py
class Order(SQLAlchemyBase):
    __tablename__ = "orders"
    customer_id: Mapped[int]
    total: Mapped[Decimal]

# repositories.py
class OrderRepository(SQLAlchemyRepository):
    model_type = Order
    
    def get_customer_orders(self, customer_id: int):
        # Custom logic
        pass

# services.py
class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo
```

### ETL and Data Processing

Simplify batch operations:

```python
class DataIngestionRepository(SQLAlchemyRepository):
    def bulk_insert(self, records: list[dict]):
        """Efficient bulk insertion"""
        pass
    
    def get_unprocessed(self):
        """Get pending records"""
        pass
```

## Integrated Best Practices

Database Utils incorporates best practices from SQLAlchemy and Alembic:

- ✅ **Concurrent migrations** - Conventions for Alembic
- ✅ **Query optimization** - Type-safe queries
- ✅ **Constraint safety** - Consistent naming for constraints
- ✅ **Schema versioning** - Compatible with migrations

## Next Steps

- Explore examples in the [repository](https://github.com/javalce/database-utils)
- Read the [quick start guide](index.md)
- Check out the [API documentation](../api/index.md)

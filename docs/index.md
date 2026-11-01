---
icon: lucide/database
---

# Database Utils

Lightweight, extensible Python database utilities. Less boilerplate, same control.

[![PyPI](https://img.shields.io/pypi/v/database-utils.svg)](https://pypi.org/project/database-utils/)
[![Python Versions](https://img.shields.io/pypi/pyversions/database-utils.svg)](https://pypi.org/project/database-utils/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/javalce/database-utils/blob/main/LICENSE)

## Why Database Utils?

Database work should be straightforward. **Database Utils** provides:

- ✅ Consistent naming conventions for migrations and constraints
- ✅ Reusable model mixins and base classes
- ✅ Two flexible repository patterns: simple and CRUD
- ✅ Type-safe operations throughout
- ✅ Zero dependencies in core; install your adapter separately (e.g., SQLAlchemy)
- ✅ Designed for production use with Alembic migrations
- ✅ Built-in best practices for scalable database schemas

## Installation

/// tab | uv

```bash
uv add database-utils
```

///

/// tab | pip

```bash
pip install database-utils
```

///

## Quick Start

### 1. Define Your Model

```python
from sqlalchemy import String, create_engine
from sqlalchemy.orm import Mapped, mapped_column, Session
from database_utils.sqlalchemy import SQLAlchemyBase

class User(SQLAlchemyBase):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)

engine = create_engine("sqlite:///db.sqlite")
SQLAlchemyBase.metadata.create_all(engine)
```

### 2. Choose Your Pattern

**Simple Pattern** — Model is your schema:

```python
from database_utils.sqlalchemy import SQLAlchemyRepository

class UserRepository(SQLAlchemyRepository):
    model_type = User

with Session(engine) as session:
    repo = UserRepository(session)
    user = User(name="Alice", email="alice@example.com")
    saved = repo.save(user)  # Create
    user = repo.get(saved.id)  # Read
    saved.name = "Alice Updated"
    repo.save(saved)  # Update
    repo.delete(saved)  # Delete
```

**CRUD Pattern** — Separate schemas for validation:

```python
from dataclasses import dataclass
from database_utils.sqlalchemy import SQLAlchemyCrudRepository

@dataclass
class UserCreate:
    name: str
    email: str

@dataclass
class UserUpdate:
    name: str | None = None
    email: str | None = None

class UserRepository(SQLAlchemyCrudRepository):
    model_type = User

with Session(engine) as session:
    repo = UserRepository(session)
    user = repo.create(UserCreate(name="Alice", email="alice@example.com"))
    user = repo.get(user.id)
    updated = repo.update(user, UserUpdate(name="Alice Updated"))
    repo.delete(updated)
```

## Repository Patterns

| Pattern | Use Case | Schema |
|---------|----------|--------|
| **[Simple](tutorial/simple-pattern.md)** | Prototypes, simple CRUD | Model is schema |
| **[CRUD](tutorial/crud-pattern.md)** | Production APIs, validation | Separate schemas |

## Features

- 📚 **[Explore all features](features.md)**
- 🎓 **[Learn with tutorials](tutorial/index.md)**
- 🗂️ **Repository pattern** for clean data access
- 🎨 **Model mixins** for reusable functionality
- 🛠️ **SQLAlchemy integration** built-in
- 🔧 **Extensible design** for custom implementations

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/javalce/database-utils/blob/main/LICENSE) file for details.

---

**Made with ❤️ by [Javier Valero Cejudo](https://github.com/javalce)**

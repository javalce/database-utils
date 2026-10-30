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
- ✅ Type-safe repository pattern when you need it
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

Define your SQLAlchemy models with `SQLAlchemyBase`:

```python
from sqlalchemy import mapped_column, Integer, String, Mapped, create_engine, select
from database_utils.sqlalchemy import SQLAlchemyBase

class User(SQLAlchemyBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

engine = create_engine("sqlite:///db.sqlite")
SQLAlchemyBase.metadata.create_all(engine)

with Session(engine) as session:
    # Create
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()

    # Query
    stmt = select(User).where(User.email == "alice@example.com")
    result = session.scalar(stmt)
```

`SQLAlchemyBase` proporciona:

- Convenciones de nombres para migraciones
- Base declarativa lista para Alembic
- Type safety con Mapped y mapped_column

## Next Steps

- 📖 Read the [documentation](https://github.com/javalce/database-utils)
- 🐛 Report issues on [GitHub](https://github.com/javalce/database-utils/issues)
- 🤝 Contribute on [GitHub](https://github.com/javalce/database-utils)

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/javalce/database-utils/blob/main/LICENSE) file for details.

---

**Made with ❤️ by [Javier Valero Cejudo](https://github.com/javalce)**

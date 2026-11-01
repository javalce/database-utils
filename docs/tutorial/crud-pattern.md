---
icon: lucide/layers
---

# CRUD Pattern Tutorial

Learn how to use `SQLAlchemyCrudRepository` with separate input and update schemas for robust data handling.

## When to Use

The CRUD pattern is perfect when:

- You need input validation separate from your model
- You want different fields for creation vs. updates
- You're building a production API with strict contracts
- Your models and API schemas should be decoupled

## Setup

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
```

### 2. Define Input Schemas

Use dataclasses or Pydantic models:

```python
from dataclasses import dataclass

@dataclass
class UserCreate:
    """Schema for creating a user"""
    name: str
    email: str

@dataclass
class UserUpdate:
    """Schema for updating a user (all fields optional)"""
    name: str | None = None
    email: str | None = None
```

Or with Pydantic (recommended for validation):

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """Schema for creating a user"""
    name: str
    email: EmailStr

class UserUpdate(BaseModel):
    """Schema for updating a user (all fields optional)"""
    name: str | None = None
    email: EmailStr | None = None
```

### 3. Create Your Repository

```python
from database_utils.sqlalchemy import SQLAlchemyCrudRepository

class UserRepository(SQLAlchemyCrudRepository):
    model_type = User
```

### 4. Initialize Database

```python
engine = create_engine("sqlite:///db.sqlite")
SQLAlchemyBase.metadata.create_all(engine)
```

## Operations

### Create

Create with validation schema using `create()`:

```python
with Session(engine) as session:
    repo = UserRepository(session)
    
    # Create request data
    user_data = UserCreate(name="Alice", email="alice@example.com")
    
    # Create saves and returns the model
    user = repo.create(user_data)
    
    print(user.id)  # Auto-generated
    print(user.name)  # "Alice"
```

### Read

Retrieve records with `list()` and `get()`:

```python
with Session(engine) as session:
    repo = UserRepository(session)
    
    # Get all users
    all_users = repo.list()
    print(len(all_users))
    
    # Get by ID
    user = repo.get(1)
    if user:
        print(user.name)
```

### Update

Modify with validation schema using `update()`:

```python
with Session(engine) as session:
    repo = UserRepository(session)
    
    # Retrieve the user to update
    user = repo.get(1)
    if not user:
        raise ValueError("User not found")
    
    # Update with partial data (fields not provided stay unchanged)
    update_data = UserUpdate(name="Alice Updated")
    updated = repo.update(user, update_data)
    
    print(updated.name)  # "Alice Updated"
    print(updated.email)  # Still "alice@example.com"
```

### Delete

Remove records with `delete()`:

```python
with Session(engine) as session:
    repo = UserRepository(session)
    
    # Retrieve
    user = repo.get(1)
    
    # Delete
    repo.delete(user)
    
    # After session commit, it's removed from database
```

## Complete Example

```python
from dataclasses import dataclass
from sqlalchemy import String, create_engine
from sqlalchemy.orm import Mapped, mapped_column, Session
from database_utils.sqlalchemy import SQLAlchemyBase, SQLAlchemyCrudRepository

# 1. Define model
class User(SQLAlchemyBase):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)

# 2. Define schemas
@dataclass
class UserCreate:
    name: str
    email: str

@dataclass
class UserUpdate:
    name: str | None = None
    email: str | None = None

# 3. Create repository
class UserRepository(SQLAlchemyCrudRepository):
    model_type = User

# 4. Setup database
engine = create_engine("sqlite:///db.sqlite")
SQLAlchemyBase.metadata.create_all(engine)

# 5. Use it
with Session(engine) as session:
    repo = UserRepository(session)
    
    # Create
    user_data = UserCreate(name="Alice", email="alice@example.com")
    user = repo.create(user_data)
    print(f"Created: {user.name}")
    
    # Read
    user = repo.get(user.id)
    print(f"Retrieved: {user.name}")
    
    # Update (partial)
    update_data = UserUpdate(name="Alice Updated")
    updated = repo.update(user, update_data)
    print(f"Updated: {updated.name}, email still: {updated.email}")
    
    # Delete
    repo.delete(updated)
    
    # Verify deletion
    deleted = repo.get(user.id)
    print(f"After delete: {deleted}")  # None (after commit)
    
    session.commit()
```

## Validation with Pydantic

For stronger validation, use Pydantic models:

```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr

class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None

# Usage with FastAPI
from fastapi import FastAPI

app = FastAPI()

@app.post("/users")
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    repo = UserRepository(session)
    user = repo.create(user_data)
    session.commit()
    return user

@app.put("/users/{user_id}")
def update_user(user_id: int, user_data: UserUpdate, session: Session = Depends(get_session)):
    repo = UserRepository(session)
    user = repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404)
    updated = repo.update(user, user_data)
    session.commit()
    return updated
```

## Tips

### Partial Updates

The CRUD pattern naturally handles partial updates:

```python
# Only update name, email stays unchanged
update_data = UserUpdate(name="New Name", email=None)
updated = repo.update(user, update_data)
# email field was None, so it wasn't changed
```

### Autocommit

Like the simple pattern, `update()` calls `flush()` but you need to commit:

```python
with Session(engine) as session:
    repo = UserRepository(session)
    user = repo.get(1)
    
    # Changes visible in session
    repo.update(user, UserUpdate(name="Updated"))
    
    # But not persisted until:
    session.commit()
```

### Combined with Mixins

Add timestamps and soft deletes:

```python
from database_utils.sqlalchemy.mixins import TimestampMixin, SoftDeleteMixin

class User(SQLAlchemyBase, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    # created_at, updated_at, is_deleted, deleted_at automatically included
```

### Custom Validation Logic

Extend repository for domain logic:

```python
class UserRepository(SQLAlchemyCrudRepository):
    model_type = User
    
    def create_with_defaults(self, user_data: UserCreate) -> User:
        """Custom create with business logic"""
        # Could add defaults, validation, etc.
        return self.create(user_data)

# Usage
user = repo.create_with_defaults(UserCreate(name="Alice", email="alice@example.com"))
```



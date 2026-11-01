---
icon: lucide/sparkles
---

# Features

Database Utils provides a set of utilities designed to simplify working with databases in Python, without sacrificing flexibility or control.

## Core Features

### Repository Pattern

A generic and type-safe abstraction for database operations. Two patterns to choose from:

- **Simple Pattern** - Direct model operations with `save()` and `delete()`
- **CRUD Pattern** - Full schema flexibility with `create()`, `update()`, and `delete()`

Benefits:
- **Generic typing** - Full support for TypeVar, maintaining type safety
- **Flexible implementations** - Extend with your own operations
- **Abstraction layer** - Decouple your code from the specific database

### Zero Dependencies Core

The core module has no external dependencies. Install only what you need:

- Core `database-utils` - No dependencies
- SQLAlchemy integration - Only required if using the SQLAlchemy module
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

Declarative base class with built-in naming conventions for database constraints:

- **Indexes** - `idx_tablename_column`
- **Foreign keys** - `fk_tablename_column_referred_table`
- **Unique constraints** - `uq_tablename_column`
- **Check constraints** - `ck_tablename_constraint`

**Benefits:**
- Alembic ready - Compatible with automatic migrations
- Production grade - Designed for production projects
- Consistent - Naming conventions across your project

### Repository Patterns

#### SQLAlchemyRepository

For straightforward use cases where the model is the schema.

Operations:
- `list()` - Get all records
- `get(id)` - Get a record by ID
- `save(model)` - Create or update a record
- `delete(model)` - Delete a record

**Use when:**
- You don't need separate DTOs
- The model itself is your data transfer object
- You want minimal boilerplate

#### SQLAlchemyCrudRepository

For complex applications with separate schemas for input and updates.

Operations:
- `list()` - Get all records
- `get(id)` - Get a record by ID
- `create(obj_in)` - Create with validation schema
- `update(db_obj, obj_in)` - Update with partial schema
- `delete(model)` - Delete a record

**Use when:**
- You need validation and transformation on input data
- You want to use Pydantic or dataclasses for schemas
- You need fine-grained control over creation vs. update logic
- Your API and persistence models differ

### Model Mixins

Reusable mixins for common functionality:

- `TimestampMixin` - Automatic `created_at` and `updated_at` fields
- `SoftDeleteMixin` - Soft delete support with `is_deleted` and `deleted_at`
- Customize for your specific needs

## Integrated Best Practices

Database Utils incorporates best practices from SQLAlchemy and Alembic:

- ✅ **Concurrent migrations** - Conventions for Alembic
- ✅ **Query optimization** - Type-safe queries
- ✅ **Constraint safety** - Consistent naming for constraints
- ✅ **Schema versioning** - Compatible with migrations
- ✅ **Flexible patterns** - Choose the right pattern for your needs



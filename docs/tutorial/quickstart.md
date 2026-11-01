---
icon: lucide/book-open
---

# Tutorials

Learn by doing with step-by-step guides for each repository pattern.

## Choose Your Pattern

### [Simple Pattern](simple-pattern.md)

Direct model operations without separate schemas. Best for:
- Simple CRUD applications
- Prototypes and MVPs
- Internal tools and scripts

**Quick example:**
```python
repo = UserRepository(session)
user = User(name="Alice", email="alice@example.com")
saved = repo.save(user)
repo.delete(saved)
```

### [CRUD Pattern](crud-pattern.md)

Separate input and update schemas with validation. Best for:
- Production APIs with validation
- Complex data transformation
- Clear separation of concerns

**Quick example:**
```python
repo = UserRepository(session)
user = repo.create(UserCreate(name="Alice", email="alice@example.com"))
updated = repo.update(user, UserUpdate(name="Alice Updated"))
repo.delete(user)
```

---

Start with the pattern that matches your use case.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeGuard

if TYPE_CHECKING:
    from pydantic import BaseModel


def is_pydantic_model(obj: Any) -> TypeGuard[BaseModel]:
    try:
        from pydantic import BaseModel
    except ImportError:
        return False

    return isinstance(obj, BaseModel)

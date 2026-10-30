"""Tests for database_utils._internal.utils module."""
import pytest

from database_utils._internal.utils import is_pydantic_model


class MockNonPydanticClass:
    """Non-Pydantic class for testing."""

    def __init__(self, name: str) -> None:
        self.name = name


class TestIsPydanticModel:
    """Test is_pydantic_model utility function."""

    def test_returns_false_for_none(self) -> None:
        """Test that is_pydantic_model returns False for None."""
        result = is_pydantic_model(None)
        assert result is False

    def test_returns_false_for_regular_object(self) -> None:
        """Test that is_pydantic_model returns False for regular objects."""
        obj = MockNonPydanticClass("test")
        result = is_pydantic_model(obj)
        assert result is False

    def test_returns_false_for_dict(self) -> None:
        """Test that is_pydantic_model returns False for dict."""
        result = is_pydantic_model({"name": "test"})
        assert result is False

    def test_returns_false_for_string(self) -> None:
        """Test that is_pydantic_model returns False for string."""
        result = is_pydantic_model("test string")
        assert result is False

    def test_returns_false_for_int(self) -> None:
        """Test that is_pydantic_model returns False for int."""
        result = is_pydantic_model(42)
        assert result is False

    def test_returns_false_for_list(self) -> None:
        """Test that is_pydantic_model returns False for list."""
        result = is_pydantic_model([1, 2, 3])
        assert result is False

    def test_returns_true_for_pydantic_model(self) -> None:
        """Test that is_pydantic_model returns True for Pydantic models."""
        try:
            from pydantic import BaseModel

            class TestModel(BaseModel):
                name: str
                value: int

            obj = TestModel(name="test", value=42)
            result = is_pydantic_model(obj)
            assert result is True
        except ImportError:
            pytest.skip("pydantic not installed")

    def test_type_guard_enables_narrowing(self) -> None:
        """Test that is_pydantic_model can be used as a type guard."""
        try:
            from pydantic import BaseModel

            class Model(BaseModel):
                value: str

            obj: object = Model(value="test")

            # This should work with type checking
            if is_pydantic_model(obj):
                # obj should be narrowed to BaseModel type
                assert hasattr(obj, "model_dump")
        except ImportError:
            pytest.skip("pydantic not installed")

    def test_pydantic_v2_compatibility(self) -> None:
        """Test that function works with Pydantic v2."""
        try:
            from pydantic import BaseModel

            class UserModel(BaseModel):
                id: int
                name: str

            user = UserModel(id=1, name="John")
            result = is_pydantic_model(user)

            assert result is True

            # Verify we can access Pydantic v2 methods
            assert hasattr(user, "model_dump")
        except ImportError:
            pytest.skip("pydantic not installed")

    def test_multiple_pydantic_models(self) -> None:
        """Test with multiple different Pydantic models."""
        try:
            from pydantic import BaseModel

            class Model1(BaseModel):
                x: int

            class Model2(BaseModel):
                y: str

            m1 = Model1(x=1)
            m2 = Model2(y="test")

            assert is_pydantic_model(m1) is True
            assert is_pydantic_model(m2) is True
        except ImportError:
            pytest.skip("pydantic not installed")

    def test_isinstance_check_with_basemodel(self) -> None:
        """Test the underlying isinstance check."""
        try:
            from pydantic import BaseModel

            class TestModel(BaseModel):
                name: str

            instance = TestModel(name="test")

            # Verify that the instance is actually a BaseModel
            assert isinstance(instance, BaseModel)

            # And that our function detects it
            assert is_pydantic_model(instance) is True
        except ImportError:
            pytest.skip("pydantic not installed")

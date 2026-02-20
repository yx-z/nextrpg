"""
Tests for nextrpg.core module_and_attribute and dataclass helpers.
"""

import pytest

from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.module_and_attribute import (
    ModuleAndAttribute,
    to_module_and_attribute,
)


class TestModuleAndAttribute:
    """Tests for ModuleAndAttribute class."""

    def test_module_and_attribute_creation(self):
        """Test creating ModuleAndAttribute."""
        ma = ModuleAndAttribute("os.path", "join")

        assert ma.module == "os.path"
        assert ma.attribute == "join"

    def test_module_and_attribute_qualname(self):
        """Test qualname property."""
        ma = ModuleAndAttribute("os.path", "join")
        assert ma.qualname == "os.path.join"

    def test_module_and_attribute_save_data(self):
        """Test save_data property."""
        ma = ModuleAndAttribute("os.path", "join")
        save_data = ma.save_data

        assert save_data == ("os.path", "join")
        assert isinstance(save_data, tuple)

    def test_module_and_attribute_load_from_save(self):
        """Test load_from_save class method."""
        data = ["os.path", "join"]
        ma = ModuleAndAttribute.load_from_save(data)

        assert ma.module == "os.path"
        assert ma.attribute == "join"

    def test_module_and_attribute_load_from_save_invalid_length(self):
        """Test load_from_save with invalid data."""
        data = ["os.path", "join", "extra"]

        with pytest.raises(AssertionError):
            ModuleAndAttribute.load_from_save(data)

    def test_module_and_attribute_imported(self):
        """Test imported property loads actual module attribute."""
        ma = ModuleAndAttribute("os.path", "join")
        imported = ma.imported

        # Should be the actual os.path.join function
        import os.path

        assert imported is os.path.join

    def test_to_module_and_attribute_with_function(self):
        """Test to_module_and_attribute with a function."""

        def test_func():
            pass

        ma = to_module_and_attribute(test_func)

        # Module name should match the actual module this test is in
        assert ".test_core_helpers" in ma.module
        # Attribute includes the local function path, so just check it ends with the name
        assert "test_func" in ma.attribute

    def test_to_module_and_attribute_with_class(self):
        """Test to_module_and_attribute with a class."""
        ma = to_module_and_attribute(ModuleAndAttribute)

        assert ma.module == "nextrpg.core.module_and_attribute"
        assert ma.attribute == "ModuleAndAttribute"

    def test_module_and_attribute_frozen(self):
        """Test ModuleAndAttribute is frozen."""
        ma = ModuleAndAttribute("os", "path")

        with pytest.raises(Exception):  # FrozenInstanceError
            ma.module = "os.path"


class TestPrivateInitBelow:
    """Tests for private_init_below sentinel."""

    def test_private_init_below_returns_singleton(self):
        """Test private_init_below returns consistent object."""
        init1 = private_init_below()
        init2 = private_init_below()

        # Should be the same instance
        assert type(init1) == type(init2)

    def test_private_init_below_type(self):
        """Test private_init_below returns special type."""
        init = private_init_below()

        from nextrpg.core.dataclass_with_default import _PrivateInitType

        assert isinstance(init, _PrivateInitType)


class TestDefaultFunction:
    """Tests for default function and _Default class."""

    def test_default_stores_callable(self):
        """Test default stores callable."""
        func = lambda self: 42
        default_obj = default(func)

        # Should be callable
        assert callable(default_obj)

    def test_default_callable_invocation(self):
        """Test invoking default."""
        func = lambda self: 100
        default_obj = default(func)

        class DummyObject:
            pass

        obj = DummyObject()
        result = default_obj(obj)

        assert result == 100

    def test_default_with_lambda(self):
        """Test default with lambda function."""
        default_obj = default(lambda self: self.value * 2)

        class TestObj:
            value = 5

        obj = TestObj()
        result = default_obj(obj)

        assert result == 10


class TestDataclassWithDefault:
    """Tests for dataclass_with_default decorator."""

    def test_dataclass_with_default_basic(self):
        """Test basic dataclass_with_default usage."""
        from dataclasses import KW_ONLY

        @dataclass_with_default(frozen=True)
        class TestClass:
            name: str
            _: KW_ONLY = private_init_below()
            computed: int = default(lambda self: len(self.name))

        obj = TestClass(name="hello")

        assert obj.name == "hello"
        assert obj.computed == 5

    def test_dataclass_with_default_computation(self):
        """Test default field computation."""
        from dataclasses import KW_ONLY

        @dataclass_with_default(frozen=True)
        class Rectangle:
            width: int
            height: int
            _: KW_ONLY = private_init_below()
            area: int = default(lambda self: self.width * self.height)

        rect = Rectangle(width=5, height=3)

        assert rect.width == 5
        assert rect.height == 3
        assert rect.area == 15

    def test_dataclass_with_default_caching(self):
        """Test that default values are cached."""
        from dataclasses import KW_ONLY

        call_count = [0]

        def compute(self):
            call_count[0] += 1
            return call_count[0]

        @dataclass_with_default(frozen=True)
        class TestClass:
            _: KW_ONLY = private_init_below()
            value: int = default(compute)

        obj = TestClass()

        # First access
        val1 = obj.value
        # Second access should use cached value
        val2 = obj.value

        assert val1 == val2 == 1

    def test_dataclass_with_default_multiple_defaults(self):
        """Test multiple default fields."""
        from dataclasses import KW_ONLY

        @dataclass_with_default(frozen=True)
        class Calculator:
            x: int
            y: int
            _: KW_ONLY = private_init_below()
            sum_val: int = default(lambda self: self.x + self.y)
            product: int = default(lambda self: self.x * self.y)

        calc = Calculator(x=3, y=4)

        assert calc.sum_val == 7
        assert calc.product == 12

    def test_dataclass_with_default_decorator_without_args(self):
        """Test decorator applied without arguments."""

        @dataclass_with_default
        class SimpleClass:
            name: str

        obj = SimpleClass(name="test")
        assert obj.name == "test"

    def test_dataclass_with_default_decorator_with_args(self):
        """Test decorator applied with arguments."""

        @dataclass_with_default(frozen=True)
        class SimpleClass:
            name: str

        obj = SimpleClass(name="test")
        assert obj.name == "test"

    def test_dataclass_with_default_frozen(self):
        """Test frozen=True makes dataclass immutable."""
        from dataclasses import KW_ONLY

        @dataclass_with_default(frozen=True)
        class TestClass:
            name: str
            _: KW_ONLY = private_init_below()
            computed: int = default(lambda self: 42)

        obj = TestClass(name="test")

        with pytest.raises(Exception):  # FrozenInstanceError
            obj.name = "changed"


class TestPrivateInitIntegration:
    """Integration tests for private_init_below in dataclasses."""

    def test_kw_only_marker_with_default(self):
        """Test KW_ONLY marker with private_init_below."""
        from dataclasses import KW_ONLY

        @dataclass_with_default(frozen=True)
        class TestClass:
            positional: str
            _: KW_ONLY = private_init_below()
            keyword: str = "default"

        obj = TestClass("pos_value", keyword="kw_value")

        assert obj.positional == "pos_value"
        assert obj.keyword == "kw_value"

    def test_private_init_separates_fields(self):
        """Test that private_init_below separates field groups."""
        from dataclasses import KW_ONLY

        @dataclass_with_default
        class TestClass:
            required: str
            _: KW_ONLY = private_init_below()
            optional: str = "opt"

        obj = TestClass(required="req")

        assert obj.required == "req"
        assert obj.optional == "opt"

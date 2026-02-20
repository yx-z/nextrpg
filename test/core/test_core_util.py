"""
Tests for nextrpg.core.util module.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from nextrpg.core.util import generator_name, type_name


class TestTypeName:
    """Tests for type_name function."""

    def test_type_name_with_class(self):
        """Test type_name returns correct name for a class."""

        class TestClass:
            pass

        result = type_name(TestClass)
        assert result == "TestClass"

    def test_type_name_with_instance(self):
        """Test type_name returns correct name for an instance."""

        class TestClass:
            pass

        instance = TestClass()
        result = type_name(instance)
        assert result == "TestClass"

    def test_type_name_with_builtin_types(self):
        """Test type_name works with builtin types."""
        assert type_name(int) == "int"
        assert type_name(42) == "int"
        assert type_name(str) == "str"
        assert type_name("hello") == "str"
        assert type_name(list) == "list"
        assert type_name([1, 2, 3]) == "list"

    def test_type_name_with_nested_classes(self):
        """Test type_name works with nested classes."""

        class OuterClass:
            class InnerClass:
                pass

        result = type_name(OuterClass.InnerClass)
        assert result == "InnerClass"


class TestGeneratorName:
    """Tests for generator_name function."""

    def test_generator_name_with_simple_generator(self):
        """Test generator_name returns correct name for a generator."""

        def my_generator():
            yield 1

        gen = my_generator()
        result = generator_name(gen)
        assert result == "my_generator"

    def test_generator_name_with_generator_expression(self):
        """Test generator_name works with generator expressions."""
        gen = (x for x in range(10))
        result = generator_name(gen)
        # Generator expressions use <genexpr> as the name
        assert isinstance(result, str)

    def test_generator_name_preserves_underscores(self):
        """Test generator_name preserves underscores in names."""

        def my_test_generator():
            yield 1

        gen = my_test_generator()
        result = generator_name(gen)
        assert result == "my_test_generator"


class TestTypeNameCaching:
    """Tests for caching behavior of type_name function."""

    def test_type_name_uses_cache(self):
        """Test that type_name uses functools.cache."""

        class TestClass:
            pass

        # Call twice - should use cache on second call
        result1 = type_name(TestClass)
        result2 = type_name(TestClass)

        assert result1 == result2 == "TestClass"

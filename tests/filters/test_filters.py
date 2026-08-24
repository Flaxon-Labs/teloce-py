"""
Tests for the filters module.
"""

import pytest

from teloce.filters.registry import FilterRegistry
from teloce.filters.strings import StringFilters
from teloce.filters.numbers import NumberFilters
from teloce.filters.dates import DateFilters
from teloce.filters.arrays import ArrayFilters
from teloce.filters.objects import ObjectFilters


class TestFilters:
    """Tests for filters."""

    def test_string_capitalize(self):
        """Test capitalize filter."""
        assert StringFilters.capitalize("hello") == "Hello"
        assert StringFilters.capitalize("HELLO") == "Hello"
        assert StringFilters.capitalize("") == ""

    def test_string_uppercase(self):
        """Test uppercase filter."""
        assert StringFilters.uppercase("hello") == "HELLO"
        assert StringFilters.uppercase("") == ""

    def test_string_lowercase(self):
        """Test lowercase filter."""
        assert StringFilters.lowercase("HELLO") == "hello"
        assert StringFilters.lowercase("") == ""

    def test_string_trim(self):
        """Test trim filter."""
        assert StringFilters.trim("  hello  ") == "hello"
        assert StringFilters.trim("") == ""

    def test_string_truncate(self):
        """Test truncate filter."""
        assert StringFilters.truncate("hello world", 5) == "hello..."
        assert StringFilters.truncate("hello", 10) == "hello"

    def test_string_slugify(self):
        """Test slugify filter."""
        assert StringFilters.slugify("Hello World") == "hello-world"
        assert StringFilters.slugify("Hello! World!") == "hello-world"

    def test_number_currency(self):
        """Test currency filter."""
        assert NumberFilters.currency(19.99) == "$19.99"
        assert NumberFilters.currency(19.99, "€") == "€19.99"

    def test_number_percent(self):
        """Test percent filter."""
        assert NumberFilters.percent(0.25) == "25%"
        assert NumberFilters.percent(0.333, 1) == "33.3%"

    def test_number_round(self):
        """Test round filter."""
        assert NumberFilters.round(1.5) == 2
        assert NumberFilters.round(1.4) == 1

    def test_date_format(self):
        """Test date format filter."""
        import datetime
        dt = datetime.datetime(2024, 1, 15, 10, 30)
        assert DateFilters.date_format(dt, "%Y-%m-%d") == "2024-01-15"

    def test_array_join(self):
        """Test join filter."""
        assert ArrayFilters.join(["a", "b", "c"]) == "a, b, c"
        assert ArrayFilters.join(["a", "b", "c"], "-") == "a-b-c"

    def test_array_first(self):
        """Test first filter."""
        assert ArrayFilters.first([1, 2, 3]) == 1
        assert ArrayFilters.first([]) is None

    def test_array_last(self):
        """Test last filter."""
        assert ArrayFilters.last([1, 2, 3]) == 3
        assert ArrayFilters.last([]) is None

    def test_object_keys(self):
        """Test keys filter."""
        assert ObjectFilters.keys({"a": 1, "b": 2}) == ["a", "b"]
        assert ObjectFilters.keys({}) == []

    def test_object_values(self):
        """Test values filter."""
        assert ObjectFilters.values({"a": 1, "b": 2}) == [1, 2]
        assert ObjectFilters.values({}) == []

    def test_object_pick(self):
        """Test pick filter."""
        obj = {"a": 1, "b": 2, "c": 3}
        assert ObjectFilters.pick(obj, "a", "c") == {"a": 1, "c": 3}

    def test_object_omit(self):
        """Test omit filter."""
        obj = {"a": 1, "b": 2, "c": 3}
        assert ObjectFilters.omit(obj, "b") == {"a": 1, "c": 3}

    def test_registry(self):
        """Test filter registry."""
        registry = FilterRegistry()
        registry.register_func("test", lambda x: x, "Test filter")
        
        assert registry.has("test")
        assert registry.get("test") is not None
        registry.register_js("suffix", "value => String(value) + '!'")
        assert registry.get_js_filters()["suffix"].startswith("value =>")

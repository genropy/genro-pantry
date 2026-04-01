# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""End-to-end test for the decorator."""

import pytest

from pantry._registry import Pantry


class TestDecoratorEndToEnd:
    def test_with_installed_package(self):
        p = Pantry()

        @p("pip")
        def use_pip():
            return "ok"

        assert use_pip() == "ok"

    def test_with_missing_package(self):
        p = Pantry()

        @p("nonexistent-pkg-xyz-999")
        def needs_exotic():
            pass

        with pytest.raises(RuntimeError, match="requires: nonexistent-pkg-xyz-999"):
            needs_exotic()

    def test_preserves_function_metadata(self):
        p = Pantry()

        @p("pip")
        def my_function():
            """My docstring."""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

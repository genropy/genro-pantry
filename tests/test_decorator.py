# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""End-to-end test for the standalone requires() decorator."""

import pytest

from pantry._registry import Pantry


class TestRequiresEndToEnd:
    def test_with_installed_package(self, tmp_path):
        """Use a real pyproject.toml that lists 'packaging' — known to be installed."""
        content = """
[project]
name = "demo"

[project.optional-dependencies]
core = ["packaging"]
"""
        toml_path = tmp_path / "pyproject.toml"
        toml_path.write_text(content)
        p = Pantry.from_pyproject(toml_path)

        @p("packaging")
        def use_packaging():
            import packaging
            return packaging.__name__

        assert use_packaging() == "packaging"

    def test_with_missing_package(self, tmp_path):
        """Decorator must raise for a package that is not installed."""
        content = """
[project]
name = "demo"

[project.optional-dependencies]
exotic = ["nonexistent-pkg-xyz-999"]
"""
        toml_path = tmp_path / "pyproject.toml"
        toml_path.write_text(content)
        p = Pantry.from_pyproject(toml_path)

        @p("nonexistent-pkg-xyz-999")
        def needs_exotic():
            pass

        with pytest.raises(RuntimeError, match="requires: nonexistent-pkg-xyz-999"):
            needs_exotic()

    def test_preserves_function_metadata(self, tmp_path):
        content = """
[project]
name = "demo"

[project.optional-dependencies]
core = ["packaging"]
"""
        toml_path = tmp_path / "pyproject.toml"
        toml_path.write_text(content)
        p = Pantry.from_pyproject(toml_path)

        @p("packaging")
        def my_function():
            """My docstring."""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

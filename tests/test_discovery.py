# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Tests for pantry._discovery."""

import pytest

from pantry._discovery import find_pyproject, parse_optional_deps


class TestFindPyproject:
    def test_finds_in_current_dir(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
        result = find_pyproject(tmp_path)
        assert result == tmp_path / "pyproject.toml"

    def test_walks_upward(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
        child = tmp_path / "a" / "b" / "c"
        child.mkdir(parents=True)
        result = find_pyproject(child)
        assert result == tmp_path / "pyproject.toml"

    def test_raises_when_missing(self, tmp_path):
        # Create a deeply nested dir with no pyproject.toml anywhere
        leaf = tmp_path / "no" / "toml" / "here"
        leaf.mkdir(parents=True)
        with pytest.raises(FileNotFoundError, match="pyproject.toml not found"):
            find_pyproject(leaf)


class TestParseOptionalDeps:
    def test_parses_groups(self, tmp_path):
        content = """
[project]
name = "demo"

[project.optional-dependencies]
imaging = ["pillow>=9.0", "wand"]
data = ["numpy", "pandas>=2.0"]
"""
        toml_path = tmp_path / "pyproject.toml"
        toml_path.write_text(content)
        result = parse_optional_deps(toml_path)
        assert result == {
            "imaging": ["pillow>=9.0", "wand"],
            "data": ["numpy", "pandas>=2.0"],
        }

    def test_missing_section_returns_empty(self, tmp_path):
        content = "[project]\nname = 'demo'\n"
        toml_path = tmp_path / "pyproject.toml"
        toml_path.write_text(content)
        result = parse_optional_deps(toml_path)
        assert result == {}

    def test_missing_project_returns_empty(self, tmp_path):
        content = "[build-system]\nrequires = ['hatchling']\n"
        toml_path = tmp_path / "pyproject.toml"
        toml_path.write_text(content)
        result = parse_optional_deps(toml_path)
        assert result == {}

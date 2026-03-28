# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""Tests for pantry._registry.Pantry."""

import types

import pytest

from pantry._registry import Pantry


def _make_probe(pkg_name, module_name, available, version=None):
    """Build a probe-result dict for testing."""
    mod = types.ModuleType(module_name) if available else None
    return {
        "pkg_name": pkg_name,
        "module_name": module_name,
        "module": mod,
        "version": version,
        "available": available,
    }


@pytest.fixture
def sample_pantry():
    data = {
        "pillow": _make_probe("pillow", "PIL", True, "10.1.0"),
        "wand": _make_probe("wand", "wand", False),
        "numpy": _make_probe("numpy", "numpy", True, "1.26.0"),
    }
    groups = {
        "imaging": ["pillow", "wand"],
        "data": ["numpy"],
    }
    return Pantry(data, groups)


class TestHas:
    def test_available(self, sample_pantry):
        assert sample_pantry.has("pillow") is True

    def test_unavailable(self, sample_pantry):
        assert sample_pantry.has("wand") is False

    def test_unknown(self, sample_pantry):
        assert sample_pantry.has("nonexistent") is False

    def test_multiple_all_available(self, sample_pantry):
        assert sample_pantry.has("pillow", "numpy") is True

    def test_multiple_some_missing(self, sample_pantry):
        assert sample_pantry.has("pillow", "wand") is False


class TestHasGroup:
    def test_group_with_available(self, sample_pantry):
        assert sample_pantry.has_group("imaging") is True

    def test_group_all_available(self, sample_pantry):
        assert sample_pantry.has_group("data") is True

    def test_unknown_group(self, sample_pantry):
        assert sample_pantry.has_group("nonexistent") is False


class TestGet:
    def test_returns_module(self, sample_pantry):
        mod = sample_pantry.get("pillow")
        assert isinstance(mod, types.ModuleType)
        assert mod.__name__ == "PIL"

    def test_returns_none_unavailable(self, sample_pantry):
        assert sample_pantry.get("wand") is None

    def test_returns_none_unknown(self, sample_pantry):
        assert sample_pantry.get("nonexistent") is None

    def test_default_on_unavailable(self, sample_pantry):
        sentinel = object()
        assert sample_pantry.get("wand", sentinel) is sentinel

    def test_default_on_unknown(self, sample_pantry):
        assert sample_pantry.get("nonexistent", 42) == 42

    def test_default_not_used_when_available(self, sample_pantry):
        mod = sample_pantry.get("pillow", "fallback")
        assert isinstance(mod, types.ModuleType)


class TestGetItem:
    def test_returns_module(self, sample_pantry):
        mod = sample_pantry["pillow"]
        assert isinstance(mod, types.ModuleType)
        assert mod.__name__ == "PIL"

    def test_raises_when_unavailable(self, sample_pantry):
        with pytest.raises(RuntimeError, match="'wand' is not available"):
            sample_pantry["wand"]

    def test_raises_when_unknown(self, sample_pantry):
        with pytest.raises(RuntimeError, match="'nonexistent' is not available"):
            sample_pantry["nonexistent"]


class TestDecorator:
    def test_passes_when_available(self, sample_pantry):
        @sample_pantry("pillow", "numpy")
        def process():
            return "ok"

        assert process() == "ok"

    def test_raises_when_missing(self, sample_pantry):
        @sample_pantry("wand")
        def transform():
            return "ok"

        with pytest.raises(RuntimeError, match="transform requires: wand"):
            transform()

    def test_error_message_format(self, sample_pantry):
        @sample_pantry("wand", "nonexistent")
        def multi_dep():
            pass

        with pytest.raises(RuntimeError, match="pip install wand nonexistent"):
            multi_dep()


class TestReport:
    def test_report_content(self, sample_pantry):
        report = sample_pantry.report()
        assert "pantry report" in report
        assert "pillow" in report
        assert "PIL" in report
        assert "10.1.0" in report
        assert "\u2713" in report  # checkmark
        assert "\u2717" in report  # cross
        assert "available: 2/3" in report

    def test_report_empty(self):
        p = Pantry({}, {})
        report = p.report()
        assert "no optional dependencies" in report


class TestRepr:
    def test_repr(self, sample_pantry):
        assert repr(sample_pantry) == "Pantry(2/3 available)"


class TestFromPyproject:
    def test_from_pyproject(self, tmp_path):
        content = """
[project]
name = "demo"

[project.optional-dependencies]
tools = ["packaging"]
"""
        toml_path = tmp_path / "pyproject.toml"
        toml_path.write_text(content)
        p = Pantry.from_pyproject(toml_path)
        assert p.has("packaging") is True
        assert p.has_group("tools") is True

# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""Tests for pantry._registry.Pantry."""

import types

import pytest

from pantry._registry import Pantry


class TestHas:
    def test_installed_package(self):
        p = Pantry()
        assert p.has("pip") is True

    def test_missing_package(self):
        p = Pantry()
        assert p.has("nonexistent-package-xyz-999") is False

    def test_multiple_all_installed(self):
        p = Pantry()
        assert p.has("pip", "setuptools") is True

    def test_multiple_one_missing(self):
        p = Pantry()
        assert p.has("pip", "nonexistent-package-xyz-999") is False


class TestGet:
    def test_returns_module(self):
        p = Pantry()
        mod = p.get("json")
        # json is stdlib, no pip distribution — get returns None
        # use a real pip package instead
        mod = p.get("pip")
        assert mod is not None
        assert isinstance(mod, types.ModuleType)

    def test_returns_none_missing(self):
        p = Pantry()
        assert p.get("nonexistent-package-xyz-999") is None

    def test_returns_default(self):
        p = Pantry()
        sentinel = object()
        assert p.get("nonexistent-package-xyz-999", sentinel) is sentinel


class TestGetItem:
    def test_returns_module(self):
        p = Pantry()
        mod = p["pip"]
        assert isinstance(mod, types.ModuleType)

    def test_raises_missing(self):
        p = Pantry()
        with pytest.raises(RuntimeError, match="not available"):
            p["nonexistent-package-xyz-999"]

    def test_error_message_includes_install(self):
        p = Pantry()
        with pytest.raises(RuntimeError, match="pip install nonexistent-package-xyz-999"):
            p["nonexistent-package-xyz-999"]


class TestVersion:
    def test_installed_package(self):
        p = Pantry()
        ver = p.version("pip")
        assert ver is not None
        assert "." in ver  # version string like "24.0"

    def test_missing_package(self):
        p = Pantry()
        assert p.version("nonexistent-package-xyz-999") is None


class TestDecorator:
    def test_passes_when_available(self):
        p = Pantry()

        @p("pip")
        def my_func():
            return "ok"

        assert my_func() == "ok"

    def test_raises_when_missing(self):
        p = Pantry()

        @p("nonexistent-package-xyz-999")
        def my_func():
            return "ok"

        with pytest.raises(RuntimeError, match="requires"):
            my_func()

    def test_preserves_metadata(self):
        p = Pantry()

        @p("pip")
        def my_func():
            """My doc."""
            return "ok"

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My doc."


class TestReport:
    def test_report_with_args(self):
        p = Pantry()
        report = p.report("pip", "nonexistent-package-xyz-999")
        assert "pip" in report
        assert "nonexistent-package-xyz-999" in report
        assert "\u2713" in report
        assert "\u2717" in report

    def test_report_empty(self):
        p = Pantry()
        report = p.report()
        assert "no packages queried" in report

    def test_report_after_has(self):
        p = Pantry()
        p.has("pip")
        report = p.report()
        assert "pip" in report


class TestRepr:
    def test_repr(self):
        p = Pantry()
        p.has("pip")
        r = repr(p)
        assert "Pantry(" in r
        assert "available" in r


class TestSmartResolution:
    def test_pillow_to_pil(self):
        """If pillow is installed, its module name should be PIL."""
        p = Pantry()
        entry = p._probe("pillow")
        if entry["available"]:
            assert entry["module_name"] == "PIL"


class TestImportFallback:
    def test_stdlib_module_without_distribution(self):
        """Stdlib modules have no pip distribution but are importable."""
        p = Pantry()
        assert p.has("json") is True

    def test_get_stdlib_module(self):
        import json

        p = Pantry()
        mod = p.get("json")
        assert mod is json

    def test_getitem_stdlib_module(self):
        import json

        p = Pantry()
        assert p["json"] is json

    def test_truly_missing_module(self):
        p = Pantry()
        assert p.has("nonexistent_xyz_999") is False


class TestCaching:
    def test_probe_cached(self):
        p = Pantry()
        entry1 = p._probe("pip")
        entry2 = p._probe("pip")
        assert entry1 is entry2

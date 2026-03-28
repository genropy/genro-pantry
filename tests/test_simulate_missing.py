# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""Tests for pantry.simulate_missing context manager."""

import pytest

from pantry._registry import Pantry


def _pantry_with_packages() -> Pantry:
    """Create a Pantry with known probe data (no real imports needed)."""
    data = {
        "numpy": {"available": True, "module": None, "module_name": "numpy", "version": "1.26"},
        "pandas": {"available": True, "module": None, "module_name": "pandas", "version": "2.1"},
        "wand": {"available": False, "module": None, "module_name": "wand", "version": None},
    }
    groups = {"data": ["numpy", "pandas"], "imaging": ["wand"]}
    return Pantry(data, groups)


class TestSimulateMissing:
    def test_hides_package(self):
        p = _pantry_with_packages()
        assert p.has("numpy") is True
        with p.simulate_missing("numpy"):
            assert p.has("numpy") is False
        assert p.has("numpy") is True

    def test_hides_multiple(self):
        p = _pantry_with_packages()
        assert p.has("numpy", "pandas") is True
        with p.simulate_missing("numpy", "pandas"):
            assert p.has("numpy") is False
            assert p.has("pandas") is False
        assert p.has("numpy", "pandas") is True

    def test_get_returns_none(self):
        p = _pantry_with_packages()
        with p.simulate_missing("numpy"):
            assert p.get("numpy") is None

    def test_get_returns_default(self):
        p = _pantry_with_packages()
        with p.simulate_missing("numpy"):
            assert p.get("numpy", "fallback") == "fallback"

    def test_getitem_raises(self):
        p = _pantry_with_packages()
        with p.simulate_missing("numpy"), pytest.raises(RuntimeError, match="not available"):
            p["numpy"]

    def test_report_shows_hidden_as_unavailable(self):
        p = _pantry_with_packages()
        with p.simulate_missing("numpy"):
            report = p.report()
            # numpy still appears in the group but marked unavailable
            assert "\u2717" in report  # ✗ marker

    def test_restores_on_exception(self):
        p = _pantry_with_packages()
        with pytest.raises(ValueError, match="boom"), p.simulate_missing("numpy"):
            assert p.has("numpy") is False
            raise ValueError("boom")
        assert p.has("numpy") is True

    def test_unknown_package_is_noop(self):
        p = _pantry_with_packages()
        with p.simulate_missing("nonexistent"):
            assert p.has("numpy") is True

    def test_already_unavailable(self):
        p = _pantry_with_packages()
        assert p.has("wand") is False
        with p.simulate_missing("wand"):
            assert p.has("wand") is False
        assert p.has("wand") is False

    def test_decorator_respects_missing(self):
        p = _pantry_with_packages()

        @p("numpy")
        def compute():
            return "ok"

        assert compute() == "ok"
        with p.simulate_missing("numpy"), pytest.raises(RuntimeError, match="requires: numpy"):
            compute()
        assert compute() == "ok"

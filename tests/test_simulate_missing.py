# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""Tests for pantry.simulate_missing context manager."""

import pytest

from pantry._registry import Pantry


class TestSimulateMissing:
    def test_hides_package(self):
        p = Pantry()
        assert p.has("pip") is True
        with p.simulate_missing("pip"):
            assert p.has("pip") is False
        assert p.has("pip") is True

    def test_hides_multiple(self):
        p = Pantry()
        with p.simulate_missing("pip", "setuptools"):
            assert p.has("pip") is False
            assert p.has("setuptools") is False
        assert p.has("pip", "setuptools") is True

    def test_get_returns_none(self):
        p = Pantry()
        with p.simulate_missing("pip"):
            assert p.get("pip") is None

    def test_get_returns_default(self):
        p = Pantry()
        with p.simulate_missing("pip"):
            assert p.get("pip", "fallback") == "fallback"

    def test_getitem_raises(self):
        p = Pantry()
        with p.simulate_missing("pip"), pytest.raises(RuntimeError, match="not available"):
            p["pip"]

    def test_restores_on_exception(self):
        p = Pantry()
        with pytest.raises(ValueError, match="boom"), p.simulate_missing("pip"):
            assert p.has("pip") is False
            raise ValueError("boom")
        assert p.has("pip") is True

    def test_unknown_package_is_noop(self):
        p = Pantry()
        with p.simulate_missing("nonexistent-xyz"):
            assert p.has("pip") is True

    def test_report_shows_hidden_as_unavailable(self):
        p = Pantry()
        p.has("pip")
        with p.simulate_missing("pip"):
            report = p.report()
            assert "\u2717" in report

    def test_decorator_respects_missing(self):
        p = Pantry()

        @p("pip")
        def compute():
            return "ok"

        assert compute() == "ok"
        with p.simulate_missing("pip"), pytest.raises(RuntimeError, match="requires: pip"):
            compute()
        assert compute() == "ok"

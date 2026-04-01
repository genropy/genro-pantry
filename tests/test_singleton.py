# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""Tests for the module-level Pantry instance (import pantry)."""

from pantry._registry import Pantry


class TestModuleInstance:
    def test_import_returns_pantry_instance(self):
        import pantry
        assert isinstance(pantry, Pantry)

    def test_has_method_available(self):
        import pantry
        assert hasattr(pantry, "has")
        assert hasattr(pantry, "get")
        assert hasattr(pantry, "report")
        assert hasattr(pantry, "lazy_import")
        assert hasattr(pantry, "simulate_missing")

    def test_getitem_available(self):
        import pantry
        mod = pantry["pip"]
        assert mod.__name__ == "pip"

    def test_get_available(self):
        import pantry
        mod = pantry.get("pip")
        assert mod is not None

    def test_pantry_class_accessible(self):
        import pantry
        assert pantry.Pantry is Pantry

    def test_callable_decorator(self):
        import pantry

        @pantry("pip")
        def use_pkg():
            return "ok"

        assert use_pkg() == "ok"

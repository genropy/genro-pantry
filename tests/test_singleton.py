# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
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
        assert hasattr(pantry, "has_group")
        assert hasattr(pantry, "report")

    def test_getitem_available(self):
        import pantry
        # 'ruff' is in dev optional-dependencies — always installed in dev
        mod = pantry["ruff"]
        assert mod.__name__ == "ruff"

    def test_get_available(self):
        import pantry
        mod = pantry.get("ruff")
        assert mod is not None

    def test_pantry_class_accessible(self):
        import pantry
        assert pantry.Pantry is Pantry

    def test_callable_decorator(self):
        import pantry

        @pantry("ruff")
        def use_pkg():
            return "ok"

        assert use_pkg() == "ok"

# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Tests for pantry lazy_import — circular import breaker for own modules."""

import pytest

from pantry._registry import Pantry


def _empty_pantry() -> Pantry:
    return Pantry({}, {})


class TestRegistration:
    def test_registers_path(self):
        p = _empty_pantry()
        p.lazy_import("json")
        assert "json" in p._lazy

    def test_multiple_paths(self):
        p = _empty_pantry()
        p.lazy_import("json", "os", "sys")
        assert "json" in p._lazy
        assert "os" in p._lazy
        assert "sys" in p._lazy

    def test_idempotent_before_resolve(self):
        p = _empty_pantry()
        p.lazy_import("json")
        p.lazy_import("json")
        assert p._lazy["json"] is Pantry._UNRESOLVED

    def test_idempotent_after_resolve(self):
        """Re-registering after resolution must not reset the cache."""
        p = _empty_pantry()
        p.lazy_import("json")
        resolved = p["json"]
        p.lazy_import("json")
        assert p._lazy["json"] is resolved

    def test_does_not_affect_probe_data(self):
        p = _empty_pantry()
        p.lazy_import("json")
        assert "json" not in p._data


class TestResolution:
    def test_stdlib_module(self):
        import json

        p = _empty_pantry()
        p.lazy_import("json")
        assert p["json"] is json

    def test_stdlib_submodule(self):
        import xml.etree.ElementTree

        p = _empty_pantry()
        p.lazy_import("xml.etree.ElementTree")
        assert p["xml.etree.ElementTree"] is xml.etree.ElementTree

    def test_attribute_on_module(self):
        from collections import OrderedDict

        p = _empty_pantry()
        p.lazy_import("collections.OrderedDict")
        assert p["collections.OrderedDict"] is OrderedDict

    def test_class_on_submodule(self):
        from pathlib import PurePosixPath

        p = _empty_pantry()
        p.lazy_import("pathlib.PurePosixPath")
        assert p["pathlib.PurePosixPath"] is PurePosixPath

    def test_caching(self):
        p = _empty_pantry()
        p.lazy_import("json")
        first = p["json"]
        second = p["json"]
        assert first is second

    def test_nonexistent_module_raises(self):
        p = _empty_pantry()
        p.lazy_import("no_such_module_xyz_999")
        with pytest.raises(RuntimeError, match="no module named"):
            p["no_such_module_xyz_999"]

    def test_bad_attribute_raises(self):
        p = _empty_pantry()
        p.lazy_import("os.nonexistent_attr_xyz_999")
        with pytest.raises(RuntimeError, match="has no attribute"):
            p["os.nonexistent_attr_xyz_999"]

    def test_bad_parent_raises(self):
        p = _empty_pantry()
        p.lazy_import("no_such_pkg_xyz.Foo")
        with pytest.raises(RuntimeError, match="no module named"):
            p["no_such_pkg_xyz.Foo"]


class TestLazyVsProbe:
    """Lazy imports and pyproject.toml probes are separate systems."""

    def test_lazy_takes_priority(self):
        """If same key exists in both, lazy wins."""
        import json

        data = {"json": {"available": True, "module": None, "module_name": "json"}}
        p = Pantry(data)
        p.lazy_import("json")
        assert p["json"] is json  # lazy resolves the real module

    def test_probe_still_works(self):
        import json as json_mod

        data = {"json": {"available": True, "module": json_mod, "module_name": "json"}}
        p = Pantry(data)
        # No lazy_import — probe system should work as before
        assert p["json"] is json_mod

    def test_get_ignores_lazy(self):
        p = _empty_pantry()
        p.lazy_import("json")
        assert p.get("json") is None

    def test_has_ignores_lazy(self):
        p = _empty_pantry()
        p.lazy_import("json")
        assert p.has("json") is False

    def test_report_ignores_lazy(self):
        p = _empty_pantry()
        p.lazy_import("json")
        report = p.report()
        assert "json" not in report

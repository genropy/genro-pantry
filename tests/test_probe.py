# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""Tests for pantry._probe."""

from pathlib import PurePosixPath
from unittest.mock import MagicMock, patch

import pytest

from pantry._probe import probe, resolve_module_name, strip_specifier


class TestStripSpecifier:
    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("pillow>=9.0", "pillow"),
            ("numpy", "numpy"),
            ("pandas>=2.0,<3.0", "pandas"),
            ("scikit-learn!=1.0;python_version>='3.8'", "scikit-learn"),
            ("requests[security]>=2.20", "requests"),
            ("my-package==1.0", "my-package"),
        ],
    )
    def test_various_specs(self, raw, expected):
        assert strip_specifier(raw) == expected


class TestResolveModuleName:
    def test_real_package_packaging(self):
        # 'packaging' is installed — its module name should resolve to 'packaging'
        name = resolve_module_name("packaging")
        assert name == "packaging"

    def test_fallback_hyphen_replace(self):
        # Non-existent package falls back to hyphen→underscore
        name = resolve_module_name("non-existent-package-xyz-999")
        assert name == "non_existent_package_xyz_999"

    @patch("pantry._probe.importlib.metadata.distribution")
    def test_top_level_txt(self, mock_dist_fn):
        dist = MagicMock()
        dist.read_text.return_value = "PIL\n"
        mock_dist_fn.return_value = dist
        assert resolve_module_name("pillow") == "PIL"

    @patch("pantry._probe.importlib.metadata.distribution")
    def test_fallback_init_py(self, mock_dist_fn):
        dist = MagicMock()
        dist.read_text.return_value = None  # no top_level.txt
        dist.files = [
            PurePosixPath("mymod/__init__.py"),
            PurePosixPath("mymod/core.py"),
        ]
        mock_dist_fn.return_value = dist
        assert resolve_module_name("mymod") == "mymod"

    @patch("pantry._probe.importlib.metadata.distribution")
    def test_fallback_single_py(self, mock_dist_fn):
        dist = MagicMock()
        dist.read_text.return_value = None
        dist.files = [PurePosixPath("helper.py")]
        mock_dist_fn.return_value = dist
        assert resolve_module_name("helper") == "helper"


class TestProbe:
    def test_available_package(self):
        result = probe("packaging")
        assert result["available"] is True
        assert result["module"] is None  # lazy: module not imported yet
        assert result["pkg_name"] == "packaging"
        assert result["version"] is not None

    def test_load_module(self):
        from pantry._probe import load_module

        result = probe("packaging")
        assert result["module"] is None
        mod = load_module(result)
        assert mod is not None
        assert result["module"] is mod  # cached in entry

    def test_unavailable_package(self):
        result = probe("nonexistent-package-xyz-999")
        assert result["available"] is False
        assert result["module"] is None
        assert result["pkg_name"] == "nonexistent-package-xyz-999"

    def test_never_raises(self):
        # Even with a truly broken name, probe must not raise
        result = probe("")
        assert isinstance(result, dict)
        assert result["available"] is False

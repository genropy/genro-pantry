# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""Pantry — lightweight syntactic sugar for optional Python dependencies.

Usage::

    import pantry

    if pantry.has("numpy"):
        import numpy as np

    PIL = pantry["pillow"]          # raise if missing
    np = pantry.get("numpy")        # None if missing

    @pantry("pillow", "numpy")
    def process(path):
        ...
"""

import sys

from ._registry import Pantry

_instance = Pantry()
_instance.Pantry = Pantry  # type: ignore[attr-defined]
sys.modules[__name__] = _instance  # type: ignore[assignment]

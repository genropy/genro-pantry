# Copyright (c) 2025 Softwell S.r.l. — MIT License
"""Pantry — runtime capability registry for optional Python dependencies.

Usage::

    import pantry

    PIL = pantry["pillow"]          # raise if missing
    np = pantry.get("numpy")        # None if missing

    if pantry.has("redis"):
        ...

    @pantry("pillow", "numpy")
    def process(path):
        ...

    print(pantry.report())
"""

import sys

from ._registry import Pantry

try:
    _instance = Pantry.discover()
except FileNotFoundError:
    _instance = Pantry({}, {})

# Replace the module with the Pantry instance so that
# `import pantry` gives direct access to has/get/report/[]/()
_instance.Pantry = Pantry  # type: ignore[attr-defined]
sys.modules[__name__] = _instance  # type: ignore[assignment]

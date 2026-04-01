# Changelog

## 0.5.0 (2026-04-01)

**Breaking change**: complete architecture rewrite.

- **Removed pyproject.toml dependency** — Pantry now uses `importlib.metadata` directly.
  Works everywhere: development, installed packages, Docker, notebooks.
- **Removed `packaging` dependency** — zero external dependencies, pure stdlib.
- **Removed dependency groups** — `has_group()` removed. Use `has()` directly.
- **Removed `Pantry.discover()` and `Pantry.from_pyproject()`** — no longer needed.
- **On-demand probing** — nothing happens at `import pantry` time. Packages are
  probed on first `has()`, `get()`, or `[]` call.
- **Added `pantry.version(pkg)`** — returns installed version string.
- **`report()` accepts package names** — `pantry.report("numpy", "pandas")`.
- **Recommended pattern**: `if pantry.has("pkg"): import pkg` — works with pipreqs and IDEs.
- Source reduced from ~400 to ~300 lines (one file + bootstrap).

## 0.4.0 (2026-03-28)

- **Lazy probing**: external dependencies are no longer imported at `import pantry` time.
  Only metadata (installed? version?) is checked at startup. The actual `import_module()`
  happens on first `get()` or `[]` access. This makes `import pantry` fast even with
  many heavy optional dependencies (torch, pandas, etc.)
- **`pantry.simulate_missing(*pkgs)`**: context manager for testing fallback behavior.
  Temporarily hides packages so `has()`, `get()`, `[]`, decorator, and `report()` see
  them as unavailable. State is restored on exit, even on exceptions.

## 0.3.0 (2026-03-28)

- License changed from Apache 2.0 to MIT
- Promoted to Beta status
- Enriched README and documentation (design philosophy, troubleshooting, examples)

## 0.2.0 (2026-03-28)

- `pantry.lazy_import("dotted.path")` — register own modules for deferred import
- Breaks circular imports: register at top level, resolve on first `pantry["path"]` access
- Two-step resolution: submodules via `import_module`, attributes via `getattr`
- Results cached after first resolution
- Separate from external dependency system (`has`, `get`, `report` unaffected)
- Bridge toward PEP 690 (Lazy Imports)

## 0.1.0 (2026-03-28)

First public release.

- Auto-discovery of `pyproject.toml` optional-dependencies
- Module-as-instance pattern: `import pantry` returns a `Pantry` instance
- `pantry["pkg"]` — strict import, raises if missing
- `pantry.get("pkg")` — safe import with optional default
- `pantry.has(*pkgs)` — variadic availability check
- `pantry.has_group("group")` — group-level check
- `pantry("pkg1", "pkg2")` — decorator to guard functions
- `pantry.report()` — formatted summary table
- Smart module name resolution (pip name → importable name)
- PEP 561 typed (`py.typed` marker)
- MIT license

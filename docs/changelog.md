# Changelog

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
- Apache 2.0 license

# API Reference

## Module-Level Instance

```python
import pantry
```

Importing `pantry` returns a `Pantry` instance. All methods below are
available directly on this object.

---

## `pantry.has(*pkgs)`

```python
pantry.has("numpy")
pantry.has("numpy", "pandas")
```

Return `True` if all listed packages are installed. Uses distribution
metadata only — does **not** import the module.

**Parameters:**
: `*pkgs` (str) — one or more pip package names

**Returns:**
: `bool`

---

## `pantry[key]`

```python
PIL = pantry["pillow"]
User = pantry["myapp.models.User"]   # if lazy_import'd
```

Return a module (or lazy-resolved object). Checks lazy imports first,
then installed packages.

**Parameters:**
: `key` (str) — pip package name or lazy-registered dotted path

**Returns:**
: `types.ModuleType` (or any object for lazy attribute access)

**Raises:**
: `RuntimeError` — if not found in either system

---

## `pantry.get(pkg, default=None)`

```python
np = pantry.get("numpy")
redis = pantry.get("redis", "fallback")
```

Return the imported module, or *default* if unavailable. The module
is imported lazily on first access and cached.

**Parameters:**
: `pkg` (str) — pip package name
: `default` (object, optional) — value to return when unavailable

**Returns:**
: `types.ModuleType | None`

---

## `pantry.version(pkg)`

```python
pantry.version("numpy")   # "1.26.4" or None
```

Return the installed version of *pkg*, or `None`.

**Parameters:**
: `pkg` (str) — pip package name

**Returns:**
: `str | None`

---

## `pantry(*pkgs)` — Decorator

```python
@pantry("pillow", "numpy")
def process(path):
    ...
```

Decorator that guards a function. Raises `RuntimeError` at call-time
if any listed package is missing.

**Parameters:**
: `*pkgs` (str) — one or more pip package names

**Returns:**
: decorated function (metadata preserved via `functools.wraps`)

---

## `pantry.report(*pkgs)`

```python
print(pantry.report("numpy", "pandas", "pillow"))
print(pantry.report())  # all previously queried packages
```

Return a formatted availability table. With arguments, probes those
packages. Without arguments, reports all packages queried in this session.

**Parameters:**
: `*pkgs` (str, optional) — packages to report on

**Returns:**
: `str`

---

## `pantry.lazy_import(*paths)` — Own Modules

```python
pantry.lazy_import("myapp.models.User")
```

Register dotted paths for deferred import. No import at registration time.
Resolve on first `pantry["path"]` access. Cached after first resolution.

For your own modules — to break circular imports. Separate from the
external dependency system.

**Parameters:**
: `*paths` (str) — dotted import paths

**Returns:**
: `None`

---

## `pantry.simulate_missing(*pkgs)` — Testing

```python
with pantry.simulate_missing("numpy"):
    assert pantry.has("numpy") is False
```

Context manager that temporarily hides packages. All methods (`has`, `get`,
`[]`, decorator, `report`) see them as unavailable. Restored on exit.

**Parameters:**
: `*pkgs` (str) — packages to hide

**Yields:**
: `None`

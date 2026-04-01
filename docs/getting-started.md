# Getting Started

## Installation

```bash
pip install mypantry
```

Zero dependencies — only Python standard library.

## First Use

```python
import pantry

# Check if numpy is installed
print(pantry.has("numpy"))    # True or False

# Check version
print(pantry.version("numpy"))  # "1.26.4" or None

# Import safely
np = pantry.get("numpy")     # module or None

# Import strictly
np = pantry["numpy"]          # module or RuntimeError
```

## Recommended Pattern

The best way to use mypantry is to guard standard imports at the top of
your file:

```python
import pantry

if pantry.has("numpy"):
    import numpy as np

if pantry.has("pillow"):
    from PIL import Image

@pantry("numpy", "pillow")
def process(path):
    img = Image.open(path)
    return np.array(img)
```

This pattern gives you:

- **pipreqs** sees the real imports → dependency detection works
- **IDE autocompletion** works → standard Python imports
- **pantry** provides clean error messages → `RuntimeError` with `pip install X`

## How It Works

When you `import pantry`, the module replaces itself with a `Pantry` instance.

- `has()` — checks `importlib.metadata` (is the distribution installed?)
- `get()` / `[]` — imports the module lazily on first access, caches the result
- Smart module name resolution: `pillow` → `PIL`, `scikit-learn` → `sklearn`

No configuration files, no startup scanning, no pyproject.toml dependency.
Works in any context: dev, installed, Docker, notebooks.

## Next Steps

- {doc}`usage` — all access patterns in detail
- {doc}`api` — full API reference

# kuronuri Architecture Reference

## 1. Overall Design

```
User (external)
    │
    ├── Python API (__init__.py acts as facade)
    │       └── mask() / NERModel / strategy functions
    │
    └── CLI (_cli.py acts as adapter layer)
            └── calls the same mask()

[Data Flow]
Raw text
  → _get_pipeline(model)  ← singleton held by @cache
  → obtain NER entity list
  → filter by mask_tags
  → sort by start descending (for offset management)
  → strategy(entity, tag_labels) replaces each span
  → masked text
```

---

## 2. Strategy Pattern in Detail

`MaskStrategy = Callable[[dict, dict[str, str]], str]` is the core of the pattern.

```python
# Comparison of 3 built-in strategies
mask_with_block  → "█" repeated for entity["end"] - entity["start"] characters
mask_with_label  → builds "<Person>" from tag_labels.get(tag, tag)
mask_with_fixed  → factory function that holds char and length via closure
```

Why `mask_with_fixed` is a factory function:
Parameters (char, length) must be passed outside the strategy function signature,
so they are pre-bound via closure.

---

## 3. Pipeline Caching with @cache

```python
@cache
def _get_pipeline(model: NERModel) -> Any:
    return hf_pipeline("token-classification", model=model.model_name, ...)
```

`NERModel` uses `@dataclass(unsafe_hash=True)` for this reason:
- Only `model_name` and `aggregation_strategy` serve as hash keys
- `tag_labels` (dict) is excluded with `hash=False`
- Changing only the labels for the same model name reuses the same pipeline

---

## 4. Reverse Replacement Algorithm

```python
entities_to_mask = sorted(..., key=lambda e: e["start"], reverse=True)

for entity in entities_to_mask:
    result = result[:entity["start"]] + strategy(...) + result[entity["end"]:]
```

Replacing from the front causes index drift because the replacement string length differs.
Processing from the back avoids affecting the indices of already-processed positions.

---

## 5. CLI Encoding Handling

```python
_BOM_ENCODINGS: list[tuple[bytes, str]] = [
    (codecs.BOM_UTF32_LE, "utf-32-le"),  # 4 bytes (longer)
    (codecs.BOM_UTF32_BE, "utf-32-be"),
    (codecs.BOM_UTF16_LE, "utf-16-le"),  # 2 bytes (shorter)
    (codecs.BOM_UTF16_BE, "utf-16-be"),
    (codecs.BOM_UTF8, "utf-8-sig"),
]
```

Why longer BOMs are checked first:
The UTF-32 LE BOM (FF FE 00 00) starts with the UTF-16 LE BOM (FF FE),
so checking the shorter one first would cause a false match.

---

## 6. Facade Pattern (__init__.py)

```python
from kuronuri._masker import (mask, NERModel, ...)
__all__ = ["mask", "NERModel", ...]
```

The leading `_` in `_masker.py` is a convention indicating internal implementation.
If the file is split or renamed in the future, only `__init__.py` needs to be updated.

---

## 7. Design Principles Summary

| Principle | Implementation |
|---|---|
| Facade pattern | `__init__.py` |
| Strategy pattern | `MaskStrategy` type alias + 3 strategy functions |
| Cache (singleton-like) | `@cache` + `NERModel` hash design |
| Adapter pattern | `_cli.py` |
| Separation of concerns | CLI (I/O, encoding) and core (NER, replacement) fully separated |
| Single responsibility | Each file has exactly one responsibility |

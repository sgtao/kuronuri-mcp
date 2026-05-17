---
name: kuronuri
description: |
  Skill for integrating and implementing the "kuronuri" Python library, which masks PII in text using NER models.
  Activate when the user says: "use kuronuri", "mask PII", "redact personal information", "remove PII before LLM",
  "implement anonymization", "detect entities with NER", "mask this text", or similar phrases.
  If the MCP tools (mask_text / list_ner_tags) are connected, perform masking in real time within the conversation.
  If not connected, generate code examples, usage guides, custom strategy implementations, or CLI commands.
---

# kuronuri Integration Skill

## Overview

`kuronuri` (黒塗り) is a Python library that masks PII (Personally Identifiable Information) in text
using local NER model inference.

This skill operates in two modes:

| Mode | Condition | Capabilities |
|---|---|---|
| **Real-time execution** | MCP server connected | Mask text and list NER tags live in conversation |
| **Code generation** | MCP server not connected | Generate Python/CLI code, explain design |

---

## Step 0: Mode detection (always run at skill start)

Check whether the following MCP tools are available:

| Tool name | Function |
|---|---|
| `mask_text` | Mask PII in text and return the result |
| `list_ner_tags` | Return NER tag list for the given language |

- **Connected → go to Step 1A (real-time execution mode)**
- **Not connected → go to Step 1B (code generation mode)**

---

## Step 1A: Real-time execution mode

### Parameter confirmation

Use `ask_user_input_v0` to confirm the following before executing:

**Question 1: What is the language of the target text?**
- English (en)
- Japanese (ja)

**Question 2: Which masking strategy?**
- `███` block fill (default)
- `<Person>` label display
- `***` fixed string

**Question 3: Which tags to mask?**
- Model default (all PII)
- Person names only (PER / private_person)
- Person names + email
- Other (free specification)

If the tag list is needed, call `list_ner_tags` first and display the results.

### Execution

After confirming, call `mask_text` and output the masked result directly.

```
# Internal call example
mask_text(
    text="山田太郎（yamada@example.com）の件について",
    lang="ja",
    strategy="block",
)
# → "███（█████████████████）の件について"
```

### Post-execution confirmation block

```
---
💬 How does the result look?

- ✅ OK
- 🔧 Try a different strategy or tags
- 📋 Write this as Python code
- 🔍 Explain how it works
```

---

## Step 1B: Code generation mode

Use `ask_user_input_v0` to confirm the user's goal:

**Question: What is your goal?**

- Use from Python code (API usage)
- Use from the CLI for quick masking
- Implement a custom model or strategy
- Integrate into an LLM pre-processing pipeline
- Understand how the library works

Branch based on the selected goal.

---

## Step 2: Code generation branches

### A. Python API branch

#### A-1. Confirm language and model

```
What language is the target text?
- English (EN_MODEL: openai/privacy-filter)
- Japanese (JA_MODEL: tsmatz/xlm-roberta-ner-japanese)
- Other (Hugging Face custom model)
```

#### A-2. Confirm masking strategy

```
Which masking format?
- ███ (fill with blocks proportional to length) ← default
- <Person> (label display)
- *** (fixed string)
- Custom (lambda or custom function)
```

#### A-3. Code generation patterns

```python
# English, default (block fill)
from kuronuri import mask
result = mask("Hello, I'm Taro Yamada. My email is yama9999999@example.com.")

# Japanese, label strategy, person names only
from kuronuri import mask, mask_with_label, JA_MODEL
result = mask(
    "山田太郎です。メールは yama9999999@example.com です。",
    model=JA_MODEL,
    mask_tags={"PER"},
    strategy=mask_with_label,
)

# Custom lambda strategy
from kuronuri import mask
result = mask(
    "Hello, I'm Taro Yamada.",
    strategy=lambda e, _labels: f"[{e['entity_group']}]",
)
```

---

### B. CLI branch

**Command template:**

```bash
kuronuri \
  [--lang ja | --model MODEL_ID] \
  [--strategy block | label | fixed] \
  [--fixed-char CHAR --fixed-length N] \
  [-t TAG [-t TAG ...]] \
  [-o output.txt] \
  "INPUT_TEXT_OR_FILE"
```

**Generated examples:**

```bash
# Japanese file → file output
kuronuri --lang ja -o output.txt input.txt

# Label strategy to stdout
kuronuri --strategy label report.txt

# Mask person names and organizations only (Japanese)
kuronuri --lang ja -t PER -t ORG input.txt

# Custom model
kuronuri --model my-org/my-ner-model input.txt
```

---

### C. Custom model / strategy branch

**Custom model:**

```python
from kuronuri import NERModel, mask

my_model = NERModel(
    model_name="my-org/my-ner-model",
    default_mask_tags=frozenset({"PERSON", "ORG"}),
    tag_labels={"PERSON": "Person", "ORG": "Organization"},
)
result = mask("テキスト", model=my_model)
```

**Custom strategy (function):**

```python
from kuronuri import mask

def my_strategy(entity: dict, tag_labels: dict) -> str:
    label = tag_labels.get(entity["entity_group"], entity["entity_group"])
    length = entity["end"] - entity["start"]
    return f"[{label}:{length}chars]"

result = mask("テキスト", strategy=my_strategy)
```

**Custom strategy (factory):**

```python
from kuronuri import mask, MaskStrategy

def mask_with_emoji(emoji: str = "🙈") -> MaskStrategy:
    def _strategy(entity: dict, tag_labels: dict) -> str:
        return emoji * max(1, (entity["end"] - entity["start"]) // 2)
    return _strategy

result = mask("山田太郎です", model=JA_MODEL, strategy=mask_with_emoji("🙈"))
```

---

### D. LLM pre-processing pipeline branch

**Combined with OpenAI API:**

```python
from kuronuri import mask
import openai

def safe_chat(user_input: str) -> str:
    """Send to LLM only after removing PII."""
    sanitized = mask(user_input)
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": sanitized}],
    )
    return response.choices[0].message.content
```

**FastAPI (async) endpoint:**

```python
from fastapi import FastAPI
from pydantic import BaseModel
from kuronuri import mask, JA_MODEL
import asyncio

app = FastAPI()

class TextRequest(BaseModel):
    text: str
    lang: str = "en"

@app.post("/mask")
async def mask_endpoint(req: TextRequest) -> dict:
    model = JA_MODEL if req.lang == "ja" else None
    kwargs = {"model": model} if model else {}
    loop = asyncio.get_event_loop()
    masked = await loop.run_in_executor(None, lambda: mask(req.text, **kwargs))
    return {"masked": masked}
```

> ⚠️ `mask()` is synchronous. In async endpoints, wrap it with `run_in_executor` to avoid blocking the event loop.

---

### E. Library internals branch

Use `ask_user_input_v0` to confirm which aspect to explain (multi_select):

- How masking strategies work (Strategy Pattern)
- NER pipeline caching (`@cache`)
- Reverse replacement algorithm (offset management)
- CLI encoding handling
- `NERModel` dataclass design

Explain the design philosophy with code references from `references/architecture.md`.

---

## Step 3: Confirmation block (required after every code generation)

```
---
💬 Does this solve your problem?

- ✅ OK, I'll use this as-is
- 🔧 Try a different strategy or model
- 📦 Show me how to install dependencies
- 🔍 Explain how this code works
```

### 📦 "Show installation" branch

```bash
# CPU environment (recommended: install CPU-only PyTorch first if GPU is not needed)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install kuronuri

# With uv (add CPU index to pyproject.toml first)
uv add torch
uv add kuronuri
```

### 🔍 "Explain internals" branch

Output a design explanation based on the relevant section in `references/architecture.md`.

---

## Tag and model reference (quick lookup)

### EN_MODEL (`openai/privacy-filter`)

| Tag | Meaning | `mask_with_label` output |
|---|---|---|
| `private_person` | Person name | `<Person>` |
| `private_address` | Address | `<Address>` |
| `private_email` | Email | `<Email>` |
| `private_phone` | Phone number | `<Phone>` |
| `private_url` | URL | `<URL>` |
| `private_date` | Date | `<Date>` |
| `account_number` | Account / card number | `<AccountNumber>` |
| `secret` | API key / password | `<Secret>` |

### JA_MODEL (`tsmatz/xlm-roberta-ner-japanese`)

| Tag | Meaning | Default mask |
|---|---|---|
| `PER` | Person name | ✅ |
| `ORG` | Organization | ✅ |
| `LOC` | Location | ✅ |
| `ORG-P` | Political organization | — |
| `ORG-O` | Other organization | — |
| `INS` | Facility | — |
| `PRD` | Product | — |
| `EVT` | Event | — |

---

## Operational rules

- Always check MCP tool connectivity at skill start and switch mode accordingly
- Use `ask_user_input_v0` to confirm the use case before generating code or executing
- Always output minimal but complete runnable examples (include `import` statements)
- Never omit the confirmation block
- Always add a note about NER limitations (missed detections, false positives)
- Proactively suggest async or batch processing when applicable

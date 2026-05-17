# kuronuri-mcp

An MCP server and skill that runs [kuronuri](https://github.com/sincekmori/kuronuri) PII masking in real time inside Claude conversations.

---

## Directory Structure

```
kuronuri-mcp/
├── CHANGELOG.md                <- Changelog
├── SKILL.md                    <- Claude skill definition (required)
├── server.py                   <- MCP server (tool definitions)
├── pyproject.toml              <- Dependency management
├── mise.toml                   <- Task runner configuration
├── tests/                      <- Unit tests
├── references/
│   └── architecture.md        <- Detailed code design notes
├── evals/
│   └── test-cases.md          <- Functional test cases
└── README.md                   <- This file
```

---

## Setup

### 1. Install Dependencies

**Using pip:**

```bash
cd kuronuri-mcp/

# Install CPU-only PyTorch first (no GPU required, ~200 MB)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install "mcp[cli]" kuronuri
```

**Using uv (recommended):**

```bash
uv sync
```

### 2. Verify Installation

```bash
# Try with the MCP dev tool
mcp dev server.py

# Via uv
uv run mcp dev server.py
```

### 3. Register with Claude Code

```bash
# Project-local registration
claude mcp add kuronuri -- python /path/to/kuronuri-mcp/server.py

# Confirm registration
claude mcp list
```

### 4. Register with Claude Desktop

Add the following to `~/.claude/claude_mcp_config.json`:

```json
{
  "mcpServers": {
    "kuronuri": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/absolute/path/to/kuronuri-mcp",
        "python",
        "server.py"
      ]
    }
  }
}
```

---

## Tools

### `mask_text`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `text` | str | required | Text to mask |
| `lang` | str | `"en"` | `"en"` or `"ja"` |
| `strategy` | str | `"block"` | `"block"` / `"label"` / `"fixed"` |
| `mask_tags` | list[str] | null | Tags to mask (null uses model defaults) |
| `fixed_char` | str | `"█"` | Replacement character for fixed strategy |
| `fixed_length` | int | `3` | Replacement length for fixed strategy |

### `list_ner_tags`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `lang` | str | `"en"` | `"en"` or `"ja"` |

---

## Skill Modes

| Mode | Condition | Behavior |
|---|---|---|
| Real-time execution | MCP server connected | Masks PII inline during conversation |
| Code generation | MCP server not connected | Generates Python/CLI code and design notes |

---

## Notes

- The first run downloads NER models from Hugging Face (EN: ~500 MB, JA: ~1 GB).
- Subsequent runs use the local cache and work offline.
- NER models are not perfect; false negatives and false positives can occur. Always combine with human review.
- Text is processed locally only and never sent to external services.

---

## For Developers

### Development Setup

```bash
# Install all dependencies including dev tools
uv sync
```

### Task Reference

| Command | Description |
|---|---|
| `mise run fix` | Format and lint with ruff, type-check with ty |
| `mise run test` | Unit tests without model loading (fast) |
| `mise run test-cov` | Unit tests with coverage report (model required) |
| `mise run test-all` | Full test suite across Python 3.10-3.12 (model required) |

### Test Structure

Tests under `tests/` are split into two categories:

- **Standard tests** (default): kuronuri models are mocked. Fast and suitable for CI.
- **Model tests** (`--run-model` flag): Runs against real NER models. Requires model download on first run.

```bash
# Standard tests
uv run pytest

# Model tests (uses real models)
uv run pytest --run-model
```

### Pre-push Checklist

```bash
mise run fix
mise run test-all
```

---

## License

Apache-2.0

This project uses [kuronuri](https://github.com/sincekmori/kuronuri) by Shinsuke Mori (Apache-2.0).

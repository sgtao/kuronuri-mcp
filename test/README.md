# kuronuri-mcp-test — Smoke test sample project

Sample scripts for verifying kuronuri / kuronuri-mcp behavior.

---

## Structure

```
kuronuri-test/
├── data/
│   ├── sample_ja.txt          ← Japanese sample text (contains fictional PII)
│   └── sample_en.txt          ← English sample text (contains fictional PII)
├── masked/                    ← Output directory for 02_file_batch.py (auto-created)
└── scripts/
    ├── 01_basic.py            ← Basic operation check (strategy × language combinations)
    ├── 02_file_batch.py       ← Batch file masking
    ├── 03_mcp_client.py       ← Direct MCP client call
    └── 04_claude_code_test.md ← Natural language test procedure for Claude Code
```

---

## Setup

```bash
# Install kuronuri (CPU environment)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install kuronuri "mcp[cli]"
```

---

## How to run

### Step 1: Basic operation check

```bash
python scripts/01_basic.py
```

Runs through all combinations of strategy (block / label / fixed) and language (en / ja).
Note: The first run downloads the model, which may take a few minutes.

---

### Step 2: Batch file processing

```bash
# Default (block strategy)
python scripts/02_file_batch.py

# Label strategy
python scripts/02_file_batch.py --strategy label

# Explicit language
python scripts/02_file_batch.py --lang ja --strategy label
```

Processes all `data/*.txt` files and writes results to `masked/`.

---

### Step 3: MCP client direct call

```bash
# Verify server.py path before running
python scripts/03_mcp_client.py
```

Calls `mask_text` / `list_ner_tags` over the MCP protocol.
Adjust the `SERVER_PATH` variable to point to your `server.py`.

---

### Step 4: Natural language test in Claude Code

Follow the instructions in `scripts/04_claude_code_test.md` to test with prompts in Claude Code.

```bash
# Register MCP server (first time only)
claude mcp add kuronuri -- uv run --directory /path/to/kuronuri-mcp python server.py
```

---

## Notes

- All sample data in `data/` contains entirely fictional information
- First-run model download: EN model ~500 MB, JA model ~1 GB
- NER models are not perfect — missed detections and false positives can occur

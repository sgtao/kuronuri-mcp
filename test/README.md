# kuronuri-mcp-test — 動作確認サンプルプロジェクト

kuronuri / kuronuri-mcp の動作を確認するためのサンプル集。

---

## 構成

```
kuronuri-test/
├── data/
│   ├── sample_ja.txt          ← 日本語サンプル（個人情報入り）
│   └── sample_en.txt          ← 英語サンプル（個人情報入り）
├── masked/                    ← 02_file_batch.py の出力先（自動生成）
└── scripts/
    ├── 01_basic.py            ← 基本動作確認（戦略・言語の組み合わせ）
    ├── 02_file_batch.py       ← ファイル一括マスキング
    ├── 03_mcp_client.py       ← MCP クライアント直接呼び出し
    └── 04_claude_code_test.md ← Claude Code での自然言語テスト手順
```

---

## セットアップ

```bash
# kuronuri をインストール（CPU環境）
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install kuronuri "mcp[cli]"
```

---

## 実行手順

### Step 1：基本動作確認

```bash
python scripts/01_basic.py
```

戦略（block / label / fixed）と言語（en / ja）の組み合わせを一通り確認できる。
※ 初回はモデルのダウンロードが走るため数分かかる。

---

### Step 2：ファイル一括処理

```bash
# デフォルト（ブロック戦略）
python scripts/02_file_batch.py

# ラベル戦略
python scripts/02_file_batch.py --strategy label

# 言語を明示
python scripts/02_file_batch.py --lang ja --strategy label
```

`data/*.txt` を処理して `masked/` に出力する。

---

### Step 3：MCPクライアント直接呼び出し

```bash
# server.py のパスを確認してから実行
python scripts/03_mcp_client.py
```

MCP プロトコル経由で `mask_text` / `list_ner_tags` を呼び出す。
kuronuri-mcp の `server.py` へのパスを `SERVER_PATH` 変数で調整すること。

---

### Step 4：Claude Code での自然言語テスト

`scripts/04_claude_code_test.md` の手順に従い、Claude Code 上でプロンプトを試す。

```bash
# MCP 登録（初回のみ）
claude mcp add kuronuri -- uv run --directory /path/to/kuronuri-mcp python server.py
```

---

## 注意事項

- `data/` 内のサンプルデータはすべて架空の情報です
- 初回実行時のモデルダウンロード：EN モデル ~500MB、JA モデル ~1GB
- NER モデルは完璧ではなく検出漏れ・誤検出がある

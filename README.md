# kuronuri-mcp

Claude会話内でkuronuriによるPIIマスキングをリアルタイム実行するMCPサーバー＋スキル。

---

## ディレクトリ構成

```
kuronuri-mcp/
├── SKILL.md                    ← Claudeスキル本体（必須）
├── server.py                   ← MCPサーバー（ツール定義）
├── pyproject.toml              ← 依存管理
├── references/
│   └── architecture.md        ← コード設計の詳細解説
├── evals/
│   └── test-cases.md          ← 動作確認テストケース（R系3件＋C系9件）
└── README.md                   ← このファイル
```

---

## セットアップ手順

### 1. 依存インストール

```bash
cd kuronuri-mcp/

# CPU版PyTorchを先に入れる（GPU不要、~200MB）
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install kuronuri "mcp[cli]"
```

uv の場合：

```bash
uv add torch  # pyproject.toml の pytorch-cpu index を参照
uv add kuronuri mcp
```

### 2. 動作確認

```bash
# MCPのdev toolで試す
mcp dev server.py
```

### 3. Claude Code への登録

```bash
# プロジェクトローカル
claude mcp add kuronuri -- python /path/to/kuronuri-mcp/server.py

# 登録確認
claude mcp list
```

### 4. Claude Desktop（claude_mcp_config.json）への登録

`~/.claude/claude_mcp_config.json` に追記：

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

## 提供ツール

### `mask_text`

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `text` | str | 必須 | マスク対象テキスト |
| `lang` | str | `"en"` | `"en"` または `"ja"` |
| `strategy` | str | `"block"` | `"block"` / `"label"` / `"fixed"` |
| `mask_tags` | list[str] | null | 指定タグのみマスク（nullでデフォルト） |
| `fixed_char` | str | `"█"` | fixed戦略の置換文字 |
| `fixed_length` | int | `3` | fixed戦略の文字数 |

### `list_ner_tags`

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `lang` | str | `"en"` | `"en"` または `"ja"` |

---

## スキルのモード

| モード | 条件 | 動作 |
|---|---|---|
| リアルタイム実行 | MCPサーバー接続済み | 会話内で即マスク実行 |
| コード生成 | MCPサーバー未接続 | Python/CLIコード・設計解説を生成 |

---

## 注意事項

- 初回実行時にHugging Faceからモデルをダウンロード（EN: ~500MB、JA: ~1GB）
- 以降はキャッシュからオフラインでも動作する
- NERモデルは完璧ではなく検出漏れ・誤検出がある。人間のレビューを組み合わせること
- テキストはローカルでのみ処理され、外部に送信されない

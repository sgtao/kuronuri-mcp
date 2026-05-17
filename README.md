# kuronuri-mcp

Claude会話内で[kuronuri](https://github.com/sincekmori/kuronuri) によるPIIマスキングをリアルタイム実行するMCPサーバー＋スキル。

---

## ディレクトリ構成

```
kuronuri-mcp/
├── CHANGELOG.md                ← 変更履歴
├── SKILL.md                    ← Claudeスキル本体（必須）
├── server.py                   ← MCPサーバー（ツール定義）
├── pyproject.toml              ← 依存管理
├── mise.toml                   ← タスクランナー設定
├── tests/                      ← ユニットテスト
├── references/
│   └── architecture.md        ← コード設計の詳細解説
├── evals/
│   └── test-cases.md          ← 動作確認テストケース
└── README.md                   ← このファイル
```

---

## セットアップ手順

### 1. 依存インストール

**pip の場合：**

```bash
cd kuronuri-mcp/

# CPU版PyTorchを先に入れる（GPU不要、~200MB）
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install "mcp[cli]" kuronuri
```

**uv の場合（推奨）：**

```bash
uv sync
```

### 2. 動作確認

```bash
# MCPのdev toolで試す
mcp dev server.py

# uv 経由の場合
uv run mcp dev server.py
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

---

## 開発者向け

### 開発環境のセットアップ

```bash
# 依存インストール（dev ツール含む）
uv sync
```

### タスク一覧

| コマンド | 内容 |
|---|---|
| `mise run fix` | ruff によるフォーマット・Lint修正 + ty による型チェック |
| `mise run test` | ユニットテスト（モデル不要、高速） |
| `mise run test-cov` | ユニットテスト + カバレッジレポート表示（モデルあり） |
| `mise run test-all` | Python 3.10〜3.12 全バージョンでテスト（モデルあり） |

### テスト構成

`tests/` 以下のテストは2種類に分かれています：

- **通常テスト**（デフォルト）：kuronuriモデルをモック化して実行。高速で CI 向け
- **モデルテスト**（`--run-model` フラグ）：実際のNERモデルをロードして実行。初回はモデルDLが発生

```bash
# 通常テスト
uv run pytest

# モデルテスト（実モデル使用）
uv run pytest --run-model
```

### push 前チェック

```bash
mise run fix
mise run test
```

---

## ライセンス

Apache-2.0

このプロジェクトは [kuronuri](https://github.com/sincekmori/kuronuri)（作者: Shinsuke Mori、Apache-2.0）を使用しています。

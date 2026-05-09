# kuronuri-mcp
kuronuri スキル — セットアップ & 使い方ガイド

## ディレクトリ構成

```
kuronuri-mcp/
├── SKILL.md                    ← スキル本体（必須）
├── references/
│   └── architecture.md        ← コード設計の詳細解説（スキルから参照）
├── evals/
│   └── test-cases.md          ← 動作確認用テストケース
└── README.md                  ← このファイル
```

---

## インストール方法

### Claude Code でのインストール

```bash
# ローカルスコープ（現在のプロジェクトのみ）
claude mcp add --scope local /path/to/kuronuri-mcp

# ユーザースコープ（全プロジェクトで使える）
claude mcp add --scope user /path/to/kuronuri-mcp
```

### claude.ai スキルとして登録

1. `kuronuri-mcp/` フォルダごと所定のスキルディレクトリに配置
2. `SKILL.md` の frontmatter `name` が `kuronuri` であることを確認

---

## トリガーフレーズ（発火条件）

以下のフレーズを含む入力で自動的にこのスキルが使われる：

- 「kuronuriを使いたい」
- 「PIIをマスキングしたい」
- 「個人情報を黒塗りしたい」
- 「LLMに渡す前に個人情報を消したい」
- 「匿名化処理を実装したい」
- 「NERでエンティティを検出したい」

---

## 動作確認

`evals/test-cases.md` のテストケースを順に試して、期待動作と照合する。

---

## カスタマイズポイント

### 対応モデルを追加したい場合

`SKILL.md` の「タグ・モデルリファレンス」セクションに新モデルのタグ表を追記する。

### 新しいユースケースブランチを追加したい場合

`SKILL.md` の「ステップ2：ブランチ別対応」に新セクション（例：`F. バッチ処理ブランチ`）を追加する。

### アーキテクチャ解説を深めたい場合

`references/architecture.md` に解説を追記し、`SKILL.md` の該当ブランチからの参照を追加する。

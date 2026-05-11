# 04_claude_code_test.md — Claude Code での自然言語テスト手順

kuronuri-mcp を Claude Code に登録した後、
以下のプロンプトを順に試して動作を確認する。

---

## 事前準備：Claude Code への MCP 登録

```bash
# kuronuri-mcp ディレクトリのパスを確認
ls /path/to/kuronuri-mcp/server.py

# Claude Code に登録（パスは環境に合わせて変更）
claude mcp add kuronuri -- uv run --directory /path/to/kuronuri-mcp python server.py

# 登録確認
claude mcp list
```

---

## テスト1：タグ一覧の確認

```
日本語の NER タグ一覧を見せて
```

**期待される動作：**
- `list_ner_tags(lang="ja")` が呼ばれる
- PER / ORG / LOC などのタグ表が表示される

---

## テスト2：インライン文字列のマスク（日本語）

```
「山田太郎（yamada.taro@example.co.jp、090-1234-5678）の件について」を日本語モデルでマスクして
```

**期待される動作：**
- `mask_text(text="...", lang="ja", strategy="block")` が呼ばれる
- 人名・メール・電話番号が `███` に置き換わる

---

## テスト3：戦略を指定してマスク

```
「田中誠一、03-9876-5432」をラベル表示でマスクして
```

**期待される動作：**
- `mask_text(..., strategy="label")` が呼ばれる
- `<Person>、<Phone>` のように表示される

---

## テスト4：人名だけマスク

```
「鈴木花子（suzuki@example.jp）の住所は東京都渋谷区です」で人名だけマスクして。メールや住所は残して
```

**期待される動作：**
- `mask_text(..., mask_tags=["PER"])` が呼ばれる
- 人名のみ `███`、メール・住所はそのまま残る

---

## テスト5：英語テキストのマスク

```
Mask this: "Hello, I'm John Doe. My email is john.doe@example.com and phone is +1-800-555-0199."
```

**期待される動作：**
- `mask_text(text="...", lang="en", strategy="block")` が呼ばれる
- 人名・メール・電話が `███` に置き換わる

---

## テスト6：ファイル内容を渡してマスク

```
（data/sample_ja.txt の内容をコピペして）
このテキストの個人情報を日本語モデルでマスクして
```

**期待される動作：**
- 長文全体が処理される
- 複数の人名・メール・電話番号が一括マスクされる

---

## 確認ポイント

| チェック項目 | 確認方法 |
|---|---|
| MCPツールが呼ばれているか | Claude の応答に「mask_text を呼び出しました」的な表示があるか |
| 正しいパラメータで呼ばれているか | lang / strategy / mask_tags が意図通りか |
| マスク結果が正しいか | 個人情報が置き換わり、それ以外が残っているか |
| 検出漏れがないか | 同じテキスト内に複数のPIIがある場合に全て処理されているか |

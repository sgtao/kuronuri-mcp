---
name: kuronuri
description: |
  テキスト中の個人情報（PII）をNERモデルでマスキングするPythonライブラリ「kuronuri」の活用・実装支援スキル。
  「kuronuriを使いたい」「PIIをマスキングしたい」「個人情報を黒塗りしたい」「LLMに渡す前に個人情報を消したい」
  「匿名化処理を実装したい」「NERでエンティティを検出したい」「このテキストをマスクして」「今すぐ黒塗りして」
  などのフレーズが含まれる場合は必ずこのスキルを使う。
  MCPツール（mask_text / list_ner_tags）が接続済みであれば会話内でリアルタイムにマスキングを実行する。
  未接続の場合はコード例の生成・ユースケース別ガイド・カスタム戦略の実装・CLIコマンド生成を行う。
---

# kuronuri 統合スキル

## 概要

`kuronuri`（黒塗り）はテキスト内のPII（個人識別情報）をNERモデルでローカル推論してマスキングするPythonライブラリ。

このスキルには2つのモードがある：

| モード | 条件 | できること |
|---|---|---|
| **リアルタイム実行** | MCPサーバー接続済み | 会話内でその場マスク・タグ一覧表示 |
| **コード生成** | MCPサーバー未接続 | Python/CLIコード生成・設計解説 |

---

## ステップ0：モード判定（スキル起動時に必ず行う）

以下のMCPツールが利用可能か確認する。

| ツール名 | 機能 |
|---|---|
| `mask_text` | テキストのPIIをマスキングして返す |
| `list_ner_tags` | 言語別のNERタグ一覧を返す |

- **接続済み → ステップ1A（リアルタイム実行モード）へ**
- **未接続 → ステップ1B（コード生成モード）へ**

---

## ステップ1A：リアルタイム実行モード

### パラメータ確認

`ask_user_input_v0` で以下を確認してから実行する。

**質問1：対象テキストの言語は？**
- 英語（en）
- 日本語（ja）

**質問2：マスキング戦略は？**
- `███` ブロック塗りつぶし（デフォルト）
- `<Person>` ラベル表示
- `***` 固定文字列

**質問3：マスク対象タグは？**
- モデルのデフォルト（全PII）
- 人名のみ（PER / private_person）
- 人名＋メール
- その他（フリー指定）

タグ一覧が必要なら `list_ner_tags` を先に呼び出して表示する。

### 実行

確認後、`mask_text` ツールを呼び出してマスク結果をそのまま出力する。

```
# 内部呼び出し例
mask_text(
    text="山田太郎（yamada@example.com）の件について",
    lang="ja",
    strategy="block",
)
# → "███（█████████████████）の件について"
```

### 実行後の確認ブロック

```
---
💬 結果はいかがですか？

- ✅ OK
- 🔧 別の戦略・タグで試したい
- 📋 このコードをPythonで書いて
- 🔍 しくみを詳しく知りたい
```

---

## ステップ1B：コード生成モード

`ask_user_input_v0` でユーザーの目的を確認する。

**質問：今回の目的は？**

- Pythonコードから使いたい（API利用）
- CLIコマンドで手軽に使いたい
- カスタムモデル・戦略を実装したい
- LLM前処理パイプラインに組み込みたい
- ライブラリのしくみを理解したい

目的に応じて以下のブランチに分岐する。

---

## ステップ2：コード生成ブランチ

### A. Python API利用ブランチ

#### A-1. 言語・モデルの確認

```
対象テキストの言語は？
- 英語（EN_MODEL: openai/privacy-filter）
- 日本語（JA_MODEL: tsmatz/xlm-roberta-ner-japanese）
- その他（Hugging Face カスタムモデル）
```

#### A-2. マスキング戦略の確認

```
どの形式でマスクしますか？
- ███（文字数に合わせて塗りつぶす）← デフォルト
- <Person>（ラベル表示）
- ***（固定文字列）
- カスタム（lambdaや自作関数）
```

#### A-3. コード生成パターン

```python
# 英語・デフォルト（ブロック塗りつぶし）
from kuronuri import mask
result = mask("Hello, I'm Taro Yamada. My email is yama9999999@example.com.")

# 日本語・ラベル戦略・人名のみ
from kuronuri import mask, mask_with_label, JA_MODEL
result = mask(
    "山田太郎です。メールは yama9999999@example.com です。",
    model=JA_MODEL,
    mask_tags={"PER"},
    strategy=mask_with_label,
)

# カスタムlambda戦略
from kuronuri import mask
result = mask(
    "Hello, I'm Taro Yamada.",
    strategy=lambda e, _labels: f"[{e['entity_group']}]",
)
```

---

### B. CLI利用ブランチ

**コマンドテンプレート：**

```bash
kuronuri \
  [--lang ja | --model MODEL_ID] \
  [--strategy block | label | fixed] \
  [--fixed-char CHAR --fixed-length N] \
  [-t TAG [-t TAG ...]] \
  [-o output.txt] \
  "INPUT_TEXT_OR_FILE"
```

**生成パターン例：**

```bash
# 日本語ファイル→ファイル出力
kuronuri --lang ja -o output.txt input.txt

# ラベル戦略でstdoutへ
kuronuri --strategy label report.txt

# 人名・組織名だけマスク（日本語）
kuronuri --lang ja -t PER -t ORG input.txt

# カスタムモデル
kuronuri --model my-org/my-ner-model input.txt
```

---

### C. カスタムモデル・戦略実装ブランチ

**カスタムモデル：**

```python
from kuronuri import NERModel, mask

my_model = NERModel(
    model_name="my-org/my-ner-model",
    default_mask_tags=frozenset({"PERSON", "ORG"}),
    tag_labels={"PERSON": "Person", "ORG": "Organization"},
)
result = mask("テキスト", model=my_model)
```

**カスタム戦略（関数）：**

```python
from kuronuri import mask

def my_strategy(entity: dict, tag_labels: dict) -> str:
    label = tag_labels.get(entity["entity_group"], entity["entity_group"])
    length = entity["end"] - entity["start"]
    return f"[{label}:{length}文字]"

result = mask("テキスト", strategy=my_strategy)
```

**カスタム戦略（ファクトリ）：**

```python
from kuronuri import mask, MaskStrategy

def mask_with_emoji(emoji: str = "🙈") -> MaskStrategy:
    def _strategy(entity: dict, tag_labels: dict) -> str:
        return emoji * max(1, (entity["end"] - entity["start"]) // 2)
    return _strategy

result = mask("山田太郎です", model=JA_MODEL, strategy=mask_with_emoji("🙈"))
```

---

### D. LLM前処理パイプライン組み込みブランチ

**OpenAI API との組み合わせ：**

```python
from kuronuri import mask
import openai

def safe_chat(user_input: str) -> str:
    """PIIを除去してからLLMに送る"""
    sanitized = mask(user_input)
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": sanitized}],
    )
    return response.choices[0].message.content
```

**FastAPI（非同期）エンドポイント：**

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

> ⚠️ `mask()` は同期関数。async endpoint では `run_in_executor` でラップしないとイベントループをブロックする。

---

### E. ライブラリ理解ブランチ

`ask_user_input_v0` で解説したい観点を確認する（multi_select）：

- マスキング戦略のしくみ（Strategy Pattern）
- NERパイプラインのキャッシュ（@cache）
- 後方からの置換アルゴリズム（offset管理）
- CLIのエンコーディング処理
- NERModel データクラスの設計

詳細は `references/architecture.md` を参照しながら、コードを引用して設計思想を解説する。

---

## ステップ3：確認ブロック（コード生成後は毎回必須）

```
---
💬 このコードで解決できそうですか？

- ✅ OK、このまま使う
- 🔧 別の戦略・モデルを試したい
- 📦 依存インストール方法も教えて
- 🔍 このコードのしくみを詳しく知りたい
```

### 📦「インストール方法も教えて」分岐

```bash
# CPU環境（推奨：GPU不要なら先にCPUビルドのPyTorchを入れる）
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install kuronuri

# uvの場合（pyproject.tomlにCPU indexを追記後）
uv add torch
uv add kuronuri
```

### 🔍「しくみを詳しく」分岐

`references/architecture.md` の該当セクションをもとに設計解説を出力する。

---

## タグ・モデルリファレンス（クイック参照）

### EN_MODEL（`openai/privacy-filter`）

| タグ | 意味 | `mask_with_label`出力 |
|---|---|---|
| `private_person` | 人名 | `<Person>` |
| `private_address` | 住所 | `<Address>` |
| `private_email` | メール | `<Email>` |
| `private_phone` | 電話番号 | `<Phone>` |
| `private_url` | URL | `<URL>` |
| `private_date` | 日付 | `<Date>` |
| `account_number` | 口座・カード番号 | `<AccountNumber>` |
| `secret` | APIキー・パスワード | `<Secret>` |

### JA_MODEL（`tsmatz/xlm-roberta-ner-japanese`）

| タグ | 意味 | デフォルトマスク |
|---|---|---|
| `PER` | 人名 | ✅ |
| `ORG` | 組織 | ✅ |
| `LOC` | 場所 | ✅ |
| `ORG-P` | 政治組織 | — |
| `ORG-O` | その他組織 | — |
| `INS` | 施設 | — |
| `PRD` | 製品 | — |
| `EVT` | イベント | — |

---

## 運用ルール

- スキル起動時に必ずMCPツールの接続状態を確認し、モードを切り替える
- `ask_user_input_v0` でユースケースを先に確認してからコード・実行を行う
- コードは必ず動くミニマルな完全例を出す（`import`から書く）
- 確認ブロックは省略しない
- NERの限界（検出漏れ・誤検出）には必ずメモを添える
- 非同期・バッチ処理が必要そうなら積極的に提案する

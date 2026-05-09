---
name: kuronuri
description: |
  テキスト中の個人情報（PII）をNERモデルでマスキングするPythonライブラリ「kuronuri」の活用・実装支援スキル。
  「kuronuriを使いたい」「PIIをマスキングしたい」「個人情報を黒塗りしたい」「LLMに渡す前に個人情報を消したい」
  「匿名化処理を実装したい」「NERでエンティティを検出したい」などのフレーズが含まれる場合は必ずこのスキルを使う。
  コード例の生成・ユースケース別ガイド・カスタム戦略の実装・CLIコマンド生成まで一気通貫で対応する。
---

# kuronuri 活用・実装支援スキル

## 概要

`kuronuri`（黒塗り）はテキスト内のPII（個人識別情報）をNERモデルでローカル推論してマスキングするPythonライブラリ。
このスキルは「何をしたいか」をヒアリングし、最適なコード・CLI・設計を即座に提案する。

---

## ステップ1：ユースケースの特定

`ask_user_input_v0` でユーザーの目的を確認する。

**質問：今回の目的は？**

- Pythonコードから使いたい（API利用）
- CLIコマンドで手軽に使いたい
- カスタムモデル・戦略を実装したい
- LLM前処理パイプラインに組み込みたい
- ライブラリのしくみを理解したい

目的に応じて以下のブランチに分岐する。

---

## ステップ2：ブランチ別対応

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

#### A-3. コード生成

確認した内容をもとに、以下のテンプレートを埋めてコードを生成する。

```python
from kuronuri import mask{MODEL_IMPORT}{STRATEGY_IMPORT}

text = "{USER_TEXT}"

result = mask(
    text,
    {MODEL_ARG}{MASKTAGS_ARG}    strategy={STRATEGY_ARG},
)
print(result)
```

**生成パターン例：**

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

#### B-1. 入力タイプの確認

```
処理対象は？
- インライン文字列（コマンドに直接入力）
- ファイル（.txt などのファイルパス）
```

#### B-2. CLIコマンド生成

確認内容をもとに最適なコマンドを生成する。

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

#### C-1. カスタムモデルの実装

```python
from kuronuri import NERModel, mask

my_model = NERModel(
    model_name="my-org/my-ner-model",          # HuggingFace model ID
    default_mask_tags=frozenset({"PERSON", "ORG"}),
    tag_labels={
        "PERSON": "Person",
        "ORG": "Organization",
    },
    # aggregation_strategy="simple",  # 必要なら変更
)

result = mask("テキスト", model=my_model)
```

#### C-2. カスタム戦略の実装

```python
from kuronuri import mask, MaskStrategy

# パターン1：lambda（シンプル）
strategy = lambda entity, labels: f"[REDACTED:{entity['entity_group']}]"

# パターン2：関数（ロジックが複雑な場合）
def my_strategy(entity: dict, tag_labels: dict) -> str:
    tag = entity["entity_group"]
    label = tag_labels.get(tag, tag)
    length = entity["end"] - entity["start"]
    return f"[{label}:{length}文字]"

result = mask("テキスト", strategy=my_strategy)
```

#### C-3. ファクトリ関数パターン（mask_with_fixedと同様）

```python
def mask_with_emoji(emoji: str = "🙈") -> MaskStrategy:
    """エンティティをemojiで置き換えるカスタム戦略ファクトリ"""
    def _strategy(entity: dict, tag_labels: dict) -> str:
        length = entity["end"] - entity["start"]
        return emoji * max(1, length // 2)
    return _strategy

result = mask("山田太郎です", model=JA_MODEL, strategy=mask_with_emoji("🙈"))
```

---

### D. LLM前処理パイプライン組み込みブランチ

#### D-1. 組み込みパターンの確認

```
どのLLM/フレームワークと組み合わせますか？
- OpenAI API（openai-python）
- Anthropic API（anthropic-python）
- LangChain / LlamaIndex
- FastAPI（Webアプリのエンドポイント）
- その他
```

#### D-2. 組み込みコードの生成

**OpenAI API との組み合わせ例：**

```python
from kuronuri import mask
import openai

def safe_chat(user_input: str) -> str:
    """PIIを除去してからLLMに送る"""
    sanitized = mask(user_input)  # PII除去
    
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": sanitized}],
    )
    return response.choices[0].message.content

# 使用例
reply = safe_chat("山田太郎 （yama9999999@example.com）の件について教えて")
```

**FastAPI エンドポイント例：**

```python
from fastapi import FastAPI
from pydantic import BaseModel
from kuronuri import mask, JA_MODEL

app = FastAPI()

class TextRequest(BaseModel):
    text: str
    lang: str = "en"

@app.post("/mask")
def mask_text(req: TextRequest) -> dict:
    model = JA_MODEL if req.lang == "ja" else None
    kwargs = {"model": model} if model else {}
    return {"masked": mask(req.text, **kwargs)}
```

**非同期（asyncio）対応例：**

```python
import asyncio
from kuronuri import mask

async def mask_async(text: str, **kwargs) -> str:
    """同期のmask()をイベントループをブロックせずに実行"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: mask(text, **kwargs))

# FastAPI の async endpoint でも安全に使える
```

---

### E. ライブラリ理解ブランチ

解説すべき観点を確認する：

```
どの部分を理解したいですか？（複数選択可）
- マスキング戦略のしくみ（Strategy Pattern）
- NERパイプラインのキャッシュ（@cache）
- 後方からの置換アルゴリズム（offset管理）
- CLIのエンコーディング処理
- NERModel データクラスの設計
```

選択された項目について、コードを引用しながら設計思想を説明する。
詳細は `references/architecture.md` を参照。

---

## ステップ3：確認ブロック（毎回必須）

コード・コマンドを提示した後、必ず以下を出力する：

```
---
💬 **このコードで解決できそうですか？**

- ✅ OK、このまま使う
- 🔧 別の戦略・モデルを試したい
- 📦 依存インストール方法も教えて
- 🔍 このコードのしくみを詳しく知りたい
```

ユーザーの選択に応じて以下に分岐する：

### 🔧「別の戦略・モデルを試したい」分岐
ステップ2に戻り、別の戦略・モデルのコードを提示する。

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

### EN_MODEL タグ一覧

| タグ | 意味 | mask_with_label出力 |
|---|---|---|
| `private_person` | 人名 | `<Person>` |
| `private_address` | 住所 | `<Address>` |
| `private_email` | メール | `<Email>` |
| `private_phone` | 電話番号 | `<Phone>` |
| `private_url` | URL | `<URL>` |
| `private_date` | 日付 | `<Date>` |
| `account_number` | 口座・カード番号 | `<AccountNumber>` |
| `secret` | APIキー・パスワード | `<Secret>` |

### JA_MODEL タグ一覧

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

- `ask_user_input_v0` でユースケースを先に確認してからコードを生成する
- コードは必ず動くミニマルな完全例を出す（`import`から書く）
- 確認ブロックは省略しない
- NERの限界（検出漏れ・誤検出）には必ずメモを添える
- 非同期・バッチ処理が必要そうなら積極的に提案する

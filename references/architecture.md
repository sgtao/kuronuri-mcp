# kuronuri アーキテクチャ解説リファレンス

## 1. 全体設計図

```
外部（ユーザー）
    │
    ├── Python API（__init__.py がファサード）
    │       └── mask() / NERModel / Strategy関数群
    │
    └── CLI（_cli.py がアダプター層）
            └── 同じ mask() を呼び出す

【データフロー】
生テキスト
  → _get_pipeline(model)  ← @cache でシングルトン保持
  → NERエンティティリスト取得
  → mask_tags でフィルタリング
  → start降順ソート（offset管理のため）
  → strategy(entity, tag_labels) で文字列置換
  → マスク済みテキスト
```

---

## 2. ストラテジーパターンの詳細

`MaskStrategy = Callable[[dict, dict[str, str]], str]` という型エイリアスがパターンの核。

```python
# 3種のビルトイン戦略の比較
mask_with_block  → entity["end"] - entity["start"] 文字分の「█」
mask_with_label  → tag_labels.get(tag, tag) から "<Person>" を生成
mask_with_fixed  → クロージャでchar・lengthを保持するファクトリ
```

`mask_with_fixed` だけファクトリ関数になっている理由：
パラメータ（char, length）を戦略関数のシグネチャ外で渡す必要があるため、
クロージャで事前束縛する。

---

## 3. @cache によるパイプラインキャッシュ

```python
@cache
def _get_pipeline(model: NERModel) -> Any:
    return hf_pipeline("token-classification", model=model.model_name, ...)
```

`NERModel` が `@dataclass(unsafe_hash=True)` なのはこのため。
- `model_name` と `aggregation_strategy` のみがハッシュキー
- `tag_labels`（dict）は `hash=False` で除外
- 同名モデルでラベルだけ変えても同一パイプラインを再利用

---

## 4. 後方置換アルゴリズム

```python
entities_to_mask = sorted(..., key=lambda e: e["start"], reverse=True)

for entity in entities_to_mask:
    result = result[:entity["start"]] + strategy(...) + result[entity["end"]:]
```

前から置換すると置換後の文字列長変化でoffsetがズレる。
後ろから処理することで既処理部分のインデックスに影響しない。

---

## 5. CLIのエンコーディング処理

```python
_BOM_ENCODINGS: list[tuple[bytes, str]] = [
    (codecs.BOM_UTF32_LE, "utf-32-le"),  # 4バイト（長い）
    (codecs.BOM_UTF32_BE, "utf-32-be"),
    (codecs.BOM_UTF16_LE, "utf-16-le"),  # 2バイト（短い）
    (codecs.BOM_UTF16_BE, "utf-16-be"),
    (codecs.BOM_UTF8, "utf-8-sig"),
]
```

長いBOMを先にチェックする理由：
UTF-32 LE BOM（FF FE 00 00）はUTF-16 LE BOM（FF FE）を先頭に含むため、
短い方を先に照合すると誤判定が起きる。

---

## 6. ファサードパターン（__init__.py）

```python
from kuronuri._masker import (mask, NERModel, ...)
__all__ = ["mask", "NERModel", ...]
```

`_masker.py` の先頭の `_` は「内部実装」を示す慣習。
将来ファイルを分割・リネームしても `__init__.py` だけ修正すればOK。

---

## 7. 設計原則まとめ

| 原則 | 実装箇所 |
|---|---|
| ファサードパターン | `__init__.py` |
| ストラテジーパターン | `MaskStrategy` 型エイリアス + 3戦略関数 |
| キャッシュ（シングルトン的） | `@cache` + `NERModel` のハッシュ設計 |
| アダプターパターン | `_cli.py` |
| 関心の分離 | CLI（I/O・エンコーディング）とコア（NER・置換）の完全分離 |
| 単一責任の原則 | 各ファイルが1つの責務を担う |

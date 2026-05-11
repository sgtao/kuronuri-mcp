"""
01_basic.py — kuronuri 基本動作確認

動作確認項目:
  1. 英語テキスト・デフォルト（ブロック戦略）
  2. 日本語テキスト・デフォルト（ブロック戦略）
  3. ラベル戦略（英語）
  4. ラベル戦略（日本語）
  5. 固定文字列戦略
  6. タグ絞り込み（人名のみ）
"""

from kuronuri import EN_MODEL, JA_MODEL, mask, mask_with_label, mask_with_fixed

SEP = "-" * 60


def section(title: str) -> None:
    print(f"\n{SEP}\n▶ {title}\n{SEP}")


# ── 1. 英語・ブロック（デフォルト） ──────────────────────────
section("1. 英語・ブロック戦略（デフォルト）")
en_text = "Hello, I'm John Doe. My email is john.doe@example.com and my phone is +1-800-555-0199."
print("入力:", en_text)
print("出力:", mask(en_text))

# ── 2. 日本語・ブロック ───────────────────────────────────────
section("2. 日本語・ブロック戦略（デフォルト）")
ja_text = "山田太郎です。メールは yamada.taro@example.co.jp、電話は 090-1234-5678 です。"
print("入力:", ja_text)
print("出力:", mask(ja_text, model=JA_MODEL))

# ── 3. 英語・ラベル戦略 ───────────────────────────────────────
section("3. 英語・ラベル戦略")
print("入力:", en_text)
print("出力:", mask(en_text, strategy=mask_with_label))

# ── 4. 日本語・ラベル戦略 ─────────────────────────────────────
section("4. 日本語・ラベル戦略")
print("入力:", ja_text)
print("出力:", mask(ja_text, model=JA_MODEL, strategy=mask_with_label))

# ── 5. 固定文字列戦略 ─────────────────────────────────────────
section("5. 固定文字列戦略（*** 5文字）")
print("入力:", en_text)
print("出力:", mask(en_text, strategy=mask_with_fixed(char="*", length=5)))

# ── 6. タグ絞り込み（人名のみ） ───────────────────────────────
section("6. タグ絞り込み（日本語・人名 PER のみ）")
print("入力:", ja_text)
print("出力:", mask(ja_text, model=JA_MODEL, mask_tags={"PER"}))

print(f"\n{SEP}\n✅ 完了\n{SEP}")

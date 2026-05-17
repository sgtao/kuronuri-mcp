"""
01_basic.py — kuronuri basic operation check

Verified scenarios:
  1. English text, default strategy (block)
  2. Japanese text, default strategy (block)
  3. Label strategy (English)
  4. Label strategy (Japanese)
  5. Fixed-string strategy
  6. Tag filtering (person names only)
"""

from kuronuri import JA_MODEL, mask, mask_with_fixed, mask_with_label

SEP = "-" * 60


def section(title: str) -> None:
    print(f"\n{SEP}\n▶ {title}\n{SEP}")


# ── 1. English, block (default) ──────────────────────────────
section("1. English — block strategy (default)")
en_text = "Hello, I'm John Doe. My email is john.doe@example.com and my phone is +1-800-555-0199."
print("Input:", en_text)
print("Output:", mask(en_text))

# ── 2. Japanese, block ────────────────────────────────────────
section("2. Japanese — block strategy (default)")
ja_text = "山田太郎です。メールは yamada.taro@example.co.jp、電話は 090-1234-5678 です。"
print("Input:", ja_text)
print("Output:", mask(ja_text, model=JA_MODEL))

# ── 3. English, label strategy ────────────────────────────────
section("3. English — label strategy")
print("Input:", en_text)
print("Output:", mask(en_text, strategy=mask_with_label))

# ── 4. Japanese, label strategy ───────────────────────────────
section("4. Japanese — label strategy")
print("Input:", ja_text)
print("Output:", mask(ja_text, model=JA_MODEL, strategy=mask_with_label))

# ── 5. Fixed-string strategy ──────────────────────────────────
section("5. Fixed-string strategy (*** 5 chars)")
print("Input:", en_text)
print("Output:", mask(en_text, strategy=mask_with_fixed(char="*", length=5)))

# ── 6. Tag filtering (person names only) ─────────────────────
section("6. Tag filtering — Japanese, PER (person) only")
print("Input:", ja_text)
print("Output:", mask(ja_text, model=JA_MODEL, mask_tags={"PER"}))

print(f"\n{SEP}\n✅ Done\n{SEP}")

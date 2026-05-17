"""
02_file_batch.py — Batch file masking

Reads all .txt files under data/, masks PII, and writes
the results to the masked/ directory.

Usage:
  python scripts/02_file_batch.py
  python scripts/02_file_batch.py --strategy label
  python scripts/02_file_batch.py --lang ja --strategy label
"""

import argparse
from pathlib import Path

from kuronuri import (
    EN_MODEL,
    JA_MODEL,
    mask,
    mask_with_block,
    mask_with_fixed,
    mask_with_label,
)

# ── Arguments ─────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="kuronuri batch file masking")
parser.add_argument("--lang", choices=["en", "ja"], default=None,
                    help="Language (auto-detected from filename if omitted)")
parser.add_argument("--strategy", choices=["block", "label", "fixed"], default="block",
                    help="Masking strategy (default: block)")
args = parser.parse_args()

# ── Resolve strategy ──────────────────────────────────────────
match args.strategy:
    case "label":
        strategy = mask_with_label
    case "fixed":
        strategy = mask_with_fixed(char="***", length=3)
    case _:
        strategy = mask_with_block

# ── Directory setup ───────────────────────────────────────────
root = Path(__file__).parent.parent
data_dir = root / "data"
output_dir = root / "masked"
output_dir.mkdir(exist_ok=True)

# ── Process files ─────────────────────────────────────────────
txt_files = list(data_dir.glob("*.txt"))
if not txt_files:
    print("No .txt files found in data/")
    raise SystemExit(1)

print(f"Strategy: {args.strategy} | Files: {len(txt_files)}\n")

for path in sorted(txt_files):
    # Auto-detect language from filename (_ja suffix → Japanese)
    if args.lang:
        model = JA_MODEL if args.lang == "ja" else EN_MODEL
    else:
        model = JA_MODEL if "_ja" in path.stem else EN_MODEL

    lang_label = "ja" if model is JA_MODEL else "en"
    text = path.read_text(encoding="utf-8")

    masked_text = mask(text, model=model, strategy=strategy)

    out_path = output_dir / f"{path.stem}_masked.txt"
    out_path.write_text(masked_text, encoding="utf-8")

    # Show summary of changes
    changed = sum(1 for a, b in zip(text, masked_text) if a != b)
    print(f"✅ {path.name} ({lang_label}) → {out_path.name}  [{changed} chars changed]")

print(f"\nOutput: {output_dir}/")

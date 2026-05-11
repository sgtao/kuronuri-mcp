"""
02_file_batch.py — ファイル一括マスキング処理

data/ 以下の .txt ファイルを全て読み込み、
masked/ ディレクトリにマスク済みファイルを出力する。

使い方:
  python scripts/02_file_batch.py
  python scripts/02_file_batch.py --strategy label
  python scripts/02_file_batch.py --lang ja --strategy label
"""

import argparse
from pathlib import Path

from kuronuri import JA_MODEL, EN_MODEL, mask, mask_with_block, mask_with_label, mask_with_fixed

# ── 引数 ──────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="kuronuri ファイル一括マスキング")
parser.add_argument("--lang", choices=["en", "ja"], default=None,
                    help="言語（省略時はファイル名で自動判定）")
parser.add_argument("--strategy", choices=["block", "label", "fixed"], default="block",
                    help="マスキング戦略（デフォルト: block）")
args = parser.parse_args()

# ── 戦略解決 ──────────────────────────────────────────────────
match args.strategy:
    case "label":
        strategy = mask_with_label
    case "fixed":
        strategy = mask_with_fixed(char="***", length=3)
    case _:
        strategy = mask_with_block

# ── ディレクトリ設定 ──────────────────────────────────────────
root = Path(__file__).parent.parent
data_dir = root / "data"
output_dir = root / "masked"
output_dir.mkdir(exist_ok=True)

# ── 処理 ──────────────────────────────────────────────────────
txt_files = list(data_dir.glob("*.txt"))
if not txt_files:
    print("data/ に .txt ファイルが見つかりません")
    raise SystemExit(1)

print(f"戦略: {args.strategy} | 対象: {len(txt_files)} ファイル\n")

for path in sorted(txt_files):
    # 言語の自動判定（ファイル名に _ja があれば日本語）
    if args.lang:
        model = JA_MODEL if args.lang == "ja" else EN_MODEL
    else:
        model = JA_MODEL if "_ja" in path.stem else EN_MODEL

    lang_label = "ja" if model is JA_MODEL else "en"
    text = path.read_text(encoding="utf-8")

    masked_text = mask(text, model=model, strategy=strategy)

    out_path = output_dir / f"{path.stem}_masked.txt"
    out_path.write_text(masked_text, encoding="utf-8")

    # 変更箇所のサマリー表示
    changed = sum(1 for a, b in zip(text, masked_text) if a != b)
    print(f"✅ {path.name} ({lang_label}) → {out_path.name}  [{changed} 文字変更]")

print(f"\n出力先: {output_dir}/")

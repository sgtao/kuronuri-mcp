"""日本語テキストの PII マスクスクリプト。

NER モデル（XLM-RoBERTa）で人名を検出し、
正規表現でメール・電話番号を補完してマスクする。
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from transformers import pipeline


MASK_LABELS: dict[str, str] = {
    "PER": "【人名】",
    "ORG": "【組織名】",
    "LOC": "【地名】",
    "EMAIL": "【メールアドレス】",
    "PHONE": "【電話番号】",
}

REGEX_PATTERNS: list[tuple[str, str]] = [
    ("EMAIL", r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
    ("PHONE", r"(?<!\d)0\d{1,4}[-－]?\d{2,4}[-－]?\d{3,4}(?!\d)"),
]


@dataclass
class Span:
    start: int
    end: int
    label: str


def _collect_ner_spans(text: str, ner_pipe) -> list[Span]:
    entities = ner_pipe(text)
    return [Span(e["start"], e["end"], e["entity_group"]) for e in entities]


def _collect_regex_spans(text: str) -> list[Span]:
    spans: list[Span] = []
    for label, pattern in REGEX_PATTERNS:
        for m in re.finditer(pattern, text):
            spans.append(Span(m.start(), m.end(), label))
    return spans


def _merge_spans(ner_spans: list[Span], regex_spans: list[Span]) -> list[Span]:
    """正規表現スパンを優先しつつ重複を除去して開始位置順に返す。

    正規表現（EMAIL/PHONE）はモデル誤分類より信頼度が高いため先に確定させる。
    """
    # 正規表現スパンを先に確定
    confirmed: list[Span] = sorted(regex_spans, key=lambda s: s.start)
    merged = list(confirmed)

    # NER スパンは正規表現スパンと重複しない部分のみ追加
    for span in sorted(ner_spans, key=lambda s: s.start):
        if any(s.start < span.end and span.start < s.end for s in confirmed):
            continue
        merged.append(span)

    return sorted(merged, key=lambda s: s.start)


def mask(text: str, ner_pipe) -> str:
    """テキスト中の PII をマスクして返す。

    Args:
        text: マスク対象のテキスト。
        ner_pipe: HuggingFace NER pipeline。

    Returns:
        PII をマスクラベルに置換したテキスト。
    """
    spans = _merge_spans(_collect_ner_spans(text, ner_pipe), _collect_regex_spans(text))

    result: list[str] = []
    cursor = 0
    for span in spans:
        result.append(text[cursor:span.start])
        result.append(MASK_LABELS.get(span.label, f"【{span.label}】"))
        cursor = span.end
    result.append(text[cursor:])
    return "".join(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="日本語テキストの PII マスク")
    parser.add_argument("--file", type=Path, help="マスク対象ファイル（省略時はサンプル実行）")
    args = parser.parse_args()

    ner_pipe = pipeline(
        "ner",
        model="tsmatz/xlm-roberta-ner-japanese",
        aggregation_strategy="simple",
    )

    if args.file:
        text = args.file.read_text(encoding="utf-8")
        print(mask(text, ner_pipe))
        return

    samples = [
        "山田太郎（yamada.taro@example.co.jp、090-1234-5678）の件について",
        "田中誠一様より 03-9876-5432 にご連絡ください。",
        "li.ming.dev@gmail.com 様より APIキーのリセット依頼がありました。",
    ]

    for text in samples:
        print(f"入力: {text}")
        print(f"出力: {mask(text, ner_pipe)}")
        print()


if __name__ == "__main__":
    main()

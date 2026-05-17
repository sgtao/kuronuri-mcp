"""Japanese text PII masking script.

Detects person names with an NER model (XLM-RoBERTa) and supplements
email addresses and phone numbers with regex before masking.
"""

import argparse
import re
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
    """Merge NER and regex spans, giving priority to regex matches.

    Regex spans (EMAIL/PHONE) are more reliable than model classification,
    so they are confirmed first and NER spans that overlap are dropped.
    """
    # Confirm regex spans first
    confirmed: list[Span] = sorted(regex_spans, key=lambda s: s.start)
    merged = list(confirmed)

    # Add NER spans only where they do not overlap with regex spans
    for span in sorted(ner_spans, key=lambda s: s.start):
        if any(s.start < span.end and span.start < s.end for s in confirmed):
            continue
        merged.append(span)

    return sorted(merged, key=lambda s: s.start)


def mask(text: str, ner_pipe) -> str:
    """Mask PII in text and return the result.

    Args:
        text: Input text to mask.
        ner_pipe: HuggingFace NER pipeline.

    Returns:
        Text with PII replaced by mask labels.
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
    parser = argparse.ArgumentParser(description="Japanese text PII masking")
    parser.add_argument("--file", type=Path, help="File to mask (runs samples if omitted)")
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
        print(f"Input:  {text}")
        print(f"Output: {mask(text, ner_pipe)}")
        print()


if __name__ == "__main__":
    main()

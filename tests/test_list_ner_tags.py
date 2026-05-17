"""Tests for list_ner_tags MCP tool."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_kuronuri_models():
    """Provide mocked kuronuri models with tag data."""
    en_model = MagicMock(name="EN_MODEL")
    en_model.model_name = "dslim/bert-base-NER"
    en_model.tag_labels = {"PER": "Person", "ORG": "Organization", "LOC": "Location"}
    en_model.default_mask_tags = frozenset({"PER", "ORG"})

    ja_model = MagicMock(name="JA_MODEL")
    ja_model.model_name = "llm-book/bert-base-japanese-v3-ner-wikipedia-dataset"
    ja_model.tag_labels = {"人名": "Person", "組織名": "Organization"}
    ja_model.default_mask_tags = frozenset({"人名"})

    with patch.dict(
        "sys.modules",
        {
            "kuronuri": MagicMock(
                EN_MODEL=en_model,
                JA_MODEL=ja_model,
            )
        },
    ):
        yield {"en_model": en_model, "ja_model": ja_model}


def test_list_ner_tags_returns_string(mock_kuronuri_models: dict) -> None:
    from server import list_ner_tags

    result = list_ner_tags(lang="en")

    assert isinstance(result, str)


def test_list_ner_tags_en_contains_model_name(mock_kuronuri_models: dict) -> None:
    from server import list_ner_tags

    result = list_ner_tags(lang="en")

    assert "dslim/bert-base-NER" in result


def test_list_ner_tags_en_contains_all_tags(mock_kuronuri_models: dict) -> None:
    from server import list_ner_tags

    result = list_ner_tags(lang="en")

    assert "PER" in result
    assert "ORG" in result
    assert "LOC" in result


def test_list_ner_tags_en_marks_default_mask_tags(mock_kuronuri_models: dict) -> None:
    from server import list_ner_tags

    result = list_ner_tags(lang="en")

    lines = result.splitlines()
    per_line = next(line for line in lines if "PER" in line)
    loc_line = next(line for line in lines if "LOC" in line)

    assert "✅" in per_line
    assert "—" in loc_line


def test_list_ner_tags_ja_uses_ja_model(mock_kuronuri_models: dict) -> None:
    from server import list_ner_tags

    result = list_ner_tags(lang="ja")

    assert "llm-book/bert-base-japanese-v3-ner-wikipedia-dataset" in result
    assert "人名" in result


def test_list_ner_tags_default_lang_is_en(mock_kuronuri_models: dict) -> None:
    from server import list_ner_tags

    result = list_ner_tags()

    assert "dslim/bert-base-NER" in result


def test_list_ner_tags_output_is_markdown_table(mock_kuronuri_models: dict) -> None:
    from server import list_ner_tags

    result = list_ner_tags(lang="en")

    assert "| Tag |" in result
    assert "|---|" in result


@pytest.mark.model
def test_list_ner_tags_en_real_model() -> None:
    from server import list_ner_tags

    result = list_ner_tags(lang="en")

    assert isinstance(result, str)
    assert "## EN" in result
    assert "| タグ |" in result


@pytest.mark.model
def test_list_ner_tags_ja_real_model() -> None:
    from server import list_ner_tags

    result = list_ner_tags(lang="ja")

    assert isinstance(result, str)
    assert "## JA" in result

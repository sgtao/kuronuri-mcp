"""Tests for mask_text MCP tool."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_kuronuri():
    """Provide mocked kuronuri module to avoid loading real NER models."""
    en_model = MagicMock(name="EN_MODEL")
    ja_model = MagicMock(name="JA_MODEL")
    mask_with_block = MagicMock(name="mask_with_block")
    mask_with_label = MagicMock(name="mask_with_label")
    mask_with_fixed_strategy = MagicMock(name="mask_with_fixed_strategy")
    mask_with_fixed = MagicMock(return_value=mask_with_fixed_strategy)
    mask = MagicMock(return_value="masked text")

    with patch.dict(
        "sys.modules",
        {
            "kuronuri": MagicMock(
                EN_MODEL=en_model,
                JA_MODEL=ja_model,
                mask=mask,
                mask_with_block=mask_with_block,
                mask_with_label=mask_with_label,
                mask_with_fixed=mask_with_fixed,
            )
        },
    ):
        yield {
            "en_model": en_model,
            "ja_model": ja_model,
            "mask": mask,
            "mask_with_block": mask_with_block,
            "mask_with_label": mask_with_label,
            "mask_with_fixed": mask_with_fixed,
            "mask_with_fixed_strategy": mask_with_fixed_strategy,
        }


def test_mask_text_default_strategy_uses_block(mock_kuronuri: dict) -> None:
    from server import mask_text

    mask_text("Hello John", lang="en")

    mock_kuronuri["mask"].assert_called_once_with(
        "Hello John",
        model=mock_kuronuri["en_model"],
        mask_tags=None,
        strategy=mock_kuronuri["mask_with_block"],
    )


def test_mask_text_label_strategy(mock_kuronuri: dict) -> None:
    from server import mask_text

    mask_text("Hello John", lang="en", strategy="label")

    mock_kuronuri["mask"].assert_called_once_with(
        "Hello John",
        model=mock_kuronuri["en_model"],
        mask_tags=None,
        strategy=mock_kuronuri["mask_with_label"],
    )


def test_mask_text_fixed_strategy(mock_kuronuri: dict) -> None:
    from server import mask_text

    mask_text("Hello John", lang="en", strategy="fixed", fixed_char="*", fixed_length=4)

    mock_kuronuri["mask_with_fixed"].assert_called_once_with(char="*", length=4)
    mock_kuronuri["mask"].assert_called_once_with(
        "Hello John",
        model=mock_kuronuri["en_model"],
        mask_tags=None,
        strategy=mock_kuronuri["mask_with_fixed_strategy"],
    )


def test_mask_text_ja_lang_uses_ja_model(mock_kuronuri: dict) -> None:
    from server import mask_text

    mask_text("山田太郎です", lang="ja")

    mock_kuronuri["mask"].assert_called_once_with(
        "山田太郎です",
        model=mock_kuronuri["ja_model"],
        mask_tags=None,
        strategy=mock_kuronuri["mask_with_block"],
    )


def test_mask_text_with_mask_tags(mock_kuronuri: dict) -> None:
    from server import mask_text

    mask_text("Hello John", lang="en", mask_tags=["PER", "ORG"])

    mock_kuronuri["mask"].assert_called_once_with(
        "Hello John",
        model=mock_kuronuri["en_model"],
        mask_tags=frozenset({"PER", "ORG"}),
        strategy=mock_kuronuri["mask_with_block"],
    )


def test_mask_text_empty_string(mock_kuronuri: dict) -> None:
    from server import mask_text

    result = mask_text("", lang="en")

    mock_kuronuri["mask"].assert_called_once()
    assert result == "masked text"


def test_mask_text_returns_string(mock_kuronuri: dict) -> None:
    from server import mask_text

    result = mask_text("some text")

    assert isinstance(result, str)


def test_mask_text_unknown_lang_falls_back_to_en_model(mock_kuronuri: dict) -> None:
    from server import mask_text

    mask_text("text", lang="fr")

    mock_kuronuri["mask"].assert_called_once_with(
        "text",
        model=mock_kuronuri["en_model"],
        mask_tags=None,
        strategy=mock_kuronuri["mask_with_block"],
    )


@pytest.mark.model
def test_mask_text_en_real_model() -> None:
    from server import mask_text

    result = mask_text("My name is John Smith and I live in New York.", lang="en")

    assert isinstance(result, str)
    assert "John Smith" not in result


@pytest.mark.model
def test_mask_text_ja_real_model() -> None:
    from server import mask_text

    result = mask_text("私は山田太郎です。", lang="ja")

    assert isinstance(result, str)
    assert "山田太郎" not in result

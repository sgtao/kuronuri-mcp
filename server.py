"""kuronuri MCP Server — Claude会話内でPIIマスキングを実行するサーバー."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("kuronuri")


@mcp.tool()
def mask_text(
    text: str,
    lang: str = "en",
    strategy: str = "block",
    mask_tags: list[str] | None = None,
    fixed_char: str = "█",
    fixed_length: int = 3,
) -> str:
    """テキスト内のPII（個人情報）をkuronuriでマスキングして返す。

    Args:
        text: マスク対象のテキスト
        lang: 言語 ("en" または "ja")
        strategy: マスキング戦略 ("block" / "label" / "fixed")
        mask_tags: マスク対象タグのリスト（Noneでモデルのデフォルト）
        fixed_char: fixed戦略の置換文字 (デフォルト "█")
        fixed_length: fixed戦略の文字数 (デフォルト 3)

    Returns:
        マスキング済みテキスト
    """
    from kuronuri import (
        EN_MODEL,
        JA_MODEL,
        mask,
        mask_with_block,
        mask_with_fixed,
        mask_with_label,
    )

    model = JA_MODEL if lang == "ja" else EN_MODEL

    match strategy:
        case "label":
            mask_strategy = mask_with_label
        case "fixed":
            mask_strategy = mask_with_fixed(char=fixed_char, length=fixed_length)
        case _:
            mask_strategy = mask_with_block

    tags: frozenset[str] | None = frozenset(mask_tags) if mask_tags else None

    return mask(text, model=model, mask_tags=tags, strategy=mask_strategy)


@mcp.tool()
def list_ner_tags(lang: str = "en") -> str:
    """指定言語モデルのNERタグ一覧とデフォルトマスク対象をMarkdown表で返す。

    Args:
        lang: 言語 ("en" または "ja")

    Returns:
        タグ情報のMarkdown表
    """
    from kuronuri import EN_MODEL, JA_MODEL

    model = JA_MODEL if lang == "ja" else EN_MODEL

    lines = [
        f"## {lang.upper()} モデル: `{model.model_name}`\n",
        "| タグ | ラベル | デフォルトマスク |",
        "|---|---|---|",
    ]
    for tag, label in model.tag_labels.items():
        default = "✅" if tag in model.default_mask_tags else "—"
        lines.append(f"| `{tag}` | {label} | {default} |")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")

"""
03_mcp_client.py — kuronuri-mcp MCP server smoke test

Verifies that the kuronuri-mcp server is reachable as an MCP client
and calls mask_text / list_ner_tags directly over the MCP protocol.

Prerequisite:
  claude mcp add kuronuri -- uv run --directory /path/to/kuronuri-mcp python server.py

Usage:
  python scripts/03_mcp_client.py
"""

import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Path to server.py — adjust to your environment
SERVER_PATH = Path(__file__).parent.parent.parent / "kuronuri-mcp" / "server.py"

SAMPLE_EN = "Hello, I'm John Doe. My email is john.doe@example.com."
SAMPLE_JA = "山田太郎です。メールは yamada.taro@example.co.jp、電話は 090-1234-5678 です。"

SEP = "-" * 60


async def run() -> None:
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", str(SERVER_PATH)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # ── List available tools ──────────────────────────
            tools = await session.list_tools()
            print("Available tools:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")
            print()

            # ── list_ner_tags (English) ───────────────────────
            print(SEP)
            print("▶ list_ner_tags(lang='en')")
            print(SEP)
            result = await session.call_tool("list_ner_tags", {"lang": "en"})
            print(result.content[0].text)

            # ── list_ner_tags (Japanese) ──────────────────────
            print(SEP)
            print("▶ list_ner_tags(lang='ja')")
            print(SEP)
            result = await session.call_tool("list_ner_tags", {"lang": "ja"})
            print(result.content[0].text)

            # ── mask_text: English, block strategy ───────────
            print(SEP)
            print("▶ mask_text: English, block strategy")
            print(SEP)
            result = await session.call_tool("mask_text", {
                "text": SAMPLE_EN,
                "lang": "en",
                "strategy": "block",
            })
            print("Input:", SAMPLE_EN)
            print("Output:", result.content[0].text)

            # ── mask_text: Japanese, block strategy ───────────
            print(SEP)
            print("▶ mask_text: Japanese, block strategy")
            print(SEP)
            result = await session.call_tool("mask_text", {
                "text": SAMPLE_JA,
                "lang": "ja",
                "strategy": "block",
            })
            print("Input:", SAMPLE_JA)
            print("Output:", result.content[0].text)

            # ── mask_text: Japanese, label strategy ───────────
            print(SEP)
            print("▶ mask_text: Japanese, label strategy")
            print(SEP)
            result = await session.call_tool("mask_text", {
                "text": SAMPLE_JA,
                "lang": "ja",
                "strategy": "label",
            })
            print("Input:", SAMPLE_JA)
            print("Output:", result.content[0].text)

            # ── mask_text: person names only ──────────────────
            print(SEP)
            print("▶ mask_text: Japanese, PER (person) only")
            print(SEP)
            result = await session.call_tool("mask_text", {
                "text": SAMPLE_JA,
                "lang": "ja",
                "strategy": "block",
                "mask_tags": ["PER"],
            })
            print("Input:", SAMPLE_JA)
            print("Output:", result.content[0].text)

    print(f"\n{SEP}\n✅ Done\n{SEP}")


if __name__ == "__main__":
    asyncio.run(run())

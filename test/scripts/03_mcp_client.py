"""
03_mcp_client.py — kuronuri-mcp MCPサーバーの動作確認

Claude Code 上で kuronuri-mcp が登録済みかを確認し、
MCP クライアントとして mask_text / list_ner_tags を呼び出す。

前提:
  claude mcp add kuronuri -- uv run --directory /path/to/kuronuri-mcp python server.py

使い方:
  python scripts/03_mcp_client.py
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path

# kuronuri-mcp の server.py へのパス（環境に合わせて変更）
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

            # ── ツール一覧確認 ────────────────────────────────
            tools = await session.list_tools()
            print("利用可能なツール:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")
            print()

            # ── list_ner_tags（英語） ─────────────────────────
            print(SEP)
            print("▶ list_ner_tags(lang='en')")
            print(SEP)
            result = await session.call_tool("list_ner_tags", {"lang": "en"})
            print(result.content[0].text)

            # ── list_ner_tags（日本語） ───────────────────────
            print(SEP)
            print("▶ list_ner_tags(lang='ja')")
            print(SEP)
            result = await session.call_tool("list_ner_tags", {"lang": "ja"})
            print(result.content[0].text)

            # ── mask_text: 英語・ブロック ─────────────────────
            print(SEP)
            print("▶ mask_text: 英語・block戦略")
            print(SEP)
            result = await session.call_tool("mask_text", {
                "text": SAMPLE_EN,
                "lang": "en",
                "strategy": "block",
            })
            print("入力:", SAMPLE_EN)
            print("出力:", result.content[0].text)

            # ── mask_text: 日本語・block ──────────────────────
            print(SEP)
            print("▶ mask_text: 日本語・block戦略")
            print(SEP)
            result = await session.call_tool("mask_text", {
                "text": SAMPLE_JA,
                "lang": "ja",
                "strategy": "block",
            })
            print("入力:", SAMPLE_JA)
            print("出力:", result.content[0].text)

            # ── mask_text: 日本語・label ──────────────────────
            print(SEP)
            print("▶ mask_text: 日本語・label戦略")
            print(SEP)
            result = await session.call_tool("mask_text", {
                "text": SAMPLE_JA,
                "lang": "ja",
                "strategy": "label",
            })
            print("入力:", SAMPLE_JA)
            print("出力:", result.content[0].text)

            # ── mask_text: 人名のみ ───────────────────────────
            print(SEP)
            print("▶ mask_text: 日本語・人名(PER)のみ")
            print(SEP)
            result = await session.call_tool("mask_text", {
                "text": SAMPLE_JA,
                "lang": "ja",
                "strategy": "block",
                "mask_tags": ["PER"],
            })
            print("入力:", SAMPLE_JA)
            print("出力:", result.content[0].text)

    print(f"\n{SEP}\n✅ 完了\n{SEP}")


if __name__ == "__main__":
    asyncio.run(run())

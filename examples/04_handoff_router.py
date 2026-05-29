"""handoff を使ったエージェント間ルーティング例。

日本語には日本語エージェント、英語には英語エージェントに委譲する例です。
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

# OpenAI Agents SDK から Agent, Runner, handoff をインポート
from dotenv import load_dotenv
from agents import Agent, Runner, handoff

# プロジェクトのルートディレクトリを取得（.env ファイルの場所を特定するため）
ROOT_DIR = Path(__file__).resolve().parents[1]


async def main() -> None:
    """言語別エージェントにルーティングする例を実行する。"""
    # 1. .env ファイルから環境変数を読み込む
    #   ROOT_DIR / ".env" でプロジェクトルートにある .env を指す
    load_dotenv(ROOT_DIR / ".env")

    # 2. OPENAI_API_KEY が設定されているか確認
    #   未設定の場合はエラーを発生させて実行を止める
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    # 3. OpenAI モデル名を取得（環境変数、なければデフォルトの gpt-4.1-mini）
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    # 4. 日本語エージェントを作成
    #   name: エージェントの名前（識別用）
    #   instructions: 日本語で簡潔に回答するよう指示
    #   model: 使用する OpenAI モデル
    japanese_agent = Agent(
        name="JapaneseAssistant",
        instructions="日本語で簡潔に回答してください。",
        model=model,
    )

    # 5. 英語エージェントを作成
    #   name: エージェントの名前（識別用）
    #   instructions: 英語で簡潔に回答するよう指示
    #   model: 使用する OpenAI モデル
    english_agent = Agent(
        name="EnglishAssistant",
        instructions="Respond briefly in English.",
        model=model,
    )

    # 6. ルーターエージェントを作成（handoff 指定）
    #   name: エージェントの名前（識別用）
    #   instructions:
    #     「日本語の入力は Japanese Assistant に、英語の入力は English Assistant に委譲」
    #     という委任ルールを指示
    #   handoffs: 委譲可能なエージェントのリスト
    #     handoff(japanese_agent): 日本語エージェントへ委譲
    #     handoff(english_agent): 英語エージェントへ委譲
    #     LLM が入力言語を判断して適切なエージェントへ自動で委譲
    #   model: 使用する OpenAI モデル
    router = Agent(
        name="LanguageRouter",
        instructions="日本語の入力は Japanese Assistant に、英語の入力は English Assistant に委譲してください。",
        handoffs=[handoff(japanese_agent), handoff(english_agent)],
        model=model,
    )

    # 7. Runner.run() でルーターエージェントを実行
    #   router: 実行するエージェント（手動で委譲先の設定済み）
    #   2 つ目の引数: ユーザーからの入力（プロンプト）
    #   Agent は入力を解析し、日本語なら japanese_agent、英語なら english_agent に委譲
    #   await で非同期に実行し、結果を result に格納
    result = await Runner.run(
        router,
        "Please explain the features of OpenAI Agents SDK.",
    )

    # 8. 最終的な結果を出力
    #   result.final_output: 委譲されたエージェントが生成した最終的なテキストレスポンス
    print(result.final_output)


# スクリプトを直接実行した時のエントリポイント
#   asyncio.run() でイベントループを起動し、main() コルーチンを実行
if __name__ == "__main__":
    asyncio.run(main())

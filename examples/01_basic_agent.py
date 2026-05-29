"""最小構成の OpenAI Agents SDK 例。

Agent と Runner を使って、1 つのリクエストでテキスト生成を行います。
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

# OpenAI Agents SDK で Agent と Runner をインポート
from dotenv import load_dotenv
from agents import Agent, Runner

# プロジェクトのルートディレクトリを取得（.env ファイルの場所を特定するため）
ROOT_DIR = Path(__file__).resolve().parents[1]


async def main() -> None:
    """最小構成のエージェントを実行する。"""
    # 1. .env ファイルから環境変数を読み込む
    #   ROOT_DIR / ".env" でプロジェクトルートにある .env を指す
    load_dotenv(ROOT_DIR / ".env")

    # 2. OPENAI_API_KEY が設定されているか確認
    #   未設定の場合はエラーを発生させて実行を止める
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    # 3. OpenAI モデル名を取得（環境変数、なければデフォルトの gpt-4.1-mini）
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    # 4. Agent を作成
    #   name: エージェントの名前（ログやデバッグで識別用）
    #   instructions: エージェントへの指示（システムプロンプト）
    #     この例：「日本語で明確かつ簡潔に答えよ」という制約
    #   model: 使用する OpenAI モデル名
    agent = Agent(
        name="History Tutor",
        instructions="You answer clearly and concisely in Japanese.",
        model=model,
    )

    # 5. Runner.run() でエージェントを実行
    #   agent: 実行するエージェント
    #   2 つ目の引数: ユーザーからの入力（プロンプト）
    #   await で非同期に実行し、結果を result に格納
    result = await Runner.run(
        agent,
        "OpenAI Agents SDK の概要を 2 文で説明してください。",
    )

    # 6. 生成されたテキスト（最終出力）を出力
    #   result.final_output: エージェントの最終的なテキストレスポンス
    print(result.final_output)


# スクリプトを直接実行した時のエントリポイント
#   asyncio.run() でイベントループを起動し、main() コルーチンを実行
if __name__ == "__main__":
    asyncio.run(main())

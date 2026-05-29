"""@function_tool を使ったツール例。

Python 関数をエージェントのツールとして公開し、エージェントが自律的にツールを呼び出す例です。
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

# OpenAI Agents SDK から Agent, Runner, function_tool をインポート
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

# プロジェクトのルートディレクトリを取得（.env ファイルの場所を特定するため）
ROOT_DIR = Path(__file__).resolve().parents[1]


# @function_tool デコレーターで Python 関数をエージェントのツールとして公開
# エージェントはこの関数を「検索ツール」として自律的に呼び出せる
@function_tool
def search_python_sdk_docs(topic: str) -> str:
    """Python SDK 関連のドキュメント要約を返す（モック）。

    Args:
        topic: 検索したいトピック（例：responses, images, embeddings）

    Returns:
        該当トピックのドキュメント要約テキスト
    """
    # 模擬的なドキュメント知識ベース（辞書形式）
    docs = {
        "responses": "Responses API はテキスト、画像、ツール呼び出しなどを統一的に扱えます。",
        "images": "Images API ではテキストから画像生成ができます。",
        "embeddings": "Embeddings API は意味検索やクラスタリングに使えます。",
    }

    # 引数 topic を小文字に変換して辞書から検索
    # 見つからなければ「未登録」メッセージを返す
    return docs.get(topic.lower(), f"{topic} に関する要約は未登録です。")


async def main() -> None:
    """ツール付きエージェントを実行する。"""
    # 1. .env ファイルから環境変数を読み込む
    #   ROOT_DIR / ".env" でプロジェクトルートにある .env を指す
    load_dotenv(ROOT_DIR / ".env")

    # 2. OPENAI_API_KEY が設定されているか確認
    #   未設定の場合はエラーを発生させて実行を止める
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    # 3. OpenAI モデル名を取得（環境変数、なければデフォルトの gpt-4.1-mini）
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    # 4. Agent を作成（ツールを付与）
    #   name: エージェントの名前（ログやデバッグで識別用）
    #   instructions: エージェントへの指示
    #     「必要に応じて search_python_sdk_docs ツールを使って日本語で答えてください」
    #   tools: エージェントが使用可能なツールのリスト
    #     この例では search_python_sdk_docs 関数をツールとして付与
    #   model: 使用する OpenAI モデル名
    agent = Agent(
        name="SDK Tutor",
        instructions="必要に応じて search_python_sdk_docs ツールを使って日本語で答えてください。",
        tools=[search_python_sdk_docs],
        model=model,
    )

    # 5. Runner.run() でエージェントを実行
    #   agent: 実行するエージェント（ツール付き）
    #   2 つ目の引数: ユーザーからの入力（プロンプト）
    #   エージェントは必要と判断すると search_python_sdk_docs ツールを自律的に呼び出す
    #   await で非同期に実行し、結果を result に格納
    result = await Runner.run(
        agent,
        "Responses の要点を 1 文で説明してください。",
    )

    # 6. 生成されたテキスト（最終出力）を出力
    #   result.final_output: エージェントの最終的なテキストレスポンス
    #   （ツール呼び出しの結果も考慮した回答）
    print(result.final_output)


# スクリプトを直接実行した時のエントリポイント
#   asyncio.run() でイベントループを起動し、main() コルーチンを実行
if __name__ == "__main__":
    asyncio.run(main())

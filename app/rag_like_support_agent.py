"""FAQ 検索ツール付きのサポートエージェント例。

RAG 風の小規模 FAQ をツールの形で提供し、エージェントが検索して回答する例です。
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


# 小規模な FAQ データベース（モック知識ベース）
# 本番環境では、これをベクトルデータベース（Chroma, Pinecone, FAISS など）に置き換える
FAQS = {
    # 料金に関する FAQ
    "pricing": "料金は利用モデルとトークン量で変わります。最新の価格表を確認してください。",
    # Responses API に関する FAQ
    "responses": "Responses API は入力と出力の統一インターフェースです。",
    # handoff機能に関するFAQ
    "handoff": "handoff は別エージェントへの役割委譲に使います。",
    # ツール機能に関する FAQ
    "tool": "function_tool を使うと Python 関数をエージェントのツールとして公開できます。",
}


# @function_tool デコレーターで Python 関数をエージェントのツールとして公開
# エージェントはこの関数を自律的に呼び出して FAQ を検索できる
@function_tool
def search_faq(keyword: str) -> str:
    """組み込み FAQ をキーワードで検索する。

    Args:
        keyword: 検索キーワード（例："handoff", "tool", "pricing"）

    Returns:
        一致した FAQ のリスト（複数件あり得る）または「該当 FAQ は見つかりませんでした」
    """
    # キーワードを小文字に変換（大文字小文字を区別しない検索）
    keyword = keyword.lower()

    # FAQ 辞書からキーワードが一致する項目を検索
    # 条件：
    #   1. キーワードが FAQ キー（例："pricing"）に含まれる
    #   2. またはキーワードが FAQ 値（説明文）に含まれる
    matches = [
        f"- {k}: {v}"  # 結果を整形："- キー：説明"
        for k, v in FAQS.items()
        if keyword in k or keyword in v.lower()
    ]

    # 一致する FAQ がなかった場合
    if not matches:
        return "該当 FAQ は見つかりませんでした。"

    # 一致した FAQ を改行で繋いで返す（複数件あり得る）
    return "\n".join(matches)


async def main() -> None:
    """FAQ 検索ツール付きサポートエージェントを実行する。"""
    # 1. .env ファイルから環境変数を読み込む
    #   ROOT_DIR / ".env" でプロジェクトルートにある .env を指す
    load_dotenv(ROOT_DIR / ".env")

    # 2. OPENAI_API_KEY が設定されているか確認
    #   未設定の場合はエラーを発生させて実行を止める
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    # 3. OpenAI モデル名を取得（環境変数、なければデフォルトの gpt-4.1-mini）
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    # 4. Agent を作成（FAQ 検索ツールを付与）
    #   name: エージェントの名前（識別用）
    #   instructions:
    #     ユーザー質問に答える前に、必要なら search_faq を使って関連情報を調べてください
    #     回答は日本語で簡潔にまとめてください
    #   tools: エージェントが使用可能なツールのリスト
    #     この例では search_faq を付与（FAQ 検索機能）
    #   model: 使用する OpenAI モデル
    agent = Agent(
        name="Support Agent",
        instructions=(
            "ユーザー質問に答える前に、必要なら search_faq を使って関連情報を調べてください。"
            "回答は日本語で簡潔にまとめてください。"
        ),
        tools=[search_faq],
        model=model,
    )

    # 5. Runner.run() でエージェントを実行
    #   agent: 実行するエージェント（FAQ 検索ツール付き）
    #   2 つ目の引数: ユーザーからの入力（プロンプト）
    #   Agent は「handoff と tool の違い」について回答する際、
    #   search_faq ツールを自律的に呼び出して関連 FAQ を検索
    #   await で非同期に実行し、結果を result に格納
    result = await Runner.run(
        agent,
        "handoff と tool の違いを説明してください。",
    )

    # 6. 最終的な回答を出力
    #   result.final_output: エージェントが生成した最終的なテキストレスポンス
    #     （FAQ 検索結果を考慮した回答）
    print(result.final_output)


# スクリプトを直接実行した時のエントリポイント
#   asyncio.run() でイベントループを起動し、main() コルーチンを実行
if __name__ == "__main__":
    asyncio.run(main())

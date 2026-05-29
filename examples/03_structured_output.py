"""Pydantic を使った構造化出力例。

output_type に Pydantic モデルを指定することで、JSON 形式に近い構造化データを返させます。
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

# OpenAI Agents SDK から Agent, Runner をインポート
from dotenv import load_dotenv
# Pydantic から BaseModel をインポート（データ構造定義用）
from pydantic import BaseModel
from agents import Agent, Runner

# プロジェクトのルートディレクトリを取得（.env ファイルの場所を特定するため）
ROOT_DIR = Path(__file__).resolve().parents[1]


# Pydantic の BaseModel を継承して、学習計画のデータ構造を定義
# これにより、LLM が出力するデータが常にこの構造になるように強制できる
class StudyPlan(BaseModel):
    """学習計画の出力構造。"""

    # 学習トピック（文字列）
    topic: str

    # 優先度（文字列、例："high"、"medium"、"low"）
    priority: str

    # 想定所要時間（整数、時間単位）
    estimated_hours: int

    # 実践的なタスク（文字列、例："コードを書く"）
    hands_on_task: str


async def main() -> None:
    """構造化出力の例を実行する。"""
    # 1. .env ファイルから環境変数を読み込む
    #   ROOT_DIR / ".env" でプロジェクトルートにある .env を指す
    load_dotenv(ROOT_DIR / ".env")

    # 2. OPENAI_API_KEY が設定されているか確認
    #   未設定の場合はエラーを発生させて実行を止める
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    # 3. OpenAI モデル名を取得（環境変数、なければデフォルトの gpt-4.1-mini）
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    # 4. Agent を作成（output_type で構造化出力を指定）
    #   name: エージェントの名前（ログやデバッグで識別用）
    #   instructions: エージェントへの指示（システムプロンプト）
    #     この例：「OpenAI Agents SDK の学習計画を作成してください」
    #   output_type: Pydantic モデルを指定
    #     LLM が StudyPlan 構造のデータしか返さないように強制
    #     これにより、安定した構造化 JSON 出力が得られる
    #   model: 使用する OpenAI モデル名
    agent = Agent(
        name="Study Planner",
        instructions="OpenAI Agents SDK の学習計画を作成してください。",
        output_type=StudyPlan,
        model=model,
    )

    # 5. Runner.run() でエージェントを実行
    #   agent: 実行するエージェント（構造化出力指定付き）
    #   2 つ目の引数: ユーザーからの入力（プロンプト）
    #   Agent は output_type 指定により、StudyPlan 構造のデータのみを返す
    #   await で非同期に実行し、結果を result に格納
    result = await Runner.run(
        agent,
        "まず取り組むべき学習テーマを 1 件出してください。",
    )

    # 6. 構造化された結果を JSON 形式で出力
    #   result.final_output: StudyPlan オブジェクト（Pydantic モデル）
    #   .model_dump_json(): Pydantic オブジェクトを JSON 文字列に変換
    #   indent=2: 2 文字インデントで整形（見やすく）
    #   ensure_ascii=False: 日本語をそのまま表示（エスケープしない）
    print(result.final_output.model_dump_json(indent=2, ensure_ascii=False))


# スクリプトを直接実行した時のエントリポイント
#   asyncio.run() でイベントループを起動し、main() コルーチンを実行
if __name__ == "__main__":
    asyncio.run(main())

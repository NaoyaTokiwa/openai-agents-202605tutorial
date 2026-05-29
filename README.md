# OpenAI Agents SDK チュートリアル (Docker 対応)

このプロジェクトは、OpenAI Agents SDK を学ぶためのチュートリアルです。  

## Dockerを用いた理由

ローカルの仮想環境が Python 3.9 であり、OpenAI Agents SDK は Python 3.10 以上が前提だったため、Dockerを用いた。

## 構成

- `examples/01_basic_agent.py` : 最小構成の Agent + Runner
- `examples/02_tool_agent.py` : `@function_tool` を使うツール付きエージェント
- `examples/03_structured_output.py` : Pydantic による構造化出力
- `examples/04_handoff_router.py` : 日本語/英語エージェントへのハンドオフルーター
- `app/rag_like_support_agent.py` : FAQ 検索ツール付きのサポートエージェント

## セットアップ

1. `.env.example` を `.env` にコピー
2. `.env` に OpenAI API キーを設定
3. Docker をビルドして実行

### 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して、API キーを設定してください。

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
```

## Docker による実行

```bash
# ビルド
docker compose build

# コンテナに入る（sh プロンプト）
docker compose run --rm app bash

# コンテナ内でサンプルを実行
python examples/01_basic_agent.py
python examples/02_tool_agent.py
# ...
# 退出
exit
```

## 学べること

1. `Agent` と `Runner` の基本操作
2. `@function_tool` で Python 関数をツールとして公開する方法
3. Pydantic モデルで構造化 JSON 出力を得る方法
4. `handoff()` によるマルチエージェントの分岐と委譲
5. FAQ 検索ツールを組み込んだ実務寄りエージェントの作り方

## 補足

- 本チュートリアルは Python 3.11 の Docker イメージを想定しています。
- 実行には `openai-agents` パッケージと OpenAI API キーが必要です。
- OpenAI Agents SDK は、軽量なエージェント構築、ツール、ハンドオフ、ガードレール、トレーシングなどを提供する Python SDK です。

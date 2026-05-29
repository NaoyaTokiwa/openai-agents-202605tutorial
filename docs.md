# OpenAI Agent SDK - ドキュメントまとめ

> FAQ 検索ツール付きサポートエージェントのサンプルコード、機能整理、実装解説をまとめたドキュメント

---

## 目次

1. [概要](#概要)
2. [基本的な構造](#基本的な構造)
3. [Agent と Runner](#agent-と-runner)
4. [function_tool ユーザーガイド](#function_tool-ユーザーガイド)
5. [FAQ 検索ツール付きサポートエージェント](#faq-検索ツール付きサポートエージェント)
6. [RAG 風小規模 FAQ の実装](#rag-風小規模-faq-の実装)
7. [重要ポイントとベストプラクティス](#重要ポイントとベストプラクティス)
8. [よくある質問](#よくある質問)

---

## 概要

OpenAI Agent SDK は、Python で LLM ベースのエージェントを構築するための公式ライブラリです。主要な機能は以下の通りです。

### 主要機能

| 機能 | 説明 |
|---|---|
| **Agent** | LLM エージェントの定義。名前、指示、ツール、モデルを設定 |
| **Runner** | Agent を非同期で実行。`await Runner.run()` で呼び出し |
| **@function_tool** | Python 関数をエージェントのツールとして公開 |
| **instructions** | エージェントの振る舞いを制御するプロンプト |
| **tools** | エージェントが使用可能なツールのリスト |

### インストール

```bash
pip install openai-agents
```

### 環境変数の設定

`.env` ファイルに以下の設定を追加：

```env
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4.1-mini
```

---

## 基本的な構造

### サンプルコードの構成

```python
from __future__ import annotations
import asyncio, os
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool


ROOT_DIR = Path(__file__).resolve().parents[1]
```

#### 各インポートの説明

| インポート | 役割 |
|---|---|
| `asyncio` | 非同期処理の実行（`asyncio.run()`） |
| `os` | 環境変数の読み取り（`os.getenv()`） |
| `Path` | ファイルパスの操作（`.env` の場所特定） |
| `load_dotenv` | `.env` ファイルから環境変数を読み込み |
| `Agent` | エージェントの定義クラス |
| `Runner` | エージェント実行エンジン |
| `function_tool` | Python 関数をツールとして公開するデコレーター |

---

## Agent と Runner

### Agent の作成

```python
model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
agent = Agent(
    name="Support Agent",
    instructions=(
        "ユーザー質問に答える前に、必要なら search_faq を使って関連情報を調べてください。"
        "回答は日本語で簡潔にまとめてください。"
    ),
    tools=[search_faq],
    model=model,
)
```

#### Agent パラメータ

| パラメータ | 説明 | デフォルト |
|---|---|---|
| `name` | エージェントの名前（識別用） | 必須 |
| `instructions` | エージェントの振る舞いを制御するプロンプト | 任意 |
| `tools` | エージェントが使用可能なツールのリスト | `[]` |
| `model` | 使用する OpenAI モデル | `gpt-4o` |

### Runner の実行

```python
result = await Runner.run(
    agent,
    "handoff と tool の違いを説明してください。",
)
print(result.final_output)
```

#### Runner.run() のパラメータ

| パラメータ | 説明 |
|---|---|
| `agent` | 実行するエージェントインスタンス |
| `input` | ユーザーからの入力（プロンプト） |

#### 戻り値

| プロパティ | 説明 |
|---|---|
| `result.final_output` | エージェントが生成した最終的なテキストレスポンス |

---

## function_tool ユーザーガイド

### 基本的な使い方

```python
@function_tool
def search_faq(keyword: str) -> str:
    keyword = keyword.lower()
    matches = [
        f"- {k}: {v}"
        for k, v in FAQS.items()
        if keyword in k or keyword in v.lower()
    ]
    if not matches:
        return "該当 FAQ は見つかりませんでした。"
    return "\n".join(matches)
```

#### 重要なポイント

| ポイント | 説明 |
|---|---|
| **@function_tool デコレーター** | Python 関数をエージェントのツールとして公開 |
| **型ヒント必須** | 引数と戻り値の型を指定（`keyword: str` -> `str`） |
| **Docstring** | ツールの説明（エージェントがいつツールを使うか判断する） |
| **自律的な呼び出し** | エージェントが必要に応じて自動でこの関数を呼び出す |

---

## FAQ 検索ツール付きサポートエージェント

### 完全なサンプルコード

```python
from __future__ import annotations
import asyncio, os
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool


ROOT_DIR = Path(__file__).resolve().parents[1]


FAQS = {
    "pricing": "料金は利用モデルとトークン量で変わります。最新の価格表を確認してください。",
    "responses": "Responses API は入力と出力の統一インターフェースです。",
    "handoff": "handoff は別エージェントへの役割委譲に使います。",
    "tool": "function_tool を使うと Python 関数をエージェントのツールとして公開できます。",
}


@function_tool
def search_faq(keyword: str) -> str:
    keyword = keyword.lower()
    matches = [
        f"- {k}: {v}"
        for k, v in FAQS.items()
        if keyword in k or keyword in v.lower()
    ]
    if not matches:
        return "該当 FAQ は見つかりませんでした。"
    return "\n".join(matches)


async def main() -> None:
    load_dotenv(ROOT_DIR / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")


    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    agent = Agent(
        name="Support Agent",
        instructions=(
            "ユーザー質問に答える前に、必要なら search_faq を使って関連情報を調べてください。"
            "回答は日本語で簡潔にまとめてください。"
        ),
        tools=[search_faq],
        model=model,
    )


    result = await Runner.run(
        agent,
        "handoff と tool の違いを説明してください。",
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## RAG 風小規模 FAQ の実装

### RAG とは

**RAG（Retrieval-Augmented Generation）** は、LLM が外部の知識ベースを検索して回答を生成するアーキテクチャです。

### 今回の実装の特徴

| 従来の RAG | 今回の実装 |
|---|---|
| 大規模な知識ベース（ベクトル DB） | 小規模な辞書（FAQ） |
| 埋め込み＋類似検索（Cosine Similarity） | キーワード部分一致 |
| Chroma, Pinecone, FAISS 使用 | 純粋な Python 辞書 |
| 本番環境向け | プロトタイプ・チュートリアル向け |

---

## 重要ポイントとベストプラクティス

### 1. instructions の重要性

```python
instructions=(
    "ユーザー質問に答える前に、必要なら search_faq を使って関連情報を調べてください。"
    "回答は日本語で簡潔にまとめてください。"
)
```

| 要素 | 目的 |
|---|---|
| `search_faq を使って` | ツールを使うように明示的に指示 |
| `必要なら` | 条件付きでツール使用を許可 |
| `日本語で簡潔に` | 出力形式の指定 |

### 2. tools の渡し方

```python
tools=[search_faq]  # リスト形式
```

- **複数のツールを渡す場合**：`tools=[tool1, tool2, tool3]`
- **ツールなしの場合**：`tools=[]`

### 3. 非同期処理

```python
async def main() -> None:
    result = await Runner.run(agent, input_text)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

- `Runner.run()` は非同期関数なので `await` 必須
- `asyncio.run()` でイベントループを起動

---

## 参考リンク

- [OpenAI Agent SDK 公式ドキュメント](https://platform.openai.com/docs/agents)
- [GitHub リポジトリ](https://github.com/openai/openai-agents-python)

---

# AIコーディングエージェント用バックエンドテンプレート

AIコーディングエージェント専用に設計されたPython REST APIテンプレート。信頼性が高く保守可能なバックエンド開発を保証するための包括的なガードレールと品質管理機能を備えています。

## 概要

このテンプレートは、FastAPIを使用したPython REST APIの堅牢な基盤を提供し、厳格な品質ゲートと自動テストを実装してAIエージェントをバックエンド開発のベストプラクティスに導きます。

## 主要機能

- **スキーマファースト開発**: OpenAPI仕様がすべてのAPI開発を主導
- **テスト駆動開発**: 包括的なテストカバレッジを持つ厳格なTDDワークフロー
- **自動品質ゲート**: pre-commitフックがコード品質基準を強制
- **契約テスト**: スキーマ駆動テストによるAPI準拠の保証
- **複雑度管理**: Lizardによる自動複雑度解析
- **型安全性**: 厳格な設定によるMyPy型チェック
- **シークレット検出**: detect-secretsによる機微情報の自動検出

## クイックスタート

### 前提条件

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー

### セットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd backend-template

# 依存関係をインストール
uv sync --dev

# pre-commitフックをインストール
uv run pre-commit install

# 開発サーバーを起動
uv run python main.py
```

APIは`http://localhost:8000`で利用可能になり、インタラクティブドキュメントは`http://localhost:8000/docs`で確認できます。

## 開発ワークフロー

### 1. スキーマファースト設計

常にOpenAPI仕様から開始:

```bash
# APIエンドポイントとモデルを定義
vim openapi.yaml
```

### 2. テスト駆動開発

Red-Green-Refactorサイクルに従う:

```bash
# Red: 失敗するテストを記述
vim tests/test_api.py
uv run pytest  # 失敗する

# Green: 最小限のコードを実装
vim src/api/main.py
uv run pytest  # 成功する

# Refactor: コード品質を改善
uv run ruff check --fix .
uv run mypy src/
```

### 3. 品質保証

コミット前にすべての品質ゲートを検証:

```bash
# すべての品質チェックを実行
uv run ruff check . && uv run mypy src/ && uv run pytest && uv run lizard src/ && uv run python schema_test.py && uv run detect-secrets scan --baseline .secrets.baseline .
```

## 品質ゲート

このテンプレートは自動チェックにより厳格な品質基準を強制します:

### コード品質
- **Ruff**: 包括的なルールセットを持つモダンなPythonリンター
- **MyPy**: 完全な型注釈を要求する厳格な型チェック
- **Lizard**: 設定可能な閾値による複雑度解析
- **detect-secrets**: APIキー、トークン等の機微情報検出

### テスト
- **単体テスト**: pytestによる包括的なテストカバレッジ
- **契約テスト**: schemathesisによるスキーマ駆動テスト
- **統合テスト**: 完全なAPIワークフロー検証

### 複雑度閾値
- **循環的複雑度**: ≤ 8
- **関数長**: ≤ 50行
- **引数数**: ≤ 5個

## AIエージェント向けガードレール

このテンプレートにはAIコーディングエージェント専用のガードレールが含まれています:

### 必須プラクティス
- スキーマファースト開発（OpenAPI更新なしのAPI変更禁止）
- テスト駆動開発（失敗するテストなしの本番コード禁止）
- 品質ゲートの遵守（すべてのチェックがコミット前に合格必須）

### 禁止行為
- すべての品質チェックに合格せずにコミット
- pre-commitフックのバイパス
- 既存ツールのカスタム実装作成
- 曖昧な要件に対する推測

### 意思決定フレームワーク
曖昧な要件に遭遇した場合、AIエージェントは以下を実行する必要があります:
1. 実装を即座に停止
2. コードベース内の既存パターンを調査
3. トレードオフを含む構造化されたオプションを提示
4. 明確な指導を要求
5. 選択されたアプローチを文書化

## プロジェクト構造

```
backend-template/
├── src/api/              # API実装
│   ├── main.py          # FastAPIアプリケーション
│   ├── models.py        # Pydanticモデル
│   └── database.py      # データ層
├── tests/               # テストスイート
│   └── test_api.py      # APIテスト
├── openapi.yaml         # OpenAPI仕様
├── schema_test.py       # 契約テスト
├── pyproject.toml       # プロジェクト設定
├── .pre-commit-config.yaml  # 品質ゲート
└── CLAUDE.md           # AIエージェント向け指示
```

## 利用可能なコマンド

### 開発
```bash
uv run python main.py                    # 開発サーバー起動
uv run uvicorn src.api.main:app --reload # ホットリロード付き代替
```

### テスト
```bash
uv run pytest                           # 全テスト実行
uv run pytest tests/test_api.py -v      # 特定テストファイル実行
uv run pytest -k "test_create_task"     # 特定テスト実行
uv run python schema_test.py            # 契約テスト
```

### 品質チェック
```bash
uv run ruff check .                     # コードリント
uv run ruff check --fix .               # 自動修正
uv run mypy src/                        # 型チェック
uv run lizard src/                      # 複雑度解析
uv run detect-secrets scan --baseline .secrets.baseline .  # シークレット検出
```

### Pre-commit
```bash
uv run pre-commit run --all-files       # 全フック実行
git commit -m "message"                 # フックが自動実行
```

## 設定

### コード品質設定
- **Ruff**: `pyproject.toml`でモダンなPythonルールを設定
- **MyPy**: 包括的な警告を持つ厳格な型チェック
- **Lizard**: `pyproject.toml`で定義された複雑度閾値
- **detect-secrets**: `.secrets.baseline`でベースライン管理

### テスト設定
- **Pytest**: 標準的なテスト検出と実行
- **Schemathesis**: スキーマ駆動契約テスト

## 貢献

このテンプレートは厳格な開発プラクティスに従います:

1. **品質ゲートをバイパスしない** - すべてのチェックが合格必須
2. **TDDを厳格に守る** - Red-Green-Refactorサイクル
3. **スキーマファースト開発** - OpenAPI仕様が真実の源
4. **明確化を求める** - 曖昧な要件について推測しない

## ライセンス

このテンプレートは教育および開発目的で設計されており、信頼性の高いAI支援バックエンド開発の基盤を提供します。

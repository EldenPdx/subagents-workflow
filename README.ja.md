[English](README.md) | [简体中文](README.zh-CN.md) | **日本語**

# Subagents Workflow

`subagents-workflow` は、コーディング、調査、レビュー、検証を、制御可能なネイティブ Subagent ワークフローとして整理するための、独立配布可能な **Agent Skill** です。

このリポジトリは、2 つの標準配布方式を提供します。

1. 互換 Agent ホスト向けの標準 **Agent Skills** ディレクトリ
2. リポジトリ URL から検出・インストール・更新できる **Codex skill-only plugin marketplace**

受け入れ基準は明確です。ユーザーが Agent にこのリポジトリ URL を渡すだけで、Agent が **検出 → インストール → 検証 → 呼び出し** を完了し、ユーザーに手動コピーや複雑な設定を求めないことです。

## Agent にそのまま渡すプロンプト

リポジトリ URL と一緒に、次のプロンプトを Agent に渡してください。

```text
次のリポジトリから subagents-workflow Skill をインストールして使用してください：
https://github.com/EldenPdx/subagents-workflow

Codex の場合は、リポジトリ内の plugin marketplace を優先してください。
それ以外の場合は、標準 Agent Skill
plugins/subagents-workflow/skills/subagents-workflow をインストールしてください。
インストール後に Skill のメタデータとファイル整合性を検証し、以後の
マルチエージェント要求でこの Skill を使用してください。
```

互換 Agent は、次の機械可読エントリポイントを検出できます。

- `SKILL.md`：正規 Skill を指すリポジトリルートの検出用 shim
- `.agents/plugins/marketplace.json`：Codex marketplace エントリポイント
- `plugins/subagents-workflow/.codex-plugin/plugin.json`：skill-only plugin manifest
- `plugins/subagents-workflow/skills/subagents-workflow/SKILL.md`：標準仕様に準拠した正規 Skill

## Skill の機能

この Skill は Agent に以下を行わせます。

- タスクが Subagent の利用に本当に適しているか判断する
- `direct`、`single_worker`、`parallel`、`phased` からトポロジーを選ぶ
- 親 Agent をクリティカルパス上に維持する
- 各 Agent に境界の明確なタスク契約を与える
- 並列書き込み範囲の重複を防止する
- イベント駆動で待機、修正、復旧、置換を行う
- 統合前に実際の変更内容と一次証拠を確認する
- 最終的な統合検証を実行する
- ネイティブ Subagent ツールがない場合に安全に直接実行へフォールバックする

この Skill はバックグラウンド Worker、モデルサービス、外部 Orchestrator を提供しません。また、ホスト Agent の承認、サンドボックス、権限、同時実行制御を回避する許可を与えません。

## インストール

### Codex：Plugin Marketplace（推奨）

リポジトリ marketplace と plugin をインストールします。

```bash
codex plugin marketplace add EldenPdx/subagents-workflow
codex plugin add subagents-workflow@eldenpdx
```

インストール後、新しい Codex 会話を開始して Skill を読み込ませてください。その後、明示的に呼び出せます。

```text
Use $subagents-workflow to split this task across bounded native subagents and validate the integrated result.
```

### Codex：Skill の直接インストール

`$skill-installer` を利用できる Codex 環境では、正規 Skill ディレクトリを直接インストールできます。

```text
$skill-installer install https://github.com/EldenPdx/subagents-workflow/tree/main/plugins/subagents-workflow/skills/subagents-workflow
```

この方法は、plugin marketplace を使用しない旧環境や制限された環境に適しています。

### その他の Agent Skills 互換ホスト

ホストのネイティブ Skill インストーラーに、次のディレクトリをインストールさせてください。

```text
plugins/subagents-workflow/skills/subagents-workflow
```

GitHub ディレクトリ URL を受け付ける場合は、次を使用します。

```text
https://github.com/EldenPdx/subagents-workflow/tree/main/plugins/subagents-workflow/skills/subagents-workflow
```

Skill の検索パスや再読み込み方法は Agent 製品ごとに異なります。ユーザーにローカル配置先を推測させるのではなく、ホストのネイティブインストーラーを優先してください。

## インストール検証

インストールを実行する Agent は、次を確認する必要があります。

1. Skill ディレクトリ名が `subagents-workflow` である
2. `SKILL.md` の `name` がディレクトリ名と一致する
3. description が Subagents、Multi-Agent、parallel agents、delegation の要求をカバーする
4. `agents/openai.yaml` の default prompt に `$subagents-workflow` が含まれる
5. 参照されるすべての `references/*.md` が存在する
6. Skill と plugin のバージョンが一致する

リポジトリのメンテナーは次を実行できます。

```bash
make validate
make test
```

## 呼び出し方法

### 自動検出

ユーザーが次を明示的に要求した場合、モデルによる自動呼び出しをサポートします。

- Subagents または Multi-Agent
- 並列 Agent
- Agent への委任
- 複数 Agent によるコーディング、調査、レビュー、検証

単に「徹底的に」「深く」「慎重に」と要求されただけでは、マルチエージェント実行を自動選択しません。独立性のない並列化による調整コストを避けるためです。

### 明示的な呼び出し

```text
Use $subagents-workflow to implement this feature with at most three agents.
```

```text
$subagents-workflow を使い、2 つの読み取り専用調査を委任し、親 Agent が証拠を統合してください。
```

コピー可能な例は [`examples/invocation-prompts.md`](examples/invocation-prompts.md) にあります。

## 入力とパラメーター

Skill は自然言語のタスクを受け取り、固定 JSON や CLI インターフェースを要求しません。次の項目が呼び出し契約を構成します。

| パラメーター | 値または形式 | デフォルト動作 |
|---|---|---|
| `topology` | `auto`、`direct`、`single_worker`、`parallel`、`phased` | 最小の実行可能トポロジーを自動選択 |
| `max_agents` | 正の整数 | 独立ワークストリーム数とホスト上限を超えない |
| `agent_count` | 正の整数 | 指定数を目標とし、「最大 N」を上限として扱う |
| `write_scope` | ファイルまたはディレクトリ集合 | 親 Agent が相互排他的な所有範囲を割り当てる |
| `validation` | テスト、型検査、ビルド、整形、独自チェック | リポジトリ規則とタスクのリスクから決定 |
| `external_orchestrator` | `explicit-only` | 明示要求なしでは使用しない |

これらは Agent の意思決定入力であり、ユーザーが個別設定するインストールオプションではありません。

## 出力契約

ユーザー向け完了報告には次を含めます。

```text
Topology: モード、実際の Agent 数、役割
Parent Agent: クリティカルパスと共有基盤の作業
Subagents: 各 Agent の主要結果と変更範囲
Validation: 実行コマンドと結果
Residual risks: 未対応項目、制約、またはなし
```

実装 Agent はさらに、状態、目標、変更ファイル、局所検証、リスク、推奨統合作業を親 Agent に報告します。

## ワークフロー

1. 親 Agent がタスク、コード、リポジトリ規則を理解する
2. クリティカルパス、sidecar、共有基盤、依存関係を特定する
3. 最小の実行可能トポロジーを選ぶ
4. 各 Agent に自己完結した目標と重複しない所有範囲を割り当てる
5. 独立 sidecar を開始しながら、親 Agent はクリティカルパスを進める
6. 実際の依存関係または Agent イベントが発生したときだけ調整する
7. 実際の diff、成果物、一次証拠をレビューする
8. 統合検証を実行する
9. Agent を閉じ、検証済みの結果をまとめる

詳細な契約、ランタイムアダプター、復旧手順は、正規 Skill の `references/` にあり、`SKILL.md` から段階的に読み込まれます。

## リポジトリ構成

```text
.
├── README.md
├── README.zh-CN.md
├── README.ja.md
├── SKILL.md
├── agents/openai.yaml
├── .agents/plugins/marketplace.json
├── .github/workflows/validate.yml
├── plugins/
│   └── subagents-workflow/
│       ├── .codex-plugin/plugin.json
│       ├── LICENSE
│       ├── README.md
│       └── skills/
│           └── subagents-workflow/
│               ├── SKILL.md
│               ├── agents/openai.yaml
│               ├── evals/
│               │   ├── README.md
│               │   └── evals.json
│               └── references/
│                   ├── contracts.md
│                   ├── recovery-and-validation.md
│                   └── runtime-adapters.md
├── examples/invocation-prompts.md
├── scripts/
│   ├── package.py
│   └── validate.py
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
└── SECURITY.md
```

## 依存関係と実行環境

### Skill ランタイム

サードパーティのランタイム依存はありません。必要なのは次の要素です。

- Markdown ベースの Skill を読み込める Agent
- 並列モードで Subagent の作成、通信、待機、終了を行うネイティブ機能
- 上記機能がない場合は `direct` フォールバックのみ

Codex で最適化される対応関係は次のとおりです。

- `spawn_agent`
- `send_input`
- `wait_agent`
- `close_agent`
- `resume_agent`

### リポジトリ開発

- Python 3.10+
- GNU Make（任意。各ターゲットには直接 Python コマンドがあります）
- Git

検証とパッケージングは Python 標準ライブラリだけを使用し、`pip install` は不要です。

## 互換性

| 環境 | サポートレベル | 説明 |
|---|---|---|
| Codex plugin marketplace | 完全 | plugin UI メタデータを含む推奨配布方式 |
| Codex ネイティブ Skills | 完全 | 正規 Skill ディレクトリを直接インストール可能 |
| Agent Skills 互換ホスト | コア | 標準 `SKILL.md`、references、evals を使用 |
| Subagent ツールのないホスト | 安全なフォールバック | `direct` を使用し、疑似並列化を行わない |
| 外部 Orchestrator | 条件付き | 明示要求と完全な権限がある場合のみ |

`agents/openai.yaml` は Codex 固有の UI メタデータです。他のホストは標準 Skill に影響を与えず無視できます。

## バージョン管理

プロジェクトは [Semantic Versioning](https://semver.org/) に従います。

- **MAJOR**：呼び出し契約または編成セマンティクスに非互換変更がある
- **MINOR**：後方互換なトポロジー、アダプター、ガイダンスを追加する
- **PATCH**：文書、トリガー説明、エラー処理、検証を修正する

リリース時は、次のバージョンを同時に更新します。

1. `.codex-plugin/plugin.json`
2. 正規およびルート `SKILL.md` の `metadata.version`
3. `CHANGELOG.md`

`scripts/validate.py` がバージョン整合性を検証します。

## エラー処理

| 状況 | 動作 |
|---|---|
| 独立した作業境界がない | `direct` を使用する |
| ネイティブ Subagent ツールがない | `direct` に安全にフォールバックし制約を明示する |
| Agent がブロックまたは入力を要求 | 必要最小限の質問を明確化またはユーザーへエスカレーションする |
| Agent が範囲外へ書き込む | 追加書き込みを止め、diff を確認し、所有範囲を再割り当てする |
| 並列競合 | 親 Agent または単一の指定所有者が共有ファイルを解決する |
| 局所検証が失敗 | 根本原因に最も近い所有者へ証拠を送り、狭い範囲で修正する |
| Agent が復旧不能 | 重複 Agent を増やさず、閉じてより狭いタスクに置き換える |
| 外部操作に承認が必要 | ホストの承認フローを維持し、回避しない |

## 制限事項

- 並列実行が常に高速とは限りません。Skill は有用な最小並列度を優先します。
- Subagent の分離、同時実行、権限、コンテキスト動作はホストごとに異なります。
- Skill はリポジトリのテスト、コードレビュー、セキュリティポリシーを代替しません。
- 調査結果は親 Agent が一次証拠と照合する必要があります。
- 外部 Orchestrator、リモートモデル、本番システム、有料サービスはデフォルト依存ではありません。
- Skill 対応を表明するすべてのホストが GitHub からの自動インストールに対応するとは限りません。標準パスと機械可読エントリポイントは提供しますが、最終的なインストール能力はホスト側に依存します。

## 開発

```bash
git clone https://github.com/EldenPdx/subagents-workflow.git
cd subagents-workflow
make validate
make test
```

直接コマンド：

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

## パッケージング

```bash
make package
```

次のファイルを生成します。

- `dist/subagents-workflow-plugin-<version>.zip`
- `dist/subagents-workflow-skill-<version>.zip`

plugin アーカイブは skill-only plugin 配布用、Skill アーカイブは標準 Agent Skill ディレクトリをインストールするホスト用です。

## 評価

動作評価ケースは次にあります。

```text
plugins/subagents-workflow/skills/subagents-workflow/evals/evals.json
```

評価内容：

- 小さなタスクで不要な Agent を作らない
- 本当に独立した作業を並列化する
- 共有 schema を中心に phased 実行する
- 読み取り専用調査と証拠統合を行う
- ネイティブ Subagent ツールがない場合に安全にフォールバックする

各ケースを、Skill あり・なしのクリーンなコンテキストで実行し、固定文言ではなく観測可能な動作を比較してください。

## コントリビューションとセキュリティ

- コントリビューション手順は [`CONTRIBUTING.md`](CONTRIBUTING.md) を参照してください。
- 脆弱性報告は [`SECURITY.md`](SECURITY.md) を参照してください。
- リリース履歴は [`CHANGELOG.md`](CHANGELOG.md) を参照してください。
- このプロジェクトは MIT License で提供されます。

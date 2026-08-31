[English](README.md) | **简体中文** | [日本語](README.ja.md)

# Subagents Workflow

`subagents-workflow` 是一个可独立分发的 **Agent Skill**，用于把编码、调查、评审和验证任务组织成可控的原生 Subagent 工作流。

仓库同时提供两种标准分发面：

1. **Agent Skills 标准目录**：跨兼容 Agent 使用；
2. **Codex skill-only plugin marketplace**：Codex 通过仓库链接发现、安装和更新。

核心目标：用户只需把本仓库链接交给 Agent，Agent 即可完成 **发现 → 安装 → 验证 → 调用**，无需用户手工复制文件或编写配置。

## 给 Agent 的一条指令

把下面内容连同仓库链接发给 Agent：

```text
请安装并使用这个仓库中的 subagents-workflow Skill：
https://github.com/EldenPdx/subagents-workflow

如果你是 Codex，优先使用仓库内的 plugin marketplace 安装；否则按
Agent Skills 标准安装 plugins/subagents-workflow/skills/subagents-workflow。
安装后验证 Skill 元数据和文件完整性，并在后续多智能体任务中调用它。
```

兼容 Agent 应当自动识别：

- `SKILL.md`：仓库根目录发现入口，指向规范 Skill 包；
- `.agents/plugins/marketplace.json`：Codex marketplace 入口；
- `plugins/subagents-workflow/.codex-plugin/plugin.json`：skill-only plugin manifest；
- `plugins/subagents-workflow/skills/subagents-workflow/SKILL.md`：标准 Skill 入口。

## 能力范围

该 Skill 负责：

- 判断任务是否值得使用 Subagents；
- 选择 `direct`、`single_worker`、`parallel` 或 `phased` 拓扑；
- 让父 Agent 保持在关键路径；
- 为每个 Agent 建立边界化任务契约；
- 保证并行写入范围互斥；
- 使用事件驱动的等待、纠偏、恢复和替换；
- 审查真实改动与证据，并运行最终集成验证；
- 在无原生 Subagent 工具时安全降级为直接执行。

它不提供后台 Worker、模型服务或外部 Orchestrator，也不会绕过宿主 Agent 的审批、沙箱、权限或并发限制。

## 安装

### Codex：Plugin Marketplace（推荐）

Codex 可从本仓库 marketplace 安装：

```bash
codex plugin marketplace add EldenPdx/subagents-workflow
codex plugin add subagents-workflow@eldenpdx
```

安装后开启一个新的 Codex 对话，使新 Skill 被加载。之后可显式调用：

```text
Use $subagents-workflow to split this task across bounded native subagents and validate the integrated result.
```

### Codex：直接 Skill 安装兼容路径

支持 `$skill-installer` 的环境可直接安装 Skill 子目录：

```text
$skill-installer install https://github.com/EldenPdx/subagents-workflow/tree/main/plugins/subagents-workflow/skills/subagents-workflow
```

该方式适合尚未启用 plugin marketplace 的旧版或受限环境。

### 其他 Agent Skills 兼容宿主

让宿主的 Skill 安装器安装以下目录：

```text
plugins/subagents-workflow/skills/subagents-workflow
```

如果宿主接受 GitHub 目录 URL，可直接使用：

```text
https://github.com/EldenPdx/subagents-workflow/tree/main/plugins/subagents-workflow/skills/subagents-workflow
```

不同 Agent 产品的 Skill 搜索目录和刷新方式并不统一；优先让 Agent 自己调用其原生安装器，不要让用户猜测本地目录。

## 安装验证

安装 Agent 应确认：

1. Skill 文件夹名为 `subagents-workflow`；
2. `SKILL.md` YAML frontmatter 中的 `name` 与文件夹一致；
3. `description` 可触发 Subagents、Multi-Agent、parallel agents 和 delegation 请求；
4. `agents/openai.yaml` 中的默认提示显式包含 `$subagents-workflow`；
5. 引用的 `references/*.md` 文件均存在；
6. 版本与 plugin manifest 一致。

仓库维护者可运行：

```bash
make validate
make test
```

## 调用方式

### 自动发现

当用户明确要求以下意图时，支持模型自动调用：

- Subagents / Multi-Agent；
- 并行智能体；
- 代理委派；
- 多 Agent 编码、调查、评审或验证。

仅仅要求“深入”“全面”或“仔细”不会自动触发多智能体，避免无意义的并行。

### 显式调用

```text
Use $subagents-workflow to implement this feature with at most three agents.
```

```text
请使用 $subagents-workflow，把调查拆给两个只读 Agent，父 Agent 负责证据整合。
```

更多可复制示例见 [`examples/invocation-prompts.md`](examples/invocation-prompts.md)。

## 输入与参数

Skill 接收自然语言任务，不要求固定 JSON 或 CLI 参数。以下字段构成约定的调用契约：

| 参数 | 可选值/格式 | 默认行为 |
|---|---|---|
| `topology` | `auto`、`direct`、`single_worker`、`parallel`、`phased` | 自动选择最小可行拓扑 |
| `max_agents` | 正整数 | 不超过独立工作流数量和宿主并发上限 |
| `agent_count` | 正整数 | 明确要求时作为目标；“最多 N 个”作为上限 |
| `write_scope` | 文件或目录集合 | 父 Agent 分配互斥范围 |
| `validation` | 测试、类型检查、构建、格式或自定义检查 | 从仓库规范和任务风险推导 |
| `external_orchestrator` | `explicit-only` | 未经明确要求不使用 |

参数是 Agent 的决策输入，不是必须由用户逐项配置的安装选项。

## 输出

Skill 的用户可见输出应包含：

```text
拓扑：使用的模式、实际 Agent 数量和角色
父 Agent：关键路径与共享基础
Subagents：各 Agent 的主要结果和改动范围
验证：运行的命令与结果
残余风险：未覆盖项、限制或无
```

实现 Agent 还会向父 Agent 返回：状态、目标、改动文件、局部验证、风险和建议集成动作。

## 运行逻辑

1. 父 Agent 理解任务、代码和规则；
2. 标出关键路径、sidecars、共享基础和依赖；
3. 选择最小拓扑；
4. 为每个 Agent 分配自包含目标和互斥所有权；
5. 启动可并行 sidecars，同时继续本地关键路径；
6. 在真实依赖或 Agent 事件发生时协调；
7. 审查实际 diff、产物或原始证据；
8. 运行集成验证；
9. 关闭 Agent 并汇总结果。

详细契约、运行时适配和恢复策略位于 Skill 的 `references/` 目录，并由 `SKILL.md` 按需加载。

## 目录结构

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
└── README.md
```

## 依赖与运行环境

### Skill 运行时

无第三方运行时依赖。需要：

- 能读取 Markdown Skill 的 Agent；
- 并行模式需要宿主提供创建、通信、等待和关闭 Subagent 的原生能力；
- 没有这些能力时自动降级为 `direct`。

Codex 优化映射：

- `spawn_agent`
- `send_input`
- `wait_agent`
- `close_agent`
- `resume_agent`

### 仓库开发与验证

- Python 3.10+
- GNU Make（可选；所有命令都可直接运行 Python）
- Git

验证与打包脚本仅使用 Python 标准库，不需要 `pip install`。

## 兼容性

| 环境 | 支持级别 | 说明 |
|---|---|---|
| Codex plugin marketplace | 完整 | 推荐分发路径，包含 plugin UI 元数据 |
| Codex 原生 Skills | 完整 | 可通过 Skill 子目录直接安装 |
| Agent Skills 标准兼容宿主 | 核心兼容 | 可识别 `SKILL.md`、references 和 evals |
| 无 Subagent 能力的宿主 | 安全降级 | 使用 `direct`，不伪造并行 |
| 外部 Orchestrator | 条件支持 | 仅用户明确要求且工具可用、权限完整时 |

`agents/openai.yaml` 是 Codex 专用 UI 元数据；其他宿主可忽略，不影响标准 `SKILL.md`。

## 版本管理

项目遵循 [Semantic Versioning](https://semver.org/)：

- **MAJOR**：调用契约或核心编排语义不兼容；
- **MINOR**：新增向后兼容的拓扑、适配或指导；
- **PATCH**：文档、触发描述、错误处理和验证修复。

发布时必须同步更新：

1. `.codex-plugin/plugin.json` 的 `version`；
2. `SKILL.md` 的 `metadata.version`；
3. `CHANGELOG.md`。

`scripts/validate.py` 会检查版本一致性。

## 错误处理

| 场景 | 行为 |
|---|---|
| 无独立工作边界 | 使用 `direct` |
| 原生 Subagent 工具不可用 | 安全降级为 `direct` 并说明限制 |
| Agent 阻塞或请求输入 | 澄清；必要时升级给用户 |
| Agent 越界 | 停止后续写入，审查 diff，重新分配所有权 |
| 并行冲突 | 由父 Agent 或唯一所有者解决共享文件 |
| 局部验证失败 | 把失败证据发给最接近根因的所有者并聚焦修复 |
| Agent 无法恢复 | 关闭后替换为更窄任务，不重复批量创建 |
| 外部操作需要审批 | 保留宿主审批，不自行绕过 |

## 使用限制

- 该 Skill 不保证并行一定比直接执行更快；它会优先选择最小可行并行度。
- 不同宿主的 Subagent 隔离、并发、权限和上下文模型不同。
- Skill 无法替代仓库自己的测试、代码审查或安全策略。
- 调查 Agent 的结论必须由父 Agent 检查证据。
- 外部 Orchestrator、远程模型、生产系统或收费服务不属于默认依赖。
- 不能保证所有声称支持 Skills 的 Agent 都支持自动 GitHub 安装；仓库提供标准路径和可机器识别入口，但最终安装能力由宿主决定。

## 开发

```bash
git clone https://github.com/EldenPdx/subagents-workflow.git
cd subagents-workflow
make validate
make test
```

直接命令：

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

## 打包

```bash
make package
```

生成：

- `dist/subagents-workflow-plugin-<version>.zip`
- `dist/subagents-workflow-skill-<version>.zip`

Plugin ZIP 可用于 skill-only plugin 发布；Skill ZIP 可用于支持 Agent Skills 目录安装的宿主。

## 评测

行为评测用例位于：

```text
plugins/subagents-workflow/skills/subagents-workflow/evals/evals.json
```

评测覆盖：

- 小任务不滥用 Agent；
- 真正独立任务并行；
- 共享 schema 的分阶段拓扑；
- 只读调查与证据整合；
- 无原生工具时的安全降级。

建议在干净上下文中分别运行“启用 Skill”和“不启用 Skill”两组，比较可观察行为，而不是匹配固定措辞。

## 贡献与安全

- 贡献流程见 [`CONTRIBUTING.md`](CONTRIBUTING.md)；
- 安全问题见 [`SECURITY.md`](SECURITY.md)；
- 版本变化见 [`CHANGELOG.md`](CHANGELOG.md)；
- 项目使用 MIT License。

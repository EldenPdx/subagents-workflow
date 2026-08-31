---
name: subagents-workflow
description: "编排原生 Subagents / Multi-Agent 完成编码、调查、评审或验证。Use when the user explicitly requests subagents, parallel agents, agent delegation, multi-agent work, or $subagents-workflow. Keep the parent Agent on the critical path, assign bounded non-overlapping work, and validate the integrated result; use direct execution when delegation would not help."
license: MIT
metadata:
  author: "EldenPdx"
  version: "1.0.0"
  repository: "https://github.com/EldenPdx/subagents-workflow"
  compatibility: "Requires native subagent or delegation primitives for parallel modes; optimized for Codex spawn_agent, send_input, wait_agent, close_agent, and resume_agent. Degrades to direct execution when equivalent tools are unavailable."
---

# Subagents Workflow

用宿主 Agent 的原生委派能力组织多智能体工作。目标不是最大化 Agent 数量，而是让关键路径持续推进、所有权互斥、上下文最小化，并由父 Agent 对最终集成结果负责。

## 触发与边界

仅在以下情况启用：

- 用户明确要求 Subagents、Multi-Agent、并行智能体或代理委派；
- 用户显式调用 `$subagents-workflow`；
- 用户要求把实现、调查、评审或验证拆给多个 Agent。

普通的“深入分析”“全面检查”不自动等于多智能体请求。没有可独立边界时选择 `direct`，不要为了形式创建 Agent。

## 输入契约

把用户请求解释为以下可选参数；未提供时使用默认值：

| 参数 | 含义 | 默认值 |
|---|---|---|
| `topology` | `auto`、`direct`、`single_worker`、`parallel`、`phased` | `auto` |
| `max_agents` | 同时运行的 Subagent 上限 | 独立工作流数量与宿主并发上限中的较小值 |
| `agent_count` | 用户要求的 Agent 数量 | 作为目标；若用户说“最多”则作为上限 |
| `write_scope` | 每个写入 Agent 可修改的文件或目录 | 必须由父 Agent 明确分配且互不重叠 |
| `validation` | 每个 Agent 与最终集成需要运行的检查 | 从仓库规范与任务风险推导 |
| `external_orchestrator` | 是否允许外部编排器 | `explicit-only` |

当用户给出固定 Agent 数、拓扑、文件范围或验证要求时，先读 [任务契约参考](references/contracts.md)。

## 工作流

### 1. 理解任务并标出关键路径

父 Agent 先读取完成任务所需的代码、规则和相关 Skill，识别：

- 当前必须本地立即完成的阻塞工作；
- 可独立并行的 sidecars；
- 共享基础、唯一所有者与依赖门槛；
- 最终扇入和验证点。

下一步若必须依赖某项结果，该项通常留给父 Agent 本地完成，而不是委派后立即等待。

### 2. 选择最小拓扑

| 模式 | 使用条件 | 行为 |
|---|---|---|
| `direct` | 任务小、强耦合、没有独立边界或宿主无委派工具 | 父 Agent 直接完成 |
| `single_worker` | 一个自包含 sidecar 可与父 Agent 并行 | 启动一个 Subagent，父 Agent 继续关键路径 |
| `parallel` | 两个以上任务互不依赖，写入范围互斥 | 同一波次并行启动 |
| `phased` | 存在共享基础、schema、接口或阶段依赖 | 父 Agent 或唯一所有者先完成基础，再分波次启动 |

在首次委派前，用一句话记录拓扑、父 Agent 当前任务、各 Agent 边界和最终验证点。

### 3. 建立边界化任务契约

每个 Subagent 只接收一个自包含目标。契约必须包含：角色、目标、限定任务、范围外事项、读取入口、允许与禁止写入范围、依赖、已确认决策、预期产物、验证命令和完成汇报格式。

详细模板与示例见 [任务契约参考](references/contracts.md)。写入型 Agent 直接修改其隔离工作区，并报告改动文件；调查、评审和验证任务默认只读。

### 4. 委派并继续本地工作

- 优先委派不阻塞父 Agent 下一步的 sidecars。
- 并行写入范围必须互斥；共享配置、锁文件、schema 和生成物只能有一个所有者。
- 不重复实现已委派任务；父 Agent 转向关键路径、共享基础或不同的集成工作。
- 决策影响多个 Agent 时，由父 Agent 用消息工具显式广播；不要假设 Agent 共享彼此上下文。

若宿主工具名称或行为不同、原生能力缺失，先读 [运行时适配](references/runtime-adapters.md)。

### 5. 事件驱动协调

只在以下事件检查 Agent：

- Agent 完成、阻塞或请求输入；
- 父 Agent 即将进入依赖步骤；
- 发现范围冲突、接口变化或验证失败；
- 用户提供影响任务的新信息。

等待工具应少量、长等待、面向真实依赖使用。等待期间继续做不重叠工作；不要固定频率轮询或为了等待而停止关键路径。

### 6. 扇入、审查与验证

Subagent 返回后，父 Agent 必须审查真实改动或原始证据，而不是只接受摘要：

1. 确认改动未越过所有权边界；
2. 检查接口、行为、风格和用户要求；
3. 合并不重叠成果，父 Agent 解决共享语义冲突；
4. 运行覆盖集成面的测试、类型检查、构建或格式验证；
5. 聚焦修复失败范围并重跑受影响检查；
6. 关闭不再需要的 Agent，释放并发资源。

最终完成条件是集成后的真实工作区通过验证，不是所有 Subagents 都报告 `completed`。

## 失败与恢复

出现阻塞、超时、越界、冲突或部分失败时，按“澄清 → 纠偏 → 替换 → 升级”处理。先保留有效成果，再收窄剩余任务；不要为同一问题连续创建多个重复 Agent。

详细恢复策略和最终检查清单见 [恢复与验证](references/recovery-and-validation.md)。

## 输出契约

最终向用户汇总：

```text
拓扑：<模式；实际 Agent 数量与角色>
父 Agent：<关键路径与共享基础>
Subagents：<每个 Agent 的主要结果和改动范围>
验证：<命令与结果>
残余风险：<未覆盖项、限制或无>
```

不要转储完整 Agent 对话、长日志或未经核验的自我报告。

## 硬边界

- 父 Agent 保留架构判断、关键路径和最终责任。
- 不创建用户可见的新任务来模拟 Subagent；使用宿主的原生委派工具。
- 不通过 Shell 启动隐藏 Worker 来绕过宿主的审批、沙箱或并发控制。
- 不并行修改同一文件、锁文件、schema、共享配置或生成物。
- 外部 Orchestrator 仅在用户明确要求且运行时可用时使用；切换前说明代价和权限边界。
- 涉及凭据、生产系统、破坏性操作或额外费用时，保留宿主要求的用户审批。

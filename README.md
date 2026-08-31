**English** | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

# Subagents Workflow

`subagents-workflow` is a distributable **Agent Skill** for organizing coding, investigation, review, and verification work into controlled native-subagent workflows.

The repository exposes the skill through two standard distribution surfaces:

1. a standard **Agent Skills** directory for compatible agent hosts;
2. a **Codex skill-only plugin marketplace** for repository-link discovery, installation, and updates.

The acceptance goal is simple: give an agent this repository URL and let it complete the full **discover → install → validate → invoke** flow without asking the user to copy files or author configuration manually.

## Give this directly to an agent

Send the following prompt with the repository URL:

```text
Install and use the subagents-workflow Skill from:
https://github.com/EldenPdx/subagents-workflow

If you are Codex, prefer the plugin marketplace included in the repository.
Otherwise install the standard Agent Skill at
plugins/subagents-workflow/skills/subagents-workflow. Validate the Skill metadata
and file integrity after installation, then use it for my multi-agent requests.
```

A compatible agent can discover these machine-readable entrypoints:

- `SKILL.md`: repository-root discovery shim pointing to the canonical Skill;
- `.agents/plugins/marketplace.json`: Codex marketplace entrypoint;
- `plugins/subagents-workflow/.codex-plugin/plugin.json`: skill-only plugin manifest;
- `plugins/subagents-workflow/skills/subagents-workflow/SKILL.md`: canonical standard Skill.

## What the Skill does

The Skill helps an agent:

- decide whether a task actually benefits from subagents;
- choose a `direct`, `single_worker`, `parallel`, or `phased` topology;
- keep the parent Agent on the critical path;
- define bounded task contracts for every delegated agent;
- prevent overlapping parallel write scopes;
- coordinate waiting, correction, recovery, and replacement through events;
- inspect real changes and evidence before integration;
- run final integrated validation;
- degrade safely to direct execution when native subagent tools are unavailable.

It does not ship a background worker, model service, or external orchestrator. It never authorizes bypassing the host Agent's approval, sandbox, permission, or concurrency controls.

## Installation

### Codex: plugin marketplace (recommended)

Install the repository marketplace and plugin:

```bash
codex plugin marketplace add EldenPdx/subagents-workflow
codex plugin add subagents-workflow@eldenpdx
```

Start a new Codex conversation after installation so the Skill is loaded. You can then invoke it explicitly:

```text
Use $subagents-workflow to split this task across bounded native subagents and validate the integrated result.
```

### Codex: direct Skill installation

Codex environments with `$skill-installer` can install the canonical Skill directory directly:

```text
$skill-installer install https://github.com/EldenPdx/subagents-workflow/tree/main/plugins/subagents-workflow/skills/subagents-workflow
```

This path is useful for older or restricted environments that do not use plugin marketplaces.

### Other Agent Skills-compatible hosts

Ask the host's native Skill installer to install:

```text
plugins/subagents-workflow/skills/subagents-workflow
```

If the host accepts GitHub directory URLs, use:

```text
https://github.com/EldenPdx/subagents-workflow/tree/main/plugins/subagents-workflow/skills/subagents-workflow
```

Skill search paths and refresh behavior differ across agent products. Prefer the host's native installer instead of asking users to guess a local installation directory.

## Installation validation

An installing agent should confirm that:

1. the Skill directory is named `subagents-workflow`;
2. the `name` in `SKILL.md` matches the directory name;
3. the description covers Subagents, Multi-Agent, parallel agents, and delegation requests;
4. `agents/openai.yaml` includes `$subagents-workflow` in its default prompt;
5. every referenced `references/*.md` file exists;
6. the Skill and plugin versions match.

Repository maintainers can run:

```bash
make validate
make test
```

## Invocation

### Automatic discovery

The Skill supports model invocation when the user explicitly requests:

- Subagents or Multi-Agent work;
- parallel agents;
- agent delegation;
- multi-agent coding, investigation, review, or verification.

Generic requests to be “thorough,” “deep,” or “careful” do not automatically require multi-agent execution. This avoids parallelism that adds coordination cost without useful independence.

### Explicit invocation

```text
Use $subagents-workflow to implement this feature with at most three agents.
```

```text
Use $subagents-workflow to assign two read-only investigation agents while the parent Agent integrates the evidence.
```

More copy-ready prompts are available in [`examples/invocation-prompts.md`](examples/invocation-prompts.md).

## Inputs and parameters

The Skill accepts natural-language tasks and does not require a fixed JSON or CLI interface. The following fields form its invocation contract:

| Parameter | Values or format | Default behavior |
|---|---|---|
| `topology` | `auto`, `direct`, `single_worker`, `parallel`, `phased` | Select the smallest viable topology automatically |
| `max_agents` | Positive integer | Do not exceed independent workstreams or the host concurrency limit |
| `agent_count` | Positive integer | Treat an exact request as a target and “at most N” as a ceiling |
| `write_scope` | Sets of files or directories | The parent assigns mutually exclusive ownership |
| `validation` | Tests, type checks, build, formatting, or custom checks | Infer from repository rules and task risk |
| `external_orchestrator` | `explicit-only` | Never use one without an explicit request |

These are decision inputs for the Agent, not installation options the user must configure individually.

## Output contract

The user-facing completion summary should include:

```text
Topology: mode, actual agent count, and roles
Parent Agent: critical-path and shared-foundation work
Subagents: major results and change scopes
Validation: commands and outcomes
Residual risks: uncovered items, limitations, or none
```

Implementation agents additionally report their status, goal, changed files, focused validation, risks, and recommended integration action to the parent Agent.

## Workflow

1. The parent Agent understands the task, code, and repository rules.
2. It identifies the critical path, sidecars, shared foundations, and dependencies.
3. It selects the smallest viable topology.
4. It assigns each agent a self-contained goal and non-overlapping ownership.
5. It launches independent sidecars while continuing local critical-path work.
6. It coordinates only when a real dependency or agent event occurs.
7. It reviews actual diffs, artifacts, or primary evidence.
8. It runs integrated validation.
9. It closes agents and summarizes the verified result.

Detailed contracts, runtime adapters, and recovery guidance live in the canonical Skill's `references/` directory and are loaded progressively from `SKILL.md`.

## Repository layout

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

## Dependencies and runtime

### Skill runtime

There are no third-party runtime dependencies. The Skill requires:

- an Agent that can load Markdown-based Skills;
- native primitives to create, message, wait for, and close subagents for parallel modes;
- no parallel capability for `direct` fallback mode.

The optimized Codex mapping is:

- `spawn_agent`
- `send_input`
- `wait_agent`
- `close_agent`
- `resume_agent`

### Repository development

- Python 3.10+
- GNU Make, optional because every target has a direct Python equivalent
- Git

Validation and packaging use only the Python standard library; no `pip install` step is required.

## Compatibility

| Environment | Support level | Notes |
|---|---|---|
| Codex plugin marketplace | Full | Recommended distribution path with plugin UI metadata |
| Native Codex Skills | Full | Install the canonical Skill directory directly |
| Agent Skills-compatible hosts | Core | Uses standard `SKILL.md`, references, and evals |
| Hosts without subagent tools | Safe fallback | Uses `direct` mode and does not fake parallelism |
| External orchestrators | Conditional | Only when explicitly requested and fully authorized |

`agents/openai.yaml` is Codex-specific UI metadata. Other hosts can ignore it without affecting the standard Skill.

## Versioning

The project follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: incompatible invocation-contract or orchestration-semantics changes;
- **MINOR**: backward-compatible topology, adapter, or guidance additions;
- **PATCH**: documentation, trigger description, error handling, and validation fixes.

A release must update the same version in:

1. `.codex-plugin/plugin.json`;
2. `metadata.version` in the canonical and root `SKILL.md` files;
3. `CHANGELOG.md`.

`scripts/validate.py` checks version consistency.

## Error handling

| Scenario | Behavior |
|---|---|
| No independent work boundary | Use `direct` mode |
| Native subagent tools unavailable | Fall back safely to `direct` and state the limitation |
| Agent blocked or requesting input | Clarify or escalate the smallest necessary question |
| Agent writes outside its scope | Stop further writes, inspect the diff, and reassign ownership |
| Parallel conflict | Resolve shared files through the parent or one designated owner |
| Focused validation fails | Send evidence to the owner closest to the root cause and repair narrowly |
| Agent cannot recover | Close and replace it with a narrower task instead of spawning duplicates |
| External action needs approval | Preserve the host approval flow and never bypass it |

## Limitations

- Parallel execution is not guaranteed to be faster; the Skill prefers the smallest useful degree of parallelism.
- Subagent isolation, concurrency, permission, and context behavior differ across hosts.
- The Skill does not replace repository tests, code review, or security policy.
- Investigation conclusions must be checked against primary evidence by the parent Agent.
- External orchestrators, remote models, production systems, and paid services are not default dependencies.
- Some hosts that claim Skill support may not support automatic GitHub installation. This repository provides standard paths and machine-readable entrypoints, but final installation capability belongs to the host.

## Development

```bash
git clone https://github.com/EldenPdx/subagents-workflow.git
cd subagents-workflow
make validate
make test
```

Direct commands:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

## Packaging

```bash
make package
```

This generates:

- `dist/subagents-workflow-plugin-<version>.zip`
- `dist/subagents-workflow-skill-<version>.zip`

The plugin archive is suitable for skill-only plugin distribution. The Skill archive is suitable for hosts that install standard Agent Skill directories.

## Evaluation

Behavioral evaluation cases are stored at:

```text
plugins/subagents-workflow/skills/subagents-workflow/evals/evals.json
```

They cover:

- avoiding unnecessary agents for tiny tasks;
- parallelizing genuinely independent work;
- phased execution around a shared schema;
- read-only investigations and evidence synthesis;
- safe fallback when native subagent tools are unavailable.

Run each case in a clean context both with and without the Skill. Compare observable behavior rather than exact wording.

## Contributing and security

- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the contribution workflow.
- See [`SECURITY.md`](SECURITY.md) for vulnerability reporting.
- See [`CHANGELOG.md`](CHANGELOG.md) for release history.
- The project is licensed under the MIT License.

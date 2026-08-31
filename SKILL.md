---
name: subagents-workflow
description: "编排原生 Subagents / Multi-Agent 完成编码、调查、评审或验证。Use when the user explicitly requests subagents, parallel agents, agent delegation, multi-agent work, or $subagents-workflow. Keep the parent Agent on the critical path, assign bounded non-overlapping work, and validate the integrated result; use direct execution when delegation would not help."
license: MIT
metadata:
  author: "EldenPdx"
  version: "1.0.0"
  repository: "https://github.com/EldenPdx/subagents-workflow"
  compatibility: "Repository-root discovery shim. The canonical Agent Skill is bundled inside the Codex skill-only plugin and requires native delegation primitives for parallel modes; it degrades to direct execution when they are unavailable."
  canonical-path: "plugins/subagents-workflow/skills/subagents-workflow/SKILL.md"
---

# Subagents Workflow distribution entrypoint

This root file is a compatibility entrypoint for Agents that discover a Skill
by scanning a repository root.

1. Read the [canonical Skill](plugins/subagents-workflow/skills/subagents-workflow/SKILL.md).
2. Treat that file, its `agents/`, `references/`, and `evals/` siblings as the
   authoritative Skill package.
3. Follow the canonical instructions for the current user request.

Prefer installing the repository's Codex marketplace or the canonical Skill
directory rather than copying this shim alone. If the canonical path is absent,
stop and report an incomplete installation instead of guessing the workflow.

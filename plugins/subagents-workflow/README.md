# Subagents Workflow plugin

This is the Codex skill-only plugin distribution for the repository's
`subagents-workflow` Agent Skill.

- Plugin manifest: `.codex-plugin/plugin.json`
- Bundled skill: `skills/subagents-workflow/`
- Runtime dependencies: none beyond the host Agent's native delegation tools
- Authentication: none

Install from the repository marketplace:

```bash
codex plugin marketplace add EldenPdx/subagents-workflow
codex plugin add subagents-workflow@eldenpdx
```

Start a new Codex conversation after installation so the new skill is loaded.
See the repository root `README.md` for standalone Agent Skills installation,
usage, compatibility, development, and release instructions.

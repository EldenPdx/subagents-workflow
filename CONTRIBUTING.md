# Contributing

Contributions should improve observable agent behavior, interoperability, or
packaging reliability without turning the skill into a generic orchestration
framework.

## Development workflow

1. Create a focused branch.
2. Update the canonical skill under
   `plugins/subagents-workflow/skills/subagents-workflow/`.
3. Add or revise an eval when behavior changes.
4. Run:

   ```bash
   make validate
   make test
   ```

5. Describe the user-visible behavior, validation, and compatibility impact in
   the pull request.

## Skill-writing rules

- Keep the frontmatter description precise enough to avoid unrelated triggers.
- Put always-needed decisions in `SKILL.md`; put conditional detail in one-level
  `references/` files.
- Preserve the parent's critical-path and final-validation responsibility.
- Do not add tool-specific dependencies unless the workflow genuinely requires
  them and a safe fallback is documented.
- Test behavior and invariants rather than exact prose.

## Version changes

When releasing, update the same version in:

- `plugins/subagents-workflow/.codex-plugin/plugin.json`;
- `plugins/subagents-workflow/skills/subagents-workflow/SKILL.md` metadata;
- `CHANGELOG.md`.

Use Semantic Versioning. Run `make package` only after validation and tests pass.

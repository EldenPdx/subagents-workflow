# Invocation examples

## One-link bootstrap prompt

Give only this prompt and the repository link to a compatible Agent:

```text
Install and use the subagents-workflow skill from:
https://github.com/EldenPdx/subagents-workflow

If you are Codex, prefer the repository's plugin marketplace. Otherwise install
the standard Agent Skill at
plugins/subagents-workflow/skills/subagents-workflow. Validate the installation,
then use the skill for my next multi-agent request.
```

## Explicit invocation

```text
Use $subagents-workflow to implement this feature. Keep the parent on the
critical path, use at most three subagents, assign non-overlapping write scopes,
and run the repository's full validation before finishing.
```

## Parallel investigation

```text
Use subagents to investigate the frontend and backend causes independently.
Both investigations must be read-only. Synthesize facts, inferences, and unknowns
before proposing a fix.
```

## Phased implementation

```text
Use $subagents-workflow with a phased topology. First establish the shared API
contract, then delegate the client and server implementations to separate
agents, followed by an independent verification pass.
```

## Exact role request

```text
Use exactly three agents if the boundaries are genuinely independent:
one implementation agent, one integration-test agent, and one read-only reviewer.
If that split would create overlapping writes, explain the safer topology first.
```

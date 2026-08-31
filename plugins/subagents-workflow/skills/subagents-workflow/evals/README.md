# Evaluation cases

`evals.json` contains behavioral forward tests for routing, ownership, phased
dependencies, read-only investigation, and no-tool fallback.

Run each prompt in a clean Agent context both with and without the skill. Grade
observable behavior rather than exact wording:

- topology fits the dependency graph;
- parent work remains on the critical path;
- write scopes do not overlap;
- waiting is dependency-driven;
- evidence and real diffs are reviewed;
- final integration validation is reported;
- unavailable tools cause safe direct-mode degradation.

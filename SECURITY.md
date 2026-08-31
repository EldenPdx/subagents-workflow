# Security policy

## Supported versions

Security fixes are applied to the latest released major version.

## Reporting a vulnerability

Do not open a public issue for vulnerabilities that could enable command
execution, approval bypass, sandbox escape, credential exposure, or unsafe
external orchestration.

Use GitHub's private security advisory flow for this repository. Include:

- affected version;
- host Agent and runtime;
- reproduction steps;
- expected and actual behavior;
- whether credentials, production systems, or external costs are involved.

The skill itself has no network service and ships no executable runtime code.
Its main security boundary is instructional: it must preserve the host's
approval, sandbox, permission, and concurrency controls.

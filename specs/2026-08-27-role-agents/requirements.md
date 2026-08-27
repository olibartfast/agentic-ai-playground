# Role Agents Across Harnesses — Requirements

Status: implemented, 2026-08-27.

## Problem

Every integration note stopped at the endpoint: how an agent reaches a model.
The delegation half of the [cloud-to-local workflow][blog] — roles, handoff
packets, and which guardrails each harness enforces — existed nowhere in the
repository, so a reader could connect an agent but not run the workflow the
benchmarks are meant to compare.

## Scope

- A cross-harness guide covering OpenCode, Kilo, Claude Code, Codex, Pi and
  Hermes, reachable from both indexes and from each agent's own notes.
- Committed role files for the harnesses that support them.
- A VS Code integration note, since VS Code carries no ACP client of its own.

## Out of scope

- Running the roles end to end. No delegated run was executed, so per-role cost
  and defect rates remain unmeasured.
- Pi and Hermes role files. Neither exposes a file-backed role system; the
  finding is recorded rather than worked around.

## Constraints

- Guardrails that matter must be configuration, not prose. A restriction stated
  only in a behaviour brief is advisory and must be labelled as such.
- Committed model identifiers must come from each harness's own catalogue, not
  copied between harnesses.
- Claims must separate what was executed here from what was read from a binary
  or from the article.

[blog]: https://olibartfast.ninja/blog/ai-coding-workflows-cloud-to-local.html

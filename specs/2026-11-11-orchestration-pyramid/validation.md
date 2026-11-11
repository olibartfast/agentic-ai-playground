# Orchestration Pyramid — Validation

## Executed

- A reviewer parsed 5 Codex TOML files, 7 Hermes YAML examples, 1 Claude
  settings JSON, and 13 Claude/OpenCode front-matter files.
- Eight updated relative links resolved. Static assertions passed for model
  assignments, tool boundaries, and delegation settings across Claude (6),
  Codex (5), OpenCode (6), and Hermes (6 profiles plus the root example).
- `git diff --check` passed.

## Not run

- No paid inference or provider API requests.
- No Hermes plugin install or edits to user-level configuration.
- No end-to-end Claude Code, Codex, or Hermes delegated session. Syntax and
  static configuration checks do not prove runtime model access, provider
  entitlement, or successful delegation.

# Role Agents Across Harnesses — Validation

## Executed

- [x] `opencode agent list` shows architect, planner, implementer,
      implementer-local and reviewer.
- [x] `opencode debug agent implementer` resolves `steps: 12`,
      `providerID: openrouter`, and `task`, `edit`, `write`, `glob` all false
      under the deny-by-default template.
- [x] `opencode debug agent reviewer` resolves `edit: false`, `write: false`,
      `task: false`.
- [x] `kilo agent list` and `kilo debug agent` show the same five roles with
      the same resolved flags and Kilo's own model identifiers.
- [x] All four `.codex/agents/*.toml` parse with `tomllib`.
- [x] `git diff --check` reports no whitespace errors.
- [x] Every relative Markdown link in the change resolves.
- [x] ACP: `session/new` in the project returns `architect` and `planner` as
      modes; the same call from `$HOME` returns only the built-ins.
- [x] ACP: with mode `architect`, `opencode export` records
      `providerID=opencode modelID=big-pickle` — the role's model is ignored.

## Not executed

- [ ] A delegated run. Whether a subagent keeps its own `model:` when spawned
      is unverified, and it is the measurement the cheap-worker argument rests
      on.
- [ ] Claude Code and Codex roles have never been run. Their front-matter keys
      were confirmed present in the shipped binaries; nothing more.
- [ ] Per-agent `model_provider` in a Codex agent file. Until tested, select a
      local provider per run with `-c model_provider=...`.

# Role Agents Across Harnesses — Plan

## Approach

1. Write the role files for OpenCode first, since it is the only harness with
   path-level enforcement and therefore the one whose guardrails can be
   verified rather than asserted.
2. Port to Kilo unchanged apart from the directory and the model identifiers,
   which come from `kilo models`.
3. Express the same roles in Claude Code and Codex using their coarser levers,
   and state in each worker's brief that its path list is not enforced.
4. Write `docs/role-agents.md` as the single cross-harness entry point and link
   it from the root README, the integrations index, and each agent's notes.
5. Record the VS Code path separately, because it is an ACP client question
   rather than an agent-configuration one.

## Decisions

- **Deny-by-default worker templates.** The committed `permission` block grants
  no edit paths and no test command. The planner regenerates both per phase.
  A template that ships a usable allowlist is a template that ships an
  over-broad one.
- **`task: deny` on every restricted agent.** Without it a worker delegates to
  an unrestricted built-in agent and inherits its tools.
- **No command that executes worker-written code.** A test runner pointed at a
  directory the worker may edit is an arbitrary-execution path wearing the name
  of the inner loop.
- **`implementer-local` differs by the model line alone.** Endpoint cautions
  live in the guide, so a local-versus-hosted comparison does not also change
  the brief.

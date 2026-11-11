# Role agents across harnesses

This guide describes a reusable orchestration pattern, then records what each
harness can enforce. The model assignments in examples are operator choices,
not project-wide defaults; provider and model availability must be checked in
the selected account or local catalogue.

## The orchestration pyramid

Keep quick, focused changes in the main session. For complex work, the main
session invokes one orchestrator, which reads the repository contract and
selects only the specialists the task needs. The orchestrator owns coordination
and integration, not implementation edits.

| Role | Responsibility | Delegation |
| --- | --- | --- |
| Main session | Small tasks directly; invoke orchestrator for complex work | May invoke orchestrator only under this workflow |
| `orchestrator` | Scope work, dispatch specialists, manage dependencies, integrate and verify | Yes; sole delegating role |
| `architect` | Resolve difficult design/interface/migration decisions; return recommendations | No |
| `planner` | Turn the objective/design into ordered tasks, paths, acceptance criteria, checks | No |
| `worker` | Implement its assigned packet and run focused checks | No; sole role assigned implementation edits |
| `reviewer` | Independently review diff against requirements; send actionable findings to worker | No |
| `explorer` | Read-only repository/source investigation; return grounded findings | No |

Typical flow: main session → orchestrator → (architect if needed) → planner →
worker(s) → reviewer → worker for fixes → reviewer or orchestrator verifies.
Skip architect/planner/reviewer when the task is small enough; do not fan out
work that shares files or requires frequent back-and-forth. The orchestrator
does not edit files. Only the worker edits implementation files. For findings,
the reviewer reports evidence and the orchestrator sends a bounded repair task
to the worker, then checks the result.

These boundaries are a workflow contract, not a universal harness security
property. A role prompt cannot enforce limits that the harness does not
provide. In particular, shared working directories, shell access, or an
unrestricted primary session can bypass a prose-only write restriction.

## Before delegation

The packet is the worker's interface. It names editable paths, read-only
context, required behavior, and the command that settles completion. Keep
acceptance checks outside the worker's editable paths where the harness can
enforce that. Read repository `AGENTS.md` and relevant specs before planning;
do not duplicate or contradict them in agent prompts.

Avoid excessive fan-out. Each child needs context and a returned result to
integrate. Parallelize only independent tasks with disjoint ownership; keep
dependencies sequential. The worker may run focused checks during development;
the orchestrator owns final integration and verification.

## Harness capabilities

| Harness | Role files / routing | Enforced boundaries and limits |
| --- | --- | --- |
| OpenCode | `.opencode/agent/*.md`; provider-qualified model and `steps` | Tool permissions can deny task/edit per role; packet paths are regenerated for each worker task. |
| Kilo | Existing `.kilo/agent/*.md` | Existing setup is unchanged in this change. |
| Claude Code | `.claude/agents/*.md`; model and effort per agent | Tool allowlists can remove write tools or constrain which agent types a primary agent invokes; shell and permissions still matter. Set nested spawn depth explicitly. |
| Codex | `.codex/agents/*.toml`; model and effort per agent | Agents inherit the parent sandbox; no path allowlist or per-agent turn cap. Read-only roles are behavioral. |
| Hermes | Profiles plus `delegate_task`; optional profile routing plugin | Child toolsets inherit from the parent; prompts and `role=leaf`/`role=orchestrator` govern delegation. Profile routes share the listed profile's credentials and terminal policy. |
| Pi | Prompt per run, `--no-tools` options | Coarse tool availability; no committed file-backed role system is established here. |

Kilo's current committed files retain their older role setup. Their migration
is out of scope; do not imply those files already implement this pyramid.
The measurements cited in the [workflow article][blog] remain historical:
multi-agent runs used roughly 50% more context/turns and 20% more tool calls
than one long session, while splitting into many small workers increased the
coordinator context substantially. They motivate bounded fan-out; they are not
measurements of the configurations in this update.

### Kilo Code's existing setup

Kilo uses `.kilo/agent/*.md`, not `.opencode/agent/`; model identifiers come
from Kilo's catalogue. The existing Kilo profile setup is outside this change.
Earlier integration checks verified its five roles and deny-by-default
worker/reviewer settings on Kilo 7.4.20; those checks do not verify this new
orchestration pattern.

## OpenCode

The role files are in [`.opencode/agent/`](../.opencode/agent/). Invoke the
orchestrator as a subagent from the main session; its `task: allow` is the sole
delegation grant. The selected
mapping is Spark (`meta/muse-spark-1.3-contributor`, high) for orchestrator,
architect, and reviewer; Ember (`meta/muse-ember-1.0`, high/low) for planner
and explorer; and DeepSeek Flash (`deepseek/deepseek-flash`, low) for worker.
The implementer filename is retained for compatibility. Worker `steps: 25`
sets the loop ceiling. Its edit permissions are a deny-by-default template;
the operator must configure only the packet's paths before dispatch (the
orchestrator itself has no edit permission and cannot change worker policy).
`task: allow` belongs only to the orchestrator; other roles deny task
delegation. Verify installed model identifiers and permissions with
`opencode agent list` and `opencode debug agent <name>` before use.

## Claude Code

Committed profiles live in [`.claude/agents/`](../.claude/agents/). The selected
model/effort mapping is:

| Role | Model | Effort |
| --- | --- | --- |
| orchestrator | `claude-sonnet-5-5` | medium |
| architect | `claude-fable-5-2` | high |
| planner | `claude-opus-5-5` | high |
| worker (`implementer` file retained for compatibility) | `claude-sonnet-5-5` | medium |
| reviewer | `claude-fable-5-2` | high |
| explorer | `claude-haiku-5-5` | low |

The role files pin full model IDs. Fable 5.2 requires Claude Code 2.1.321 or
later. In `.claude/settings.json`,
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "2"` allows the orchestrator to spawn
one leaf layer. The orchestrator has `Agent` and read-only tools; specialists
omit `Agent`, and architect/planner/reviewer/explorer use read-only tool
allowlists. The worker is the only role with `Edit`/`Write`.

This limits tools for those custom subagents. The ordinary main session still
has the tools granted by the user's settings, so “only the orchestrator
delegates” is a workflow instruction unless the operator starts a constrained
orchestrator as the main agent. Claude Code supports deeper subagent spawning
by default; keep the depth setting at two for this pattern. The `Agent(type)`
allowlist constrains types only when the custom agent runs as main; selecting
child types from a subagent is behavioral. See the [official
subagent guide](https://code.claude.com/docs/en/sub-agents) and [Fable 5.2
announcement](https://www.anthropic.com/claude-fable-and-mythos-5-2).

## Codex

Repository agent files live in [`.codex/agents/`](../.codex/agents/). This
project's assignments follow the operator's configured Codex baseline:

| Role | Model | Reasoning effort |
| --- | --- | --- |
| orchestrator | `gpt-6.1-sol` | low |
| architect | `gpt-6-astra` | high |
| planner | `gpt-6.1-terra` | medium |
| worker (`implementer.toml` retained for compatibility) | `gpt-6-luna` | high |
| reviewer | `gpt-6.1-sol` | high |
| explorer | Optional; use built-in read-only exploration | — |

Codex agent files describe agents the primary session can spawn; they do not
start a session as that role. The orchestrator's coordination-only prompt and
the worker-only edit rule are behavioral. Codex has no path allowlist or
per-agent turn cap; use workspace/read-only sandbox modes and verify the diff.
See the [Codex integration notes](../integrations/codex/notes.md).

## Hermes Agent

Hermes can route each delegated task to a named profile with the official
`advanced-delegation` plugin's `profile_routes` backend. The proposed example
is in [`integrations/hermes/orchestration/`](../integrations/hermes/orchestration/).
It uses Meta Muse Spark for orchestrator/architect/reviewer, Meta Muse Ember
for planner/explorer, and DeepSeek Flash for worker. The DeepSeek provider's
model ID is `deepseek-flash`; Ember was absent from the local Hermes Meta model
cache when this example was prepared, so verify availability before enabling
the profile route.

Set `delegation.max_spawn_depth: 2`. Only a child explicitly spawned with
`role="orchestrator"` retains the delegation toolset; leaf is the default.
Profile routes alone do not restrict child tools: children inherit the parent's
toolsets, so the worker's “only assigned paths” and the non-worker no-edit
rules remain behavioral. The example pins primary and fallback routes to Meta
and DeepSeek only, but keeps credentials out of the repository. Install and
enable the plugin using the current Hermes plugin manager before selecting the
backend; without it, the backend fails closed. See the [Hermes integration
notes](../integrations/hermes/README.md) and [delegation docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation).

## Pi

Pi's providers live in `~/.pi/agent/models.json`; role prompts are per run and
`--no-tools` / `--no-builtin-tools` are the available coarse tool controls.
Treat role boundaries as behavioral and inspect the diff. See
[`integrations/pi/`](../integrations/pi/).

## Verification status

The examples are configuration/documentation, not evidence of a completed
multi-agent run. Static parsing can confirm syntax only. Model entitlement,
provider availability, tool inheritance, and end-to-end delegation need
runtime checks in the configured account. Older benchmark observations in the
2026-08 role-agent feature packet remain historical evidence, not results for
this pyramid.

[blog]: https://olibartfast.ninja/blog/ai-coding-workflows-cloud-to-local.html

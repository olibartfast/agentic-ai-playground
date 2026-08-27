# Role agents across harnesses

Pointing an agent at a model is the easy half. This document covers the other
half of the [cloud-to-local workflow][blog]: splitting the work into roles,
putting each role in a committed file, and enforcing what a delegated worker may
do — for every harness tracked in [`integrations/`](../integrations/).

The claim being implemented is narrow and worth stating before any syntax. The
model is a dial. Roles, constraints, and the command that settles completion are
the durable parts. If those three live in the repository, swapping a model is a
configuration change; if they live in a chat transcript, they leave with the
session.

## Before any agent file

Delegation to a cheaper worker only pays once implementation is a separable job
with an explicit interface. Three repository artifacts make it one, and none of
them are agent configuration:

1. **Constraints** — decisions already made, which no agent may revisit. In this
   repository they are [`AGENTS.md`](../AGENTS.md) and
   [`specs/tech-stack.md`](../specs/tech-stack.md).
2. **A scoreboard** — one command whose exit status settles whether the work is
   done. Each feature packet declares its own in `validation.md`.
3. **Acceptance tests the worker cannot edit** — enforced below by write
   allowlists, not by asking.

Splitting work across subagents on a *single* model costs more, not less: the
measured runs behind the article report roughly 50% more context and turns and
20% more tool calls than one long session. Treat that as the price of building
the interface, and collect the return at the next step — routing implementation
to a cheaper or local model.

## The four roles

| Role | Mode | Tier | Owns |
| --- | --- | --- | --- |
| `architect` | primary | top | Architecture, roadmap shape, whole-project review |
| `planner` | primary | mid | One phase: decompose, delegate, judge what returns |
| `implementer` | subagent | cheap or local | One packet, against named paths |
| `reviewer` | subagent | mid | Read-only inspection of the diff against the packet |

Two failure modes to design against, both observed rather than theorised. A
planner that sees weak output and quietly rewrites the code itself returns cost
to the single-model baseline while the workflow still looks delegated — instruct
it to send defects back to a fresh worker, and verify by checking which role
consumed the tokens. And shrinking worker sessions inflates the planner: eight
small workers instead of two large ones cut the average worker session about
sixfold while the orchestrating context grew from 90K to 712K. Total context
barely moved. Someone composes eight briefs and reviews eight results.

## What each harness enforces

Everything above the behaviour brief is applied by the harness. The brief itself
is persuasion — in the recorded runs a worker told not to write complete code
obeyed in one phase and partially ignored it in the next, with no other change.

| Lever | OpenCode / Kilo | Claude Code | Codex | Pi | Hermes |
| --- | --- | --- | --- | --- | --- |
| Worker tier | `model:`, provider-qualified | `model:` | `model` | per-run flag | profile |
| Loop ceiling | `steps:` | `maxTurns:` | none per agent | none | none |
| Reachable tools | `permission:` keys | `tools:` / `disallowedTools:` | `sandbox_mode`, `mcp_servers` | `--no-tools` | tool policy |
| Write scope | fine, per path | coarse, working directory | coarse, workspace | coarse | coarse |
| Behaviour brief | Markdown body | Markdown body | `developer_instructions` | prompt | profile prompt |
| Model choice | any provider, cloud or local | one vendor family | one vendor family | any provider | any provider |

Two gaps deserve naming rather than papering over. Codex has no per-agent turn
or step cap — session-wide token controls are not the same thing — so
termination must come from the parent: delegate one phase, require a single
scoreboard run, and check that the child returned. And only OpenCode and its
fork offer path-level write rules; elsewhere "these files and no others" is a
review obligation, not a setting.

## OpenCode

Files live in `.opencode/agent/*.md`, one per role, with YAML front matter and
the system prompt as the body. This repository's set is in
[`.opencode/agent/`](../.opencode/agent/).

1. Create the worker with a deny-by-default permission block. The allowlist is
   the point: a rule that permits everything except the specs still leaves the
   worker free to edit the manifest, the presets, and the acceptance suite.
   Deny `task` as well — a worker that can delegate to an unrestricted built-in
   agent inherits its tools and voids every other line. And never allow a
   command that executes code the worker itself can write: permitting a test
   runner over a directory the worker may edit is the same hole wearing a
   different name.

   ```markdown
   <!-- .opencode/agent/implementer.md -->
   ---
   description: Implements one delegated packet against named paths.
   mode: subagent
   model: openrouter/deepseek/deepseek-v4-flash
   steps: 12
   permission:
     edit:
       "*": deny
       "<the packet's paths, regenerated per phase>": allow
     bash:
       "*": deny
       "python3 -m py_compile *": allow
     task: deny
     glob: deny
     webfetch: deny
     websearch: deny
   ---

   Implement only the delegated packet, touching only the paths it names.
   Read the real file before changing it. Write each file's complete final
   content; never patch by anchor. Finish by running the scoreboard command
   exactly once, then stop and report its result whether it passes or fails.
   Do not repair after it.
   ```

2. Make the reviewer read-only with `edit: {"*": deny}` rather than by asking it
   not to change anything.

3. Verify what the harness applied, not what the front matter claimed:

   ```bash
   opencode debug agent implementer
   ```

   The resolved output carries `steps`, the model as `providerID`/`modelID`, and
   a `tools` map — `glob: false`, and `edit: false`/`write: false` on a correct
   reviewer.

4. Confirm the roles are visible where you will use them:

   ```bash
   opencode agent list
   ```

Both directory spellings load: `.opencode/agent/` and `.opencode/agents/`.

### Going local is one line

```diff
-model: openrouter/deepseek/deepseek-v4-flash
+model: llama.cpp/gemma-4-26b-4b-it
```

Nothing else in the file moves — same brief, same guardrails, different
hardware. This is the entire thesis reduced to one line, and it is available
only because the provider is part of the model identifier. Serve the endpoint
per [`integrations/opencode/`](../integrations/opencode/), and size phases for
the weakest participant: one roadmap phase had to be split in two before a local
worker could complete it.

Do not maximise the served context window. A larger window on a small model
invites the oversized sessions that make small models fail; keep the worker's
context modest and control size through the packet.

### The local worker differs by one line

[`implementer-local.md`](../.opencode/agent/implementer-local.md) is
byte-identical to `implementer.md` except for `model:` and `description:`. That
is deliberate and worth protecting: a local-versus-hosted comparison in which
the two workers also carry different briefs measures the prompts, not the
models. Endpoint-specific cautions belong here, not in the worker's body.

On this machine: `llama.cpp/gemma-4-26b-4b-it` is the LAN llama-server and the
practical worker; `local/gemma-4-e4b` is the laptop CPU endpoint, where
OpenCode's 7,876-token system prompt costs roughly 161 s of prefill per cold
start, so prefer the TUI and its slot cache; `ollama/qwen2.5-coder:7b` is
reachable but measured unable to emit the tool-call wrapper, so it is not a
working agent loop. Kilo lists neither OpenRouter nor the LAN llama.cpp
provider, so its local option is `local/gemma-4-e4b`.

Keep the served context window modest on purpose. A larger window on a small
model invites exactly the oversized sessions that make small models fail;
control size through the packet instead.

## Kilo Code

Kilo is an OpenCode fork, so the schema above applies unchanged with two path
changes — see [`integrations/kilocode/`](../integrations/kilocode/):

- Agent files: `.kilo/agent/*.md`, **not** `.opencode/agent/`. Verified: with
  only `.opencode/agent/` present, `kilo agent list` shows its built-ins and
  none of the roles. This repository's set is in
  [`.kilo/agent/`](../.kilo/agent/).
- User config: `~/.config/kilo/kilo.jsonc`.
- Model identifiers differ from OpenCode's. Kilo lists no OpenRouter or LAN
  llama.cpp provider on this machine, so the roles use `kilo/~anthropic/*`,
  `kilo/~deepseek/*`, and `local/gemma-4-e4b`. Read the catalogue rather than
  copying OpenCode's strings.

```bash
kilo agent list
```

## Claude Code

Files live in `.claude/agents/*.md`. Same shape as OpenCode, different lever
names, and the model is a tier inside one vendor family. This repository's set
is in [`.claude/agents/`](../.claude/agents/):

```markdown
<!-- .claude/agents/implementer.md -->
---
name: implementer
description: Implements one delegated packet against named paths.
model: haiku
maxTurns: 12
disallowedTools: WebFetch, WebSearch
permissionMode: acceptEdits
---

Implement only the delegated packet, touching only the paths it names.
Write each file's complete final content; never patch by anchor.
Finish by running the scoreboard command exactly once, then stop and
report its result whether it passes or fails. Do not repair after it.
```

`permissionMode: acceptEdits` decides whether the agent may write in the working
directory at all — not which files. The named-path restriction therefore lives
in the packet and has to be checked in review. Define the reviewer with
`disallowedTools: Write, Edit`.

## Codex

Codex splits the same information between the planner's `config.toml` and one
TOML file per delegated agent. Support for `.codex/agents` and
`developer_instructions` is present in the shipped binary of Codex 0.149.1.
This repository's set is in [`.codex/agents/`](../.codex/agents/).

```toml
# ~/.codex/config.toml — the planner
model = "gpt-5.6-terra"
model_reasoning_effort = "medium"
```

```toml
# .codex/agents/implementer.toml — the worker
name = "implementer"
description = "Implements one delegated packet against named paths."
model = "gpt-5.6-luna"
model_reasoning_effort = "low"
sandbox_mode = "workspace-write"
developer_instructions = """
Implement only the delegated packet, touching only the paths it names.
Write each file's complete final content; never patch by anchor.
Finish by running the scoreboard command exactly once, then stop and
report its result whether it passes or fails. Do not repair after it.
"""
```

Use `sandbox_mode = "read-only"` for the reviewer. Pin
`model_reasoning_effort` on both sides of any comparison: the tiers span the
same documented effort range, so a high-effort run measured against a
default-effort one tells you about the setting rather than the model.

Because there is no per-agent step cap, the parent workflow has to terminate the
child: one phase, one scoreboard run, and an explicit check that it returned.

All four roles are committed as agent files, but they are not equivalent to the
article's `config.toml` planner and should not be read as such. Files under
`.codex/agents/` define agents the primary session may **spawn**; the installed
CLI has no flag that starts a session *as* one. A session therefore begins on
the `config.toml` model and spawns `architect` or `planner` as a child, which
adds a parent turn and its tokens to every run.

Set the tier you want to start on in `~/.codex/config.toml`, as above, and
treat the architect and planner files as reviewable records of what those roles
are — not as the mechanism that selects them. When comparing runs across
harnesses, count that extra parent: it is the kind of difference that shows up
as cost without showing up in the diff.

Reaching a local endpoint is a provider selection — `model_provider`, per
[`integrations/codex/open-models.md`](../integrations/codex/open-models.md) —
and whether that key is honoured inside an agent file rather than in
`config.toml` is unverified. A committed `implementer-local.toml` that silently
fell back to the default provider would send the work to a hosted model while
claiming to run locally, so select the local provider per run instead:

```bash
codex --model <local-model-id> -c model_provider=llama_cpp
```

Claude Code has no local variant for a different reason: its model choice stays
inside one vendor family. Only the two open harnesses treat the provider as
part of the model identifier, which is what makes the cheap-worker move and the
go-local move the same edit.

## Pi and Hermes

Neither exposes a file-backed role system of this kind, so the delegation
boundary stays in the prompt — which, by the argument above, makes it advisory
for exactly the small models most likely to ignore it.

- **Pi** — providers in `~/.pi/agent/models.json`, extensions via `pi install`,
  and `--no-tools` / `--no-builtin-tools` as the only tool lever. Roles are one
  prompt per run. See [`integrations/pi/`](../integrations/pi/).
- **Hermes** — `hermes profile create` gives a named model-plus-settings bundle,
  the closest available analogue to a role, and `hermes import-agent
  {claude-code,codex}` maps an existing agent's instructions, permission
  allowlists, MCP servers, and skills into Hermes equivalents. See
  [`integrations/hermes/`](../integrations/hermes/).

For either, replace enforcement with review: assume the worker may touch
anything in the tree and diff before trusting it.

## The handoff packet

The packet is the interface between planner and worker, and it is
model-independent — the same brief works on a frontier worker, a hosted
open-weight one, and a local model, which is what makes the roles swappable. It
names four things and nothing else:

- the paths the worker may edit,
- the files it may read but not change,
- the required final state, in behavioural terms,
- the one scoreboard command that settles completion.

What to leave out matters as much. Do not point the worker at
[`specs/`](../specs/) — following references costs context it does not have. Do
not paste whole files. Do not hand it finished code: if the planner writes the
implementation into the packet, the expensive model produced it and the cheap
one only copied it.

The packet and the worker's write allowlist must agree, which means regenerating
the permission block per phase. That is a fair trade — it forces the decision
about what a phase may touch to happen before the worker starts, rather than in
the diff.

## Every constraint maps to an observed failure

| Constraint | Failure it prevents |
| --- | --- |
| Step ceiling | Retry loops that run until the context is exhausted |
| Write allowlist | Editing the specs, tests, manifest or presets to match what was built |
| Command allowlist | Package installs, network fetches, anything bypassing the project's checks |
| Search and web tools disabled | Wandering the repository and exploding its own context |
| Whole-file writes, never anchored edits | A mismatched anchor retried forever — the most common small-model failure |
| Read the real file before changing it | Rewriting a half-remembered version held in context |
| No recursive listing of generated trees | One command flooding the window from a build or vendored tree |
| Run the scoreboard once, report, do not repair | The rerun-and-fix death spiral after the result is in |

The last row needs a distinction that is easy to get wrong. The worker's inner
development loop is not the enemy: compiling and running targeted tests while
writing code is its fastest feedback, and forbidding it makes the compiler
useless as a tool. The allowlists above therefore permit the ordinary build and
test commands. What must happen exactly once is the *scoreboard* — the run whose
exit status you record. After it reports, the worker stops. Whether to repair is
the planner's decision.

## Verification status

Claims here are not uniformly tested. What was exercised on this machine, and
what was read from a shipped binary or the article:

| Harness | Status |
| --- | --- |
| OpenCode 1.18.23 | Verified — five roles resolve via `opencode debug agent`, including `steps`, per-role model, and `glob`/`edit`/`write` disabled where declared |
| Kilo 7.4.20 | Verified — the same five roles load from `.kilo/agent/`; `kilo debug agent` confirms the model, `steps: 12`, and `edit`/`write` disabled on the reviewer |
| Codex 0.149.1 | Partly verified — `.codex/agents` and `developer_instructions` present in the binary, role files parse as valid TOML; no run performed |
| Claude Code 2.1.247 | Partly verified — `model`, `maxTurns`, `disallowedTools` and `permissionMode` all appear in the shipped binary; role files written but no run performed |
| Pi 0.84.2, Hermes 0.20.0 | Verified absent — no file-backed role system found in either CLI |

One caveat that outranks all of the above: over ACP, selecting a role does
**not** select its model. See
[`integrations/vscode-acp/`](../integrations/vscode-acp/#the-mode-picker-does-not-carry-the-roles-model).

[blog]: https://olibartfast.ninja/blog/ai-coding-workflows-cloud-to-local.html

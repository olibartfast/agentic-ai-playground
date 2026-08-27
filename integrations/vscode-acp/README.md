# VS Code over ACP

[ACP][acp] (Agent Client Protocol) is JSON-RPC over stdio between an editor and
a coding agent — LSP's shape, applied to agents. An editor that speaks it gets
every ACP agent at once instead of one vendor extension per agent.

VS Code does **not** ship an ACP client. Its own chat host
(`chat.agentHost.*`, VS Code 1.135) is a closed list — Copilot, Claude, and
Codex — with no setting that registers a fourth agent. ACP in VS Code therefore
arrives through a marketplace extension, and that extension owns the agent
list, the registry browser, and the chat panel.

Verified on VS Code 1.135.0 with [ACP Client][acp-client]
(`formulahendry.acp-client`) 0.2.0.

## Where the registry is

Two different things are called "the registry", and only one of them is in
VS Code:

| Thing | Where it lives | What it does |
| --- | --- | --- |
| The ACP agent registry | `https://cdn.agentclientprotocol.com/registry/v1/latest/registry.json` | Upstream catalogue, 39 agents as of 2026-08-27 |
| The registry browser | ACP Client extension, command `ACP: Browse Agent Registry` | Fetches that JSON and installs an entry into your settings |
| Your configured agents | `acp.agents` in VS Code user or workspace settings | What the agent picker actually shows |

Reaching the browser in the UI:

- Command Palette (<kbd>Ctrl+Shift+P</kbd>) → **ACP: Browse Agent Registry**, or
- the **ACP Client** activity-bar container → **Agents** view → its title menu
  (the `…` overflow next to the `+`).

The `+` in that same title bar is `ACP: Add Agent Configuration`, which writes
an entry by hand rather than from the catalogue.

VS Code's own Extensions marketplace is not involved past installing the client
once, and the registry is not cached in a settings file — it is fetched from
the CDN each time the browser opens.

## Install and configure

```bash
code --install-extension formulahendry.acp-client
```

Each agent is an entry in `acp.agents`, keyed by the name shown in the picker.
The value is the command VS Code spawns, which must speak ACP on stdio:

```json
{
  "acp.agents": {
    "OpenCode": {
      "command": "/home/USER/.opencode/bin/opencode",
      "args": ["acp"],
      "env": {}
    },
    "Pi": {
      "command": "npx",
      "args": ["-y", "pi-acp@latest"],
      "env": {}
    }
  },
  "acp.autoApprovePermissions": "ask"
}
```

Prefer an absolute path to an installed binary over `npx <package>@latest`.
`npx` re-resolves the package on every connection, so a cold start pays a
download before the agent's own prefill, and the version that answers is
whatever the registry published that day rather than the one recorded here.

Keep `acp.autoApprovePermissions` at `ask`. Setting `allowAll` hands blanket
approval to every agent in the list, including the ones whose guardrails are
prompt text rather than configuration.

## Agents that speak ACP

Support is uneven: three of these serve ACP themselves, three need an adapter
package in front.

| Agent | Command | Native or adapter |
| --- | --- | --- |
| [OpenCode](../opencode/) | `opencode acp` | native |
| [Kilo Code](../kilocode/) | `kilo acp` | native |
| [Hermes Agent](../hermes/) | `hermes acp` | native |
| [Codex](../codex/) | `npx @agentclientprotocol/codex-acp` | adapter, OpenAI/JetBrains/Zed |
| [Claude Code](../claude-code/) | `npx @agentclientprotocol/claude-agent-acp` | adapter, Anthropic/JetBrains/Zed |
| [Pi Agent](../pi/) | `npx pi-acp` | adapter, community |
| [Oh My Pi](../omp/) | see its notes | native |

Hermes is not in the upstream registry and has to be added by hand; the other
five are catalogue entries. Kilo and OpenCode ship as release binaries there,
so the registry browser offers to download one even when the CLI is already on
the machine — point the entry at your existing install instead.

## What ACP does not carry

The client contributes a panel, a session list, and two pickers —
`ACP: Set Agent Model` and `ACP: Set Agent Mode`. It contributes no models and
no roles. Both lists are read from the connected agent, so the
[cloud-to-local workflow][blog] is configured exactly where it was before, and
VS Code only displays the result:

| Agent | Roles read from | Models read from |
| --- | --- | --- |
| OpenCode | `.opencode/agent/*.md` | `~/.config/opencode/opencode.json` |
| Kilo Code | `.kilo/agent/*.md` | `~/.config/kilo/kilo.jsonc` |
| Claude Code | `.claude/agents/*.md` | `model:` in each agent's front matter |
| Codex | `.codex/agents/*.toml` | `~/.codex/config.toml` |
| Pi Agent | — | `~/.pi/agent/models.json` |
| Hermes Agent | — | `~/.hermes/config.yaml` |

Two consequences worth stating plainly. The role list in the panel is read from
the agent, so a role added to a project file appears there on the next
connection — but its **model does not follow it**, which is measured in
[the section below](#the-mode-picker-does-not-carry-the-roles-model); do not
assume a one-line `model:` edit changes what actually serves the session. And
an agent whose roles are not file-backed (Pi, Hermes) exposes no mode list
here, so its delegation boundary stays in the prompt.

Project-scoped role files only load when the connected agent's working
directory is that project. `acp.defaultWorkingDirectory` overrides the
workspace folder; leave it empty unless you mean to run every agent somewhere
else.

## This repository's OpenCode roles

[`.opencode/agent/`](../../.opencode/agent/) carries the five roles from the
[workflow article][blog]. OpenCode exposes them over ACP as a `mode` config
option, and only the **primary** ones are selectable — subagents are delegation
targets that a primary agent invokes, never a mode you pick:

| Role | Mode | Model | Enforced limits |
| --- | --- | --- | --- |
| `architect` | primary | `openrouter/anthropic/claude-opus-4.6` | edits confined to `specs/`, `docs/`, `README.md`, `AGENTS.md` |
| `planner` | primary | `openrouter/anthropic/claude-sonnet-4.6` | writes packets into `specs/`, no web tools |
| `implementer` | subagent | `openrouter/deepseek/deepseek-v4-flash` | `steps: 12`, deny-by-default edit and bash allowlists, glob and web disabled |
| `implementer-local` | subagent | `llama.cpp/gemma-4-26b-4b-it` | identical to `implementer`, one line changed |
| `reviewer` | subagent | `openrouter/anthropic/claude-sonnet-4.6` | `edit` and `write` resolve to `false` |

Confirm what the harness actually applied, rather than what the front matter
says, before trusting a worker:

```bash
opencode debug agent implementer
```

`implementer` and `implementer-local` differ in the model line alone. That is
the article's thesis in the form the editor can see: the same brief and the
same guardrails, cloud or local, selected by the delegating agent.

## The mode picker does not carry the role's model

Selecting a role in the panel switches the agent but **not** the model. The two
dropdowns are independent: `session/set_mode` changes which agent runs, and the
session keeps whatever model it was created with, so a role's `model:` front
matter is ignored for the primary agent over ACP.

Measured on OpenCode 1.18.23 — mode set to `architect`, then one prompt, then
`opencode export <sessionID>`:

```text
agent=architect  providerID=opencode  modelID=big-pickle
```

`big-pickle` is the global default, not the
`openrouter/anthropic/claude-opus-4.6` the role declares. Pick the model chip
to match the role you selected.

Do not answer this by adding a top-level `"model"` to the project's
`opencode.json`. That pins one vendor model into a committed file, which is
both the practice [the OpenCode notes warn against](../opencode/#verify-and-run)
and also the opposite of the article's argument that the model is a dial
rather than a property of the repository. A personal default belongs in
`~/.config/opencode/opencode.json`, where it stays a per-machine preference.

`session/set_config_option` with `optionId: "mode"` is not an alternative — it
changed neither agent nor model in testing; the session stayed on `build`.

Whether a delegated subagent keeps its own `model:` is a separate question and
is not verified here. Until it is, treat per-role model pairing under ACP as
unproven and check `opencode export` for the models a run actually used.

## When the mode list is missing your roles

Project roles load from the connected agent's working directory, and the ACP
client spawns the agent in the open workspace folder. A VS Code window with no
folder open spawns it in `$HOME`, where the project files do not exist. The
mode list is the visible symptom — same binary, same settings, cwd the only
difference:

| Agent cwd | `mode` options returned by `session/new` |
| --- | --- |
| `/home/USER` | `build`, `plan` |
| the project | `build`, `architect`, `planner`, `plan` |

Open the folder first, then **ACP: Restart Agent**. An already-connected
session keeps the cwd it was started with, so reconnecting is required and
reloading the window is not enough.

Read the list the agent actually offers, rather than inferring it, by driving
the handshake yourself:

```bash
cd /your/project
opencode acp
```

Then send `initialize` followed by `session/new` on stdin; the `configOptions`
array in the reply carries both the `model` and `mode` pickers the panel
renders.

[acp]: https://agentclientprotocol.com/
[acp-client]: https://marketplace.visualstudio.com/items?itemName=formulahendry.acp-client
[blog]: https://olibartfast.ninja/blog/ai-coding-workflows-cloud-to-local.html

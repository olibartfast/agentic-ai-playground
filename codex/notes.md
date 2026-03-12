# OpenAI Codex CLI — Rules & Best Practices

---

## 1. Project Overview

A modular repository structure designed for building Codex CLI projects with structured AI context, reusable skills, and automated development workflows. Codex CLI is OpenAI's open-source coding agent, built in Rust, that runs locally in your terminal. It can read, edit, and execute code on your machine within a selected directory.

### Installation

```bash
npm i -g @openai/codex
# or
brew install --cask codex
```

Authenticate with your ChatGPT account (Plus, Pro, Business, Edu, or Enterprise) or an API key:

```bash
codex login                    # Browser-based ChatGPT OAuth
codex login --device-code      # Device code flow (headless)
printenv OPENAI_API_KEY | codex login --with-api-key  # API key via stdin
```

### Recommended Repository Layout

```
codex_project/
├── AGENTS.md                # Primary always-on instructions — committed, shared with team
├── AGENTS.override.md       # Local override layer — gitignored
├── .codex/
│   ├── config.toml          # Project-scoped configuration
│   └── rules/               # Execpolicy rule files
├── .agents/
│   └── skills/              # Repository-scoped skills
│       ├── code-review/
│       │   └── SKILL.md
│       ├── refactor/
│       │   └── SKILL.md
│       └── release/
│           └── SKILL.md
├── README.md
├── docs/
│   ├── architecture.md
│   ├── decisions/
│   └── runbooks/
└── src/
    ├── api/
    │   └── AGENTS.md         # Directory-specific instructions
    └── persistence/
        └── AGENTS.md         # Directory-specific instructions
```

---

## 2. Custom Instructions & AGENTS.md

`AGENTS.md` is Codex's persistent instruction file — loaded at the start of every session before your first prompt. Codex builds an instruction chain by walking from the global scope down to your current working directory. Files closer to your working directory override earlier guidance because they appear later in the combined prompt.

### Instruction Discovery Order

Codex checks each directory for files in this order: `AGENTS.override.md` → `AGENTS.md` → fallback filenames (configurable). It includes at most one file per directory and concatenates them root-down, joining with blank lines.

### File Hierarchy

| File | Scope |
|------|-------|
| `~/.codex/AGENTS.override.md` | **Global override** — temporary global override without deleting base |
| `~/.codex/AGENTS.md` | **Global** — applies to all projects |
| `<project>/AGENTS.override.md` | **Project override** — local override layer (gitignored) |
| `<project>/AGENTS.md` | **Project** — committed to git, shared with team |
| `<project>/<subdir>/AGENTS.md` | **Directory-specific** — scoped context for submodules |

### Configuration Knobs

```toml
# ~/.codex/config.toml
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
project_doc_max_bytes = 65536  # Default: 32768 (32 KiB)
```

- **`project_doc_max_bytes`** — maximum combined size of instruction files before truncation. Raise the limit or split instructions across nested directories when you hit the cap.
- **`project_doc_fallback_filenames`** — additional filenames to try when `AGENTS.md` is missing at a directory level.

### Cross-Tool Compatibility

Codex also reads `CLAUDE.md` at the repo root (for Claude Code interoperability) and `.github/copilot-instructions.md` (for Copilot CLI interoperability) as additional instruction sources, though `AGENTS.md` takes primary precedence.

### AGENTS.md Best Practices

- **Keep instructions concise and actionable.** Lengthy instructions dilute effectiveness. Focus on what Codex would get wrong without them.
- **Use `AGENTS.override.md`** for temporary overrides without deleting the base file. Remove the override to restore shared guidance.
- **Layer global + project instructions.** Put personal working agreements in `~/.codex/AGENTS.md` and project norms in the repo root.
- **Avoid conflicts** between instruction files — Codex's choice between conflicting instructions is non-deterministic.
- **Test your instructions** by running `codex --ask-for-approval never "Summarize the current instructions."` from a repository root.

### Example Global Instructions

```markdown
# ~/.codex/AGENTS.md

## Working agreements
- Always run `npm test` after modifying JavaScript files.
- Prefer `pnpm` when installing dependencies.
- Ask for confirmation before adding new production dependencies.
```

### Example Project Instructions

```markdown
# AGENTS.md

## Repository expectations
- Run `npm run lint` before opening a pull request.
- Document public utilities in `docs/` when you change behavior.
```

### Example Directory Override

```markdown
# services/payments/AGENTS.override.md

## Payments service rules
- Use `make test-payments` instead of `npm test`.
- Never rotate API keys without notifying the security channel.
```

---

## 3. Memory

Codex has a persistent memory system that builds understanding of your codebase and preferences across sessions. It stores coding conventions, patterns, and preferences it deduces while working.

- Reduces the need to repeat context in every prompt
- Automatically makes future sessions more productive
- Managed via the `/memory` command
- Workspace-scoped writes ensure memories stay relevant to the project
- Use `codex debug clear-memories` to fully reset saved memory state

---

## 4. `@` File References & Inline Shortcuts

Type `@` in the composer to open a fuzzy file search over the workspace root. Press Tab or Enter to drop the highlighted path into your message.

```
@src/pipeline.py
@docs/architecture.md
```

Additional composer shortcuts:

- **`Enter`** while Codex is running — inject new instructions into the current turn
- **`Tab`** while Codex is running — queue a follow-up prompt for the next turn
- **`!command`** — run a local shell command (e.g., `!ls`); output is treated as user-provided context
- **`Esc Esc`** on empty composer — edit your previous message; keep pressing to walk further back
- **`Ctrl+G`** — open external editor (`$VISUAL` or `$EDITOR`) for longer prompts

---

## 5. Context & Session Management

| Command | What it does |
|---------|-------------|
| `/compact` | Compresses conversation history to free context window space. Instruction files survive (re-loaded). Lossy — use only when nearing the limit. |
| `/clear` | Resets session context entirely and starts a fresh chat. Free, no loss. |
| `Ctrl+L` | Clears the terminal view without starting a new conversation. |
| `/context` | Shows context window usage breakdown. |
| `/status` | Shows active model, approval policy, writable roots, and token usage. |

### Auto-Compaction

When your conversation approaches 95% of the token limit, Codex automatically compresses history in the background. You can also configure the threshold via `auto_compact_threshold` in `config.toml`.

### Session Resume

Codex stores transcripts locally so you can pick up where you left off:

```bash
codex resume                # Opens a picker of recent sessions
codex resume --last         # Resumes most recent session from current directory
codex resume --all          # Shows sessions beyond the current working directory
codex resume <SESSION_ID>   # Targets a specific session
```

Each resumed run keeps the original transcript, plan history, and approvals.

### Session Fork

Fork a previous session into a new thread while preserving the original transcript:

```bash
codex fork                  # Opens session picker
codex fork --last           # Forks most recent session
```

---

## 6. Modes of Use

Codex CLI has multiple interaction modes:

| Mode | How to use | When |
|------|-----------|------|
| **Interactive (TUI)** | `codex` | Default. Conversational back-and-forth with full-screen terminal UI. |
| **Non-interactive (exec)** | `codex exec "prompt"` or `codex e "prompt"` | Single-shot, headless execution. Streams to stdout or JSONL. |
| **Full Auto** | `codex --full-auto "prompt"` | Low-friction preset: `workspace-write` sandbox + `on-request` approvals. |
| **MCP Server** | `codex mcp` | Runs Codex as an MCP server over stdio for consumption by other agents. |
| **Codex Cloud** | `codex cloud-tasks` | Launch and manage Codex Cloud tasks from the terminal. |

### Quick One-Shot Execution

```bash
codex exec "Run tests and fix failures"
codex exec --json "Summarize this repo"     # Machine-readable JSONL output
codex exec --output result.md "..."         # Write final message to file
```

---

## 7. Sandbox & Approval System

Codex uses two layers of security that work together:

- **Sandbox mode** — controls what Codex can do technically (filesystem, network access)
- **Approval policy** — controls when Codex must ask before acting

### Sandbox Modes

| Mode | Behavior |
|------|----------|
| `read-only` | Default. Codex can browse files but won't make changes or run commands without approval. |
| `workspace-write` | Codex can read, edit within the workspace, and run routine commands. Network blocked by default. |
| `danger-full-access` | No sandbox restrictions. Use only in externally hardened environments. |

### Approval Policies

| Policy | Behavior |
|--------|----------|
| `untrusted` | Only known-safe read-only commands auto-run; everything else prompts. |
| `on-request` | Default for interactive. Model decides when to ask. |
| `never` | Never prompt. Risky — use only in isolated/CI environments. |

### Configuration

```toml
# ~/.codex/config.toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = false           # Opt in to outbound network
writable_roots = ["/path/to/extra/dir"]
```

### Command-Line Overrides

```bash
codex --full-auto "Run tests"                      # workspace-write + on-request
codex --sandbox workspace-write "Fix bug"           # Explicit sandbox mode
codex --ask-for-approval never "Deploy"             # No prompts (risky)
codex --dangerously-bypass-approvals-and-sandbox "Deploy"  # --yolo alias. CI only.
```

### Permission Control in Session

Use `/permissions` inside an interactive session to switch modes:

- **Auto** (default) — read, edit, and run commands in the working directory
- **Read-only** — browse files, won't change or execute
- **Full Access** — machine-wide access including network (use sparingly)

---

## 8. Rules (Execpolicy)

Rules give you fine-grained, per-command control over what Codex can execute outside the sandbox. They're defined in `.rules` files under `~/.codex/rules/` or `.codex/rules/`.

### Rule Syntax

```python
# ~/.codex/rules/default.rules

# Allow git read commands without prompting
prefix_rule(
    pattern = ["git", ["status", "log", "diff", "show"]],
    decision = "allow",
)

# Prompt before PR operations
prefix_rule(
    pattern = ["gh", "pr", "view"],
    decision = "prompt",
    justification = "Viewing PRs is allowed with approval",
)

# Block dangerous operations
prefix_rule(
    pattern = ["rm", "-rf"],
    decision = "forbidden",
    justification = "Recursive force deletion is too risky",
)
```

### Decisions

- **`allow`** — run without prompting
- **`prompt`** — ask for confirmation
- **`forbidden`** — block entirely

When multiple rules match, the most restrictive decision wins (`forbidden > prompt > allow`).

### Testing Rules

```bash
codex execpolicy check --pretty \
    --rules ~/.codex/rules/default.rules \
    -- gh pr view 7888
```

---

## 9. Skills

Skills are self-contained folders of instructions, scripts, and resources that Codex loads when relevant. They're portable across Codex CLI, the IDE extension, and the Codex app.

### Key Difference from AGENTS.md

- **AGENTS.md** — always-on, loaded every session
- **Skills** — loaded on demand when Codex recognizes the task matches the skill's description

### Invocation

- **Explicit** — type `$` in the composer to mention a skill, or use `/skills` to browse
- **Implicit** — Codex automatically chooses a skill when your task matches its description

### Directory Locations

| Path | Scope |
|------|-------|
| `.agents/skills/<skill-name>/` | Repository-scoped (every directory from cwd up to repo root is scanned) |
| `.github/skills/<skill-name>/` | Repository-scoped (cross-compatible with Copilot CLI and Claude Code) |
| `~/.codex/skills/<skill-name>/` | User-scoped, all projects |

### Anatomy of a SKILL.md

Every skill is a folder containing a `SKILL.md` file and optional bundled resources. `SKILL.md` has two parts: **YAML frontmatter** (metadata for discovery) and **markdown body** (instructions when invoked).

#### Frontmatter

```yaml
---
name: code-review
description: >
  Reviews code for bugs, style issues, and best practices.
  Use when reviewing pull requests, code changes, or when
  the user asks to "review", "check", or "audit" code.
---
```

- **`name`** (required) — unique identifier, lowercase with hyphens. Becomes a `/slash-command`.
- **`description`** (required) — critical for activation. Codex reads all skill descriptions at startup (~100 tokens each). Be specific about trigger phrases. Slightly "pushy" descriptions activate more reliably.

#### Optional: agents/openai.yaml

Add `agents/openai.yaml` alongside `SKILL.md` to configure UI metadata in the Codex app, set invocation policy, and declare tool dependencies.

#### Markdown Body

After frontmatter, write instructions in standard Markdown. Two categories:

**Reference-style skills** — add conventions Codex applies to ongoing work:

```markdown
---
name: api-conventions
description: API design patterns for this codebase
---
When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats: { "error": { "code": "...", "message": "..." } }
- Include request validation with Pydantic models
```

**Task-style skills** — step-by-step instructions for a specific action:

```markdown
---
name: code-review
description: >
  Comprehensive code review. Use when reviewing PRs or code changes.
---
When reviewing code:

1. **Check for bugs**: Identify runtime errors, edge cases, logic flaws.
2. **Verify style**: Ensure code follows team conventions.
3. **Evaluate architecture**: Flag violations of established patterns.
4. **Security scan**: Look for injection, hardcoded secrets, unsafe deserialization.
5. **Suggest improvements**: Propose simplifications, extractions, perf gains.
6. **Summarize**: Produce a structured report with severity levels.
```

### Bundled Resources (Optional)

```
code-review/
├── SKILL.md              # Entry point (keep under ~500 lines / 5k tokens)
├── agents/
│   └── openai.yaml       # UI metadata, invocation policy, tool dependencies
├── scripts/              # Executable code Codex runs via shell
│   └── lint_check.py
├── references/           # Supplementary docs loaded on demand
│   ├── STYLE_GUIDE.md
│   └── SECURITY_RULES.md
├── templates/            # Output scaffolds for consistent formatting
│   └── review_report.md
└── assets/               # Static files (icons, fonts, etc.)
```

### Progressive Disclosure

At startup, only frontmatter is loaded (~100 tokens). When a skill is activated, `SKILL.md` is loaded (<5k tokens). Bundled resources are read only when instructions reference them. This keeps the context window lean while making deep knowledge available on demand.

### Installing Skills

Use the built-in skill installer to install skills from the community:

```
$skill-installer
# Or prompt the installer to download from specific repositories
```

### Disabling Skills

```toml
# ~/.codex/config.toml
[[skills.config]]
path = "/path/to/skill/SKILL.md"
enabled = false
```

### SKILL.md Authoring Best Practices

- **Keep `SKILL.md` under 500 lines / 5,000 tokens.** Move detailed docs to `references/`.
- **Use active, directive language** — tell Codex what to do, not what might happen.
- **Break complex tasks into numbered steps** — sequential structure improves reliability.
- **Include examples** — concrete input/output pairs dramatically improve activation (~50% → ~90% with good examples).
- **Specify output formats** — show Codex exactly what the output should look like.
- **Define scope boundaries** — include "Out of Scope" so Codex knows when NOT to use the skill.
- **Add conditional logic** — handle branching ("If `.py`, run ruff; if `.ts`, run eslint").
- **Link to bundled resources** — use relative paths like `See [STYLE_GUIDE.md](references/STYLE_GUIDE.md)`.
- **Declare MCP dependencies** in `agents/openai.yaml` so Codex can install and wire them automatically.

---

## 10. Multi-Agent Workflows

Codex can spawn specialized agents in parallel and collect their results. This is helpful for highly parallel tasks like codebase exploration or multi-step feature plans.

### Enabling

```toml
# ~/.codex/config.toml
[features]
multi_agent = true
```

Or toggle via `/experimental` in the TUI.

### Agent Roles

Define roles in the `[agents]` section of `config.toml`:

```toml
[agents.reviewer]
description = "Find correctness, security, and test risks in code."
config_file = "./agents/reviewer.toml"  # Relative to config.toml
nickname_candidates = ["Athena", "Ada"]
```

Each role can override the default model, sandbox policy, and approval settings via its own `config_file`.

### Usage Example

```
I would like to review the following points on the current PR.
Spawn one agent per point, wait for all of them, and summarize the result:
1. Code correctness
2. Security vulnerabilities
3. Test coverage gaps
```

### CSV Fan-Out

For batch processing, Codex can fan work across agents using `spawn_agents_on_csv`. The exported CSV includes original row data plus job metadata.

### Key Details

- Sub-agents inherit your current sandbox policy
- Approval requests from inactive agent threads surface in the main thread
- `agents.max_concurrent_agents` defaults to 6
- `agents.max_agent_depth` defaults to 1 (one level of nesting)

---

## 11. Hooks (Experimental)

Shell commands that execute automatically at key points in Codex's lifecycle. Use hooks for deterministic control — things that shouldn't rely on the model "remembering."

### Hook Events

- **`SessionStart`** — fires when a session begins (setup, initialization)
- **`SessionStop`** — fires when a session ends (cleanup, archiving)

### Configuration

Hooks are configured as an experimental feature. The hooks engine is still evolving — check the changelog for the latest capabilities.

### Hook Best Practices

- **Block at commit-time, not mid-edit** — interrupting mid-plan degrades output quality.
- Use hooks for policy enforcement and observability.
- For command-level control, prefer **Rules** (execpolicy) over hooks.

---

## 12. MCP Servers

Codex CLI supports Model Context Protocol servers for connecting to external tools and services. It ships with built-in tools and you can add custom MCP servers.

### Adding MCP Servers

```bash
# Interactive setup
codex mcp add <name> <command-or-url>

# Or edit directly
# ~/.codex/config.toml
[[mcp_servers]]
name = "linear"
type = "stdio"
command = "npx"
args = ["-y", "@linear/mcp"]
```

Codex launches MCP servers automatically when a session starts and exposes their tools alongside built-ins.

### Running Codex as an MCP Server

```bash
codex mcp  # Runs Codex over stdio for consumption by other agents
```

This enables using Codex as a tool within the OpenAI Agents SDK or other MCP-compatible orchestrators.

### Plugins

Install community and custom plugins directly:

```
/plugin install owner/repo
```

Plugins can bundle MCP servers, skills, and app connectors as a single installable package.

---

## 13. Configuration

Codex reads configuration from `~/.codex/config.toml` (user-level) and `.codex/config.toml` (project-level, trusted projects only).

### Resolution Order (highest precedence first)

1. CLI flags (`-c key=value`, `--model`, etc.)
2. Project config: `.codex/config.toml` (closest to cwd wins; trusted projects only)
3. User config: `~/.codex/config.toml`
4. Built-in defaults

### Core Settings

```toml
# ~/.codex/config.toml

# Model selection
model = "gpt-5.4"                     # Recommended default
# model = "gpt-5.3-codex"             # Coding-specialized
# model = "gpt-5.3-codex-spark"       # Fast iteration (Pro only)

# Approval & Sandbox
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = false
writable_roots = []

# Web search
web_search = "cached"                  # "cached" | "live" | "disabled"

# Features
[features]
multi_agent = false
fast_mode = true
```

### Profiles

Save named configuration sets and switch between them:

```toml
[profiles.deep-review]
model = "gpt-5-pro"
model_reasoning_effort = "high"
approval_policy = "never"

[profiles.lightweight]
model = "gpt-4.1"
approval_policy = "untrusted"
```

```bash
codex --profile deep-review
```

Add `profile = "deep-review"` at the top level to make it the default.

### Custom Model Providers

```toml
model = "gpt-5.1"
model_provider = "proxy"

[model_providers.proxy]
name = "OpenAI via LLM proxy"
base_url = "http://proxy.example.com"
env_key = "OPENAI_API_KEY"

[model_providers.ollama]
name = "Ollama (local)"
base_url = "http://localhost:11434"
```

Use `--oss` flag to quickly switch to the local open-source provider (Ollama).

---

## 14. Useful Built-in Commands

| Command | What it does |
|---------|-------------|
| `/model` | Switch the active AI model or adjust reasoning levels |
| `/permissions` | Switch approval/sandbox presets (Auto, Read-only, Full Access) |
| `/compact` | Compresses session history to free context |
| `/clear` | Resets session context entirely, starts a fresh chat |
| `/status` | Shows model, approval policy, writable roots, token usage |
| `/statusline` | Customize the TUI footer status line |
| `/review` | Analyze code changes directly in the terminal |
| `/diff` | Review all session changes with syntax-highlighted diffs |
| `/copy` | Copy the latest completed output to clipboard |
| `/plan` | Enter plan mode — Codex asks questions and builds a structured plan |
| `/memory` | View and manage Codex memory |
| `/skills` | Browse available skills |
| `/agent` | Enable or manage multi-agent workflows |
| `/experimental` | Toggle experimental features |
| `/theme` | Choose from built-in themes (GitHub Dark, Light, colorblind variants) |
| `/fast` | Toggle between Fast and Standard service tiers |
| `/mcp` | View and manage MCP server connections |
| `/feedback` | Submit feedback, bug reports, or feature requests |
| `Shift+Tab` | Cycle between modes (if applicable) |
| `Ctrl+T` | Toggle reasoning visibility for extended thinking models |

---

## 15. Non-Interactive Mode (exec)

Use `codex exec` for scripted or CI-style runs:

```bash
# Simple task
codex exec "Run tests and fix failures"

# Machine-readable output
codex exec --json "Analyze codebase"

# Full automation (CI)
codex exec --ask-for-approval never --sandbox workspace-write "Run lint"

# Resume a previous exec session
codex exec resume --last "Fix the race conditions you found"

# Write output to file
codex exec --output result.md "Summarize changes"
```

### CI Integration Example

```bash
# In a CI pipeline (externally hardened environment only)
codex --dangerously-bypass-approvals-and-sandbox "Run unit tests"
```

---

## 16. Cross-Tool Portability — Claude Code & Copilot CLI

Codex CLI, Claude Code, and GitHub Copilot CLI have converged on shared open standards. The `AGENTS.md` standard is stewarded by the Agentic AI Foundation under the Linux Foundation.

### Instruction Files — What Each Tool Reads

| File | Codex CLI | Claude Code | Copilot CLI |
|------|:---------:|:-----------:|:-----------:|
| `AGENTS.md` (root + nested) | ✅ Primary | ✅ Read | ✅ Primary |
| `AGENTS.override.md` | ✅ Override layer | ❌ | ❌ |
| `CLAUDE.md` (root) | ❌ | ✅ Primary | ✅ Read |
| `.github/copilot-instructions.md` | ❌ | ✅ Read | ✅ Native |
| `~/.codex/AGENTS.md` | ✅ Global | ❌ | ❌ |
| `~/.claude/CLAUDE.md` | ❌ | ✅ Global | ❌ |

### Skills — What Each Tool Reads

| Path | Codex CLI | Claude Code | Copilot CLI |
|------|:---------:|:-----------:|:-----------:|
| `.agents/skills/<n>/SKILL.md` | ✅ Native | ❌ | ❌ |
| `.github/skills/<n>/SKILL.md` | ✅ | ✅ | ✅ |
| `.claude/skills/<n>/SKILL.md` | ❌ | ✅ Native | ✅ Read |
| `~/.codex/skills/<n>/SKILL.md` | ✅ Native | ❌ | ❌ |

### Recommended Multi-Tool Repository Layout

```
project/
├── AGENTS.md                        # Universal — all three tools read this
├── CLAUDE.md                        # Claude Code primary + Copilot CLI reads
├── .agents/
│   └── skills/                      # Codex native skill path
│       └── code-review/
│           └── SKILL.md
├── .github/
│   ├── copilot-instructions.md      # Copilot CLI native
│   ├── skills/                      # Universal skill path
│   │   └── shared-skill/
│   │       └── SKILL.md
│   └── hooks/
│       └── hooks.json               # Copilot CLI hooks
├── .codex/
│   ├── config.toml                  # Codex project config
│   └── rules/                       # Codex execpolicy rules
├── .claude/
│   ├── settings.json                # Claude Code hooks + permissions
│   └── commands/                    # Claude Code slash commands
└── src/
    └── api/
        └── AGENTS.md                # Universal scoped instructions
```

### Portability Best Practices

- **Put shared instructions in `AGENTS.md`** — this is the most universal instruction file across coding agents.
- **Put shared skills in `.github/skills/`** — all three tools read this path.
- **Use `AGENTS.override.md`** for Codex-specific local overrides.
- **Avoid duplicating instructions** across multiple files.
- **Test your instructions** with each tool you support — activation behavior and precedence rules differ.

---

## 17. Best Practices Summary

### Custom Instructions

- Keep instructions concise, structured, and conflict-free.
- Use `AGENTS.md` at the root for primary always-on guidance.
- Use `AGENTS.override.md` for temporary overrides.
- Layer global (`~/.codex/AGENTS.md`) + project instructions.
- Test by running `codex --ask-for-approval never "Summarize the current instructions."`.

### Project Structure

- Maintain a modular repo design with clear separation of concerns.
- Place directory-specific `AGENTS.md` files in submodules that need scoped context.
- Keep personal overrides in `~/.codex/` (not committed to git).

### Skills

- Use skills for reusable, task-specific AI workflows (code review, refactoring, debugging).
- Keep skill files modular, single-purpose, and under 500 lines.
- Declare MCP dependencies in `agents/openai.yaml`.
- Use `$` mentions in the composer for explicit skill invocation.
- Write descriptions with clear scope and boundaries for reliable implicit activation.

### Sandbox & Security

- Start with `workspace-write` sandbox and `on-request` approval for local development.
- Use **Rules** (execpolicy) for fine-grained command control instead of broadly expanding access.
- Reserve `danger-full-access` for externally hardened CI environments only.
- Enable network access only when explicitly needed.
- Mark untrusted projects so Codex skips project-scoped `.codex/` layers.

### Context & Session Management

- Use `/status` to check current configuration and token usage.
- Use `/clear` when switching tasks (free, no loss).
- Use `/compact` only when nearing the context limit (lossy).
- Let auto-compaction handle most context pressure automatically.
- Use `codex resume` to pick up previous sessions with full context.

### Multi-Agent Workflows

- Enable via `[features] multi_agent = true` for parallel task execution.
- Define agent roles with scoped models and sandbox settings.
- Sub-agents inherit the parent's sandbox policy by default.

### Documentation

- Document architecture decisions in `docs/decisions/`.
- Maintain runbooks in `docs/runbooks/`.
- Keep `docs/architecture.md` as the system-level overview.

---

## References

- <https://developers.openai.com/codex/cli/>
- <https://developers.openai.com/codex/cli/features/>
- <https://developers.openai.com/codex/cli/reference>
- <https://developers.openai.com/codex/cli/slash-commands/>
- <https://developers.openai.com/codex/guides/agents-md/>
- <https://developers.openai.com/codex/skills/>
- <https://developers.openai.com/codex/rules/>
- <https://developers.openai.com/codex/multi-agent/>
- <https://developers.openai.com/codex/config-basic/>
- <https://developers.openai.com/codex/config-advanced/>
- <https://developers.openai.com/codex/config-reference/>
- <https://developers.openai.com/codex/concepts/sandboxing/>
- <https://developers.openai.com/codex/agent-approvals-security/>
- <https://developers.openai.com/codex/models/>
- <https://github.com/openai/codex>

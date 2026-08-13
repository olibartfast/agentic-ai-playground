# OpenAI Codex CLI — Architecture, Rules, and Best Practices

---

## 1. Project Overview

A modular repository structure for building Codex CLI projects with structured AI context, reusable skills, and automated development workflows. Codex CLI is OpenAI’s open-source coding agent written in Rust. It can read, edit, and execute code locally within a selected workspace directory.

### Installation

```bash
npm i -g @openai/codex
# or
brew install --cask codex
````

Authenticate with your ChatGPT account (Plus, Pro, Business, Edu, or Enterprise) or an API key:

```bash
codex login                    # Browser-based ChatGPT OAuth
codex login --device-code      # Device code flow (headless)
printenv OPENAI_API_KEY | codex login --with-api-key  # API key via stdin
```

### Recommended Repository Layout

```text
codex_project/
├── AGENTS.md                # Primary always-on instructions — committed, shared with team
├── AGENTS.override.md       # Local override layer — git-ignored
├── .codex/                  # Codex CLI project configuration
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

## 2. Custom Instructions and AGENTS.md

`AGENTS.md` is Codex’s persistent instruction file. It is loaded at the start of every session before your first prompt. Codex builds an instruction chain by walking from the global scope down to your current working directory. Files closer to your working directory override earlier guidance because they appear later in the combined prompt.

### Instruction Discovery Order

In each directory, Codex searches for instruction files in this order:

`AGENTS.override.md` → `AGENTS.md` → configured fallback filenames

It includes at most one file per directory and concatenates them from root to leaf, joining them with blank lines.

### File Hierarchy

| File                           | Scope                                                                          |
| ------------------------------ | ------------------------------------------------------------------------------ |
| `~/.codex/AGENTS.override.md`  | **Global override** — temporary global override without deleting the base file |
| `~/.codex/AGENTS.md`           | **Global** — applies to all projects                                           |
| `<project>/AGENTS.override.md` | **Project override** — local override layer (git-ignored)                      |
| `<project>/AGENTS.md`          | **Project** — committed to git and shared with the team                        |
| `<project>/<subdir>/AGENTS.md` | **Directory-specific** — scoped context for submodules                         |

### Configuration Knobs

```toml
# ~/.codex/config.toml
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
project_doc_max_bytes = 65536  # Default: 32768 (32 KiB)
```

* **`project_doc_max_bytes`** — maximum combined size of instruction files before truncation. Raise the limit or split instructions across nested directories when you hit the cap.
* **`project_doc_fallback_filenames`** — additional filenames to try when `AGENTS.md` is missing at a directory level.

### Cross-Tool Compatibility

For interoperability, some repositories also include files such as `CLAUDE.md` and `.github/copilot-instructions.md`. `AGENTS.md` remains the primary instruction source for Codex.

### AGENTS.md Best Practices

* **Keep instructions concise and actionable.** Focus on what Codex would likely get wrong without guidance.
* **Use `AGENTS.override.md`** for temporary overrides without deleting the base file.
* **Layer global and project instructions.** Put personal working agreements in `~/.codex/AGENTS.md` and repository norms in the project root.
* **Avoid conflicts** between instruction files. When instructions conflict, Codex behavior becomes non-deterministic.
* **Test your instructions** by running:

```bash
codex --ask-for-approval never "Summarize the current instructions."
```

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

Codex includes a persistent memory system that builds understanding of your codebase and preferences across sessions. It stores conventions, patterns, and preferences it infers while working.

* Reduces the need to repeat context in every prompt
* Automatically makes future sessions more productive
* Managed via the `/memory` command
* Workspace-scoped writes ensure stored memories remain relevant to the current project
* Use `codex debug clear-memories` to fully reset saved memory state

---

## 4. `@` File References and Inline Shortcuts

Type `@` in the composer to open a fuzzy file search rooted at the workspace. Press Tab or Enter to insert the highlighted path into your message.

```text
@src/pipeline.py
@docs/architecture.md
```

Additional composer shortcuts:

* **`Enter`** while Codex is running — inject new instructions into the current turn
* **`Tab`** while Codex is running — queue a follow-up prompt for the next turn
* **`!command`** — run a local shell command (for example, `!ls`); output is treated as user-provided context
* **`Esc Esc`** on an empty composer — edit your previous message; keep pressing to walk further back
* **`Ctrl+G`** — open an external editor (`$VISUAL` or `$EDITOR`) for longer prompts

---

## 5. Context and Session Management

| Command    | What it does                                                                                                                                                            |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/compact` | Compresses conversation history to free context window space. Instruction files survive because they are reloaded. Lossy — use only when approaching the context limit. |
| `/clear`   | Resets session context entirely and starts a fresh chat.                                                                                                                |
| `Ctrl+L`   | Clears the terminal view without starting a new conversation.                                                                                                           |
| `/context` | Shows context window usage breakdown.                                                                                                                                   |
| `/status`  | Shows active model, approval policy, writable roots, and token usage.                                                                                                   |

### Auto-Compaction

When a conversation approaches 95% of the token limit, Codex automatically compresses history in the background. You can configure the threshold with `auto_compact_threshold` in `config.toml`.

### Session Resume

Codex stores transcripts locally so you can continue previous work:

```bash
codex resume                # Opens a picker of recent sessions
codex resume --last         # Resumes the most recent session from the current directory
codex resume --all          # Shows sessions beyond the current working directory
codex resume <SESSION_ID>   # Targets a specific session
```

Each resumed run keeps the original transcript, plan history, and approvals.

### Session Fork

Fork a previous session into a new thread while preserving the original transcript:

```bash
codex fork                  # Opens session picker
codex fork --last           # Forks the most recent session
```

---

## 6. Modes of Use

Codex CLI supports several execution modes depending on the level of automation required.

| Mode                       | How to use                                  | When                                                                     |
| -------------------------- | ------------------------------------------- | ------------------------------------------------------------------------ |
| **Interactive (TUI)**      | `codex`                                     | Default. Conversational back-and-forth with the full-screen terminal UI. |
| **Non-interactive (exec)** | `codex exec "prompt"` or `codex e "prompt"` | Single-shot, headless execution. Streams to stdout or JSONL.             |
| **Full Auto**              | `codex --full-auto "prompt"`                | Low-friction preset: `workspace-write` sandbox + `on-request` approvals. |
| **MCP Server**             | `codex mcp`                                 | Runs Codex as an MCP server over stdio for consumption by other agents.  |
| **Codex Cloud**            | `codex cloud-tasks`                         | Launch and manage Codex Cloud tasks from the terminal.                   |

### Quick One-Shot Execution

```bash
codex exec "Run tests and fix failures"
codex exec --json "Summarize this repo"     # Machine-readable JSONL output
codex exec --output result.md "..."         # Write final message to file
```

---

## 7. Sandbox and Approval System

Codex uses two layers of security:

* **Sandbox mode** — controls what Codex can do technically, including filesystem and network access
* **Approval policy** — controls when Codex must ask before acting

### Sandbox Modes

| Mode                 | Behavior                                                                                            |
| -------------------- | --------------------------------------------------------------------------------------------------- |
| `read-only`          | Default. Codex can browse files but will not make changes or run commands without approval.         |
| `workspace-write`    | Codex can read, edit within the workspace, and run routine commands. Network is blocked by default. |
| `danger-full-access` | No sandbox restrictions. Use only in externally hardened or isolated environments.                  |

### Approval Policies

| Policy       | Behavior                                                              |
| ------------ | --------------------------------------------------------------------- |
| `untrusted`  | Only known-safe read-only commands auto-run; everything else prompts. |
| `on-request` | Default for interactive sessions. The model decides when to ask.      |
| `never`      | Never prompt. Risky — use only in isolated or CI environments.        |

### Configuration

```toml
# ~/.codex/config.toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = false
writable_roots = ["/path/to/extra/dir"]
```

### Command-Line Overrides

```bash
codex --full-auto "Run tests"                                 # workspace-write + on-request
codex --sandbox workspace-write "Fix bug"                     # Explicit sandbox mode
codex --ask-for-approval never "Deploy"                       # No prompts (risky)
codex --dangerously-bypass-approvals-and-sandbox "Deploy"     # --yolo alias. CI only.
```

### Permission Control in Session

Use `/permissions` inside an interactive session to switch modes:

* **Auto** — read, edit, and run commands in the working directory
* **Read-only** — browse files without changing or executing
* **Full Access** — machine-wide access including network; use sparingly

---

## 8. Rules (Execpolicy)

Rules provide fine-grained, per-command control over what Codex can execute. They are defined in `.rules` files under `~/.codex/rules/` or `.codex/rules/`.

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

* **`allow`** — run without prompting
* **`prompt`** — ask for confirmation
* **`forbidden`** — block entirely

When multiple rules match, the most restrictive decision wins:

`forbidden > prompt > allow`

### Testing Rules

```bash
codex execpolicy check --pretty \
    --rules ~/.codex/rules/default.rules \
    -- gh pr view 7888
```

---

## 9. Skills

Skills are self-contained folders of instructions, scripts, and resources that Codex loads when relevant. They are portable across Codex CLI, the IDE extension, and the Codex app.

### Key Difference from AGENTS.md

* **`AGENTS.md`** — always on, loaded every session
* **Skills** — loaded on demand when Codex recognizes that the task matches the skill description

### Invocation

* **Explicit** — type `$` in the composer to mention a skill, or use `/skills` to browse
* **Implicit** — Codex automatically selects a skill when the task matches its description

### Directory Locations

| Path                            | Scope                                                                                                |
| ------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `.agents/skills/<skill-name>/`  | Repository-scoped; every directory from the current working directory up to the repo root is scanned |
| `.github/skills/<skill-name>/`  | Repository-scoped; cross-compatible with Copilot CLI and Claude Code                                 |
| `~/.codex/skills/<skill-name>/` | User-scoped; available across all projects                                                           |

### Anatomy of a `SKILL.md`

Each skill is a folder containing a `SKILL.md` file and optional bundled resources. `SKILL.md` has two parts:

* **YAML frontmatter** — metadata for discovery
* **Markdown body** — instructions loaded when the skill is activated

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

* **`name`** — required; unique identifier, lowercase with hyphens. It becomes a slash command.
* **`description`** — required; critical for activation. Codex reads all skill descriptions at startup. Be specific about trigger phrases. Slightly “pushy” descriptions tend to activate more reliably.

#### Optional: `agents/openai.yaml`

Add `agents/openai.yaml` alongside `SKILL.md` to configure UI metadata in the Codex app, set invocation policy, and declare tool dependencies.

#### Markdown Body

After the frontmatter, write instructions in standard Markdown.

**Reference-style skills** add conventions Codex applies during ongoing work:

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

**Task-style skills** provide step-by-step instructions for a specific action:

```markdown
---
name: code-review
description: >
  Comprehensive code review. Use when reviewing PRs or code changes.
---
When reviewing code:

1. Check for bugs: identify runtime errors, edge cases, and logic flaws.
2. Verify style: ensure code follows team conventions.
3. Evaluate architecture: flag violations of established patterns.
4. Perform a security scan: look for injection, hardcoded secrets, and unsafe deserialization.
5. Suggest improvements: propose simplifications, extractions, and performance gains.
6. Summarize findings: produce a structured report with severity levels.
```

### Bundled Resources (Optional)

```text
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

At startup, only the skill frontmatter is loaded. When a skill is activated, `SKILL.md` is loaded. Bundled resources are read only when referenced by the instructions. This keeps the context window lean while making deeper resources available when needed.

### Installing Skills

Use the built-in installer to install community skills:

```text
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

### `SKILL.md` Authoring Best Practices

* **Keep `SKILL.md` under 500 lines or 5,000 tokens.** Move detailed material to `references/`.
* **Use active, directive language.**
* **Break complex tasks into numbered steps.**
* **Include examples.** Examples dramatically improve activation rates.
* **Specify output formats** so Codex knows exactly what to produce.
* **Define scope boundaries** with an explicit “Out of Scope” section.
* **Add conditional logic** when behavior should branch by language or file type.
* **Link to bundled resources** using relative paths such as `references/STYLE_GUIDE.md`.
* **Declare MCP dependencies** in `agents/openai.yaml` so Codex can install and wire them automatically.

---

## 10. Multi-Agent Workflows

Codex can spawn specialized agents in parallel and collect their results. This is useful for highly parallel work such as codebase exploration, design reviews, or feature planning.

### Enabling

```toml
# ~/.codex/config.toml
[features]
multi_agent = true
```

You can also enable it through `/experimental` in the TUI.

### Agent Roles

Define roles in the `[agents]` section of `config.toml`:

```toml
[agents.reviewer]
description = "Find correctness, security, and test risks in code."
config_file = "./agents/reviewer.toml"  # Relative to config.toml
nickname_candidates = ["Athena", "Ada"]
```

Each role can override the default model, sandbox policy, and approval settings through its own `config_file`.

### Usage Example

```text
I would like to review the following points on the current PR.
Spawn one agent per point, wait for all to complete, and summarize the result:
1. Code correctness
2. Security vulnerabilities
3. Test coverage gaps
```

### CSV Fan-Out

For batch processing, Codex can fan work across agents using `spawn_agents_on_csv`. The exported CSV includes the original row data plus job metadata.

### Key Details

* Sub-agents inherit the current sandbox policy
* Approval requests from inactive agent threads surface in the main thread
* `agents.max_concurrent_agents` defaults to 6
* `agents.max_agent_depth` defaults to 1

---

## 11. Hooks (Experimental)

Hooks are shell commands that execute automatically at key points in Codex’s lifecycle. Use hooks for deterministic controls that should not depend on the model “remembering.”

### Hook Events

* **`SessionStart`** — fires when a session begins
* **`SessionStop`** — fires when a session ends

### Configuration

Hooks are configured as an experimental feature. The hooks engine is still evolving, so check the changelog for current capabilities.

### Example Use Cases

* Enforce commit-message policies
* Run security or environment checks at session start
* Log session metadata for auditing

### Hook Best Practices

* **Block at commit time, not mid-edit** — interrupting a plan in progress can degrade output quality
* Use hooks for policy enforcement and observability
* For command-level control, prefer **Rules** (execpolicy) over hooks

---

## 12. MCP Servers

Codex CLI supports Model Context Protocol (MCP) servers for connecting to external tools and services. It ships with built-in tools, and you can add custom MCP servers.

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

Codex automatically launches configured MCP servers when a session starts and exposes their tools alongside built-ins.

### Running Codex as an MCP Server

```bash
codex mcp
```

This runs Codex over stdio so it can be consumed by other agents or orchestrators.

### Plugins

Install community and custom plugins directly:

```text
/plugin install owner/repo
```

Plugins can bundle MCP servers, skills, and app connectors into a single installable package.

---

## 13. Configuration

Codex reads configuration from `~/.codex/config.toml` at the user level and `.codex/config.toml` at the project level for trusted projects.

### Resolution Order (Highest Precedence First)

1. CLI flags (`-c key=value`, `--model`, and so on)
2. Project config: `.codex/config.toml` (closest to the current working directory wins; trusted projects only)
3. User config: `~/.codex/config.toml`
4. Built-in defaults

### Core Settings

```toml
# ~/.codex/config.toml

# Model selection
model = "gpt-5.4"                     # Recommended default
# model = "gpt-5.3-codex"             # Coding-specialized
# model = "gpt-5.3-codex-spark"       # Fast iteration (Pro only)

# Approval and Sandbox
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

Use the `--oss` flag to quickly switch to a local open-source provider such as Ollama.

---

## 14. Useful Built-In Commands

| Command         | What it does                                                       |
| --------------- | ------------------------------------------------------------------ |
| `/model`        | Switch the active AI model or adjust reasoning levels              |
| `/permissions`  | Switch approval and sandbox presets                                |
| `/compact`      | Compress session history to free context                           |
| `/clear`        | Reset session context entirely and start fresh                     |
| `/status`       | Show model, approval policy, writable roots, and token usage       |
| `/statusline`   | Customize the TUI footer status line                               |
| `/review`       | Analyze code changes directly in the terminal                      |
| `/diff`         | Review all session changes with syntax-highlighted diffs           |
| `/copy`         | Copy the latest completed output to the clipboard                  |
| `/plan`         | Enter plan mode; Codex asks questions and builds a structured plan |
| `/memory`       | View and manage Codex memory                                       |
| `/skills`       | Browse available skills                                            |
| `/agent`        | Enable or manage multi-agent workflows                             |
| `/experimental` | Toggle experimental features                                       |
| `/theme`        | Choose from built-in themes                                        |
| `/fast`         | Toggle between Fast and Standard service tiers                     |
| `/mcp`          | View and manage MCP server connections                             |
| `/feedback`     | Submit feedback, bug reports, or feature requests                  |
| `Shift+Tab`     | Cycle between modes, when applicable                               |
| `Ctrl+T`        | Toggle reasoning visibility for extended-thinking models           |

---

## 15. Non-Interactive Mode (`exec`)

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

## 16. Cross-Tool Portability — Claude Code and Copilot CLI

Codex CLI, Claude Code, and GitHub Copilot CLI are converging on similar conventions for instruction files and skill packaging. `AGENTS.md` is emerging as a cross-tool standard for agent instruction files.

### Instruction Files — What Each Tool Reads

| File                              |       Codex CLI       | Claude Code | Copilot CLI |
| --------------------------------- | :-------------------: | :---------: | :---------: |
| `AGENTS.md` (root + nested)       |       ✅ Primary       |    ✅ Read   |  ✅ Primary  |
| `AGENTS.override.md`              |    ✅ Override layer   |      ❌      |      ❌      |
| `CLAUDE.md` (root)                | Interoperability only |  ✅ Primary  |    ✅ Read   |
| `.github/copilot-instructions.md` | Interoperability only |    ✅ Read   |   ✅ Native  |
| `~/.codex/AGENTS.md`              |        ✅ Global       |      ❌      |      ❌      |
| `~/.claude/CLAUDE.md`             |           ❌           |   ✅ Global  |      ❌      |

### Skills — What Each Tool Reads

| Path                           | Codex CLI | Claude Code | Copilot CLI |
| ------------------------------ | :-------: | :---------: | :---------: |
| `.agents/skills/<n>/SKILL.md`  |  ✅ Native |      ❌      |      ❌      |
| `.github/skills/<n>/SKILL.md`  |     ✅     |      ✅      |      ✅      |
| `.claude/skills/<n>/SKILL.md`  |     ❌     |   ✅ Native  |    ✅ Read   |
| `~/.codex/skills/<n>/SKILL.md` |  ✅ Native |      ❌      |      ❌      |

### Recommended Multi-Tool Repository Layout

```text
project/
├── AGENTS.md                        # Universal — all three tools read this
├── CLAUDE.md                        # Claude Code primary; readable by others
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
│   ├── settings.json                # Claude Code hooks and permissions
│   └── commands/                    # Claude Code slash commands
└── src/
    └── api/
        └── AGENTS.md                # Universal scoped instructions
```

### Portability Best Practices

* **Put shared instructions in `AGENTS.md`**
* **Put shared skills in `.github/skills/`**
* **Use `AGENTS.override.md`** for Codex-specific local overrides
* **Avoid duplicating instructions** across multiple files
* **Test your instruction layout** with every tool you support, because precedence and activation behavior differ

---

## 17. Common Pitfalls

### Instruction Conflicts

Avoid conflicting guidance across multiple `AGENTS.md` files. When conflicts occur, model behavior becomes non-deterministic.

### Overly Large Instruction Files

Large instruction files consume useful context window space. Prefer hierarchical instruction files over a single oversized root file.

### Skill Overlap

Avoid creating multiple skills that trigger on the same phrases, as this can lead to ambiguous or unstable activation.

### Excessive Privileges

Do not default to `danger-full-access` or `approval_policy = "never"` during normal development. Expand permissions only when justified.

---

## 18. Best Practices Summary

### Custom Instructions

* Keep instructions concise, structured, and conflict-free
* Use `AGENTS.md` at the root for primary always-on guidance
* Use `AGENTS.override.md` for temporary overrides
* Layer global (`~/.codex/AGENTS.md`) and project instructions
* Test instructions with `codex --ask-for-approval never "Summarize the current instructions."`

### Project Structure

* Maintain a modular repository design with clear separation of concerns
* Place directory-specific `AGENTS.md` files in submodules that need scoped context
* Keep personal overrides in `~/.codex/` and out of version control

### Skills

* Use skills for reusable, task-specific workflows such as code review, refactoring, or debugging
* Keep skill files modular, single-purpose, and under 500 lines
* Declare MCP dependencies in `agents/openai.yaml`
* Use `$` mentions in the composer for explicit invocation
* Write descriptions with clear scope and boundaries

### Sandbox and Security

* Start with `workspace-write` sandbox and `on-request` approval for local development
* Use **Rules** (execpolicy) for fine-grained command control
* Reserve `danger-full-access` for externally hardened CI environments only
* Enable network access only when explicitly needed
* Mark untrusted projects so Codex skips project-scoped `.codex/` layers

### Context and Session Management

* Use `/status` to check current configuration and token usage
* Use `/clear` when switching tasks
* Use `/compact` only when nearing the context limit
* Let automatic compaction handle most context pressure
* Use `codex resume` to continue previous sessions with full context

### Multi-Agent Workflows

* Enable via `[features] multi_agent = true` when parallel task execution is useful
* Define agent roles with scoped models and sandbox settings
* Sub-agents inherit the parent sandbox policy by default

### Documentation

* Document architecture decisions in `docs/decisions/`
* Maintain runbooks in `docs/runbooks/`
* Keep `docs/architecture.md` as the top-level system overview

---

## 19. Official References

* [https://developers.openai.com/codex/cli/](https://developers.openai.com/codex/cli/)
* [https://developers.openai.com/codex/cli/features/](https://developers.openai.com/codex/cli/features/)
* [https://developers.openai.com/codex/cli/reference](https://developers.openai.com/codex/cli/reference)
* [https://developers.openai.com/codex/cli/slash-commands/](https://developers.openai.com/codex/cli/slash-commands/)
* [https://developers.openai.com/codex/guides/agents-md/](https://developers.openai.com/codex/guides/agents-md/)
* [https://developers.openai.com/codex/skills/](https://developers.openai.com/codex/skills/)
* [https://developers.openai.com/codex/rules/](https://developers.openai.com/codex/rules/)
* [https://developers.openai.com/codex/multi-agent/](https://developers.openai.com/codex/multi-agent/)
* [https://developers.openai.com/codex/config-basic/](https://developers.openai.com/codex/config-basic/)
* [https://developers.openai.com/codex/config-advanced/](https://developers.openai.com/codex/config-advanced/)
* [https://developers.openai.com/codex/config-reference/](https://developers.openai.com/codex/config-reference/)
* [https://developers.openai.com/codex/concepts/sandboxing/](https://developers.openai.com/codex/concepts/sandboxing/)
* [https://developers.openai.com/codex/agent-approvals-security/](https://developers.openai.com/codex/agent-approvals-security/)
* [https://developers.openai.com/codex/models/](https://developers.openai.com/codex/models/)
* [https://github.com/openai/codex](https://github.com/openai/codex)
* [https://agents.md](https://agents.md)


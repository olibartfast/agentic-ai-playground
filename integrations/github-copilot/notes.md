# GitHub Copilot CLI — Rules & Best Practices

---

## 1. Project Overview

A modular repository structure designed for building Copilot CLI projects with structured AI context, reusable skills, custom agents, and automated development workflows.

### Recommended Repository Layout

```
copilot_cli_project/
├── AGENTS.md                    # Primary always-on instructions — committed, shared with team
├── .github/
│   ├── copilot-instructions.md  # Repository-wide custom instructions
│   ├── instructions/            # Path-specific instructions (*.instructions.md)
│   ├── agents/                  # Custom agent profiles (*.agent.md)
│   ├── skills/                  # Agent skills (SKILL.md per folder)
│   │   ├── code-review/
│   │   │   └── SKILL.md
│   │   ├── refactor/
│   │   │   └── SKILL.md
│   │   └── release/
│   │       └── SKILL.md
│   └── hooks/                   # Lifecycle hooks (hooks.json)
│       └── hooks.json
├── README.md
├── docs/
│   ├── architecture.md
│   ├── decisions/
│   └── runbooks/
└── src/
    ├── api/
    │   └── AGENTS.md            # Directory-specific instructions
    └── persistence/
        └── AGENTS.md            # Directory-specific instructions
```

---

## 2. Custom Instructions & Memory

Custom instructions are persistent guidance loaded at the start of every session before your first prompt. All instruction sources combine; more-specific files take higher priority.

### Instruction File Hierarchy

| File | Scope |
|------|-------|
| `$HOME/.copilot/copilot-instructions.md` | **Global** — applies to all projects |
| `<repo>/.github/copilot-instructions.md` | **Repository-wide** — committed to git, shared with team |
| `<repo>/.github/instructions/**/*.instructions.md` | **Path-specific** — scoped via `applyTo` frontmatter |
| `<repo>/AGENTS.md` (root) | **Primary always-on** — highest weight, shared across agents |
| `<repo>/<subdir>/AGENTS.md` | **Directory-specific** — additional context for submodules |
| `<repo>/GEMINI.md` | **Cross-compatible** — read from Gemini ecosystem, must be at repo root |
| `<repo>/CLAUDE.md` | **Cross-compatible** — read from Claude Code ecosystem, must be at repo root |

Also supported: `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` environment variable — comma-separated list of directories where Copilot will look for `AGENTS.md` and `*.instructions.md` files.

### Custom Instructions Best Practices

- **Keep instructions concise and actionable.** Lengthy instructions dilute effectiveness.
- **Use `.github/copilot-instructions.md`** for repo-wide norms: build commands, coding standards, test/lint conventions.
- **Use path-specific `*.instructions.md`** with `applyTo` frontmatter for language- or directory-specific rules (e.g., enforce C# conventions only on `*.cs` files).
- **Use `AGENTS.md`** for cross-agent instructions that should always apply. Root `AGENTS.md` is treated as primary; nested ones as additional.
- **Avoid conflicts** between instruction files — Copilot's choice between conflicting instructions is non-deterministic.
- **`/init`** generates a starter instructions file based on your project structure. Review and trim the output.
- **`--no-custom-instructions`** flag disables all instruction loading for a session if needed.

### Path-Specific Instructions Example

```markdown
<!-- .github/instructions/csharp.instructions.md -->
---
applyTo: "**/*.cs"
---
- Use `var` only when the type is obvious from the right side
- Prefer expression-bodied members for single-line methods
- Always include XML documentation on public APIs
```

### Copilot Memory

A persistent memory system that builds understanding of your codebase across sessions. Copilot stores "memories" — coding conventions, patterns, and preferences it deduces while working.

- Reduces the need to repeat context in every prompt
- Automatically makes future sessions more productive
- Managed via the `/memory` command
- Can be toggled on/off per session

---

## 3. `@` File References

Prefix any file or directory path with `@` to pull its contents into the current context.

```
@src/pipeline.py
@docs/architecture.md
```

- Works in prompts to inject file contents directly.
- Supports image paths for UI/design tasks.
- Copilot auto-loads any instruction files (AGENTS.md, etc.) present in the referenced path.

---

## 4. Context & Session Management

| Command | What it does |
|---------|-------------|
| `/compact` | Compresses conversation history to free context window space. Instruction files survive (re-loaded). Lossy — use only when nearing the limit. |
| `/clear` or `/new` | Resets session context entirely. Free, no loss. Use between unrelated tasks. |
| `/context` | Shows detailed token usage breakdown — how your context window is being used. |
| `/usage` | View session statistics. |

### Auto-Compaction

When your conversation approaches 95% of the token limit, Copilot automatically compresses history in the background without interrupting your workflow. This enables virtually infinite sessions.

---

## 5. Modes of Use

Copilot CLI has three interaction modes:

| Mode | How to use | When |
|------|-----------|------|
| **Interactive** | `copilot` | Default. Conversational back-and-forth. |
| **Plan** | `Shift+Tab` to toggle | Copilot asks clarifying questions, builds structured plan before writing code. |
| **Autopilot** | `Shift+Tab` again (experimental) | Copilot works autonomously until task completion. |
| **Programmatic** | `copilot -p "prompt"` | Single-shot, headless execution. Combine with `--allow-tool`. |

### Plan Mode Best Practice

Use Plan mode for complex, multi-step tasks. Copilot asks follow-up questions, confirms assumptions, and produces a structured plan you can review before implementation begins. This catches misunderstandings early.

```
copilot
> /plan Migrate all class components to functional components with hooks
# Answer Copilot's questions, review the plan, then:
> Implement this plan
```

---

## 6. Hooks

Shell commands that execute automatically at key points in Copilot's agent lifecycle. Use hooks for deterministic control — things that shouldn't rely on the model "remembering."

### Hook Events

- **`preToolUse`** — runs before any tool execution (validation, blocking, argument sanitization)
- **`postToolUse`** — runs after tool execution (linting, logging, testing)
- **`sessionStart`** / **`sessionEnd`** — fires at session boundaries (setup, cleanup, archiving)

### Configuration

Defined in `.github/hooks/hooks.json` (repository-level) or `~/.copilot/hooks/` (personal). Must be on the repository's default branch for coding agent use. For CLI, hooks load from the current working directory.

```json
{
  "hooks": [
    {
      "event": "preToolUse",
      "scripts": ["./hooks/validate-tool.sh"],
      "description": "Block edits to protected paths"
    },
    {
      "event": "postToolUse",
      "scripts": ["./hooks/run-lint.sh"],
      "description": "Auto-lint after file changes"
    }
  ]
}
```

### Hook Best Practices

- **Block at commit-time, not mid-edit** — interrupting mid-plan degrades output quality.
- Use `preToolUse` hooks for policy enforcement: block dangerous commands, restrict file access, require ticket IDs for edits to protected paths.
- Use `postToolUse` hooks for observability: logging, audit trails, auto-formatting.
- Test hooks locally by piping test input: `echo '{"toolName":"bash","toolArgs":"{\"command\":\"ls\"}"}' | ./my-hook.sh`

---

## 7. Custom Agents

Custom agents are specialized versions of Copilot defined in Markdown files (`.agent.md`). They specify expertise, allowed tools, MCP servers, and instructions.

### Key Concepts

- **Agents** are named personas for complex workflows (e.g., "security-reviewer", "api-architect")
- **Subagents** — Copilot can delegate tasks to subsidiary agent processes with specific expertise
- **Handoffs** — chain agents into guided workflows (Plan → Implement → Review)
- **Built-in agents** — Copilot CLI ships with default agents for common tasks (Explore, Task)

### Directory Locations

| Path | Scope |
|------|-------|
| `.github/agents/` | Repository-scoped, shared via git |
| `~/.copilot/agents/` | User-scoped, all projects |
| Organization-level | Shared across all repos in org (Business/Enterprise) |

Naming conflicts: system-level overrides repository-level, which overrides organization-level.

### Agent Profile Example (`.github/agents/security-reviewer.agent.md`)

```markdown
---
mode: agent
tools: ['search/codebase', 'read/problems']
description: Reviews code for security vulnerabilities, never edits files.
---
# Security Reviewer

You are a senior security engineer. Analyze code for:
1. Injection vulnerabilities (SQL, command, XSS)
2. Hardcoded secrets or credentials
3. Unsafe deserialization
4. Missing input validation

Output a structured report with severity levels (critical / high / medium / low).
Never modify files — only report findings.
```

### Invoking Agents

```bash
# Via slash command in interactive mode
copilot
> /security-reviewer

# Via command line
copilot --agent=security-reviewer --prompt "Review the auth module"

# Copilot auto-infers the agent from your prompt context
```

---

## 8. Agent Skills

Skills are self-contained folders of instructions, scripts, and resources that Copilot loads when relevant. They're portable across Copilot CLI, VS Code, and the coding agent.

### Key Difference from Custom Instructions

- **Custom Instructions** — always-on, loaded every session
- **Skills** — loaded on demand when Copilot recognizes the task matches the skill's description

### Directory Locations

| Path | Scope |
|------|-------|
| `.github/skills/<skill-name>/` | Project-scoped, shared via git |
| `.claude/skills/<skill-name>/` | Project-scoped — cross-compatible with Claude Code |
| `~/.copilot/skills/<skill-name>/` | User-scoped, all projects |
| `~/.claude/skills/<skill-name>/` | User-scoped — cross-compatible with Claude Code |

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
- **`description`** (required) — critical for activation. Copilot reads all skill descriptions at startup (~100 tokens each) to decide which to load. Be specific about trigger phrases. Slightly "pushy" descriptions activate more reliably.
- **`license`** (optional) — license info for the skill.

#### Markdown Body

After frontmatter, write instructions in standard Markdown. Two categories:

**Reference-style skills** — add conventions Copilot applies to ongoing work:

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
├── scripts/              # Executable code Copilot runs via shell
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

### SKILL.md Authoring Best Practices

- **Keep `SKILL.md` under 500 lines / 5,000 tokens.** Move detailed docs to `references/`.
- **Use active, directive language** — tell Copilot what to do, not what might happen.
- **Break complex tasks into numbered steps** — sequential structure improves reliability.
- **Include examples** — concrete input/output pairs dramatically improve activation and quality (activation rates jump from ~50% to ~90%).
- **Specify output formats** — show Copilot exactly what the output should look like.
- **Define scope boundaries** — include "Out of Scope" so Copilot knows when NOT to use the skill.
- **Add conditional logic** — handle branching ("If `.py`, run ruff; if `.ts`, run eslint").
- **Link to bundled resources** — use relative paths like `See [STYLE_GUIDE.md](references/STYLE_GUIDE.md)`.
- **Test across models** — what works for Opus may need more detail for Sonnet or GPT-5.

---

## 9. MCP Servers

Copilot CLI ships with GitHub's MCP server built in and supports custom MCP servers for connecting to external tools and services.

### Built-in GitHub MCP Server

Provides access to GitHub.com resources: issues, pull requests, repositories, Actions workflows, Copilot Spaces.

### Adding Custom MCP Servers

```bash
# Interactive setup
copilot
> /mcp
# Follow prompts to add a server

# Or edit directly
~/.copilot/mcp-config.json
```

MCP server config location can be changed via `COPILOT_HOME` environment variable. Also reads from `.devcontainer/devcontainer.json`.

### Plugins

Install community and custom plugins directly from GitHub repositories:

```
/plugin install owner/repo
```

Plugins can bundle MCP servers, agents, skills, and hooks as a single installable package.

---

## 10. Tool Permissions & Security

### Trusted Directories

On first launch in a directory, Copilot asks you to confirm trust. Only launch from directories you trust — Copilot can read, modify, and execute files within.

- Trust for current session only, or permanently
- Edit trusted dirs in `~/.copilot/config.json` → `trusted_folders` array

### Tool Approval

When Copilot needs a tool that modifies or executes files, it asks permission:

1. **Yes** — allow this one time
2. **Yes, and approve for session** — allow this tool freely until session ends
3. **No (Esc)** — cancel and provide alternative instructions

### Command-Line Approval Flags

| Flag | Effect |
|------|--------|
| `--allow-all-tools` | Allow everything without asking |
| `--allow-tool 'shell(git)'` | Allow a specific tool |
| `--deny-tool 'shell(rm)'` | Block a specific tool (overrides allow) |

Combine them:

```bash
copilot --allow-all-tools --deny-tool 'shell(rm)' --deny-tool 'shell(git push)'
```

---

## 11. Useful Built-in Commands

| Command | What it does |
|---------|-------------|
| `/init` | Generates starter custom instructions for the current project |
| `/compact` | Compresses session history to free context |
| `/clear` or `/new` | Resets session context entirely |
| `/memory` | View and manage Copilot Memory |
| `/model` | Switch the active AI model |
| `/review` | Analyze code changes directly in the terminal |
| `/diff` | Review all session changes with syntax-highlighted inline diffs |
| `/mcp` | View and manage MCP server connections |
| `/context` | Shows context window usage breakdown |
| `/usage` | View session statistics |
| `/theme` | Choose from built-in themes (GitHub Dark, Light, colorblind variants) |
| `/feedback` | Submit feedback, bug reports, or feature requests |
| `/experimental` | Toggle experimental features |
| `/plugin` | Install or manage plugins |
| `Shift+Tab` | Cycle between modes (Ask → Plan → Autopilot) |
| `Ctrl+T` | Toggle reasoning visibility for extended thinking models |

---

## 12. Cross-Tool Portability — Claude Code, Codex CLI & Others

GitHub Copilot CLI, Anthropic Claude Code, and OpenAI Codex CLI have converged on shared open standards for agent instructions and skills. This means a single repository can serve all three tools with minimal duplication. This section maps what each tool reads and where the overlap is.

### The AGENTS.md Open Standard

`AGENTS.md` is a shared, vendor-neutral format for guiding coding agents. It is stewarded by the [Agentic AI Foundation](https://agents.md) under the Linux Foundation. Adopters include Copilot CLI, Codex CLI, Cursor, Amp, Jules (Google), and Factory.

All three major CLI tools read `AGENTS.md` at the repo root as their primary instruction source. Nested `AGENTS.md` files in subdirectories provide scoped overrides.

### Instruction Files — What Each Tool Reads

| File | Copilot CLI | Claude Code | Codex CLI |
|------|:-----------:|:-----------:|:---------:|
| `AGENTS.md` (root + nested) | ✅ Primary | ✅ Read | ✅ Primary |
| `AGENTS.override.md` | ❌ | ❌ | ✅ Override layer |
| `.github/copilot-instructions.md` | ✅ Native | ✅ Read | ❌ |
| `.github/instructions/**/*.instructions.md` | ✅ Native | ❌ | ❌ |
| `CLAUDE.md` (root) | ✅ Read | ✅ Primary | ❌ |
| `<subdir>/CLAUDE.md` | ✅ Read | ✅ Scoped | ❌ |
| `CLAUDE.local.md` | ❌ | ✅ Personal (gitignored) | ❌ |
| `GEMINI.md` (root) | ✅ Read | ❌ | ❌ |
| `$HOME/.copilot/copilot-instructions.md` | ✅ Global | ❌ | ❌ |
| `$HOME/.claude/CLAUDE.md` | ❌ | ✅ Global | ❌ |
| `$HOME/.codex/AGENTS.md` | ❌ | ❌ | ✅ Global |

### Skills — What Each Tool Reads

Skills follow the same `SKILL.md` format across all three tools (YAML frontmatter + markdown body + optional bundled resources). The directory locations differ:

| Path | Copilot CLI | Claude Code | Codex CLI |
|------|:-----------:|:-----------:|:---------:|
| `.github/skills/<name>/SKILL.md` | ✅ | ✅ | ✅ |
| `.claude/skills/<name>/SKILL.md` | ✅ Read | ✅ Native | ❌ |
| `~/.copilot/skills/<name>/SKILL.md` | ✅ Native | ❌ | ❌ |
| `~/.claude/skills/<name>/SKILL.md` | ✅ Read | ✅ Native | ❌ |
| `~/.codex/skills/<name>/SKILL.md` | ❌ | ❌ | ✅ Native |

### Hooks — Comparison

| Aspect | Copilot CLI | Claude Code | Codex CLI |
|--------|:-----------:|:-----------:|:---------:|
| Config location | `.github/hooks/hooks.json` | `.claude/settings.json` | `~/.codex/rules/` (execpolicy) |
| Pre-tool hook | `preToolUse` | `PreToolUse` | Execpolicy rules |
| Post-tool hook | `postToolUse` | `PostToolUse` | Execpolicy rules |
| Session hooks | `sessionStart` / `sessionEnd` | ❌ | ❌ |
| Prompt hook | ❌ | `UserPromptSubmit` | ❌ |

### Custom Agents — Comparison

| Aspect | Copilot CLI | Claude Code | Codex CLI |
|--------|:-----------:|:-----------:|:---------:|
| Agent definition files | `.github/agents/*.agent.md` | N/A (uses skills + commands) | N/A (uses AGENTS.md layering) |
| Agent handoffs | ✅ Chain agents into workflows | ❌ | ✅ Via Agents SDK |
| Subagent delegation | ✅ Built-in (Explore, Task) | ❌ | ✅ Via multi-agent orchestration |
| Org-level agents | ✅ (Business/Enterprise) | ❌ | ❌ |

### Recommended Multi-Tool Repository Layout

For teams using multiple coding agents, structure your repo to maximize portability:

```
project/
├── AGENTS.md                        # Universal — all three tools read this
├── CLAUDE.md                        # Claude Code primary + Copilot CLI reads
├── .github/
│   ├── copilot-instructions.md      # Copilot CLI native
│   ├── instructions/                # Copilot CLI path-specific
│   ├── agents/                      # Copilot CLI custom agents
│   ├── skills/                      # Universal — all three tools read this
│   │   └── code-review/
│   │       └── SKILL.md
│   └── hooks/
│       └── hooks.json               # Copilot CLI hooks
├── .claude/
│   ├── settings.json                # Claude Code hooks + permissions
│   └── commands/                    # Claude Code slash commands
└── src/
    └── api/
        └── AGENTS.md                # Universal scoped instructions
```

### Portability Best Practices

- **Put shared instructions in `AGENTS.md`** — this is the only file all three tools read. Use it as your single source of truth for build commands, coding standards, and project conventions.
- **Put skills in `.github/skills/`** — this path is read by all three tools.
- **Use `CLAUDE.md` for Claude-specific context** that Copilot CLI will also pick up (Codex will not).
- **Use `.github/copilot-instructions.md` and `*.instructions.md`** only for Copilot-specific conventions that don't belong in `AGENTS.md`.
- **Use `AGENTS.override.md`** only if you use Codex CLI and need a local override layer.
- **Avoid duplicating instructions** across multiple files — if something belongs in `AGENTS.md`, don't repeat it in `CLAUDE.md` or `copilot-instructions.md`.
- **Test your instructions** with each tool you support — activation behavior and precedence rules differ subtly.

---

## 13. Best Practices Summary

### Custom Instructions

- Keep instructions concise, structured, and conflict-free.
- Use `.github/copilot-instructions.md` for repo-wide norms.
- Use path-specific `*.instructions.md` with `applyTo` for scoped conventions.
- Use `AGENTS.md` at the root for primary always-on guidance.
- Use `/init` to bootstrap, then trim aggressively.

### Project Structure

- Maintain a modular repo design with clear separation of concerns.
- Place directory-specific `AGENTS.md` files in submodules that need scoped context.
- Keep personal overrides in `~/.copilot/` (not committed to git).

### Skills & Agents

- Use **skills** for reusable, task-specific AI workflows (code review, refactoring, debugging).
- Use **custom agents** for named personas that orchestrate tools and skills for complex workflows.
- Use **custom instructions** for simple, always-on project-wide norms.
- Keep skill files modular, single-purpose, and under 500 lines.

### Hooks & Automation

- Use hooks for deterministic guardrails (formatting, linting, policy enforcement).
- Block at commit-time, not mid-edit, to avoid degrading Copilot's output.
- Test hooks locally by piping test JSON input before deploying.

### Context & Session Management

- Use `/context` to monitor window usage.
- Use `/clear` or `/new` when switching tasks (free, no loss).
- Use `/compact` only when nearing the context limit (lossy).
- Let auto-compaction handle most context pressure automatically.
- Offload long-running or async work to Copilot coding agent in the cloud.

### Documentation

- Document architecture decisions in `docs/decisions/`.
- Maintain runbooks in `docs/runbooks/`.
- Keep `docs/architecture.md` as the system-level overview.

---

## References

- <https://docs.github.com/copilot/concepts/agents/about-copilot-cli>
- <https://docs.github.com/en/copilot/how-tos/copilot-cli/cli-best-practices>
- <https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions>
- <https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli>
- <https://docs.github.com/en/copilot/concepts/agents/about-agent-skills>
- <https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-skills>
- <https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-hooks>
- <https://docs.github.com/en/copilot/reference/cli-command-reference>
- <https://github.com/github/copilot-cli>
- <https://github.com/github/awesome-copilot>
- <https://agents.md>
- <https://developers.openai.com/codex/guides/agents-md/>
- <https://developers.openai.com/codex/skills/>
- <https://developers.openai.com/codex/cli/>

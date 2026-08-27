# Claude Code — Rules & Best Practices

---

## 1. Project Overview

A modular repository structure designed for building Claude Code projects with structured AI context, reusable skills, and automated development workflows.

### Recommended Repository Layout

```
claude_code_project/
├── CLAUDE.md                # Project memory — committed, shared with team
├── CLAUDE.local.md          # Personal overrides — gitignored
├── README.md
├── docs/
│   ├── architecture.md
│   ├── decisions/
│   └── runbooks/
├── .claude/
│   ├── settings.json        # Hooks, permissions, model config
│   ├── hooks/
│   ├── commands/             # Slash commands (.md files)
│   └── skills/
│       ├── code-review/
│       │   └── SKILL.md
│       ├── refactor/
│       │   └── SKILL.md
│       └── release/
│           └── SKILL.md
├── tools/
│   ├── scripts/
│   └── prompts/
└── src/
    ├── api/
    │   └── CLAUDE.md         # Directory-specific context
    └── persistence/
        └── CLAUDE.md         # Directory-specific context
```

---

## 2. Memory & CLAUDE.md

`CLAUDE.md` is Claude's persistent memory — loaded at the start of every session before your first message. All layers combine; more-specific files override on conflict.

### File Hierarchy

| File | Scope |
|------|-------|
| `~/.claude/CLAUDE.md` | **Global** — applies to all projects |
| `<project>/CLAUDE.md` | **Project** — committed to git, shared with team |
| `<project>/<subdir>/CLAUDE.md` | **Directory-specific** — scoped context for submodules |
| `<project>/CLAUDE.local.md` | **Personal overrides** — gitignored |

### CLAUDE.md Best Practices

- **Keep it under 300 lines.** Focus on what Claude would get wrong without it — not obvious facts it can infer from the codebase.
- **Use `@path/to/file.md` imports** inside CLAUDE.md to modularize. Link out to `docs/testing.md`, `docs/architecture.md`, etc. rather than stuffing everything in one file.
- **Survives `/compact`** — Claude re-reads it from disk after compaction.
- **`/init`** generates a starter CLAUDE.md based on your project structure. Delete most of the boilerplate it produces; it tends to describe obvious things (language, framework) that waste context.
- **`#` shortcut** — prefix a prompt with `#` to write an instruction directly into CLAUDE.md without manually editing the file. Use `#` to experiment in-session, then make it permanent once you're happy with the wording.

### Auto Memory

A separate, automatic memory system alongside CLAUDE.md. Claude saves notes for itself during sessions — build commands, debugging insights, code style preferences — without you writing anything.

- Stored at `~/.claude/projects/<project>/memory/MEMORY.md` (plus topic files it creates)
- On by default; manage with the `/memory` command
- Machine-local; shared across git worktrees of the same repo

---

## 3. `@` File References

Prefix any file or directory path with `@` to pull its contents into the current context.

```
@src/pipeline.py
@docs/architecture.md
```

- Works in prompts and inside CLAUDE.md files (for imports).
- Supports image paths for UI/design tasks.
- Claude auto-loads any CLAUDE.md files present in the referenced path.

---

## 4. Context Management

| Command | What it does |
|---------|-------------|
| `/compact` | Summarizes conversation history to free context window space. CLAUDE.md survives (re-read from disk). Lossy — use only when the window is nearly full, not habitually. |
| `/clear` | Resets session context entirely with no cost. Use when switching tasks. |
| `/context` | Shows context window usage; warns if skills are being excluded. |

---

## 5. Hooks

Shell commands that execute automatically at specific points in Claude's lifecycle. Use hooks for deterministic control over behavior that shouldn't rely on Claude "remembering" to do something.

### Hook Events (8 total), including:

- **`UserPromptSubmit`** — fires before Claude processes your prompt
- **`PreToolUse`** — runs before any tool execution (validation, blocking)
- **`PostToolUse`** — runs after tool execution (linting, testing)

### Configuration

Defined in `.claude/settings.json`, or use the interactive `/hooks` command.

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write(*.py)",
      "hooks": [{ "type": "command", "command": "python -m black $file" }]
    }]
  }
}
```

### Hook Best Practice

Prefer **"block-at-submit"** (e.g., blocking at `git commit`) over blocking mid-edit. Interrupting Claude mid-plan degrades output quality.

---

## 6. Custom Commands & Skills

Both live as `.md` files and become `/slash-commands`. They've been unified — a file at `.claude/commands/review.md` and `.claude/skills/review/SKILL.md` both create `/review` and behave the same way.

### Key Difference

- **Commands** — always user-triggered via `/command-name`
- **Skills** — can also auto-invoke when Claude recognizes the task matches the skill's description

### Directory Locations

| Path | Scope |
|------|-------|
| `.claude/commands/` | Project-scoped, shared via git |
| `~/.claude/commands/` | User-scoped, all projects |
| `.claude/skills/` | Project-scoped skills |
| `~/.claude/skills/` | User-scoped skills |

### Command Features

- **`$ARGUMENTS`** — passes arguments from the invocation: `/fix-issue 123`
- **YAML frontmatter** — set `allowed-tools`, `description`, invocation control
- **Dynamic content** — embed bash (`!`) and file references (`@`) inside the `.md`
- **MCP prompts** — automatically appear as `/mcp__servername__promptname`

### Example Command (`.claude/commands/fix-issue.md`)

```markdown
Find and fix issue #$ARGUMENTS following our coding standards.
```

---

## 7. Anatomy of a SKILL.md

Every skill is a folder containing a `SKILL.md` file and optional bundled resources. `SKILL.md` has two parts: **YAML frontmatter** (metadata Claude uses for discovery) and **markdown body** (instructions Claude follows when the skill is invoked).

### Frontmatter

The frontmatter sits between `---` markers at the top. Two fields are required:

```yaml
---
name: code-review
description: >
  Reviews code for bugs, style issues, and best practices.
  Use when reviewing pull requests, code changes, or when
  the user asks to "review", "check", or "audit" code.
allowed-tools: [Bash(ruff *), Read, Grep]
---
```

- **`name`** — becomes the `/slash-command` (e.g., `/code-review`). Consider gerund form (`reviewing-code`) for clarity.
- **`description`** — this is critical: Claude reads all skill descriptions at startup (~100 tokens each) to decide which skill to load. Be specific about trigger phrases and scenarios. Descriptions that are slightly "pushy" activate more reliably (e.g., "Use when the user mentions reviews, PRs, diffs, or code quality, even if they don't say 'review' explicitly.").
- **`allowed-tools`** *(optional)* — restricts which tools the skill can use (e.g., only Bash with specific commands).

### Markdown Body

After the frontmatter, write instructions in standard Markdown. This is the core prompt that Claude follows when the skill is invoked. Two broad categories:

**Reference-style skills** add knowledge Claude applies to ongoing work (conventions, patterns, style guides):

```markdown
---
name: api-conventions
description: API design patterns for this codebase
---
When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats: { "error": { "code": "...", "message": "..." } }
- Include request validation with Pydantic models
- All responses must include X-Request-Id header
```

**Task-style skills** give Claude step-by-step instructions for a specific action:

```markdown
---
name: code-review
description: >
  Comprehensive code review. Use when reviewing PRs or code changes.
---
When reviewing code:

1. **Check for bugs**: Identify potential runtime errors, edge cases, and logic flaws.
2. **Verify style**: Ensure code follows team conventions (naming, formatting, structure).
3. **Evaluate architecture**: Flag violations of established patterns in @docs/architecture.md.
4. **Security scan**: Look for injection vulnerabilities, hardcoded secrets, unsafe deserialization.
5. **Suggest improvements**: Propose simplifications, extractions, or performance gains.
6. **Summarize**: Produce a structured report with severity levels (critical / warning / note).

If the code includes database queries, also check for SQL injection and missing indexes.
```

### Bundled Resources (Optional)

Skills become more powerful when you bundle supporting files alongside `SKILL.md`. The standard directory structure:

```
code-review/
├── SKILL.md              # Entry point (required, keep under ~500 lines / 5k tokens)
├── scripts/              # Executable code Claude runs via Bash tool
│   └── lint_check.py
├── references/           # Documentation loaded into context as needed
│   ├── STYLE_GUIDE.md
│   └── SECURITY_RULES.md
├── templates/            # Reusable output templates
│   └── review_report.md
└── assets/               # Binary files, icons, fonts
```

- **`scripts/`** — deterministic automation (linters, formatters, validators, code generators). Claude runs them via the Bash tool.
- **`references/`** — supplementary docs loaded only when needed (progressive disclosure). Keeps `SKILL.md` lean.
- **`templates/`** — output scaffolds Claude fills in for consistent formatting.
- **`assets/`** — static files used in output (icons, fonts, etc.).

**Progressive disclosure** is the key design principle: at startup, only frontmatter is loaded (~100 tokens). When a skill is activated, `SKILL.md` is loaded (<5k tokens). Bundled resources are read only when the instructions reference them. This keeps the context window lean while making deep knowledge available on demand.

### SKILL.md Authoring Best Practices

- **Keep `SKILL.md` focused and concise** — under 500 lines / 5,000 tokens. Move detailed docs to `references/`.
- **Use active, directive language** — tell Claude what to do, not what might happen.
- **Break complex tasks into numbered steps** — sequential structure improves reliability.
- **Include examples** — concrete input/output pairs dramatically improve activation and quality. Testing shows activation rates jump from ~50% to ~90% with good examples.
- **Specify output formats** — when consistency matters, show Claude exactly what the output should look like.
- **Define scope boundaries** — include an "Out of Scope" section so Claude knows when NOT to use the skill.
- **Add conditional logic** — handle branching scenarios ("If the file is a `.py`, run ruff; if `.ts`, run eslint").
- **Link to bundled resources** — use relative paths like `See [STYLE_GUIDE.md](references/STYLE_GUIDE.md)` so Claude loads them only when needed.
- **Test across models** — what works for Opus may need more detail for Haiku/Sonnet.

### Real-World Skill Examples

**Commit message formatter:**

```yaml
---
name: commit-msg
description: >
  Formats git commit messages using conventional commits.
  Use when committing code or when the user asks to write a commit message.
---
```

```markdown
Format commit messages as: type(scope): summary

Examples:
- Input: "Added JWT auth" → feat(auth): implement JWT-based authentication
- Input: "Fixed date bug" → fix(reports): correct date formatting in timezone conversion
```

**Codebase visualizer (with scripts):**

```yaml
---
name: codebase-visualizer
description: >
  Generate an interactive tree visualization of the codebase.
  Use when exploring a repo or understanding project structure.
allowed-tools: [Bash(python *)]
---
```

```markdown
Run the visualization script from the project root:

    python ~/.claude/skills/codebase-visualizer/scripts/visualize.py .

This creates codebase-map.html with collapsible directories, file sizes, and color-coded file types.
```

---

## 8. Useful Built-in Commands

| Command | What it does |
|---------|-------------|
| `/init` | Generates a starter CLAUDE.md for the current project |
| `/compact` | Compacts session history to free context |
| `/clear` | Resets session context entirely |
| `/memory` | View and manage auto-memory; toggle it on/off |
| `/hooks` | Interactive hook configuration menu |
| `/context` | Shows context window usage; warns if skills are being excluded |
| `/model` | Switch the active model |

---

## 9. Best Practices Summary

### CLAUDE.md

- Keep it focused, structured, and under 300 lines.
- Only include what Claude would get wrong without it.
- Use `@imports` to modularize into separate docs.
- Use `#` to experiment with instructions before making them permanent.

### Project Structure

- Maintain a modular repository design with clear separation of concerns.
- Place directory-specific `CLAUDE.md` files in submodules that need scoped context.
- Use `CLAUDE.local.md` for personal overrides that shouldn't be shared.

### Skills & Commands

- Use skills for reusable AI workflows (code review, refactoring, releases).
- Prefer skills over commands when auto-invocation is desirable.
- Keep prompt files modular and single-purpose.

### Hooks & Automation

- Use hooks for deterministic guardrails (formatting, linting, testing).
- Block at commit-time, not mid-edit, to avoid degrading Claude's output.
- Configure hooks in `.claude/settings.json` or via `/hooks`.

### Context & Session Management

- Use `/context` to monitor window usage.
- Use `/clear` when switching tasks (free, no loss).
- Use `/compact` only when nearing the context limit (lossy, ~1 min).
- Keep AI context minimal and precise.

### Documentation

- Document architecture decisions in `docs/decisions/`.
- Maintain runbooks in `docs/runbooks/`.
- Keep `docs/architecture.md` as the system-level overview.

---

## References

- https://code.claude.com/docs/en/how-claude-code-works
- https://code.claude.com/docs/en/cli-reference
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/slash-commands

## Role agents and delegation

This page covers the endpoint: how Claude Code reaches a model. For the other half
of the [cloud-to-local workflow][blog] — splitting work into architect,
planner, implementer and reviewer roles, writing handoff packets, and which
guardrails Claude Code enforces rather than merely requests — see
[Role agents across harnesses](../../docs/role-agents.md).

[blog]: https://olibartfast.ninja/blog/ai-coding-workflows-cloud-to-local.html

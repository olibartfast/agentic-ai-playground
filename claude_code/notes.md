# Claude Code – Feature Notes

---

## Memory & CLAUDE.md

CLAUDE.md is Claude's persistent memory — loaded at the start of every session before your first message.

**File hierarchy** (all layers combine; more specific overrides on conflict):

| File | Scope |
|------|-------|
| `~/.claude/CLAUDE.md` | Global — applies to all projects |
| `<project>/CLAUDE.md` | Project — committed to git, shared with team |
| `<project>/<subdir>/CLAUDE.md` | Directory-specific |
| `<project>/CLAUDE.local.md` | Personal overrides — gitignored |

**Tips:**
- Keep it under 300 lines. Focus on what Claude would get wrong without it — not obvious facts it can infer from the codebase.
- Use `@path/to/file.md` imports inside CLAUDE.md to modularize — link out to `docs/testing.md`, `docs/architecture.md`, etc. rather than stuffing everything in one file.
- CLAUDE.md fully survives `/compact` — Claude re-reads it from disk after compaction.

**`/init`** — generates a starter CLAUDE.md based on your project structure. Delete most of the boilerplate it produces; it tends to describe obvious things (language, framework) that waste context.

**`#` shortcut** — prefix a prompt with `#` to write an instruction directly into CLAUDE.md without manually editing the file. Good workflow: use `#` to experiment in-session, then make it permanent once you're happy with the wording.

---

## Auto Memory

A separate, automatic memory system alongside CLAUDE.md. Claude saves notes for itself during sessions — build commands, debugging insights, code style preferences — without you writing anything.

- Stored at `~/.claude/projects/<project>/memory/MEMORY.md` (plus topic files it creates)
- On by default; manage with `/memory` command
- Machine-local; shared across git worktrees of the same repo

---

## `@` File References

Prefix any file or directory path with `@` to pull its contents into the current context.

```
@src/pipeline.py
@docs/architecture.md
```

- Works in prompts and inside CLAUDE.md files (for imports)
- Supports image paths for UI/design tasks
- Faster than copy-pasting; Claude also auto-loads any CLAUDE.md files present in the referenced path

---

## `/compact`

Compacts the session by summarizing conversation history to free up context window space.

- CLAUDE.md survives compaction (re-read from disk afterward)
- Costs ~1 minute and reduces context fidelity — the summary is lossy
- Use when the context window is nearly full, not habitually
- Alternative: `/clear` resets context entirely with no cost — use it when switching tasks

---

## Hooks

Shell commands that execute automatically at specific points in Claude's lifecycle. For deterministic control over behavior that shouldn't rely on Claude "remembering" to do something.

**8 hook events**, including:
- `UserPromptSubmit` — fires before Claude processes your prompt
- `PreToolUse` — runs before any tool execution (validation, blocking)
- `PostToolUse` — runs after tool execution (linting, testing)

**Configuration:** `.claude/settings.json`, or use the interactive `/hooks` command.

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

**Best practice:** prefer "block-at-submit" (blocking at `git commit`) over blocking mid-edit. Interrupting Claude mid-plan degrades output quality.

---

## Custom Commands & Skills

Both live as `.md` files and become `/slash-commands`. They've been unified — a file at `.claude/commands/review.md` and `.claude/skills/review/SKILL.md` both create `/review` and behave the same way.

**Key difference:**
- **Commands** — always user-triggered via `/command-name`
- **Skills** — can also auto-invoke when Claude recognizes the task matches the skill's description

**Directory locations:**

| Path | Scope |
|------|-------|
| `.claude/commands/` | Project-scoped, shared via git |
| `~/.claude/commands/` | User-scoped, all projects |
| `.claude/skills/` | Project-scoped skills |
| `~/.claude/skills/` | User-scoped skills |

**Command features:**
- `$ARGUMENTS` — passes arguments from the invocation: `/fix-issue 123`
- YAML frontmatter — set `allowed-tools`, `description`, invocation control
- Dynamic content — embed bash (`!`) and file references (`@`) inside the `.md`
- MCP prompts — automatically appear as `/mcp__servername__promptname`

**Example command** (`.claude/commands/fix-issue.md`):
```
Find and fix issue #$ARGUMENTS following our coding standards.
```

---

## Useful Built-in Commands

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

## References

- https://code.claude.com/docs/en/how-claude-code-works
- https://code.claude.com/docs/en/cli-reference
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/slash-commands

# Kilo Code

[Kilo Code](https://kilocode.ai) ships a CLI and TUI as `kilo`. It is an
OpenCode fork — the command set is identical, its logs identify as `opencode`,
and it accepts the same `@ai-sdk/openai-compatible` provider schema. Anything
written for [OpenCode](../opencode/) applies here with two path changes:

- Binary: `kilo`, not `opencode`.
- User config: `~/.config/kilo/kilo.jsonc`, not
  `~/.config/opencode/opencode.json`.

The Kilo config is JSONC and may already carry a `permission` block. Add the
provider alongside it rather than replacing the file.

## Ollama on the same machine

Merge the provider block from
[`opencode.ollama.example.json`](../opencode/opencode.ollama.example.json) into
`~/.config/kilo/kilo.jsonc`, keeping the existing top-level keys:

```json
"provider": {
  "ollama": {
    "npm": "@ai-sdk/openai-compatible",
    "name": "Ollama (this laptop)",
    "options": {
      "baseURL": "http://127.0.0.1:11434/v1",
      "apiKey": "ollama"
    },
    "models": {
      "qwen2.5-coder:7b": {
        "name": "Qwen2.5-Coder 7B (Ollama)",
        "limit": { "context": 32768, "output": 4096 }
      }
    }
  }
}
```

Set `limit.context` from `ollama show <model>`, not from the model card. Take
the model id from `curl -s http://localhost:11434/v1/models` so it keeps its
tag.

## Local llama-server (Gemma 4 E4B)

Kilo ships no `local` provider by default. Add one alongside the existing
`permission` and `provider` keys rather than replacing them:

```json
"local": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "llama-server (this laptop)",
  "options": {
    "baseURL": "http://127.0.0.1:8080/v1",
    "apiKey": "dummy"
  },
  "models": {
    "gemma-4-e4b": {
      "name": "Gemma 4 E4B QAT (laptop)",
      "limit": { "context": 65536, "output": 8192 }
    }
  }
}
```

Identical to the [OpenCode block](../opencode/README.md), as the fork accepts
the same schema. Select it with `kilo run --model local/gemma-4-e4b`.

## Verify and run

```bash
kilo models | grep ollama
cd /your/project
kilo run --model ollama/qwen2.5-coder:7b "your prompt"
```

## Tool-calling check

Kilo's default agent is `code` rather than OpenCode's `build`, and it exposes a
wider tool set including `suggest` and task-list tools. On a weak model this
widens the failure surface. Probing `qwen2.5-coder:7b` with the same task used
for the other agents, 66 s wall clock:

```json
{
  "name": "suggest",
  "arguments": {
    "suggestion": "It looks like you're working in a specific directory. ..."
  }
}
```

Two failures at once. The call is emitted as fenced text rather than a
structured tool call, and the model selected `suggest` instead of `read`,
ignoring the task entirely — where OpenCode and Pi at least chose the correct
tool.

Interactively it degrades further. A bare `hello` in the TUI produced no
greeting at all, but an unrequested subagent call, 65 s at 6.3 tok/s:

```text
{"name": "general", "arguments": {"prompt": "Explore the codebase for all files
related to GPU computations ...", "subagent_type": "explore"}}
```

The same model under OpenCode answered `Hi` with ordinary conversational text.
The difference is the surrounding tool set: Kilo's `code` agent exposes more
tools, and a model that pattern-matches responds to *any* input with
tool-call-shaped JSON. Treat a wider tool set as a cost, not a feature, when
evaluating small local models.

See the [Qwen2.5-Coder-7B CPU result][qwen-result] for the root-cause isolation
across five parsers.

[qwen-result]: ../../benchmarks/2026-08-21-qwen2.5-coder-7b-cpu/result.md

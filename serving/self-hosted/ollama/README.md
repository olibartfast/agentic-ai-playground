# Ollama

Ollama provides local model installation and an API backend used by several
agent integrations.

## Install on Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Pull and run a model

```bash
ollama run gpt-oss:20b
```

Ollama also serves an OpenAI-compatible API on `http://localhost:11434/v1`
whenever the daemon is running, which is how agent integrations connect to it.

## Agent clients

Four agents were configured against this backend and measured on the same task.
Each integration page carries its config and its result:

- [Pi Agent](../../../integrations/pi/) — `~/.pi/agent/models.json`
- [OpenCode](../../../integrations/opencode/) — `~/.config/opencode/opencode.json`
- [Kilo Code](../../../integrations/kilocode/) — `~/.config/kilo/kilo.jsonc`
- [Hermes](../../../integrations/hermes/) — `~/.hermes/config.yaml`

All four share one requirement: take the model id from the endpoint, not the
model card, because Ollama ids carry a tag. Set any context limit from
`ollama show <model>` rather than the published window — Ollama truncates to its
own `num_ctx` and an overstated limit is cut silently.

No agent completed a tool call against `qwen2.5-coder:7b`. See the
[agent matrix](../../../benchmarks/2026-08-21-qwen2.5-coder-7b-cpu/result.md)
before assuming a model served here is usable for agent work.

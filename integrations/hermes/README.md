# Hermes Agent

[Hermes Agent](https://github.com/NousResearch/hermes-agent) is a CLI and TUI
agent installed as `hermes`, configured from `~/.hermes/config.yaml`.

## Hosted or tunnelled endpoint

Select a custom OpenAI-compatible endpoint in Hermes' model configuration. Use
the loopback endpoint provided by the SSH tunnel, the model name returned by
`/v1/models`, and an environment variable for the API key. Do not commit keys.

## Local Ollama

Hermes ships an `ollama-cloud` provider for models hosted on ollama.com. A
local daemon is a different case: register it as a named custom provider.
Append to `~/.hermes/config.yaml`, keeping existing top-level keys:

```yaml
providers:
  ollama:
    base_url: "http://127.0.0.1:11434/v1"
    api_key: "ollama"
```

Named entries are addressed as `custom:<name>`, so the provider above is
selected per run without disturbing the configured default:

```bash
hermes --provider custom:ollama -m qwen2.5-coder:7b
```

Use `key_env: "SOME_VAR"` instead of `api_key` for any endpoint that is not on
loopback. The literal value above is acceptable only because Ollama ignores the
Authorization header and the endpoint is bound to `127.0.0.1`.

## Local llama-server

A second custom provider for llama.cpp, alongside the `ollama` entry:

```yaml
providers:
  ollama:
    base_url: "http://127.0.0.1:11434/v1"
    api_key: "ollama"
  local:
    base_url: "http://127.0.0.1:8080/v1"
    api_key: "none"
```

```bash
hermes --provider custom:local -m gemma-4-e4b
```

Unlike the Ollama path, this one clears the context floor described below —
but only if the server was started with `--ctx-size 65536` or more. Hermes
reads the window the endpoint reports, so the refusal is a function of the
serve flag, not of the model's published capability.

## Minimum context window

Hermes enforces a hard floor of **64,000 tokens** and exits before contacting
the endpoint if the model reports less:

```text
Model qwen2.5-coder:7b has a context window of 32,768 tokens, which is below
the minimum 64,000 required by Hermes Agent.
```

This makes Hermes unusable with several otherwise-serviceable local models,
`qwen2.5-coder:7b` among them. Two cautions before working around it:

- The suggested `model.context_length` key is global. Setting it also
  misdescribes whatever provider is configured as the default.
- Declare the model's *true* window only. Qwen2.5-Coder-7B is trained to 32K;
  claiming 64K replaces an explicit refusal with silent truncation, which is
  harder to diagnose.

Prefer a model whose real window clears the floor. See the
[Qwen2.5-Coder-7B CPU result][qwen-result] for the full agent matrix.

[qwen-result]: ../../benchmarks/2026-08-21-qwen2.5-coder-7b-cpu/result.md

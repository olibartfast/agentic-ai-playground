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

## Version note: `--provider` has changed shape three times

Check `hermes chat --help` against the installed build before copying any
command from this page. The flag has taken three incompatible forms:

| Version | Form | Local endpoint reachable by |
| --- | --- | --- |
| pre-0.10 | `--provider custom:<name>` | the flag |
| 0.10.0 | fixed enum, no custom form | a profile only |
| 0.20.5 | built-in **or** a user-defined name from `providers:` | the flag again |

On **0.20.5** the local endpoint is selected directly, which is the simplest
route and leaves the configured default untouched:

```bash
hermes chat -q "Reply with exactly the word: ready" \
  --provider local -m qwen3-coder-30b
```

Measured on this build: 21,936 prompt tokens, 113 s of prefill against a local
GPU endpoint — see the [2026-08-26 record][agents-2026-08-26]. That is 66% more
than 0.10.0 shipped, so re-measure rather than reusing an older figure.

[agents-2026-08-26]: ../../benchmarks/2026-08-26-agent-client-prompt-sizes/result.md

### The 0.10.0 profile workaround

Kept because it still works, and because an isolated history, `.env`, or
SOUL.md is sometimes wanted for a local model. It is no longer *required*
merely to reach a local endpoint.

On **0.10.0** the CLI moved to subcommands (`hermes chat`), and
`--provider` became a fixed enum of built-in providers with no `custom:` form.
`-m local/qwen3-coder-30b` does **not** reach a `providers:` entry either — the
whole string is sent as a model name to whatever provider is currently default:

```text
HTTP 400: The supported API model names are deepseek-v4-pro, ... but you
passed local/qwen3-coder-30b.
```

On 0.10.0, routing comes from the `model:` block rather than a per-run flag.
Because that block is global, changing it in place would repoint the default
away from whatever hosted provider is configured. Use a **profile** instead —
an isolated Hermes home with its own `config.yaml`:

```bash
hermes profile create llamacpp --clone
```

Then set that profile's `model:` block to the local endpoint, leaving the
default profile untouched:

```yaml
model:
  default: qwen3-coder-30b
  provider: local
  base_url: http://127.0.0.1:8080/v1
```

`hermes profile create` writes a wrapper script into `~/.local/bin` named after
the profile, so the profile is selected by invoking it:

```bash
llamacpp chat -q "Reply with exactly the word: ready"
```

**Do not name the profile `local`.** `local` is a bash builtin and takes
precedence over `$PATH`, so the generated wrapper is unreachable from an
interactive shell — `local chat` fails with *"can only be used in a function"*.
Rename with `hermes profile rename local llamacpp` if it has already been
created.

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

# Claude Code — Routing to Open Models

Reference for routing Claude Code to open-weights deployments (DeepSeek,
Nemotron, Qwen, GLM, Gemma, Llama) and aggregator/inference APIs (Together AI,
OpenRouter, Fireworks, Z.ai, Moonshot).

Last verified: May 2026.

---

## How it works

Claude Code talks the Anthropic Messages API (`/v1/messages`). Setting
`ANTHROPIC_BASE_URL` redirects all traffic to a custom endpoint for that
session. When unset, Claude Code uses the official Anthropic API normally.

**You can switch freely between providers and official Anthropic — just not
in the same session simultaneously.**

```bash
export ANTHROPIC_BASE_URL="https://your-endpoint/anthropic"
export ANTHROPIC_AUTH_TOKEN="your-key"

# Map Anthropic model tiers to provider-specific model names
export ANTHROPIC_DEFAULT_OPUS_MODEL="model-name"
export ANTHROPIC_DEFAULT_SONNET_MODEL="model-name"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="model-name"

# Suppress telemetry calls that will fail on non-Anthropic backends
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

---

## Three integration paths

### 1. Native Anthropic-compatible endpoints

Some providers ship a Messages-API surface specifically for Claude Code — zero
friction, no proxy needed:

| Provider        | Base URL                              |
| --------------- | ------------------------------------- |
| DeepSeek        | `https://api.deepseek.com/anthropic`  |
| Z.ai (GLM)      | `https://api.z.ai/api/anthropic`      |
| Moonshot (Kimi) | `https://api.moonshot.ai/anthropic`   |

### 2. Self-hosted with a Messages-API server

- **vLLM** has first-party support for Claude Code via its Anthropic-compatible
  API.
- **LiteLLM proxy** acts as a translation layer for OpenAI-compatible backends
  (llama.cpp, Ollama, vendor APIs without an Anthropic mode).

### 3. Translation proxy for OpenAI-only providers

Together AI, OpenRouter, and Fireworks expose only Chat Completions. Use
LiteLLM or
[`claude-code-router`](https://github.com/musistudio/claude-code-router) to
translate Messages → Chat Completions.

---

## Shell-function pattern (recommended)

Add to `~/.bashrc` or `~/.zshrc` to switch providers on demand without
permanently changing env vars:

```bash
# Official Anthropic — just use `claude` normally, no override needed

# DeepSeek — native Anthropic endpoint, no proxy required
deepseek() {
  ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic" \
  ANTHROPIC_AUTH_TOKEN="${DEEPSEEK_API_KEY}" \
  ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro" \
  ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro" \
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
  claude "$@"
}

# Together AI — requires LiteLLM proxy on port 4000
together() {
  ANTHROPIC_BASE_URL="http://localhost:4000" \
  ANTHROPIC_AUTH_TOKEN="sk-local-dev" \
  ANTHROPIC_DEFAULT_SONNET_MODEL="qwen3-coder" \
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
  claude "$@"
}

# Z.ai (GLM) — native Anthropic endpoint
glm() {
  ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
  ANTHROPIC_AUTH_TOKEN="${Z_AI_API_KEY}" \
  ANTHROPIC_DEFAULT_OPUS_MODEL="glm-4.6" \
  ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.6" \
  ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air" \
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
  claude "$@"
}

# Moonshot (Kimi) — native Anthropic endpoint
kimi() {
  ANTHROPIC_BASE_URL="https://api.moonshot.ai/anthropic" \
  ANTHROPIC_AUTH_TOKEN="${KIMI_API_KEY}" \
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
  claude "$@"
}
```

Usage:

```bash
claude          # official Anthropic
deepseek        # DeepSeek (no proxy needed)
together        # Together AI (LiteLLM must be running)
glm             # Z.ai GLM
kimi            # Moonshot Kimi
```

---

## LiteLLM proxy (for chat-only providers)

Required for Together AI, OpenRouter, NVIDIA NIM, and any provider without a
native Anthropic endpoint.

### Install

```bash
pip install litellm[proxy]
```

### Config (`litellm-config.yaml`)

```yaml
model_list:
  - model_name: deepseek-v4-pro
    litellm_params:
      model: deepseek/deepseek-v4-pro
      api_key: os.environ/DEEPSEEK_API_KEY

  - model_name: qwen3-coder
    litellm_params:
      model: together_ai/Qwen/Qwen3-Coder-480B-A35B-Instruct
      api_key: os.environ/TOGETHER_API_KEY

  - model_name: nemotron-49b
    litellm_params:
      model: nvidia_nim/nvidia/llama-3.3-nemotron-super-49b-v1
      api_key: os.environ/NVIDIA_API_KEY

  - model_name: glm-4.6
    litellm_params:
      model: openrouter/z-ai/glm-4.6
      api_key: os.environ/OPENROUTER_API_KEY

general_settings:
  master_key: sk-local-dev
```

### Run and connect

```bash
litellm --config litellm-config.yaml --port 4000
```

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="sk-local-dev"
export ANTHROPIC_DEFAULT_SONNET_MODEL="qwen3-coder"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
claude
```

---

## Provider quick-reference

| Provider | Native Anthropic endpoint | LiteLLM needed |
| --- | --- | --- |
| DeepSeek | `api.deepseek.com/anthropic` | No |
| Z.ai (GLM) | `api.z.ai/api/anthropic` | No |
| Moonshot (Kimi) | `api.moonshot.ai/anthropic` | No |
| Together AI | None | Yes |
| OpenRouter | None | Yes |
| NVIDIA NIM | None | Yes |
| vLLM (local) | Native (`/v1/messages`) | No |
| Ollama / llama.cpp | None | Yes |

### DeepSeek

Models: `deepseek-v4-pro`, `deepseek-v4-flash`, `deepseek-reasoner`.
Native Anthropic endpoint — no proxy needed. Cheapest path with strong coding
output.

### Together AI

No native Anthropic endpoint. Requires LiteLLM. Catalog includes Qwen3-Coder,
DeepSeek V3/R1, Llama, GLM, Gemma, Nemotron. Models use HuggingFace-style
paths.

### NVIDIA Nemotron

NIM endpoints are OpenAI-compatible only. Use LiteLLM proxy.
For local Nemotron via vLLM, it serves `/v1/messages` natively — no proxy
needed.

---

## Caveats

- `ANTHROPIC_BASE_URL` affects the whole session — you cannot mix official
  Anthropic and a custom provider in the same session.
- Tool-call schemas, streaming, and system prompt handling differ between
  Anthropic and OpenAI wire formats. Simple base-URL swaps work for chat but
  can break on complex agent loops, especially subagents and plan mode.
- Open models below ~70B on coding tasks lag noticeably — Claude Code's prompt
  harness is tuned for Claude.

---

## Decision matrix

| Goal | Recommended path |
| --- | --- |
| Try DeepSeek for a session | Native `/anthropic` endpoint, shell function |
| Use Together AI / OpenRouter catalog | LiteLLM proxy + shell function |
| Run Nemotron / Qwen locally | LiteLLM proxy (vLLM backend) |
| Switch between many providers | Shell functions per provider |
| Best agentic quality (subagents, hooks) | Stay on official Anthropic |
| Cheapest path with strong coding output | DeepSeek via native `/anthropic` endpoint |

---

## References

- Claude Code model config: <https://code.claude.com/docs/en/model-config>
- Claude Code env vars: <https://code.claude.com/docs/en/env-vars>
- LiteLLM proxy: <https://docs.litellm.ai/docs/proxy/quick_start>
- claude-code-router: <https://github.com/musistudio/claude-code-router>
- vLLM Anthropic-compatible server: <https://docs.vllm.ai/en/latest/serving/openai_compatible_server/>

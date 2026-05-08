# Claude Code — Routing to Open Models

Reference for routing Claude Code to open-weights deployments (DeepSeek,
Nemotron, Qwen, GLM, Gemma, Llama) and aggregator/inference APIs (Together AI,
OpenRouter, Fireworks, Z.ai, Moonshot).

Last verified: May 2026.

---

## Overview

Claude Code's CLI talks the Anthropic Messages API (`/v1/messages`). Anything
that exposes that wire format works as a drop-in.

### Configuration mechanism

Two environment variables drive routing:

```bash
export ANTHROPIC_BASE_URL="https://your-endpoint/anthropic"
export ANTHROPIC_AUTH_TOKEN="your-key"
export ANTHROPIC_DEFAULT_OPUS_MODEL="model-name"
export ANTHROPIC_DEFAULT_SONNET_MODEL="model-name"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="model-name"
```

The model alias env vars (`opus`/`sonnet`/`haiku`) override what those names
resolve to at the new endpoint. Set `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`
for non-Anthropic backends to avoid telemetry calls that will fail.

---

## Three integration paths

### 1. Native Anthropic-compatible endpoints

Some providers ship a Messages-API surface specifically for Claude Code:

| Provider        | Base URL                              |
| --------------- | ------------------------------------- |
| DeepSeek        | `https://api.deepseek.com/anthropic`  |
| Z.ai (GLM)      | `https://api.z.ai/api/anthropic`      |
| Moonshot (Kimi) | `https://api.moonshot.ai/anthropic`   |

These are zero-friction — set the env vars and go.

### 2. Self-hosted with a Messages-API server

- **vLLM** has first-party support for Claude Code via its Anthropic-compatible API.
- **LiteLLM Proxy** acts as a translation layer for OpenAI-compatible backends
  (llama.cpp, Ollama, vendor APIs without Anthropic mode).

### 3. Translation proxy for OpenAI-only providers

For Together AI, OpenRouter, and Fireworks (which expose only Chat Completions),
use LiteLLM's `/anthropic` passthrough endpoint or
[`claude-code-router`](https://github.com/musistudio/claude-code-router) to
translate Messages → Chat Completions.

---

## Shell-function pattern

Add these to `~/.zshrc` or `~/.bashrc` to switch providers on demand:

```bash
deepseek() {
  export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
  export ANTHROPIC_AUTH_TOKEN="${DEEPSEEK_API_KEY}"
  export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-reasoner"
  export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-chat"
  export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
  claude "$@"
}

glm() {
  export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
  export ANTHROPIC_AUTH_TOKEN="${Z_AI_API_KEY}"
  export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-4.6"
  export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.6"
  export ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air"
  claude "$@"
}

kimi() {
  export ANTHROPIC_BASE_URL="https://api.moonshot.ai/anthropic"
  export ANTHROPIC_AUTH_TOKEN="${KIMI_API_KEY}"
  claude "$@"
}
```

---

## LiteLLM unified proxy

For multi-provider setups, one LiteLLM proxy speaks both Anthropic and OpenAI
protocols and gives you a single auth surface.

`litellm-config.yaml`:

```yaml
model_list:
  - model_name: deepseek-chat
    litellm_params:
      model: deepseek/deepseek-chat
      api_key: os.environ/DEEPSEEK_API_KEY

  - model_name: deepseek-reasoner
    litellm_params:
      model: deepseek/deepseek-reasoner
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

Run the proxy:

```bash
litellm --config litellm-config.yaml --port 4000
```

Point Claude Code at it:

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="sk-local-dev"
export ANTHROPIC_DEFAULT_SONNET_MODEL="qwen3-coder"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
claude
```

---

## Provider quick-reference

### DeepSeek

| Endpoint                          | Notes           |
| --------------------------------- | --------------- |
| `api.deepseek.com/anthropic`      | Native, recommended |

Models: `deepseek-chat`, `deepseek-reasoner`.

### Together AI

No native Anthropic endpoint. Requires LiteLLM or `claude-code-router` proxy.
Catalog includes Qwen3-Coder, DeepSeek V3/R1, Llama, GLM, Gemma, Nemotron.

### NVIDIA Nemotron

NVIDIA Build / NIM endpoints are OpenAI-compatible only. Use LiteLLM proxy to
expose them to Claude Code.

---

## Caveats

- Tool-call schemas, streaming, and system prompt handling differ between
  Anthropic and OpenAI wire formats. Simple base-URL swaps work for chat but
  can break on complex agent loops, especially subagents and plan mode.
- Open models below ~70B-class on coding lag noticeably on Claude Code's prompt
  harness — it is tuned for Claude.

---

## Decision matrix

| Goal                                    | Recommended path                                |
| --------------------------------------- | ----------------------------------------------- |
| Try DeepSeek for a session              | Native `/anthropic` endpoint                    |
| Use Together AI / OpenRouter catalog    | LiteLLM proxy + Claude Code                     |
| Run Nemotron / Qwen / Gemma locally     | LiteLLM proxy (vLLM backend)                    |
| Switch between many models routinely    | LiteLLM proxy pointed at this CLI               |
| Best agentic quality (subagents, hooks) | Stay on Anthropic defaults                      |
| Cheapest path with strong coding output | DeepSeek-Reasoner via native `/anthropic` endpoint |

---

## References

- Claude Code model config: <https://code.claude.com/docs/en/model-config>
- LiteLLM proxy: <https://docs.litellm.ai/docs/proxy/quick_start>
- claude-code-router: <https://github.com/musistudio/claude-code-router>
- vLLM OpenAI-compatible server: <https://docs.vllm.ai/en/latest/serving/openai_compatible_server/>

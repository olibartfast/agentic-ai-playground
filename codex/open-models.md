# Codex CLI — Routing to Open Models

Reference for routing Codex CLI to open-weights deployments (DeepSeek,
Nemotron, Qwen, GLM, Gemma, Llama) and aggregator/inference APIs (Together AI,
OpenRouter, Fireworks).

Last verified: May 2026.

---

## Overview

Open-model support is first-class in Codex CLI. It defines a `model_providers`
system in `~/.codex/config.toml`, has a built-in `--oss` flag for local
servers, and supports profiles to bind model + provider + reasoning-effort
together.

---

## Built-in `--oss` flag (local models)

Set up Ollama or LM Studio, then:

```bash
ollama pull qwen3-coder
codex --oss -m qwen3-coder
```

Pin the default OSS provider in `config.toml`:

```toml
oss_provider = "ollama"   # or "lmstudio"
```

---

## Custom providers

Built-in IDs (`openai`, `ollama`, `lmstudio`) are reserved. Define your own:

```toml
# ~/.codex/config.toml

[model_providers.together]
name = "Together"
base_url = "https://api.together.ai/v1"
env_key = "TOGETHER_API_KEY"
wire_api = "responses"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"
wire_api = "responses"

[model_providers.deepseek]
name = "DeepSeek"
base_url = "https://api.deepseek.com/v1"
env_key = "DEEPSEEK_API_KEY"
wire_api = "chat"

[model_providers.llama_cpp]
name = "llama.cpp local"
base_url = "http://localhost:8001/v1"
wire_api = "responses"
stream_idle_timeout_ms = 10000000
```

---

## Profiles

Profiles bind a model, provider, and optional reasoning-effort into a named
preset:

```toml
[profiles.deepseek]
model_provider = "deepseek"
model = "deepseek-chat"

[profiles.qwen]
model_provider = "together"
model = "Qwen/Qwen3-Coder-480B-A35B-Instruct"
model_reasoning_effort = "high"

[profiles.local]
model_provider = "llama_cpp"
model = "unsloth/GLM-4.7-Flash"
```

Invoke a profile:

```bash
codex --profile qwen
codex --profile local --dangerously-bypass-approvals-and-sandbox
```

---

## Wire API caveat (important)

Codex is migrating from Chat Completions (`wire_api = "chat"`) to OpenAI's
Responses API (`wire_api = "responses"`) exclusively.

| Provider type                               | wire_api setting  |
| ------------------------------------------- | ----------------- |
| vLLM, Unsloth Studio (`/v1/responses`)      | `"responses"`     |
| DeepSeek `/v1`, Together AI, OpenRouter     | `"chat"` (for now)|
| LiteLLM proxy (translates both ways)        | `"responses"`     |

For chat-only providers, either set `wire_api = "chat"` and accept that it
will break in a future release, or front them with LiteLLM.

---

## Provider-specific configs

### DeepSeek

```toml
[model_providers.deepseek]
name = "DeepSeek"
base_url = "https://api.deepseek.com/v1"
env_key = "DEEPSEEK_API_KEY"
wire_api = "chat"

[profiles.deepseek]
model_provider = "deepseek"
model = "deepseek-chat"
```

Models: `deepseek-chat`, `deepseek-reasoner`.

### Together AI

```toml
[model_providers.together]
name = "Together"
base_url = "https://api.together.ai/v1"
env_key = "TOGETHER_API_KEY"
wire_api = "responses"

[profiles.qwen]
model_provider = "together"
model = "Qwen/Qwen3-Coder-480B-A35B-Instruct"
model_reasoning_effort = "high"
```

Together AI catalog includes Qwen3-Coder, DeepSeek V3/R1, Llama, Mixtral, GLM,
Gemma, Nemotron. Models use HuggingFace-style paths.

### NVIDIA Nemotron

```toml
[model_providers.nvidia]
name = "NVIDIA NIM"
base_url = "https://integrate.api.nvidia.com/v1"
env_key = "NVIDIA_API_KEY"
wire_api = "chat"

[profiles.nemotron]
model_provider = "nvidia"
model = "nvidia/llama-3.3-nemotron-super-49b-v1"
```

For local Nemotron, use vLLM with the model loaded — it gives a
Responses-compatible endpoint.

### Local with llama.cpp + Unsloth

Unsloth's llama.cpp build serves Responses format at `/v1/responses` natively:

```bash
llama-server -m model.gguf --port 8001 --host 0.0.0.0
```

```toml
[model_providers.llama_cpp]
name = "llama.cpp"
base_url = "http://localhost:8001/v1"
wire_api = "responses"
stream_idle_timeout_ms = 10000000
```

```bash
codex --model unsloth/GLM-4.7-Flash -c model_provider=llama_cpp
```

---

## LiteLLM unified proxy

For multi-provider setups, one LiteLLM proxy translates between Chat and
Responses formats and gives you a single auth surface.

`litellm-config.yaml`:

```yaml
model_list:
  - model_name: deepseek-chat
    litellm_params:
      model: deepseek/deepseek-chat
      api_key: os.environ/DEEPSEEK_API_KEY

  - model_name: qwen3-coder
    litellm_params:
      model: together_ai/Qwen/Qwen3-Coder-480B-A35B-Instruct
      api_key: os.environ/TOGETHER_API_KEY

  - model_name: nemotron-49b
    litellm_params:
      model: nvidia_nim/nvidia/llama-3.3-nemotron-super-49b-v1
      api_key: os.environ/NVIDIA_API_KEY

general_settings:
  master_key: sk-local-dev
```

Run:

```bash
litellm --config litellm-config.yaml --port 4000
```

Wire Codex CLI at it via `config.toml`:

```toml
[model_providers.litellm]
name = "LiteLLM"
base_url = "http://localhost:4000/v1"
env_key = "LITELLM_KEY"   # set to sk-local-dev
wire_api = "responses"
```

---

## Decision matrix

| Goal                                    | Recommended path                      |
| --------------------------------------- | ------------------------------------- |
| Use Together AI catalog                 | Custom provider in `config.toml`      |
| Run Nemotron / Qwen / Gemma locally     | `--oss` or vLLM Responses endpoint    |
| Switch between many models routinely    | LiteLLM proxy + Codex pointed at it   |
| Best agentic quality (subagents, hooks) | Stay on OpenAI defaults               |
| DeepSeek quick session                  | `[profiles.deepseek]` + `wire_api=chat` |

---

## References

- Codex CLI advanced config: <https://developers.openai.com/codex/config-advanced>
- Codex CLI configuration reference: <https://developers.openai.com/codex/config-reference>
- vLLM OpenAI-compatible server: <https://docs.vllm.ai/en/latest/serving/openai_compatible_server/>
- Unsloth + Codex CLI tutorial: <https://unsloth.ai/docs/basics/codex>
- LiteLLM proxy: <https://docs.litellm.ai/docs/proxy/quick_start>
- Together AI OpenAI compatibility: <https://docs.together.ai/docs/openai-api-compatibility>

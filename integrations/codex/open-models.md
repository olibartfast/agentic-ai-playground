# Codex CLI — Routing to Open Models

Reference for routing Codex CLI to open-weights deployments (DeepSeek,
Nemotron, Qwen, GLM, Gemma, Llama) and aggregator/inference APIs (Together AI,
OpenRouter, Fireworks).

Last verified: May 2026.

---

## Official provider support

Codex CLI officially supports these providers out of the box:

| Provider | Built-in ID | How to activate |
| --- | --- | --- |
| OpenAI | `openai` | Default |
| Ollama | `ollama` | `--oss` flag or `oss_provider = "ollama"` |
| LM Studio | `lmstudio` | `--oss` flag or `oss_provider = "lmstudio"` |
| Amazon Bedrock | `amazon-bedrock` | `model_provider = "amazon-bedrock"` |
| Azure OpenAI | custom | `wire_api = "responses"` + `query_params` |

Everything else (Together AI, DeepSeek, OpenRouter, NVIDIA NIM) requires a
custom provider definition and **must** expose the OpenAI Responses API.

---

## Wire API requirement

`wire_api = "chat"` has been removed. All providers must use:

```toml
wire_api = "responses"
```

Providers that only support Chat Completions (DeepSeek, Together AI, OpenRouter,
NVIDIA NIM) **must be fronted by a LiteLLM proxy**, which translates Responses
↔ Chat for you.

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

## LiteLLM proxy (required for chat-only APIs)

For any provider that doesn't natively serve the Responses API, run a local
LiteLLM proxy. Codex talks Responses to LiteLLM; LiteLLM talks Chat to the
upstream provider.

### Install

```bash
pip install litellm[proxy]
```

### Config (`~/.codex/litellm-config.yaml`)

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

general_settings:
  master_key: sk-local-dev
```

### Codex config pointing at LiteLLM

```toml
[model_providers.litellm]
name = "LiteLLM"
base_url = "http://localhost:4000/v1"
env_key = "LITELLM_KEY"
wire_api = "responses"

[profiles.deepseek]
model_provider = "litellm"
model = "deepseek-v4-pro"

[profiles.qwen]
model_provider = "litellm"
model = "qwen3-coder"
model_reasoning_effort = "high"
```

### Single-terminal wrapper script

```bash
#!/bin/bash
set -e
export LITELLM_KEY=sk-local-dev

litellm --config ~/.codex/litellm-config.yaml --port 4000 &>/tmp/litellm.log &
LITELLM_PID=$!
trap "kill $LITELLM_PID 2>/dev/null" EXIT

until curl -sf http://localhost:4000/health >/dev/null 2>&1; do sleep 0.5; done

codex --profile "${1:-deepseek}" "${@:2}"
```

---

## Provider-specific configs

### DeepSeek

Models: `deepseek-v4-pro`, `deepseek-v4-flash`.
DeepSeek does **not** support the Responses API — use LiteLLM proxy (see above).

Direct config that will **not** work without LiteLLM:
```toml
# This alone is not enough — DeepSeek needs LiteLLM in front
[model_providers.deepseek]
name = "DeepSeek"
base_url = "https://api.deepseek.com/v1"
env_key = "DEEPSEEK_API_KEY"
wire_api = "responses"   # will fail — DeepSeek doesn't serve this format
```

### Together AI

Together AI does **not** support the Responses API — use LiteLLM proxy.
Catalog includes Qwen3-Coder, DeepSeek V3/R1, Llama, Mixtral, GLM, Gemma,
Nemotron. Models use HuggingFace-style paths.

### NVIDIA NIM

```toml
# Via LiteLLM proxy only
- model_name: nemotron-49b
  litellm_params:
    model: nvidia_nim/nvidia/llama-3.3-nemotron-super-49b-v1
    api_key: os.environ/NVIDIA_API_KEY
```

For local Nemotron via vLLM, it serves `/v1/responses` natively — no proxy
needed:

```toml
[model_providers.vllm]
name = "vLLM local"
base_url = "http://localhost:8000/v1"
wire_api = "responses"
```

### Local with llama.cpp + Unsloth

Unsloth's llama.cpp build serves Responses format natively — no proxy needed:

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

### Amazon Bedrock

Built-in — no custom provider needed:

```toml
model_provider = "amazon-bedrock"
model = "<bedrock-model-id>"

[model_providers.amazon-bedrock.aws]
profile = "default"
region = "eu-central-1"
```

### Azure OpenAI

```toml
[model_providers.azure]
base_url = "https://YOUR_PROJECT.openai.azure.com/openai"
wire_api = "responses"
query_params = { api-version = "2025-04-01-preview" }
```

---

## Decision matrix

| Goal | Recommended path |
| --- | --- |
| Use DeepSeek or Together AI | LiteLLM proxy → custom provider |
| Run any model locally (Ollama/LM Studio) | `--oss` flag |
| Run local model with Responses API (vLLM, llama.cpp+Unsloth) | Custom provider, no proxy |
| Amazon Bedrock or Azure | Built-in provider support |
| Switch between many remote models | LiteLLM proxy with multiple model entries |
| Best agentic quality (subagents, hooks) | Stay on OpenAI defaults |

---

## References

- Codex CLI models: <https://developers.openai.com/codex/models>
- Codex CLI advanced config: <https://developers.openai.com/codex/config-advanced>
- Codex CLI configuration reference: <https://developers.openai.com/codex/config-reference>
- vLLM OpenAI-compatible server: <https://docs.vllm.ai/en/latest/serving/openai_compatible_server/>
- Unsloth + Codex CLI tutorial: <https://unsloth.ai/docs/basics/codex>
- LiteLLM proxy: <https://docs.litellm.ai/docs/proxy/quick_start>
- Together AI OpenAI compatibility: <https://docs.together.ai/docs/openai-api-compatibility>
